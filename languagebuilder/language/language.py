from ..grammar.grammar import Grammar
from ..phonetics.phonetics import Phonetics
from ..phonology.phonology import Phonology
from ..lexicon.dictionary import Dictionary
import random

# NOTE: throughout the code "ipa" (usu uncaps) denotes any stored phonetic symbols
# associated with a set of features in a language

# TODO: consider layering spelling & sound change before storing vs when requested
#   NOTE:   similar update problems when syllables or phonemes change anyhow; how
#           consistent do you want updates/stores to be compared to structures?
#   - fast access when computed then stored
#   - computing on request avoids updated letters/rules leaving legacy sounds/spellings
#   - similar consideration to storing exponents though!
#   - instead could have update functions through language
#       - these manage both storage and manipulation

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
    def generate(self, length=None, definition="", spell_after_change=False, pre=False, post=False, bound=False, properties=None, word_classes=None):
        # choose a random number of syllables if no syllable count supplied
        if not length:
            length = random.randrange(1, 5)
        # verify that syllable count is a whole number
        if not isinstance(length, int):
            print(f"Language failed to generate word - invalid number of syllables {length}")
            return
        
        # generate the created phonemes in syllables
        word = self.phonology.build_word(length=length)

        # add as a grammatical word piece
        if pre or post:
            # determine word to attach before or after
            pre_word = word if pre else ""
            post_word = word if post else ""
            # generate a second word piece for circum material
            if pre and post:
                post_word = self.phonology.build_word(length=length)
            # create the exponent
            self.grammar.exponents.add(
                pre=pre_word,
                post=post_word,
                properties=properties,
                bound=bound,
                pos=word_classes
            )
            pre_change = ""
            post_change = ""
            pre_spelling = ""
            post_spelling = ""
            grammatical_forms = {
                (True, True, True): "circumfix",
                (True, False, True): "prefix",
                (True, False, False): "suffix",
                (False, True, True): "circumposition",
                (False, False, True): "preposition",
                (False, False, False): "postposition"
            }
            grammatical_form = grammatical_forms[(bound, pre and post, pre)]
            
            # TODO: apply sound and spelling changes to grammatical pieces

            # TODO: use exponents to create a formatted properties and word class string

            formatted_word = f"{pre_word}{"- -" if pre and post else "-"}{post_word}"
            formatted_spelling = f"{pre_spelling}{"- -" if pre and post else "-"}{post_spelling}"
            formatted_change = f"{pre_change}{"- -" if pre and post else "-"}{post_change}"
            formatted_definition = f"{grammatical_form} for {properties} {word_classes}"
        else:
            formatted_word = word
            formatted_definition = definition.strip()

        # store created word or word piece and return lookup info
        return self.store(formatted_word, formatted_definition, formatted_change, formatted_spelling)
        
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
    def store(self, word, definition):
        self.dictionary.add()
    
