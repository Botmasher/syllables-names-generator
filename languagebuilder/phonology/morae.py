class Morae:
    def __init__(self, phonology):
        self.phonology = phonology
        self.morae = {}     # map of morae counts

    def set_mora(self, sounds_or_features, count=1, overwrite=False):
        vetted_mora = []
        for features in sounds_or_features:
            # TODO: use special abbrevs data not hardcoded ones
            if features == "C":
                vetted_mora.append(["consonant"])
            elif features == "V":
                vetted_mora.append(["vowel"])
            elif self.phonology.has_sound(features):
                vetted_mora.append(self.phonology.phonetics.get_features(features))
            else:
                vetted_features = self.phonology.phonetics.parse_features(features)
                if not vetted_features:
                    return
                vetted_mora.append(vetted_features)
        if not overwrite and self.morae.get(vetted_mora):
            return
        self.morae[vetted_mora] = count
        return self.morae[count]

    def count_morae(self, sounds):
        morae_features = [
            self.phonology.phonetics.parse_features(sound)
            for sound in sounds
        ]
        current_mora = []
        count = 0
        for features in morae_features:
            current_mora.append(features)
            # TODO: check for existence of any subset of features in dict lists
            if self.morae.get(current_mora):
                count += 1
                current_mora = []
        if current_mora:
            return
        return count
    