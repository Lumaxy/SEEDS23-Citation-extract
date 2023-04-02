from pprint import pprint
from time import perf_counter
import re
import Levenshtein
import networkx as nx
from networkx import Graph
import matplotlib.pyplot as plt
import pandas as pd
from Word import Word
from Sentence import Sentence
from ReportedSpeech import ReportedSpeech
import stanza
import numpy as np
from Coref import resolve_text


def filter_VIPs(list_persons: pd.DataFrame) -> tuple[list, list]:
    """
    @return the list of vips, and their association
    """
    vip_list = pd.read_json("resources/people.json")
    output_list = []
    association_dict = {}
    vip_list["pers_nom"] = vip_list["pers_nom"].str.lower()
    vip_list["pers_prenom"] = vip_list["pers_prenom"].str.lower()
    for person in list_persons:
        full_name_person = person.split(' ')
        full_name_person_lowercase = [x.lower() for x in full_name_person]
        one_match = vip_list[vip_list['pers_nom'].isin(
            full_name_person_lowercase)]
        two_match = one_match[one_match['pers_prenom'].isin(
            full_name_person_lowercase)]
        if not two_match.empty:
            output_list.append(person)
            association_dict[str(person)] = two_match.to_dict()

    return output_list, association_dict


def obfuscate_direct_citation_in_article(article: str) -> str:
    """
    @args article: The news article to obfuscate
    @return the obfuscated news article (citation replaced with <<----------------------->>), to keep the full sentence when extraction it. (correct length, Hence the number of -----)
    """
    article_obfuscated_direct_citation = article
    for match in re.finditer('["«]([%\wÀ-ú\. ’!?\-\', €$£]+)["»]', article):
        article_obfuscated_direct_citation = article_obfuscated_direct_citation.replace(
            match.group(), f"«{''.join(['-' for _ in range(len(match.group()) - 2)])}»")

    assert len(article_obfuscated_direct_citation) == len(article)

    return article_obfuscated_direct_citation


def replace_direct_citation(sentence: str) -> str:
    """
    @args article: The article to obfuscate
    @return the obfuscated news article (citation replaced with « citation directe »). Usefull when using NLP pipeline (the syntax of the sentence is correct)
    """
    article_replaced_direct_citation = sentence
    for match in re.finditer('«(-)+»', sentence):
        article_replaced_direct_citation = article_replaced_direct_citation.replace(
            match.group(), f"« citation directe »")

    return article_replaced_direct_citation


def build_graph(words: list[Word]) -> Graph:
    graph = nx.Graph()
    words[0] = Word(0, "root", 0, "", "", "")

    labeldict = {}

    # Create nodes
    for word in words.values():
        labeldict[word.index] = word.text
        graph.add_node(word.index)

    # Create edges and add children to nodes
    for word in words.values():
        head_node = next(
            (x for x in words.values() if x.index == word.head), None)
        if head_node:
            graph.add_edge(head_node.index, word.index)
            head_node.children.append(word)

    # draw_and_show_graph(graph, labeldict)

    return graph


def find_closest_upos_citing_verb(graph, words, start_word, list_of_upos, list_of_citing_verbs) -> Word | None:
    """
    Applicable sur un graphe de mots
    """
    shortest_path_length_from_start = sorted(dict(
        nx.all_pairs_shortest_path_length(graph))[start_word.index].items(), key=lambda x: x[1])
    aux_index = next(
        (x for x in shortest_path_length_from_start if words[x[0]].upos in list_of_upos and words[x[0]].lemma in list_of_citing_verbs), None)
    if aux_index:
        return words[aux_index[0]]
    return None


def find_closest_deprel(graph, words, start_word, list_of_deprel) -> Word | None:
    shortest_path_length_from_start = sorted(dict(
        nx.all_pairs_shortest_path_length(graph))[start_word.index].items(), key=lambda x: x[1])
    aux_index = next(
        (x for x in shortest_path_length_from_start if words[x[0]].deprel in list_of_deprel), None)
    if aux_index:
        return words[aux_index[0]]
    return None


def extract_full_name(word: Word, people: set[str]) -> str:
    r = sorted(map(lambda x: (x, Levenshtein.distance(
        word.text, x)), people), key=lambda x: x[1])
    if r:
        return r[0][0]
    return ""


def draw_and_show_graph(graph: Graph, labeldict: dict):
    nx.draw(graph, node_color=range(len(graph.nodes)),
            font_color="red", labels=labeldict, with_labels=True)
    plt.show()


