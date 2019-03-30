from ..grammar.grammar import Grammar
from ..phonetics.phonetics import Phonetics
from ..phonology.phonology import Phonology
from ..lexicon.dictionary import Dictionary
import random

# NOTE: throughout the code "ipa" (usu uncaps) denotes any stored phonetic symbols
# associated with a set of features in a language

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
    def generate(self, definition="", num_syllables=None, properties=None, word_classes=None):
        num_syllables = random.randrange(1, 4)
        root = self.phonology.build_word(length=num_syllables)
        # TODO: handle dictionary here not in phonology
        #   - citation forms?
        # TODO: also dictionary but including exponents (corpus?)
        return self.grammar.build_unit(root, properties=properties, word_classes=word_classes)
        
