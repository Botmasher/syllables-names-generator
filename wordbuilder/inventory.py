# TODO handle syllables separately
class Inventory:
    def __init__(self):
        self.ipa = set()
        self.ipa_by_feature = {}
        self.symbol_length_limit = 4

    def get(self, ipa="", features=[]):
        """Find a phonetic symbol from its features or features for a symbol"""
        if ipa and type(ipa) is str and not features:
            return self.get_features(ipa)
        elif features and not ipa:
            return self.get_ipa(features=features)
        else:
            print("Inventory get failed - invalid symbol {0} or features {1}".format(ipa, features))
            return

    def get_ipa(self, features=[]):
        """Find every phonetic symbol that has the given features"""
        if type(features) is str:
            feature = features
            if feature in self.ipa_by_feature:
                return list(self.ipa_by_feature[feature])
            else:
                print("Inventory get_ipa failed - unknown feature {0}".format(feature))
                return []

        # reduce to set of found letters
        matching_letters = set()
        for i in range(len(features)):
            feature = features[i]
            if feature not in self.ipa_by_feature:
                print("Inventory get_ipa failed - unknown feature {0}".format(feature))
                return []
            if i == 0:
                matching_letters = self.ipa_by_feature[feature]
                continue
            matching_letters &= self.ipa_by_feature[feature]

        return list(matching_letters)

    def get_features(self, letter):
        """Read all features associated with a single phonetic symbol"""
        matching_features = []
        for feature in self.ipa_by_feature:
            if letter in self.ipa_by_feature[feature]:
                matching_features.append(feature)
        return matching_features

    def _add_unique(self, symbol, feature):
        """Private add unique phonetic symbol to map of symbols by features"""
        if not (type(symbol) is str and type(feature) is str):
            return
        if feature not in self.ipa_by_feature:
            self.ipa_by_feature[feature] = set()
        if symbol not in self.ipa_by_feature[feature]:
            self.ipa_by_feature[feature].add(symbol)
        return self.ipa_by_feature[feature]

    def add(self, symbol="", features=[]):
        """Store a new phonetic symbol with features"""
        if not symbol or type(symbol) is not str or len(symbol) > self.symbol_length_limit:
            print("Inventory add_ipa failed - invalid phonetic symbol {0}".format(symbol))
            return
        for feature in features:
            if not self._add_unique(symbol, feature):
                print("Inventory add_ipa failed - unknown feature {0}".format(feature))
                # TODO wipe letter from letters data
                # self.remove_letter(letter) # also remove feature if no letters left
                return
        self.ipa.add(symbol)
        return {symbol: self.get_features(symbol)}

    def remove(self, symbol):
        """Remove a phonetic symbol and its feature associations from the inventory"""
        if symbol not in self.ipa:
            print("Inventory remove failed - phonetic symbol {0} not found".format(symbol))
            return
        for feature in self.ipa_by_feature:
            if symbol in self.ipa_by_feature[feature]:
                self.ipa_by_feature[feature].remove(symbol)
        self.ipa.remove(symbol)
        return self.ipa

    def reset(self, symbol, new_features):
        """Update all features associated with a single phonetic symbol"""
        if symbol not in self.ipa:
            print("Inventory reset failed - phonetic symbol {0} not found".format(letter))
            return
        for feature, symbols in self.ipa_by_feature.items():
            symbol in symbols and self.ipa_by_feature[feature].remove(symbol)
            feature in new_features and self.ipa_by_feature[feature].add(symbol)
        return {symbol: self.get_features(symbol)}

    def get_syllables(self):
        """Read all syllables listed in the inventory"""
        return list(self.syllables)

    def add_syllable(self, syllable):
        """Add a syllable structure to the inventory syllables collection"""
        if type(syllable).__name__ == 'Syllable' and syllable not in self.syllables:
            self.syllables.add(syllable)
        return self.syllables

    def remove_syllable(self, syllable):
        """Remove a syllable structure from the inventory syllables collection"""
        if syllable in self.syllables:
            self.syllables.remove(syllable)
        return self.syllables
