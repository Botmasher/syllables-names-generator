import uuid     # track_ids

# Helper for Language.apply_rule
# track each application of a sound change rule
# - track an ongoing search for rule environment match in a phonetic string
# - store the source
class RuleTracker():
    def __init__(self):
        self.tracker = {}

    def track(self, rule_id, environment_structure, sound_features):
        """Add ongoing rule environment slot match check to the rules application tracker"""
        # check for valid environment sequence
        environment_structure
        if not environment_structure:
            print(f"RuleTracker failed to track rule - invalid environment {environment_structure}")
            return

        print(f"RuleTracker will track rule if sound fits {environment_structure[0]}")
        
        # compare first environment slot to see if current symbol fits
        environment_slot = environment_structure[0]
        if not self.is_features_submatch(environment_slot, sound_features):
            print("RuleTracker failed to track - sound {0} did not match environment slot {1}".format(sound_features, environment_slot))
            return
        
        # create a new track
        track_id = uuid.uuid4()
        self.tracker[track_id] = {
            # the current slot being evaluated for sound matches
            'count': 0,
            # the total number of slots to match before applying rule
            'length': len(environment_structure),
             # identified sounds to change
            'source': '',
            # index of identified sound to change
            'index': None,
            # rule object defining environment and change
            'rule': rule_id
        }
        print("RuleTracker started tracking")
        return track_id

    def untrack(self, track_id):
        """Remove one rule environment slot match check to the rules application tracker"""
        if track_id not in self.tracker:
            print("RuleTracker failed to untrack - invalid track_id {0}".format(track_id))
            return
        self.tracker.pop(track_id)
        return track_id

    def get(self, track_id=None):
        """Read one track or all if no id specified"""
        if track_id:
            if track_id in self.tracker:
                return self.tracker[track_id]
            else:
                return {}
        return self.tracker

    # TODO: connect match setting directly to source/environment check methods
    #   - avoid business logic in Language.apply_rule
    def set_source_match(self, track_id, source=None, index=None):
        """Add identified source sound and source index to an existing rule track"""
        if track_id not in self.tracker:
            print(f"RuleTracker set source failed - unknown track {track_id}")
            return
        if not index or not source:
            print(f"RuleTracker set source failed - missing critical ipa index or source info")
            return
        print(f"Found source match (_)! Storing {source}")
        self.tracker[track_id]['source'] = source
        self.tracker[track_id]['index'] = index
        self.tracker[track_id]['count'] += 1
        return self.tracker[track_id]

    def count_features_match(self, track_id):
        """Count up a matching feature for this track. Counts are used
        to determine when a rule fully applies across sounds in a word."""
        if track_id not in self.tracker:
            print("RuleTracker count match failed - unknown track {0}".format(track_id))
            return
        self.tracker[track_id]['count'] += 1
        return self.tracker[track_id]

    # determine if a phonetic symbol fits in an environment slot
    def is_features_submatch(self, slot_features, symbol_features):
        """Check if the symbol has all listed features. Intended for comparing environments and applying rules."""
        # are all slot features found in this symbol's features?
        return set(symbol_features) >= set(slot_features)

    def is_source_slot_match(self, sound_features, environment_features, source_features):
        """Determine if the sound fits in the source->target change slot in the environment"""
        # not an environment slot match
        if environment_features not in ["_", ["_"]]:
            return False
        # check if the evaluated sound has all of the rule source features
        if self.is_features_submatch(source_features, sound_features):
            return True
        # sound is not a source features match for the slot
        print("Did not find a source match on {0}, even though environment up to this point matched.".format(sound_features))
        return False

    def is_environment_slot_match(self, sound_features, environment_features):
        """Determine if the sound fits in the environment slot"""
        # no environment match - reset this particular rule
        if not self.is_features_submatch(environment_features, sound_features):
            return False
        # surrounding environment match - keep tracking rule
        return True
