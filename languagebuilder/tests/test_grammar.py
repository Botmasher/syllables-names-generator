import unittest

from ..grammar import grammar

# compare classes to instances in tests
from ..grammar.word_classes import WordClasses
from ..grammar.exponents import Exponents
from ..grammar.properties import Properties

def setUpModule():
    print("Setting up the Grammar test module")

def tearDownModule():
    print("Shutting down the Grammar test module")

class GrammarFixture(unittest.TestCase):
    @classmethod
    def setUpClass(this_class):
        """Instantiate grammar for all tests in the class"""
        print("Setting up a Grammar instance")
        this_class.grammar = grammar.Grammar()
    
    @classmethod
    def tearDownClass(this_class):
        """"Delete grammar instance for tests"""
        # TODO: destroy or dispose method on Grammar
        print("Tearing down a Grammar instance")
        this_class.grammar = None
    
class GrammarDefaultValues(GrammarFixture):
    def test_default_word_classes(self):
        self.assertIsInstance(self.grammar.word_classes, WordClasses, "incorrect starting word_classes map")

    def test_default_exponents(self):
        self.assertIsInstance(self.grammar.exponents, Exponents, "incorrect starting exponents map")

    def test_default_properties(self):
        self.assertIsInstance(self.grammar.properties, Properties, "incorrect starting properties map")

class GrammarProperties(GrammarFixture):
    def test_add_property(self):
        self.assertIsNotNone(
            self.grammar.properties.add(category="added_category", grammeme="added_grammeme"),
            "failed to add property category-grammeme pair"
        )
    
    # TODO: add property various ways (dict, defaultdict, list)
    def test_add_property_none(self):
        self.assertIsNone(
            self.grammar.properties.add(category="added_category", grammeme=None),
            "incorrect handling of adding new property with missing grammeme"
        )

    def test_add_properties(self):
        added_properties = self.grammar.properties.add_many({
            'added_categories_1': ('added_grammemes_1', 'added_grammemes_2'),
            'added_categories_2': ('added_grammemes_3', 'added_grammemes_4')
        })
        added_properties = [
            grammeme
            for grammemes in added_properties.values()
            for grammeme in grammemes
        ]
        self.assertEqual(
            len(added_properties),
            4,
            f"could not add multiple properties {added_properties}"
        )
    
    def test_add_properties_same_grammeme_name(self):
        properties = self.grammar.properties.add_many({
            'same_grammeme_category_1': ('same_grammeme_1', 'same_grammeme_2'),
            'same_grammeme_category_2': ('same_grammeme_1', 'same_grammeme_2')
        })
        added_properties = [
            grammeme
            for grammemes in properties.values()
            for grammeme in grammemes
        ]
        self.assertEqual(
            len(added_properties),
            4,
            f"could not add multiple properties with the same grammeme name but under different categories"
        )
    
    def test_add_remove_property(self):
        self.grammar.properties.add("removed_category", "removed_grammeme")
        self.grammar.properties.remove("removed_category", "removed_grammeme")
        self.assertIsNone(
            self.grammar.properties.get('removed_category', 'removed_grammeme'),
            "failed to add then remove a property"
        )

    # NOTE: properties no longer contain description, only category:{grammeme,...}
    # def test_update_property_description(self):
    #     test_description = "test description"
    #     self.grammar.properties.add("updated_category", "updated_grammeme")
    #     self.grammar.properties.update("updated_category", "updated_grammeme", description=test_description)
    #     self.assertEqual(
    #         self.grammar.properties.get("updated_category", "updated_grammeme").get("description"),
    #         test_description,
    #         "failed to add then update a property's description attribute"
    #     )

    def test_get_property_existing(self):
        self.grammar.properties.add("get_category", "get_grammeme")
        self.assertIsNotNone(
            self.grammar.properties.get("get_category", "get_grammeme"),
            "failed to get a property that was added to the grammar"
        )

    def test_get_property_nonexisting(self):
        self.assertIsNone(
            self.grammar.properties.get("noncategory", "nongrammeme"),
            "failed to handle getting property that was not added to the grammar"
        )

    def test_find_property_existing(self):
        self.grammar.properties.add(category="find_category", grammeme="find_grammeme")
        self.assertEqual(
            self.grammar.properties.find(category="find_category")[0],
            ("find_category", "find_grammeme"),
            "did not find added category and grammeme using grammar find_properties"
        )
    
    # TODO: create uuids to test created and updated names
    #   - avoid potential conflicts from using such similar manual names across properties tests
    def test_rename_property_category(self):
        self.grammar.properties.add("rename_category_category", "rename_category_grammeme")
        self.grammar.properties.rename_category("rename_category_category", "renamed_category")
        self.assertIn(
            "rename_category_grammeme",
            self.grammar.properties.get("renamed_category"),
            "failed to change the name of a category"
        )
    
    def test_rename_property_grammeme(self):
        self.grammar.properties.add("rename_grammeme_category", "rename_grammeme_grammeme")
        self.grammar.properties.rename_grammeme("rename_grammeme_category", "rename_grammeme_grammeme", "renamed_grammeme")
        self.assertIsNotNone(
            self.grammar.properties.get("rename_grammeme_category", "renamed_grammeme"),
            "failed to change the property grammeme name"
        )
    
    def test_recategorize_property_grammeme(self):
        self.grammar.properties.add("categorize_category", "categorize_grammeme")
        self.grammar.properties.recategorize("categorize_category", "categorize_grammeme", "recategorize_category")
        self.assertIsNotNone(
            self.grammar.properties.get("recategorize_category", "categorize_grammeme"),
            "failed to change the property grammeme's parent category"
        )

