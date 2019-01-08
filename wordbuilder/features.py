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
        self.features = {}

    def get(self):
        """Read the features collection"""
        return self.features

    def get_features(self, ipa):
        """Find all features associated with a phonetic symbol"""
        if type(ipa) is not str:
            print("Features get_features failed - invalid phonetic symbol {0}".format(ipa))
            return []
        found_features = set()
        for feature, symbols in self.features.items():
            ipa in symbols and found_features.add(feature)
        return list(found_features)

    def get_ipa(self, features):
        """Find phonetic symbols matching all given features"""
        if len(features) <= 0 or features[0] not in self.features:
            return []
        # intersect symbols for listed features
        found_ipa = set(self.features[features[0]])
        for feature in features[1:]:
            if feature in self.features:
                found_ipa &= self.features[feature]
            else:
                return []
        print(found_ipa)
        return list(found_ipa)

    def add_map(self, ipa_features_map):
        """Add phonetic symbols mapped to their associated features"""
        if type(ipa_features_map) is not dict:
            print("Features add_map failed - expected dict not {0}".format(type(ipa_features_map)))
            return
        # new symbols and new features - other methods do one or the other
        for symbol, features in ipa_features_map.items():
            self.add_ipa(symbol, features)
        return self.get()

    # TODO remove or update symbol
    # TODO update feature name (incl avoid conflicts)

    def add_ipa(self, symbol, features):
        """Add a phonetic symbol to existing feature symbol sets"""
        if type(symbol) != str or type(features) != list:
            print("Features add_ipa failed - invalid symbol or features")
            return
        for feature in features:
            if feature in self.features:
                self.features[feature].add(symbol)
            else:
                self.features[feature] = {symbol}
                #self.add_feature(feature, default_value=symbol)
                #print("Features add_ipa added new feature {0}".format(feature))
        return self.get_ipa(symbol)

    def add_feature(self, feature, default_value=None):
        """Add one new feature to the features map"""
        if type(feature) is not str:
            print("Features add_feature failed - invalid feature {0}".format(feature))
            return
        if feature not in self.features:
            self.features[feature] = {default_value} if default_value else {}
            return feature
        print("Features add_feature ignored {0} - key already exists".format(feature))
        return

    def distribute_sounds(self, ipa):
        """Populate selectable symbols following a Zipf distribution"""
        # construct a mock population that behaves Zipfianly
        # TODO unrandomize - allow for weighted rank input
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

    def has_ipa(self, ipa):
        """Check if the phonetic symbol exists in the features map"""
        for feature in self.features:
            if ipa in self.features[feature]:
                return True
        return False

    def has_feature(self, feature):
        """Check if the feature exists in the features map"""
        return feature in self.features
