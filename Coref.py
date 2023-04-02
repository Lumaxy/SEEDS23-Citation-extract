from spacy.tokens import Span
from itertools import islice


def appartient_a_la_base(person: str, vip_list) -> str:
    """
    Test si la personne est dans la liste des vips
    """
    full_name_person = person.split(' ')
    if len(full_name_person) > 6:
        # il est possible que des phrases soient detectées comme correspondance, on veut les éliminer.
        # exemple :
        # "proposition de loi, déposée par Aurore Bergé (Renaissance) visant à imposer une peine d’inéligibilité à davantage d’auteurs de violences"
        # est associé à "Le texte"
        # aurore bergé peut être detectée dans la premiere proposition, mais ce n'est pas souhaitable
        return ""
    full_name_person_lowercase = [x.lower() for x in full_name_person]
    one_match = vip_list[vip_list['pers_nom'].isin(full_name_person_lowercase)]
    two_match = one_match[one_match['pers_prenom'].isin(
        full_name_person_lowercase)]
    if len(two_match.index) == 1:
        prenom = two_match.loc[two_match.index[0]]['pers_prenom']
        prenom = prenom[0].upper() + prenom[1:]

        nom = two_match.loc[two_match.index[0]]['pers_nom']
        nom = nom[0].upper() + nom[1:]
        return prenom + " " + nom
    else:
        return ""


def element_is_vip(list_person: list, vip_list) -> list[str]:
    """
    Filter the given name list.
    [Macron, Juliette Machin] -> [Macron]
    """
    res_set = set()
    for person in list_person:
        res_set.add(appartient_a_la_base(person.text, vip_list))

    if '' in res_set:
        res_set.remove('')

    if len(res_set) == 1:
        name = res_set.pop()
        return name

    return ""


def resolve_text(text: str, vip_list, nlp):
    """
    Transforme les pronoms en noms
    @args text {str}: Article
    @return new_text {str}: Il -> Emmanuel Macron
    """
    doc = nlp(text)
    new_text = doc._.resolved_text

    interesting_spans = []
    spans_replacement = []
    for idx, cluster in enumerate(doc._.coref_clusters):
        curr_span = []
        name_collection = []
        for span in cluster:
            if span[1] - span[0] < 6:
                curr_span.append([span[0], span[1]])
                name_collection.append(
                    Span(doc, span[0], span[1]+1, str(idx).upper()))
        selected = element_is_vip(name_collection, vip_list)
        if selected != '':
            interesting_spans += curr_span
            spans_replacement += [selected for _ in curr_span]
    new_text = []
    token_list = [token for token in doc]
    numbers = iter(range(len(token_list)))
    for i in numbers:
        replacement = False
        for span_i, elem in enumerate(interesting_spans):
            if i == elem[0]:
                replacement = True
                new_text.append(" " + spans_replacement[span_i] + " ")
                interval = elem[1]-elem[0]
                # consume inteval
                next(islice(numbers, interval, interval), None)
        if not replacement:
            new_text.append(token_list[i].text_with_ws)
    return "".join(new_text)
