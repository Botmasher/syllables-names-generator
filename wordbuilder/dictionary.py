# NOTE a dictionary manages a map of {headword: [entries], } pairs
# - Headwords have a spelling that each entry for a headword shares
# - Each entries list stores entry maps contain spelling, sounds and definition attributes
# - Searching for a single "word" requires passing both a spelled headword and entry index

# TODO: rethink attributes as arrays instead of string
# String vs array:
#   - should noun "ache" vs verb "ache" be separate entries or options under one entry?
#   - what about pronunciation variants of "pecan"?
class Dictionary():
    def __init__(self):
        self.dictionary = {}    # map of headword:[entries]

    def is_word(self, word):
        """Check if entries exist for a spelled word"""
        return word in self.dictionary

    def is_entry(self, word, index=0):
        """Check if an indexed entry exists for the spelled word"""
        return self.is_word(word) and index < len(self.dictionary[word])

    # TODO lookup and store words in list (see comment within .add func)
    #   - ability to filter words by ipa
    #   - ability to filter by keywords in definition
    def lookup(self, headword, entry_index=None):
        """Read all entries (default) or one indexed entry for a spelled word"""
        if not self.is_word(headword):
            print ("Dictionary lookup failed - invalid headword {0}".format(headword, entry_index))
            return
        if not entry_index:
            return self.dictionary[headword]
        return self.dictionary[headword][entry_index]

    def define(self, headword, entry_index=0):
        """Read the definition for a single entry under one headword"""
        if not self.is_entry(headword, index=entry_index):
            print("Dictionary define failed - invalid headword {0} or entry index {1}".format(headword, entry_index))
            return
        return self.dictionary[headword][entry_index]['definition']

    def add(self, spelling="", sound="", definition="", sound_change=""):
        """Create a dictionary entry and list it under the spelled headword"""
        if not (type(spelling) is str and len(spelling) > 0):
            print ("Dictionary add failed - invalid spelling {0}".format(spelling))
            return

        # create an entry
        headword = spelling
        entry = {
            'spelling': spelling,
            'definition': definition if type(definition) is str else "",
            # underlying phonetic representation
            'sound': sound if type(sound) is str else "",
            # phonetic representation after sound changes applied
            'change': sound_change if type(sound_change) is str else ""
        }
        # structure lists of entries (homographs) per spelling
        if not self.is_word(headword):
            self.dictionary[headword] = []
        self.dictionary[headword].append(entry)
        # return all entries - allow caller to see context and calculate index)
        return self.lookup(headword)

    def update(self, headword, entry_index=0, sound="", definition="", sound_change=""):
        """Update any attributes of one entry aside from its spelling"""
        if not self.is_entry(headword, index=entry_index):
            print("Dictionary update failed - invalid entry {0} for headword {1}".format(entry_index, headword))
            return
        # modify entry with any new strings
        entry = self.dictionary[headword][entry_index]
        self.dictionary[headword][entry_index] = {
            'spelling': entry['spelling'],
            'definition': definition if definition else entry['definition'],
            'sound': sound if sound else entry['sound'],
            'change': sound_change if sound_change else entry['change']
        }
        return self.lookup(headword, entry_index=entry_index)

    def update_spelling(self, headword, new_spelling, entry_index=0):
        """Update the spelling of a single entry (not its headword) and move it under the appropriate headword"""
        if not self.is_entry(headword, index=entry_index):
            print("Dictionary update_spelling failed - invalid entry {0} for headword {1}".format(entry_index, headword))
            return
        # remove the old entry
        old_entry = self.lookup(headword)
        self.remove_entry(headword, entry_index=entry_index)
        # add the new entry
        self.add(
            spelling=new_spelling,
            sound=old_entry['sound'],
            definition=old_entry['definition'],
            change=old_entry['change']
        )
        return self.lookup(new_spelling)

    def redefine(self, headword, entry_index=0, definition=""):
        """Change the definition of one entry under a spelled headword"""
        if not self.is_entry(headword, index=entry_index):
            print("Dictionary redefine failed - invalid headword {0}".format(headword))
            return
        if type(definition) is not str:
            print("Dictionary redefine failed - invalid definition {0}".format(definition))
            return
        self.dictionary[headword][entry_index]['definition'] = definition
        return self.lookup(headword, entry_index=entry_index)

    # TOODO remove - handled by update method
    def change_sound(self, headword, entry_index=0, sound="", sound_change=""):
        """Modify the sound representation or sound change representation for one entry"""
        if not self.is_entry(headword, index=entry_index) or type(sound) is not str or type(sound_change) is not str:
            print("Dictionary change_sound failed - invalid headword {0}, entry {1}, sound string {2}, or sound change string {3}".format(headword, entry_index, sound, sound_change))
            return
        self.dictionary[headword][entry_index]['sound'] = sound
        self.dictionary[headword][entry_index]['change'] = sound_change
        return self.lookup(headword, entry_index=entry_index)

    def remove_entry(self, headword, entry_index=0):
        """Remove a single entry in the array of entries for the headword"""
        if not self.is_entry(headword, index=entry_index):
            print("Dictionary remove failed to find entry {0} for headword {1}".format(entry_index, headword))
            return
        return self.dictionary[headword].pop(entry_index)

    def remove_headword(self, headword):
        """Remove one spelled word key and its entire array of entries from the dictionary"""
        if not self.is_word(headword):
            print("Dictionary remove failed - unknown headword {0}".format(headword))
            return
        return self.dictionary.pop(headword)
