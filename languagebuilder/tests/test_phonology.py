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

class PhonologyAddUpdateDelete(PhonologyFixture):
    @classmethod
    def setUpClass(this_class):
        super(PhonologyAddUpdateDelete, this_class).setUpClass()
        
    def test_add_sound(self):
        self.phonology.add_sound("a", ["a"])
        self.assertTrue(
            self.phonology.has_sound("a"),
            "failed to add a new sound to the phonology"
        )

    def test_get_sound_features(self):
        self.phonology.add_sound("k", ["k"])
        self.assertEqual(
            self.phonology.get_sound_features("k") & {"voiceless", "velar", "stop"},
            {"voiceless", "velar", "stop"},
            "failed to add a sound and get its features"
        )

    def test_update_sound_letters(self):
        self.phonology.add_sound("k", ["k"])
        self.phonology.update_sound("k", ["k", "q"])
        self.assertIn(
            "q",
            self.phonology.get_sound_letters("k"),
            "failed to update a sound's letters"
        )

    def test_remove_sound(self):
        self.phonology.add_sound("k", ["k"])
        self.phonology.remove_sound("k")
        self.assertFalse(
            self.phonology.has_sound("k"),
            "failed to remove a sound from the inventory"
        )

class PhonologySyllables(PhonologyFixture):
    @classmethod
    def setUpClass(this_class):
        super(PhonologySyllables, this_class).setUpClass()
        this_class.phonology.add_syllable("CV")
        this_class.phonology.add_syllable("V")

    def test_add_syllable(self):
        self.phonology.add_syllable("CVC")
        self.assertNotIn(
            self.phonology.find_syllables(["C", "V", "C"]),
            "failed to add a new syllable to the phonology"
        )

    def test_add_syllable_with_features(self):
        self.phonology.add_syllable(["velar stop", "V", "velar fricative"])
        self.assertNotIn(
            find
            self.phonology.find_syllables(["V"]),
            "failed to add a new syllable with phonological features to the phonology"
        )
    
    def test_update_syllable(self):
        self.phonology.update_syllable("CV", "CVV")
        self.assertNotIn(
            self.phonology.find_syllables(['C', 'V', 'V']),
            [None, []],
            "failed to update an existing syllable in the phonology"
        )

    def test_remove_syllable(self):
        confirmations = self.phonology.remove_syllable("V")
        self.assertNotIn(
            confirmations,
            [None, []],
            "failed to remove an existing syllable from the phonology"
        )

# TODO: test varied built words for determining if inventory, syllables and rules work
# rather than testing substructure individually to probe how they work
class PhonologyBuildWord(PhonologyFixture):
    @classmethod
    def setUpClass(this_class):
        super(PhonologyBuildWord, this_class).setUpClass()
        this_class.phonology.add_sound("k", ["q"])
        this_class.phonology.add_sound("a", ["a"])
        this_class.phonology.add_syllable("CV")

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
        rule_id = self.phonology.add_rule(['vowel'], ['vowel'], "V")
        self.assertTrue(
            self.phonology.has_rule(rule_id),
            "could not add one sound change rule to the rules"
        )
    
    def test_remove_rule(self):
        rule_id = self.phonology.add_rule(['vowel'], ['vowel'], "V")
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
        self.phonology.add_rule(["voiceless"], ["voiced"], "V_V")
        entry = self.phonology.build_word(2)
        self.assertEqual(
            entry['change'],
            "kaga",
            "failed to apply a single voicing rule correctly"
        )

    def test_build_word_lenition(self):
        self.phonology.add_rule(["stop"], ["fricative"], "V_V")
        self.phonology.add_rule(["voiceless"], ["voiced"], "V_V")
        entry = self.phonology.build_word(2)
        self.assertEqual(
            entry['change'],
            "kaɣa",
            "failed to layer multiple leniting rules correctly"
        )
