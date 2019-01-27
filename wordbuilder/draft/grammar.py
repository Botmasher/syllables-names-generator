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

        # map affixes to or from grammemes
        self.affixes = {}               # map of details about each affix
        self.grammemes_per_affix = {}   # affix: [{grammeme,...}, ...] list pairs
        self.affixes_per_grammeme = {}  # grammeme: [affix, ...] list pairs
        # TODO same but for particles (or just store bound bool for affixes)
        self.particles = {}

    def add_grammeme(self, category, grammeme):
        """Add one grammatical feature category and value to the grammar"""
        if category not in self.grammemes:
            self.grammemes[category] = set()
        self.grammemes[category].add(grammeme)
        return self.grammemes[category]

    def is_grammeme(self, grammeme):
        """Check if the grammatical value name is part of the grammar"""
        for category in self.grammemes:
            if grammeme in self.grammemes[category]:
                return True
        return False

    # TODO what about prefix and suffix attributes - just read from hyphen position?
    #   - instead map affixes with affix_ids (just store phon-graph feats)
    #   - then use affix_ids in affixes_per_grammeme and grammemes_per_affix
    #   - store optional definition for specific grammeme combinations?
    def add_affix(self, prefix="", suffix="", grammemes=[], is_bound=True):
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
        affix_id = uuid.uuid4()

        # add to lookup maps
        for grammeme in grammemes:
            if grammeme not in self.affixes_per_grammeme:
                self.affixes_per_grammeme[grammeme] = set()
            self.affixes_per_grammeme[grammeme].add(affix_id)
        self.grammemes_per_affix[affix_id] = set(grammemes)

        # add to details map
        self.affixes[affix_id] = {
            'prefix': prefix,
            'suffix': suffix,
            'bound': is_bound
        }
        return affix_id

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
