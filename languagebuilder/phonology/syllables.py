from uuid import uuid4

class Syllables():
    def __init__(self, phonology):
        # map of syllable structures
        self.syllables = {}
        # special syllable character abbreviations
        self.syllable_characters = ['_', '#', ' ', 'C', 'V']
        # reference phonology into which injected
        self.phonology = phonology

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
        # return all syllables if no id given
        if not syllable_id:
            return self.syllables
        # return a single syllable entry
        if self.has(syllable_id):
            return self.syllables.get(syllable_id)
        # no matching syllable entry
        return

    # TODO: check how environment/rule formats readout
    def print_syllables(self):
        """Print out all syllables in a human-readable formatted string"""
        syllable_text = ""
        count = 0
        for syllable in self.syllables.values():
            count += 1
            syllable_text += f"Syllable {count}: "
            for syllable_item in syllable.get_structure():
                for feature in syllable_item:
                    syllable_text += f"{feature}, "
            syllable_text = syllable_text[:-2]
            syllable_text += "\n"
        print(syllable_text)
        return syllable_text

    def add(self, structure):
        """Add a new syllable to the syllables map"""
        if not self.is_valid_structure(structure):
            print(f"Syllables add failed - invalid structure {structure}")
            return

        # break up string into traversable terms
        raw_structure = structure.split() if isinstance(structure, str) else structure

        # store valid terms for added structure
        new_structure = []

        # TODO: use below checks as starting point for vetting _is_valid_structure

        # build up sequence of valid features or syllable characters
        for syllable_item in raw_structure:
            if isinstance(syllable_item, str):
                if not (syllable_item in self.syllable_characters or self.phonology.phonetics.has_feature(syllable_item)):
                    print(f"Syllables add failed - invalid syllable item {syllable_item}")
                    return
                elif syllable_item == 'C':
                    new_structure.append(["consonant"])
                elif syllable_item == 'V':
                    new_structure.append(["vowel"])
                else:
                    new_structure.append([syllable_item])
            elif isinstance(syllable_item, list):
                for feature in syllable_item:
                    if not self.phonology.phonetics.has_feature(syllable_item):
                        print("Phonology add_syllable failed - invalid syllable feature {0}".format(feature))
                        return
                new_structure.append(syllable_item)
        
        # add created syllable to the map
        syllable_id = f"syllable-{uuid4()}"
        self.syllables[syllable_id] = new_structure
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
        return self.syllables.pop(syllable_id, None)

    def clear(self):
        """Reset the syllables map and return a cache read method"""
        syllables_cache = self.syllables.copy()
        def read_cache():
            return syllables_cache
        self.syllables.clear()
        return read_cache
