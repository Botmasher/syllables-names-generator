from ..grammar.grammar import Grammar
from ..phonetics.phonetics import Phonetics
from ..phonology.phonology import Phonology
from ..lexicon.dictionary import Dictionary
import random

# NOTE: throughout the code "ipa" (usu uncaps) denotes any stored phonetic symbols
# associated with a set of features in a language

# TODO: consider layering spelling & sound change before storing vs when requested
#   - fast access when computed then stored
#   - computing on request avoids updated letters/rules leaving legacy sounds/spellings

# Shape of stored language data:
# dictionary : {
#   ("word", 0): {          # entry headword, index
#       'phones': "",       # phonemes generated for the word
#       'change': "",       # phones after sound change rules applied
#       'spelling': "",     # letters after spelling applied
#       'rules': [],        # list of ids for sound change rules applied
#       'word_class': "",   # part of speech used for word grammar
#       'definition': "",   # user-inputted string defining the word (built automatically for exponents)
#       'tags': []          # semantic tags for searching for the word
#       'exponent': ""      # id pointing to attributes if grammatical piece
#   },
#   ...
# }
# 
# units / corpus : {
#   'example_id': {
#       'phones': ""            # string containing the built unit example phones
#       'change': ""            # string after sound changes applied
#       'boundaries': True      # whether sound change applied across boundaries
#       'spelling': ""          # string after spelling applied
#       'spell_change': True    # whether spelling applied after sound changes
#       'exponents': []         # exponents attached to this unit
#   },
#   ...
# }
#
# TODO: lay out patterns for exponents around base
# paradigms : {
# }

# TODO: language-level methods atop various components to check then pass through
# - handle feature checks in language instead of shared Features dependency
#   - check before passing non C xor V to syll
#   - check before adding consonant or vowel to inventory
#   - check before adding features to phone
# - language dictionary storing created words and definitions
# - set up default letters and symbols
# - have language check inventory, environment, rules
#   - e.g. avoid ['smiles', '_', 'sauce'] allow ['vowel', '_', 'vowel']
#   - '0', '#' when applying rules
# - see tasks within other class files

class Language:
    def __init__(self, name="", display_name=""):
        self.name = name
        self.display_name = display_name
        # ipa (sound symbols) and features
        self.phonetics = Phonetics()
        # word classes, properties, exponents
        self.grammar = Grammar()
        # phonemes and syllables atop phonetics
        self.phonology = Phonology(self.phonetics)
        # words with ipa, morphology, definition
        self.dictionary = Dictionary()

    def rename(self, name="", display_name=""):
        """Set the id name or display name for the language"""
        self.name = name if name else self.name
        self.display_name = display_name if display_name else self.display_name
        return {
            'name': self.name,
            'display_name': self.display_name
        }

    # TODO: send built sounds back up here to store them in dictionary
    #   - otherwise must pass language/dictionary down to phonology to store

    # TODO: send built grammar back up here to cache in a history
    def generate(self, num_syllables=None, definition="", pre=False, post=False, bound=False, properties=None, word_classes=None):
        if not num_syllables:
            num_syllables = random.randrange(1, 4)
        else:
            if not isinstance(num_syllables, int):
                return
        word = self.phonology.build_word(length=num_syllables)
        # TODO: handle dictionary here not in phonology
        #   - citation forms?
        # TODO: also dictionary but including exponents (corpus?)
        # TODO: sound changes
        #   - before vs after?
        #   - 
        return self.grammar.build_unit(word, properties=properties, word_classes=word_classes)
        
    def attach(self, word=None, definition=None, entry_index=0, properties=None, word_classes=None):
        # - iterate through grammar for that part of speech
        # - produce a unit
        # - or produce a table of all possible forms
        # - store the unit in the corpus
    
        # TODO: lookup by definition or headword
        # TODO: store word classes in dictionary
        definition and self.dictionary.search
        word and self.dictionary.lookup(headword=word, entry_index=entry_index)
        # TODO: build up around found word
        self.grammar.build_unit(word, properties, word_classes)

    # TODO: generate and store examples in either dictionary or corpus
    #   - take in a definition
    #   - take in a word class
    #   - for grammar, send to corpus and 
    #   - also store grammar in dictionary but with exponent id
    #   - should results of sound changes really be stored? or refs to the rules?
    #   - should separate spellings be stored for changes? or flag for spelling before/after change?
    #   - core idea is to store important data for display but only 
    def store(self):
        self.dictionary.add()
    
