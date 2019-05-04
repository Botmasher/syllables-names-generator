from ..tools.functional_maps import merge_maps
from ..tools.flat_list import flatten
class Properties:
    def __init__(self, grammar):
        # reference to parent grammar where exponents provide these properties
        # used to update exponent details when categories or grammemes change
        self.grammar = grammar
        
        # store properties map containing {category: {grammeme, ...}}
        self.properties = {}

    # Methods for properties CRUD

    def get(self, category=None, grammeme=None):
        """Read category:grammemes from the properties map"""
        # fetch all categories and grammemes
        if not category and not grammeme:
            return self.properties
        # fetch all grammemes in a single category
        elif not grammeme:
            return self.properties.get(category)
        # fetch a single grammeme
        else:
            return (None, grammeme)[grammeme in self.properties.get(category, {})]
    
    def is_grammeme(self, grammeme):
        """Check if the grammeme exists in the properties map"""
        return grammeme in flatten(self.properties.values())

    def is_category(self, category):
        """Check if the category exists in the properties map"""
        return category in self.properties

    def add(self, category=None, grammeme=None):
        """Add one grammatical value to an existing category in the properties"""
        # check for valid category and grammeme input
        if not (category and grammeme and isinstance(category, str) and isinstance(grammeme, str)):
            print("Properties.add failed - expected category and grammeme to be non-empty strings")
            return

        # property category:grammeme pair already exists
        if grammeme in self.properties.get(category, []):
            print(f"Added property {category}:{grammeme} already exists")
            return

        # add the grammeme to the category set
        self.properties.setdefault(category, set()).add(grammeme)

        # read the created grammeme
        return grammeme

    def add_many(self, properties_details):
        """Add a map of grammatical values within categories to the properties"""
        if not isinstance(properties_details, dict):
            print(f"Properties.add_many failed - invalid properties map {properties_details}")
            return
        # store each new grammatical value added to the grammar
        # verify it has the expected details structure:
        # {
        #   # string representing the lookup category over the grammeme
        #   category: {
        #       # pass a sequence full of the category's grammemes
        #       grammeme_0,
        #       ...
        #   },
        # or pass only a string to turn into a properties set
        #   grammeme_1
        # }
        added_properties = {}
        # traverse properties details adding all valid category:grammemes
        for category, grammemes in properties_details.items():
            # wrap just a single grammeme string into a set
            new_grammemes = set([grammemes]) if isinstance(grammemes, str) else grammemes
            
            # check that grammemes to add are a list or set
            if not isinstance(grammemes, (list, tuple, set)):
                print(f"Properties.add_many skipped category {category} - invalid grammemes {grammemes}")
                
            # add grammemes collection to the property category's set of grammemes
            # expect category input to contain a set or list of grammemes
            added_grammemes = set([
                self.add(category=category, grammeme=grammeme)
                for grammeme in new_grammemes
            ])

            # add created category:grammemes to properties map to return
            if added_grammemes:
                added_properties[category] = added_grammemes
 
        # output map of added category:grammemes to send back
        return added_properties

    def update(self, category=None, grammeme=None, new_category=None, new_grammeme=None):
        """Modify the category or grammeme of one grammatical property"""
        # check for existing grammatical property
        if not self.get(category, grammeme):
            print(f"Properties update failed - invalid category:grammeme {category}:{grammeme}")
            return
        
        # change grammeme name and remove previous name from its category
        if new_grammeme and isinstance(new_grammeme, str):
            updated_grammeme = new_grammeme
            self.properties[category].remove(grammeme)
        # keep grammeme name
        else:
            updated_grammeme = grammeme

        # add updated grammeme name to new category
        if new_category and isinstance(new_category, str):
            updated_category = new_category
            self.properties.setdefault(new_category, set()).add(updated_grammeme)
        # add updated grammeme name to same category
        else:
            updated_category = category
            self.properties[category].add(updated_grammeme)

        # delete category if left with empty grammemes set
        not self.properties[category] and self.properties.pop(category)

        # report back the modified details
        return {updated_category: updated_grammeme}

    def remove(self, category, grammeme):
        """Delete the record for and exponent references to one property from the grammar"""
        if not self.get(category, grammeme):
            print(f"Properties remove failed - unknown category:grammeme {category}:{grammeme}")
            return
        # delete property key and details
        self.properties[category].remove(grammeme)
        # delete property from exponent properties category sets that have it
        for exponent_id, exponent_details in self.grammar.exponents.get_items():
            if category in exponent_details['properties'] and grammeme in exponent_details['properties'][category]:
                self.grammar.exponents.get(exponent_id)['properties'][category].remove(grammeme)
            # also delete the category from properties if it is left empty
            if self.grammar.exponents.get(exponent_id)['properties'][category] == set():
                self.grammar.exponents.get(exponent_id)['properties'].pop(category)
        # return the deleted details
        return {category: grammeme}
    
    # update grammeme name, grammeme categorization or category name

    def rename_category(self, category, new_category):
        """Update a category name in the properties map and for all grammemes and exponents that reference it"""
        # verify that category exists
        if category not in self.properties:
            print(f"Properties.rename_category failed - unknown property category {category}")
            return
        # check for category rename conflict where target already exists
        if new_category in self.properties:
            print(f"Properties.rename_category failed - new category name already exists in properties: {new_category}")
            return
        
        # retrieve property grammemes and clear out old category
        grammemes = self.properties.pop(category)
        
        # update the category attribute within each grammeme's details
        for grammeme_name in grammemes:
            grammemes[grammeme_name]['category'] = new_category

        # store grammemes under the new target category
        self.properties[new_category] = grammemes

        # update the property category reference in exponents that point to it
        for exponent_id, exponent_details in self.grammar.exponents.get_items():
            if category in exponent_details['properties']:
                self.grammar.exponents.get(exponent_id)['properties'][new_category] = self.grammar.exponents.get(exponent_id)['properties'].pop(category)

        # retrieve the new target category
        return self.properties[new_category]

    def recategorize(self, source_category, grammeme, target_category):
        """Recategorize an existing grammeme from below its source category to below a destination category"""
        # check existence of current property
        if not self.get(source_category, grammeme):
            print("Properties.recategorize failed - unrecognized property {}:{}".format(source_category, grammeme))
            return
        # check type of swap target category
        if not isinstance(target_category, str):
            print("Properties.recategorize failed - expected target category string not {}".format(target_category))
            return

        # retrieve and modify the grammeme details
        grammeme_details = self.properties[source_category].pop(grammeme)
        # create a new details entry
        grammeme_details = merge_maps(
            grammeme_details,
            {'category': target_category}
        )
        # remove the original category if it is left empty
        not self.properties[source_category] and self.properties.pop(source_category)
        # add the grammeme under the destination category
        self.properties.setdefault(target_category, {})[grammeme] = grammeme_details

        # swap the grammeme's category within exponent properties that reference it
        for exponent_id, exponent_details in self.grammar.exponents.get_items():
            if grammeme in exponent_details['properties'].get(source_category, {}):
                # remove grammeme from exponent properties
                self.grammar.exponents.get(exponent_id)['properties'][source_category].remove(grammeme)
                # remove empty category from exponent properties
                not exponent_details['properties'][source_category] and self.grammar.exponents.get(exponent_id)['properties'].pop(source_category)
                # add grammeme to destination category under exponent properties
                self.grammar.exponents.get(exponent_id)['properties'].setdefault(target_category, set()).add(grammeme)

        # retrieve and send back the new grammeme details
        return self.properties[target_category][grammeme]

    def rename_grammeme(self, category, grammeme, new_grammeme):
        """Rename the grammeme for a single property and update exponents to reference the new name"""
        # check for updated grammeme string and existing property
        if not (new_grammeme and isinstance(new_grammeme, str)):
            print("Properties.rename_grammeme failed - invalid non-empty new grammeme string {0}".format(new_grammeme))
            return
        if not self.get(category, grammeme):
            print("Properties.rename_grammeme failed - unknown category:grammeme {0}:{1}".format(category, grammeme))
            return

        # remove old grammeme entry
        grammeme_details = self.properties[category].pop(grammeme)
        # store the new details with the new grammeme name
        grammeme_details['grammeme'] = new_grammeme
        self.properties[category][new_grammeme] = grammeme_details

        # swap out grammeme name within all exponents that reference the property
        for exponent_id, exponent_details in self.grammar.exponents.get_items():
            if grammeme in exponent_details['properties'].get(category, {}):
                self.grammar.exponents.get(exponent_id)['properties'][category].remove(grammeme)
                self.grammar.exponents.get(exponent_id)['properties'][category].add(new_grammeme)

        # return updated property details
        return self.properties[category][new_grammeme]

    def find(self, grammeme=None, category=None):
        """Return category:grammeme pairs naming properties with the matching details"""
        # check that at least one of the attributes is filled in
        if not (isinstance(grammeme, str) or isinstance(category, str)):
            print("Properties.find failed - expected at least one detail present")
            return
        # store category grammemes for propreties with matching details
        # check and return the explicit category:grammeme pair
        if grammeme and category:
            if self.get(category, {}).get(grammeme):
                return [(category, grammeme)]
            return
        # uncategorized grammeme - return all occurrences
        elif grammeme and not category:
            return [(found_category, grammeme) for found_category in filter(
                lambda filtered_category: grammeme in self.properties[filtered_category],
                self.properties.keys()
            )]
        # all grammemes in a single category
        elif category in self.properties:
            return [(category, stored_grammeme) for stored_grammeme in self.properties[category].keys()]
        # no valid category or grammeme supplied
        else:
            return
    

    # Methods for comparing maps and identifying requested properties

    def is_properties_map(self, properties=None):
        """Verify a well-structured map containing known categories and grammemes"""
        # expect a map to compare
        if not isinstance(properties, dict):
            print("Properties.is_properties_map check failed - invalid properties map {}".format(properties))
            return False
        
        # vet every single grammeme within every property category
        for category in properties:
            # verify category exists in the grammatical properties
            if category not in self.properties:
                return False
            # verify paralleled structure of nested grammemes under category
            for grammeme in self.properties[category]:
                # check against properties stored in the grammar
                if not self.get(category, grammeme):
                    return False
        
        # no properties or structures fell through during checks
        return True

    def filter_grammemes(self, category, grammemes):
        """Structure a set of category grammemes allowing for flexible input"""
        # handle a grammemes set or single string within a known category
        if category in self.properties:
            # return recognized grammeme collection members inside of a set
            if isinstance(grammemes, (list, set, tuple)):
                return set(grammemes).intersection(self.properties.get(category, set()))
            # recognized grammeme string inside of a set
            if isinstance(grammemes, str) and grammemes in self.properties.get(category, set()):
                # only one grammeme string given
                return {grammemes}
        # unrecognized category name or grammeme type input
        else:
            return

    def filter(self, properties=None):
        """Return a filtered properties copy containing only verified category keys and grammemes sets"""
        # verify that a map was provided
        if not isinstance(properties, dict):
            print("Properties.filter failed - expected properties dict not {0}".format(properties))
            return

        # map collections for all known categories
        filtered_map = {
            # collect only known grammemes under known categories
            category: self.filter_grammemes(category, grammemes)
            # iterate through categories - category existence handled in grammemes filter
            for category, grammemes in properties.items()
        }

        return filtered_map

    def map_uncategorized_properties(self, properties=None):
        """Build a map of properties using a list of grammeme names"""
        # typecheck for properties list
        if not isinstance(properties, list):
            print("Grammar map_uncategorized_properties failed - invalid properties list {0}".format(properties))
            return

        # collect recognizable/guessable properties and map them as category:grammemes
        properties_map = {}
        for category in properties:
            # read the first category:grammeme details where the grammeme matches this string
            properties_details = self.find(category=category)
            # abandon mapping if a property is not found
            if not properties_details or 'grammeme' not in properties_details[0]:
                print("Grammar map_uncategorized_properties failed - unknown property {0}".format(category))
                return
            # retrieve the category and grammeme from the stored details
            property_entry = properties_details[0]
            category = property_entry['category']
            grammeme = property_entry['grammeme']
            # add grammeme beneath its category - to new set if needed
            properties_map[category] = properties_map.get(category, set()).add(grammeme)

        return properties_map

    # subdict method used to determine whether requested properties
    def is_subproperties(self, compared_properties, base_properties=None):
        """Check whether all category:grammemes in a compared properties map exist in the base properties map"""
        # verify two comparable maps have been passed
        if not isinstance(compared_properties, dict) or not isinstance(base_properties, dict):
            print("Grammar is_subproperties failed - expected a comparison map and base map, got {0} and {1}".format(compared_properties, base_properties))
            return

        # default to entire properties tree
        if base_properties is None:
            base_properties = self.properties

        # check every compared category and grammeme for inclusion in the base map
        for category in compared_properties:
            # expect all compared categories to exist in the base map
            if category not in base_properties:
                return False

            # expect falsy category values to be shared by both
            if not compared_properties[category]:
                if base_properties[category]:
                    return False

            # expect iterable to turn into set of properties
            compared_grammemes = {grammeme for grammeme in compared_properties[category]}
            base_grammemes = {grammeme for grammeme in base_properties[category]}

            # expect all compared grammemes to exist in the base category
            if not compared_grammemes.issubset(base_grammemes):
                return False

        # no mismatch pitfalls - consider compared map as true subproperties
        return True
