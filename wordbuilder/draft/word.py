## test classes for word and word grammar

# TODO separating analytic pieces
#   - store as separate words or piece of this word?
#   - treat spaces as part of morphology?
#   - OR just solve for building out a bit of syntax (then can store affixes, particles separately as well)

class Word:
    def __init__(self, spelling="", ipa="", morphology=[], defintion=""):
        self.ipa = ""
        self.morphology = []
        self.spelling = ""
        self.definition = ""
        self.rules = []

    def get(self):
        return {
            'ipa': self.ipa,
            'morphology': self.morphology,
            'spelling': self.spelling,
            'definition': self.definition,
            'rules': self.rules
        }

    def apply_rules(self, rules, inventory):
        for rule in rules:
            for symbol in self.ipa:
                # NOTE consider window for environment lookups
                # lookup and see if rule apples

    def add_rule(self, rule_id):
        self.rules.append(rule_id)

    def ipa(self):
        return self.ipa

    def define(self):
        return self.definition

    def grammar(self):
        return self.morphology

    # /!\ updating spelling means changing place in outer dict!
    def update(self, ipa="", spelling="", morphology=[]):
        # TODO better checks
        if ipa:
            self.ipa = ipa
        if spelling:
            self.spelling = spelling
        if morphology:
            self.morphology = morphology
        return self.get()

# store and check grammatical features
class Morphology:
    def __init__(self):
        self.grammar = {}   # dict for {word_classes: {categories : {values}}}

    def get(self):
        return self.grammar

    def add(self, pos, category="", value=""):
        # accept single strings like "noun class animate"
        if not pos:
            print("Morphology add failed - unrecognized word class {0}".format(pos))
        if pos and not (category or value):
            grammatical_feature = self.parse(pos)
            if grammatical_feature:
                pos, category, value = grammatical_feature
            else:
                print("Morphology grammar add failed - unrecognized word class, category or value")
                return
        if pos not in self.grammar:
            self.grammar[pos] = {}
        if category not in self.grammar[pos]:
            self.grammar[pos][category] = set()
        self.grammar[pos][category].add(value)
        return self.get()

    # TODO update, remove

    def parse(self, grammar_string):
        feature = grammar_string.split(" ")
        if feature and len(grammar) == 3
            return
        return feature
