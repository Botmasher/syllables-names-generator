import uuid
import re
import random

# NOTE the grammar relates grammatical exponents <> grammatical properties
# - exponents are phones of affixes, adpositions, particles, pre or post a base
# - properties are word classes, categories, grammemes
class Grammar:
    def __init__(self):
        # map of details about each property
        # NOTE if property names are not unique this will cause conflicts on read
        # TODO consider returning to property names instead of generated ids
        self.properties = {}
        # map of exponent details, including pointing to an exponent's property ids
        self.exponents = {}

    # TODO store ids here or in add_exponent
    def add_property(self, property, abbreviation=None, description=None):
        """Add one word class, category or grammeme to the grammar"""
        if not property or type(property) is not str:
            print("Grammar add_property failed - expected property to be non-empty string")
            return
        # store property using name as lookup key
        property_id = "grammatical-property-{0}".format(uuid.uuid4())
        self.properties[property_id] = {
            'id': property_id,
            'name': property,
            'abbreviation': abbreviation if type(abbreviation) is str else None,
            'description': description if type(description) is str else None
        }
        return property_id

    def add_properties(self, properties_details):
        """Add a list of word classes, categories or grammemes to the grammar"""
        if type(properties_details) is not list:
            print("Grammar add_properties failed - invalid list of properties {0}".format(properties_details))
            return
        # pass each property through and store its id in the grammar
        property_ids = []
        for property in properties_details:
            if type(property) is not dict or 'name' not in property:
                print("Grammar add_properties skipped invalid element - expected dict with 'name', got {0}".format(property))
                continue
            name = property['name']
            abbreviation = property['abbreviation'] if 'abbreviation' in property else None
            description = property['description'] if 'description' in property else None
            property_id = self.add_property(name, abbreviation=abbreviation, description=description)
            property_id and property_ids.append(property_id)
        return property_ids

    def add_exponent(self, pre="", post="", bound=True, properties=[]):
        """Add one grammatical exponent to the grammar"""
        if not ((pre or post) and (type(pre) is str and type(post) is str)):
            print("Grammar add_exponent failed - expected pre or post exponent string")
            return

        # TODO update to use unique names as ids
        exponent_properties = set()
        for property in properties:
            property_id = self.find_property_ids(name=property, first_only=True)
            if not property_id:
                property_id = self.find_property_ids(abbreviation=property, first_only=True)
                if not property_id:
                    print("Grammar add_exponent failed - properties has unknown property name or abbreviation {0}".format(property))
                    return
            exponent_properties.add(property_id)

        # store exponent details
        exponent_id = "grammatical-exponent-{0}".format(uuid.uuid4())
        self.exponents[exponent_id] = {
            'id': exponent_id,
            'pre': pre,
            'post': post,
            'bound': bound,
            'properties': exponent_properties
        }
        return exponent_id

    def add_exponents(self, exponents_details):
        """Add a list of grammatical exponents with properties"""
        if type(exponents_details) is not list:
            print("Grammar add_exponents failed - invalid list of exponents {0}".format(exponents_details))
            return
        exponent_ids = []
        for exponent in exponents_details:
            if type(exponent) is not dict or 'properties' not in exponent or not ('pre' in exponent or 'post' in exponent):
                print("Grammar add_exponents skipped invalid element - expected dict with 'properties' and 'pre' or 'post', got {0}".format(exponent))
                continue
            pre = exponent['pre'] if 'pre' in exponent else ""
            post = exponent['post'] if 'post' in exponent else ""
            bound = exponent['bound'] if 'bound' in exponent else True
            properties = exponent['properties']
            exponent_id = self.add_exponent(pre=pre, post=post, bound=bound, properties=properties)
            exponent_id and exponent_ids.append(exponent_id)
        return exponent_ids

    def remove_property(self, property_id):
        """Delete the record for and exponent references to one property from the grammar"""
        if property_id not in self.exponents:
            print("Grammar remove_property failed - unknown id {0}".format(property_id))
            return
        # delete property key and details
        removed_property = self.properties[property_id]
        self.properties.pop(property_id)
        # delete property from exponents that have it
        for exponent_id, exponent_details in self.exponents.items():
            if property_id in exponent_details['properties']:
                self.exponents[exponent_id]['properties'].remove(property_id)
        return removed_property

    def remove_exponent(self, exponent_id):
        """Delete the record for one exponent from the grammar"""
        if exponent_id not in self.exponents:
            print("Grammar remove_exponent failed - unknown id {0}".format(exponent_id))
            return
        # delete exponent id and details
        removed_exponent = self.exponents[exponent_id]
        self.exponents.pop(exponent_id)
        return removed_exponent

    def update_property(self, property_id, name=None, abbreviation=None, description=None):
        """Modify any details for one grammatical property"""
        if not self.is_property_id(property_id):
            print("Grammar update_property failed - invalid property id")
            return
        property = self.properties[property_id]
        self.properties[property_id] = {
            'id': property['id'],
            'name': name if name and type(name) is str else property['name'],
            'abbreviation': abbreviation if abbreviation and type(abbreviation) is str else property['abbreviation'],
            'description': description if abbreviation and type(abbreviation) is bool else property['description']
        }
        return property_id

    def update_exponent(self, exponent_id, pre="", post="", bound=None):
        """Modify any details for one grammatical exponent"""
        if not self.is_exponent_id(exponent_id):
            print("Grammar update_exponent failed - invalid exponent id")
            return
        exponent = self.exponents[exponent_id]
        self.exponents[exponent_id] = {
            'id': exponent['id'],
            'pre': pre if pre and type(pre) is str else exponent['pre'],
            'post': post if post and type(post) is str else exponent['post'],
            'bound': bound if bound and type(bound) is bool else exponent['bound'],
            'properties': exponent['properties']
        }
        return exponent_id

    # read
    def unabbreviate_property(self, abbreviation):
        """Return full property names for properties that use the abbreviation"""
        # NOTE this works when property ids and names are the same and unique
        properties = []
        for property_id, property_details in self.properties.items():
            if abbreviation == property_details['abbreviation']:
                properties.append(property_id)
        return properties

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
        found_exponent_ids = []
        query_details = {
            'pre': None,
            'post': None,
            'bound': None
        }
        # search for exponents where details match non-blank query details
        for exponent_id, exponent_details in self.exponents.items():
            query_details['pre'] = pre if pre is not None else exponent_details['name']
            query_details['post'] = post if post is not None else exponent_details['post']
            query_details['bound'] = bound if bound is not None else exponent_details['bound']
            if query_details['pre'] == exponent_details['pre'] and query_details['post'] == exponent_details['post'] and query_details['bound'] == exponent_details['bound']:
                if first_only:
                    return exponent_id
                found_exponent_ids.append(exponent_id)
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
