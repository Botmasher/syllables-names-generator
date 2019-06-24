from ..tools import string_list
from ..tools import flat_list

# NOTE a dictionary manages a map of {headword: [entries], } pairs
# - Headwords have a spelling that each entry for a headword shares
# - Each entries list stores entry maps contain spelling, sounds and definition attributes
# - Searching for a single "word" requires passing both a spelled headword and entry index

# TODO: consider attributes as arrays of options
# String vs array:
#   - should noun "ache" vs verb "ache" be separate entries or options under one entry?
#   - what about pronunciation variants of "pecan"?
#   - currently multiple options have to exist as separate entries
class Dictionary():
    def __init__(self, grammar, phonology, affix_symbol, spacing_symbol):
        self.dictionary = {}        # map of headword:[entries]
        self.grammar = grammar      # reference to language grammar for exponent data
        self.phonology = phonology  # reference to phonology for sound change and spelling
        # special characters
        self.affix_symbol = affix_symbol
        self.spacing_symbol = spacing_symbol

    def is_word(self, word):
        """Check if entries exist for a spelled word"""
        return word in self.dictionary

    def is_entry(self, word, index=0):
        """Check if an indexed entry exists for the spelled word"""
        return self.is_word(word) and index < len(self.dictionary[word])

    # TODO: intersect matches from multiple attributes
    # TODO: exact match (see _search_definitions)
    def search(self, spelling="", keywords="", sound="", change="", exact=False, max_results=10):
        """Search dictionary for entries with a matching attribute. Only one attribute
        is searched per call."""
        #if not spelling and not keywords and not sound and not change:        
        #    raise ValueError("Dictionary search missing one or more values to search for")

        # TODO: matches for exponents
        matches = []
        for headword, entries in self.dictionary:
            for entry, i in entries.items():
                if entry['exponent']:
                    match['spelling'] = []
                    match['sound'] = []
                    match['change'] = []
                    match['definition'] = entry['definition']
                else:
                    match = dict(entry)
                did_match = True
                if sound and sound != match['sound']:
                    did_match = False
                if spelling and spelling != match['spelling']:
                    did_match = False
                if change and change != match['change']:
                    did_match = False
                if keywords and list(filter(lambda w: w not in match['definition'], keywords)):
                    did_match = False
                if did_match:
                    matches.append((headword, i))
                if len(matches) >= max_results:
                    return matches
        return matches

        # if spelling:
        #     return self._search_spellings(spelling, max_results=max_results)
        # if keywords:
        #     return self._search_definitions(keywords, exact=exact, max_results=max_results)
        # if change:
        #     return self._search_sounds(change, sound_change=True, max_results=max_results)
        # if sound:
        #     return self._search_sounds(sound, sound_change=False, max_results=max_results)
    
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
        for headword in self.dictionary:
            for entry_index, entry in enumerate(self.dictionary[headword]):
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

    def _search_sounds(self, ipa, max_results=10, sound_change=False):
        """Search for headword entries that have the specified pronunciation"""
        # ensure spelling is a list of strings
        sounds = string_list.string_listify(ipa, True)
        if not string_list.is_string_list(sounds):
            print(f"Dictionary search failed - invalid ipa {ipa}")
       
        # list of headword, entry_index tuples
        matches = []
        
        # search entries for changed sounds instead of underlying sounds
        sound_key = 'change' if sound_change else 'sound'
        # search through all entries to find requested number of sound matches
        for headword in self.dictionary:
            for entry_index in self.dictionary[headword]:
                if sounds == self.dictionary[headword][entry_index][sound_key]:
                    matches.append((headword, entry_index))
                if len(matches) >= max_results-1:
                    return matches
        return matches

    def _search_spellings(self, spelling, max_results=10):
        """Search for headword entries that have the given spelling"""
        # ensure spelling is a list of strings
        spelling = string_list.string_listify(spelling, True)
        
        # store lookups for exact spelling matches
        matches = [
            [
                (headword, i)
                for i, entry in enumerate(entries)
                if spelling == entry['spelling']
            ]
            for headword, entries in self.dictionary.items()
        ]

        matches = flat_list.flatten(matches, depth = 1)

        # TODO: inexact search
        # matches = []
        # # traverse dictionary for matching spellings
        # for headword, entries in self.dictionary.items():
        #     # add references to all subentries with this spelling
        #     if spelling == headword:
        #         map(lambda i: matches.append((headword, i)), range(len(entries)))
        #     # send back matches at match limit
        #     if len(matches) >= max_results:
        #         break
        
        # send back matches cut at requested results count
        return matches[:max_results]

    def lookup(self, headword, entry_index=None):
        """Read all entries (default) or one indexed entry for a spelled word"""
        if not self.is_word(headword):
            print (f"Dictionary lookup failed - unknown or invalid headword {headword}")
            return
        if entry_index is None:
            return self.dictionary[headword]
        return self.dictionary[headword][entry_index]

    def define(self, headword, entry_index=0):
        """Read the definition for a single entry under one headword"""
        if not self.is_entry(headword, index=entry_index):
            print("Dictionary define failed - invalid headword {0} or entry index {1}".format(headword, entry_index))
            return
        return self.dictionary[headword][entry_index]['definition']

    # TODO: access exponent information through Grammar instead of
    # heavily formatting pre,mid,post here or when calling this method
    #   - also define when accessed instead of stored?
    #   - go through exponent entries when using search
    def _lookup_exponent(self, exponent_id):
        return self.grammar.exponents.get(exponent_id)

    def _format_exponent_entry(self, exponent_id):
        exponent_details = self._lookup_exponent(exponent_id)
        exponent_entry = {
            'sound': [],
            'change': [],
            'spelling': []
        }
        return exponent_entry

    def _display_exponent_pieces(self, pre, mid, post, bound=True):
        """Format grammatical pieces of one exponent into a single human
        readable string ready to display."""
        
        # create list of exponent pieces with separators
        display_list = []
        # pre/circum material
        display_list += pre
        if pre:
            if bound:
                display_list += [self.affix_symbol]
            display_list += [self.spacing_symbol]
        # mid/infix material
        if mid and bound:
            display_list += [self.affix_symbol]
        display_list += mid
        if mid:
            if bound:
                display_list += [self.affix_symbol]
            display_list += [self.spacing_symbol]
        # post/circum material
        if post and bound:
            display_list += [self.affix_symbol]
        display_list += post

        # remove excess spacing
        if display_list[0] == self.spacing_symbol:
            display_list = display_list[1:]
        if display_list[-1] == self.spacing_symbol:
            display_list = display_list[:-1]
        
        return display_list

    def add(self, sound=None, spelling=None, change=None, definition=None, exponent=None, pos=None):
        """Create a dictionary entry and list it under the spelled headword"""
        # expect both valid spelling and phones
        if not (sound and spelling) and not exponent:
            print (f"Dictionary add failed - expected both spelling and sound or an exponent reference")
            return

        # ensure sound and spelling are lists of strings
        spelling = string_list.string_listify(spelling, True)
        sound = string_list.string_listify(sound, True)
        if not string_list.is_string_list(spelling) and not exponent:
            print(f"Dictionary add failed - invalid spelling {spelling}")
        if not string_list.is_string_list(sound) and not exponent:
            print(f"Dictionary add failed - invalid sounds {sound}")

        # Create an entry
        headword = "".join(spelling)

        # build headword key from entry spelling
        if exponent:
            # combine grammatical material and format into
            # TODO: either use post_change spelling here or handle inside Grammar 
            exponent_details = self.grammar.exponents.get(exponent)
            pre_spelling = self.phonology.spell(exponent_details['pre'])
            mid_spelling = self.phonology.spell(exponent_details['mid'])
            post_spelling = self.phonology.spell(exponent_details['post'])
            headword = self._display_exponent_pieces(pre_spelling, mid_spelling, post_spelling, exponent_details['bound'])
            # clear out details to rely on grammatical exponents data on fetch
            spelling = ""
            sound = ""
            change = ""
        else:
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
            # reference to exponent id for grammatical entry
            'exponent': exponent,
            # word class / part of speech
            'pos': pos
        }
        # structure lists of entries (homographs) per spelling
        self.dictionary.setdefault(headword, []).append(entry)
        # return entry lookup format
        return (headword, len(self.dictionary[headword])-1)

    def update(self, headword, entry_index=0, spelling="", sound="", change="", definition="", exponent="", pos=""):
        """Update any attributes of one entry. Updating spelling moves the dictionary entry.
        Updating any other attribute modifies the entry in place.
        NOTE: directly mutates values generated by the language!
        """
        if not self.is_entry(headword, index=entry_index):
            print("Dictionary update failed - invalid entry {0} for headword {1}".format(entry_index, headword))
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
            'exponent': exponent,
            'pos': pos
        }
        # new entry layering over modifications
        modified_entry = {
            **self.dictionary[headword][entry_index],
            **{k: v for k, v in modified_attributes.items() if v}
        }

        # move respelled entry within dictionary
        if spelling:
            self.dictionary.setdefault(spelling, []).append(modified_entry)
            self.dictionary[headword][entry_index] = None
        # replace same-spelling entry
        else:
            self.dictionary[headword][entry_index] = modified_entry

        return ((spelling, headword)[not spelling], entry_index)

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
            exponent=old_entry['exponent'],
            pos=old_entry['pos']
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
