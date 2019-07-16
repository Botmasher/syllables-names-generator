from uuid import uuid4

class Corpus:
    def __init__(self):
        self.corpus = {}    # example entry storage - see add() for entry shape

    def add(self, sound="", change="", spelling="", definition="", exponents=None, properties=None, pos=None):
        """Create corpus entry containing this example, including three possible levels
        of representation, grammatical info and a definition."""
        # check for valid grammatical data
        if properties and not isinstance(properties, dict):
            print(f"Corpus add failed - expected properties map not {properties}")
            return
        if pos and not isinstance(pos, (list, set, tuple, str)):
            print(f"Corpus add failed - expected sequence or string pos not {pos}")
            return
        # ensure pos is stored as set
        if pos:
            pos = set([pos]) if isinstance(pos, str) else set(pos)
        # add entry to corpus
        entry_id = f"corpus-{uuid4()}"
        self.corpus[entry_id] = {
            'sound': sound,             # list of strings
            'change': change,           # list of strings
            'spelling': spelling,       # list of strings
            'definition': definition,   # string
            'exponents': exponents,     # list of string ids
            'properties': properties,   # dict
            'pos': pos                  # set of strings
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
