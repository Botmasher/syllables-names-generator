from uuid import uuid4

class Syllables():
    def __init__(self):
        self.syllables = {}

    def has(self, syllable_id):
        """Check if an id exists in the syllables map"""
        return syllable_id in self.syllables

    # TODO: vet for syllable characters || features
    def is_valid_structure(self, structure):
        if not isinstance(structure, list):
            return False
        return True

    def get(self, syllable_id=None):
        """Read one syllable or all if no id given"""
        if syllable_id:
            return self.syllables.get(syllable_id)
        return self.syllables

    def add(self, structure):
        """Add a new syllable to the syllables map"""
        if not self.is_valid_structure(structure):
            return
        syllable_id = f"syllable-{uuid4()}"
        self.syllables[syllable_id] = structure
        return syllable_id

    def update(self, syllable_id, structure):
        """Modify an existing syllable"""
        if not self.get(syllable_id):
            print("Syllable update failed - unknown syllable_id")
            return
        if not self.is_valid_structure(structure):
            print(f"Syllable update failed - invalid syllable structure {structure}")
            return
        self.syllables[syllable_id] = structure
        return syllable_id

    def remove(self, syllable_id):
        """Remove one syllable from the syllables map"""
        if self.has(syllable_id):
            return self.syllables.pop(syllable_id)
        return

    def clear(self):
        """Reset the syllables map and return a cache read method"""
        syllables_cache = self.syllables.copy()
        def read_cache():
            return syllables_cache
        self.syllables.clear()
        return read_cache
