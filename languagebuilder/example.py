from .phonology.features import Features
from .language.language import Language

## TEST - make features
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

# TEST - build empty language
my_language = Language(
    name='Testerlangubekke',
    display_name='Testaroundish',
    features=features
)

# TEST - add inventory to language
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

# TEST - features by ipa and ipa by features readable from Features instance
print(my_language.features.map_by_ipa())
print(my_language.features.map_by_features())

# TEST - special symbols like β and two-char ones like ts are readable and have correct features
print(my_language.features.get_features('ts'))
print(my_language.features.get_features('β'))
#
# # TODO have inventory tie features to chars, and do the add sounds instead of language
# #print(my_language.phonemes)     # recall this is a dict of ipa:phoneme pairs
# print(my_language.get_sound_features('i'))
#
# # TODO weight syllables so CV > just V
my_language.add_syllable('CVC')
my_language.add_syllable('VC')
my_language.add_syllable('CV')
my_language.print_syllables()
# TODO add word shapes (root, affixes, compounds, or initial VCV but not mid CVVCV)

## TEST - run rules (independent of above features, inventory, lang)
my_language.add_rule(['voiceless'], ['voiced'], 'V_V')
# TODO spelling layer can change too but if not default to historical
print(my_language.apply_rules("kat"))    # expected: "kat", got: "kat"
print(my_language.apply_rules("kata"))   # expected: "kada", got: "kada"
print(my_language.apply_rules("katta"))  # expected: "katta", got: "katta"
print(my_language.apply_rules("akatakatta"))  # expected: "agadagatta", got: "agadagatta"

## TEST - build root word
word_entry = my_language.build_word(length=2, definition="camel")
print(word_entry)

## TEST - add affixes and build words with them
my_language.grammar.properties.add("number", "singular")
my_language.grammar.properties.add("number", "plural")
my_language.grammar.properties.add("semantic", "doer-person")
my_language.grammar.word_classes.add("noun")
my_language.grammar.word_classes.add("verb")
plural_s = my_language.grammar.exponents.add(post="s", properties="plural noun")
gerund_ing = my_language.grammar.exponents.add(post="er", properties="gerund")
my_language.grammar.morphosyntax.add_exponent_order(plural_s, inner=gerund_ing)
healers = my_language.grammar.build_unit("heal", properties="plural doer-person")
print(healers)

# TODO: compounding (plus or minus exponents)
