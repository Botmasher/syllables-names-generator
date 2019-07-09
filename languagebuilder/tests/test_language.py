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
        self.language.phonology.update_sound("k", letters=["q", "qh"])
        self.assertIn(
            "qh",
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
            self.language.grammar.properties.get("class", "animate"),
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
        this_class.language.phonology.add_rule("bilabial fricative", "labiodental fricative", "V_V")
        
        # set up grammar
        this_class.language.grammar.properties.add("tense", "future")
        this_class.language.grammar.properties.add("tense", "nonfuture")
        this_class.language.grammar.properties.add("aspect", "perfective")
        this_class.language.grammar.properties.add("aspect", "imperfective")
        this_class.language.grammar.properties.add("number", "singular")
        this_class.language.grammar.properties.add("number", "plural")
        this_class.language.grammar.word_classes.add("noun")
        this_class.language.grammar.word_classes.add("verb")
        this_class.language.grammar.exponents.add(post="ta", properties="future perfective", pos="verb")
        this_class.language.grammar.exponents.add(post="ka", properties="future imperfective", pos="verb")
        this_class.language.grammar.exponents.add(post="fa", properties="nonfuture", pos="verb")
        
        # TODO: sounds and grammar
        #   - phonetics, inventory, syllables
        #   - word classes, properties, exponents (including ordering)

    def test_generate_root_word(self):
        root_word = self.language.generate(length=4, word_class="verb")[0]
        self.assertTrue(
            isinstance(root_word, str) and len(root_word) >= 8,
            "failed to generate a new root word in the language"
        )

    def test_generate_grammatical_word(self):
        self.language.grammar.properties.add("category", "grammeme")
        affix = self.language.generate(
            length=1,
            pre=False,
            post=True,
            bound=True,
            word_class="verb",
            properties="grammeme"
        )
        self.assertIsNotNone(
            affix.get('spelling'),
            "failed to generate a new grammatical word in the language"
        )

    def test_generate_grammatical_infix(self):
        self.language.grammar.properties.add("category", "infix0")
        affix = self.language.generate(
            length=2,
            pre=False,
            mid=True,
            post=False,
            bound=True,
            word_class="noun",
            properties="infix0"
        )
        self.assertIsNotNone(
            affix.get('spelling'),
            "failed to generate a grammatical infix in the language"
        )

    def test_apply_grammar(self):
        base = self.language.generate(2)
        base_entry = self.language.vocabulary.lookup(*base)
        unit = self.language.attach(
            *base,
            properties="imperfective future",
            word_classes="verb"
        )
        self.assertEqual(
            "".join(unit['sound']),
            "".join(base_entry['sound']) + "ka",
            "failed to generate a new root + grammatical unit in the language"
        )

    def test_apply_grammatical_infix(self):
        self.language.grammar.properties.add("category", "infix1")
        affix = self.language.generate(
            length=1,
            mid=True,
            bound=True,
            word_class="noun",
            properties="infix1"
        )
        # TODO: have midpoint count num input sylls not resulting sounds
        base = self.language.generate(2, midpoint=1)
        base_entry = self.language.vocabulary.lookup(*base)       
        unit = self.language.attach(
            *base,
            properties="infix1",
            word_classes="noun"
        )
        # build word with infix for comparison
        expected_unit = base_entry['sound'][:2] + affix['sound'] + base_entry['sound'][2:]
        self.assertEqual(
            "".join(unit['sound']),
            "".join(expected_unit),
            "failed to generate and apply a grammatical infix inside of a generated word"
        )

    def test_build_unit(self):
        base = self.language.generate(2)
        base_entry = self.language.vocabulary.lookup(*base)
        unit = self.language.attach(
            *base,
            properties="imperfective future",
            word_classes="verb"
        )
        self.assertEqual(
            "".join(unit['sound']),
            "".join(base_entry['sound']) + "ka",
            "failed to generate a new root + grammatical unit in the language"
        )

    def test_apply_sound_changes(self):
        changed_sounds = self.language.phonology.apply_rules("paputaki")
        self.assertEqual(
            "".join(changed_sounds),
            "pafuθaxi",
            f"failed to change sounds following ordered sound rules in the language"
        )
    
    def test_attach_and_sound_change(self):
        unit = self.language.attach(
            "ta",
            lookup=False,
            word_classes="verb",
            properties="imperfective future"
        )
        self.assertEqual(
            "".join(unit['change']),
            "taxa",
            "failed to build a grammatical unit and change sounds across boundaries"
        )

    def test_spell_word(self):
        word = self.language.generate(2)
        word_entry = self.language.vocabulary.lookup(*word)
        matches = self.language.vocabulary.search(spelling=word_entry['spelling'])
        self.assertIn(
            word,
            matches,
            "failed to spell a newly generated word"
        )
    
    def test_spell_unit(self):
        root = self.language.generate(2)
        unit_entry = self.language.attach(
            root[0],
            root[1],
            word_classes = "verb",
            properties = "imperfective future"
        )
        self.assertIn(
            root[0],
            "".join(unit_entry.get('spelling', "")),
            f"failed to spell a newly generated unit {unit_entry}"
        )
    
    def test_lookup_word(self):
        word = self.language.generate(2, "cat")
        word_entry = self.language.vocabulary.lookup(*word)
        self.assertEqual(
            "".join(word_entry['spelling']),
            word[0],
            "failed to look up a generated word"
        )
    
    def test_define_word(self):
        word = self.language.generate(2, "dog")
        definition = self.language.vocabulary.define(*word)
        self.assertEqual(
            definition,
            "dog",
            "failed to define a generated word"
        )        
    
    def test_search_word(self):
        word_0 = self.language.generate(2, definition="round")
        word_1 = self.language.generate(2, definition="round table")
        self.language.generate(2, definition="table")
        results = self.language.vocabulary.search(keywords="round")
        self.assertTrue(
            len(results) == 2 and word_0 in results and word_1 in results,
            f"failed to find generated words in a keyword search: found {results}"
        )   
    
    def test_read_grammatical_definition(self):
        exponent = self.language.generate(pre=False, post=True, bound=True, properties="imperfective future", word_class="verb")
        definition = exponent['definition']
        exponent_pos = exponent['pos']
        exponent_properties = exponent['properties']
        self.assertEqual(
            definition,
            "suffix for imperfective aspect, future tense verbs",
            f"failed to create a definition for a grammatical piece with properties {exponent_properties} and word class {exponent_pos}"
        )

class LanguageStorage(LanguageFixture):
    @classmethod
    def setUpClass(this_class):
        super(LanguageStorage, this_class).setUpClass()
        
        this_class.language.phonetics.add_map({
            'a': ['vowel', 'front', 'open', 'unrounded', 'short'],
            'aː': ['vowel', 'front', 'open', 'unrounded', 'long'],
            'pʰ': ['consonant', 'voiceless', 'bilabial', 'stop', 'aspirated'],
            'tʰ': ['consonant', 'voiceless', 'dental', 'alveolar', 'stop', 'aspirated'],
            'kʰ': ['consonant', 'voiceless', 'velar', 'stop', 'aspirated']
        })
        this_class.language.phonology.add_sounds({
            'a': ['a'],
            'aː': ['ā'],
            'pʰ': ['p'],
            'tʰ': ['t'],
            'kʰ': ['k']
        })
        this_class.language.phonology.syllables.add("CV")
        this_class.language.phonology.syllables.add("CVC")
        
        this_class.language.grammar.properties.add("category", "default")
        this_class.language.grammar.properties.add("category", "marked")
        this_class.language.grammar.word_classes.add("noun")
        this_class.language.grammar.word_classes.add("verb")
        this_class.language.grammar.exponents.add(post=["a", "pʰ"], properties="marked", pos="noun")
        this_class.language.grammar.exponents.add(post=["a", "kʰ"], properties="marked", pos="verb")

    def test_store_sound_list(self):
        base = self.language.generate(length=3)
        stored_base = self.language.vocabulary.lookup(*base)
        self.assertGreaterEqual(
            len({"pʰ", "tʰ", "kʰ"} & set(stored_base.get('sound', []))),
            1,
            "failed to generate and store a base word entry with sound and spelling lists of single or multicharacter symbols"
        )

    def test_store_generated_base(self):
        base = self.language.generate(length=2, word_class="verb")
        entry = self.language.vocabulary.lookup(*base)
        self.assertIsNotNone(
            entry.get('sound'),
            "failed to generate and store a base word in the language"
        )

class LanguageSoundChanges(LanguageFixture):
    @classmethod
    def setUpClass(this_class):
        super(LanguageSoundChanges, this_class).setUpClass()
        this_class.language.phonetics.add_map({
            'a': ['vowel', 'front', 'open', 'unrounded', 'short'],
            'k': ['consonant', 'voiceless', 'velar', 'stop', 'unaspirated'],
            'kʰ': ['consonant', 'voiceless', 'velar', 'stop', 'aspirated'],
            'g': ['consonant', 'voiced', 'velar', 'stop', 'unaspirated'],
            'gʰ': ['consonant', 'voiced', 'velar', 'stop', 'aspirated']
        })
        this_class.language.phonology.add_sounds({
            'a': ['a'],
            'gʰ': ['g']
        })
        #this_class.language.phonology.syllables.add("VC")
        this_class.language.phonology.add_rule("aspirated", "unaspirated", "V_C")
        this_class.language.phonology.add_rule("aspirated", "unaspirated", "#_")
        this_class.language.phonology.add_rule("aspirated", "unaspirated", "V_#")
        this_class.language.phonology.add_rule("voiced", "voiceless", "#_#")
        this_class.language.phonology.add_rule("voiced", "voiceless", "V_V")
        this_class.language.phonology.add_rule("aspirated", "unaspirated", "V_V")

    # simple change applications

    def test_change_sound_word_end(self):
        sounds = ["a", "a", "gʰ"]
        changed_sounds = self.language.phonology.apply_rules(sounds)
        self.assertEqual(
            "".join(changed_sounds),
            "aag",
            "failed to apply a simple sound change to the last sound in a word"
        )

    def test_change_sound_word_start(self):
        changed_sounds = self.language.phonology.apply_rules(["gʰ", "a", "a"])
        self.assertEqual(
            "".join(changed_sounds),
            "gaa",
            "failed to apply a simple sound change to the first sound in a word"
        )

    def test_change_sound_before_consonant(self):
        changed_sounds = self.language.phonology.apply_rules(["a", "gʰ", "gʰ", "a"])
        self.assertEqual(
            "".join(changed_sounds),
            "aggʰa",
            "failed to apply a simple sound change to the middle of a word"
        )

    def test_change_sound_between_vowels(self):
        changed_sounds = self.language.phonology.apply_rules(["a", "gʰ", "a"])
        self.assertEqual(
            "".join(changed_sounds),
            "aka",
            "failed to apply a simple sound change between vowels"
        )

    def test_change_monophone(self):
        changed_sounds = self.language.phonology.apply_rules(["gʰ"])
        self.assertEqual(
            "".join(changed_sounds),
            "k",
            "failed to change a word containing only a single sound"
        )

    # TODO: compound change applications
    #   - see if various rule orders work

    # sound changes in longer structures (units and sentences)

    def test_change_sounds_within_words(self):
        changed_sounds = self.language.change_sounds(
            ["a", "gʰ", "a", "gʰ", " ", "a", "gʰ"],
            blocked_by_spacing=True
        )
        self.assertEqual(
            changed_sounds,
            ["a", "k", "a", "g", " ", "a", "g"],
            "failed to change sounds of each word in a sentence"
        )

    def test_change_sounds_across_sentence(self):
        changed_sounds = self.language.change_sounds(
            ["a", "gʰ", "a", "gʰ", " ", "a", "gʰ"],
            blocked_by_spacing=False
        )
        self.assertEqual(
            changed_sounds,
            ["a", "k", "a", "k", " ", "a", "g"],
            "failed to spread sound changes across an entire sentence"
        )
        

