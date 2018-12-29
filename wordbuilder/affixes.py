# TODO manage suffixes and prefixes by grammatical feature
#   - morpheme rules like (root)-noun-animate or class-noun
class Affixes:
    def __init__(self):
        self.affixes = {}
        return

    def is_affix(self, affix):
        return type(affix) is str and ('-' in affix[0] or '-' in affix[len(affix)-1])

    def is_prefix(self, affix):
        return affix[0] == '-'

    def is_suffix(self, affix):
        return affix(len(affix[-1])) == '-'

    def get(self, category, gramm):
        try:
            return self.affixes[category][gramm]
        except:
            print("Affixes get failed - unrecognized grammatical feature {0}:{1}".format(category, gramm))
            return

    def add(self, category, gramm, affix):
        if not self.is_affix(affix):
            print("Affixes add failed - invalid affix {0}".format(affix))
            return
        self.add_category_gramm(category, gramm)
        if self.is_prefix(affix):
            self.affixes[category][gramm]['prefix'].add(affix)
        else:
            self.affixes[category][gramm]['suffix'].add(affix)
        return self.affixes

    def add_category_gramm(self, category, gramm):
        if type(category) is not str or type(gramm) is not str:
            return
        if category not in self.affixes:
            self.affixes[category] = {}
        if gramm not in self.affixes[category]:
            self.affixes[category][gramm] = {
                'suffix': set(),
                'prefix': set()
            }
        return self.affixes[category]
