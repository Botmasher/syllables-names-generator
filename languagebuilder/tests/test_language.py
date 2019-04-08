import unittest
from ..language.language import Language

def setUpModule():
    print("Setting up the Language test module")

def tearDownModule():
    print("Shutting down the Language test module")

class LanguageFixture(unittest.TestCase):
    @classmethod
    def setUpClass(this_class):
        """Instantiate Language for all tests in the class"""
        print("Setting up a Language instance")
        this_class.language = Language("Testianishese")
    
    @classmethod
    def tearDownClass(this_class):
        """"Delete Language instance for tests"""
        print("Tearing down a Language instance")
        this_class.language = None

class LanguageSounds(LanguageFixture):
    @classmethod
    def setUpClass(this_class):
        super(LanguageSounds, this_class).setUpClass()

    def test_add_phone(self):
        self.language.phonetics.add("k", ["voiceless", "velar", "stop",  "consonant"])
        self.assertTrue(
            self.language.phonetics.has_ipa("k"),
            "failed to add a phone to the language"
        )
            
    def test_add_sound(self):
        self.language.phonetics.add("k", ["voiceless", "velar", "stop", "consonant"])
        self.language.phonology.add_sound("k", letters=["q"])
        self.assertTrue(
            self.language.phonology.has_sound("k"),
            "failed to add a phoneme to the language"
        )      

    def test_update_sound(self):
        self.language.phonetics.add("k", ["voiceless", "velar", "stop", "consonant"])
        self.language.phonology.add_sound("k", ["q"])
        self.language.phonology.update_sound("k", letters=["qh"])
        self.assertIn(
            "q",
            self.language.phonology.get_sound_letters("k"),
            "failed to update properties for a phoneme"
        )

    def test_remove_sound(self):
        self.language.phonetics.add("k", ["voiceless", "velar", "stop", "consonant"])
        self.language.phonology.add_sound("k", letters=["q"])
        self.language.phonology.remove_sound("k")
        self.assertTrue(
            self.language.phonetics.has_ipa("k") and not self.language.phonology.has_sound("k"),
            "failed to remove added ipa from phonology while keeping it in the phonetics"
        )  
    
    def test_add_syllable(self):
        syllable_id = self.language.phonology.syllables.add("CVC")
        self.assertTrue(
            self.language.phonology.syllables.has(syllable_id),
            "failed to add a syllable to the language"
        )
    
    def test_update_syllable(self):
        syllable_id = self.language.phonology.syllables.add("CVC")
        self.language.phonology.syllables.update(syllable_id, "CVV")
        self.assertEqual(
            self.language.phonology.syllables.get(syllable_id),
            self.language.phonology.syllables.structure("CVV"),
            "failed to update an existing syllable in the language"
        )

    def test_remove_syllable(self):
        syllable_id = self.language.phonology.syllables.add("CVC")
        self.language.phonology.syllables.remove(syllable_id)
        self.assertFalse(
            self.language.phonology.syllables.has(syllable_id),
            "failed to remove a syllable from the language"
        )

    def test_add_rule(self):
        self.language.phonetics.add("k", ["voiceless", "velar", "stop", "consonant"])
        self.language.phonology.add_sound("k", letters=["q"])
        rule_id = self.language.phonology.add_rule("k", "t", "_")
        self.assertIsNotNone(
            self.language.phonology.get_rule(rule_id),
            "failed to add a sound change rule to the language"
        )

class LanguageGrammar(LanguageFixture):
    @classmethod
    def setUpClass(this_class):
        super(LanguageGrammar, this_class).setUpClass()

    def test_add_property(self):
        self.language.grammar.properties.add("class", "animate")
        self.assertIsNotNone(
            self.language.grammar.properties.properties.get("class", {}).get("animate"),
            "failed to add a grammatical property to the language"
        )

    def test_add_word_class(self):
        self.language.grammar.word_classes.add("noun")
        self.assertIn(
            "noun",
            self.language.grammar.word_classes.word_classes,
            "failed to add a grammatical word class to the language"
        )

    def test_add_exponent(self):
        self.language.grammar.properties.add("aspect", "perfective")
        exponent_id = self.language.grammar.exponents.add(pre="i", post="nei", bound=False, properties="perfective")
        self.assertIsNotNone(
            self.language.grammar.exponents.get(exponent_id),
            "failed to add a grammatical exponent to the language"
        )