class GrammarExponents(GrammarFixture):
    @classmethod
    def setUpClass(this_class):
        super(GrammarExponents, this_class).setUpClass()
        this_class.grammar.properties.add("exponent_category", "exponent_grammeme")
    
    def test_add_exponent(self):
        exponent_id = self.grammar.exponents.add(pre="test_pre", post="test_post", bound=True, properties={
            'exponent_category': 'exponent_grammeme'
        })
        self.assertIsNotNone(
            self.grammar.exponents.get(exponent_id),
            "could not add one new exponent"
        )
    
    def test_add_exponent_empty(self):
        self.assertIsNone(
            self.grammar.exponents.add(),
            "failed to handle adding defaults-only new exponents with no details"
        )

    def test_add_exponents(self):
        added_exponent_ids = self.grammar.exponents.add_many([
            {
                'pre': "multiple_pre",
                'post': "",
                'bound': False,
                'properties': {'exponent_category': 'exponent_grammeme'}
            },
            {
                'pre': "",
                'post': "multiple_post",
                'bound': True,
                'properties': {'exponent_category': 'exponent_grammeme'}
            }
        ])
        self.assertEqual(
            len(added_exponent_ids),
            2,
            "failed to add multiple new exponents"
        )

    def test_add_exponent_with_grammeme_string(self):
        exponent_id = self.grammar.exponents.add(pre="added_pre", properties={'exponent_category': 'exponent_grammeme'})
        self.assertIsNotNone(
            self.grammar.exponents.get(exponent_id),
            "could not add a new exponent passing a properties map with a grammeme in a string"
        )

    def test_add_exponent_with_grammeme_collection(self):
        exponent_id = self.grammar.exponents.add(pre="added_pre", properties={'exponent_category': ['exponent_grammeme']})
        self.assertIsNotNone(
            self.grammar.exponents.get(exponent_id),
            "could not add a new exponent passing a properties map with a grammeme collection"
        )       

    def test_update_exponent(self):
        test_pre = "test_pre"
        exponent_id = self.grammar.exponents.add(
            pre="updated_pre",
            post="updated_post",
            properties={'exponent_category': 'exponent_grammeme'}
        )
        self.grammar.exponents.update(exponent_id, pre=test_pre)
        self.assertEqual(
            self.grammar.exponents.get(exponent_id).get('pre'),
            test_pre,
            "failed to add then update an exponent's attributes"
        )
    
    def test_add_remove_exponent(self):
        exponent_id = self.grammar.exponents.add(pre="added_pre", post="added_post", properties={
            'exponent_category': 'exponent_grammeme'
        })
        self.grammar.exponents.remove(exponent_id)
        self.assertIsNone(
            self.grammar.exponents.get(exponent_id),
            "failed to add then remove an exponent"
        )
    
    def test_get_exponent(self):
        exponent_id = self.grammar.exponents.add(pre="get_pre", properties={'exponent_category': 'exponent_grammeme'})
        self.assertIsNotNone(
            self.grammar.exponents.get(exponent_id),
            "failed to add then check if exponent exists"
        )

    def test_find_exponents(self):
        exponent_id = self.grammar.exponents.add(pre="existing_exponent", properties={'exponent_category': 'exponent_grammeme'})
        self.assertIn(
            exponent_id,
            self.grammar.exponents.find(pre="existing_exponent"),
            "failed to add then find existing exponent"
        )

    def test_find_exponent_nonexisting(self):
        self.assertEqual(
            list(self.grammar.exponents.find(pre="nonexisting_pre")),
            [],
            "failed to return empty list after searching for nonexistent exponent"
        )
    
    def test_change_exponent_property_category(self):
        self.grammar.properties.add("categorized_category", "categorized_grammeme")
        exponent_id = self.grammar.exponents.add(post="test_post", properties={'categorized_category': 'categorized_grammeme'})
        self.grammar.properties.recategorize("categorized_category", "categorized_grammeme", "recategorized_category")
        self.assertIn(
            "recategorized_category",
            self.grammar.exponents.get(exponent_id).get("properties", {}),
            "failed to update changed property category name within exponent details"
        )

    def test_change_exponent_property_grammeme(self):
        self.grammar.properties.add("named_category", "named_grammeme")
        exponent_id = self.grammar.exponents.add(post="test_post", properties={'named_category': 'named_grammeme'})
        self.grammar.properties.rename_grammeme("named_category", "named_grammeme", "renamed_grammeme")
        self.assertIn(
            "renamed_grammeme",
            self.grammar.exponents.get(exponent_id).get("properties", {}).get("named_category", []),
            "failed to update changed property grammeme name within exponent details"
        )

