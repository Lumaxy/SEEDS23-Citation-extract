from bs4 import BeautifulSoup
import pandas as pd


def clean_html_code(article: str) -> str:
    """
    Remove specific html element. Here we handle : 
        - Paywall (pour lire la suiteDéjà abonné ? Se connecter)
        - Framed Article
        - Twitter references (oembed-twitter)
    """
    soup = BeautifulSoup(article, 'html.parser')

    for paywall_div in soup.css.select("div.paywall"):
        paywall_div.decompose()

    for framed_article in soup.css.select("div.article-framed"):
        framed_article.decompose()

    for twitter_reference in soup.css.select("div.oembed-twitter"):
        twitter_reference.decompose()

    return soup.get_text()


def read(path: str) -> pd.DataFrame:
    """
    Lis et nettoie chaque article et renvoie l'ensemble des articles dans la colonne "articles" d'un DataFrame Pandas.
    """
    df = pd.DataFrame()

    df["articles"] = pd.read_json(path) \
        .dropna() \
        .reset_index().contenu.str.replace("’", "'") \
        .str.replace("\.", ".  ") \
        .str.replace('M\.', 'Monsieur') \
        .apply(clean_html_code)

    return df