class LanguageWords(LanguageFixture):
    @classmethod
    def setUpClass(this_class):
        super(LanguageWords, this_class).setUpClass()
        # set up sounds
        this_class.language.phonetics.add_map({
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
            'ϕ': ['consonant', 'voiceless', 'bilabial', 'fricative'],
            'β': ['consonant', 'voiced', 'bilabial', 'fricative'],
            'f': ['consonant', 'voiceless', 'labiodental', 'fricative'],
            'v': ['consonant', 'voiced', 'labiodental', 'fricative'],
            'θ': ['consonant', 'voiceless', 'dental', 'alveolar', 'fricative'],
            'ð': ['consonant', 'voiced', 'dental', 'alveolar', 'fricative'],
            'x': ['consonant', 'voiceless', 'velar', 'fricative'],
            'ɣ': ['consonant', 'voiced', 'velar', 'fricative']
        })
        this_class.language.phonology.add_sounds({
            'a': ['ah'],
            'i': ['ee'],
            'u': ['oo'],
            'p': ['p'],
            'f': ['hp'],
            't': ['t'],
            'θ': ['ht'],
            'k': ['k'],
            'x': ['hk']
        })
        this_class.language.phonology.syllables.add("CV")
        this_class.language.phonology.add_rule("stop", "fricative", "V_V")
        this_class.language.phonology.add_rule("bilabial fricative", "labiodental fricative", "_")

        # set up grammar
        this_class.language.grammar.properties.add("tense", "future")
        this_class.language.grammar.properties.add("tense", "nonfuture")
        this_class.language.grammar.properties.add("aspect", "perfective")
        this_class.language.grammar.properties.add("aspect", "imperfective")
        this_class.language.grammar.properties.add("number", "singular")
        this_class.language.grammar.properties.add("number", "plural")
        this_class.language.grammar.word_classes.add("noun")
        this_class.language.grammar.word_classes.add("verb")
        this_class.language.grammar.exponents.add(post="-ta", properties="future perfective", pos="verb")
        this_class.language.grammar.exponents.add(post="-ka", properties="future imperfective", pos="verb")
        this_class.language.grammar.exponents.add(post="-fa", properties="nonfuture", pos="verb")
        this_class.language.grammar.exponents.add(pre="0-", properties="singular", pos="noun")
        this_class.language.grammar.exponents.add(pre="pa-", properties="plural", pos="noun")
        
        # TODO: sounds and grammar
        #   - phonetics, inventory, syllables
        #   - word classes, properties, exponents (including ordering)

    def test_generate_root_word(self):
        root_word = self.language.generate(syllables=4, word_class="verb")
        self.assertTrue(
            isinstance(root_word, str) and len(root_word) == 8,
            "failed to generate a new root word in the language"
        )

    def test_generate_grammatical_word(self):
        self.language.grammar.properties.add("category", "grammeme")
        affix = self.language.generate(
            pre=False,
            post=True,
            bound=True,
            syllables=1,
            word_class="verb",
            properties="grammeme"
        )
        self.assertNotIn(
            self.language.grammar.exponents.find(post=affix['post']),
            [[], (), None],
            "failed to generate a new grammatical word in the language"
        )
        
    def test_apply_grammar(self):
        root = self.language.generate(2)
        unit = self.language.attach(
            root,
            word_class="verb",
            properties="imperfective future"
        )
        self.assertEqual(
            unit,
            f"{root}-n",
            "failed to generate a new root + grammatical unit in the language"
        )

    def test_build_unit(self):
        root = self.language.generate(2)
        unit = self.language.attach(root, word_class="verb", properties="imperfective future")
        self.assertEqual(
            unit,
            f"{root}-n",
            "failed to generate a new root + grammatical unit in the language"
        )

    def test_apply_sound_changes(self):
        changed_sounds = self.language.change_sounds("paputaki")
        self.assertEqual(
            changed_sounds,
            "pafuθaxi",
            "failed to change sounds following sound rules in the language"
        )
    
    def test_attach_and_sound_change(self):
        root = "ta"
        unit = self.language.attach(
            root,
            word_class="verb",
            properties="imperfective future",
            change_boundaries=True
        )
        self.assertEqual(
            unit,
            "taxa",
            "failed to build a grammatical unit and change sounds across boundaries"
        )

    def test_spell_word(self):

        return
    
    def test_lookup_word(self):
        return
    
    def test_define_word(self):
        return
    
    def test_search_word(self):
        return

    def test_print_dictionary(self):
        return
    
    def test_read_grammatical_description(self):
        # from properties and word classes
        return
    

    