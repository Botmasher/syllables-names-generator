from .language.language import Language

# build empty language
my_language = Language(
    name='Katattahk',
    display_name='Testaroundish'
)

# define phonetics

# TODO: adding features beyond vc/p/m like aspirated breaks
# Phonology.change_symbol unless corresponding feature added
# to all complements, like "unaspirated".
# Organized object instead?
# NOTE: documentation - right now if you really care about a feature
# and it's in one phonetics features set you should have the 
# complement for every other relevant symbol, like unaspirated

my_language.phonetics.add_map({
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
    'pʰ': ['consonant', 'voiceless', 'bilabial', 'stop', 'aspirated'],
    'b': ['consonant', 'voiced', 'bilabial', 'stop'],
    'bʰ': ['consonant', 'voiced', 'bilabial', 'stop', 'aspirated'],
    't': ['consonant', 'voiceless', 'dental', 'alveolar', 'stop'],
    'tʰ': ['consonant', 'voiceless', 'dental', 'alveolar', 'stop', 'aspirated'],
    'd': ['consonant', 'voiced', 'dental', 'alveolar', 'stop'],
    'dʰ': ['consonant', 'voiced', 'dental', 'alveolar', 'stop', 'aspirated'],
    'k': ['consonant', 'voiceless', 'velar', 'stop'],
    'kʰ': ['consonant', 'voiceless', 'velar', 'stop', 'aspirated'],
    'g': ['consonant', 'voiced', 'velar', 'stop'],
    'gʰ': ['consonant', 'voiced', 'velar', 'stop', 'aspirated'],
    'q': ['consonant', 'voiceless', 'uvular', 'stop'],
    'ɢ': ['consonant', 'voiced', 'uvular', 'stop'],
    'ʔ': ['consonant', 'voiceless', 'glottal', 'stop'],
    'm': ['consonant', 'voiced', 'bilabial', 'nasal'],
    'ɱ': ['consonant', 'voiced', 'labiodental', 'nasal'],
    'n': ['consonant', 'voiced', 'alveolar', 'nasal'],
    'ɲ': ['consonant', 'voiced', 'palatal', 'nasal'],
    'ŋ': ['consonant', 'voiced', 'velar', 'nasal'],
    'ɴ': ['consonant', 'voiced', 'uvular', 'nasal'],
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
    'r': ['consonant', 'voiced', 'alveolar', 'rhotic', 'trill', 'liquid'],
    'ɾ': ['consonant', 'voiced', 'alveolar', 'rhotic', 'tap', 'liquid'],
    'l': ['consonant', 'voiced', 'alveolar', 'lateral', 'approximant', 'liquid'],
    'ɬ': ['consonant', 'voiceless', 'alveolar', 'lateral', 'fricative'],
    'ɮ': ['consonant', 'voiced', 'alveolar', 'lateral', 'fricative'],
    'j': ['consonant', 'voiced', 'palatal', 'approximant', 'glide'],
    'w': ['consonant', 'voiced', 'velar', 'approximant', 'glide']
})

# inventory to language
my_language.phonology.add_sounds({
    'a': ['a', 'ah'],
    'i': ['i', 'ie'],
    'u': ['u'],
    'p': ['p', 'b'],
    'pʰ': ['bh'],
    'f': ['ph'],
    't': ['t', 'd'],
    'tʰ': ['dh'],
    'θ': ['th'],
    'k': ['k', 'g'],
    'kʰ': ['gh'],
    'x': ['kh', 'hh'],
    'f': ['kh', 'hh'],
    's': ['s'],
    'ts': ['ds'],
    'j': ['y'],
    'n': ['n'],
    'm': ['m']
})

# NOTE: three methods for getting features for an IPA char
#   - Inventory.get_features reads local inventory dict listing letters by feature
#   - Features.get_features retrieves list of feature keys where sound exists in set
#   - Language.get_sound_features wraps the features (NOT inventory) method
#       - but only for phonemes in the language

