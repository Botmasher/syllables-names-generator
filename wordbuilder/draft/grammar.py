import uuid
import re
import random

# TODO rethink how affixes, particles, word relations work
#   - affixes, adpositions, particles aren't always one per value
#   - often overlapping values to get to a single morpheme
#       - some langs have root-p:1-num:pl
#       - others have root-(1 pl inclusive)
#   - consider: how did Features handle sounds?
#       - strings per feature-value set
#       - feature-value sets per string

class Grammar:
    def __init__(self):
        # store morphosyntactic word classes, features and values
        # NOTE flattened properties just relate sounds to grammar
        # - previously mapped {word classes: {features: [values]}}
        # - now just a property has many exponents, an exponent has many properties
        # - borrow patterns used for features <> ipa
        # - each property name must be unique OR you can use ids and property objects
        # map affixes to or from grammemes

        # TODO point to properties per exponent, maybe also exponents under properties
        self.exponents = {}     # map of details about each exponent
        self.properties = {}    # map of details about each property

    # TODO store ids here or in add_exponent
    def add_property(self, property, abbreviation=None, description=None):
        """Add one word class, category or grammeme to the grammar"""
        if not property or type(property) is not str:
            print("Grammar add_property failed - expected property to be non-empty string")
            return
        # store property using name as lookup key
        property_id = "grammatical-property-{0}".format(uuid.uuid4)
        self.properties[property_id] = {
            'id': property_id,
            'name': property,
            'abbreviation': abbreviation if type(abbreviation) is str else None,
            'description': description if type(description) is str else None
        }
        return property_id

    def add_exponent(self, pre="", post="", bound=True):
        """Add one grammatical exponent to the grammar"""
        if not ((pre or post) and (type(pre) is str and type(post) is str)):
            print("Grammar add_exponent failed - expected pre or post exponent string")
            return
        # store exponent details
        exponent_id = "grammatical-exponent-{0}".format(uuid.uuid4)
        self.exponents[exponent_id] = {
            'id': exponent_id,
            'pre': pre,
            'post': post,
            'bound': bound,
            # TODO find and add property ids here too
            'properties': set()
        }
        return exponent_id

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
            if abbreviation = property_details['abbreviation']:
                properties.append(property_id)
        return properties

    def find_property_ids(self, name=None, abbreviation=None, description=None, first_only=False):
        """Return every property (or optionally the first only) with the matching details"""
        if not name or abbreviation or details:
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
                found_property_ids.append(property_id)
            if first_only:
                return found_property_ids
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
                found_exponent_ids.append(exponent_id)
            if first_only:
                return found_exponent_ids
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

    def build_word(self, root, properties):
        """Build up relevant morphology using the given grammatical properties"""
        # TODO determine relevant sets of properties, associate with exponents
        # - break into exponent property sets
        # - each property could appear in multiple exponent property sets
        # - store the found exponents that have those properties
        # - call attach_exponent to add each found exponent to the word

        # TODO when searching exponent properties check if they exist in self.properties
        # - if not, delete them since they've been removed via remove_property
        # - alternatively store blacklist or scrublist populated through remove_property

    def attach_exponent(self, stem, exponent_id=""):
        """Attach one grammatical exponent to a string of phones"""
        if not (stem and exponent_id) or not self.is_exponent(exponent_id):
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

    # TODO exponents are not theoretical unlike properties; must tolerate same phones
    # - only store in exponents_per_property and reduce over it
    def add(self, pre="", post="", bound=True, properties=[], overwrite=False):
        """Add a grammatical exponent and its associated properties (word class, categories, grammemes) to the grammar"""
        exponent_id = self.add_exponent(pre=pre, post=post, bound=bound)
        if not exponent_id:
            print("Grammar add failed - exponent already exists or is invalid")
            return

        for property in properties:
            if not self.add_property(property, overwrite=overwrite) and not self.is_property(property):
                print("Grammar add failed - one or more invalid properties")
                return

        for property in properties:
            if property not in self.exponents_per_property:
                self.exponents_per_property[property] = set()
            self.exponents_per_property[property].add(exponent_id)

        return exponent_id

    # TODO rely only on exponents_per_property
    # - for: exponents could be unique enough to have different property sets
    # - for: avoids duplicating data and means clean functional access (reduce and filter)
    # - against: stored extra details about a property and an exponent are useful
    # - against: since exponents are not unique (unlike theoretically ipa) the back-forth mapping relies on exponent_ids and exponent details data
    #
    # Alternatively: store relations under self.properties or self.exponents
    # - the attr adds ids set under key to existing dicts rather than entirely new dicts
    # - could do one and use lookups and calc or do both and have quick access but more crudwork
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
