from uuid import uuid4

class Corpus:
    def __init__(self):
        self.corpus = {}

    def add(self, sound="", change="", spelling="", definition="", exponents=None, properties=None, pos=None):
        entry_id = f"corpus-{uuid4()}"
        self.corpus[entry_id] = {
            'sound': sound,
            'change': change,
            'spelling': spelling,
            'definition': definition,
            'exponents': exponents,
            'properties': properties,
            'pos': pos
        }
        return entry_id

    def get(self, entry_id):
        return self.corpus.get(entry_id)

    def remove(self, entry_id):
        return self.corpus.pop(entry_id, None)

    def update(self, entry_id, sound="", change="", spelling="", definition=""):
        # check for valid entry
        entry = self.get(entry_id)
        if not entry:
            print(f"Corpus failed to update unrecognized id {entry_id}")
            return

        # only modify updated values for the entry
        updates = {
            'sound': sound,
            'change': change,
            'spelling': spelling,
            'definition': definition
        }
        entry = {
            k: updates[k] if updates.get(k) else v
            for k, v in entry.items()
        }

        return entry_id
