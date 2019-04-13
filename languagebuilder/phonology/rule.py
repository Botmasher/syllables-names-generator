# TODO rule management and prioritization
class Rule:
    def __init__(self, source=None, target=None, environment=None):
        self.set_rule(source=source, target=target, environment=environment)
        return

    def get(self):
        return {
            'source': self.source,
            'target': self.target,
            'environment': self.environment
        }

    def get_source(self):
        return self.source

    def get_target(self):
        return self.target

    def get_environment(self):
        return self.environment

    def get_pretty(self, use_notation=False):
        """Format rule into a human readable statement."""
        text = ""
        if use_notation:
            text += "{0} -> {1} / {2}"
        else:
            text += "Change {0} to {1} when it's {2}."
        return text.format(
            self.source,
            self.target,
            self.environment.get_pretty(use_notation=use_notation)
        )

    def check(self):
        """Internal method for checking the validity of rule attributes"""
        if not isinstance(self.source, list):
            print(f"Rule check failed - invalid source {self.source}")
            return False
        if not isinstance(self.target, list):
            print(f"Rule check failed - invalid target {self.target}")
            return False
        if type(self.environment.__name__) != 'Environment':
            print(f"Rule check failed - invalid environment {self.environment}")
            return False
        return True

    def set_rule(self, source, target, environment):
        """Internal method for setting all rule attributes"""
        self.source = [source] if isinstance(source, str) else source
        self.target = [target] if isinstance(target, str) else target
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
        self.set_rule(new_source, new_target, new_environment)
        if not self.check():
            self.set_rule(prev_rule['source'], prev_rule['target'], prev_rule['environment'])
            return
        return self.get()

    def clear(self):
        self.source = None
        self.target = None
        self.environment = None
        return self.get()
