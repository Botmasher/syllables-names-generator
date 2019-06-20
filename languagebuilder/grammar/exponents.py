from uuid import uuid4
from ..tools.functional_maps import merge_maps

# TODO: consider "exponent" name
#   - in linguistics may be used for expression of grammatical properties or even linguistic phenomena (like semantics)
#   - more commonly recognized as a mathematical term
#   - idiosyncratic here since just bundles adpositional and affixal elements

class Exponents:
    def __init__(self, grammar):
        # grammar for which exponents provide properties and word classes
        # used to verify category:grammemes and parts of speech (read only)
        self.grammar = grammar
        # exponents collection managed throughout this class
        self.exponents = {}

    def get(self, exponent_id=None):
        """Read exponent details for one entry (or all if none specified) in the exponents map"""
        if not exponent_id:
            return self.exponents
        return self.exponents.get(exponent_id)

    def get_keys(self):
        """Fetch all exponent ids from the grammatical exponents map"""
        return self.exponents.keys()

    def get_values(self):
        """Fetch all exponent details from the grammatical exponents map"""
        return self.exponents.values()

    def get_items(self):
       """Fetch all exponent ids and details from the grammatical exponents map"""
       return self.exponents.items()

    def exists(self, pre=None, mid=None, post=None):
        """Check if the given sounds are an exponent in this grammar"""
        # check for pre or post material
        if not (pre or mid or post):
            print("Exponents exists failed - expected pre or post list or string")
            return

        # turn pre and post strings into list of ipa
        searched_details = {
            'pre': list(pre) if pre else [],
            'mid': list(mid) if mid else [],
            'post': list(post) if post else []
        }
        # search details for pre/post matches
        for exponent_details in self.exponents.values():
            common_details = {
                k: v for k, v in searched_details.items()
                if v == exponent_details[k]
            }
            if searched_details == common_details:
                return True
            # # circumfix or circumposition
            # if exponent_details['pre'] and exponent_details['post'] and pre == exponent_details['pre'] and post == exponent_details['post']:
            #     return True
            # # prefix or preposition
            # if exponent_details['pre'] and pre == exponent_details['pre']:
            #     return True
            # # suffix or postposition
            # if exponent_details['post'] and post == exponent_details['post']:
            #     return True
        return False

    # NOTE: added exponent['properties'] details expect this structure:
    # {
    #   category: {grammeme, ...},     # grammemes set NOT dict of value:details pairs as in self.properties
    #   category: 'grammeme'           # a single string is also allowed
    #   ...
    # }
    # NOTE: other language methods expect pre, post lists of ipa not string
    def add(self, pre=None, mid=None, post=None, bound=True, properties=None, pos=None):
        """Add one grammatical exponent to the grammar. This exponent has pre or post
        material (or both), is affixed or free, provides properties and optionally
        is restricted to specific parts of speech."""

        # turn pre and post strings into list of ipa; leave string lists alone
        vetted_pre = self.vet_input(pre)
        vetted_mid = self.vet_input(mid)
        vetted_post = self.vet_input(post)

        # ensure exponent has either valid pre or post material
        if not (vetted_pre or vetted_mid or vetted_post):
            raise ValueError("Exponents add failed - expected pre, mid or post material")

        # vet and check provided grammatical properties
        parsed_properties = self.grammar.parse_properties(properties) if isinstance(properties, str) else properties
        if not parsed_properties or not isinstance(parsed_properties, dict):
            raise TypeError("Exponents add failed - expected valid properties map or string")

        # collect valid word classes to include or exclude when property is applied
        recognized_word_classes = self.grammar.word_classes.filter(pos)

        # vet the categories and values of provided properties
        recognized_properties = self.grammar.properties.filter(parsed_properties)
        
        # back out of add if no recognized properties provided by exponent
        if not recognized_properties:
            print(f"Exponents add failed - invalid properties {parsed_properties}")
            return
        
        # store exponent details
        exponent_id = f"grammatical-exponent-{uuid4()}"
        self.exponents[exponent_id] = {
            'id': exponent_id,
            'pre': vetted_pre,
            'mid': vetted_mid,
            'post': vetted_post,
            'bound': bound,
            'properties': recognized_properties,
            'pos': recognized_word_classes
        }
        return exponent_id

    def add_many(self, exponents_details):
        """Add a list of grammatical exponents with properties"""
        if not isinstance(exponents_details, list):
            print(f"Exponents add_many failed - invalid list of exponents {exponents_details}")
            return
        # prepare to store ids of created exponents
        exponent_ids = []
        # shape and store details
        for exponent in exponents_details:
            # verify expected details for an exponent
            # NOTE: not all-or-nothing add, log skipped exponents to console
            if not isinstance(exponent, dict) or not {'pre', 'mid', 'post'} & exponent.keys() or 'properties' not in exponent:
                print(f"Exponents add_many skipped invalid exponent dict {exponent}")
                continue
            # shape new details layering default values over missing details
            new_exponent_details = merge_maps({
                'pre': [],
                'mid': [],
                'post': [],
                'bound': True,
                'pos': set()
            }, exponent)
            # create an exponent entry using the new details
            exponent_id = self.add(
                pre=new_exponent_details['pre'],
                mid=new_exponent_details['mid'],
                post=new_exponent_details['post'],
                bound=new_exponent_details['bound'],
                properties=new_exponent_details['properties'],
                pos=new_exponent_details['pos']
            )
            # keep references to successful exponents
            exponent_id and exponent_ids.append(exponent_id)
        return exponent_ids

    def update(self, exponent_id, pre=None, mid=None, post=None, bound=None, properties=None, pos=None):
        """Modify the basic details of one grammatical exponent"""
        # check that the exponent exists
        if exponent_id not in self.exponents:
            print(f"Exponents.update failed - unknown exponent id {exponent_id}")
            return
        
        # treat incoming strings as sound sequences
        vetted_pre = self.vet_input(pre)
        vetted_mid = self.vet_input(mid)
        vetted_post = self.vet_input(post)
        
        # only modify bound flag if provided
        vetted_bound = bound if isinstance(bound, bool) else None

        # store existing parts of speech for this exponent
        recognized_word_classes = self.grammar.word_classes.filter(pos) if pos else None

        # filter requested category, values sets through the existing properties
        recognized_properties = self.grammar.properties.filter(properties) if properties else None

        # create new entry with non-empty details overlayed onto existing ones
        updated_exponent_details = merge_maps(
            self.exponents[exponent_id],
            {
                'pre': vetted_pre,
                'mid': vetted_mid,
                'post': vetted_post,
                'bound': vetted_bound,
                'properties': recognized_properties,
                'pos': recognized_word_classes
            }
        )
        # assign the existing exponent to point to the new details
        self.exponents[exponent_id] = updated_exponent_details
        return exponent_id

    def vet_input(self, raw_material):
        """Ensure exponent material has the expected type and structure,
        including turning a string into a list of sounds."""
        # invalid sound collection
        if not raw_material or not isinstance(raw_material, (list, tuple, str)):
            return []
        # flat list of sound strings
        return list(filter(lambda s: isinstance(s, str), list(raw_material)))

    def remove(self, exponent_id):
        """Delete the record for one exponent and return a copy of the details"""
        return self.exponents.pop(exponent_id, None)   
    
    # Specific exponent attribute updates and removals

    def add_pos(self, exponent_id, pos):
        """Add one included or excluded word class to the grammatical property"""
        # check that the exponent exists and that there is a part of speech to add
        if exponent_id not in self.exponents:
            print(f"Exponents add_pos failed - unknown exponent {exponent_id}")
            return
        if not self.grammar.word_classes.get(pos):
            print(f"Exponents add_pos failed - expected an existing word class not {pos}")
            return

        # add verified part of speech to exponent word class set
        self.exponents[exponent_id]['pos'].add(pos)
        
        return self.exponents[exponent_id]

    def remove_pos(self, exponent_id, pos):
        """Remove one included or excluded word class from the grammatical property"""
        # check for the property
        if exponent_id not in self.exponents:
            print(f"Exponents remove_pos failed - unknown exponent {exponent_id}")
            return

        # remove word class from exponent parts of speech
        pos and self.exponents[exponent_id]['pos'].discard(pos)
        
        # return the exponent details
        return self.exponents[exponent_id]

    def replace_pos(self, exponent_id, pos=None):
        """Update the included or excluded word classes for a property"""
        # verify that the property exists
        if exponent_id not in self.exponents:
            print(f"Exponents replace_pos failed - unknown exponent {exponent_id}")
            return
        # check for valid include and exclude part of speech lists
        if not pos or not isinstance(pos, (list, tuple, set)):
            print(f"Exponents replace_pos failed - invalid include pos list {pos}")
            return

        # collect only recognized parts of speech
        recognized_word_classes = self.grammar.word_classes.filter(pos)

        # store word classes
        merge_maps(
            self.exponents[exponent_id],
            {
                'pos': recognized_word_classes
            },
            value_check=lambda x: x != set()
        )

        return self.exponents[exponent_id]

    # TODO: find exponents by properties
    #   - consider attribues-per-exponent map for easy reverse lookups
    def find(self, pre=None, mid=None, post=None, bound=None, pos=None, count=None):
        """List exponent ids (all or up to a count limit) with the matching details"""
        # expect at least one attribute to match against
        if not any([pre, post, bound, pos]):
            print("Grammar find_exponents failed - expected at least one detail to search for")
            return
        
        # check and convert pre and post input
        pre = self.vet_input(pre)
        mid = self.vet_input(mid)
        post = self.vet_input(post)

        # vet parts of speech for existing word classes
        filtered_pos = self.grammar.word_classes.filter(pos)

        # prepare to store exponents with matching details
        found_exponents = []
        # search for exponents where details match non-blank query details
        for exponent_id, exponent_details in self.exponents.items():
            # overlay a new details map switching in non-null query args
            query_details = merge_maps(exponent_details, {
                'pre': pre,
                'mid': mid,
                'post': post,
                'bound': bound,
                'pos': filtered_pos
            }, value_check=lambda x: x is not None)
            # check if the query exponent details match the current exponent
            if query_details == exponent_details:
                # collect ids of exponents matching the compared details
                found_exponents.append(exponent_id)
                # return requested exponents if count tally reached
                if count and len(found_exponents) >= count:
                    break
        
        # return a list of exponents with matching details
        return found_exponents