# built and fed to language
from inventory import Inventory
from features import Features
from language import Language
# instantiated inside language
from affixes import Affixes
from phoneme import Phoneme
from syllable import Syllable
from environment import Environment

## TEST - make features

# TODO manage syll, phon, env in L as already c Affixes
features = Features()
features.add_map({
    'a': ['vowel', 'front', 'open', 'unrounded'],
    'i': ['vowel', 'front', 'close', 'unrounded'],
    'y': ['vowel', 'front', 'close', 'rounded'],
    'ə': ['vowel', 'central', 'mid', 'unrounded'],
    'e': ['vowel', 'front', 'close', 'mid', 'unrounded'],
    'ɑ': ['vowel', 'retracted', 'unrounded'],
    'ɒ': ['vowel', 'retracted', 'rounded'],
    'ɔ': ['vowel', 'retracted', 'mid', 'rounded'],
    'o': ['vowel', 'raised', 'mid', 'rounded'],
    'u': ['vowel', 'raised', 'rounded'],
    'p': ['consonant', 'voiceless', 'bilabial', 'stop'],
    'b': ['consonant', 'voiced', 'bilabial', 'stop'],
    't': ['consonant', 'voiceless', 'dental', 'alveolar', 'stop'],
    'd': ['consonant', 'voiced', 'dental', 'alveolar', 'stop'],
    'k': ['consonant', 'voiceless', 'velar', 'stop'],
    'g': ['consonant', 'voiced', 'velar', 'stop'],
    'q': ['consonant', 'voiceless', 'uvular', 'stop'],
    'ɢ': ['consonant', 'voiced', 'uvular', 'stop'],
    'ʔ': ['consonant', 'voiceless', 'glottal', 'stop'],
    'ϕ': ['consonant', 'voiceless', 'bilabial', 'fricative'],
    'β': ['consonant', 'voiced', 'bilabial', 'fricative'],
    'f': ['consonant', 'voiceless', 'labiodental', 'fricative'],
    'v': ['consonant', 'voiced', 'labiodental', 'fricative'],
    'θ': ['consonant', 'voiceless', 'dental', 'alveolar', 'fricative'],
    'ð': ['consonant', 'voiced', 'dental', 'alveolar', 'fricative'],
    'ʃ': ['consonant', 'voiceless', 'postalveolar', 'fricative'],
    'ʒ': ['consonant', 'voiced', 'postalveolar', 'fricative'],
    'x': ['consonant', 'voiceless', 'velar', 'fricative'],
    'ɣ': ['consonant', 'voiced', 'velar', 'fricative'],
    'χ': ['consonant', 'voiceless', 'uvular', 'fricative'],
    'ʁ': ['consonant', 'voiced', 'uvular', 'fricative'],
    'h': ['consonant', 'voiceless', 'glottal', 'fricative'],
    'ɦ': ['consonant', 'voiced', 'glottal', 'fricative'],
    's': ['consonant', 'voiceless', 'alveolar', 'sibilant'],
    'z': ['consonant', 'voiced', 'alveolar', 'sibilant'],
    'ts': ['consonant', 'voiceless', 'alveolar', 'affricate'],
    'dz': ['consonant', 'voiced', 'alveolar', 'affricate'],
    'tʃ': ['consonant', 'voiceless', 'postalveolar', 'affricate'],
    'dʒ': ['consonant', 'voiced', 'postalveolar', 'affricate'],
    'r': ['consonant', 'voiced', 'alveolar', 'trill'],
    'ɾ': ['consonant', 'voiced', 'alveolar', 'tap'],
    'ɬ': ['consonant', 'voiceless', 'alveolar', 'lateral', 'fricative'],
    'ɮ': ['consonant', 'voiced', 'alveolar', 'lateral', 'fricative'],
    'j': ['consonant', 'voiced', 'palatal', 'approximant'],
    'w': ['consonant', 'voiced', 'velar', 'approximant']
})
# TODO solve feature 'consonant'/'vowel' not getting into features inventory
print(features.map_by_features())

## TEST - use above features to build lang and sylls
inventory = Inventory()

my_language = Language(
    name='Testerlangubekke',
    display_name='Testaroundish',
    features=features,
    inventory=inventory
)

my_language.add_sounds({
    'a': ['a', 'ah'],
    'i': ['i', 'ie'],
    'u': ['u'],
    'p': ['p', 'b'],
    'f': ['ph'],
    't': ['t', 'd'],
    'θ': ['th'],
    'k': ['k', 'g'],
    'x': ['kh', 'hh'],
    's': ['s'],
    'ts': ['ds']
})

# NOTE three methods for getting features for an IPA char
#   - Inventory.get_features reads local inventory dict listing letters by feature
#   - Features.get_features retrieves list of feature keys where sound exists in set
#   - Language.get_sound_features wraps the features (NOT inventory) method
#       - but only for phonemes in the language

# # TODO special symbols like β and two-char ones like ts not getting features
# print(my_language.features.get_features('i'))
# print(my_language.features.get_features('β'))
# #print(my_language.features.features)
#
# # TODO have inventory tie features to chars, and do the add sounds instead of language
# #print(my_language.phonemes)     # recall this is a dict of ipa:phoneme pairs
# print(my_language.get_sound_features('i'))
#
# # TODO weight syllables so CV > just V
# my_language.add_syllable('CVC')
# my_language.add_syllable('VC')
# my_language.add_syllable('CV')
# my_language.print_syllables()

# TODO add word shapes (root, affixes, compounds, or initial VCV but not mid CVVCV)


## TEST - run rules (independent of above features, inventory, lang)
my_language.add_rule(['voiceless'], ['voiced'], 'V_V')
# /!\ inventory lacks relevant sounds for this rule
#   - TODO: handle this case better
#my_language.add_rule(['voiced', 'stop'], ['voiced', 'fricative'], 'V_V')
print(my_language.apply_rules("kat"))    # expected: "kat", got: ""
print(my_language.apply_rules("kata"))   # expected: "kada", got: ""
print(my_language.apply_rules("katta"))  # expected: "katta", got: ""