def extract_sentences(article: str, resolved_article: str) -> dict[int, Sentence]:
    """
    Extrait l'ensemble des phrases de l'article
    @return dict with:
        - Key: index of sentence
        - Values: Sentence object
    #TODO: Change the way the sentence are found (using ?, !, ;, and not only dots)
    """
    article_obfuscated_direct_citation = obfuscate_direct_citation_in_article(
        article)
    resolved_article_obfuscated_direct_citation = obfuscate_direct_citation_in_article(
        resolved_article)

    list_of_sentences_obfuscated_direct_citation = list(map(lambda x: x + ".",
                                                            filter(lambda sentence: len(sentence) > 0,
                                                                   article_obfuscated_direct_citation.split("."))))

    resolved_article_list_of_sentences_obfuscated_direct_citation = list(map(lambda x: x + ".",
                                                                             filter(lambda sentence: len(sentence) > 0,
                                                                                    resolved_article_obfuscated_direct_citation.split("."))))

    # Be sure to have the same number of sentence, otherwise there is a problem ! Check the regex in function obfuscate_sentence
    assert len(resolved_article_list_of_sentences_obfuscated_direct_citation) == len(
        list_of_sentences_obfuscated_direct_citation)

    sentences = {i: Sentence(list_of_sentences_obfuscated_direct_citation[i]) for i in range(
        len(list_of_sentences_obfuscated_direct_citation))}

    current_total_size = 0
    for index, sentence in sentences.items():
        sentence.start = current_total_size
        sentence.end = current_total_size+len(sentence.obfuscated_sentence)
        sentence.index_in_text = index

        sentence.raw_sentence = article[sentence.start:sentence.end]
        sentence.replaced_direct_citation = replace_direct_citation(
            sentence.obfuscated_sentence)
        sentence.coreferenced_sentence = replace_direct_citation(
            resolved_article_list_of_sentences_obfuscated_direct_citation[index])

        current_total_size += len(sentence.obfuscated_sentence)

    return sentences


def get_sentence_before(sentence: Sentence, sentences: list[Sentence]) -> Sentence | None:
    return sentences[sentence.index_in_text - 1] if sentence.index_in_text - 1 > 0 else None


def get_sentence_after(sentence: Sentence, sentences: list[Sentence]) -> Sentence | None:
    return sentences[sentence.index_in_text + 1] if sentence.index_in_text + 1 < len(sentences) else None


def extract_citation_from_article(article: str, citing_verbs: np.ndarray, vip_list: pd.DataFrame, nlp_pipeline: stanza.Pipeline, spacy_nlp=None) -> list[ReportedSpeech]:
    """
    @arg article {str} the full news article to analyse
    @arg citing_verbs {np.ndarray} The list of verb used in reported speech
    @arg vip_list {pd.DataFrame} People of interest list
    @arg nlp_pipeline {stanza.Pipeline} the stanza pipeline used to analyse the news article.
    @arg citing_verbs {numpy.ndarray} the list of identified verb of speech
    @return the list of identified reported speech
    """
    results = {}

    resolved_article = article if spacy_nlp is None else resolve_text(
        article, vip_list, spacy_nlp)

    sentences = extract_sentences(article, resolved_article)

    for sentence in sentences.values():
        stanza_doc = nlp_pipeline(sentence.coreferenced_sentence)

        people = set(
            [ent.text for sent in stanza_doc.sentences for ent in sent.ents if ent.type == "PER"])

        # Nobody speak here, droping this sentence
        if len(people) == 0:
            continue

        words = {word.id: Word(word.id, word.text, word.head, word.deprel, word.upos, word.lemma)
                 for sent in stanza_doc.sentences for word in sent.words}

        citing_verbs_in_sentence = list(filter(
            lambda word: word.lemma in citing_verbs, words.values()))

        # No sign of reported speech here, droping this sentence
        if not citing_verbs_in_sentence:
            continue

        graph = build_graph(words)

        clue_words = list(filter(lambda x: x.text == "«", words.values()))

        # We could enhance the following: Finding several person name in a given range.
        # Here we only detect the closest in the graph, not all in a range.

        # is it a direct citation with clear « ?
        if clue_words:

            # It is ! Finding the speaker
            for clue in clue_words:
                citing_verb_of_clue = find_closest_upos_citing_verb(
                    graph, words, clue, ["VERB", "AUX"], citing_verbs)

                speaker = find_closest_deprel(
                    graph, words, citing_verb_of_clue, ["flat:name"])
                if speaker:
                    full_name = extract_full_name(speaker, people)
                    # We could enhance by using additional_information to build a great speaker object
                    filtered_list, additional_information = filter_VIPs(
                        [full_name])
                    if len(filtered_list) > 0:
                        results[sentence] = filtered_list[0]

        else:
            # Rapported speech without direct citation, it's getting harder....
            for word in citing_verbs_in_sentence:
                speaker = find_closest_deprel(
                    graph, words, word, ["flat:name"])
                if speaker:
                    full_name = extract_full_name(speaker, people)
                    # We could enhance by using additional_information to build a great speaker object
                    filtered_list, additional_information = filter_VIPs(
                        [full_name])
                    if len(filtered_list) > 0:
                        results[sentence] = filtered_list[0]

    tmp = [ReportedSpeech(sentence,
                          speaker,
                          get_sentence_before(sentence, sentences),
                          get_sentence_after(sentence, sentences))
           for sentence, speaker in results.items()]
    print(*list(map(lambda x: str(x), tmp)), sep="\n\n")
    return tmp
