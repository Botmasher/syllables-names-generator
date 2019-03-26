from ..tools.flat_list import flatten

# order word and sentence elements relative to each other
class Morphosyntax:
    def __init__(self, grammar):
        # used to read and verify that ordered exponents exist
        self.grammar = grammar
        
        # relative exponent ordering word or phrase units
        self.exponent_order = {}
        
        # fixed left-to-right order of elements within a unit]
        #   - unit can be ordered by a mix of word classes and properties
        #   - built to be used within a named fixed sentence order
        #
        # structure of unit:sequence pairs:
        # {
        #   'unit_name': [
        #       {'property_1', 'property_2'...},    # possible properties in this piece
        #       {'word_class_1},                    # word class in this piece
        #       ...
        #   ]
        # }
        self.units = {}

        # fixed left-to-right order of units in various types of sentences
        #   - each discrete part is a unit or a word classes
        #   - see arrange method for the reordering process
        #
        # structure of sentence:sequence pairs:
        # {
        #   'sentence_name': [
        #       {'unit_name', 'word_class', ...},   # options
        #       {'unit_name_2'},
        #       {'word_class_2', word_class_3}
        #   ]
        # }
        self.sentences = {}

    # TODO: conditional ordering
    #   - example [first_ending, [another, only_if_another] || [this_one], ...]

    # TODO: assuming exponents are included, subarrange exponent units
    #   - have exponents gravitate to nearest applicable base (how to know? word classes?)
    #   - subarrange exponents around that base
    
    # TODO: support varying syntax and flexible word order
    #   - "interrogative" vs "declarative" syntax in EN
    #   - word order in nonconfig langs

    def get_unit(self, unit_name):
        """Read unit pieces sequence for one named unit"""
        return self.units.get(unit_name)

    def check_unit_piece(self, piece):
        """Check whether a unit piece is a property or a word class"""
        # unit piece is a property two-member list [category,grammeme]
        if isinstance(piece, (tuple, list)):
            # category, grammeme found in grammar properties
            if self.grammar.properties.get(piece[0], {}).get(piece[1]):
                return "properties"
            # unfound property
            return
        # unit piece is a single-entry map {category:grammeme}
        elif isinstance(piece, dict) and len(piece.keys()) == 1:
            # category:grammeme pair found in grammar properties
            category = list(piece.keys())[0]
            grammeme = piece[category]
            if self.grammar.properties.get(category, {}).get(grammeme):
                return "properties"
            # unfound property
            return
        # unit piece is a word class name
        elif piece in self.grammar.word_classes:
            return "word_classes"
        # unrecognized unit piece
        else:
            return

    def add_unit(self, unit_name, unit_sequence, overwrite=False):
        """Store a new fixed order for a unit (sequence of properties or word classes)"""
        # avoid updating an existing unit
        if not overwrite and unit_name in self.units:
            print("Morphosyntax failed to add new unit order - unit name already exists {}".format(unit_name))
            return

        # store left-to-right sequence of unit pieces
        # each piece many contain properties, word classes, exponents
        filtered_unit = []

        # go through unit linearly veting and assigning options for each spot
        for unit_piece in unit_sequence:
            # build set of options for current position in the unit
            unit_piece_options = set()
            # add a single property, word class or exponent at this spot
            if isinstance(unit_piece, str) and self.check_unit_piece(unit_piece):
                unit_piece_options.add(unit_piece)
            # add recognized properties, word classes or exponents to this spot
            elif isinstance(unit_piece, (tuple, set, list)):
                [unit_piece_options.add(piece) for piece in unit_piece if self.check_unit_piece(piece)]
            # unrecognized unit info in the current piece
            else:
                continue
            # build up sequence of properties, word classes, exponents
            filtered_unit.append(unit_piece_options)
        
        # add the named unit sequence to the units map
        self.units[unit_name] = filtered_unit

        return self.units[unit_name]

    def update_unit(self, unit_name, unit_sequence):
        """Update an order for a named unit sequence"""
        if unit_name not in self.units:
            print("Morphosyntax failed to update unrecognized unit name {}".format(unit_name))
            return
        return self.add_unit(unit_name, unit_sequence, overwrite=True)

    def remove_unit(self, unit_name):
        """Delete and return one unit sequence from the unit order map"""
        # check for unit existence
        if not self.get_unit(unit_name):
            return
        # remove and return the named unit
        removed_unit = self.units.pop(unit_name)
        return removed_unit
    
    def get_sentence(self, sentence_name):
        """Read one named sentence sequence"""
        return self.sentences.get(sentence_name)

    def add_sentence(self, sentence_name, sentence_sequence, overwrite=False, all_or_none=False):
        """Add a named sentence type with a sequence of units in the sentence"""
        # check for existing sentence type name and sequence of units
        if (overwrite or sentence_name in self.sentences) or not isinstance(sentence_sequence, (list, tuple)):
            print("Failed to add sentence to morphosyntax - expected valid sentence name and sequence")
            return
        
        # collect only known units
        filtered_units = [
            unit for unit in sentence_sequence
            if unit in self.units
        ]

        # back out if any non-units given
        if all_or_none and len(filtered_units) != len(sentence_sequence):
            return

        # add units sequence to sentences
        self.sentences[sentence_name] = filtered_units

        return self.sentences[sentence_name]

    def update_sentence(self, sentence_name, sentence_sequence, all_or_none=False):
        """Modify the unit sequence of a single named sentence type"""
        # check that the sentence type already exists
        if not self.get_sentence(sentence_name):
            return
        # run sentence add with overwrite
        return self.add_sentence(sentence_name, sentence_sequence, overwrite=True)
    
    def remove_sentence(self, sentence_name):
        """Delete and return one existing sentence sequence from the sentence order map, or None if not sentence found"""
        # check for existence of sentence
        if not self.get_sentence(sentence_name):
            return
        # remove and return the sentence sequence
        removed_sentence = self.sentences.pop(sentence_name)
        return removed_sentence


    ## Relative Exponent ordering

    # TODO: ordering of non-positional exponents for example multiple apophonies

    # relative inner OR outer exponents add method for one exponent
    def make_relative_exponents_set(self, exponent_id, exponents_collection, inner_outer_key):
        """Add to and return a copy of a relative exponents pre or post set"""
        return self.exponent_order.get(
            exponent_id, {}
        ).get(
            inner_outer_key, set()
        ) | {
            exponent for exponent in exponents_collection
            if self.grammar.exponents.get(exponent)
        }

    # abstracted relative order-key collection add method for one axis item
    def make_relative_set(self, ordering_map, order_id, added_collection, order_item_key):
        """Add to and return a copy of a relative  set"""
        return ordering_map.get(
            order_id, {}
        ).get(
            order_item_key, set()
        ) | {
            item for item in added_collection
            if ordering_map.get(item)
        }
    
    def add_exponent_order(self, exponent_id, inner=None, outer=None):
        """Store the position of other exponents compared to an exponent
        Take exponent id the other exponents will be relative to, then
        pass collections of exponent ids occuring closer to the base (inner)
        or away from it (outer) compared to the given exponent
        """
        # back out if no main exponent or relatives
        if not self.grammar.exponents.get(exponent_id) or not (inner or outer):
            print("Grammar morphosyntax expected one existing exponent and at least one pre or post collection")
            return
        
        # initialize positional exponent collections
        # read: from args
        requested_exponents = {
            'inner': inner,
            'outer': outer
        }
        # write: vet and collect
        filtered_exponents = {}

        # filter requested exponents allowing for single string or collection input
        # store recognized ones and their position compared to the main exponent
        for position, exponents in requested_exponents.items():
            # exponents collection is a single string - create a one-item set
            if isinstance(exponents, str) and self.grammar.exponents.get(exponents):
                filtered_exponents[position] = {exponents}
            # create set from requested exponents collection
            elif isinstance(exponents, (list, tuple, set)):
                filtered_exponents[position] = {
                    exponent for exponent in exponents
                    if self.grammar.exponents.get(exponent)
                }
            # empty set if unrecognized exponent args for this position
            else:
                filtered_exponents[position] = set()

        # merge new relative exponents into stored exponent orders
        for position, added_exponents in filtered_exponents.items():
            # get current exponents at this position (inner/outer)
            existing_exponents = self.exponent_order.setdefault(exponent_id, {})
            position_exponents = existing_exponents.get(position, set())
            
            # get exponents set for the complementary position
            opposite_position = "inner" if position == "outer" else "outer"
            opposite_position_exponents = existing_exponents.get(opposite_position, set())

            # unite new exponent collection with existing set
            updated_exponents = added_exponents | position_exponents
            # store updated relative positional exponent collection
            self.exponent_order[exponent_id][position] = updated_exponents
            self.exponent_order[exponent_id][opposite_position] = opposite_position_exponents

            # TODO: optimize searching and updating relative entries
            # reverse update relative entries with correct position of main exponent
            for added_exponent in added_exponents:
                # remove relative from the added exponent's opposite position
                # example: if adding "pre" inner relative to exponent, delete it from outer
                self.exponent_order[exponent_id][opposite_position].discard(added_exponent)
                
                # get the relative exponent inner and outer sets
                added_exponent_details = self.exponent_order.setdefault(added_exponent, {})
                
                # add main exponent to the opposite position in its relative
                # (if they are inner or outer, add main outer/inner)
                # example: -affix1-affix2 with affix2 relative inner affix1 should add affix1 to the set in the 'pre' key of affix2
                added_exponent_details.setdefault(opposite_position, set()).add(exponent_id) 
                # self.exponent_order                         \
                #     .setdefault(added_exponent, {})         \
                #     .setdefault(opposite_position, set())   \
                #     .add(exponent_id)

                # delete main from the non-opposite position in its relative
                # (if main in relative's inner/outer and they're outer/inner, remove main)
                # example: -affix1-affix2 with affix2 relative post affix1 should not store affix1 in the 'post' key of affix2
                added_exponent_details.setdefault(position, set()).discard(exponent_id)
                # self.exponent_order                         \
                #     .setdefault(added_exponent, {})         \
                #     .setdefault(position, set())            \
                #     .discard(exponent_id)

        # TODO: ? enforce individual relatives must be either inner xor outer compared to main

        return self.exponent_order.get(exponent_id)


    ## Use stored morphosyntax to arrange words in a given unit or sentence
    
    # TODO: Latest fix works much of the time, but solve for:
    #   - create exponent1, exponent2, exponent3, exponent4
    #   - order exponent4 inner to exponent3
    #   - order exponent2 outer to exponent3 and inner to exponent1
    #   - sometimes result => exponent1, exponent2, exponent3, exponent4
    #   - sometimes result => exponent3, exponent4, exponent1, exponent2

    # build chains of inner-to-outermosts
    #   - filter input list for valid exponent ids
    #       - if ordered-only flag, drop unordered ids from this list
    #       - (unordered ids are any not found as keys in exponent_order)
    #   - use a source (unordered) and target (ordered) list
    #       - source is filtered exponent ids
    #       - target is initialized empty list
    #   - sort the exponent ids based on inner-to-outerness
    #       - traverse source list looking for next innermost not yet in the target
    #       - if none are innermore than this one, ?prepend it
    #       - look to end each time for innermost compared to this one
    #   - once innermost identified in that traversal, build inner/outer tree
    #       - (this still runs within the traversal)
    #       - look through the innermost's outers
    #       - if any of those outers are in the source list, order them
    #           - make sure they aren't already in targets
    #           - place them and their inner/outers in the list before the innermost
    #       - search their inners and outers for source list matches
    #           - make sure they aren't already in targets
    #           - attach inners after and outers before the compared matches
    #           - recursively though: the inners are the inners/outers of inners...
    #           - ... and the outers are inners/outers of outers
    #   - resulting shape:
    #       - [inners, outermore, outers] + []

    def _chain_inners_outers(self, exponent_id, source_ids, skipset=None):
        """Return a list of contiguous inner/outer exponent ids ordered from
        outermost to innermost. Only orders source_ids and avoids ids in skipset.
        exponent_id:    ordered exponent to branch off inners/outers this call 
        source_ids:     collection of ids to chain
        skipset:        set of ids already chained; initialize with values to skip
        """
        # initialize a set for tracked ids on the first call if none provided
        if skipset is None:
            skipset = set()
        else:
            skipset = set(skipset)
        
        # do not order ids not in ordered map or already in handled tracked cases
        if exponent_id not in self.exponent_order or exponent_id in skipset:
            return []
        
        # register this id as a handled case
        skipset.add(exponent_id)

        # vet left and right branches for untracked ids that still need to be sorted
        inners = list(filter(
            lambda inner: inner not in skipset,
            self.exponent_order[exponent_id]['inner']
        ))
        outers = list(filter(
            lambda outer: outer not in skipset,
            self.exponent_order[exponent_id]['outer']
        ))

        # exponent only if pursuing empty left and right branches
        if not (inners or outers) and exponent_id in source_ids:
            return [exponent_id]
        
        # id between branches
        # allows branching over/skipping ids not in source list
        central_id = [exponent_id] if exponent_id in source_ids else []

        # recursively build up inners and outers branching to both sides
        # of these inners and outers...
        inners_outers = [
            self._chain_inners_outers(outer, source_ids, skipset) for outer in outers
        ] + central_id + [
            self._chain_inners_outers(inner, source_ids, skipset) for inner in inners
        ]

        # send back a flatlist bubbling up from all chained inners and outers
        return flatten(inners_outers)

    def arrange_exponents(self, exponent_ids, filter_ordered_only=False):
        """Take a list of exponents and return a reordered copy of the list
        after applying relative exponent inner/outer ordering. Exponents not
        added to the morphosyntax ordered exponents map are not returned within
        the reordered sequence. Breaks in relative exponent chain may result in
        unpredictable order of single exponents or groups of ordered exponents.
        """
        # filter down to a collection of only explicitly ordered exponents
        if filter_ordered_only:
            filtered_exponents = list(filter(
                lambda x: x in self.exponent_order,
                exponent_ids
            ))
        # collect any known exponent
        else:
            filtered_exponents = list(filter(
                lambda x: self.grammar.exponents.get(x),
                exponent_ids
            ))

        # store exponent ids sorted from by innerness
        ordered_exponents = []

        # Sort a list of which exponents are inner-outer compared to each other
        # with inner terms closer to a base and outer away from it.
        #
        # Every element may know if it's "inner" or "outer" compared to one or
        # more other elements, but for any single element the attribute is optional
        # (an element is allowed to know nothing about inners or outers).
        #
        # Order all of them from outermost to innermost
        for exponent_id in filtered_exponents:
            # do not repeat branch-chain-sort on already ordered exponents
            if exponent_id in ordered_exponents:
                continue

            # avoid looking for outers of the found inner if it's not ordered
            if exponent_id not in self.exponent_order:
                ordered_exponents.append(exponent_id)
            
            # branch chain sort all inners and outers recursively off this exponent
            #   - adjacency not required
            #   - members not to be ordered are not included in returned list
            #   - members not to be ordered still have inners outers searched
            else:
                ordered_exponents += self._chain_inners_outers(
                    exponent_id,
                    filtered_exponents,
                    set()
                )

        # send back the sorted exponents list
        return ordered_exponents

    # TODO: rework Syntax side to manage sentences and sentence units well
    #
    def arrange_sentence(self, sentence, sentence_tags, sentence_type):
        """Take a collection of sentence items and return a reordered copy
        reordering units using on the named sentence type."""

        # check if sentence type exists in collection
        if sentence_type not in self.sentences:
            print(f"Morphosyntax failed to arrange unidentified sentence type {sentence_type}")
            return
        # expect all sentence elements to be tagged 
        if len(sentence) != len(sentence_tags):
            print(f"Morphosyntax failed to arrange sentence - tokens and tags counts do not match")
            return

        # TODO: arrange sentence units and each individual unit
        #   - expect one-to-one mapping of sentence elements and tags
        #   - expect tags to be properties or word classes (per-unit info)
        #   - expect groups of units
        #   - linearly identify which raw pieces belong to which units
        #   - assume properties in multiple units are nearer to their units

        # set up a sequence for catching all unit pieces in order
        sentence_units = [
            {
                'unit_piece': unit_piece,
                # data for elements from the passed-in sentence
                'token': None,
                'tag': None
            }
            for unit in self.sentences[sentence_type]
            for unit_piece in self.units[unit]
        ]

        # which indexes have already settled in order
        used_indexes = set()

        # fill in units
        for unit_piece in sentence_units:
            # find the next unused element fiting into this piece of this unit
            for i in range(len(sentence_tags)):
                if sentence_tags[i] in unit_piece and i not in used_indexes:
                    # remember the token/tag as used
                    used_indexes.add(i)
                    # store info for the token/tag
                    sentence_units[unit_piece]['token'] = sentence[i]
                    sentence_units[unit_piece]['tag'] = sentence_tags[i]
                    break
            continue
        
        # use the settled tokens to collect reordered sentence elements
        ordered_sentence = [sentence_units[unit]['token'] for unit in sentence_units]

        return ordered_sentence
