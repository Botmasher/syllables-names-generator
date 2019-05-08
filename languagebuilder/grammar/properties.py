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
        # check existing grammatical property depending on grammeme or category update
        if not self.get(category, grammeme):
            print(f"Properties update failed - invalid category or grammeme")
            return
        # check for updated category and grammeme strings
        if not new_category or not isinstance(new_category, str):
            print(f"Properties update failed - expected new_category string not {new_category}")
            return
        # check if new property already exists in properties map
        if self.get(new_category, new_grammeme):
            print(f"Properties update failed - new category or grammeme already exists")
            return

        # change grammeme name and remove previous name from its category
        if new_grammeme and isinstance(new_grammeme, str):
            updated_grammeme = new_grammeme
            self.properties[category].remove(grammeme)
        # keep grammeme name
        else:
            updated_grammeme = grammeme

        # add updated grammeme name to new category
        if new_category:
            updated_category = new_category
            self.properties[new_category] = self.properties.pop(category)
            self.properties[new_category].add(updated_grammeme)
        # add updated grammeme name to same category
        else:
            updated_category = category
            self.properties[category].add(updated_grammeme)

        # remove old category if left with empty grammemes
        if self.properties.get(category) == set():
            self.properties.pop(category)

        # update all property references from exponent details
        self._update_in_exponents(
            category,
            grammeme,
            new_category=new_category,
            new_grammeme=new_grammeme
        )

        # report back the modified details
        return {updated_category: updated_grammeme}

    def _update_in_exponents(self, category, grammeme=None, new_category=None, new_grammeme=None):
        """Iterate through grammatical exponents updating category or grammeme names.
        Internal method to be used when changing category or recategorizing grammeme."""
        # store exponent ids to return
        updated_exponents = set()
        
        # iterate through all exponents to modify category and grammeme names
        for exponent_id, exponent_details in self.grammar.exponents.get_items():
            # skip exponents with nonmatching properties
            if category not in exponent_details['properties']:
                continue

            # change grammeme name in exponent entry
            if new_grammeme and grammeme in exponent_details['properties'].get(category, {}):
                # delete old grammeme then add new to category
                self.grammar.exponents.get(exponent_id)['properties'][category].remove(grammeme)
                self.grammar.exponents.get(exponent_id)['properties'][category].add(new_grammeme)
                # record in modded set
                updated_exponents.add(exponent_id)

            # change category name in exponent entry
            if new_category and category in exponent_details['properties']:
                # switch grammemes from old category to new one
                existing_grammemes = self.grammar.exponents.get(exponent_id)['properties'].pop(category, set())
                self.grammar.exponents.get(exponent_id)['properties'][new_category] = existing_grammemes
                
                updated_exponents.add(exponent_id)
        
        return list(updated_exponents)

    def _remove_from_exponents(self, category=None, grammeme=None):
        """Delete either a category or grammeme from exponents referencing this property"""
        # check existence of category and optional grammeme
        if not self.get(category):
            print(f"Failed to remove property from exponents - invalid category {category}")
            return
        if grammeme and not self.get(category, grammeme):
            print(f"Failed to remove property from exponents - invalid grammeme {grammeme}")
            return

        # store ids of changed exponents for return
        updated_exponents = set()

        # delete grammeme or category from exponent properties map 
        for exponent_id, exponent_details in self.grammar.exponents.get_items():
            # skip exponents with no matching grammatical property
            if category not in exponent_details['properties']:
                continue
            
            # apply delete within category
            if grammeme in exponent_details['properties'][category]:
                self.grammar.exponents.get(exponent_id)['properties'][category].remove(grammeme)
                updated_exponents.add(exponent_id)

            # apply delete to category - no grammeme supplied or category left empty
            if not grammeme or not exponent_details['properties'][category]:
                self.grammar.exponents.get(exponent_id)['properties'].pop(category)
                updated_exponents.add(exponent_id)

        return list(updated_exponents)

    def _remove_from_properties(self, category=None, grammeme=None):
        """Delete the record for and exponent references to one property from the grammar"""
        # check for valid property to remove
        # pass through null grammeme for checking category only
        if not self.get(category, grammeme):
            print(f"Properties remove failed - invalid category or grammeme")
            return
        
        # delete property grammeme if supplied
        self.properties[category].discard(grammeme)
        # delete property category entirely if no grammeme supplied
        not grammeme and self.properties.pop(category)

        # delete property from exponent properties sets that have it
        self._remove_from_exponents(category, grammeme)

        # return the deleted details
        return {category: grammeme}
    
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
            print(f"Properties map check failed - expected properties dict not {properties}")
            return False
        
        # vet every single grammeme within every property category
        for category in properties:
            # verify category exists in the grammatical properties
            if category not in self.properties:
                return False
            # verify all grammemes exist in the grammatical properties
            if not set(properties[category]).issubset(self.properties[category]):
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
            print(f"Properties filter failed - expected properties dict not {properties}")
            return

        # filter down the passed-in map to contain only known categories:grammemes
        filtered_map = {
            # collect only known grammemes under known categories
            category: self.filter_grammemes(category, grammemes)
            # iterate through categories - category existence handled in grammemes filter
            for category, grammemes in properties.items()
            if self.get(category)
        }

        return filtered_map

    def map_uncategorized_properties(self, grammemes=None):
        """Build a map of properties using a list of grammemes"""
        # typecheck for properties list
        if not isinstance(grammemes, list):
            print(f"Grammar map_uncategorized_properties failed - invalid grammemes list {grammemes}")
            return

        # collect recognizable properties in a map of category:grammemes
        properties_map = {}
        for grammeme in grammemes:
            # find category,grammeme pairs where the category contains this grammeme
            categories = self.find(grammeme=grammeme)
            # abandon mapping if category not found
            if not categories or grammeme not in categories[0]:
                print(f"Grammar map_uncategorized_properties failed - unknown property {grammeme}")
                return
            # retrieve the category and grammeme from the stored details
            category = categories[0][0]
            # add grammeme to a grammemes set beneath its category
            properties_map.setdefault(category, set()).add(grammeme)

        return properties_map

    # NOTE: subdict method to determine whether requested properties match existing ones
    def is_subproperties(self, compared_properties, base_properties=None):
        """Check whether all category:grammemes in a compared properties map
        exist in the base properties map"""
        # default to entire properties tree
        if base_properties is None:
            base_properties = self.properties

        # verify two comparable maps have been passed
        if not isinstance(compared_properties, dict) or not isinstance(base_properties, dict):
            print("Grammar is_subproperties failed - expected a comparison map and base map, got {0} and {1}".format(compared_properties, base_properties))
            return

        # verify that all compared properties are included in the base map
        for category in compared_properties:
            # expect all compared categories to exist in the base map
            if category not in base_properties:
                return False

            # expect both grammemes collections to be lists or sets
            if not isinstance(compared_properties[category], (set, list, tuple)) or not isinstance(base_properties[category], (set, list, tuple)):
                return False

            # expect falsy category values to be shared by both
            if not compared_properties[category] and base_properties[category]:
                return False

            # expect iterable to turn into set of properties
            compared_grammemes = set(compared_properties[category])
            base_grammemes = set(base_properties[category])

            # expect all compared grammemes to exist in the base category
            if not compared_grammemes.issubset(base_grammemes):
                return False

        # no mismatch pitfalls - judge compared properties to be subproperties of base
        return True
    
    # Update grammeme name, grammeme categorization or category name
    # NOTE: now handled through Properties.update taking new_category or new_grammeme

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
        
        # update the property category
        self.update(category, new_category=new_category)

        # update the property category reference in exponents that point to it
        self._update_in_exponents(category, new_category=new_category)

        # retrieve the updated category
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

        # modify the grammeme in properties
        self.update(category=source_category, grammeme=grammeme, new_category=target_category)

        # swap the grammeme's category within exponent properties that reference it
        self._update_in_exponents(source_category, grammeme=grammeme, new_category=target_category)

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

        # modify grammeme in properties
        self.update(
            category=category,
            grammeme=grammeme,
            new_grammeme=new_grammeme
        )

        # modify references to grammeme in exponents
        self._update_in_exponents(
            category,
            grammeme=grammeme,
            new_grammeme=new_grammeme
        )
        
        # return updated property details
        return self.properties[category][new_grammeme]
