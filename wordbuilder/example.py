# built and fed to language
from inventory import Inventory
from features import features
from rules import Rules
from language import Language
# instantiated inside language
from affixes import Affixes
from phoneme import Phoneme
from syllable import Syllable
from environment import Environment

# TODO manage syll, phon, env in L as already c Affixes
basic_ipa_features = Features()
basic_ipa_features.add({
    'a': ['vowel', 'front', 'open', 'unrounded'],
    'i': ['vowel', 'front', 'close', 'unrounded'],
    'ə': ['vowel', 'central', 'mid', 'unrounded'],
    'e': ['vowel', 'front', 'close', 'mid', 'unrounded'],
    'o': ['vowel', 'raised', 'mid', 'rounded'],
    'u': ['vowel', 'raised', 'rounded'],
    'p': ['consonant', 'voiceless', 'bilabial', 'stop'],
    'b': ['consonant', 'voiced', 'bilabial', 'stop'],
    't': ['consonant', 'voiceless', 'dental', 'stop'],
    'd': ['consonant', 'voiced', 'dental', 'stop'],
    'k': ['consonant', 'voiceless', 'velar', 'stop'],
    'g': ['consonant', 'voiced', 'velar', 'stop'],
    'ϕ': ['consonant', 'voiceless', 'bilabial', 'fricative'],
    'β': ['consonant', 'voiced', 'bilabial', 'fricative'],
    'f': ['consonant', 'voiceless', 'labiodental', 'fricative'],
    'v': ['consonant', 'voiced', 'labiodental', 'fricative'],
    'θ': ['consonant', 'voiceless', 'dental', 'fricative'],
    'ð': ['consonant', 'voiced', 'dental', 'fricative'],
    'x': ['consonant', 'voiceless', 'velar', 'fricative'],
    'ɣ': ['consonant', 'voiced', 'velar', 'fricative'],
    'tʃ': ['consonant', 'voiceless', 'postalveolar', 'affricate'],
    'dʒ': ['consonant', 'voiced', 'postalveolar', 'affricate'],
})

my_language = Language(
    name='',
    display_name='',
    features=basic_ipa_features,
    inventory=None,
    rules=None
)
