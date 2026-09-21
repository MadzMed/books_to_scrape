import requests
from bs4 import BeautifulSoup

BASE_URL = "https://books.toscrape.com/"


def fetch_html(url, session):
    """Télécharge le HTML d'une URL et le retourne sous forme de texte."""
    # TODO


def parse_html(html):
    """Transforme une chaîne HTML en objet BeautifulSoup."""
    # TODO


# --- Page listing ---


def get_listing_title(book):
    # TODO
    ...


def get_price(book):
    # TODO
    ...


def get_star_rating(book):
    # TODO (indice : la note est encodée dans une classe CSS, ex. "star-rating Three")
    ...


def get_stock_status(book):
    # TODO
    ...


def get_thumbnail_url(book):
    # TODO
    ...


def get_listing_relative_url(book):
    """URL relative vers la page de détail du livre (pour aller la chercher ensuite)."""
    # TODO


# --- Page détail ---


def get_upc(soup):
    # TODO (indice : c'est une ligne d'un tableau HTML)
    ...


def get_description(soup):
    # TODO
    ...


def get_number_available(soup):
    # TODO (indice : le texte ressemble à "In stock (22 available)")
    ...


def get_detail_image_url(soup):
    # TODO
    ...


# --- Pagination et orchestration ---


def iter_catalogue_pages(session):
    """Générateur qui parcourt toutes les pages du catalogue."""
    # TODO (indice : cherchez le lien "next" en bas de page, arrêtez-vous quand il n'y en a plus)


def get_book_links_from_page(soup):
    """Retourne la liste des blocs <article class="product_pod"> d'une page."""
    # TODO


def scrape_book(book_tag, page_url, session):
    """Récupère toutes les infos d'un livre (listing + détail) sous forme de dict."""
    # TODO


def scrape_all_books():
    """Parcourt tout le catalogue et retourne la liste de tous les livres."""
    # TODO


# --- Sortie ---


def save_to_csv(records, path="books.csv"):
    """Écrit la liste de dictionnaires dans un fichier CSV."""
    # TODO


if __name__ == "__main__":
    books = scrape_all_books()
    save_to_csv(books)
    print(f"{len(books)} livres sauvegardés dans books.csv")