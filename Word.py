class Word:
    """
    Case class for Word analysed by nlp pipeline
    """

    def __init__(self, index, text, head, deprel, upos, lemma):
        self.index = index
        self.text = text
        self.head = head
        self.deprel = deprel
        self.upos = upos
        self.lemma = lemma
        self.children = []

    def __repr__(self):
        return f'id: {self.index}\tword: {self.text}\thead id: {self.head}\tdeprel: {self.deprel}\tupos: {self.upos}\tlemma: {self.lemma}'
