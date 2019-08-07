import unittest
from ..phonology.phonology import Phonology
from ..phonetics.phonetics import Phonetics
from ..tools.flat_list import flatten

def setUpModule():
    print("Setting up the Phonology test module")

def tearDownModule():
    print("Shutting down the Phonology test module")

class PhonologyFixture(unittest.TestCase):
    @classmethod
    def setUpClass(this_class):
        """Instantiate Phonology for all tests in the class"""
        print("Setting up a Phonology instance")
        this_class.phonetics = Phonetics()
        this_class.phonetics.add("a", ["vowel", "front", "open", "unrounded"])
        this_class.phonetics.add("k", ["consonant", "voiceless", "velar", "stop"])
        this_class.phonetics.add("g", ["consonant", "voiced", "velar", "stop"])
        this_class.phonetics.add("kʰ", ["consonant", "voiceless", "aspirated", "velar", "stop"])
        this_class.phonetics.add("gʰ", ["consonant", "voiced", "aspirated", "velar", "stop"])
        this_class.phonetics.add("x", ["consonant", "voiceless", "velar", "fricative"])
        this_class.phonetics.add("ɣ", ["consonant", "voiced", "velar", "fricative"])
        this_class.phonology = Phonology(this_class.phonetics)
    
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
        self.phonology.phonemes.add("x", ["h"])
        self.assertEqual(
            set(self.phonology.get_sound_features("x")),
            {"consonant", "voiceless", "velar", "fricative"},
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
        self.phonology.phonemes.add("g", ["g"])
        self.phonology.phonemes.remove("g")
        self.assertFalse(
            self.phonology.has_sound("g"),
            "failed to remove a sound from the inventory"
        )

    def test_change_sound(self):
        symbol = self.phonology.change_symbol(["voiceless"], ["voiced"], "k")
        self.assertEqual(
            symbol,
            "g",
            "failed to change a sound from voiceless to voiced"
        )
    
    def test_change_sound_extra_feature(self):
        self.phonology.phonemes.add("kʰ", ["kh"])
        symbol = self.phonology.change_symbol(["voiceless"], ["voiced"], "kʰ")
        self.assertEqual(
            symbol,
            "gʰ",
            "failed to change a consonant with an extra feature (aspiration) compared to other consonants"
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
        entry = self.phonology.build_word(1, as_string=True)
        self.assertEqual(
            entry['sound'],
            "ka",
            "failed to build a one-syllable word"
        )

    def test_build_word_letters(self):
        entry = self.phonology.build_word(1, as_string=True)
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
        entry = self.phonology.build_word(3, as_string=True)
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
            list("kaxa"),
            "failed to apply a single stop-to-fricative rule correctly"
        )

    def test_build_word_voicing(self):
        rule_id = self.phonology.add_rule(["voiceless"], ["voiced"], "V_V")
        entry = self.phonology.build_word(2, as_string=True)
        self.phonology.remove_rule(rule_id)
        self.assertEqual(
            entry['change'],
            "kaga",
            "failed to apply a single voicing rule correctly"
        )

    def test_build_word_lenition(self):
        rule_0 = self.phonology.add_rule(["stop"], ["fricative"], "V_V")
        rule_1 = self.phonology.add_rule(["voiceless"], ["voiced"], "V_V")
        entry = self.phonology.build_word(2, as_string=True)
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
            list("ka"),
            "applied rule to inapplicable sound"
        )

    def test_build_word_applicable_rule_nonexisting_sound(self):
        rule_id = self.phonology.add_rule(["velar"], ["palatal"], "_")
        entry = self.phonology.build_word(1, as_string=True)
        self.phonology.remove_rule(rule_id)
        self.assertEqual(
            entry['sound'],
            "ka",
            "failed to handle sound change where changed feature combination does not exist in the phonetics"
        )
    
    def test_build_word_nochange_rule(self):
        rule_id = self.phonology.add_rule(["velar"], ["velar"], "_V")
        entry = self.phonology.build_word(1, as_string=True)
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
        this_class.phonetics.add("ts", ["consonant", "voiceless", "alveolar", "affricate"])
        this_class.phonetics.add("dz", ["consonant", "voiced", "alveolar", "affricate"])
        this_class.phonetics.add("o", ["vowel", "back", "mid", "rounded"])
        this_class.phonology.phonemes.add("ts", ["c"])
        this_class.phonology.phonemes.add("dz", ["z"])
        this_class.phonology.phonemes.add("o", ["o"])
        this_class.phonology.syllables.add("CV")
        
    def test_spell_word(self):
        # spell the word as given in letters
        phonemes = ['ts', 'o', 'ts', 'o']
        # use class phonology to spell word
        spelling = self.phonology.spell(phonemes)
        self.assertEqual(
            "".join(spelling),
            "coco",
            "failed to spell a simple word with known letters"
        )

    def test_spell_word_fallback_phonemes(self):
        # fall back on one consonant but not the other
        phonemes = ['g', 'o', 'dz', 'o']
        fallback_phonemes = ['ts', 'o', 'ts', 'o']
        # use class phonology to spell
        spelling = self.phonology.spell(phonemes, fallback_phonemes)
        self.assertEqual(
            "".join(spelling),
            "cozo",
            "failed to use fallback phonemes correctly when spelling a word"
        )

    def test_spell_word_sound_change(self):
        self.phonology.add_rule("voiceless", "voiced", "V_")
        # spell changed sounds but fall back on pre-change sounds
        phonemes = ['ts', 'o', 'ts', 'o']
        changed_phonemes = self.phonology.apply_rules(phonemes)
        # use class phonology to spell
        spelling = self.phonology.spell(changed_phonemes, phonemes)
        self.assertEqual(
            "".join(spelling) if spelling else "",
            "cozo",
            f"failed to spell a word after a sound change was applied"
        )

    def test_build_spell_word(self):
        """Test building and spelling a word after sound changes based on class phonology"""

        # TODO: repair rule with environment _V not applying!
        # TODO: extract rule from difference (like dz > ts picking up on voicing)

        # add sound change and build word 
        self.phonology.add_rule("voiceless", "voiced", "V_")
        word = self.phonology.build_word(
            length=4,
            apply_rules=True,
            spell_after_change=True,
            as_string=True
        )
        # expect word
        self.assertIn(
            (None, word['spelling'])[not not word['spelling']],
            ["cozozozo", "zozozozo"],  # changes result in ts,dz > dz | V_(V)
            "failed to generate a word with valid spelling"
        )