class GrammarWordClasses(GrammarFixture):
    @classmethod
    def setUpClass(this_class):
        super(GrammarWordClasses, this_class).setUpClass()
        this_class.grammar.properties.add("exponent_category", "exponent_grammeme")

    def test_add_word_class(self):
        self.grammar.word_classes.add("added_word_class")
        self.assertIn(
            "added_word_class",
            self.grammar.word_classes.get(),
            "failed to add one new word class"
        )
    
    def test_update_word_class(self):
        self.grammar.word_classes.add("updated_word_class")
        self.grammar.word_classes.rename("updated_word_class", "renamed_word_class")
        self.assertIn(
            "renamed_word_class",
            self.grammar.word_classes.get(),
            "failed to update the name of an added word class"
        )

    def test_remove_word_class(self):
        self.grammar.word_classes.add("removed_word_class")
        self.assertIsNotNone(
            self.grammar.word_classes.remove("removed_word_class"),
            "failed to remove added word class"
        )



    def test_add_word_class_to_exponent_pos(self):
        self.grammar.word_classes.add("added_exponent_pos")
        exponent_id = self.grammar.exponents.add(pre="pre", properties={'exponent_category': 'exponent_grammeme'})
        self.grammar.exponents.add_pos(exponent_id, "added_exponent_pos")
        self.assertIn(
            "added_exponent_pos",
            self.grammar.exponents.get(exponent_id)['pos'],
            "failed to add word class to an exponent's pos collection"
        )

    def test_remove_word_class_from_exponent_pos(self):
        self.grammar.word_classes.add("excluded_exponent_pos")
        exponent_id = self.grammar.exponents.add(post="-post", properties={'exponent_category': 'exponent_grammeme'})
        self.grammar.exponents.remove_pos(exponent_id, "excluded_exponent_pos")
        self.assertNotIn(
            "excluded_exponent_pos",
            self.grammar.exponents.exponents[exponent_id]['pos'],
            "failed to remove word class directly from an exponent's pos collection"
        )
    
    def test_remove_word_class_then_check_exponent_pos(self):
        self.grammar.word_classes.add("removed_exponent_pos")
        exponent_id = self.grammar.exponents.add(pre="pre", properties={'exponent_category': 'exponent_grammeme'})
        self.grammar.exponents.add_pos(exponent_id, "removed_exponent_pos")
        self.grammar.word_classes.remove("removed_exponent_pos")
        self.assertNotIn(
            "removed_word_class",
            self.grammar.exponents.get(exponent_id)['pos'],
            "failed to delete a removed word class from an exponent's pos collection"
        )

