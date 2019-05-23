import unittest
from ..phonology.phonology import Phonology
from ..phonetics.phonetics import Phonetics

def setUpModule():
    print("Setting up the Phonology test module")

def tearDownModule():
    print("Shutting down the Phonology test module")

class PhonologyFixture(unittest.TestCase):
    @classmethod
    def setUpClass(this_class):
        """Instantiate Phonology for all tests in the class"""
        print("Setting up a Phonology instance")
        phonetics = Phonetics()
        phonetics.add("a", ["vowel", "front", "open", "unrounded"])
        phonetics.add("k", ["consonant", "voiceless", "velar", "stop"])
        phonetics.add("g", ["consonant", "voiced", "velar", "stop"])
        phonetics.add("x", ["consonant", "voiceless", "velar", "fricative"])
        phonetics.add("ɣ", ["consonant", "voiced", "velar", "fricative"])
        this_class.phonology = Phonology(phonetics)
    
    @classmethod
    def tearDownClass(this_class):
        """"Delete Phonology instance for tests"""
        print("Tearing down a Phonology instance")
        this_class.phonology = None

class PhonologyPhonemes(PhonologyFixture):
    @classmethod
    def setUpClass(this_class):
        super(PhonologyPhonemes, this_class).setUpClass()
        
    def test_add_sound(self):
        self.phonology.add_sound("a", ["a"])
        self.assertTrue(
            self.phonology.phonemes.has("a"),
            "failed to add a new sound to the phonology"
        )

    def test_get_sound_features(self):
        self.phonology.phonemes.add("k", ["k"])
        self.assertEqual(
            set(self.phonology.get_sound_features("k")) & {"voiceless", "velar", "stop"},
            {"voiceless", "velar", "stop"},
            "failed to add a sound and get its features"
        )

    def test_update_sound_letters(self):
        self.phonology.phonemes.add("k", ["k"])
        self.phonology.phonemes.update("k", ["k", "q"])
        self.assertIn(
            "q",
            self.phonology.get_sound_letters("k"),
            "failed to update a sound's letters"
        )

    def test_remove_sound(self):
        self.phonology.phonemes.add("k", ["k"])
        self.phonology.phonemes.remove("k")
        self.assertFalse(
            self.phonology.has_sound("k"),
            "failed to remove a sound from the inventory"
        )

class PhonologySyllables(PhonologyFixture):
    @classmethod
    def setUpClass(this_class):
        super(PhonologySyllables, this_class).setUpClass()

    def test_add_syllable(self):
        syllable_id = self.phonology.syllables.add("CVC")
        self.assertTrue(
            self.phonology.syllables.has(syllable_id),
            "failed to add a new syllable to the phonology"
        )

    def test_add_syllable_with_features(self):
        syllable_id = self.phonology.syllables.add(["velar stop", "V", "velar fricative"])
        self.assertTrue(
            self.phonology.syllables.has(syllable_id),
            "failed to add a new syllable with phonological features to the phonology"
        )
    
    def test_update_syllable(self):
        syllable_id = self.phonology.syllables.add("VVV")
        self.phonology.syllables.update(syllable_id, "CVV")
        self.assertEqual(
            self.phonology.syllables.get(syllable_id),
            self.phonology.syllables.structure("CVV"),
            "failed to update an existing syllable in the phonology"
        )

    def test_parse_syllable_characters(self):
        structure = self.phonology.syllables.structure("V_C#")
        self.assertEqual(
            structure,
            [['vowel'], ['_'], ['consonant'], ['#']],
            "failed to parse a string into a structured list of syllable characters"
        )

    def test_remove_syllable(self):
        syllable_id = self.phonology.syllables.add("CCC")
        self.phonology.syllables.remove(syllable_id)
        self.assertIsNone(
            self.phonology.syllables.get(syllable_id),
            "failed to remove an existing syllable from the phonology"
        )

