# Exercice — Scraper books.toscrape.com

## Objectif

Écrire un script Python `scraper.py` qui récupère **l'intégralité des livres** du site d'entraînement [https://books.toscrape.com/](https://books.toscrape.com/) et sauvegarde le résultat dans un fichier `books.csv`.

Le site contient environ 1000 livres répartis sur 50 pages de catalogue (20 livres par page). Chaque livre a aussi sa propre page de détail, accessible en cliquant sur son titre.

## Prérequis

- `requests` pour télécharger le HTML
- `beautifulsoup4` pour le parser

```bash
pip install requests beautifulsoup4
```

## Consignes générales

1. **Une fonction = une donnée récupérée.** Ne faites pas une seule grosse fonction qui extrait tout d'un coup : chaque champ (titre, prix, note, stock, image, UPC, description, nombre disponible) doit être extrait par sa propre fonction, réutilisable et testable indépendamment.
2. **Gérez la pagination.** Votre script doit parcourir automatiquement toutes les pages du catalogue, sans coder en dur "50 pages" — il doit s'arrêter tout seul quand il n'y a plus de page suivante.
3. **Suivez le lien de chaque livre** pour aller chercher les informations qui ne sont disponibles que sur sa page de détail.
4. **Exportez le résultat en CSV**, avec une ligne par livre.

## Données à récupérer

### Sur la page de listing (catalogue)

Vous devez en extraire :

| Champ | Description |
|---|---|
| `title` | Titre du livre |
| `price` | Prix (en nombre, sans le symbole devise) |
| `star_rating` | Note du livre, de 1 à 5 |
| `in_stock` | `True`/`False` selon la disponibilité affichée |
| `thumbnail_url` | URL de l'image miniature (en URL absolue, pas relative) |

### Sur la page de détail du livre

En suivant le lien du titre, vous arrivez sur une page qui contient en plus :

| Champ | Description |
|---|---|
| `upc` | Code UPC du livre |
| `description` | Texte de description du livre |
| `number_available` | Nombre exact d'exemplaires en stock |
| `image_url` | URL de l'image en haute résolution (en URL absolue) |

## Étapes suggérées

Avancez progressivement plutôt que de tout écrire d'un coup :

1. **Échauffement** : téléchargez la page d'accueil et affichez le titre de tous les livres qui s'y trouvent (vous devez retrouver 20 titres).
2. **Un livre complet** : pour un seul livre de la page 1, récupérez les 5 champs de la page de listing, puis suivez son lien et récupérez les 4 champs de la page de détail. Assemblez le tout dans un dictionnaire.
3. **Toute une page** : généralisez l'étape précédente à tous les livres d'une page catalogue.
4. **Toutes les pages** : ajoutez la logique de pagination pour parcourir tout le catalogue.
5. **Export** : sauvegardez la liste de dictionnaires obtenue dans un fichier `books.csv`.

## Squelette de fonctions à compléter

Vous êtes obligé de suivre exactement ces noms, ils vous donnent une structure de départ cohérente avec la consigne "une fonction par donnée" :

```python
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
```

## Comment vérifier votre travail

Vous pouvez lancer la commande 

```shell
pytest test_scraper.py
```

## Pour aller plus loin (bonus)

- Ajouter un export `books.json` en plus du CSV
- Ajouter un petit délai (`time.sleep`) entre les requêtes par politesse envers le serveur
- Gérer les erreurs réseau avec une nouvelle tentative en cas d'échec