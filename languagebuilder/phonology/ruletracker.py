import uuid     # track_ids

# Track each application of a sound change rule
# - follows all sequential matches for a single rule
# - tracks ongoing search for rule environment match in a phonetic string
# - stores the source sound to change if successful
# - TODO: removes any unsuccessful tracks along the way
# - TODO: access externally by iterating through a sound sequence and calling:
#   - .track when starting to track a rule application at a specific sound
#   - .match when continuing to track a rule application at subsequent sounds
#   - .successes when finished tracking to fetch all successful tracks
class RuleTracker():
    def __init__(self, environment, source_features, source_symbol="_", boundary_symbol="#"):
        # track ongoing matches of the rule
        self.tracks = {}
        
        # store rule information
        self.environment = environment  # environment slots for checking features and length
        self.source_features = source_features  # features to match for sound to change
        # NOTE: rule_id no longer necessary if applying one sound change at a time
        #self.rule_id = rule_id          # tracked rule defining environment and change
        
        # store symbols for checking against source slots and start/end boundaries
        self.source_symbol = source_symbol
        self.boundary_symbol = boundary_symbol

    def track(self, word_index):
        """Add ongoing rule environment check to the rule application tracker
        to compare the current position in the word to the first position in
        the rule environment. Sets up track only - does not begin checking for
        matches until match called on the created track."""
        # compare first environment slot to see if current symbol fits - skip to
        # (successfully match) word start symbol if present in rule environment
        #
        # TODO: remove Phonology.apply_rule architecture looking for boundary matches
        #   - this is now handled here
        #   - also work this magic in slots below, comparing environment len to ?
        #   - would need to know actual environment structure each time

        # create a track for this rule at this position
        track_id = uuid.uuid4()

        # avoid starting multiple tracks for the same rule at the same word index
        if word_index in self.tracks:
            print(f"RuleTracker track failed - already tracking starting at index {word_index}")
            return

        # set up track using initial index where this track was set as key
        self.tracks[word_index] = {
            'count': 0,     # current slot to evaluate for sound matches
            'source': "",   # identified sound to change
            'index': None,  # index of identified sound to change
        }
        print(f"RuleTracker set up tracking starting at word index {word_index}")
        return track_id

    def untrack(self, track_id):
        """Remove one rule environment slot match check to the rules application tracker"""
        if track_id not in self.tracks:
            print("RuleTracker failed to untrack - invalid track_id {0}".format(track_id))
            return
        self.tracks.pop(track_id)
        return track_id

    def get(self, track_id=None):
        """Read one track or all if no id specified"""
        if track_id:
            if track_id in self.tracks:
                return self.tracks[track_id]
            else:
                return {}
        return self.tracks

    # TODO: connect match setting directly to source/environment check methods
    #   - avoid business logic in Language.apply_rule
    def set_source_match(self, track_id, source=None, index=None):
        """Add identified source sound and source index to an existing rule track"""
        if track_id not in self.tracks:
            print(f"RuleTracker set source failed - unknown track {track_id}")
            return
        if not index or not source:
            print(f"RuleTracker set source failed - missing critical ipa index or source info")
            return
        print(f"Found source match (_)! Storing {source}")
        self.tracks[track_id]['source'] = source
        self.tracks[track_id]['index'] = index
        self.tracks[track_id]['count'] += 1
        return self.tracks[track_id]

    def count_features_match(self, track_id):
        """Count up a matching feature for this track. Counts are used
        to determine when a rule fully applies across sounds in a word."""
        # count sound match
        track = self.tracks[track_id]
        track['count'] += 1
        # also check for and count end boundary match
        if track['count'+2] >= len(self.environment) and self.environment[track['count'+1]] == "#":
            track['count'] += 1
        return self.tracks[track_id]

    def finish(self):
        """End tracking and return all successful tracks"""
        return {
            # filter tracks
            track_id: track
            for track_id, track in self.tracks
            # define track success
            if track['source'] and track['count'] >= len(self.environment)
        }

    def match_all(self, features, index):
        """Match the current sound against source or environment matches for every track"""
        for track_id in self.tracks:
            self.match(track_id, features, index)
        return
    
    def match(self, track_id, features, index):
        """Check for source or environment match and update or remove track depending
        on successful match."""
        # check for valid track and features
        if not isinstance(features, (list, tuple, set)):
            raise TypeError(f"RuleTracker match failed - invalid features collection {features}")
        track = self.get(track_id)
        if not track:
            raise ValueError(f"RuleTracker match failed - invalid track id {track_id}")
        
        environment_features = self.environment[track['count']]

        did_match = False

        # Keep tracking if features match current slot, otherwise untrack
        #
        # match a boundary marker at this slot
        if environment_features == self.boundary_symbol:
            # TODO: handle this case if within environment
            pass
        # match the source sound to change
        elif environment_features == self.source_symbol:
            # TODO: handle all this in source slot check
            if self.is_source_slot_match:
                self.set_source_match(track_id, features, index)
                did_match = True
            else:
                self.untrack(track_id)
        # match an environment slot surrounding the source to change
        else:
            # TODO: handle all this in environment slot check
            if self.is_environment_slot_match(track_id, features):
                self.count_features_match(track_id)
                did_match = True
            else:
                self.untrack(track_id)

        return did_match

    # determine if a phonetic symbol fits in an environment slot
    def is_features_submatch(self, slot_features, symbol_features):
        """Check if the symbol has all listed features. Intended for comparing environments and applying rules."""
        # are all slot features found in this symbol's features?
        return set(symbol_features) >= set(slot_features)

    def is_source_slot_match(self, sound_features, environment_features, source_features):
        """Determine if the sound fits in the source->target change slot in the environment"""
        # not an environment slot match
        if environment_features != self.source_symbol:
            return False
        # check if the evaluated sound has all of the rule source features
        if self.is_features_submatch(source_features, sound_features):
            return True
        # sound is not a source features match for the slot
        print("Did not find a source match on {0}, even though environment up to this point matched.".format(sound_features))
        return False

    # TODO: just pass track and sound, since track already knows environment
    # NOTE: at this point you could handle much more here!
    #   - send slot to match and let tracker figure out if it's source, environment, edge
    #   - declare match done here in tracker
    def is_environment_slot_match(self, track_id, sound_features):
        """Determine if the sound fits in the environment slot"""
        track = self.get(track_id)
        environment_features = self.environment[track['count']]
        # no environment match - reset this particular rule
        if not self.is_features_submatch(environment_features, sound_features):
            return False
        # surrounding environment match - keep tracking rule
        return True