class GrammarBuildWords(GrammarFixture):
    @classmethod
    def setUpClass(this_class):
        super(GrammarBuildWords, this_class).setUpClass()
        # add a word class
        this_class.grammar.word_classes.add("noun")
        # add basic properties
        this_class.grammar.properties.add("category", "grammeme")
        this_class.grammar.properties.add("category", "grammeme_noun")
        this_class.grammar.properties.add("category", "grammeme_verb")
        this_class.grammar.properties.add("category", "nonexponented_grammeme")
        # add basic exponents
        this_class.grammar.exponents.add(post="-verb", properties={'category': 'grammeme_verb'}, bound=True)
        this_class.grammar.exponents.add(pre="noun-", properties={'category': 'grammeme_noun'}, pos="noun", bound=True)
        this_class.grammar.exponents.add(pre="nounish", properties={'category': ['grammeme', 'grammeme_noun']}, pos="noun", bound=False)
        this_class.grammar.exponents.add(pre="circum-", post="-fix", properties={'category': 'grammeme'}, bound=True)

    def test_build_unit(self):
        unit = self.grammar.build_unit("baseword", properties={'category': 'grammeme_verb'})
        self.assertEqual(
            unit,
            "baseword-verb",
            "failed to build grammatical unit using a simple exponent providing one property"
        )

    def test_build_unit_parsed(self):
        unit = self.grammar.build_unit("baseword", properties='category grammeme_verb')
        self.assertEqual(
            unit,
            "baseword-verb",
            "failed to build grammatical unit using a simple parsed properties string"
        )
    
    def test_build_unit_parsed_uncategorized(self):
        unit = self.grammar.build_unit("baseword", properties="grammeme grammeme_noun", word_classes="noun")
        self.assertEqual(
            unit,
            "nounish baseword",
            "failed to build grammatical unit using a parsed properties string with missing category but valid grammemes"
        )
    
    def test_build_unit_parsed_postcategorized(self):
        unit = self.grammar.build_unit("baseword", properties='grammeme_noun category grammeme category', word_classes="noun")
        self.assertEqual(
            unit,
            "nounish baseword",
            "failed to build grammatical unit using a parsed properties string where the category follows the grammeme"
        )

    def test_build_unit_parsed_messy(self):
        unit = self.grammar.build_unit("baseword", properties='   ἄβγδ  grammeme :  grammeme_noun , category   , something  else too     ', word_classes="noun")
        self.assertEqual(
            unit,
            "nounish baseword",
            "failed to build grammatical unit using a messy parsed properties string with extra content, whitespace and special characters"
        )

    def test_build_unit_excluded_word_class(self):
        unit = self.grammar.build_unit("baseword", properties={'category': 'grammeme_verb'}, word_classes="noun", exact_pos=True)
        self.assertEqual(
            unit,
            "baseword",
            "failed to handle building a grammatical unit requesting a property and a word class excluded by the provided property"
        )

    def test_build_unit_multiproperty_exponent(self):
        unit = self.grammar.build_unit("baseword", properties={'category': ['grammeme', 'grammeme_noun']}, word_classes="noun")
        self.assertEqual(
            unit,
            "nounish baseword",
            "failed to build grammatical unit using a single exponent providing multiple properties"
        )

    def test_build_unit_circumfix(self):
        unit = self.grammar.build_unit("baseword", properties={'category': 'grammeme'})
        self.assertEqual(
            unit,
            "circum-baseword-fix",
            "could not build grammatical unit with material both before and after the base"
        )

    def test_build_unit_existing_property_nonexisting_exponent(self):
        unit = self.grammar.build_unit("baseword", properties={'category': 'nonexponented_grammeme'})
        self.assertEqual(
            unit,
            "baseword",
            "did not handle building grammatical unit using existing property associated with no existing exponent"
        )

    def test_build_unit_nonexisting_property(self):
        unit = self.grammar.build_unit(
            "baseword",
            properties={'noncategory': 'nongrammeme'},
            all_requested=True
        )
        self.assertIsNone(
            unit,
            "did not handle avoiding building grammatical unit using nonexistent property"
        )

