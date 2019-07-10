# collection management
from .phonemes import Phonemes
from .syllables import Syllables
from .rules import Rules
from .ruletracker import RuleTracker
# for sound, letter and syllable generation
import random

# TODO: accentuation/suprasegmentals here and in Phonetics 

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

        # TODO: check Phonetics here and pass crud to Syllables for consistency
        #   - already done with add_sound (for Phonemes), add_rule (for Rules)
        #   - the Language checks Phonetics but the injected classes remain decoupled
        self.syllables = Syllables(self)    # reference phonology for feature checking

        # creating and applying rules
        self.rules = Rules()
        self.source_symbol = "_"
        self.boundary_symbol = "#"

    # inventory now managed through Phonemes (letters <> ipa) and Features (features <> ipa) instead of previous Inventory class
    def inventory(self):
        """Read all phonetic symbols stored in this inventory"""
        return self.phonemes.symbols()
    
    # Rules
    def add_rule(self, source, target, environment_structure):
        """Add one rule to the phonological rules"""
        # NOTE: environment now handled from within Rules
        # create the environment
        # environment = Environment(structure=environment_structure)
        # if not environment.get():
        #     print(f"Phonology add_rule failed - invalid environment structure {environment_structure}")
        #     return
        
        # filter features sequences
        vetted_source = self.phonetics.parse_features(source)
        vetted_target = self.phonetics.parse_features(target)
        print("Adding Rule - vetted source: ", vetted_source)
        print("Adding Rule - vetted target: ", vetted_target)

        if not (vetted_source and vetted_target):
            print(f"Phonology add_rule failed - invalid features lists for source {vetted_source} or target {vetted_target}")
            return

        # create and store the rule
        rule_id = self.rules.add(vetted_source, vetted_target, environment_structure)
        if not rule_id:
            print("Phonology add_rule failed - invalid source, target or environment")
            return
        return rule_id

    def get_rule(self, rule_id, pretty_print=False):
        """Look up one rule in the phonological rules collection"""
        # fetch the rule and verify it returned a rule object
        rule = self.rules.get(rule_id)
        if not rule:
            print(f"Phonology get_rule failed - unknown rule {rule_id}")
        # format the rule in human readable text instead
        if pretty_print:
            return self.rules.get_pretty(rule_id)
        # send back the rule object
        return rule

    def has_rule(self, rule_id):
        """Check if a single rule exists in the phonological rules collection"""
        return self.rules.has(rule_id)
    
    def remove_rule(self, rule_id):
        """Delete a rule from the phonological rules collection"""
        return self.rules.remove(rule_id)

    # Syllable methods to stay consistent with rule and sound management at this level
    def add_syllable(self, syllable_structure):
        """Passthrough method for Syllables add"""
        return self.syllables.add(syllable_structure)
    #
    def update_syllable(self, syllable_id, syllable_structure):
        """Passthrough method for Syllables update"""
        return self.syllables.update(syllable_id, syllable_structure)
    #
    def remove_syllable(self, syllable_id):
        """Passthrough method for Syllables remove"""
        return self.syllables.remove(syllable_id)

    # IPA methods checking both phonology and phonetics
    def has_sound(self, ipa):
        """Check that fully-featured sound exists both in phonemes and phonetics"""
        if self.phonetics.has_ipa(ipa) and self.phonemes.has(ipa):
            return True
        return False
    #
    def get_sound_features(self, ipa):
        if not self.has_sound(ipa):
            print(f"Phonology get_sound_features failed - unknown symbol {ipa}")
            return
        return self.phonetics.get_features(ipa)
    #
    def get_sound_letters(self, ipa):
        if not self.has_sound(ipa):
            print(f"Phonology get_sound_letters failed - unknown symbol {ipa}")
            return
        return self.phonemes.get_letters(ipa)
    #
    def get_sound_weight(self, ipa):
        if not self.has_sound(ipa):
            print(f"Phonology get_sound_weight failed - unknown symbol {ipa}")
            return
        return self.phonemes.get_weight(ipa)
    #
    # TODO: add weights for letter choice
    #   - current weight intended for distributing phon freq
    def add_sound(self, ipa, letters=[], weight=0):
        """Add one phonetic symbol, associated letters and optional weight
        to the inventory and """
        if not self.phonetics.has_ipa(ipa) or not all(isinstance(l, str) for l in letters) or len(letters) < 1:
            raise NameError("Phonology add_sound failed - invalid phonetic symbol or letters")
        # check for modification to existing phoneme
        if self.phonemes.has(ipa):
            print(f"Phonology add_sound failed - phoneme {ipa} already exists")
            return
        # store phoneme data
        return self.phonemes.add(ipa, letters, weight)
    #
    def add_sounds(self, ipa_letters_map):
        """Add multiple phonetic symbols to the inventory with their associated
        letters and optional weight"""
        if not isinstance(ipa_letters_map, dict):
            print(f"Phonology add_sounds failed - expected dict not {type(ipa_letters_map)}")
            return
        sounds = []
        for ipa, letters in ipa_letters_map.items():
            added_sound = self.add_sound(ipa, letters=letters)
            sounds.append(added_sound)
        return sounds
    #
    def update_sound(self, ipa, letters=None, weight=None, new_ipa=None):
        """Update sound properties, only modifying ipa if it is a known phonetic symbol"""
        if new_ipa and not self.phonetics.has_ipa(new_ipa):
            print(f"Phonology update_sound failed - invalid new ipa symbol {new_ipa}")
            return
        return self.phonemes.update(
            ipa,
            letters=letters,
            weight=weight,
            new_ipa=new_ipa
        )
    #
    def remove_sound(self, ipa):
        """Passthrough method for removing a single phoneme from the inventory"""
        return self.phonemes.remove(ipa)

    # use rule to turn symbol from source into target
    def change_symbol(self, source_features, target_features, ipa_symbol, exact=True):
        """Turn one symbol into another with a source -> target features shift.
        args:
            source_features (list): sound features to be replaced (change from)
            target_features (list): sound features to be adopted (change into)
            ipa_symbol (str):       ipa symbol representing the changed sound
            exact (bool):           get ipa with updated features as an improper set
        returns:
            => (str)    a single ipa symbol after this sound change
        """
        # fetch symbols matching the symbol feature
        symbol_features = self.phonetics.get_features(ipa_symbol)
        new_symbol_features = set(target_features)
        
        # log start of change attempt
        print(f"Currently attempting to turn {symbol_features} into a {target_features}")
        
        # merge target features into symbol features where rule changes from source->target
        for feature in symbol_features:
            if feature in source_features and feature not in target_features:
                pass
            else:
                new_symbol_features.add(feature)
        
        # find phonetic symbols with these features
        # from all possible symbols not just current inventory
        new_symbols = self.phonetics.get_ipa(list(new_symbol_features), exact=exact)

        # no symbols match this new set of features
        if not new_symbols:
            # log change attempt failure
            print(f"Unable to find a symbol matching {new_symbol_features}. Keeping {symbol_features}.")
            return

        # choose a new symbol from matching symbols
        new_symbol = new_symbols[0]

        # TODO: decide how to select from symbols list (just zeroth? arbitrary?)
        
        # log change attempt success
        print(f"Successfully changed '{ipa_symbol}' into '{new_symbol}'.")

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
    # - walk through the word's sounds and the phonological rules
    # - see if rule and word environments match (relying on RuleTracker for help)
    # - apply rule to change source sound in word to rule target sound if they do
    
    # TODO: interact with lexicon storage, adding phonetic word and sound change alongside spelling and definition
    #   - store tracks or store the changed symbols list alongside word in lexicon

    def apply_rule(self, ipa, rule_id):
        """Change a word's sounds applying one sound change rule"""
        if not isinstance(ipa, (str, list, tuple)):
            print(f"Phonology apply_rule failed - expected ipa string or list not {ipa}")
            return
        
        # set of word sound symbols
        try:
            word_sounds = set([c for c in ipa])
        except:
            raise ValueError(f"Phonology apply_rule failed - invalid sound sequence {ipa}")
        
        # prepare input sequence for search - add start and end markers
        ipa_sequence = [self.boundary_symbol] + list(ipa) + [self.boundary_symbol]

        # features for all sounds in the word including word boundary
        word_features = {
            ipa: self.phonetics.get_features(ipa)
            for ipa in word_sounds
        }
        word_features[self.boundary_symbol] = self.boundary_symbol

        # fetch the rule object
        rule = self.rules.get(rule_id)
        if not rule:
            print(f"Phonology apply_rule failed - invalid rule_id {rule_id}")
            return

        # store tracks for each possible rule application
        # TODO: consider if this is one instance per rule only
        #   - originally instantiated in apply_rules
        #   - how to track individual tracks across all rules given feeding?
        rule_tracker = RuleTracker(
            rule['environment'],
            rule['source'],
            source_symbol=self.source_symbol,
            boundary_symbol=self.boundary_symbol
        )

        # look through features and find environment matches for each step of every rule
        # use with self.rule_tracker and methods, full matches and strategy commented above to handle overlaps
        for word_index in range(len(ipa_sequence)):
            symbol = ipa_sequence[word_index]
            sound_features = word_features[symbol]

            # log this attempt to fit symbol into rule environment
            print(f"Checking if rule starts applying at {sound_features}.\nRule: {self.rules.get_pretty(rule_id)}")

            # Rule Track: start tracking for full environment match at this word index
            rule_tracker.track(word_index)

            # store completed rule tracks and avoid mutating dict mid iteration
            #tracks = rule_tracker.get()

            # Tracks Loop: do any tracked applications ("tracks") continue to match?
            # - each track is an ongoing attempt to match the rule
            # - attempt to match word sound to each currently tracked environment slot
            rule_tracker.match_all(sound_features, word_index)
            
        # prepare an ipa representation of the word to update as rule applied
        new_ipa_sequence = list(ipa_sequence)

        # change sounds identified as source matches in successful rule tracks
        for successful_track in rule_tracker.successes().values():
            # get the sound to change
            index_to_change = successful_track['index']
            ipa_to_change = new_ipa_sequence[index_to_change]
            
            # verify sound to change has not been updated to fall outside of rule
            features_to_change = self.phonetics.get_features(ipa_to_change)
            if not rule_tracker.is_features_submatch(rule['source'], features_to_change):
                continue

            # perform the sound change
            changed_ipa = self.change_symbol(
                rule['source'],  # rule source features that were matched
                rule['target'],  # rule target features to transform sound
                ipa_to_change    # the matched sound to change
            )
            if not changed_ipa:
                changed_ipa = ipa_to_change
            print("source ipa: " + ipa_to_change)
            print("updated ipa: " + changed_ipa)

            # store the changed sound
            new_ipa_sequence[index_to_change] = changed_ipa

        # remove added start and end boundaries
        if new_ipa_sequence[0] == self.boundary_symbol and new_ipa_sequence[-1] == self.boundary_symbol:
            new_ipa_sequence = new_ipa_sequence[1:-1]
        else:
            raise ValueError(f"Changed word lacks expected start and end boundaries.")

        # send back the list of sequences with sounds changed
        print(f"Finished applying rule to create new sequence: {new_ipa_sequence}")
        return new_ipa_sequence

    def apply_rules(self, ipa_sequence):
        """Change a word's sounds applying every sound change rule. This feeds the
        result of each rule application to the next rule as sorted in Rules.order"""

        # set up the word
        print(f"\nApplying all rules to input ipa sequence {ipa_sequence}")
        new_ipa_sequence = [character for character in ipa_sequence]

        # traverse local rules map searching for and applying rule matches
        for rule_id in self.rules.get():
            new_ipa_sequence = self.apply_rule(new_ipa_sequence, rule_id)

        print(f"Finished applying all rules to create new ipa sequence {new_ipa_sequence}\n")

        # return the changed sequence fed through all rules
        return new_ipa_sequence

    def build_word(self, length=1, apply_rules=True, spell_after_change=False, order_rules=True, as_string=False, midpoint=None):
        """Form a word following the defined inventory and syllable structure.
        Run optional syllable event on each successful syllable built.
        
        args:
            length (int): number of syllables in the built word
            apply_rules (bool): whether to apply sound change rules to the word
            spell_after_change (bool): whether to base the spelling on the changed sounds
            order_rules (bool): apply sound change rules in order or randomly
            as_string (bool): return the word as a string instead of a list of ipa symbols
            midpoint (int): number of syllables to the left of word split point
        return:
            map entry representing a built word following the phonology. map attributes:
            'sound' (list): string list containing the basic sounds in the word
            'change' (list): string list containing sounds after sound changes applied
            'spelling' (list): string list containing spelling symbols derived from sounds
            'midpoint' (int): the split/infix point within the sound symbols
        """
        # form a list of possible syllables to choose from
        syllables = self.syllables.get()
        if not syllables:
            print("Phonology build_word failed - no possible syllables found")
            return

        # choose random syllable structures to build shape of final word
        syllable_structures = [
            syllables[random.choice(list(syllables.keys()))]
            for i in range(length)
        ]

        print(f"Choosing from syllable structures:\n{syllable_structures}")

        # store sound (phonemes) forms of words being built
        word_ipa = []

        # prepare to count number of sounds before midpoint syllable
        if midpoint:
            syllable_count = 0
            midpoint_sound_count = 0

        # TODO: choose ipa by frequency (commonness) using Phoneme 'weight'
        for syllable_structure in syllable_structures:
            built_syllable = []
            for feature_set in syllable_structure:
                # find all inventory ipa that have these features
                symbols = self.phonetics.get_ipa(feature_set, filter_phonemes=self.inventory())
                print("Choosing from the following symbols: ", symbols)
                # TODO: you store Phoneme with associated letters so this should be easy
                #   - inventory maps features to letters
                #   - features maps them to sounds
                #   - instead stick with features <> ipa <> letters
                #   - use Features and Phoneme to accomplish (see features.py comment)
                if symbols:
                    # choose from ipa symbols that matched subset of features
                    symbol = random.choice(symbols)
                    # storage
                    word_ipa.append(symbol)         # for word output
                    built_syllable.append(symbol)   # for syllable-by-syllable callback
            # count up the number of sounds to the left of the midpoint
            if midpoint:
                if syllable_count < midpoint:
                    midpoint_sound_count += len(built_syllable) 
                syllable_count += 1

        # TODO: affixation before sound changes
        #   - have Language method for building and applying sound change atop units

        # apply sound changes to built word
        word_changed = self.apply_rules(word_ipa) if apply_rules else word_ipa

        #raise ValueError(f"oh no it's {word_ipa}, which changed into {word_changed}")

        # respell word either before or following sound changes
        word_spelling = self.spell(word_changed, word_ipa) if spell_after_change else self.spell(word_ipa)
        
        # send back phones, sound change result and spelling result
        word_entry = {
            'spelling': word_spelling,
            'sound': word_ipa,
            'change': word_changed,
            'midpoint': midpoint_sound_count if midpoint else None
        }

        # optionally turn lists of sound symbols into strings
        # NOTE: intended for custom output; language methods expect lists of strings!
        if as_string:
            return {
                k: "".join(v) if isinstance(v, list) else v
                for k, v in word_entry.items()
            }

        return word_entry

    # TODO: handle spelling rules and environments
    def spell(self, phonemes, fallback_phonemes=None):
        """Transform a list of sounds into a list of letters (including multigraphs)
        representing a spelled word. Use optional fallback list in case changed
        phonemes do not have letters. Fallback length and character indexes must match
        the main phonemes list."""
        # check for valid input lists
        if not isinstance(phonemes, list):
            raise TypeError(f"Phonology spell failed - invalid phonemes list {phonemes}")
        if fallback_phonemes:
            if not isinstance(fallback_phonemes, list):
                raise TypeError(f"Phonology spell failed - expected fallback phonemes list not {fallback_phonemes}")
            elif len(fallback_phonemes) != len(phonemes):
                raise ValueError(f"Phonology spell failed - fallback phonemes {fallback_phonemes} list length does not match phonemes {phonemes}")

        # left-to-right spelling letter storage
        letters = []
        # sound and letter that get spelled each pass
        spelled_phoneme = None
        letter = None
        # characters that can be passed through without spelling
        skippable_chars = ("")

        print(f"These are the changed sounds to spell: {phonemes}")
        print(f"These are the fallback sounds to spell: {fallback_phonemes}")

        # traverse choosing a letter for each sound
        for i, phoneme in enumerate(phonemes):
            # do not attempt to respell ignored characters
            if phoneme in skippable_chars:
                continue

            # find a valid spellable phoneme or fallback
            if self.phonemes.has(phoneme):
                spelled_phoneme = phoneme
            elif fallback_phonemes and self.phonemes.has(fallback_phonemes[i]):
                spelled_phoneme = fallback_phonemes[i]
            else:
                raise NameError(f"Phonology failed to spell unrecognized phoneme {phoneme} or find a fallback sound {fallback_phonemes[i]}.")
            
            
            # choose a letter from possible representations
            letter = random.choice(list(self.phonemes.get_letters(spelled_phoneme)))
            # store the letter to spell this sound
            letters.append(letter)

        # send back a list of letters spelling the word
        return letters
