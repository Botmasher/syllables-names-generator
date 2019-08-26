from uuid import uuid4

# NOTE: idiosyncratic usage, as with other terms in this program.
# Not every "mora" is one "beat", though this deals with storage
# and computation and does not make a theoretical assertion. In fact,
# if beats are not explicitly input, each stored mora has 1 beat.
#
# - mora: moraic item containing features associated with any number of beats
# - beat: counted number of beats for a mora
# - features (features list): same as moraic structure (ordered list of featuresets)
# - details: moraic values under the id containing its features and beats

class Morae:
    def __init__(self, phonology):
        self.phonology = phonology
        self.morae = {}         # map moraic ids to features and beat count data
    
    def get(self, moraic_id=None):
        """Return the moraic details stored under the given id key, or all items
        if no key is specified."""
        if moraic_id is not None:
            return self.morae.get(moraic_id)
        return self.morae

    def add(self, sounds_or_features, beats=1, overwrite=False):
        """Store a moraic structure and its associated beat count. Sounds or features
        will be converted to a valid list of featuresets and used in the future
        to identify matching morae.
        
        Args:
            sounds_or_features (list): List of featuresets or sound strings.
            beats (int, float): the number of beats in the mora(e).
        
        Returns:
            A string id morae dict key where the mapped value stores moraic details.
        """
        if not isinstance(beats, (int, float)):
            raise TypeError(f"Morae expected beat count to be a number not {beats}")

        # structure mora as list of lists
        moraic_list = self.vet_mora(sounds_or_features)

        if not moraic_list:
            print(f"Morae failed to add invalid mora {sounds_or_features}")
            return
        
        # optionally remove mora if it already exists
        existing_moraic_ids = self.find(moraic_list, vet_mora=False)
        if existing_moraic_ids:
            if overwrite:
                [self.remove(moraic_id) for moraic_id in existing_moraic_ids]
            else:
                print(f"Moraic structure already exists in Morae: {existing_moraic_ids}")
                return

        # map moraic details
        moraic_id = f"moraic-{uuid4()}"
        self.morae[moraic_id] = {
            'features': moraic_list,    # list of features lists
            'beats': beats              # beat count
        }
        return moraic_id

    def remove(self, moraic_id):
        """Delete one item from the morae map"""
        return self.morae.pop(moraic_id)

    def find(self, mora=None, beats=None, vet_mora=True, first_only=False):
        """Return a list of ids for morae that share the beatcount or moraic structure"""
        # 
        if not (mora or beats):
            print(f"Morae find failed - expected moraic structure or beats to search for")
            return

        # structure mora into list of featuresets
        features = self.vet_mora(mora) if vet_mora and mora else mora
        
        # search for matching morae
        moraic_ids = []
        for moraic_id, moraic_details in self.morae.items():
            # match morae with requested data
            requested_details = {
                'features': features if features else moraic_details['features'],
                'beats': beats if beats else moraic_details['beats']
            }
            if requested_details == moraic_details:
                moraic_ids.append(moraic_id)
            # break and return at the very first matching moraic entry
            if moraic_ids and first_only:
                return moraic_ids

        return moraic_ids

    def match(self, features_list):
        """Return a list of ids for morae where this moraic structure is a features
        subset match for every feature in a same-length sample superset"""
        moraic_ids = [
            moraic_id
            for moraic_id, moraic_details in self.morae.items()
            if set(features_list).issuperset(set(moraic_details['features']))
        ]
        return moraic_ids

    def is_mora(self, mora):
        """Check if the moraic structure exists within stored morae"""
        mora_list = self.vet_mora(mora)
        return self.find(mora_list, first_only=True) is not None
        
    # TODO: turn this into a more general phonology list of features list method
    #   - could be used to generate sylls, ...
    def vet_mora(self, sounds_or_features):
        """Turn a list of sounds or features into a list of lists of features
        to be identified as a mora"""
        vetted_mora = []
        for features in sounds_or_features:
            # attempt to read as a single sound
            if self.phonology.phonetics.has_ipa(features):
                vetted_mora.append(self.phonology.phonetics.get_features(features))
            # attempt to read as a special feature character
            elif isinstance(features, str) and features in self.phonology.syllables.syllable_characters:
                feature = self.phonology.syllables.syllable_characters[features]
                vetted_feature = feature if self.phonology.phonetics.has_feature(feature) else None
                if vetted_feature:
                    vetted_mora.append([vetted_feature])
            # attempt to read as a feature string or features list
            elif self.phonology.phonetics.parse_features(features):
                vetted_features = self.phonology.phonetics.parse_features(features)
                vetted_mora.append(vetted_features)
            # back out if sound or features not found in this position
            else:
                print(f"Morae failed to vet unrecognized features in {sounds_or_features}")
                return
        return vetted_mora

    # TODO: handle conflicts/overlaps, like if V counts as 1 but VC is 2
    
    def is_superlist(self, list_of_setlists, compared_setlist):
        """Check that any setlists in a list of list of sets are supersets of the
        compared setlist's sets, in order"""
        matches = list(filter(
            lambda x: x,
            [
                set(l[i]).issuperset(set(compared_setlist[i]))
                if i < len(compared_setlist) else False
                for l in list_of_setlists
                for i in range(len(l))
            ]
        ))
        return any(matches)

    def count(self, sounds_sample):
        """Count the number of beats in a sound sample based on stored morae"""
        # convert sounds into a list of per-sound feature collections
        sample_features = [
            self.phonology.phonetics.get_features(sound)
            for sound in sounds_sample
        ]
        
        # keep track of moraic windows from sample and matched moraic beats
        tracked_morae = []
        count = 0
        
        # track, build and match moraic subsample windows
        for features in sample_features:
            # add features to all tracks and start a new track with current features
            # (each sample sound/features list starts a new features set list)
            tracked_morae += [[]]
            [track.append(features) for track in tracked_morae]
            # traverse morae looking for matches
            for compared_details in self.morae.values():
                compared_features = compared_details['features']
                # compare tossable tracks for full matchups
                # (any sample moraic window matches any existing moraic entry)
                if self.is_superlist(tracked_morae, compared_features):
                    # count beats and reset tracking
                    count += compared_details['beats']
                    tracked_morae.clear()
                    break
        
        ## TODO: figure a way to check for leftover beats
        # if leftover_beats_check():
        #    return

        return count
            