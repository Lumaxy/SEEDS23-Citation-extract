import pandas as pd
import Clean
import stanza
import spacy
import numpy as np
from Function import extract_citation_from_article


df = Clean.read('resources/articles.json')

#https://fr.wiktionary.org/wiki/Cat%C3%A9gorie:Verbes_de_parole_en_fran%C3%A7ais
citing_verbs = np.loadtxt('resources/liste_verbes_paroles.csv', dtype='str')

vip_dataframe = pd.read_json("resources/people.json")
vip_dataframe["pers_nom"] = vip_dataframe["pers_nom"].str.lower()
vip_dataframe["pers_prenom"] = vip_dataframe["pers_prenom"].str.lower()

stanza_nlp = stanza.Pipeline('fr')
# spacy_nlp = spacy.load("fr_core_news_lg")
# spacy_nlp.add_pipe("xx_coref")

print("extracting citation...")
reported_speech_dataframe = df.articles.apply(
    lambda x: extract_citation_from_article(x, citing_verbs, vip_dataframe, nlp_pipeline=stanza_nlp))
reported_speech_dataframe.to_json("resources/citations.json")

reported_speech_dataframe.apply(lambda final_result: print(*list(map(lambda x: str(x), final_result)), sep="\n\n"))

print(reported_speech_dataframe)
