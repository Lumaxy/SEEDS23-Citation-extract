class Sentence:

    def __init__(self, obfuscated_sentence: str):
        """
        Object nul sans logique

        obfuscated_sentence: Macron a annoncé : <<--------------------------->>
        raw_sentence: Macron a annoncé : << Bloquez tous ! Les rues... >>
        replaced_direct_citation: Macron a annoncé : << Citation directe >>
        coreferenced_sentence: Il a annoncé -> Macorn a annoncé
        start, end: Position in text (in char)
        """
        self.obfuscated_sentence = obfuscated_sentence
        self.raw_sentence = ""
        self.replaced_direct_citation = ""
        self.coreferenced_sentence = ""
        self.start = 0
        self.end = 0
        self.index_in_text = 0

    def __repr__(self):
        return f"{self.start}:{self.end}, index:{self.index_in_text}\n{self.raw_sentence}\n{self.obfuscated_sentence}\n{self.replaced_direct_citation}\n{self.coreferenced_sentence}"
