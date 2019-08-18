import uuid

# TODO: move single Rule methods and map/attrs here
# find a rule based on source/target/environment

class Rules():
    def __init__(self):
        self.rules = {}     # map of rule objects
        self.order = []     # ids sequence representing rule order or chronology

    # Rule objects cruds and checks

    def has(self, rule_id):
        """Check if the rule exists in stored rules"""
        return rule_id in self.rules

    def get(self, rule_id=None, ordered=True):
        """Read the value for one stored rule, or all if no id passed in"""
        # fetch all if no rule id given
        if not rule_id:
            # order or unordered rule objects
            rules = self.rules if not ordered else {
                r: self.rules[r] for r in self.order
            }
            return rules
        # rule does not exist in rules store
        if not self.has(rule_id):
            print(f"Rules get failed - invalid rule_id: {rule_id}")
            return
        # found rule
        return self.rules[rule_id]

    def get_pretty(self, rule_id, use_notation=False):
        """Format rule into a human readable statement."""
        # check for valid rule
        rule = self.rules.get(rule_id)
        if not rule:
            print(f"Rules get_pretty format failed - invalid rule_id {rule_id}")
            return
        # format the rule into human readable text
        text = "{0} -> {1} / {2}" if use_notation else "Change {0} to {1} when it's {2}"
        return text.format(
            rule['source'],
            rule['target'],
            self.pretty_environment(rule['environment'], use_notation=use_notation)
        )

    # TODO: Expect vetted parsed features lists here
    def add(self, source=None, target=None, environment=None):
        """Add one rule to the rules and its id to the rule orders"""
        # create and verify environment structure
        environment_structure = self.structure_environment(environment)
        if not environment_structure:
            print(f"Rules add failed - invalid environment structure {environment}")
            return

        # verify source and target sequences
        if not isinstance(source, list) or not isinstance(target, list):
            print(f"Rules add failed - invalid lists for source {source} or target {target}")
            return

        # TODO: check that source and target features are valid
        #   - handled at the Phonology level
        #   - do you also want to tie Phonetics into Rules to perform the check?

        # store the rule 
        rule_id = uuid.uuid4()
        self.rules[rule_id] = {
            'source': source,
            'target': target,
            'environment': environment_structure
        }
        # add as latest to rule ordering
        self.order.append(rule_id)
        # send back key identifying rule
        return rule_id

    def update(self, rule_id, source=None, target=None, environment=None):
        """Modify an existing rule"""
        # original and updated rule attributes
        rule = self.rules[rule_id]
        mod_rule = {
            'source': source,
            'target': target,
            'environment': environment
        }
        # modify the rule
        self.rules[rule_id] = {
            **rule,
            **{
                k: v for k, v in mod_rule.items()
                if v is not None
            }
        }
        return rule_id

    def remove(self, rule_id):
        """Remove one rule from the rules"""
        if not self.has(rule_id):
            print(f"Rules remove failed - invalid rule_id: {rule_id}")
            return
        # remove rule object from rules map and id from ordering
        rule = self.rules.pop(rule_id)
        i = self.order.index(rule_id)
        self.order.pop(i)
        return rule
    

    # Manage environments

    # TODO: allow more complex environments including specific consonant/vowel features
    def structure_environment(self, environment_structure):
        """Create an environment structure from a features list or string"""
        # parse short strings like 'C_C'
        if isinstance(environment_structure, str):
            short_symbols = {'C': ["consonant"], 'V': ["vowel"], '_': "_", '#': "#"}
            structure = [short_symbols[symbol] for symbol in environment_structure]
        else:
            structure = list(environment_structure)
        # store environment elements as list
        if not self.is_environment(structure):
            raise ValueError(f"Rules failed to set environment with invalid structure {structure}")
        return structure

    def is_environment(self, environment_structure):
        """Check for valid rule environment structure list including one open slot"""
        if isinstance(environment_structure, list) and environment_structure.count('_') == 1:
            return True
        return False

    def pretty_environment(self, environment_structure, use_notation=False):
        """Format environment structure as human readable text"""
        body_text = ""
        intro_text = ""

        for i in range(len(environment_structure)):
            slot = environment_structure[i]
            # notation
            if use_notation:
                slot_txt = ""
                if 'consonant' in slot:
                    slot_txt += "C"
                elif 'vowel' in slot:
                    slot_txt += "V"
                elif slot == '_':
                    slot_txt += "_"
                elif slot == '#':
                    slot_txt += "#"
                features = [f"+{feature}" for feature in slot if feature not in ('consonant', 'vowel')]
                if features:
                    body += "{0}({1})".format(slot_txt, ",".join(features))
                else:
                    body += f"{slot_txt}"
                continue
            # verbose
            line = ""
            if isinstance(slot, list):
                line += "an " if slot[0][0].lower() in ['a', 'e', 'i', 'o', 'u'] else "a "
                for feature in slot:
                    line += f"{feature}, "
            elif isinstance(slot, str):
                if slot == "_":
                    if i == 0:
                        intro_text += "before "
                    elif i == len(environment_structure) - 1:
                        intro_text += "after "
                    else:
                        intro_text += "between "
                        body_text = body_text[:-2] if body_text.endswith(", ") else body_text
                        line += " and "
                elif slot == "#":
                    line += "a word break "
                else:
                    line += f"a {slot}"
            else:
                pass
            body_text += line
        if body_text[(len(body_text)-2):] == ", ":
            body_text = body_text[:-2]
        return f"{intro_text}{body_text}"


    # Manage rule order sequence list

    def order_swap(self, rule_a, rule_b):
        """Switch the ordering position of two rule indexes so that they
        apply in reverse order"""
        # swap position of ids
        if self.has(rule_a) and self.has(rule_b):
            a_i = self.order.index(rule_a)
            b_i = self.order.index(rule_b)
            self.order[a_i] = rule_b
            self.order[b_i] = rule_a
            return True
        # unrecognized rules
        return False

    def get_order(self, reverse=False):
        """Fetch the ordering of all rule ids optionally reversing their order"""
        # back-to-front rule ordering
        if reverse:
            return list(reversed(self.order))
        # front-to-back rule ordering
        return self.order

    def order_before(self, rule_id_before, rule_id_after):
        """Change a rule index to apply before another rule"""
        if not (self.has(rule_id_before) and self.has(rule_id_after)):
            print(f"Failed to reorder rules - either before or after id not found")
            return
        
        # get rule order positions
        before_i = self.order.index(rule_id_before)
        after_i = self.order.index(rule_id_after)
        
        # only perform swap if first precedes second
        if after_i <= before_i:
            self.order_swap(rule_id_before, rule_id_after)
        
        return self.order
    
    def order_absolute(self, rule_id, order_i=0):
        """Set the index of a rule within the relative rule order sequence"""
        if not self.has(rule_id):
            print(f"Failed to reorder invalid rule {rule_id}")
            return
        # calculate new position in cut list
        new_i = order_i - 1 if self.order.index(rule_id) > order_i else order_i
        # remove rule id from list
        filtered_order = list(filter(
            lambda x: x != rule_id,
            self.order[:]
        ))
        # add rule id at new position
        self.order = filtered_order[:new_i] + [rule_id] + filtered_order[new_i:]
        return self.order