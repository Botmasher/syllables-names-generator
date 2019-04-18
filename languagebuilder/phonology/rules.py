import uuid

# TODO: move single Rule methods and map/attrs here

class Rules():
    def __init__(self):
        self.rules = {}     # map of rule objects
        self.order = []     # ids sequence representing rule order or chronology

    # TODO: retire method once Rule is constructed internally
    def is_rule(self, rule):
        """Check if the object is a Rule instance"""
        return type(rule).__name__ == 'Rule'

    def order_swap(self, rule_a, rule_b):
        """Switch the ordering position of two rule ids so that they
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

    def order_before(self, rule_before, rule_after):
        """Change a rule index to apply before another rule"""
        if self.has(rule_before) and self.has(rule_after):
            # place rule before relative id
            before_i = self.order.index(rule_before)
            after_i = self.order.index(rule_after)
            self.order = self.order[:rule_after] + [rule_before] + self.order[rule_after:]
            # remove moved id accounting for list growth
            if after_i > before_i:
                self.order.pop(before_i)
            # add one if before_id was duplicated in a position before its index
            else:
                self.order.pop(before_i + 1)
            return True
        return False
    
    def order_absolute(self, rule_id, order_i=0):
        """Set the index of a rule within the relative rule order sequence"""
        if self.has(rule_id):
            # place the id at new position in list
            original_i = self.order.index(rule_id)
            self.order = self.order[:order_i] + [rule_id] + self.order[order_i:]
            # remove original id accounting for list growth if moved before
            if order_i > original_i:
                self.order.pop(original_i)
            else:
                self.order.pop(original_i + 1)
            return True
        return False

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

    # TODO: take source, target, environment
    def add(self, rule, order=None):
        """Add one rule to the rules"""
        if not self.is_rule(rule):
            print(f"Rules add failed - invalid rule_id: {rule}")
            return
        # store the rule 
        rule_id = uuid.uuid4()
        self.rules[rule_id] = rule
        # add as latest to rule ordering
        self.order.append(rule_id)
        # send back key identifying rule
        return rule_id

    # TODO: take rule attributes not just entire reassignment
    def update(self, rule_id, rule):
        """Modify an existing rule"""
        if not self.is_rule(rule):
            print(f"Rules update failed - invalid rule {rule}")
            return
        # modify the rule
        self.rules[rule_id] = rule
        return rule_id

    def remove(self, rule_id):
        """Remove one rule from the rules"""
        if not self.has(rule_id):
            print(f"Rules remove failed - invalid rule_id: {rule_id}")
            return
        # remove rule object from rules map and id from ordering
        rule = self.rules.pop(rule_id)
        self.order.pop(rule_id)
        return rule

    # def clear(self):
    #     """Reset the rules store"""
    #     rules_cache = self.rules
    #     self.rules = {}
    #     def read_cache():
    #         return rules_cache
    #     return read_cache