# TEST: features by ipa and ipa by features readable from Features instance
print(my_language.phonetics.map_by_ipa())
print(my_language.phonetics.map_by_features())

# TEST: special symbols like β and two-char ones like ts are readable and have correct features
print(my_language.phonetics.get_features('ts'))
print(my_language.phonetics.get_features('β'))

# TODO: weight syllables for frequency during generation, like CV > V
my_language.phonology.syllables.add('CVC')
my_language.phonology.syllables.add('VC')
my_language.phonology.syllables.add('CV')
# TODO: add word shapes, like initial VCV but not mid CVVCV

## TEST: run rules (independent of above features, inventory, lang)
my_language.phonology.add_rule(['voiceless'], ['voiced'], 'V_V')
my_language.phonology.add_rule(['stop'], ['fricative'], 'V_V')

# TODO: spelling layer can change too but if not default to historical

# TODO: sound change to or from silence or zero, like katta > kata
#   - also look for same sounds as last (identical)

print(my_language.phonology.apply_rules("kat"))         # expected: > "kat"
print(my_language.phonology.apply_rules("kata"))        # expected: > "kada" > "ka"
print(my_language.phonology.apply_rules("katta"))       # expected: > "katta"
print(my_language.phonology.apply_rules("akatakatta"))  # expected: > "agadagatta" > "aɣaaɣatta"

## TEST: build word root
word_entry = my_language.generate(length=2, definition="camel")
print(word_entry)

## TEST: add exponents and build units
my_language.grammar.properties.add("number", "singular")
my_language.grammar.properties.add("number", "plural")
my_language.grammar.properties.add("semantic", "doer")
my_language.grammar.word_classes.add("noun")
my_language.grammar.word_classes.add("verb")

# TODO: also parse properties in call to create exponent

# TODO: add exponents then run sound change in case attached
#   - this means the form stored under 'sound' is the main one to pass around
#   - option to change across word boundaries
#   - example: if create root vafiv and attach is-, voicing changes the whole to izvaviv

# TODO: logic of inner vs outer (including inconsistencies building with pre vs post)
#   - am I adding elements that are to the exponent's inner?
#   - or am I adding elements the exponent is inner to?
# - resolution: 

plural_s = my_language.grammar.exponents.add(post="s", properties={'number': "plural"})
doer_er = my_language.grammar.exponents.add(post="er", properties={'semantic': "doer"})

my_language.grammar.morphosyntax.add_exponent_order(plural_s, inner=doer_er)
healers = my_language.grammar.build_unit("heal", properties="plural doer")
print(healers)

my_language.grammar.properties.add("semantic", "re")
my_language.grammar.properties.add("semantic", "un")
prefix_re = my_language.grammar.exponents.add(pre="re", properties={'semantic': "re"})
prefix_un = my_language.grammar.exponents.add(pre="un", properties={'semantic': "un"})
my_language.grammar.morphosyntax.add_exponent_order(prefix_un, inner=prefix_re)
unrehealers = my_language.grammar.build_unit("heal", properties="plural re un doer")
print(unrehealers)

# TODO: handle circumfixes - attaching material gets interlaced
#   - currently all pres attach first then all posts
#   - evaluate circumfix pieces individually for both post and pre inners/outers

my_language.grammar.properties.add("semantic", "circumfix1")
my_language.grammar.properties.add("semantic", "circumfix2")
circumfix1 = my_language.grammar.exponents.add(
    pre="circum1-",
    post="-fix1",
    properties={'semantic': "circumfix1"}
)
circumfix2 = my_language.grammar.exponents.add(
    pre="circum2-",
    post="-fix2",
    properties={'semantic': "circumfix2"}
)
#my_language.grammar.morphosyntax.add_exponent_order(circumfix2, inner=[circumfix1, prefix_un, prefix_re])
my_language.grammar.morphosyntax.add_exponent_order(circumfix1, outer=circumfix2, inner=[prefix_un, plural_s])
circum_unrehealers_fix = my_language.grammar.build_unit(
    "heal",
    properties="plural doer un circumfix2 re circumfix1"
)
print(circum_unrehealers_fix)