class GrammarOrderMorphosyntax(GrammarFixture):
    @classmethod
    def setUpClass(this_class):
        super(GrammarOrderMorphosyntax, this_class).setUpClass()
        # add properties to provide across ordered exponents
        this_class.grammar.properties.add("category", "grammeme1")
        this_class.grammar.properties.add("category", "grammeme2")
        # and for switching places
        this_class.grammar.properties.add("category", "grammemeSwap1")
        this_class.grammar.properties.add("category", "grammemeSwap2")

    def test_order_exponents(self):
        # add orderable exponents
        first_prefix = self.grammar.exponents.add(pre="first-", properties={'category': 'grammeme1'}, bound=True)
        second_prefix = self.grammar.exponents.add(pre="second-", properties={'category': 'grammeme2'}, bound=True)
        # order the exponents
        self.grammar.morphosyntax.add_exponent_order(first_prefix, inner=second_prefix)
        # see if exponents are in order when building word
        built_unit = self.grammar.build_unit("rootword", properties="grammeme1 grammeme2")
        self.assertEqual(
            built_unit,
            "first-second-rootword",
            "morphosyntax did not arrange exponents in the correct order"
        )

    def test_reorder_exponents(self):
        # add orderable exponents
        first_prefix = self.grammar.exponents.add(pre="first-", properties={'category': 'grammemeSwap1'}, bound=True)
        second_prefix = self.grammar.exponents.add(pre="second-", properties={'category': 'grammemeSwap2'}, bound=True)
        # order the exponents
        self.grammar.morphosyntax.add_exponent_order(first_prefix, inner=second_prefix)
        # reorder the exponents
        self.grammar.morphosyntax.add_exponent_order(first_prefix, outer=second_prefix)
        # see if exponents are in order when building word
        built_unit = self.grammar.build_unit("rootword", properties="grammemeSwap1 grammemeSwap2")
        self.assertEqual(
            built_unit,
            "second-first-rootword",
            "morphosyntax did not rearrange exponents to switch their order correctly"
        )

    # TODO: investigate why sometimes => 4512 instead of 1245
    def test_remote_order_exponents(self):
        # check that non-contiguous inners and outers are sorted
        # example: 1, 2, 4, 5 are sorted even though 3 is not present
        # add properties and exponents
        self.grammar.properties.add('n', '1')
        self.grammar.properties.add('n', '2')
        self.grammar.properties.add('n', '3')
        self.grammar.properties.add('n', '4')
        self.grammar.properties.add('n', '5')
        n_1 = self.grammar.exponents.add(post="1", properties={'n': '1'}, bound=True)
        n_2 = self.grammar.exponents.add(post="2", properties={'n': '2'}, bound=True)
        n_3 = self.grammar.exponents.add(post="3", properties={'n': '3'}, bound=True)
        n_4 = self.grammar.exponents.add(post="4", properties={'n': '4'}, bound=True)
        n_5 = self.grammar.exponents.add(post="5", properties={'n': '5'}, bound=True)
        
        # order exponents
        self.grammar.morphosyntax.add_exponent_order(n_2, inner=n_1, outer=n_3)
        self.grammar.morphosyntax.add_exponent_order(n_3, inner=n_2, outer=n_4)
        self.grammar.morphosyntax.add_exponent_order(n_5, inner=n_4)
        print({
            self.grammar.exponents.get(e_id)['post']: {
                'inner': [
                    self.grammar.exponents.get(c_id)['post']
                    for c_id in self.grammar.morphosyntax.exponent_order[e_id]['inner']
                ],
                'outer': [
                    self.grammar.exponents.get(c_id)['post']
                    for c_id in self.grammar.morphosyntax.exponent_order[e_id]['outer']
                ]
            }
            for e_id in self.grammar.morphosyntax.exponent_order
        })
        
        # see if exponents are in order when building word
        built_unit = self.grammar.build_unit("rootword", properties="4 2 1 5")

        self.assertEqual(
            built_unit,
            "rootword1245",
            "morphosyntax did not correctly arrange exponents when not requesting one skipped ordered inner or outer element"
        )
    
    def test_order_exponents_subset(self):
        # check that only requested exponents are sorted when morphosyntax
        # contains ordered info branching off to even more exponents
        self.grammar.properties.add('abc', 'A')
        self.grammar.properties.add('abc', 'B')
        self.grammar.properties.add('abc', 'C')
        self.grammar.properties.add('abc', 'D')
        self.grammar.properties.add('abc', 'E')
        abc_A = self.grammar.exponents.add(post="A", properties={'abc': 'A'}, bound=True)
        abc_B = self.grammar.exponents.add(post="B", properties={'abc': 'B'}, bound=True)
        abc_C = self.grammar.exponents.add(post="C", properties={'abc': 'C'}, bound=True)
        abc_D = self.grammar.exponents.add(post="D", properties={'abc': 'D'}, bound=True)
        abc_E = self.grammar.exponents.add(post="E", properties={'abc': 'E'}, bound=True)
        
        # order exponents
        self.grammar.morphosyntax.add_exponent_order(abc_B, inner=abc_A, outer=abc_C)
        self.grammar.morphosyntax.add_exponent_order(abc_D, inner=abc_C, outer=abc_E)
        
        # see if exponents are in order when building word
        built_unit = self.grammar.build_unit("rootword", properties="C B")

        self.assertEqual(
            built_unit,
            "rootwordBC",
            "morphosyntax failed to include only requested ordered exponents"
        )

