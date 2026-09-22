"""
Scraper pour https://books.toscrape.com/

Récupère l'ensemble des livres du catalogue (pagination gérée automatiquement)
et sauvegarde les résultats dans un fichier CSV.

Pour chaque livre, on récupère :
- depuis la page de listing : titre, prix, note (étoiles), stock, image miniature
- depuis la page de détail du livre : UPC, description, nombre d'exemplaires
  disponibles, image haute résolution

Chaque donnée est récupérée par une fonction dédiée (une responsabilité = une
fonction), à l'exception de l'orchestration (scrape_book, scrape_all_books) et
du helper générique de lecture du tableau HTML (_get_table_value), qui sont
volontairement transverses.
"""

from __future__ import annotations

import csv
import re
import time
from typing import Iterator
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup, Tag

BASE_URL = "https://books.toscrape.com/"
FIRST_PAGE_URL = urljoin(BASE_URL, "catalogue/page-1.html")
DEFAULT_DELAY = 0.2  # secondes entre deux requêtes, par politesse envers le serveur
CSV_PATH = "books.csv"

STAR_RATINGS = {
    "One": 1,
    "Two": 2,
    "Three": 3,
    "Four": 4,
    "Five": 5,
}


# --------------------------------------------------------------------------
# Primitives HTTP / parsing
# --------------------------------------------------------------------------

def fetch_html(url: str, session: requests.Session, timeout: float = 10, retries: int = 3) -> str:
    """Récupère le HTML d'une URL, avec quelques tentatives en cas d'erreur réseau."""
    last_error: Exception | None = None
    for attempt in range(1, retries + 1):
        try:
            response = session.get(url, timeout=timeout)
            response.raise_for_status()
            return response.text
        except requests.RequestException as exc:
            last_error = exc
            if attempt < retries:
                time.sleep(1)
    raise RuntimeError(f"Échec du téléchargement de {url} après {retries} tentatives") from last_error


def parse_html(html: str) -> BeautifulSoup:
    """Parse une chaîne HTML en objet BeautifulSoup."""
    return BeautifulSoup(html, "html.parser")


# --------------------------------------------------------------------------
# Extraction des champs — page de listing (un <article class="product_pod"> par livre)
# --------------------------------------------------------------------------

def get_listing_title(book: Tag) -> str:
    """Titre du livre."""
    return book.select_one("h3 > a")["title"]


def get_listing_relative_url(book: Tag) -> str:
    """URL relative vers la page de détail du livre."""
    return book.select_one("h3 > a")["href"]


def get_price(book: Tag) -> float:
    """Prix du livre, en float (ex: '£51.77' -> 51.77)."""
    text = book.select_one(".product_price .price_color").get_text(strip=True)
    numeric = re.sub(r"[^\d.]", "", text)
    return float(numeric)


def get_star_rating(book: Tag) -> int:
    """Note du livre (1 à 5), déduite de la classe CSS 'One'...'Five'."""
    classes = book.select_one("p.star-rating")["class"]
    rating_class = next(c for c in classes if c != "star-rating")
    return STAR_RATINGS[rating_class]


def get_stock_status(book: Tag) -> bool:
    """True si le livre est en stock, False sinon."""
    text = book.select_one("p.instock.availability").get_text(strip=True)
    return "in stock" in text.lower()


def get_thumbnail_url(book: Tag) -> str:
    """URL relative de l'image miniature du livre."""
    return book.select_one("img")["src"]


# --------------------------------------------------------------------------
# Extraction des champs — page de détail du livre
# --------------------------------------------------------------------------

def _get_table_value(soup: BeautifulSoup, label: str) -> str | None:
    """Helper générique : lit la valeur associée à un libellé dans le tableau produit."""
    for row in soup.select("table.table-striped tr"):
        header = row.find("th")
        if header and header.get_text(strip=True) == label:
            value = row.find("td")
            return value.get_text(strip=True) if value else None
    return None


def get_upc(soup: BeautifulSoup) -> str:
    """Code UPC du livre."""
    return _get_table_value(soup, "UPC")


def get_number_available(soup: BeautifulSoup) -> int:
    """Nombre d'exemplaires disponibles (ex: 'In stock (22 available)' -> 22)."""
    text = _get_table_value(soup, "Availability") or ""
    match = re.search(r"\((\d+) available\)", text)
    return int(match.group(1)) if match else 0


def get_description(soup: BeautifulSoup) -> str:
    """Description du livre (peut être vide si absente de la page)."""
    element = soup.select_one("#product_description ~ p")
    return element.get_text(strip=True) if element else ""


def get_detail_image_url(soup: BeautifulSoup) -> str:
    """URL relative de l'image haute résolution du livre."""
    return soup.select_one("#product_gallery img")["src"]


# --------------------------------------------------------------------------
# Pagination et orchestration
# --------------------------------------------------------------------------

def iter_catalogue_pages(session: requests.Session, delay: float = DEFAULT_DELAY) -> Iterator[tuple[str, BeautifulSoup]]:
    """Parcourt toutes les pages du catalogue en suivant le lien 'next'.

    Yield un tuple (url_de_la_page, soup) pour chaque page, dans l'ordre.
    """
    url: str | None = FIRST_PAGE_URL
    while url:
        html = fetch_html(url, session)
        soup = parse_html(html)
        yield url, soup

        next_link = soup.select_one("li.next > a")
        url = urljoin(url, next_link["href"]) if next_link else None
        if url:
            time.sleep(delay)


def get_book_links_from_page(soup: BeautifulSoup) -> list[Tag]:
    """Liste des balises <article class="product_pod"> présentes sur une page catalogue."""
    return soup.find_all("article", class_="product_pod")


def scrape_book(book_tag: Tag, page_url: str, session: requests.Session, delay: float = DEFAULT_DELAY) -> dict:
    """Récupère toutes les informations d'un livre (page listing + page détail)."""
    detail_url = urljoin(page_url, get_listing_relative_url(book_tag))

    detail_html = fetch_html(detail_url, session)
    detail_soup = parse_html(detail_html)
    time.sleep(delay)

    return {
        "title": get_listing_title(book_tag),
        "price": get_price(book_tag),
        "star_rating": get_star_rating(book_tag),
        "in_stock": get_stock_status(book_tag),
        "number_available": get_number_available(detail_soup),
        "thumbnail_url": urljoin(page_url, get_thumbnail_url(book_tag)),
        "image_url": urljoin(detail_url, get_detail_image_url(detail_soup)),
        "detail_url": detail_url,
        "upc": get_upc(detail_soup),
        "description": get_description(detail_soup),
    }


def scrape_all_books(delay: float = DEFAULT_DELAY) -> list[dict]:
    """Scrape l'ensemble des livres du catalogue, toutes pages confondues."""
    records: list[dict] = []
    with requests.Session() as session:
        for page_url, page_soup in iter_catalogue_pages(session, delay=delay):
            for book_tag in get_book_links_from_page(page_soup):
                records.append(scrape_book(book_tag, page_url, session, delay=delay))
            print(f"{page_url} — {len(records)} livres cumulés")
    return records


# --------------------------------------------------------------------------
# Sortie
# --------------------------------------------------------------------------

def save_to_csv(records: list[dict], path: str = CSV_PATH) -> None:
    """Écrit la liste de livres dans un fichier CSV."""
    if not records:
        return
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(records[0].keys()))
        writer.writeheader()
        writer.writerows(records)


def main() -> None:
    records = scrape_all_books()
    save_to_csv(records)
    print(f"{len(records)} livres sauvegardés dans {CSV_PATH}")


if __name__ == "__main__":
    main()
