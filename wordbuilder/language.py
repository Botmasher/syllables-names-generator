from syllable import Syllable
from rule import Rule
from environment import Environment
from phoneme import Phoneme
from affixes import Affixes
import uuid

# TODO
# - handle feature checks in language instead of shared Features dependency
#   - check before passing non C xor V to syll
#   - check before adding consonant or vowel to inventory
#   - check before adding features to phone
# - language dictionary storing created words and definitions
# - set up default letters and symbols
# - have language check inventory, environment, rules
#   - e.g. avoid ['smiles', '_', 'sauce'] allow ['vowel', '_', 'vowel']
#   - '0', '#' when applying rules
# - see tasks within other class files

class Language:
    def __init__(self, name="", display_name="", features=None, inventory=None, rules=None):
        self.name = name
        self.display_name = display_name
        self.features = features
        self.inventory = inventory
        self.rules = rules
        self.affixes = Affixes()
        self.environments = {}  # instantiated environments
        self.syllables = {}     # set of syllables - inventory?
        self.phonemes = {}      # dict of created phonemes - inventory?
        self.dictionary = {}    # words with ipa, morphology, definition

    def set_inventory(self, inventory):
        """Set the inventory object for this language"""
        self.inventory = inventory

    def set_features(self, features):
        """Set the features object for this language"""
        self.features = features

    # TODO compare with Rules.add checks already in place
    def add_rule(self, source, target, environment):
        if not (self.features.has_ipa(source) and self.features.has_ipa(target)):
            print("Language add_rule failed - invalid source or target symbols")
            return
        e = Environment(structure=environment)
        if not e.get():
            print("Language add_rule failed - invalid environment given")
            return
        self.rules.add(source, target, e)

    def print_syllables(self):
        syllable_text = ""
        count = 0
        for syllable in self.inventory.get_syllables():
            count += 1
            syllable_text += "Syllable {0}: ".format(count)
            for syllable_item in syllable.get():
                for feature in syllable_item:
                    syllable_text += "{0}, ".format(feature)
            syllable_text = syllable_text[:-2]
            syllable_text += "\n"
        print(syllable_text)
        return syllable_text

    def add_syllable(self, syllable_structure, parse_cv=True):
        # build valid symbol or features list
        syllable_characters = ['_', '#', ' ', 'C', 'V']
        if parse_cv and type(syllable_structure) is str:
            cv_structure = []
            for cv_char in syllable_structure:
                if cv_char in syllable_characters:
                    cv_structure.append(cv_char)
                else:
                    print("Language add_syllable failed - invalid character {0} found when parsing syllable string".format(cv_char))
                    return
            syllable_structure = cv_structure
        new_syllable_structure = []
        for syllable_item in syllable_structure:
            if type(syllable_item) is str:
                if not (syllable_item in syllable_characters or self.features.has_feature(syllable_item)):
                    print("Language add_syllable failed - invalid syllable item {0}".format(syllable_item))
                    return
                elif syllable_item == 'C':
                    new_syllable_structure.append(["consonant"])
                elif syllable_item == 'V':
                    new_syllable_structure.append(["vowel"])
                else:
                    new_syllable_structure.append([syllable_item])
            elif type(syllable_item) is list:
                for feature in syllable_item:
                    if not self.features.has_feature(syllable_item):
                        print("Language add_syllable failed - invalid syllable feature {0}".format(feature))
                        return
                new_syllable_structure.append(syllable_item)
        syllable = Syllable(new_syllable_structure)
        self.inventory.add_syllable(syllable)
        return

    def add_affix(self, category, grammar, affix):
        """Add a grammatical category and value affix in phonetic transcription"""
        for symbol in affix:
            if symbol != '-' or not self.inventory.has_ipa(symbol):
                print("Language add_affix failed - invalid affix {0}".format(affix))
                return
        self.affixes.add(category, grammar, affix)
        return self.affixes.get(affix)

    # Rules
    # TODO update, remove
    def add_rule(self, source, target, environment_structure):
        """Add one rule to the language's rules dictionary"""
        environment = Environment(structure=environment_structure)
        if not environment.get():
            print("Language add_rule failed - invalid or empty environment {0}".format(environment))
            return
        rule = Rule(source=source, target=target, environment=environment)
        if not rule.get():
            print("Language add_rule failed - invalid rule {0}".format(rule))
            return
        rule_id = uuid.uuid4()
        self.rules[rule_id] = rule
        return rule_id

    def get_rule(self, rule_id, pretty_print=False):
        """Look up one rule in the language's rules dictionary"""
        if rule_id in self.rules:
            rule = self.rules[rule_id]
            pretty_print and rule.get_pretty()
            return rule
        print("Language get_rule failed - unknown rule {0}".format(rule_id))
        return

    # TODO decide to handle sound lookups and feature associations here vs inventory
    #   - currently relying on this class symbol:phoneme mapping but building sylls c chars from inv
    #   - features knows all possibilities but inventory builds out current set
    def is_ipa(self, symbol):
        if not self.features.has_ipa(symbol):
            print("invalid phonetic symbol {0}".format(symbol))
            return False
        return True
    #
    def get_sound_features(self, ipa):
        if not self.is_ipa(ipa) or ipa not in self.phonemes:
            print("Language phonetic symbol not found: {0}".format(ipa))
            return
        phoneme = self.phonemes[ipa].get()
        return self.features.get_features(phoneme['symbol'])
    #
    def get_sound_letters(self, ipa):
        if not self.is_ipa(ipa) or ipa not in self.phonemes:
            print("Language phonetic symbol not found: {0}".format(ipa))
            return
        phoneme = self.phonemes[ipa].get()
        return phoneme['letters']


    # TODO add weights for letter choice? for rules?
    #   - current weight intended for distributing phon commonness/freq of occ
    def add_sound(self, ipa, letters=[], weight=0):
        """Add one phonetic symbol, associated letters and optional weight to the language's inventory"""
        if not self.features.has_ipa(ipa) or not all(isinstance(l, str) for l in letters):
            print("Language add_sound failed - invalid phonetic symbol or letters")
            return {}
        sound = Phoneme(ipa, letters=letters, weight=weight)
        self.phonemes[ipa] = sound
        # TODO decide if adding sounds to language (above) or managing through inventory (below)
        features = self.features.get_features(ipa)
        for letter in letters:
            self.inventory.add_letter(letter=letter, features=features)
        return {ipa: self.phonemes[ipa]}

    def add_sounds(self, ipa_letters_map):
        """Add multiple sounds to the language's inventory"""
        if type(ipa_letters_map) is not dict:
            print("Language add_sounds failed - expected dict not {0}".format(type(ipa_letters_map)))
            return
        sounds = {}
        for ipa, letters in ipa_letters_map.items():
            added_sound = self.add_sound(ipa, letters=letters)
            sounds.update(added_sound)
        return sounds

    # build a full word c affixes
    # NOTE: do entirely in phon and make sure Affix(es) class coheres
    #   - consider lang creator might use "-" as symbol
    # TODO: think again about affixation
    #   - include word class for categorizing like ['noun']['class']['animate']?
    #   - what about compounding?
    #   - what about analytic syntax like say "dnen bmahuwa" for cat-ANIM?
    def apply_affixes(self, root_ipa, grammatical_features={}, boundaries=True):
        morphology = root_ipa
        affixes = self.affixes.get()
        for grammatical_category in grammatical_features:
            grammar = grammatical_features[grammatical_category]
            try:
                affix = affixes[grammatical_category][grammar]
                if 'suffix' in affix:
                    suffix = random.sample(affix['suffix'])
                    morphology.append(suffix)
                elif 'prefix' in affix:
                    prefix = random.sample(affix['prefix'])
                    morphology.insert(prefix)
            except:
                continue
        built_word = ""
        if not boundaries:
            # for feeding to sound change rules
            built_word = "".join(morphology)
        else:
            # for displaying hyphenated morphology
            built_word = "-".join(morphology)
        return {
            'ipa': built_word,
            'shape': morphology
        }

    def store_word(self, spelling, phonology, morphology, definition=""):
        entry = {
            'spelling': spelling,
            'ipa': phonology,
            'morphology': morphology,
            'definition': definition
        }
        # array for homonyms
        if spelling in self.dictionary:
            self.dictionary[spelling].append(entry)
        else:
            self.dictionary[spelling] = [entry]
        return self.dictionary[spelling]

    def lookup(self, spelling):
        if spelling in self.dictionary:
            return self.dictionary[spelling]
        print("Language word lookup faield - unknown spelling {0}".format(spelling))
        return

    def define(self, spelling):
        words = self.lookup(spelling)
        if not words:
            return
        # iterate over homonyms
        definitions = [word['definition'] for word in words]
        return definitions

    # TODO add affixes, apply rules and store word letters and symbols
    def build_word(self, length=1):
        """Form a word following the defined inventory and syllable structure"""
        if not self.inventory and self.inventory.get_syllables():
            print("Language build_word failed - unrecognized inventory or inventory  syllables")
            return
        word = ""
        for i in range(length):
            syllable = random.choice(self.inventory.get_syllables())
            syllable_structure = syllable.get()
            for syllable_letter_feature in syllable_structure:
                letters = self.inventory.get_letter(syllable_letter_feature)
                # TODO choose letters by weighted freq/uncommonness
                if letters:
                    word += random.choice(letters)
        return word