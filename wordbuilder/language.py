from phoneme import Phoneme
from syllable import Syllable
from environment import Environment
from rule import Rule
from ruletracker import RuleTracker
from collector import Collector
from affixes import Affixes
#from rules import Rules
from dictionary import Dictionary

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
        self.rules = Collector(accepted_types=['Rule'])    # switched to generic class instead of Rules()
        self.environments = Collector(accepted_types=['Environment'])

        # TODO instantiate below from generic Collector
        self.affixes = Affixes()
        self.syllables = {}     # set of syllables - inventory?
        self.phonemes = {}      # dict of created phonemes - inventory?

        self.dictionary = Dictionary()    # words with ipa, morphology, definition

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

    # TODO add weights for letter choice? relative chron order for rules?
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

    # use rule to turn symbol from source into target
    def change_symbol(self, source_features, target_features, ipa_symbol):
        """Turn one symbol into another with a source->target features shift"""
        symbol_features = self.features.get_features(ipa_symbol)
        print(symbol_features)
        new_symbol_features = set(target_features)
        print(target_features)
        print("\nSuccessful rule!")
        print("Currently attempting to turn {0} into a {1}".format(symbol_features, target_features))
        # merge target features into symbol features where rule changes from source->target
        for feature in symbol_features:
            if feature in source_features and feature not in target_features:
                pass
            else:
                new_symbol_features.add(feature)
        # find phonetic symbols with these features
        new_symbols = self.features.get_ipa(list(new_symbol_features))
        # TODO choose a new symbol from matching symbols if more than one
        new_symbol = new_symbols[0]
        return new_symbol

    # No longer tracking rules as they are applied - tracking "tracks" with rule pointed to
    #   - each track is a potential change with an id and some data
    #   - so you will have to see if rule applies, add to tracks, then go through tracker
    #   - add to first so that you have new ones (incl any single-rules) during tracker iterate
    #   - so divide looks like this:
    #     - 0. initialize tracker, list of full matches this iteration
    #       - tracker needs to know: rule, source ipa, environment slot pointer (current count), environment length
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

    # Use rules to change source sounds to target sounds when in a rule environment
    # - walk through the word's sounds and the language's rules
    # - see if rule and word environments match (relying on RuleTracker for help)
    # - apply rule to change source sound in word to rule target sound if they do

    # TODO boundary hashtags - start/end tags #string# to match rules applying at borders
    # TODO change to or from silence to add or delete sounds (e.g. katta > kata, katata > kataata)
    # TODO interact with lexicon storage, adding phonetic word and sound change alongside spelling and definition
    def apply_rules(self, ipa_string):
        """Change a phonetic word's sounds applying all of the language's sound change rules"""
        # store tracks for each possible rule application
        rule_tracker = RuleTracker()

        print("\nApplying rules to word {0}".format(ipa_string))
        # set of word sounds
        word_sounds = set([c for c in ipa_string])
        # features for all sounds in the word
        # TODO should features (like original inventory) store two-way mapping?
        word_features = {
            ipa: self.features.get_features(ipa)
            for ipa in word_sounds
        }
        # gather index, symbol replacement pairs to update final string
        changed_symbols = []    # list of (string index, new symbol)

        # NOTE: not used below - double check and delete
        # prepare to track any rule matches (self.tracker track_ids)
        full_matches = []   # list of track_ids that completed each pass

        # store local rules map to search for rule matches
        rules = self.rules.get()

        # look through features and find environment matches for each step of every rule
        # use with self.rule_tracker and methods, full matches and strategy commented above to handle overlaps
        for word_index in range(len(ipa_string)):
            symbol = ipa_string[word_index]
            try:
                sound_features = word_features[symbol]
            except:
                print("Did not find features for symbol {0}".format(symbol))
                continue
            print("Evaluating the current sound: {0}".format(sound_features))

            # TODO: update to check for new rule applications to track
            # - think through if self.rule_tracker should be class level?
            # - instead make it local since it's cleared out each call (avoiding leaking to other words)
            # - then store it (or better the changed symbols list) alongside word in lexicon

            # (1) Rules Loop: do any new rules start to match at this symbol? Track them.
            # check if any new rule applications can be tracked
            for rule_id in rules:
                rule = rules[rule_id]
                print("Checking to see if rule {0} starts applying here".format(rule_id))
                # start tracking for full environment match
                # - track checked while iterating through rest of ipa_string
                # - tracker only tracks as long as environment matches
                # - zeroth nonmatches screened
                rule_tracker.track(rule)
                # NOTE: your count for successful track is 0, compared to len
                # - below will recheck for 0th match.
                # - problem: what if the first is a slot match? not storing source and index here
                # - solution: maybe let it do that extra check here then more detailed there
                else:
                    continue

            # (2) Tracks Loop: do any tracked applications ("tracks") continue to match?
            # - Untrack them if they do not
            # - Continue tracking (update slot match count) if they do
            # - If found slot _ match, bingo! - store the sound plus the word_i in track["index"] attr
            # - Add track to full_matches if count reached length
            #   - untrack and get the popped track entry
            #   - make sure you have a source sound and an index in the track entry
            #   - store the popped track in full_matches

            # (3) Full Tracks Loop: go through tracks
            # - go through each fully successful match
            # - figure out which target sound to turn the source into
            # - store the index and target sound
            # - futureproof support later adding weight / rel chron order

            # TODO: update tracks to continue checking or discard ongoing rule applications
            # NOTE error dict changes size during iteration (due to untrack pops)!

            # store completed rule tracks and avoid mutating dict mid iteration
            tracks_to_pop = []
            for track_id in rule_tracker.get():
                # a track is an ongoing attempt to match a single rule
                # each track is expected to match shape of value added in _track_rule
                track = rule_tracker[track_id]

                # the rule being matched by this track
                # one rule may be associated with multiple (even overlapping) tracks within a sound symbols string
                rule = track['rule']

                # current location in environment symbol is tested against
                environment_slot_features = rule.get_environment().get_structure()[track['count']]

                # log this attempt to fit symbol into rule environment
                print("Applying rule {0}: {1}".format(rule, rule.get_pretty()))
                print("Looking for environment matching {0}".format(environment_slot_features))

                # flag to check if rule track fails to match sound to slot
                did_keep_tracking = False

                # environment source match - store sound to change and keep tracking
                if rule_tracker.check_source_slot_match(sound_features, environment_slot_features, rule.get_source()):
                    rule_tracker.set_source_match(track_id, source=symbol, index=word_index)
                    did_keep_tracking = True
                # surrounding environment match - keep tracking
                elif rule_tracker.check_environment_slot_match(sound_features, environment_slot_features):
                    self.count_features_match(track_id)
                    did_keep_tracking = True
                # no match for this track - prepare to untrack
                else:
                    print("Found no features match - resetting the rule")
                    tracks_to_pop.append(track_id)
                    #did_keep_tracking = False  # default

                # matched to the end of the rule environment - add to found changes
                if did_keep_tracking and track['count'] >= track['length']:
                    # new symbol, index pairs for updating the final sound string (changed word)
                    # TODO incorporate weighting or relative chronology as a third value
                    changed_symbols.append((
                        rule_tracker[track_id]['index'],
                        self.change_symbol(
                            rule.get_source(),
                            rule.get_target(),
                            rule_tracker[track_id]['source']
                        )
                    ))
                    # drop this track from the tracker
                    # TODO consider keeping tracker, storing ['target'] and ['index'] and using them below
                    tracks_to_pop.append(track_id)

            # ditch any successful or failed completed track
            [rule_tracker.untrack(track_id) for track_id in tracks_to_pop]

        # build a new ipa representation of the word after rule applied
        new_ipa_string = list(ipa_string)
        for entry in changed_symbols:
            # transform word by updating index to changed symbol
            new_ipa_string[entry[0]] = entry[1]
        print("".join(new_ipa_string))
        return (ipa_string, "".join(new_ipa_string))

    # TODO update below methods to conform to Dictionary object
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
