import unittest
from ..phonetics.features import Features

def setUpModule():
    print("Setting up the Phonetics test module")

def tearDownModule():
    print("Shutting down the Phonetics test module")

class FeaturesFixture(unittest.TestCase):
    @classmethod
    def setUpClass(this_class):
        """Instantiate Features for all tests in the class"""
        print("Setting up a Features instance")
        this_class.features = Features()
    
    @classmethod
    def tearDownClass(this_class):
        """"Delete Features instance for tests"""
        print("Tearing down a Features instance")
        this_class.features = None
    
class FeaturesDefaultValues(FeaturesFixture):
    def test_default_ipa(self):
        self.assertDictEqual(
            self.features.ipa,
            {},
            "expected empty starting IPA-to-features mapping dict"
        )

    def test_default_features(self):
        self.assertDictEqual(
            self.features.features,
            {},
            "expected empty starting features-to-IPA mapping dict"
        )

class FeaturesAddUpdateDelete(FeaturesFixture):
    @classmethod
    def setUpClass(this_class):
        super(FeaturesAddUpdateDelete, this_class).setUpClass()
        this_class.features.add("symbol_keep", ["feature", "updatable", "keepable"])
        this_class.features.add("symbol_update", ["feature", "updatable"])
        this_class.features.add("symbol_remove", ["feature", "updatable", "removable"])
    
    def test_add_sound(self):
        self.features.add("symbol_added", ["feature", "added"])
        self.assertEqual(
            self.features.get_ipa(["feature", "added"])[0],
            "symbol_added",
            "failed to add a new symbol and its associated features"
        )

    def test_update_ipa(self):
        self.features.update_symbol("symbol_update", "symbol_updated")
        self.assertTrue(
            self.features.has_ipa("symbol_updated") and not self.features.has_ipa("symbol_update"),
            "failed to change a symbol's name"
        )

    def test_update_features(self):
        self.features.update_feature("updatable", "updated")
        self.assertTrue(
            self.features.has_feature("updated") and not self.features.has_feature("updatable"),
            "failed to update a feature's name"
        )

    def test_remove_sound(self):
        self.features.remove_symbol("symbol_remove")
        self.assertFalse(
            self.features.has_ipa("symbol_remove"),
            "failed to delete a symbol from features"
        )
    
    def test_remove_feature(self):
        self.features.remove_feature("removable")
        self.assertFalse(
            self.features.has_feature("removable"),
            "failed to delete a feature from features"
        )
