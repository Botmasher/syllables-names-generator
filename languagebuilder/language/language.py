from ..grammar.grammar import Grammar
from ..phonology.phonology import Phonology
from ..lexicon.dictionary import Dictionary

# NOTE: throughout the code "ipa" (usu uncaps) denotes any stored phonetic symbols
# associated with a set of features in a language

# TODO
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
        self.grammar = Grammar()        # word classes, properties, exponents
        self.phonology = Phonology()    # phonemes and syllables, atop "phonetics"
        self.dictionary = Dictionary()  # words with ipa, morphology, definition

    def rename(self, name="", display_name=""):
        self.name = name if name else self.name
        self.display_name = display_name if display_name else self.display_name
        return {
            'name': self.name,
            'display_name': self.display_name
        }
    
    # TODO: send built sounds back up here to store them in dictionary
    #   - otherwise must pass language/dictionary down to phonology to store

    # TODO: send built grammar back up here to cache in a history

