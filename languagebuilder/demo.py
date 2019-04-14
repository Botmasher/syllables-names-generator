from .language.language import Language
from .data.ipa_features import vc_map as ipa_features_map

katatak = Language(name="Katatak")

katatak.phonetics.add_map(ipa_features_map)

katatak.phonology.add_sounds({
    'a': ['ah'],
    'i': ['ie'],
    'u': ['ue', 'oo'],
    't': ['t'],
    'k': ['k']
})
katatak.phonology.add_syllable('CV')
test_word = katatak.phonology.build_word(length=3)
print(test_word)

katatak.phonology.add_rule('stop', 'fricative', 'V_V')
word = katatak.generate(length=2, definition='wug')
entry = katatak.dictionary.lookup(*word)[0]
print(entry)

katatak.grammar.properties.add('number', 'plural')
katatak.grammar.exponents.add(post='ta', properties='plural')
unit = katatak.attach(*word, 'plural')
print(unit)