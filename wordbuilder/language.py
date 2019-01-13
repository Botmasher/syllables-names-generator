from syllable import Syllable
from rule import Rule
from rules import Rules
from environment import Environment
from phoneme import Phoneme
from affixes import Affixes

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
    def __init__(self, name="", display_name="", features=None, inventory=None, rules={}):
        self.name = name
        self.display_name = display_name
        self.features = features
        self.inventory = inventory
        self.rules = Rules()
        self.rule_tracker = {}  # match environment and apply rules
        self.affixes = Affixes()
        self.environments = {}  # instantiated environments to limit created syllables
        self.syllables = {}     # set of syllables - inventory?
        self.phonemes = {}      # dict of created phonemes - inventory?
        self.dictionary = {}    # words with ipa, morphology, definition

    def set_inventory(self, inventory):
        """Set the inventory object for this language"""
        self.inventory = inventory

    def set_features(self, features):
        """Set the features object for this language"""
        self.features = features

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
    # TODO: access Rules update, remove methods
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
        rule_id = self.rules.add(rule)
        return rule_id

    def get_rule(self, rule_id, pretty_print=False):
        """Look up one rule in the language's rules dictionary"""
        rule = self.rules.get(rule_id=rule_id)
        pretty_print and rule.get_pretty()
        not rule and print("Language get_rule failed - unknown rule {0}".format(rule_id))
        return rule

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

    ## walk through a word's sounds, see if rule environments match, apply if they do
    # TODO rule layering - currently it's all-at-once!

    ## APPLY_RULE HELPERS
    # are all features found for this symbol (subset of its features)?
    def _is_features_submatch(self, features, symbol_features):
        for feature in features:
            if feature not in symbol_features:
                return False
        return True

    # TODO entirely separate out handling rule tracker
    #   - associate more closely with rule than generally with language
    # reset a single rule tracker entry

    def _untrack_rule(self, track_id):
        if track_id not in self.rule_tracker:
            print("Language failed to untrack rule - invalid tracker track_id {0}".format(track_id))
            return
        self.rule_tracker.pop(track_id)
        return track_id

    def _track_rule(self, rule):
        if rule not in rules:
            print("".format(rule))
            return
        self.tracker[track_id] = {
            # the current slot being evaluated for sound matches
            'count': 0,
            # the total number of slots to match before applying rule
            'length': len(rule.get_environment().get_structure()),
             # identified sounds to change
            'source': '',
            # index of identified sound to change
            'index': None,
            # rule object defining environment and change
            'rule': rule
        }
        return track_id

    # TODO update this checking on changes to features (added ipa:features map)
    # use rule to turn symbol from source into target
    def change_symbol(self, source_features, target_features, ipa_symbol):
        symbol_features = self.features.get_features(ipa_symbol)
        new_symbol_features = set(target_features)
        print(new_symbol_features)
        for feature in symbol_features:
            if feature in source_features and feature not in target_features:
                pass
            else:
                new_symbol_features.add(feature)
        print(new_symbol_features)
        new_symbols = self.features.get_ipa(list(new_symbol_features))
        print(new_symbols)
        # TODO choose a new symbol from matching symbols if more than one
        new_symbol = new_symbols[0]
        return new_symbol

    # TODO: change from tracking rules as they are applied to tracking "tracks" with rule pointed to
    #   - each track is a potential change with an id and some data
    #   - so you will have to see if rule applies, add to tracks, then go through tracker
    #   - add to first so that you have new ones (incl any single-rules) during tracker iterate
    #   - so divide looks like this:
    #     - 0. initialize tracker, list of full matches this iteration
    #       - tracker needs to know: , source ipa
    #       - changer needs: source ipa, rule source, rule target
    #       - full matches list needs: current this pass through new-rules and tracks
    #     - 1. look at letter, rules, tracks
    #       - Does it match any new rules that apply to these features? Start track
    #       - Does it match current environment slots in tracker? Update track
    #       - Does it fail to match environment slots in tracker? Remove track
    #       - Does it fully match the entire environment? Add to full match list of track ids
    #     - 2. look through tracks
    #       - if no change, remove track
    #       - if full match determine target sound
    #       - store target sounds, indexes, (? weights)
    #       - clear list of full matches (tracks ids) to prepare it for next pass
    #       - if last letter and not in track ids, get rid of the tracker entry (caught mid-applying)
    #     - 3. propose and implement changes once all changes stored
    #       - note that you also have a full tracker object of all applied tracks
    #       - consider storing tracker and then applying in a separate method
    #   - eventually weighting rules add another value to sounds to change

    def apply_rules(self, ipa_string):
        print("\nApplying rules to word {0}".format(ipa_string))
        # set of word sounds
        word_sounds = set([c for c in ipa_string])
        # features for all sounds in the word
        # TODO should features (like original inventory) store two-way mapping?
        word_features = {
            ipa: self.features.get_features(ipa)
            for ipa in word_sounds
        }
        # gather (index, symbol replacement) pairs to update final string
        change_tracker = []

        # track any rule matches
        # TODO: use self.rule_tracker and methods, full matches and strategy commented above to handle overlaps
        #rules_tracker = {}
        full_matches = []

        # look up features
        for word_i in range(len(ipa_string)):
            symbol = ipa_string[word_i]
            try:
                sound_features = word_features[symbol]
            except:
                print("Did not find features for symbol {0}".format(symbol))
                continue
            print("Evaluating the current sound: {0}".format(sound_features))
            # match word features to features in rule environment lists

            # TODO: update to check for new rule applications to track
            for rule_id in self.rules:
                # do same rule checking as done below for rules for each track
                # ? pull out slot-checking into own method
                pass

            # TODO: update tracks to continue checking or discard ongoing rule applications
            for track_id in rules_tracker:

                rule_data = rules_tracker[rule_id]  # this and following to track_id
                print("Applying rule {0}".format(rule_data['rule']))
                print("{0}".format(rule_data['rule'].get_pretty()))
                environment_slot = rule_data['rule'].get_environment().get_structure()[rule_data['count']]
                print("Looking for environment matching: {0}".format(environment_slot))
                # environment slot matches - store sound
                if environment_slot in ["_", ["_"]]:
                    # check if the sound is one changed by rule source -> target
                    if self._is_features_submatch(rule_data['rule'].get_source(), word_features[symbol]):
                        print("Found source match (_)! Storing {0}".format(symbol))
                        rule_data['source'] = symbol
                        rule_data['index'] = word_i
                        rule_data['count'] += 1
                    else:
                        print("Did not find a source match on {0}, even though environment up to this point matched.".format(symbol))
                        self.reset_rule_data(rule_data)
                # surrounding environment matches - keep searching
                elif self._is_features_submatch(environment_slot, word_features[symbol]):
                    print("Found features match in symbol: {0}".format(symbol))
                    rule_data['count'] += 1
                # no environment match - reset this particular rule
                # TODO: work with ANY running find in parallel - see tracking TODO above
                else:
                    print("Found no features match - resetting the rule")
                    rules_tracker[rule_id] = self._reset_rule_data(rule_data)
                # if count is up to the total change the sound
                print(rules_tracker)
                if rule_data['count'] >= rule_data['length']:
                    # store the new target and the source index to change
                    if rule_data['source']:
                        new_symbol = self.change_symbol(rule_data['rule'].get_source(), rule_data['rule'].get_target(), rule_data['source'])
                        new_index = rule_data['index']
                        rule_data['targets'].append(new_symbol)
                        rule_data['indexes'].append(new_index)
                        change_tracker.append((new_index, new_symbol))
                    rules_tracker[rule_id] = self._reset_rule_data(rule_data)
        # TODO use constructed rule data ['targets'] and ['indexes'] to update word
        new_ipa_string = list(ipa_string)
        for entry in change_tracker:
            new_ipa_string[entry[0]] = entry[1]
        print("".join(new_ipa_string))
        return (ipa_string, "".join(new_ipa_string))

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
        print("Language word lookup failed - unknown spelling {0}".format(spelling))
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
