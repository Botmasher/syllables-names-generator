from collector import Collector

# TODO separate phonemes/letters/weights (language) from ipa-features (features) - do not handle features here!
class Phonemes(Collector):
    def __init__(self):
        Collector.__init__(self, accepted_types=['Phoneme'])
        self.ipa_by_feature = {}

    def add(self, phoneme, features):
        if not type(phoneme).__name__ == 'Phoneme':
            return("Phonemes add failed - invalid phoneme {0}".format(phoneme))
        ipa = phoneme.get_symbol()
        for feature in features:
            if feature not in self.ipa_by_feature:
                self.ipa_by_feature[feature] = set()
            self.ipa_by_feature[feature].add(ipa)
        super(Phonemes, self).add(phoneme, key=ipa)

    def get_symbol(self, ipa):
        phoneme = self.get(key=ipa)
        if not phoneme:
            print("Phonemes get_symbol failed - unknown phoneme {0}".format(phoneme))
            return
        return phoneme.get_symbol()

    def get_letters(self, ipa):
        phoneme = self.get(key=ipa)
        if not phoneme:
            print("Phonemes get_letters failed - unknown phoneme {0}".format(phoneme))
            return
        return phoneme.get_letters()

    def get_weight(self, ipa):
        phoneme = self.get(key=ipa)
        if not phoneme:
            print("Phonemes get_weight failed - unknown phoneme {0}".format(phoneme))
            return
        return phoneme.get_weight()

    def get_ipa(self, features):
        """Find every phonetic symbol that has the given features"""
        if type(features) is str:
            feature = features
            if feature in self.ipa_by_feature:
                return list(self.ipa_by_feature[feature])
            else:
                print("Inventory get_ipa failed - unknown feature {0}".format(feature))
                return []

        # reduce to set of found letters
        matching_ipa = set()
        for i in range(len(features)):
            feature = features[i]
            if feature not in self.ipa_by_feature:
                print("Inventory get_ipa failed - unknown feature {0}".format(feature))
                return []
            if i == 0:
                matching_ipa = self.ipa_by_feature[feature]
                continue
            matching_ipa &= self.ipa_by_feature[feature]

        return list(matching_ipa)

    def get_features(self, ipa):
        """Read all features associated with a single phonetic symbol"""
        matching_features = []
        for feature in self.ipa_by_feature:
            if ipa in self.ipa_by_feature[feature]:
                matching_features.append(feature)
        return matching_features