class PhonologySuprasegmentals(PhonologyFixture):
    @classmethod
    def setUpClass(this_class):
        super(PhonologySuprasegmentals, this_class).setUpClass()
        this_class.phonetics.add("ts", ["consonant", "voiceless", "alveolar", "affricate"])
        this_class.phonetics.add("o", ["vowel", "back", "mid", "rounded"])
        this_class.phonology.phonemes.add("ts", ["c"])
        this_class.phonology.phonemes.add("o", ["o"])
        this_class.phonology.syllables.add("CV")
        #this_class.phonology.suprasegmentals.add("`", stress="primary", pitch=None)

    def test_add_remove_default_contour(self):
        contour_name = self.phonology.suprasegmentals.add_default_contour(
            "primary",
            mark="`",
            conditioning_mark=None,
            offset=1,
            chain=None
        )
        contour = self.phonology.suprasegmentals.get_default_contour(contour_name)
        self.phonology.suprasegmentals.remove_default_contour(contour_name)
        self.assertEqual(
            contour.get('offset'),
            1,
            f"failed to create, store and remove a suprasegmentals default contour"
        )

    def test_apply_default_contour(self):
        self.phonology.suprasegmentals.add_default_contour("default_accent", "acute", offset=-1)
        accented_word = self.phonology.suprasegmentals.apply_default_contour([["r", "p", "a"], ["b", "a"], ["p", "a", "p"]], "default_accent")
        # TODO: add mark -> letter mapping
        self.assertEqual(
            "".join(flatten(accented_word)),
            "rpabapáp",
            f"failed to apply a suprasegmentals default contour"
        )

    # # TODO: rewrite suprasegmentals tests below considering:
    # #   - custom contours
    # #   - default contours
    # #   - ability to mark both sound and spelling
    # #   - ability to mark any letters of interest (not only V)
    # #   - /!\ syllable shape checks
    # #       - accent last if long [C,V,C,(C)] otherwise penult
    # #       - high tone on second mora no matter which syllable

    # def test_mark_accent(self):
    #     word = self.phonology.build_word(
    #         length=3,
    #         apply_rules=True,
    #         spell_after_change=False
    #     )
    #     # NOTE: or store marking info in built word?
    #     word = self.phonology.suprasegmentals.mark(word['sound'], 2, stress="primary")
    #     self.assertEqual(
    #         word,
    #         "tsotsòtso",
    #         "failed to mark a generated word with an accent"
    #     )

    # def test_move_accent(self):
    #     word = self.phonology.build_word(length=4, apply_rules=True)
    #     # NOTE: mark name still needed to retrieve which mark to adjust
    #     # TODO: how to represent word-wide pitch contours
    #     self.phonology.suprasegmentals.mark(word['sound'], 3, stress="primary")
    #     word = self.phonology.suprasegmentals.move(word['sound'], 4, stress="primary")
    #     self.assertEqual(
    #         word,
    #         "tsotsotsòtso",
    #         "failed to move a generated word's accent to a new syllable"
    #     )

    # # TODO: attach marks to syllable, persist marks through sound changes,
    # # update marks with mark changes, have marks associated with spelling
    # # Sound changes:
    # #   - what if a marked sound is deleted in a change?
    # #   - what if a marked sound falls after a deleted sound?
    # #   - what if a sound change depends on e.g. a previous accent shift?
    # #   - what if a change impacts both underlying sound and added mark?
    # # Spelling:
    # #   - how to spell vs ignore marked sounds?
    # #   - when does spelling take place?
    # #   - how are spelled letters marked? independently of marked sounds?

    # def test_accent_sound_and_spelling(self):
        
    #     # word = self.phonology.build_word(length=4, apply_rules=True)
    #     # imagine a fixed word
    #     word_sounds = "bopo'bipo"   # expected segs output
        
    #     # accomodate two changes: oxytonic stress, high V syncope C_C
    #     word_change = self.phonology.apply_rules(word_sounds)  # expect "bopop'po"
        
    #     # ensure markings are stored for seg accentuation
    #     # phon_char = "'"
    #     # spelled_char = "´" # also map to specific letters: á, ŕ, ...

    #     # now based on those changes the following words should be renderable
    #     # in post-change sounds and spelling form
    #     spelled_sounds = self.phonology.suprasegmentals.sound_out(word_change)
    #     spelled_change = self.phonology.suprasegmentals.spell_out(word_change)
    #     self.assertEqual(
    #         [spelled_sounds, spelled_change],
    #         ["bopobípo", "bopopó"],
    #         "failed to change accented phonological segments and spell the changed sounds"
    #     )

    # def test_accent_default(self):
    #     self.phonology.suprasegmentals.default(
    #         stress="primary",
    #         syllable=-2
    #     )
    #     word = [["t", "o"], ["t", "a"], ["t", "o"]]
    #     spelling = self.phonology.suprasegmentals.spell_out(word)
    #     self.assertEqual(
    #         spelling,
    #         "totáto",
    #         "failed to apply default accentuation to segments and spell the accented word"
    #     )

    # def test_accent_exception(self):
    #     self.phonology.suprasegmentals.default(
    #         stress="primary",
    #         syllable=-2,
    #         mark_exception=True
    #     )
    #     word = [["t", "o"], ["t", "a"], ["t", "o"]]
    #     marked_word = self.phonology.suprasegmentals.mark((word, 0), 3, stress="primary")
    #     unmarked_word = self.phonology.suprasegmentals.mark((word, 1), 2, stress="primary")
    #     marked_spelling = self.phonology.suprasegmentals.spell_out((word, 0))
    #     unmarked_spelling = self.phonology.suprasegmentals.spell_out((word, 1))
    #     self.assertEqual(
    #         [marked_spelling, unmarked_spelling],
    #         ["totató", "totato"],
    #         "failed to mark exception to default accentuation while leaving nonexception unmarked"
    #     )