class GrammarOrderSentences(GrammarFixture):
    @classmethod
    def setUpClass(this_class):
        super(GrammarOrderSentences, this_class).setUpClass()
        # add properties and word classes for defining exponents
        this_class.grammar.properties.add("case", "subject")
        this_class.grammar.properties.add("case", "object")
        this_class.grammar.properties.add("voice", "active")
        this_class.grammar.properties.add("voice", "passive")
        this_class.grammar.properties.add("aspect", "perfective")
        this_class.grammar.properties.add("aspect", "imperfective")
        this_class.grammar.word_classes.add("noun")
        this_class.grammar.word_classes.add("verb")
        # add exponents for nouns and verbs
        this_class.grammar.exponents.add(
            pre="a",
            bound=True,
            properties="perfective active",
            pos="verb"
        )
        this_class.grammar.exponents.add(
            pre="r",
            bound=True,
            properties="imperfective active",
            pos="verb"
        )
        this_class.grammar.exponents.add(
            pre="uk",
            bound=False,
            properties="subject",
            pos="noun"
        )
        this_class.grammar.exponents.add(
            pre="nu",
            bound=False,
            properties="object",
            pos="noun"
        )

    def test_build_sentence(self):
        self.grammar.sentences.add(
            name = "indefinite_imperfective",
            structure = [
                ["verb", "imperfective active"],
                ["noun", "subject"],
                ["noun", "object"]
            ],
            # TODO: allow translation
            #   - look in dictionary/corpus first
            #   - then fall back to this structure
            #   - ? perhaps have paradigms translate using grammatical properties
            # translation = [
            #     "a",
            #     1,
            #     "did",
            #     0,
            #     "a",
            #     2
            # ]
        )
        mock_verb = {
            'sound': 'tota',
            'spelling': 'tota',
            'definition': 'chase',
            'pos': 'verb'
        }
        mock_subject = {
            'sound': 'kata',
            'spelling': 'kata',
            'definition': 'cat',
            'pos': 'noun'
        }
        mock_object = {
            'sound': 'data',
            'spelling': 'data',
            'definition': 'dog',
            'pos': 'noun'
        }
        sentence = self.grammar.sentences.apply(
            "indefinite_imperfective",
            [mock_verb, mock_subject, mock_object]
        )
        self.assertEqual(
            sentence,
            # "A cat did chase a dog", # NOTE: if using translation
            "rtota uk kata nu data",
            "grammar failed to build (add and apply) a basic sentence"
        )

    def test_add_sentence(self):
        self.grammar.sentences.add(
            name = "indefinite_perfective_transitive",
            structure = [
                ["verb", "perfective active"],
                ["noun", "subject"],
                ["noun", "object"]
            ]
        )
        self.assertEqual(
            self.grammar.sentences.get("indefinite_perfective_transitive")[0],
            [
                self.grammar.parse_word_classes("verb"),
                self.grammar.parse_properties("perfective active"),
            ],
            "grammar failed to add a basic sentence"
        )
    
    def test_remove_sentence(self):
        self.grammar.sentences.add(
            name="deleted_sentence",
            structure=[
                ["verb", "perfective aspect"]
            ]
        )
        self.grammar.sentences.remove("deleted_sentence")
        self.assertNotIn(
            "deleted_sentence",
            self.grammar.sentences.sentences,
            "grammar failed to remove a sentence"
        )

    def test_update_sentence(self):
        self.grammar.sentences.add(
            name="updated_sentence",
            structure=[
                ["verb", "perfective aspect"]
            ]
        )
        self.grammar.sentences.update(
            "updated_sentence",
            [["verb", "imperfective aspect"]]
        )
        self.assertEqual(
            self.grammar.sentences.get("updated_sentence")[0][1],
            self.grammar.parse_properties("imperfective aspect"),
            "grammar failed to modify an existing sentence structure"
        )

