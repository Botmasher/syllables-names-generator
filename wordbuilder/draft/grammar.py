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
        # NOTE do we need categories at all or just grammemes?
        self.grammemes = {} # dict of category: {grammeme, ...} set pairs

        self.word_classes = []
        # store morphosyntactic word classes, features and values
        self.properties = {
            # 'word class': {
            #   'feature': [
            #       'value',
            #       ...
            #   ]
            # }
        }

        # map affixes to or from grammemes
        self.exponents = {}                 # map of details about each exponent
        self.properties_per_exponent = {}   # exponent: [{grammeme,...}, ...] list pairs
        self.exponents_per_property = {}    # grammeme: [exponent, ...] list pairs

    def add_word_class(self, word_class):
        """Add a new word class to the morphosyntax"""
        if word_class not in self.properties:
            self.properties[word_class] = {}
        else:
            print("Grammar add_word_class skipped existing class {0}".format(word_class))
        return self.properties[word_class]

    def add_property(self, word_class="*", category="", grammeme="", abbreviation="", description=""):
        """Add one grammatical feature category and value to the grammar"""
        if not (type(category) is str and type(grammar) is str and type(word_class) is str):
            print("Grammar add_property failed - expected string arguments")
            return
        self.add_word_class(word_class)
        # TODO consider flattening so that all levels are just listable features for the grammar builder
        if category not in self.grammemes:
            self.grammemes[word_class][category][grammeme] = {
                'value': grammeme,
                'abbreviation': abbreviation,
                'description': description
            }
        self.grammemes[category].add(grammeme)
        return self.grammemes[category]

    def is_property(self, word_class="", category="", grammeme=""):
        """Check if the word class, grammatical category or grammatical value are part of the grammar"""
        # flags for searching
        found_word_class = False if word_class else True
        found_category = False if category else True
        found_grammeme = False if grammeme else True

        # expect one category and one grammeme
        if type(category) is not str or type(grammeme) is not str:
            print("Grammar is_property failed - invalid category or grammeme")
            return

        # give flexibility for searching through one, many or all word classses
        word_classes = []
        if type(word_class) in (list, tuple, set):
            # multiple passed-in word classes
            word_classes = list(word_classes)
        elif not word_class or word_class = "*":
            # all word classes
            word_classes = self.properties.keys()
        elif type(word_class) is str:
            # one passed-in word class
            word_classes = [word_class]
        else:
            print("Grammar is_property failed - unrecognized word class {0}".format(word_class))
            return

        # TODO simplify to search for one so this method stays predictable to caller
        for grammar_word_class in word_classes:
            if grammar_word_class not in self.properties:
                return False
            else:
                found_word_class = True
            for grammar_category in self.properties[grammar_word_class]:
                if category == grammar_category:
                    found_category = True
                # TODO update to search for stored grammeme dicts
                if grammar_grammeme in self.properties[grammar_word_class][grammar_category]:
                    found_grammeme = True
                    return True

        # for category in self.grammemes:
        #     if grammeme in self.grammemes[category]:
        #         return True
        return False

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