class PhonologyMorae(PhonologyFixture):
    @classmethod
    def setUpClass(this_class):
        super(PhonologyMorae, this_class).setUpClass()
        this_class.phonetics.add("k", ["consonant", "voiceless", "velar", "stop"])
        this_class.phonetics.add("o", ["vowel", "back", "mid", "rounded"])
        this_class.phonology.phonemes.add("k", ["c"])
        this_class.phonology.phonemes.add("o", ["o"])
        this_class.phonology.syllables.add("VC")
        this_class.phonology.syllables.add("VVC")
        #this_class.phonology.morae.set_mora([])

    def test_set_basic_mora(self):
        beats = 1
        self.phonology.morae.set_mora([["vowel"], ["consonant"]], beats=beats)
        self.assertIn(
            ["consonant", "vowel"],
            self.phonology.morae.morae.get(beats, []),
            "failed to set a new simple mora"
        )

    def test_interpret_mora(self):
        mora = self.phonology.morae.set_mora(["V", "C"])
        self.assertEqual(
            mora,
            [["vowel"], ["consonant"]],
            "failed to set mora using consonant and vowel abbreviations"
        )

    def test_check_mora(self):
        mora = self.phonology.morae.set_mora(["V", "V", "C"], beats=2)
        self.assertTrue(
            self.phonology.morae.is_mora(mora),
            "failed to find mora in stored morae"
        )

    # TODO: handle mora already added but with different counts
    #   - map of beats -> morae vs mora -> beats?
    def test_count_beats(self):
        mora = self.phonology.morae.set_mora(["V", "V", "C"], beats=2)
        self.assertEqual(
            self.phonology.morae.get_beats(mora),
            2,
            "failed to count beats in existing mora"
        )
