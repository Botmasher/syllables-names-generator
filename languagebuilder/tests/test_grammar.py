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
            'added_categories': ('added_grammemes_1', 'added_grammemes_2')
        })
        added_properties = list(filter(
            lambda x: isinstance(x, dict) and 'grammeme' in x,
            added_properties
        ))
        self.assertEqual(
            len(added_properties),
            2,
            "could not add multiple properties"
        )
    
    def test_add_remove_property(self):
        self.grammar.properties.add("removed_category", "removed_grammeme")
        self.grammar.properties.remove("removed_category", "removed_grammeme")
        self.assertIsNone(
            self.grammar.properties.get('removed_category', 'removed_grammeme'),
            "failed to add then remove a property"
        )

    def test_update_property_description(self):
        test_description = "test description"
        self.grammar.properties.add("updated_category", "updated_grammeme")
        self.grammar.properties.update("updated_category", "updated_grammeme", description=test_description)
        self.assertEqual(
            self.grammar.properties.get("updated_category", "updated_grammeme").get("description"),
            test_description,
            "failed to add then update a property's description attribute"
        )

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
        self.assertEqual(
            self.grammar.properties.get("renamed_category", "rename_category_grammeme").get('category'),
            "renamed_category",
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
        exponent_id = self.grammar.exponents.add(pre="pre", properties={'category': 'grammeme'})
        self.grammar.exponents.add_pos(exponent_id, "added_exponent_pos")
        self.assertIn(
            "added_exponent_pos",
            self.grammar.exponents.get(exponent_id)['pos'],
            "failed to add word class to an exponent's pos collection"
        )

    def test_remove_word_class_from_exponent_pos(self):
        self.grammar.word_classes.add("excluded_exponent_pos")
        exponent_id = self.grammar.exponents.add(post="-post", properties={'category': 'grammeme'})
        self.grammar.exponents.remove_pos(exponent_id, "excluded_exponent_pos")
        self.assertNotIn(
            "excluded_exponent_pos",
            self.grammar.exponents.get(exponent_id)['pos'],
            "failed to remove word class directly from an exponent's pos collection"
        )
    
    def test_remove_word_class_then_check_exponent_pos(self):
        self.grammar.word_classes.add("removed_exponent_pos")
        exponent_id = self.grammar.exponents.add(pre="pre", properties={'category': 'grammeme'})
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
        unit = self.grammar.build_unit("baseword", properties={'noncategory': 'nongrammeme'})
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

# TODO: more robust testing of parse strings
