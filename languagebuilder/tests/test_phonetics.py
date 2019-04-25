import unittest
from ..phonetics.phonetics import Phonetics

def setUpModule():
    print("Setting up the Phonetics test module")

def tearDownModule():
    print("Shutting down the Phonetics test module")

class PhoneticsFixture(unittest.TestCase):
    @classmethod
    def setUpClass(this_class):
        """Instantiate Phonetics for all tests in the class"""
        print("Setting up a Phonetics instance")
        this_class.phonetics = Phonetics()
    
    @classmethod
    def tearDownClass(this_class):
        """"Delete Phonetics instance for tests"""
        print("Tearing down a Phonetics instance")
        this_class.phonetics = None
    
class PhoneticsDefaultValues(PhoneticsFixture):
    def test_default_ipa(self):
        self.assertDictEqual(
            self.phonetics.ipa,
            {},
            "expected empty starting IPA-to-features mapping dict"
        )

    def test_default_features(self):
        self.assertDictEqual(
            self.phonetics.features,
            {},
            "expected empty starting features-to-IPA mapping dict"
        )

class PhoneticsAddUpdateDelete(PhoneticsFixture):
    @classmethod
    def setUpClass(this_class):
        super(PhoneticsAddUpdateDelete, this_class).setUpClass()
        this_class.phonetics.add("symbol_keep", ["feature", "updatable", "keepable"])
        this_class.phonetics.add("symbol_update", ["feature", "updatable"])
        this_class.phonetics.add("symbol_remove", ["feature", "updatable", "removable"])
    
    def test_add_sound(self):
        self.phonetics.add("symbol_added", ["feature", "added"])
        self.assertEqual(
            self.phonetics.get_ipa(["feature", "added"])[0],
            "symbol_added",
            "failed to add a new symbol and its associated features"
        )

    def test_update_ipa(self):
        self.phonetics.update_symbol("symbol_update", "symbol_updated")
        self.assertTrue(
            self.phonetics.has_ipa("symbol_updated") and not self.phonetics.has_ipa("symbol_update"),
            "failed to change a symbol's name"
        )

    def test_parse_features(self):
        features = self.phonetics.parse_features("updatable keepable feature")
        self.assertEqual(
            set(features),
            {'updatable', 'keepable', 'feature'},
            "failed to parse a string into a list of valid features"
        )

    def test_update_features(self):
        self.phonetics.update_feature("updatable", "updated")
        self.assertTrue(
            self.phonetics.has_feature("updated") and not self.phonetics.has_feature("updatable"),
            "failed to update a feature's name"
        )

    def test_remove_sound(self):
        self.phonetics.remove_symbol("symbol_remove")
        self.assertFalse(
            self.phonetics.has_ipa("symbol_remove"),
            "failed to delete a symbol from features"
        )
    
    def test_remove_feature(self):
        self.phonetics.remove_feature("removable")
        self.assertFalse(
            self.phonetics.has_feature("removable"),
            "failed to delete a feature from features"
        )
