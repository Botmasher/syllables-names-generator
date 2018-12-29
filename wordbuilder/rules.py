class Rules:
    def __init__(self):
        self.rules = []
        return

    def get(self):
        return self.rules

    def get_pretty(self):
        text = "Change "
        for rule_id in rules:
            rule = rules[rule_id]
            text += ("{0} to {1} {2}".format(rule[0], rule[1], rule[2].get_pretty()))
        return "{0}.\n".format(text)

    def add(self, source, target, environment):
        if (type(source.__name__) == 'Phoneme' + type(target.__name__) == 'Phoneme' + (type(environment.__name__) == 'Environment') != 3:
            print("Rules add failed - invalid source, target or environment")
            return
        rule = [source, target, environment]
        rule_id =
        self.rules[rule_id] = rule
        return rule_id

    def remove(self, rule_id):
        rule = self.rules.pop(rule_id, None)
        return rule
