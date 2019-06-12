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

        # translation structures kept in sync with sentences
        # TODO: incorporate into sentences
        self.translations = {}

        # TODO: support varying syntax and flexible word order
        #   - word order in nonconfig langs
    
    def get(self, name):
        """Read one named sentence sequence"""
        return self.sentences.get(name)

    def get_translation(self, name):
        return self.translations.get(name)

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
                print(f"Sentences vet_structure failed - invalid unit properties {unit[1]}")
                return
            units_sequence.append([unit_word_classes, unit_properties])
        return units_sequence

    # TODO: find a less user-defined way to generate translations
    #   - map structures to structure in target language?
    #   - e.g. X ({case:instrumental, deixis:indefinite}, noun) -> "with a(n) X"
    #   - this would put the structure at source of both units and translation
    def vet_translation(self, translation, structure, insertion_symbol="{}"):
        """Verify and format a valid translation for the given structure. Pass an
        insertion symbol to verify symbol used to format the translation on apply.
        Return a dict mapping each structural unit index to a unit translation
        with a formattable insertion point for a unit's base."""
        # send back empty to store in translations map
        if not translation:
            return []
        
        # collect valid translation piece for each unit in structure
        vetted_translation = []
        for translation_piece in translation:
            # expect translation piece to be a two-member sequence
            # ("translation", index) associated with a structural unit
            unit_translation = translation_piece[0]
            unit_index = translation_piece[1]
            if not isinstance(unit_translation, str) or not isinstance(unit_index, int) or not structure[unit_index]:
                return
            # expect one insertion symbol per translation piece
            if insertion_symbol not in unit_translation:
                return
            # add piece data to collection of vetted elements
            vetted_translation.append((unit_translation, unit_index))
            
        # expect no structural unit left untranslated
        if set([piece[1] for piece in vetted_translation]) != set(range(len(structure))):
            return
        
        return vetted_translation

    def add(self, name="", structure=None, translation=None, all_or_none=False):
        """Add a named sentence type with a sequence of units in the sentence"""
        # check for existing sentence type name and sequence of units
        if not name or name in self.sentences or not isinstance(structure, (list, tuple)):
            print("Failed to add sentence - expected valid name and structure")
            return
        
        # create the sentence's units structure sequence
        vetted_structure = self.vet_structure(structure)
        vetted_translation = self.vet_translation(translation, structure)
        if not vetted_structure:
            raise ValueError(f"Sentences failed to add {name} - invalid sentence structure {structure}")
        if vetted_translation is None:
            raise ValueError(f"Sentences failed to add {name} - invalid translation {translation}")
        
        # add units structure to sentences
        self.sentences[name] = vetted_structure
        self.translations[name] = vetted_translation

        return name

    def update(self, name, structure=None, translation=None, all_or_none=False):
        """Modify the unit sequence of a single named sentence type"""
        # check that the sentence type already exists
        if not self.get(name):
            print(f"Sentences update failed - unrecognized sentence name {name}")
            return
        
        # create valid units structure and translation
        vetted_structure = self.vet_structure(structure)
        vetted_translation = self.vet_translation(translation, structure)
        
        # back out of update if nothing to modify
        if not vetted_structure and vetted_translation is None:
            print(f"Sentences update failed - no valid translation or structure supplied")
            return

        # overwrite named sentence's units structure
        if vetted_structure:
            self.sentences[name] = vetted_structure
        if vetted_translation:
            self.translations[name] = translation

        return name

    def rename(self, name, new_name):
        """Change the name (id) of a stored sentence"""
        # check that named sentence exists and new name does not
        if not self.get(name) or self.get(new_name):
            return
        
        # remap both structure and translation to new name
        structure = self.sentences.pop(name)
        translation = self.translations.pop(name)
        self.sentences[new_name] = structure
        self.translations[new_name] = translation

        return new_name
    
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
        translation = self.get_translation(name)
        if not sentence or translation is None:
            print(f"Failed to apply unidentified sentence named {name}")
            return

        # expect full entries instead of tying this to dictionary with lookups
        # TODO: high-level sentence methods with lookups from the Language
        fetched_words = [
            entry for entry in headwords
            if isinstance(entry, dict) and set(entry).issuperset({'pos', 'sound', 'definition'}) 
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
        # peel apart unit-per-unit translation strings and unit reference indexes
        if translation:
            applied_translation, translation_indexes = list(zip(*translation))
            applied_translation = list(applied_translation)

        # iterate through both sentence units and headwords
        # - unit structure is (word_classes, properties)
        # - headwords is a map containing various representations of word and data
        for i, unit in enumerate(sentence):
            word_data = fetched_words[i]
            word_sounds = word_data['sound']
            word_pos = word_data['pos']
            word_definition = word_data['definition']
            unit_pos, unit_properties = unit
            # compare headword class to expected word class
            if word_pos not in unit_pos:
                #print(fetched_words)
                #print(unit)
                print(f"Failed to apply sentence - word {word_sounds} part of speech {word_pos} does not match expected word class {unit_pos}")
                return
            # create grammatical unit with headword and sentence unit properties
            built_unit = self.grammar.build_unit(
                word_sounds,
                properties=unit_properties,
                word_classes=word_pos
            )
            # add spacing separator and unit to sentence
            len(applied_sentence) > 0 and applied_sentence.append(spacing) 
            [applied_sentence.append(unit_piece) for unit_piece in built_unit]

            # Translate the unit
            # step ahead if nothing to translate
            if not translation:
                continue
            # locate unit's related translation piece
            translation_index = translation_indexes.index(i)
            # format with headword at insertion symbol (see vet_translation)
            formatted_translation = applied_translation[translation_index].format(word_definition)
            applied_translation[translation_index] = formatted_translation

        # format and return sentence representation
        sentence_data = {
            'sound': applied_sentence,
            'change': applied_sentence, # TODO: run sound changes, s/c blocking spaces
            'translation': applied_translation if translation else []
        }
        return sentence_data
