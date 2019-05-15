# TODO: consider is this phrases and sentences?
#   - example: DP instead of having everything attach to exponents

# Sentences stores instructions for building out any
# predefined unit structures to be filled with headwords
class Sentences:
    def __init__(self, grammar):
        # up reference for checking exponents and building units
        self.grammar = grammar

        # fixed left-to-right order of units in various types of sentences
        #   - each discrete part is a unit or a word classes
        #   - see arrange method for the reordering process
        #
        # structure of sentence:sequence pairs:
        # {
        #   'sentence_name': [
        #       {'unit_name', 'word_class', ...},   # options
        #       {'unit_name_2'},
        #       {'word_class_2', word_class_3}
        #   ]
        # }
        self.sentences = {}

        # TODO: support varying syntax and flexible word order
        #   - "interrogative" vs "declarative" syntax in EN
        #   - word order in nonconfig langs
    
    def get(self, name):
        """Read one named sentence sequence"""
        return self.sentences.get(name)

    def add(self, name="", structure=None, overwrite=False, all_or_none=False):
        """Add a named sentence type with a sequence of units in the sentence"""
        # check for existing sentence type name and sequence of units
        if not name or (overwrite or name in self.sentences) or not isinstance(structure, (list, tuple)):
            print("Failed to add sentence - expected valid name and structure")
            return
        
        # TODO: take in word class, exponents and test-build every unit

        # collect only known units
        filtered_units = [
            unit for unit in structure
            if unit in self.grammar.exponents.exponents
        ]

        # back out if any non-units given
        if all_or_none and len(filtered_units) != len(structure):
            return

        # add units sequence to sentences
        self.sentences[name] = filtered_units

        return self.sentences[name]

    def update(self, name, structure, all_or_none=False):
        """Modify the unit sequence of a single named sentence type"""
        # check that the sentence type already exists
        if not self.get(name):
            return
        # run sentence add with overwrite
        return self.add(name, structure, overwrite=True)
    
    def remove(self, name):
        """Delete and return one existing sentence structure from the
        sentences map, or None if sentence not found"""
        # remove and return the sentence sequence
        return self.sentences.pop(name, None)

    def list_headwords(self, name):
        """See which words need to be filled out for a named sentence"""
        sentence = self.get(name)
        if not sentence:
            return
        headwords = []
        for unit in sentence:
            # ? structure like this:    [ [ word, [ properties... ] ] , ... ]
            print(unit[0])
            headwords.append(unit[0])
        return headwords

    def apply(self, name, headwords):
        """Take a collection of sentence items and return a reordered copy
        reordering units using on the named sentence type."""

        # check if sentence type exists in collection
        if name not in self.sentences:
            print(f"Failed to arrange unidentified sentence {name}")
            return
        
        sentence = self.get(name)
        
        ordered_sentence = []

        # TODO: arrange sentence
        # - fill in headwords for each slot
        # - add exponents/properties for each headword
        # - follow order of units given in self.sentences[name]
        
        return "".join(ordered_sentence)
