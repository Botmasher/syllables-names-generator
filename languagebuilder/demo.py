from .language.language import Language
from .data.ipa_features import vc_map as ipa_features_map

lang = Language(name="Katatak")

lang.phonetics.add_map(ipa_features_map)
lang.phonology.add_sounds({
    'a': ['ah'],
    'i': ['ie'],
    'u': ['ue'],
    't': ['t'],
    'k': ['k']
})
lang.phonology.add_syllable('CV')
lang.phonology.add_rule('stop', 'fricative', 'V_V')

lang.grammar.word_classes.add("noun")
lang.grammar.properties.add(category='number', grammeme='plural')
lang.grammar.exponents.add(post='ta', properties='plural number', pos='noun')

lang.generate(length=2, definition='wug')
entry = lang.translate('wug', 'plural', 'noun')
[print(f"{k}: {v}") for k,v in entry.items()]
