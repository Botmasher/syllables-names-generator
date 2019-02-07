import uuid
import re
import random

# NOTE the grammar relates grammatical exponents <> grammatical properties
# - exponents are phones of affixes, adpositions, particles, pre or post a base
# - properties are categories, grammemes
# - word classes help filter or limit the application of exponents to built words
class Grammar:
    def __init__(self):
        # word classes used to include or exclude words for exponents
        self.word_classes = {}
        # map of category, grammatical value pairs with details for each value
        self.properties = {}
        # map of exponent details, including pointing to an exponent's property ids
        self.exponents = {}

    # TODO: nest properties data
    # - expected: requested properties clearly match one or more exponents
    # - issue: flattening everything as grammemes creates inconsistent judgments when requested properties vs stored exponent properties sets are not well matched
    #
    # - proposed solution A: create {category: {properties}}
    #   - requested properties must now be passed in a dict
    #   - OR requested properties may be a list of grammemes ONLY
    #   - perhaps store a list of word_classes
    #   - perhaps store word_classes per exponent that are included/excluded
    # - implementation:
    #   - give properties a category and value in add, update, remove and read
    #   - requested properties now expect {'category': 'value', ...} pairs
    #   - excluded properties can be set of categories or values
    #   - give exponents a reference to their must include {'category': 'value'} pairs
    #   - give exponents a list of excluded properties
    #
    # - proposed solution B: limit ONLY to grammemes (expect everything to be low level)
    #   - each grammeme has a unique name
    #   - exponents explicitly lay out include/exclude properties, allowing vetting of broader terms in requested

    # TODO: break merge_maps out as a util instead of limiting it to this class
    # functional dict building to avoid direct mutations in word class, property and exponent update methods
    def merge_maps(self, base_map, overlay_map, key_check=lambda x: x, value_check=lambda x: x):
        """Overlay map pairs with filtered keys and values onto a base map and return the new map"""
        # expect both an old "base" and a new "overlay" dict
        if not(type(base_map) is dict and type(overlay_map) is dict):
            print("Grammar merge_maps failed - invalid base map or overlay map")
            return
        # expect a valid filter function to validate overlayed keys and values
        if type(key_check).__name__ != 'function' or type(vale_check).__name__ != 'function':
            print("Grammar merge_maps failed - invalid checker functions")
            return
        # unpack old and new maps filtering the new one for proper types
        new_map = {
            **base_map,
            **{k: v for k, v in overlay_map.items() if key_check(k) and value_check(v)}
        }
        return new_map

    def add_word_class(self, word_class, abbreviation=None, description=None):
        """Add one word class or part of speech to the grammar"""
        if word_class in self.word_classes:
            print("Grammar add_word_class skipped {0} - word class already exists".format(word_class))
            return
        # create a new entry for the part of speech
        self.word_classes[word_class] = {
            'name': word_class,
            'abbreviation': abbreviation,
            'description': description
        }
        # read the created part of speech
        return self.word_classes[word_class]

    def update_word_class(self, word_class, abbreviation=None, description=None):
        """Modify the details (but not the name) of a single word class"""
        if word_class not in self.word_classes:
            print("Grammar update_word_class failed - unknown word class {0}".format(word_class))
            return
        # create new word class entry updating only changed details
        word_class_details = self.merge_maps(self.word_classes[word_class], {
            'abbreviation': abbreviation,
            'description': description
        }, value_check=lambda x: type(x) is str)
        self.word_classes[word_class] = word_class_details
        # read the modified part of speech
        return self.word_classes[word_class]

    def remove_word_class(self, word_class):
        """Delete one word class from word classes map and exponents that reference it"""
        if word_class not in self.word_classes:
            print("Grammar remove_word_class failed - unrecognized word class {0}".format(word_class))
            return
        # delete part of speech from the map
        removed_word_class = self.word_classes[word_class]
        self.word_classes[word_class].pop(word_class)
        # remove part of speech from all exponents that exclude and include it
        for exponent_id, exponent_details in self.exponents:
            if word_class in exponent_details['exclude']:
                self.exponents[exponent_id]['exclude'].remove(word_class)
            if word_class in exponent_details['include']:
                self.exponents[exponent_id]['include'].remove(word_class)
        # return deleted details
        return removed_word_class

    def get_property(self, category=None, value=None):
        """Read one grammatical value from one category in the grammar"""
        try:
            return self.properties[category][value]
        except:
            return

    def add_property(self, category=None, value=None, abbreviation=None, description=None, create_category=True):
        """Add one grammatical value to an existing category in the grammar"""
        if not (category and value and type(category) is str and type(value) is str):
            print("Grammar add_property failed - expected category and value to be non-empty strings")
            return
        # check if property category or grammeme already exists
        if category not in self.properties:
            if create_category:
                self.properties[category] = {}
            else:
                print("Grammar add_property failed - unrecognized category {0}".format(category))
                return
        if value in self.properties[category]:
            print("Grammar add_property failed - category {0} already contains grammatical value {1} - did you mean to run update_property?".format(category, value))
            return
        # create a new entry for the grammeme
        self.properties[category][value] = {
            'category': category,
            'value': value,
            'abbreviation': abbreviation if type(abbreviation) is str else None,
            'description': description if type(description) is str else None
        }
        # read the created entry
        return self.get_property(category, value)

    def add_properties(self, properties_details):
        """Add a map of grammatical values within categories to the grammar"""
        if type(properties_details) is not dict:
            print("Grammar add_properties failed - invalid properties map {0}".format(properties_details))
            return
        # store each new grammatical value added to the grammar
        # verify it has the expected details structure:
        # {
        #   category: [
        #       {'value': str, 'abbreviation': str, 'description': str},
        #       ...
        #   ],
        #   ...
        # }
        added_properties = []
        for category, values in properties_details.items():
            # skip non-list categories
            if type(values) not in (list, tuple):
                print("Grammar add_properties skipped category {0} - invalid values list {1}".format(category, values))
                continue
            # iterate through values and add each category:value
            for value in values:
                if type(value) is not dict or 'value' not in value:
                    print("Grammar add_properties skipped invalid entry {0}:{1} - expected map with a 'value'".format(category, value))
                    continue
                # pass value to create along with optional attributes
                value = property['value']
                abbreviation = value['abbreviation'] if 'abbreviation' in value else None
                description = value['description'] if 'description' in value else None
                property = self.add_property(category=category, value=value, abbreviation=abbreviation, description=description)
                # build up list of added properties
                property and added_properties.append(property)
        return added_properties

    def update_property(self, category, value, abbreviation=None, description=None):
        """Modify any details for one grammatical property"""
        if not self.get_property(category, value):
            print("Grammar update_property failed - invalid category value {0}:{1}".format(category, value))
            return
        # create new property entry with modified details
        grammatical_value_details = self.merge_maps(self.properties[category][value], {
            'abbreviation': abbreviation,
            'description': description
        }, value_check=lambda x: type(x) is str)
        self.properties[category][value] = grammatical_value_details
        # access and return the created details
        return self.get_property(category, value)

    def remove_property(self, category, value):
        """Delete the record for and exponent references to one property from the grammar"""
        if category not in self.properties or value not in self.properties[category]:
            print("Grammar remove_property failed - unknown category value {0}:{1}".format(category, value))
            return
        # reference deleted details
        removed_property = self.get_property(category, value)
        # delete property key and details
        self.properties[category].pop(value)
        # delete property from exponent properties category sets that have it
        for exponent_id, exponent_details in self.exponents.items():
            if category in exponent_details['properties'] and value in exponent_details['properties'][category]:
                self.exponents[exponent_id]['properties'][category].remove(value)
                # also delete the category from properties if it is left empty
                if self.exponents[exponent_id]['properties'][category] == set():
                    self.exponents[exponent_id]['properties'].pop(category)
        # return the deleted details
        return removed_property

    # TODO: parse single-string exponent properties as category:value pairs
    #   - like "present tense indicative mood"
    #   - even tolerate dropping the category like "present tense indicative"

    # TODO: shouldn't the properties be the ones storing include/exclude?
    #   - it's not that some exponents are present tense verbs and others are for present tense nouns
    #   - it's that a grammar may have a property associated with a word class

    # NOTE: exponent['properties'] now have this structure:
    # {
    #   category: {value, ...},     # grammemes set NOT dict of value:details pairs as in self.properties
    #   category: 'value'           # a single string category also allowed
    #   ...
    # }
    def add_exponent(self, pre="", post="", bound=True, properties={}, include=[], exclude=[]):
        """Add one grammatical exponent to the grammar"""
        if not ((pre or post) and (type(pre) is str and type(post) is str)):
            print("Grammar add_exponent failed - expected pre or post exponent string")
            return

        # structure the categories and values of included properties
        exponent_properties = {}
        for category, values in properties.items():
            # avoid non-existing categories
            if category not in self.properties:
                print("Grammar add_exponent failed - invalid grammatical category {0}".format(category))
                return
            exponent_properties[category] = set()
            # format a set for a single grammeme in one category, like past tense
            if type(values) is str:
                if not self.get_property(category, value):
                    print("Grammar add_exponent failed - invalid grammatical value {0}".format(value))
                    return
                values = {values}
            # add one or more grammemes in one category, like past and present tense
            for value in values:
                # check that property exists then build it into this exponent
                if not self.get_property(category, value):
                    print("Grammar add_exponent failed - invalid grammatical value {0} in category {1}".format(value, category))
                    return
                exponent_properties[category].add(value)

        # check excluded word classes
        # TODO: allow excluded properties of any kind
        included_word_classes = {
            word_class for word_class in exclude
            if word_class in self.word_classes
        }
        excluded_word_classes = {
            word_class for word_class in include
            if word_class in self.word_classes
        }

        # store exponent details
        exponent_id = "grammatical-exponent-{0}".format(uuid.uuid4())
        self.exponents[exponent_id] = {
            'id': exponent_id,
            'pre': pre,
            'post': post,
            'bound': bound,
            'properties': exponent_properties,
            'include': included_word_classes,
            'exclude': excluded_word_classes
        }
        return exponent_id

    def add_exponents(self, exponents_details):
        """Add a list of grammatical exponents with properties"""
        if type(exponents_details) is not list:
            print("Grammar add_exponents failed - invalid list of exponents {0}".format(exponents_details))
            return
        # prepare to store ids of created exponents
        exponent_ids = []
        # shape and store details
        for exponent in exponents_details:
            # verify expected details for an exponent
            if type(exponent) is not dict or 'properties' not in exponent or not ('pre' in exponent or 'post' in exponent):
                print("Grammar add_exponents skipped invalid element - expected dict with 'properties' and 'pre' or 'post', got {0}".format(exponent))
                continue
            # shape new details layering default values over missing details
            new_exponent_details = self.merge_maps(exponent, {
                'pre': "",
                'post': "",
                'bound': True,
            }, key_check=lambda x: x not in exponent)
            # create an exponent entry using the new details
            exponent_id = self.add_exponent(
                pre=new_exponent_details['pre'],
                post=new_exponent_details['post'],
                bound=new_exponent_details['bound'],
                properties=new_exponent_details['properties']
            )
            # keep references to successful exponents
            exponent_id and exponent_ids.append(exponent_id)
        return exponent_ids

    def remove_exponent(self, exponent_id):
        """Delete the record for one exponent from the grammar"""
        # check that the exponent exists
        if exponent_id not in self.exponents:
            print("Grammar remove_exponent failed - unknown id {0}".format(exponent_id))
            return
        # keep a copy of the details to return
        removed_exponent = self.exponents[exponent_id]
        # delete exponent id and details
        self.exponents.pop(exponent_id)
        return removed_exponent

    def update_exponent(self, exponent_id, pre="", post="", properties={}, bound=None):
        """Modify the basic details of one grammatical exponent"""
        # check that the exponent exists
        if exponent_id not in self.exponents:
            print("Grammar update_exponent failed - unknown exponent id {0}".format(exponent_id))
            return
        # filter requested category, values sets through the existing properties
        # TODO: abstract this and use for checking updated properties maps elsewhere in the grammar
        updated_properties = {
            category: set(values) for category, values in properties.items()
            if category in self.properties
            and type(values) in (set, list, tuple)
            and [value for value in values if value in self.properties[category]]
        }
        # create new entry with non-empty details overlayed onto existing ones
        updated_exponent_details = self.merge_maps(
            self.exponents[exponent_id],
            {
                'pre': pre if pre and type(pre) is str else None,
                'post': post if post and type(post) is str else None,
                'bound': bound if type(bound) is bool else None,
                'properties': updated_properties if updated_properties else None
            },
            value_check=lambda x: x is not None
        )
        # assign the existing exponent to point to the new details
        self.exponents[exponent_id] = updated_exponent_details
        return exponent_id

    # TODO: update finding, checking and building methods below
    #       to use the data and grammatical crud methods above
    #
    # /!\ actively under construction /!\
    #

    def unabbreviate_property(self, abbreviation, first_only=False):
        """Search for full property names that use the abbreviation"""
        # NOTE: this works based on property ids and names being unique
        property_names = []
        # search through all properties details for matching abbreviations
        for property_id, property_details in self.properties.items():
            if abbreviation == property_details['abbreviation']:
                property_names.append(property_id)
                # stop the search at the first matching property
                if first_only:
                    break
        return property_names

    def find_property_ids(self, name=None, abbreviation=None, description=None, first_only=False):
        """Return every property (or optionally the first only) with the matching details"""
        if not name or abbreviation or description:
            print("Grammar find_property_ids failed - invalid details given")
            return
        found_property_ids = []
        query_details = {
            'name': name,
            'abbreviation': abbreviation,
            'description': description
        }
        # search through properties where details match query details not left blank
        for property_id, property_details in self.properties.items():
            query_details['name'] = name if name is not None else property_details['name']
            query_details['abbreviation'] = abbreviation if abbreviation is not None else property_details['abbreviation']
            query_details['description'] = description if description is not None else property_details['description']
            if query_details['name'] == property_details['name'] and query_details['description'] == property_details['description'] and query_details['abbreviation'] == property_details['abbreviation']:
                if first_only:
                    return property_id
                found_property_ids.append(property_id)
        return found_property_ids

    def find_exponent_ids(self, pre=None, post=None, bound=None, first_only=False):
        """Return every exponent (or optionall the first only) with the matching details"""
        if pre is None and post is None:
            print("Grammar find_exponent_ids failed - invalid details given")
            return
        # prepare to store exponents with matching details
        found_exponent_ids = []
        # search for exponents where details match non-blank query details
        for exponent_id, exponent_details in self.exponents.items():
            # overlay a new details map switching in non-null query args
            query_details = self.merge_maps(exponent_details, {
                'pre': pre,
                'post': post,
                'bound': bound
            }, value_check=lambda x: x is not None)
            # check if the query exponent details match the current exponent
            if query_details == exponent_details:
                # build up a list of all exponents matching these same details
                found_exponent_ids.append(exponent_id)
                # return the exponent immediately if only one is requested
                if first_only:
                    break
        # return a list of exponents with matching details
        return found_exponent_ids

    # TODO incorporate property name -> id reads from above instead of treating names as ids
    def identify_properties(self, properties, use_abbreviations=False):
        """Split a string or list of property names into a set of property ids"""
        if type(properties) not in (tuple, set, list, str):
            print("Grammar failed to parse properties - expected a list or string")
            return
        # create a set of unique property terms
        properties_split = re.split(r"\W+", properties) if type(properties) is str else properties
        property_ids = []
        # search for property name in properties
        # NOTE this commits the Grammar to relying on unique full property names
        for property in properties_split:
            # add found full property names including optionally for abbreviated properties
            if property in self.properties:
                property_ids.append(property)
            elif use_abbreviations:
                unabbreviated_properties = self.unabbreviate_property(property)
                unabbreviated_properties and property_ids.append(unabbreviated_properties[0])
            else:
                continue
        properties_set = set(properties_split)
        return properties_set

    def is_exponent_id(self, exponent_id):
        """Check if the id is in the grammar exponent map"""
        return exponent_id in self.exponents

    def is_property_id(self, property_id):
        """Check if the id is in the grammatical properties map"""
        return property_id in self.properties

    def is_exponent(self, pre="", post=""):
        """Check if the given sounds are an exponent in this grammar"""
        if not (pre or post):
            print("Grammar is_exponent failed - expected pre or post string")
            return
        # search details for pre/post matches
        for exponent_details in self.exponents.values():
            # circumfix or circumposition
            if exponent_details['pre'] and exponent_details['post'] and pre == exponent_details['pre'] and post == exponent_details['post']:
                return True
            # prefix or preposition
            if exponent_details['pre'] and pre == exponent_details['pre']:
                return True
            # suffix or postposition
            if exponent_details['post'] and post == exponent_details['post']:
                return True
        return False

    def is_property(self, name="", abbreviation=""):
        """Check if a grammatical property name or abbreviation is part of the grammar"""
        if name and abbreviation:
            print("Grammar is_property failed - expected either property name or abbreviation")
            return
        # search property details for matching name or abbreviation
        for property_details in self.properties.values():
            if abbreviation and name == property_details['abbreviation']:
                return True
            if name and name == property_details['name']:
                return True
        return True

    # TODO deal with properties smaller or larger than what's in the grammar
    #
    # - case 1: built word properties are less verbose than stored exponent properties
    #   - example: word is ['verb', 'past'] but past affix is ['verb', 'past', 'tense']
    #
    # - case 2: built word properties are more verbose than exponent
    #   - example: word is ['verb', 'past', 'tense'] but past affix is ['past']
    #
    # - case 3: built word properties are less verbose but cover multiple exponents
    #   - example: word is ['verb', 'past', 'tense'] but affixes are ['verb', 'finite'] and ['past', 'tense']
    #
    def build_word(self, root, properties=[], avoid_redundant_exponents=False):
        """Build up relevant morphology using the given grammatical properties"""
        if not(type(root) is str and properties and type(properties) in (list, tuple, set)):
            print("Grammar build_word failed - invalid root string {0} or properties list {1}".format(root, properties))
            return

        print("Building word...")
        # find all relevant exponents
        matching_exponents = []
        # typecast for set operations
        properties_set = set(properties)
        # exponent ids and their shared properties with requested properties
        common_properties = {}
        # find the most likely properties match
        for exponent_id, exponent_details in self.exponents.items():
            # TODO determine exponent-word properties match, accounting for cases above
            # - store matched exponent id with match set of query properties
            # - if later exponent intersects those query properties and more, toss the old id and replace it
            # - ? so go through all interims each loop and replace?
            # - ? if any are subsets
            #
            # - expect requested properties set to be smaller per requested exponent than the exponents
            # - expect requested properties set to be larger per requested exponent if requesting multiple exponents
            # - expect requested properties set not to duplicate properties possibly repeated in multiple exponents
            # - expect exponent properties set to contain all relevant properties possibly requested

            # retrieve all property names for this exponent

            # TODO if using property names, AGAIN ask why not just have them be unique?)
            # TODO consider must-exclude and must-include properties sets (see note in branches below)

            exponent_properties_set = {self.properties[property_id]['name'] for property_id in exponent_details['properties']}
            # check for common members between requested properties and exponent properties
            property_intersection = properties_set & exponent_properties_set
            # search for properties in common
            if property_intersection:
                # store the exponent and intersection to compare for most relevant exponents later
                common_properties[exponent_id] = property_intersection
                # found a perfect match - set it as the exponent
                if len(property_intersection) == len(properties_set):
                    # NOTE stops at first match of multiple; consider that {verb} may "exactly" match many
                    print("found exact exponent properties match: ", properties_set)
                    matching_exponents = [exponent_id]
                    break

        print("common properties: ", common_properties)
        print("matching exponents: ", matching_exponents)
        # hold the requested properties steady, throw exponent properties against it
        # if any exponent properties match at all, keep them
        # not ditching them because they have fewer or greater common_properties
        # only ditching them if their common_properties are perfect subsets of other property matchsets
        #
        # PROBLEM: what if you only match {verb, tense} but not the specific tense?
        #   - either add one exponent arbitrarily (the zeroth one found)
        #   - or add a bunch of exponents for different verb tenses
        #   - really tenable? instead resort to the most atomic properties only (grammemes-like)?

        # PROBLEM: is {verb, tense, past, indicative, first, person, singular} a better match than {verb, tense, past}?

        # no exact match exponent superset found - guess likely matches
        # pick through exponents to find only highest supersets of each other
        # /!\ NOTE quadratic /!\
        if not matching_exponents:
            # iterate through exponents with intersecting ("common") properties
            # find "better" intersections until you're left with a "best":
            # - if an exponent has a property set that is a strict superset of this one, it is a better intersection
            # - if no exponent_ids have larger property sets than this, keep it
            # TODO can you check for best supersections during the intersection loop above instead of this comparison?
            best_matches = set()
            for exponent_id, property_intersection in common_properties.items():
                best_match = exponent_id
                best_property_set = property_intersection
                # check for largest strict supersets of the common property set
                for compared_exponent_id, compared_property_intersection in common_properties.items():
                    if compared_property_intersection.issuperset(best_property_set) and len(compared_property_intersection) > len(best_property_set):
                        best_match = compared_exponent_id
                        best_property_set = compared_property_intersection
                best_matches.add(best_match)
            matching_exponents = list(best_matches)

        # list of either one exact exponent properties match or one or more guesses
        print(matching_exponents)

        # add exponents to build up the word
        word = root
        for exponent_id in matching_exponents:
            word = self.attach_exponent(word, exponent_id=exponent_id)
        return word

    def attach_exponent(self, stem, exponent_id=None):
        """Attach one grammatical exponent to a string of phones"""
        if not (stem and exponent_id) or not self.is_exponent_id(exponent_id):
            print("Grammar attach_exponent failed - unknown stem word or exponent id")
            return
        exponented_word = stem
        exponent = self.exponents[exponent_id]

        # exponent is affix
        if exponent['bound']:
            exponented_word = exponent['pre'] + exponented_word + exponent['post']
        # exponent is particle or adposition structure
        else:
            if exponent['pre']:
                exponented_word = "{0} {1}".format(exponent['pre'], exponented_word)
            if exponent['post']:
                exponented_word = "{0} {1}".format(exponented_word, exponent['post'])
        return exponented_word

