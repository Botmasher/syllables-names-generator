class Corpus:
    def __init__(self):
        self.corpus = []

    def add(self, sound="", change="", spelling="", definition="", exponents=None):
        entry = {
            'sound': sound,
            'change': change,
            'spelling': spelling,
            'definition': definition,
            'exponents': exponents
        }
        self.corpus.append(entry)
        return entry

    def get(self, entry_id=0):
        return self.corpus[entry_id]