my_language.grammar.properties.add("semantic", "exponent1")
my_language.grammar.properties.add("semantic", "exponent2")
my_language.grammar.properties.add("semantic", "exponent3")
my_language.grammar.properties.add("semantic", "exponent4")
exponent1 = my_language.grammar.exponents.add(pre="exponent1", properties={'semantic': 'exponent1'})
exponent2 = my_language.grammar.exponents.add(pre="exponent2", properties={'semantic': 'exponent2'})
exponent3 = my_language.grammar.exponents.add(pre="exponent3", properties={'semantic': 'exponent3'})
exponent4 = my_language.grammar.exponents.add(pre="exponent4", properties={'semantic': 'exponent4'})
my_language.grammar.morphosyntax.add_exponent_order(exponent3, inner=exponent4)
my_language.grammar.morphosyntax.add_exponent_order(exponent2, outer=exponent1, inner=exponent3)
exponents123 = my_language.grammar.build_unit(
    " ",
    properties="exponent2 exponent1 exponent4 exponent3"
)
print(exponents123)

# NOTE: grammar will find the optimal exponent providing requested properties
my_language.grammar.exponents.add(post="(eclipsed both -s & -er)", bound=False, properties={
    'number': "plural",
    'semantic': "doer"
})
print(my_language.grammar.build_unit("heal", properties="doer plural"))

# TODO: compounding (plus or minus exponents)

# Generate many words - added to original example above
definitions = [
    ("camel", 2),
    ("dog", 2),
    ("cat", 2),
    ("house", 2),
    ("bridge", 1),
    ("water", 1),
    ("person", 2),
    ("star", 3),
    ("ocean", 2),
    ("mountain", 2),
    ("in, on, among", 1),
    ("with (comitative)", 1),
    ("with (instrumental)", 1)
]
for word_params in definitions:
    my_language.generate(
        definition = word_params[0],
        length = word_params[1]
    )
my_language.grammar.properties.add("case", "instrumental")
my_language.grammar.properties.add("case", "comitative")
search_results = my_language.vocabulary.search(keywords="instrumental")
entry = my_language.vocabulary.lookup(*search_results[0])
print(entry)

# my_language.add_grammar(
#     *search_results[0],
#     post=entry['sound'],
#     properties="instrumental comitative",
#     word_classes="noun",
#     bound=True
# )

my_language.syllables_min_max(1, 3)

search_results = my_language.vocabulary.search(keywords="instrumental")
entry = my_language.vocabulary.lookup(*search_results[0])
print(entry)


# Make sentences

# add verb properties for full sentence
my_language.grammar.properties.add("aspect", "perfective")
my_language.grammar.properties.add("aspect", "imperfective")
my_language.grammar.properties.add("mood", "realis")
my_language.grammar.properties.add("mood", "irrealis")
my_language.grammar.properties.add("case", "nominative")
my_language.grammar.properties.add("case", "accusative")

# create exponents
my_language.generate(
    length = 1,     
    post = True,
    bound = True,
    properties = "perfective realis",
    word_class = "verb"
)
my_language.generate(
    length = 1,     
    post = True,
    bound = True,
    properties = "nominative",
    word_class = "noun"
)
my_language.generate(
    length = 1,     
    post = True,
    bound = True,
    properties = "accusative",
    word_class = "noun"
)

# generate words and look up headwords
my_language.syllables_min_max(2, 4)     # TODO: separate exponent min max
generated_verb = my_language.generate(
    definition = "run around",
    word_class = "verb"
)
generated_subject = my_language.generate(
    definition = "wolf",
    word_class = "noun"
)
generated_object = my_language.generate(
    definition = "sheep",
    word_class = "noun"
)
v = my_language.vocabulary.lookup(*generated_verb)
s = my_language.vocabulary.lookup(*generated_subject)
o = my_language.vocabulary.lookup(*generated_object)

