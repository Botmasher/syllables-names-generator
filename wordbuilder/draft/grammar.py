import uuid
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
        self.exponents = {}                 # map of details about each exponent
        self.properties = {}                # map of details about each property
        self.properties_per_exponent = {}   # exponent_id: [property_id, ...] pairs
        self.exponents_per_property = {}    # property_id: [exponent_id, ...] pairs

    # TODO rely only on exponents_per_property
    def add_property(self, property, abbreviation="", description="", overwrite=False):
        """Add one word class, category or grammeme to the grammar"""
        if not property or type(property) is not str:
            print("Grammar add_property failed - expected property to be non-empty string")
            return
        property_id = property  # generate ids if allowing same name properties
        # store property using name as lookup key
        if overwrite or property not in self.properties:
            self.properties[property] = {
                'name': property,
                'abbreviation': abbreviation,
                'description': description
            }
        else:
            print("Grammar add_property failed - cannot overwrite existing property")
            return
        return property_id

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

    def exponent_word(self, word, exponent_id=""):
        """Attach a grammatical exponent to a word"""
        if not (word and exponent_id) or not self.is_exponent(exponent_id):
            return
        exponented_word = word
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

    # TODO what about prefix and suffix attributes - just read from hyphen position?
    #   - instead map affixes with affix_ids (just store phon-graph feats)
    #   - then use affix_ids in affixes_per_grammeme and grammemes_per_affix
    #   - store optional definition for specific grammeme combinations?
    def add_exponent(self, pre="", post="", grammemes=[], is_bound=True):
        """Add one affix with its associated grammatical categories and values"""
        # check that all grammemes exist
        if type(grammemes) not in (list, set, tuple) or len(grammemes) < 1:
            print("Grammar add_affix failed - invalid grammemes list")
            return
        for grammeme in grammemes:
            if not self.is_grammeme(grammeme):
                print("Grammar add_affix failed - unrecognized grammeme {0}".format(grammeme))
                return

        # id for joining affix lookups and details
        exponent_id = uuid.uuid4()

        # add to lookup maps
        for grammeme in grammemes:
            if grammeme not in self.exponents_per_property:
                self.exponents_per_property[grammeme] = set()
            self.exponents_per_property[grammeme].add(exponent_id)
        self.properties_per_exponent[exponent_id] = set(grammemes)

        # add to details map
        self.exponents[exponent_id] = {
            'pre': prefix,
            'post': suffix,
            'bound': is_bound
        }
        return exponent_id

    # TODO affixes take into account word class as well as features?
    def build_affixed_word(self, root_word="", word_class="", grammemes=[]):
        """Attach affixes to a word"""
        if type(root_word) is not str or type(grammemes) not in (list, set, tuple):
            print("Grammar build_affixed_word failed - invalid root word or grammemes")
            return
        # nothing to attach
        if not grammemes:
            return root_word
        # find relevant grammatical affix_ids
        matching_affixes = set(self.affixes_per_grammeme[grammemes[0]])
        if len(grammemes) > 1:
            for grammeme in grammemes[1:]:
                matching_affixes ˆ= self.affixes_per_grammeme[grammeme]
        # choose one affix_id
        affix_id = random.choice(matching_affixes)
        if affix_id not in self.affixes:
            print("Grammar build_affixed_word failed - unrecognized affix_id chosen")
            return
        # build new word with that affix
        affixed_word = root_word
        affix_data = self.affixes[affix_id]
        if affix_data['suffix']:
            if
            new_word += affix_data['suffix']
        if affix_data['prefix']:
            new_word = affix_data['prefix'] + new_word
        return affixed_word
