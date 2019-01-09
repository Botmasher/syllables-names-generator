# (Features : features <> (ipa) <> letter : Phoneme)
#   - "feature" is broad, including "consonant" or really any consistent string
#   - "ipa" is any phonetic symbol associated with features
#   - "letter" is generally a looser graphic representation in writing
# features <> syllables
#   - "syllable" is a sequence of feature collections when generating a syllable
#   - a list of features is used to pick each letter in a syllable
# features, letters, syllables < inventory
#   - each letter can be added as multiple phonemes ("th" may be two letters)
#   - OR just have inventory store map of {letter:[phonemes]}
#   - may need to generate not just words but underlying sounds, then letters
# inventory, rules < language
#   - rules contain sequences of lists like syllables
#   - rules couple two sequences, input and operation, for how sounds should change
#   - search for input matches then change specific features
#       - this means storing strings of features for each word, or phon symbs

# features to and from phonetic symbols
class Features:
    def __init__(self):
        self.features = {}  # map feature:{ipa}
        self.ipa = {}       # map ipa:{features}

    def has_ipa(self, symbol):
        """Check if the symbol exists in the ipa map"""
        return type(symbol) is str and symbol in self.ipa

    def has_feature(self, feature):
        """Check if the feature exists in the features map"""
        return type(feature) is str and feature in self.features

    def map_by_features(self):
        """Read the ipa-per-features map"""
        return self.features

    def map_by_ipa(self):
        """Read the features-per-ipa map"""
        return self.ipa

    def get_features(self, symbol):
        """Find all features associated with a phonetic symbol"""
        if not self.has_ipa(symbol):
            print("Features get_features failed - invalid phonetic symbol {0}".format(ipa))
            return []
        return list(self.ipa[symbol])

    def get_ipa(self, features, exact=True):
        """Find phonetic symbols matching all given features"""
        if len(features) < 1:
            return []
        found_symbols = set()
        # compare test features to stored features for symbol matches
        for symbol, match_features in self.ipa:
            if exact and not set(features) ^ match_features:
                found_symbols.add(symbol)
            elif match_features.issupperset(features):
                found_symbols.add(symbol)
            continue
        return list(found_symbols)

    def add_map(self, ipa_features_map):
        """Add phonetic symbols mapped to their associated features"""
        if type(ipa_features_map) is not dict:
            print("Features add_map failed - expected dict not {0}".format(type(ipa_features_map)))
            return
        # new symbols and new features - other methods do one or the other
        for symbol, features in ipa_features_map.items():
            self.add_ipa(symbol, features)
            self.add_features(features, symbol=symbol)
        return True

    # TODO remove or update symbol
    # TODO update feature name (incl avoid conflicts)

    def add_ipa(self, symbol, features, overwrite_symbol=False):
        """Add a phonetic symbol to existing feature symbol sets"""
        if type(symbol) != str or type(features) != list:
            print("Features add_ipa failed - invalid symbol or features")
            return False
        # add new symbol
        if not self.has_ipa(symbol) or overwrite_symbol:
            print("Features add_ipa - adding new symbol {0}".format(symbol))
            self.ipa[symbol] = set()
        # add features to symbol
        for feature in features:
            if not self.has_feature(feature):
                print("Features add_ipa skipped unknown feature {0} for symbol {1}".format(feature, symbol))
            else:
                self.ipa[symbol].add(features)
        return True

    def add_features(self, features, symbol=None):
        """Add features to the features map with an associated phonetic symbol"""
        if type(features) is not list:
            print("Features add_features failed - invalid features list {0}".format(features))
            return False
        for feature in features:
            # log unrecognized or new features
            type(feature) is not str and print("Features add_feature skipped invalid feature {0}".format(feature))
            # add feature
            if not self.has_feature(feature):
                print("Adding new feature {0}".format(feature))
                self.features[feature] = set()
            # add symbol to feature
            symbol and self.features[feature].add(symbol)
        return True

    # NOTE: old add feature to add one empty entry (before class updated to double)
    def _add_feature(self, feature, default_value=None):
        """Add one new feature to the features map"""
        if type(feature) is not str:
            print("Features add_feature failed - invalid feature {0}".format(feature))
            return
        if feature not in self.features:
            self.features[feature] = {default_value} if default_value else {}
            return feature
        print("Features add_feature ignored {0} - key already exists".format(feature))
        return

    # TODO unrandomize - allow for weighted rank input
    def distribute_sounds(self, ipa):
        """Populate selectable symbols following a Zipf distribution"""
        # construct a mock population that behaves Zipfianly
        consonants = []
        vowels = []
        consonants_input = list(self.features['consonants'])[:]
        vowels_input = list(self.features['vowels'])[:]
        random.shuffle(consonants_input)
        random.shuffle(vowels_input)
        high_frequency = 1000
        for i in range(len(vowels_input)):
            vowel = vowels_input[i]
            symbol_count = (1 / i) * (most_common_frequency)
            vowels += [vowel] * symbol_count
        for i in range(len(consonants_input)):
            consonant = consonants_input[i]
            symbol_count = (1 / i) * (most_common_frequency)
            consonants += [consonant] * symbol_count
        return {'consonants': consonants, 'vowels': vowels}
