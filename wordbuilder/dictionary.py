class Dictionary():
    def __init__(self):
        self.dictionary = {}

    def is_word(self, word):
        """Check if entries exist for a spelled word"""
        return word in self.dictionary

    def add(self, spelling="", sound="", definition="", sound_change=""):
        """Create a dictionary entry for a single word"""
        # create an entry
        entry = {
            'spelling': spelling if type(spelling) is str else "",
            'definition': definition if type(definition) is str else "",
            # underlying phonetic representation
            'sound': sound if type(sound) is str else "",
            # phonetic representation after sound changes applied
            'change': sound_change if type(sound_change) is str else ""
        }
        # TODO support structuring values as lists of entries (homographs) per spelling
        # if not self.is_word(word):
        #     self.dictionary[spelling] = [entry]
        # else:
        #     self.dictionary[spelling].append(entry)
        self.dictionary[spelling] = entry
        return self.dictionary[spelling]

    def update(self, spelling="", sound="", definition="", sound_change=""):
        if not self.is_word(spelling):
            return
        self.dictionary[spelling] = {
            'spelling': spelling,
            'definition': definition if definition else self.dictionary[spelling]['definition'],
            'sound': sound if sound else self.dictionary[spelling]['sound'],
            'change': sound_change if sound_change else self.dictionary[spelling]['change']
        }
        return self.dictionary[spelling]

    # TODO lookup and store words in list (see comment within .add func)
    #   - ability to filter words by ipa
    #   - ability to filter by keywords in definition
    def lookup(self, headword):
        if not self.is_word(headword):
            return
        return self.dictionary[headword]

    def define(self, headword):
        if not self.is_word(headword):
            return
        return self.dictionary[headword]['definition']

    def redefine(self, headword, definition=""):
        if not self.is_word(headword) or type(definition) is not str:
            return
        self.dictionary[headword]['definition'] = definition
        return self.dictionary[headword]

    def change_sound(self, headword, sound="", sound_change=""):
        if not self.is_word(headword) or type(sound) is not str or type(sound_change) is not str:
            return
        self.dictionary[headword]['sound'] = sound
        self.dictionary[headword]['change'] = sound_change
        return self.dictionary[headword]
