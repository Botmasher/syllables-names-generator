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

    # TODO optimize search time - currently exhaustive through all entries no matter what
    def search(self, keywords, max_results=20):
        """Search entry definitions for keyword matches"""
        if not keywords or not isinstance(keywords, (list, tuple, str)):
            print("Dictionary search failed - expected keywords/definition to search for")
            return
        
        # ensure keywords are a traversable sequence
        keywords = keywords.split() if isinstance(keywords, str) else keywords

        scored_matches = []   # list of (headword, entry_index, keywords_score) for relevant matches
        for headword in self.dictionary:
            for entry_index, entry in enumerate(self.dictionary[headword]):
                # definitions are stored under headword entries inside the dictionary
                definition = entry['definition']
                # keep track of keyword matches
                keywords_score = 0
                # simple match - look for single string within definition
                if isinstance(keywords, str):
                    if keywords in definition:
                        keywords_score = 1
                        scored_matches.append((headword, entry_index, keywords_score))
                    continue
                # list match - determine how close the match is
                for keyword in keywords:
                    if keyword in definition:
                        keywords_score += 1
                #  entry if relevant and move to next entry
                keywords_score and scored_matches.append((headword, entry_index, keywords_score))
                continue

        # what if scored_matches len is 0?
        if len(scored_matches) <= 0:
            return scored_matches

        # sort matches by keywords scores (third element in tuple)
        ordered_matches = sorted(scored_matches, key=lambda l: l[2])

        # score and rank relevant matches up to requested limit
        return ordered_matches[:max_results-1]

    def search_sounds(self, ipa="", max_results=10, sound_change=False):
        """Search for headword entries that have the specified pronunciation"""
        if not ipa or type(ipa) is not str:
            print("Dictionary search_sounds failed - invalid pronunciation {0}".format(ipa))
        # list of headword, entry_index tuples
        matches = []
        # search entries for changed sounds instead of underlying sounds
        sound_key = 'change' if sound_change else 'sound'
        # search through all entries to find requested number of sound matches
        for headword in self.dictionary:
            for entry_index in self.dictionary[headword]:
                if ipa == self.dictionary[headword][entry_index][sound_key]:
                    matches.append((headword, entry_index))
                if len(matches) >= max_results-1:
                    return matches
        return matches

    # TODO lookup and store words in list (see comment within .add func)
    #   - ability to filter words by ipa
    #   - ability to filter by keywords in definition
    def lookup(self, headword, entry_index=None):
        """Read all entries (default) or one indexed entry for a spelled word"""
        if not self.is_word(headword):
            print ("Dictionary lookup failed - invalid headword {0}".format(headword))
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

    def add(self, sound="", spelling="", change=None, definition=None, exponent=None):
        """Create a dictionary entry and list it under the spelled headword"""
        # expect both valid spelling and phones
        if not (sound and spelling and isinstance(sound, str) and isinstance(spelling, str)):
            print (f"Dictionary add failed - expected to store both spelling and sound")
            return

        # create an entry
        headword = spelling
        # NOTE: keys created here are accessed throughout class
        entry = {
            # representation of entry in letters
            'spelling': spelling,
            # representation of entry in sounds
            'sound': sound,
            # sound representation after sound changes applied
            'change': change if isinstance(change, str) else "",
            # passed-in definition
            'definition': definition if isinstance(definition, str) else "",
            # reference to exponent id for grammatical entry
            'exponent': exponent
        }
        # structure lists of entries (homographs) per spelling
        self.dictionary.setdefault(headword, []).append(entry)
        # return entry lookup format
        return (headword, len(self.dictionary[headword])-1)

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
            'change': sound_change if sound_change else entry['change'],
            'exponent': entry['exponent']
        }
        return (headword, entry_index)

    def update_spelling(self, headword, new_spelling, entry_index=0):
        """Update the spelling of a single entry (not its headword) and move it under the appropriate headword"""
        if not self.is_entry(headword, index=entry_index):
            print("Dictionary update_spelling failed - invalid entry {0} for headword {1}".format(entry_index, headword))
            return
        # remove the old entry
        old_entry = self.lookup(headword)
        self.remove_entry(headword, entry_index=entry_index)
        # add the new entry
        return self.add(
            spelling=new_spelling,
            sound=old_entry['sound'],
            change=old_entry['change'],
            definition=old_entry['definition'],
            exponent=old_entry['exponent']
        )

    def redefine(self, headword, entry_index=0, definition=""):
        """Change the definition of one entry under a spelled headword"""
        if not self.is_entry(headword, index=entry_index):
            print(f"Dictionary redefine failed - invalid entry {headword}({entry_index})")
            return
        if not isinstance(definition, str):
            print(f"Dictionary redefine failed - invalid definition {definition}")
            return
        self.dictionary[headword][entry_index]['definition'] = definition
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