# TODO: TEST intuitive buildout of more realistic looking words
#        - content differs but generally these tested actions are repeats
#
# grammar = Grammar()

# # add grammemes and pos
# grammar.word_classes.add(["noun", "verb"])
# grammar.properties.add_many({
#     'tense': ["present", "past", "future"],
#     'aspect': ["perfective", "imperfective"],
#     'number': ["singular", "plural"],
#     'case': ["nominative", "oblique"]
# })

# # add basic exponents
# plural_noun_exponent = grammar.exponents.add(
#     post="s",
#     properties={"case": "nominative", "number": "plural"},
#     bound=True
# )
# grammar.exponents.add_pos(plural_noun_exponent, "noun")

# # build words

# singular_noun = grammar.build_unit("house", properties="nominative singular", word_classes=('noun'))
# plural_noun = grammar.build_unit("house", properties="nominative plural", word_classes={'noun'})
# print(singular_noun, plural_noun)

# singular_noun = grammar.build_unit("mouse", properties="nominative singular", word_classes=["noun"])
# plural_noun = grammar.build_unit("mouse", properties="nominative plural", word_classes="noun")
# print(singular_noun, plural_noun)


# # test arrange morphosyntax order
# inner_affix = grammar.exponents.add(pre="(inn-", post="-ner)", properties={
#     'tense': "present"
# })
# print("inner affix: " + inner_affix)
# outer_affix = grammar.exponents.add(pre="out-", post="-ter", properties={
#     'aspect': "perfective"
# })
# print("outer affix: " + outer_affix)

# added_ordering = grammar.morphosyntax.add_exponent_order(outer_affix, inner=[
#     inner_affix
# ], outer=[])
# print(grammar.morphosyntax.exponent_order)

# orderly_unit = grammar.build_unit("base", properties="present perfective")
# print(orderly_unit)

# switched_ordering = grammar.morphosyntax.add_exponent_order(outer_affix, outer=[
#     inner_affix
# ])
# print(grammar.morphosyntax.exponent_order)

# orderly_unit = grammar.build_unit("base", properties="present perfective")
# print(orderly_unit)

# TODO: more robust testing of parse strings
