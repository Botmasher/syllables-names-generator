import unittest
from wordbuilder.draft.grammar import Grammar

## test discovery through CLI from this dir or above:
## `python3 -m unittest discover -v -p "test_*"`

def setUpModule():
    print("Setting up the entire test module")

def tearDownModule():
    print("Shutting down the entire test module")

class GrammarFixture(unittest.TestCase):
    @classmethod
    def setUpClass(this_class):
        """Instantiate grammar for all tests in the class"""
        print("Setting up a Grammar instance")
        this_class.grammar = Grammar()
    
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

    def test_rename_property(self):
        self.grammar.add_property("name_category", "name_grammeme")
        self.grammar.change_property_grammeme("name_category", "name_grammeme", "rename_grammeme")
        self.assertIsNotNone(
            self.grammar.get_property("name_category", "rename_grammeme"),
            "failed to change the property grammeme name"
        )
    
    def test_recategorize_property(self):
        self.grammar.add_property("categorize_category", "categorize_grammeme")
        self.grammar.change_property_category("categorize_category", "categorize_grammeme", "recategorize_category")
        self.assertIsNotNone(
            self.grammar.get_property("recategorize_category", "categorize_grammeme"),
            "failed to change the property category name"
        )

# TODO: word classes
#   - add_word_class
#   - update_word_class
#   - remove_word_class
#   - check for removed exponent ids in property includes/excludes (name is fine since it's by id)

# TODO: add word classes to property includes and excludes
# - through setupclass? or in word classes test itself?
# - test property word classes include, include, change_property_category

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
        self.grammar.change_property_category("categorized_category", "categorized_grammeme", "recategorized_category")
        self.assertIn(
            "recategorized_category",
            self.grammar.exponents.get(exponent_id, {}).get("properties", {}),
            "failed to update changed property category name within exponent details"
        )

    def test_change_exponent_property_category(self):
        self.grammar.add_property("named_category", "named_grammeme")
        exponent_id = self.grammar.add_exponent(post="test_post", properties={'named_category': 'named_grammeme'})
        self.grammar.change_property_grammeme("named_category", "named_grammeme", "renamed_grammeme")
        self.assertIn(
            "renamed_grammeme",
            self.grammar.exponents.get(exponent_id, {}).get("properties", {}).get("named_category", []),
            "failed to update changed property grammeme name within exponent details"
        )

# ## Cases from Grammar instantiation and testing

# # 1 - build properties
# grammar = Grammar()

# # expect grammar to add individually
# # TODO: ignore capitalization

# grammar.add_word_class("verb")
# grammar.add_property(category="tense", grammeme="past")
# grammar.add_property(category="tense", grammeme="present")
# grammar.add_property(category="mood", grammeme="indicative")
# added_property = grammar.add_property(category="mood", grammeme="interrogative")
# print(added_property)

# # expect grammar to add all

# # grammar.add_property("voice", "active")
# # grammar.add_property("voice", "passive")
# added_properties = grammar.add_properties({
#     'voice': ["active", "passive"]
# })
# print(added_properties)

# # negative tests - expect grammar to detect issue, avoid adding and return None
# #grammar.add_properties([])
# #grammar.add_properties([{}])
# #grammar.add_properties(['chocolate'])
# #grammar.add_properties([{'name': "xyz", 'favorites': 0}])
# #grammar.add_properties([{'favorites': 0}])

# print("Found property with grammeme 'past': ", grammar.find_properties(grammeme="past"))
# print("Found property with category 'tense': ", grammar.find_properties(category="tense"))
# print("Found property with category 'voice': ", grammar.find_properties(category="voice"))
# print("Found property with category 'emotion': ", grammar.find_properties(category="emotion"))
# # TODO: implement more robust search incl description and included/excluded classes
# #   - also use those include/excludes to test building words with requested recognized/unrecognized/mixed word classes

# # 2 - build exponents
# added_exponent = grammar.add_exponent(post="past", bound=True, properties={'tense': 'past'})
# added_exponent = grammar.add_exponent(pre="pres", post="ent", bound=False, properties={'tense': 'present'})
# added_exponent = grammar.add_exponent(pre="indi", post="cative", bound=False, properties={'mood': 'indicative'})
# # added_exponents = grammar.add_exponents([
# #     {'post': "l", 'bound': True, 'properties': {}}
# # ])
# print("Added exponent: ", added_exponent)
# #grammar.add_exponent(properties=["noun", "deixis", "proximal"])
# #grammar.add_exponent(pre=[], post=[], properties=[])
# #grammar.add_exponent(pre="", post="", properties=[])

# # 3 - build demo words
# #word_1 = grammar.build_word("poiuyt", properties={'tense': 'past'})
# #print(word_1)

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


# # UNPROVIDABLE PROPERTIES
# #
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
