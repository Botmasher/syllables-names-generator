# TODO: consider is this phrases and sentences?
#   - example: DP instead of having everything attach to exponents

# NOTE: a named sentence is a list of blueprints for building a sequence of units

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
        # structure of sentences:
        # {
        #   sentence_name: {
        #       # sequence for building units
        #       'structure': [
        #           [word_class, properties],
        #           ...
        #       ],
        #       # sentence-level properties for passing in type "sentence"
        #       # example: property sentence:interrogative to attach question particle
        #       'properties': {}
        #   },
        #   ...
        # }
        # NOTE: for now keep simpler sentences map between names : structures
        self.sentences = {}

        # TODO: support varying syntax and flexible word order
        #   - word order in nonconfig langs
    
    def get(self, name):
        """Read one named sentence sequence"""
        return self.sentences.get(name)

    def vet_structure(self, structure):
        """Check and refine the units structure sequence for one sentence"""
        if not isinstance(structure, (list, tuple)):
            print(f"Sentences vet_structure failed - expected structure list {structure}")
            return
        # create sequence of structures for building units
        units_sequence = []
        for unit in structure:
            # expect (word_class, properties) pairs
            if not isinstance(unit, list) or len(unit) != 2:
                print(f"Sentences vet_structure failed - unrecognized unit-building structure {unit}")
                return
            # add properties and pos for this unit structure
            unit_word_classes = self.grammar.parse_word_classes(unit[0]) if unit[0] else None
            unit_properties = self.grammar.parse_properties(unit[1])
            # check for valid properties
            if not unit_properties:
                print(f"Sentences vet_structure failed - invalid unit properties {unit_properties}")
                return
            units_sequence.append([unit_word_classes, unit_properties])
        return units_sequence

    def add(self, name="", structure=None, all_or_none=False):
        """Add a named sentence type with a sequence of units in the sentence"""
        # check for existing sentence type name and sequence of units
        if not name or name in self.sentences or not isinstance(structure, (list, tuple)):
            print("Failed to add sentence - expected valid name and structure")
            return
        
        # create the sentence's units structure sequence
        vetted_structure = self.vet_structure(structure)
        if not vetted_structure:
            print(f"Sentences add failed - invalid sentence structure {structure}")
            return

        # add units structure to sentences
        self.sentences[name] = vetted_structure

        return self.sentences[name]

    def update(self, name, structure, all_or_none=False):
        """Modify the unit sequence of a single named sentence type"""
        # check that the sentence type already exists
        if not self.get(name):
            print(f"Sentences update failed - unrecognized sentence name {name}")
            return
        
        # create valid units structure
        vetted_structure = self.vet_structure(structure)
        if not vetted_structure:
            print(f"Sentences add failed - invalid sentence structure {structure}")
            return

        # overwrite named sentence's units structure
        self.sentences[name] = vetted_structure

        return self.sentences[name]
    
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