# create and apply sentence
my_language.grammar.sentences.add(
    name = "basic:transitive",
    structure = [
        ["noun", "nominative"],
        ["noun", "accusative"],
        ["verb", "perfective realis"]
    ],
    translation=[
        ("The {}", 0),
        ("did {}", 2),
        ("the {}.", 1)
    ]
)
# TODO: make composable like ability to embed units (definite + noun)
sentence = my_language.grammar.sentences.apply(
    name = "basic:transitive",
    headwords = [s, o, v]
)
print(sentence)
print("".join(sentence['sound']))
print(" ".join(sentence['translation']))


# Phonotactics
# TODO: if dependency points back to scale, allow choices at or beyond that point
my_language.phonology.syllables.phonotactics.add_nucleus("V")
my_language.phonology.syllables.phonotactics.add_nucleus("vowel", "glide")
my_language.phonology.syllables.phonotactics.add_nucleus(["vowel"], ["vowel", "close"])
my_language.phonology.syllables.phonotactics.hierarchy.add(
    "stop", "fricative", "nasal", "approximant", "liquid", "glide"
)
my_language.phonology.syllables.phonotactics.hierarchy.depend("sibilant", "stop")
my_language.phonology.syllables.phonotactics.hierarchy.depend("sibilant", "fricative")
my_language.phonology.syllables.phonotactics.hierarchy.depend("stop", "liquid")
my_language.phonology.syllables.phonotactics.hierarchy.depend("stop", "glide")
my_language.phonology.syllables.phonotactics.hierarchy.depend("fricative", "liquid")
my_language.phonology.syllables.phonotactics.hierarchy.depend("approximant", None)
my_language.phonology.syllables.phonotactics.hierarchy.depend("liquid", None)
my_language.phonology.syllables.phonotactics.hierarchy.depend("fricative", "glide")
my_language.phonology.syllables.phonotactics.hierarchy.depend("voiceless", "voiceless")
my_language.phonology.syllables.phonotactics.hierarchy.depend("voiced", "voiced")

my_language.phonology.syllables.add(
    "V", "CV", "CCV", "CCCV", "CCCV", "CCVC", "CCCVCCC", "CCCCVCCCC"
)
syllable = my_language.phonology.syllables.phonotactics.shape("V")
print(f"V syllable: {syllable}")
syllable = my_language.phonology.syllables.phonotactics.shape("CV")
print(f"CV syllable: {syllable}")
syllable = my_language.phonology.syllables.phonotactics.shape("CCV")
print(f"CCV syllable: {syllable}")
syllable = my_language.phonology.syllables.phonotactics.shape("CCVC")
print(f"CCVC syllable: {syllable}")
syllable = my_language.phonology.syllables.phonotactics.shape("CCCVCCC")
print(f"CCVCCC syllable: {syllable}")
syllable = my_language.phonology.syllables.phonotactics.shape("CCCV")
print(f"CCCV syllable: {syllable}")
syllable = my_language.phonology.syllables.phonotactics.shape("CCCCV")
print(f"CCCCV syllable: {syllable}")
syllable = my_language.phonology.syllables.phonotactics.shape("CCCCVCCCC")
print(f"CCCCVCCCC syllable: {syllable}")


# TODO:
#   - [ ] more refined management of syllable building
#       - permitted and avoided consonant clusters
#       - or probabilistically what to (dis)prefer
#   - [ ] change sounds at borders (base beginning/end)
#   - [ ] definitions for sentences
#   - [ ] (test above)

# TODO: check and refine exponent storage
#   - examples (from corpus?) for entries in the dictionary
#       - at least examples for the exponents since they're so out of context otherwise
#   - definitions, are they really shaping up well? what about support for other langs?
#       - already hardcoding terms like "preposition" in Grammar.autodefine despite abstracting "exponent" mechanics
#   - searchability of terms with - or ... in the spelling (see Language.generate when pre/post material exists)
