import uuid

# TODO abstract this class (restricted store) for any stored type
#   - label (like self.types=['Rule']) for types to check on create
#   - store id:object pairs in dict
#   - maybe expect a dict per key to store subattributes

class Rules():
    def __init__(self):
        self.rules = {}

    def is_rule(self, rule):
        """Check if the object is a Rule instance"""
        if type(rule).__name__ == 'Rule':
            return True
        return False

    def has(self, rule_id):
        """Check if the rule exists in stored rules"""
        if rule_id in self.rules:
            return True
        return False

    def get(self, rule_id=None):
        """Read the value for one stored rule, or all if no id passed in"""
        # fetch all for zero-arg calls
        if not rule_id:
            return self.rules
        # rule does not exist in rules store
        if not self.has(rule_id):
            print("Rules get failed - unknown rule {0}".format(rule_id))
            return
        # found rule
        return self.rules[rule_id]

    def add(self, rule):
        """Add one rule to the rules"""
        if not self.is_rule(rule):
            print("Rules add failed - invalid rule {0}".format(rule))
            return
        rule_id = uuid.uuid4()
        self.rules[rule_id] = rule
        return rule_id

    def update(self, rule_id, rule):
        """Modify an existing rule"""
        if not self.is_rule(rule):
            print("Rules update failed - unknown rule {0}".format(rule_id))
            return
        # TODO destructure incoming object for partial update
        self.rules[rule_id] = rule
        return rule_id

    def remove(self, rule_id):
        """Remove one rule from the rules"""
        if rule_id in self.rules:
            self.rules.pop(rule_id)
            return True
        return False

    def clear(self):
        """Reset the rules store"""
        rules_cache = self.rules
        self.rules = {}
        def read_cache():
            return rules_cache
        return read_cache