# 1 - build properties
grammar = Grammar()

# expect grammar to add individually
# TODO ignore caps
grammar.add_property("verb", abbreviation="v", description="word class: for verbs")
grammar.add_property("noun", abbreviation="n", description="word class: for nouns")
grammar.add_property("adjective", abbreviation="adj", description="word class: for adjectives")
grammar.add_property("adverb", abbreviation="adv", description="word class: for adverbs")
added_property = grammar.add_property("particle", abbreviation="part", description="word class: for particles")
print(added_property)

# expect grammar to add all
# TODO limit/filter which properties must be excluded or included with another?
# - example: cases can include only nouns, adjectives
# TODO allow multiple abbreviations, ? maybe strip of dot so nom. pl. -> nom pl
added_properties = grammar.add_properties([
    {'name': "case", 'description': "category: nominal case"},
    {'name': "nominative", 'abbreviation': "nom", 'description': "grammeme: case mainly for subjects"},
    {'name': "accusative", 'abbreviation': "acc", 'description': "grammeme: case mainly for objects"},
    {'name': "number", 'abbreviation': "num", 'description': "category: grammatical number"},
    {'name': "singular", 'abbreviation': "s", 'description': "grammeme: singular number"},
    {'name': "plural", 'abbreviation': "pl", 'description': "grammeme: plural number"},
    {'name': "deixis", 'description': "category: distance indicators"},
    {'name': "proximal", 'abbreviation': "prox", 'description': "grammeme: near distance"},
    {'name': "distal", 'abbreviation': "dist", 'description': "grammeme: far distance"},
    {'name': "aspect", 'abbreviation': "asp", 'description': "category: verbal aspect"},
    {'name': "perfective", 'description': "grammeme: perfective aspect"},
    {'name': "imperfective", 'description': "grammeme: imperfective aspect"},
    {'name': "tense", 'abbreviation': "tns", 'description': "category: verbal tense"},
    {'name': "present", 'abbreviation': "pres", 'description': "grammeme: present tense"},
    {'name': "past", 'abbreviation': "past", 'description': "grammeme: past tense"},
    {'name': "mood", 'description': "grammeme: verbal mood"},
    {'name': "indicative", 'abbreviation': "ind", 'description': "grammeme: indicative mood"},
    {'name': "voice", 'abbreviation': "vc", 'description': "category: voice"},
    {'name': "active", 'abbreviation': "act", 'description': "grammeme: active voice"}
])
print(added_properties)
# expect grammar to detect issue, avoid adding and return None
grammar.add_properties([])
grammar.add_properties([{}])
grammar.add_properties(['chocolate'])
grammar.add_properties([{'name': "xyz", 'favorites': 0}])
grammar.add_properties([{'favorites': 0}])

print(grammar.is_property(name="mood"))
print(grammar.is_property(abbreviation="pl"))
print(grammar.is_property(name="verb", abbreviation="v"))

# 2 - build exponents
grammar.add_exponent(post="tele", bound=False, properties=["noun", "deixis", "proximal"])
added_exponent = grammar.add_exponent(post="talak", bound=False, properties=["noun", "deixis", "distal"])
added_exponents = grammar.add_exponents([
    {'post': "l", 'bound': True, 'properties': ["verb", "present", "tense", "perfective", "aspect", "indicative", "mood", "active", "voice"]},
    {'post': "hapa", 'bound': True, 'properties': ["verb", "past", "tense", "perfective", "aspect", "indicative", "mood", "active", "voice"]}
])
print(added_exponent)
print(added_exponents)
grammar.add_exponent(properties=["noun", "deixis", "proximal"])
grammar.add_exponent(pre=[], post=[], properties=[])
grammar.add_exponent(pre="", post="", properties=[])

# 3 - build demo words
word_1 = grammar.build_word("poiuyt", properties=["verb", "past"])
print(word_1)
word_2 = grammar.build_word("poiuyt", properties=["verb"])
print(word_2)
