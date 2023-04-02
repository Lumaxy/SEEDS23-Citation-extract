from Sentence import Sentence


class ReportedSpeech:
    """
    Case class for reported speech.
    """

    def __init__(self, sentence: Sentence, speaker: str, sentence_before: Sentence, sentence_after: Sentence):
        self.sentence = sentence
        self.sentence_before = sentence_before
        self.sentence_after = sentence_after
        self.speaker = speaker

    def sentence_before_str(self):
        return "" if self.sentence_before is None else self.sentence_before.raw_sentence

    def sentence_after_str(self):
        return "" if self.sentence_after is None else self.sentence_after.raw_sentence

    def full_text(self):
        return f"{self.speaker} said: {self.sentence_before_str()}{self.sentence.raw_sentence}{self.sentence_after_str()}"

    def __repr__(self):
        return f"{self.speaker} said: {self.sentence.raw_sentence}"
