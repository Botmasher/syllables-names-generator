import unittest
from ..draft import grammar

## test discovery through CLI from this dir or above:
## `python3 -m unittest discover -v -p "test_*"`

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
        self.assertEqual(self.grammar.word_classes, {}, "incorrect starting word_classes map")

    def test_default_exponents(self):
        self.assertEqual(self.grammar.exponents, {}, "incorrect starting exponents map")

    def test_default_properties(self):
        self.assertEqual(self.grammar.properties, {}, "incorrect starting properties map")

class GrammarProperties(GrammarFixture):
    def test_add_property(self):
        self.assertIsNotNone(
            self.grammar.add_property(category="added_category", grammeme="added_grammeme"),
            "failed to add property category-grammeme pair"
        )
    
    # TODO: add property various ways (dict, defaultdict, list)
    def test_add_property_none(self):
        self.assertIsNone(
            self.grammar.add_property(category="added_category", grammeme=None),
            "incorrect handling of adding new property with missing grammeme"
        )

    def test_add_properties(self):
        added_properties = self.grammar.add_properties({
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
        self.grammar.add_property("removed_category", "removed_grammeme")
        self.grammar.remove_property("removed_category", "removed_grammeme")
        self.assertIsNone(
            self.grammar.properties.get('removed_category', {}).get('removed_grammeme'),
            "failed to add then remove a property"
        )

    def test_update_property_description(self):
        test_description = "test description"
        self.grammar.add_property("updated_category", "updated_grammeme")
        self.grammar.update_property("updated_category", "updated_grammeme", description=test_description)
        self.assertEqual(
            self.grammar.properties.get("updated_category", {}).get("updated_grammeme", {}).get("description"),
            test_description,
            "failed to add then update a property's description attribute"
        )

    def test_get_property_existing(self):
        self.grammar.add_property("get_category", "get_grammeme")
        self.assertIsNotNone(
            self.grammar.get_property(category="get_category", grammeme="get_grammeme"),
            "failed to get a property that was added to the grammar"
        )

    def test_get_property_nonexisting(self):
        self.assertIsNone(
            self.grammar.get_property(category="noncategory", grammeme="nongrammeme"),
            "failed to handle getting property that was not added to the grammar"
        )

    def test_find_property_existing(self):
        self.grammar.add_property(category="find_category", grammeme="find_grammeme")
        self.assertEqual(
            self.grammar.find_properties(category="find_category")[0],
            ("find_category", "find_grammeme"),
            "did not find added category and grammeme using grammar find_properties"
        )
    
    # TODO: create uuids to test created and updated names
    #   - avoid potential conflicts from using such similar manual names across properties tests
    def test_rename_property_category(self):
        self.grammar.add_property("rename_category_category", "rename_category_grammeme")
        self.grammar.rename_property_category("rename_category_category", "renamed_category")
        self.assertEqual(
            self.grammar.properties.get("renamed_category", {}).get("rename_category_grammeme", {}).get('category'),
            "renamed_category",
            "failed to change the name of a category"
        )
    
    def test_rename_property_grammeme(self):
        self.grammar.add_property("rename_grammeme_category", "rename_grammeme_grammeme")
        self.grammar.rename_property_grammeme("rename_grammeme_category", "rename_grammeme_grammeme", "renamed_grammeme")
        self.assertIsNotNone(
            self.grammar.get_property("rename_grammeme_category", "renamed_grammeme"),
            "failed to change the property grammeme name"
        )
    
    def test_recategorize_property_grammeme(self):
        self.grammar.add_property("categorize_category", "categorize_grammeme")
        self.grammar.change_property_grammeme_category("categorize_category", "categorize_grammeme", "recategorize_category")
        self.assertIsNotNone(
            self.grammar.get_property("recategorize_category", "categorize_grammeme"),
            "failed to change the property grammeme's parent category"
        )

class GrammarExponents(GrammarFixture):
    @classmethod
    def setUpClass(this_class):
        super(GrammarExponents, this_class).setUpClass()
        this_class.grammar.add_property("exponent_category", "exponent_grammeme")
    
    def test_add_exponent(self):
        exponent_id = self.grammar.add_exponent(pre="test_pre", post="test_post", bound=True, properties={
            'exponent_category': 'exponent_grammeme'
        })
        self.assertIn(
            exponent_id,
            self.grammar.exponents,
            "could not add one new exponent"
        )
    
    def test_add_exponent_empty(self):
        self.assertIsNone(
            self.grammar.add_exponent(),
            "failed to avoid adding defaults-only new exponents with no details"
        )

    def test_add_exponents(self):
        added_exponent_ids = self.grammar.add_exponents([
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
        exponent_id = self.grammar.add_exponent(pre="added_pre", properties={'exponent_category': 'exponent_grammeme'})
        self.assertIn(
            exponent_id,
            self.grammar.exponents,
            "could not add a new exponent passing a properties map with a grammeme in a string"
        )

    def test_add_exponent_with_grammeme_collection(self):
        exponent_id = self.grammar.add_exponent(pre="added_pre", properties={'exponent_category': ['exponent_grammeme']})
        self.assertIn(
            exponent_id,
            self.grammar.exponents,
            "could not add a new exponent passing a properties map with a grammeme collection"
        )       

    def test_update_exponent(self):
        test_pre = "test_pre"
        exponent_id = self.grammar.add_exponent(pre="updated_pre", post="updated_post", properties={
            'exponent_category': 'exponent_grammeme'
        })
        self.grammar.update_exponent(exponent_id, pre=test_pre)
        self.assertEqual(
            self.grammar.exponents.get(exponent_id, {}).get('pre'),
            test_pre,
            "failed to add then update an exponent's attributes"
        )
    
    def test_add_remove_exponent(self):
        exponent_id = self.grammar.add_exponent(pre="added_pre", post="added_post", properties={
            'exponent_category': 'exponent_grammeme'
        })
        self.grammar.remove_exponent(exponent_id)
        self.assertIsNone(
            self.grammar.exponents.get('exponent_id'),
            "failed to add then remove an exponent"
        )
    
    def test_get_exponent(self):
        self.grammar.add_exponent(pre="get_pre", properties={'exponent_category': 'exponent_grammeme'})
        self.assertIsNotNone(
            self.grammar.is_exponent(pre="get_pre"),
            "failed to add then check if exponent exists"
        )

    def test_find_exponents(self):
        exponent_id = self.grammar.add_exponent(pre="existing_exponent", properties={'exponent_category': 'exponent_grammeme'})
        self.assertIn(
            exponent_id,
            self.grammar.find_exponents(pre="existing_exponent"),
            "failed to add then find existing exponent"
        )

    def test_find_exponent_nonexisting(self):
        self.assertEqual(
            self.grammar.find_exponents(pre="nonexisting_pre"),
            [],
            "failed to return empty list after searching for nonexistent exponent"
        )
    
    def test_change_exponent_property_category(self):
        self.grammar.add_property("categorized_category", "categorized_grammeme")
        exponent_id = self.grammar.add_exponent(post="test_post", properties={'categorized_category': 'categorized_grammeme'})
        self.grammar.change_property_grammeme_category("categorized_category", "categorized_grammeme", "recategorized_category")
        self.assertIn(
            "recategorized_category",
            self.grammar.exponents.get(exponent_id, {}).get("properties", {}),
            "failed to update changed property category name within exponent details"
        )

    def test_change_exponent_property_grammeme(self):
        self.grammar.add_property("named_category", "named_grammeme")
        exponent_id = self.grammar.add_exponent(post="test_post", properties={'named_category': 'named_grammeme'})
        self.grammar.rename_property_grammeme("named_category", "named_grammeme", "renamed_grammeme")
        self.assertIn(
            "renamed_grammeme",
            self.grammar.exponents.get(exponent_id, {}).get("properties", {}).get("named_category", []),
            "failed to update changed property grammeme name within exponent details"
        )

class GrammarWordClasses(GrammarFixture):
    @classmethod
    def setUpClass(this_class):
        super(GrammarWordClasses, this_class).setUpClass()
        this_class.grammar.add_property("exponent_category", "exponent_grammeme")
    
    def test_add_word_class(self):
        self.grammar.add_word_class("added_word_class")
        self.assertIn(
            "added_word_class",
            self.grammar.word_classes,
            "failed to add one new word class"
        )
    
    def test_update_word_class(self):
        self.grammar.add_word_class("updated_word_class")
        self.grammar.update_word_class("updated_word_class", name="renamed_word_class")
        self.assertIn(
            "renamed_word_class",
            self.grammar.word_classes,
            "failed to update the name of an added word class"
        )

    def test_remove_word_class(self):
        self.grammar.add_word_class("removed_word_class")
        self.assertIsNotNone(
            self.grammar.remove_word_class("removed_word_class"),
            "failed to remove added word class"
        )

    def test_add_word_class_to_property(self):
        self.grammar.add_word_class("included_word_class")
        self.grammar.add_property("added_pos_category", "added_pos_grammeme")
        self.grammar.add_property_word_class(
            "added_pos_category",
            "added_pos_grammeme",
            include="included_word_class"
        )
        self.assertIn(
            "included_word_class",
            self.grammar.properties['added_pos_category']['added_pos_grammeme']['include'],
            "failed to add word class to a property's includes/excludes"
        )
    
    def test_remove_word_class_from_property(self):
        self.grammar.add_word_class("excluded_word_class")
        self.grammar.add_property("removed_pos_category", "removed_pos_grammeme")
        self.grammar.add_property_word_class(
            "removed_pos_category",
            "removed_pos_grammeme",
            exclude="excluded_word_class"
        )
        self.grammar.remove_word_class("excluded_word_class")
        self.assertNotIn(
            "excluded_word_class",
            self.grammar.properties['removed_pos_category']['removed_pos_grammeme']['exclude'],
            "failed to delete removed word class from a property's includes/excludes"
        )

#TODO: test add_property and add_property_word_class to see if include-exclude sets can be added to/updated (word class name updated)/removed from
class GrammarBuildWords(GrammarFixture):
    @classmethod
    def setUpClass(this_class):
        super(GrammarBuildWords, this_class).setUpClass()
        # add a word class
        this_class.grammar.add_word_class("noun")
        # add basic properties
        this_class.grammar.add_property("category", "grammeme")
        this_class.grammar.add_property("category", "grammeme_noun", include="noun")
        this_class.grammar.add_property("category", "grammeme_verb", exclude="noun")
        this_class.grammar.add_property("category", "nonexponented_grammeme")
        # add basic exponents
        this_class.grammar.add_exponent(post="-verb", properties={'category': 'grammeme_verb'}, bound=True)
        this_class.grammar.add_exponent(pre="noun-", properties={'category': 'grammeme_noun'}, bound=True)
        this_class.grammar.add_exponent(pre="nounish", properties={'category': ['grammeme', 'grammeme_noun']}, bound=False)
        this_class.grammar.add_exponent(pre="circum-", post="-fix", properties={'category': 'grammeme'}, bound=True)

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
        unit = self.grammar.build_unit("baseword", properties={'category': 'grammeme_verb'}, word_classes="noun")
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

    
    # TODO: test with included/excluded word classes

    # # NOTE: fourth case, where existing exponent provides nonexisting property, covered in exponent and build word filters
    # # - test this though!

    # # build word with nonexisting property, which is not provided by any exponent
    # # - skip unrecognized properties (previously expected to )
    # # - CASE: no property exists for antipassive voice
    # #word_2a = grammar.build_word("poiuyt", properties='present tense past tense mood:indicative antipassive')
    # word_2a = grammar.build_word("poiuyt", properties={
    #     'tense': ['present', 'past'],
    #     'mood': 'indicative'
    # })
    # print(word_2a)

    # # build word with existing property but no exponent providing that property
    # # - fail to build if not all properties provided (when all_or_none is True)
    # # - CASE: no exponent exists for passive voice
    # word_2b = grammar.build_word("poiuyt", properties='present tense past tense mood:indicative passive')
    # print(word_2b)
    # word_2c = grammar.build_word("poiuyt", properties='present tense past tense mood:indicative passive', all_or_none=True)
    # print(word_2c)

    # # build word with unprovidable property removed
    # # - CASE: exponents exist to provide all requested properties
    # word_2d = grammar.build_word("poiuyt", properties='present tense past tense indicative mood')
    # print(word_2d)

    # #word_4 = grammar.build_word("kuxuf", properties='mood:indicative past indicative')
    # #print(word_4)


# ## Cases from Grammar instantiation and testing

# # TODO: ignore capitalization

# # TODO: implement more robust search incl description and included/excluded classes
# #   - also use those include/excludes to test building words with requested recognized/unrecognized/mixed word classes

# # TODO: Flexible Parsing
# # Consider shapes of strings expected to be parsed:
# #   "present tense indicative mood verb"
# #   "tense: present, mood: indicative, verb"
# #   "tense:pres mood:ind v"
# #   "pres ind v"
# #   "present tense indicative verb"
# #   "v, present, indicative"
# #   "pres-ind-v"
# #   ""
# #   "vpres"

# # LIMITS OF REQUESTED PROPERTIES
# #
# # NOTE: use modified .properties and .exponents structure to handle
# # requested properties smaller or larger than what's in the grammar
# #
# # - case 1: built word properties are less verbose than stored exponent properties
# #   - example: word is ['verb', 'past'] but past affix is ['verb', 'past', 'tense']
# #
# # - case 2: built word properties are more verbose than exponent
# #   - example: word is ['verb', 'past', 'tense'] but past affix is ['past']
# #
# # - case 3: built word properties are less verbose but cover multiple exponents
# #   - example: word is ['verb', 'past', 'tense'] but affixes are ['verb', 'finite'] and ['past', 'tense']
# #
# # - case 4: built word properties are empty
