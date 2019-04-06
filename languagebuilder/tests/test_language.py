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

    def test_remove_sound(self):
        self.language.phonetics.add("k", ["voiceless", "velar", "stop", "consonant"])
        self.language.phonology.add_sound("k", letters=["q"])
        self.language.phonology.remove_sound("k")
        self.assertTrue(
            self.language.phonetics.has_ipa("k") and not self.language.phonology.has_sound("k"),
            "failed to remove added ipa from phonology while keeping it in the phonetics"
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

    def test_add_syllable(self):
        return

    def test_update_syllable(self):
        return

    def test_remove_syllable(self):
        return

    def test_add_rule(self):
        return

    def test_add_rules(self):
        return

    #def test_build_word(self):
    #    return

class LanguageGrammar(LanguageFixture):
    @classmethod
    def setUpClass(this_class):
        super(LanguageGrammar, this_class).setUpClass()

    def test_add_property(self):
        return

    def test_add_word_class(self):
        return

    def test_add_exponent(self):
        return

    #def test_build_unit(self):
    #    return

class LanguageWords(LanguageFixture):
    @classmethod
    def setUpClass(this_class):
        super(LanguageWords, this_class).setUpClass()
        # TODO: sounds and grammar
        #   - phonetics, inventory, syllables
        #   - word classes, properties, exponents (including ordering)

    def test_build_root(self):
        return

    def test_build_unit(self):
        return

    def test_apply_grammar(self):
        return

    def test_apply_sound_changes(self):
        # to root, to unit
        return

    def test_spell_word(self):
        # stored? or from sound change?
        return

    def test_store_word(self):
        return
    
    def test_lookup_word(self):
        return
    
    def test_define_word(self):
        return
    
    def test_search_word(self):
        return

    def test_print_dictionary(self):
        return
    

    