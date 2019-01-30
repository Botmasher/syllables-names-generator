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
        self.exponents = {}     # map of details about each exponent
        self.properties = {}    # map of details about each property
        #self.properties_per_exponent = {}   # exponent_id: [property_id, ...] pairs
        self.exponents_per_property = {}    # property_id: [exponent_id, ...] pairs

    # TODO rely only on exponents_per_property
    def add_property(self, property, abbreviation=None, description=None, overwrite=False):
        """Add one word class, category or grammeme to the grammar"""
        if not property or type(property) is not str:
            print("Grammar add_property failed - expected property to be non-empty string")
            return
        property_id = property  # generate ids if allowing same name properties
        # store property using name as lookup key
        if overwrite or property not in self.properties:
            self.properties[property] = {
                'name': property,
                'abbreviation': abbreviation if type(abbreviation) is str else None,
                'description': description if type(description) is str else None
            }
        else:
            print("Grammar add_property failed - cannot overwrite existing property")
            return
        return property_id

    def remove_property(self, property):
        """Delete the record for one property from the grammar"""
        try:
            removed_property = self.properties[property]
            self.properties.pop(property)
            return removed_property
        except:
            print("Grammar remove_property failed - unknown property {0}".format(property))
            return
        # TODO please REMOVE property from exponents_per_property when augmenting words

    def unabbreviate_property(self, abbreviation):
        """Return full property names for properties that use the abbreviation"""
        # NOTE this works when property ids and names are the same and unique
        properties = []
        for property, property_details in self.properties.items():
            if abbreviation = property_details['abbreviation']:
                properties.append(property)
        return properties

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

    # TODO update
    def add_exponent(self, pre="", post="", bound=True, overwrite=False):
        """Add one grammatical exponent to the grammar"""
        if not ((pre or post) and (type(pre) is str and type(post) is str)):
            print("Grammar add_exponent failed - expected pre or post exponent string")
            return
        exponent_id = uuid.uuid4
        if overwrite or exponent not in self.exponents:
            self.exponents[exponent_id] = {
                'id': exponent_id,
                'pre': pre,
                'post': post,
                'bound': bound
            }
        else:
            print("Grammar add_property failed - cannot overwrite existing property")
            return
        return exponent_id

    def build_word(self, root, properties, layer_exponents=False):
        """Build up relevant morphology using the given grammatical properties"""
        # TODO determine relevant sets of properties, associate with exponents
        # - break into exponent property sets
        # - each property could appear in multiple exponent property sets
        # - layering exponents allows property subsets to overlap where exponents exist:
        #   - if True, a relevant exponent's property set is proper subset of another, do not use that exponent
        #   - if False, a relevant property subset can determine an exponent
        #   - example: True may attach a verb exponent, a verb transitive one and a verb second person singular one
        #   - NOTE perhaps throw out this option for practicality
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
    def is_exponent(self, exponent):
        """Check if a string of sounds is an exponent in this grammar"""
        if not (exponent and type(exponent) is str):
            print("Grammar is_exponent failed - expected valid exponent string")
            return False
        return exponent in self.exponents

    def is_property(self, property):
        """Check if a word class, category or grammeme is part of the grammar"""
        if not (property and type(property) is str):
            print("Grammar is_property failed - expected valid property string")
            return False
        return property in self.properties