# TODO: test varied built words for determining if inventory, syllables and rules work
# rather than testing substructure individually to probe how they work
class PhonologyWords(PhonologyFixture):
    @classmethod
    def setUpClass(this_class):
        super(PhonologyWords, this_class).setUpClass()
        this_class.phonology.phonemes.add("k", ["q"])
        this_class.phonology.phonemes.add("a", ["a"])
        this_class.phonology.syllables.add("CV")

    def test_build_word_sounds(self):
        entry = self.phonology.build_word(1)
        self.assertEqual(
            entry['sound'],
            "ka",
            "failed to build a one-syllable word"
        )

    def test_build_word_letters(self):
        entry = self.phonology.build_word(1)
        self.assertEqual(
            entry['spelling'],
            "qa",
            "failed to build a word with simple spelling"
        )

    def test_add_rule(self):
        rule_id = self.phonology.add_rule(['vowel'], ['vowel'], "_")
        self.assertTrue(
            self.phonology.has_rule(rule_id),
            "could not add one sound change rule to the rules"
        )
    
    def test_remove_rule(self):
        rule_id = self.phonology.add_rule(['vowel'], ['vowel'], "_")
        self.phonology.remove_rule(rule_id)
        self.assertFalse(
            self.phonology.has_rule(rule_id),
            "could not create then remove a single sound change rule"
        )

    def test_build_word_multisyllable(self):
        entry = self.phonology.build_word(3)
        self.assertEqual(
            entry['spelling'],
            "qaqaqa",
            "failed to build a simple three syllable word"
        )

    def test_build_word_fricativization(self):
        rule_id = self.phonology.add_rule(["stop"], ["fricative"], "V_V")
        entry = self.phonology.build_word(2)
        self.phonology.remove_rule(rule_id)
        self.assertEqual(
            entry['change'],
            "kaxa",
            "failed to apply a single stop-to-fricative rule correctly"
        )

    def test_build_word_voicing(self):
        rule_id = self.phonology.add_rule(["voiceless"], ["voiced"], "V_V")
        entry = self.phonology.build_word(2)
        self.phonology.remove_rule(rule_id)
        self.assertEqual(
            entry['change'],
            "kaga",
            "failed to apply a single voicing rule correctly"
        )

    def test_build_word_lenition(self):
        rule_0 = self.phonology.add_rule(["stop"], ["fricative"], "V_V")
        rule_1 = self.phonology.add_rule(["voiceless"], ["voiced"], "V_V")
        entry = self.phonology.build_word(2)
        self.phonology.remove_rule(rule_0)
        self.phonology.remove_rule(rule_1)
        self.assertEqual(
            entry['change'],
            "kaɣa",
            "failed to layer multiple leniting rules correctly"
        )
    
    def test_build_word_inapplicable_rule(self):
        rule_id = self.phonology.add_rule(["dental"], ["velar"], "_V")
        entry = self.phonology.build_word(1)
        self.phonology.remove_rule(rule_id)
        self.assertEqual(
            entry['sound'],
            "ka",
            "applied rule to inapplicable sound"
        )

    def test_build_word_applicable_rule_nonexisting_sound(self):
        rule_id = self.phonology.add_rule(["velar"], ["palatal"], "_")
        entry = self.phonology.build_word(1)
        self.phonology.remove_rule(rule_id)
        self.assertEqual(
            entry['sound'],
            "ka",
            "failed to handle sound change where changed feature combination does not exist in the phonetics"
        )
    
    def test_build_word_nochange_rule(self):
        rule_id = self.phonology.add_rule(["velar"], ["velar"], "_V")
        entry = self.phonology.build_word(1)
        self.phonology.remove_rule(rule_id)
        self.assertEqual(
            entry['sound'],
            "ka",
            "applied rule to inapplicable sound"
        )    

class PhonologySpelling(PhonologyFixture):
    @classmethod
    def setUpClass(this_class):
        super(PhonologySpelling, this_class).setUpClass()
        this_class.phonology.phonemes.add("c", ["ts"])
        this_class.phonology.phonemes.add("z", ["dz"])
        this_class.phonology.phonemes.add("o", ["o"])
        this_class.phonology.syllables.add("CV")

    def test_spell_word(self):
        # spell the word as given in letters
        phonemes = ['ts', 'o', 'ts', 'o']
        spelling = self.phonology.spell(phonemes)
        self.assertEqual(
            spelling,
            "coco",
            "failed to spell a simple word with known letters"
        )

    def test_spell_word_fallback_phonemes(self):
        # fall back on one consonant but not the other
        phonemes = ['g', 'o', 'dz', 'o']
        fallback_phonemes = ['ts', 'o', 'ts', 'o']
        spelling = self.phonology.spell(phonemes, fallback_phonemes)
        self.assertEqual(
            spelling,
            "cozo",
            "failed to use fallback phonemes correctly when spelling a word"
        )

    def test_build_spell_word(self):
        # generate a word
        word = self.phonology.build_word(
            length=4,
            apply_rules=True,
            spell_after_change=True
        )
        self.assertTrue(
            word['spelling'] and word['spelling'] == self.phonology.spell(word['sound'], word['change']),
            "failed to spell  word with known letters"
        )