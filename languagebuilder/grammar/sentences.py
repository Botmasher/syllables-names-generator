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
        
        # catch a single word class, properties pair in a one-depth list and
        # try reinterpreting as a list with the pair as the first element
        # TODO: parse strings including both
        if len(structure) == 2 and all(isinstance(e, str) for e in structure):
            word_class = self.grammar.parse_word_classes(structure[0])
            properties = self.grammar.parse_properties(structure[1])
            if properties and word_class:
                return [[word_class, properties]]

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

    def update(self, name, structure=None, all_or_none=False):
        """Modify the unit sequence of a single named sentence type"""
        # check that the sentence type already exists
        if not self.get(name):
            print(f"Sentences update failed - unrecognized sentence name {name}")
            return
        
        # create valid units structure
        vetted_structure = self.vet_structure(structure)
        if not vetted_structure:
            print(f"Sentences update failed - invalid sentence structure {structure}")
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

    def apply(self, name="", headwords=None, spacing=" "):
        """Take a named sentence and a list of headwords to fill out the units in the
        name sentence and build out a sequence of units."""

        # check for sentence type in collection
        sentence = self.get(name)
        if not sentence:
            print(f"Failed to apply unidentified sentence {name}")
            return

        # grab list of word objects from the dictionary
        #fetched_words = [
        #   self.language.dictionary.lookup(word, i)
        #   for word, i in headwords
        #]
        # expect full entries instead of tying this to dictionary with lookups
        # TODO: high-level sentence methods with lookups from the Language
        fetched_words = [
            entry for entry in headwords
            if isinstance(entry, dict) and 'pos' in entry and 'sound' in entry 
        ]

        # check that headwords match buildable sentence units
        if not isinstance(fetched_words, (list, tuple)):
            print(f"Failed to apply sentence - expected headwords list not {headwords}")
            return
        if len(sentence) != len(fetched_words):
            print(f"Failed to apply sentence - number of headwords does not match fillable sentence units")
            return len(fetched_words)
        
        # store final built units
        applied_sentence = []

        # iterate through both sentence units and headwords
        # - unit structure is (word_classes, properties)
        # - headwords is a map containing various representations of word and data
        for i, unit in enumerate(sentence):
            word_data = fetched_words[i]
            word_sounds = word_data['sound']
            word_pos = word_data['pos']
            unit_pos, unit_properties = unit
            # compare headword class to expected word class
            if word_pos not in unit_pos:
                print(f"Failed to apply sentence - word {word_sounds} part of speech {word_pos} does not match expected word class {unit_pos}")
                return
            # create grammatical unit with headword and sentence unit properties
            built_unit = self.grammar.build_unit(
                word_sounds,
                properties=unit_properties,
                word_classes=word_pos
            )
            applied_sentence.append(built_unit)
        
        # return single string sentence
        return spacing.join(applied_sentence)
