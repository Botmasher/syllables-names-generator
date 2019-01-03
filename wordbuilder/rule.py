# TODO rule management and prioritization
class Rule:
    def __init__(self, source=None, target=None, environment=None):
        self.set(source=source, target=target, environment=environment)
        return

    def get(self):
        return {
            'source': self.source,
            'target': self.target,
            'environment': self.environment
        }

    def get_pretty(self):
        """Format rule into a human readable statement."""
        text = "Change "
        text += ("{0} to {1} when the sound is {2}".format(
            self.source,
            self.target,
            self.environment.get_pretty()
        ))
        return "{0}.".format(text)

    def check(self):
        """Internal method for checking the validity of rule attributes"""
        if type(self.source.__name__) != 'Phoneme':
            print("Rule check failed - invalid source {0}".format(source))
            return False
        if type(self.target.__name__) != 'Phoneme'):
            print("Rule check failed - invalid target {0}".format(target))
            return False
        if type(self.environment.__name__) != 'Environment':
            print("Rule check failed - invalid environment {0}".format(environment))
            return False
        return True

    def set(self, source, target, environment):
        """Internal method for setting all rule attributes"""
        self.source = source
        self.target = target
        self.environment = environment
        return self.get()

    # TODO ? check source, target, environment in language
    # TODO use rule layering to apply in the right order
    def update(self, source=None, target=None, environment=None):
        """Set one or more rule attributes"""
        prev_rule = self.get()
        new_source = source if source else prev_rule['source']
        new_target = target if target else prev_rule['target']
        new_environment = environment if environment else prev_rule['environment']
        self.set(source, target, environment)
        if not self.check():
            self.set(prev_rule['source'], prev_rule['target'], prev_rule['environment'])
            return
        return self.get()

    def clear(self):
        self.source = None
        self.target = None
        self.environment = None
        return self.get()
