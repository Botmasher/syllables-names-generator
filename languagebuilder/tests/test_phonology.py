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
        this_class.phonology = Phonology(phonetics)
    
    @classmethod
    def tearDownClass(this_class):
        """"Delete Phonology instance for tests"""
        print("Tearing down a Phonology instance")
        this_class.phonology = None

# TODO: test with varied inputs instead of expecting explicit infrastructure
#
# class PhonologyDefaultValues(PhonologyFixture):
#     def test_default_ipa(self):
#         self.assertDictEqual(
#             self.phonology.rules
#             {},
#             "expected empty starting IPA-to-features mapping dict"
#         )

class PhonologyAddUpdateDelete(PhonologyFixture):
    @classmethod
    def setUpClass(this_class):
        super(PhonologyAddUpdateDelete, this_class).setUpClass()
        
    def test_add_sound(self):
        self.phonology.add_sound("a", ["a"])
        self.assertEqual(
            self.phonology.has_sound("a"),
            "failed to add a new sound to the phonology"
        )

    def test_get_sound_features(self):
        self.phonology.add_sound("t", ["t", "td"])
        self.assertEqual(
            self.phonology.get_sound_features("t") & {"voiceless", "alveolar", "stop"},
            {"voiceless", "dental", "stop"},
            "failed to add a sound and get its features"
        )
