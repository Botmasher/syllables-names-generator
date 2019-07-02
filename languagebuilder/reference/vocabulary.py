from ..tools import string_list
from ..tools import flat_list

# NOTE: vocabulary manages a map of {headword: [entries], }
# - Headwords have a spelling that each entry for a headword shares
# - Each entries list stores entry maps contain spelling, sounds and definition attributes
# - Searching for a single "word" requires passing both a spelled headword and entry index

# NOTE: exponents no longer stored in Vocabulary (see: Summary)
#   - vocabulary defines and gives sounds, spellings for headwords
#   - grammatical pieces are meant to be used alongside base headwords

# TODO: consider attributes as arrays of options
# String vs array:
#   - should noun "ache" vs verb "ache" be separate entries or options under one entry?
#   - what about pronunciation variants of "pecan"?
#   - currently multiple options have to exist as separate entries
class Vocabulary():
    def __init__(self):
        self.vocabulary = {}         # map of headword:[entries]

    def is_word(self, word):
        """Check if entries exist for a spelled word"""
        return word in self.vocabulary

    def is_entry(self, word, index=0):
        """Check if an indexed entry exists for the spelled word"""
        return self.is_word(word) and index < len(self.vocabulary[word])

    # TODO: exact match (see _search_definitions)
    def search(self, spelling=None, keywords=None, sound=None, change=None, exact=False, max_results=10):
        """Search dictionary for entries with matching attributes. If only keywords are
        supplied, look for relevant definitions. Otherwise, attempt to find entries with
        all supplied attributes."""
        if not spelling and not keywords and not sound and not change:        
            raise ValueError("Dictionary search missing one or more values to search for")
        
        # sorted matches after searching relevant definitions
        matching_definitions = self._search_definitions(
            keywords,
            exact=exact,
            max_results=max_results
        ) if keywords else None
        # return definition matches if not searching for sounds or spelling
        if keywords and not spelling and not sound and not change:
            return matching_definitions

        # list sequences of letters and sounds
        spelling = string_list.string_listify(spelling) if spelling else []
        sound = string_list.string_listify(sound) if sound else []
        change = string_list.string_listify(change) if change else []

        # start with definition matches if keywords supplied otherwise search all entries
        searched_vocabulary = matching_definitions if matching_definitions else self.vocabulary

        # build and return a list of matching word entries
        matches = []
        for headword, entries in searched_vocabulary:
            for entry, i in entries.items():
                compared = {
                    'sound': not sound or sound == entry['sound'],
                    'change': not change or change == entry['change'],
                    'spelling': not spelling or spelling == entry['spelling']
                }
                if False not in compared.values():
                    matches.append((headword, i))
                if len(matches) >= max_results:
                    return matches
        return matches

    def _search_definitions(self, keywords, exact=False, max_results=10):
        """Search entry definitions for keyword matches"""
        # check for valid keywords
        if not isinstance(keywords, (list, tuple, str)):
            print("Dictionary search failed - expected list of keywords to search for in definitions")
            return
        
        # ensure keywords are a traversable sequence
        keywords = keywords.split() if isinstance(keywords, str) else keywords

        # list of (headword, entry_index, keywords_score) for relevant matches
        scored_matches = []

        # traverse entries searching for relevant matches
        for headword in self.vocabulary:
            for entry_index, entry in enumerate(self.vocabulary[headword]):
                # definitions are stored under headword entries inside the dictionary
                definition = entry['definition']
                # keep track of keyword matches
                keywords_score = 0

                # NOTE: string searches are currently split into 
                # # simple match - look for single string within definition
                # if isinstance(keywords, str):
                #     if keywords in definition:
                #         keywords_score = 1
                #         scored_matches.append((headword, entry_index, keywords_score))
                #     continue

                # list match - determine how close the match is
                for keyword in keywords:
                    if keyword in definition:
                        keywords_score += 1
                #  entry if relevant and move to next entry
                if keywords_score:
                    scored_matches.append((headword, entry_index, keywords_score))

                # stop searching when max results found
                if len(scored_matches) >= max_results:
                    break
            if len(scored_matches) >= max_results:
                break

        # hand back matches sorted by keywords score (third element in tuple)
        sorted_matches = sorted(scored_matches, key=lambda l: l[2])
        # strip weights and return (headword,entry_index) lookup pairs
        return [(match[0], match[1]) for match in sorted_matches]

    # TODO: update sound/spell search to account for storage in lists
    # - Phonology and Grammar now build word, unit lists not simple strings

    def lookup(self, headword, entry_index=None):
        """Read all entries (default) or one indexed entry for a spelled word"""
        if not self.is_word(headword):
            print (f"Dictionary lookup failed - unknown or invalid headword {headword}")
            return
        if entry_index is None:
            return self.vocabulary[headword]
        return self.vocabulary[headword][entry_index]

    def define(self, headword, entry_index=0):
        """Read the definition for a single entry under one headword"""
        if not self.is_entry(headword, index=entry_index):
            print(f"Failed to define invalid headword {headword} with entry index {entry_index}")
            return
        return self.vocabulary[headword][entry_index]['definition']

    def add(self, sound=None, spelling=None, change=None, midpoint=None, definition=None, pos=None):
        """Create a dictionary entry and list it under the spelled headword"""
        # expect both valid spelling and phones
        if not (sound and spelling):
            print (f"Add failed - expected both spelling and sound")
            return

        # ensure sound and spelling are lists of strings
        spelling = string_list.string_listify(spelling, True)
        sound = string_list.string_listify(sound, True)
        if not string_list.is_string_list(spelling):
            print(f"Dictionary add failed - invalid spelling {spelling}")
        if not string_list.is_string_list(sound):
            print(f"Dictionary add failed - invalid sounds {sound}")

        # Create an entry
        headword = "".join(spelling)

        # build headword key from entry spelling
        headword = "".join(spelling)

        entry = {
            # representation of entry in letters
            'spelling': spelling,
            # representation of entry in sounds
            'sound': sound,
            # sound representation after sound changes applied
            'change': change if isinstance(change, str) else "",
            # passed-in definition
            'definition': definition if isinstance(definition, str) else "",
            # place where word may be split (used for infixes)
            'midpoint': midpoint if isinstance(midpoint, int) and midpoint < len(sound) else None,
            # word class / part of speech
            'pos': pos
        }
        # structure lists of entries (homographs) per spelling
        self.vocabulary.setdefault(headword, []).append(entry)
        # return entry lookup format
        return (headword, len(self.vocabulary[headword])-1)

    def update(self, headword, entry_index=0, spelling="", sound="", change="", definition="", midpoint=None, pos=""):
        """Update any attributes of one entry. Updating spelling moves the dictionary entry.
        Updating any other attribute modifies the entry in place.
        NOTE: directly mutates values generated by the language!
        """
        if not self.is_entry(headword, index=entry_index):
            print(f"Update failed - invalid entry {headword},{entry_index}")
            return
        
        # ensure sounds and spelling are lists of strings
        if sound:
            sound = string_list.string_listify(sound, True)
        if spelling:
            spelling = string_list.string_listify(spelling, True)
        if change:
            change = string_list.string_listify(change, True)
    
        # modifications adding any new strings
        modified_attributes = {
            'spelling': spelling,
            'definition': definition,
            'sound': sound,
            'change': change,
            'midpoint': midpoint,
            'pos': pos
        }
        # new entry layering over modifications
        modified_entry = {
            **self.vocabulary[headword][entry_index],
            **{k: v for k, v in modified_attributes.items() if v}
        }

        # move respelled entry within dictionary
        if spelling:
            self.vocabulary.setdefault(spelling, []).append(modified_entry)
            self.vocabulary[headword][entry_index] = None
        # replace same-spelling entry
        else:
            self.vocabulary[headword][entry_index] = modified_entry

        return ((spelling, headword)[not spelling], entry_index)

    def update_spelling(self, headword, new_spelling, entry_index=0):
        """Update the spelling of a single entry (not its headword) and move it under the appropriate headword"""
        if not self.is_entry(headword, index=entry_index):
            print(f"Failed to update spelling - invalid entry {headword},{entry_index}")
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
            pos=old_entry['pos']
        )

    def redefine(self, headword, entry_index=0, definition=""):
        """Change the definition of one entry under a spelled headword"""
        if not self.is_entry(headword, index=entry_index):
            print(f"Redefine failed - invalid entry {headword}({entry_index})")
            return
        if not isinstance(definition, str):
            print(f"DRedefine failed - invalid definition {definition}")
            return
        self.vocabulary[headword][entry_index]['definition'] = definition
        return self.lookup(headword, entry_index=entry_index)

    def remove_entry(self, headword, entry_index=0):
        """Remove a single entry in the array of entries for the headword"""
        if not self.is_entry(headword, index=entry_index):
            print(f"Remove failed - unrecognized entry index {entry_index} for headword {headword}")
            return
        return self.vocabulary[headword].pop(entry_index)

    def remove_headword(self, headword):
        """Remove one spelled word key and its entire array of entries from
        the vocabulary"""
        if not self.is_word(headword):
            print(f"Remove - unknown headword {headword}")
            return
        return self.vocabulary.pop(headword)
