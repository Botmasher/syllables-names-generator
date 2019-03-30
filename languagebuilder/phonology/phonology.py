# collection management
from .phonemes import Phonemes
from ..tools.collector import Collector
from ..tools.setcollector import SetCollector
# objects collected
from .phoneme import Phoneme
from .syllable import Syllable
from .environment import Environment
from .rule import Rule
from .ruletracker import RuleTracker
# for sound, letter and syllable generation
import random

# TODO: handle actions in dedicated collections classes
#   - create classes for Environments, Syllables
#   - move .add, .update, .remove to Phonemes, Rules, Environments, Syllables
#   - inject classes here

class Phonology:
    def __init__(self, phonetics):
        # phonetic mapping between ipa and features
        self.phonetics = phonetics
        # collections for this inventory
        self.phonemes = Phonemes()
        self.environments = Collector(accepted_types=['Environment'])
        self.syllables = SetCollector(accepted_types=['Syllable'])
        self.rules = Collector(accepted_types=['Rule'])

    # inventory now managed through Phonemes (letters <> ipa) and Features (features <> ipa) instead of previous Inventory class
    def inventory(self):
        """Read all phonetic symbols stored for this language"""
        return self.phonemes.symbols()

    def print_syllables(self):
        """Print out all syllables in a human-readable formatted string"""
        syllable_text = ""
        count = 0
        for syllable in self.syllables.get():
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
        """Add one syllable to the syllables collection for this language"""
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
                if not (syllable_item in syllable_characters or self.phonetics.has_feature(syllable_item)):
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
                    if not self.phonetics.has_feature(syllable_item):
                        print("Language add_syllable failed - invalid syllable feature {0}".format(feature))
                        return
                new_syllable_structure.append(syllable_item)
        syllable = Syllable(new_syllable_structure)
        self.syllables.add(syllable)
        return syllable
    
    # Rules
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
        rule = self.rules.get(rule_id)
        pretty_print and rule.get_pretty()
        not rule and print("Language get_rule failed - unknown rule {0}".format(rule_id))
        return rule

    # TODO decide to handle sound lookups and feature associations here vs inventory
    #   - features knows all possibilities but inventory builds out current set
    def is_ipa(self, symbol):
        if not self.phonetics.has_ipa(symbol):
            print("invalid phonetic symbol {0}".format(symbol))
            return False
        return True
    #
    def get_sound_features(self, ipa):
        if not self.is_ipa(ipa) or not self.phonemes.has(ipa):
            print("Language get_sound_features failed - unknown symbol {0}".format(ipa))
            return
        return self.phonetics.get_features(ipa)
    #
    def get_sound_letters(self, ipa):
        if not self.is_ipa(ipa) or not self.phonemes.has(ipa):
            print("Language get_sound_letters failed - unknown symbol {0}".format(ipa))
            return
        letters = self.phonemes.get_letters(ipa)
        return letters

    # TODO: add weights for letter choice
    #   - current weight intended for distributing phon freq
    def add_sound(self, ipa, letters=[], weight=0):
        """Add one phonetic symbol, associated letters and optional weight to the language's inventory"""
        if not self.phonetics.has_ipa(ipa) or not all(isinstance(l, str) for l in letters):
            print("Language add_sound failed - invalid phonetic symbol or letters")
            return {}
        phoneme = Phoneme(ipa, letters=letters, weight=weight)
        self.phonemes.add(phoneme)
        return {ipa: self.phonemes.get(key=ipa)}

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

    # use rule to turn symbol from source into target
    def change_symbol(self, source_features, target_features, ipa_symbol):
        """Turn one symbol into another with a source->target features shift"""
        symbol_features = self.phonetics.get_features(ipa_symbol)
        print(symbol_features)
        new_symbol_features = set(target_features)
        print(target_features)
        print("Successful rule!")
        print("Currently attempting to turn {0} into a {1}".format(symbol_features, target_features))
        # merge target features into symbol features where rule changes from source->target
        for feature in symbol_features:
            if feature in source_features and feature not in target_features:
                pass
            else:
                new_symbol_features.add(feature)
        # find phonetic symbols with these features
        # choose from all possible symbols not just current inventory
        new_symbols = self.phonetics.get_ipa(list(new_symbol_features))

        # TODO choose a new symbol from matching symbols if more than one
        new_symbol = new_symbols[0]

        # TODO also suggest changed spellings
        # - (default to same if none available)

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

    # TODO: boundary hashtags
    #   - start/end tags #string# to match rules applying at borders
    #   - change to or from silence to add or delete sounds (e.g. katta > kata, katata > kataata)
    
    # TODO: interact with lexicon storage, adding phonetic word and sound change alongside spelling and definition
    #   - store tracks or store the changed symbols list alongside word in lexicon

    def apply_rules(self, ipa_string):
        """Change a phonetic word's sounds applying all of the language's sound change rules"""
        # store tracks for each possible rule application
        rule_tracker = RuleTracker()

        print("\nApplying rules to word {0}".format(ipa_string))
        # set of word sounds
        word_sounds = set([c for c in ipa_string])
        # features for all sounds in the word
        word_features = {
            ipa: self.phonetics.get_features(ipa)
            for ipa in word_sounds
        }

        # collect each track of rules that applies within the word ipa
        successful_tracks = []

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

            # (1) Rules Loop: do any new rules start to match at this symbol? Track them.
            # check if any new rule applications can be tracked
            for rule_id in rules:
                rule = rules[rule_id]
                print(f"Checking to see if rule {rule_id} starts applying here")
                # start tracking for full environment match
                # - track checked while iterating through rest of ipa_string
                # - tracker only tracks as long as environment matches
                # - zeroth nonmatches screened
                rule_tracker.track(rule, sound_features)
                # NOTE: your count for successful track is 0, compared to len
                # - below will recheck for 0th match.
                # - problem: what if the first is a slot match? not storing source and index here
                # - solution: maybe let it do that extra check here then more detailed there

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

            # store completed rule tracks and avoid mutating dict mid iteration
            tracks_to_pop = []
            tracks = rule_tracker.get()
            for track_id in tracks:
                # a track is an ongoing attempt to match a single rule
                # each track is expected to match shape of value added in _track_rule
                track = tracks[track_id]

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
                if rule_tracker.is_source_slot_match(sound_features, environment_slot_features, rule.get_source()):
                    rule_tracker.set_source_match(track_id, source=symbol, index=word_index)
                    did_keep_tracking = True
                # surrounding environment match - keep tracking
                elif rule_tracker.is_environment_slot_match(sound_features, environment_slot_features):
                    rule_tracker.count_features_match(track_id)
                    did_keep_tracking = True
                # no match for this track - prepare to untrack
                else:
                    print("Found no features match - resetting the rule")
                    tracks_to_pop.append(track_id)
                    #did_keep_tracking = False  # default

                # fetch track again for refreshed count and index data
                track = rule_tracker.get(track_id=track_id)

                # TODO: apply RuleTracker tracks in order instead of changing each here
                #   - this overwrites sounds based on individual rule determination
                #   - stack changes by feeding each one to the other
                #   - see if the next one applies if not pass same sound down

                # matched to the end of the rule environment - add to found changes
                if did_keep_tracking and track['count'] >= track['length']:
                    
                    # full ruletrack match
                    successful_tracks.append(track)
                    
                    # drop this track from the tracker
                    tracks_to_pop.append(track_id)

            # ditch any successful or failed completed track
            [rule_tracker.untrack(track_id) for track_id in tracks_to_pop]

        # build a new ipa representation of the word after rule applied
        new_ipa_string = list(ipa_string)

        # use tracker ['rule']['target'] and tracker ['index'] to layer sound changes
        #
        # TODO: incorporate weighting or relative chronology in values
        for successful_track in successful_tracks:
            print(successful_track)
            # get the sound to change
            index_to_change = successful_track['index']
            ipa_to_change = new_ipa_string[index_to_change]
            applied_rule = successful_track['rule']
            
            # NOTE: tracker ['source'] is in this loop the original sound
            # before any changes were layered
            #original_ipa = successful_track['source']
            
            # verify sound to change has not been updated to fall outside of rule
            features_to_change = self.phonetics.get_features(ipa_to_change)
            if not rule_tracker.is_features_submatch(applied_rule.get_source(), features_to_change):
                continue

            # perform the sound change
            changed_ipa = self.change_symbol(
                applied_rule.get_source(),  # rule source features that were matched
                applied_rule.get_target(),  # rule target features to transform sound
                ipa_to_change               # the matched sound to change
            )
            print("source ipa: " + ipa_to_change)
            print("updated ipa: " + changed_ipa)

            # store the changed sound
            new_ipa_string[index_to_change] = changed_ipa

        ## NOTE: old way - mutate symbols directly based on track changing that index
        # for entry in changed_symbols:
        #     # transform word by updating index to changed symbol
        #     new_ipa_string[entry[0]] = entry[1]

        print("".join(new_ipa_string))
        return (ipa_string, "".join(new_ipa_string))

    # TODO add affixes, apply rules and store word letters and symbols
    def build_word(self, length=1, definition="", store_in_dictionary=True, apply_rules=True):
        """Form a word following the defined inventory and syllable structure"""
        # form a list of possible syllables to choose from
        syllables = list(self.syllables.get())
        if not syllables:
            print("Language build_word failed - no possible syllables found in {0}".format(syllables))
            return

        # store sound (phonemes) and spelling (graphemes) forms of words being built
        # TODO store same-length lists of letters and ipa in dictionary instead of strings
        word_spelling = []
        word_ipa = []

        # TODO choose letters by weighted freq/uncommonness
        for i in range(length):
            try:
                syllable = random.choice(syllables)
            except:
                print("Language build_word failed - no syllables found in inventory")
                return
            syllable_structure = syllable.get()
            for feature_set in syllable_structure:
                # find all inventory ipa that have these features
                symbols = self.phonetics.get_ipa(feature_set, filter_phonemes=self.inventory())
                # TODO you store Phoneme with associated letters so this should be easy
                #   - right now inventory maps features to letters
                #   - features maps them to sounds
                #   - instead stick with features <> ipa <> letters
                #   - use Features and Phoneme to accomplish (see features.py comment)
                if symbols:
                    # choose from ipa symbols that matched subset of features
                    symbol = random.choice(symbols)
                    word_ipa.append(symbol)
                    # choose letter from letters set inside phoneme object
                    letters = self.phonemes.get_letters(symbol)
                    word_spelling.append(random.choice(letters))

        # TODO: affixation before sound changes
        #   - have Language method for building and applying sound change atop units

        # apply sound changes to built word
        word_changed = self.apply_rules(word_ipa)[1] if apply_rules else word_ipa

        word_spelling = "".join(word_spelling)
        word_ipa = "".join(word_ipa)

        # # add to dictionary instance
        # if store_in_dictionary:
        #     entries = self.dictionary.add(spelling=word_spelling, sound=word_ipa, sound_change=word_changed, definition=definition)
        #     return entries[len(entries)-1]
        #else:
        # mimic dictionary entry
        return {
            'spelling': word_spelling,
            'sound': word_ipa,
            'change': word_changed,
            'definition': definition
        }
