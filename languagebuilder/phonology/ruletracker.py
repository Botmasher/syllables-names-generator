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

    def get(self, track_id=None):
        """Read one track or all if no id specified"""
        if track_id:
            if track_id in self.tracks:
                return self.tracks[track_id]
            else:
                return {}
        return self.tracks
    
    def successes(self):
        """Filter all tracks down to a map of only successful ones."""
        return {
            track_id: track
            for track_id, track in self.tracks.items()
            if track['success']
        }

    def failures(self):
        """Filter all tracks down to a map of only failed ones."""
        return {
            track_id: track
            for track_id, track in self.tracks.items()
            if track['failure']
        }

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
            # succed/fail flags to set during sound or environment checks
            'succes': False,
            'failure': True
        }
        print(f"RuleTracker set up tracking starting at word index {word_index}")
        return track_id

    def untrack(self, track_id):
        """Remove one rule environment slot match check to the rules application tracker"""
        if track_id not in self.tracks:
            print(f"RuleTracker failed to untrack - invalid track_id {track_id}")
            return
        self.tracks.pop(track_id)
        return track_id

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

        # TODO: verify that boundary is being checked sequentially then delete!
        # also check for and count end boundary match
        #if track['count'+2] >= len(self.environment) and self.environment[track['count'+1]] == "#":
        #    track['count'] += 1
        
        return self.tracks[track_id]
    
    def check_success(self, track_id):
        """Mark a rule track as successful if it has a valid source sound and matched
        up to the length of the rule's environment. Return the track's success value."""
        if self.tracks[track_id]['count'] >= len(self.environment):
            self.tracks[track_id]['success'] = True
        return self.tracks[track_id]['success']

    def match_all(self, features, index):
        """Match the current sound against source or environment matches for every track.
        Return ids for matched tracks."""
        unmatched_tracks = []
        matched_tracks = []
        for track_id in self.tracks:
            did_track = self.match(track_id, features, index)
            matched_tracks.append(track_id) if did_track else unmatched_tracks.append(track_id)
        
        # NOTE: 'success' and 'failure' keys added to avoid mutating tracks during loops
        #[self.tracks.pop(t) for t in unmatched_tracks]
        
        return matched_tracks
    
    # Check if tracks continue to match
    # - Untrack them if they do not
    # - Continue tracking (update slot match count) if they do
    # - If found slot _ match, bingo! - store the sound plus the word_i in track["index"] attr
    # - Add track to successful matches if environment count reached length
    #   - untrack and get the popped track entry
    #   - make sure you have a source sound and an index in the track entry
    #   - store the popped track in full_matches
    def match(self, track_id, features, index):
        """Check for source or environment match and update or remove track depending
        on successful match. Enable each finished track's success flag and each failed
        track's failure flag. Skip previously failed and successful tracks.
        NOTE: does not clear out unmatched tracks!
        args:
            track_id (int):     track key representing starting word index of the track
            features (list):    sound features collection to match against next environment slot
            index (int):        index of the current sound being evaluated in the word
        """
        # expect a valid track and features
        if not isinstance(features, (list, tuple, set)):
            raise TypeError(f"RuleTracker match failed - invalid features collection {features}")
        track = self.get(track_id)
        if not track:
            raise ValueError(f"RuleTracker match failed - invalid track id {track_id}")
        
        # do not check track if track has finished
        if track['success'] or track['failure']:
            print(f"RuleTracker match skipped {features} - track {track_id} has already {('succeeded', 'failed')[not track['success']]}.")
            return

        environment_features = self.environment[track['count']]

        # Keep tracking if features match current slot, otherwise untrack
        
        # NOTE: attempting to handle this case when checking environment slot match
        # match a boundary marker at this slot
        #if environment_features == self.boundary_symbol:
        #    pass
        
        # match the source sound to change
        if environment_features == self.source_symbol:
            return self.check_source_match(track_id, features, index)
        # check for environment slot match, including features or word boundary
        return self.check_environment_match(track_id, features)

    # determine if a phonetic symbol fits in an environment slot
    def is_features_submatch(self, slot_features, symbol_features):
        """Check if the symbol has all listed features. Intended for comparing environments and applying rules."""
        # are all slot features found in this symbol's features?
        return set(symbol_features) >= set(slot_features)

    def check_source_match(self, track_id, features, index):
        """Determine if the sound fits in the source->target change slot in the environment"""
        # fetch current track and environment
        track = self.tracks[track_id]
        environment_slot = self.environment[track['count']]
        # check if the evaluated sound has all of the rule source features
        if self.is_features_submatch(self.source_features, features):
            self.set_source_match(track_id, features, index)
            print(f"RuleTracker successfully found a source sound with features {features}")
            # mark success if rule completely finished matching
            self.check_success(track_id)
            return True
        
        # sound is not a source features match for the slot
        print(f"RuleTracker did not find a source match on {features}, even though environment up to this point matched.")
        self.tracks[track_id]['failure'] = True
        
        # log extra message when failure is owed to no environment slot match
        if environment_slot != self.source_symbol:
            print(f"RuleTracker expected a source slot symbol {self.source_symbol} at slot {environment_slot}")
       
        return False

    # TODO: just pass track and sound, since track already knows environment
    # NOTE: at this point you could handle much more here!
    #   - send slot to match and let tracker figure out if it's source, environment, edge
    #   - declare match done here in tracker
    def check_environment_match(self, track_id, features):
        """Determine if the sound fits in the environment slot"""
        # read track and environment data
        track = self.tracks[track_id]
        environment_slot = self.environment[track['count']]
        # failed environment match - prepare to reset this particular track
        if not self.is_features_submatch(environment_slot, features):
            self.tracks[track_id]['failure'] = True
            return False
        # surrounding environment match - count and keep tracking rule
        self.count_features_match(track_id)
        # check if rule is finished and mark success
        self.check_success(track_id)         
        return True
