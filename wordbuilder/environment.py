# TODO store environments in rules
class Environment:
    def __init__(self, structure=[]):
        self.set(structure)
        return

    def is_structure(self, structure):
        if type(structure) is list and structure.count('_') == 1:
            return True
        return False

    def get(self):
        return {'structure': self.structure}

    def get_structure(self):
        return self.structure

    def get_pretty(self, use_notation=False):
        """Format environment structure as human readable text"""
        body_text = ""
        intro_text = ""
        for i in range(len(self.structure)):
            slot = self.structure[i]
            # notation
            if use_notation:
                slot_txt = ""
                if 'consonant' in slot:
                    slot_txt += "C"
                elif 'vowel' in slot:
                    slot_txt += "V"
                elif slot == '_':
                    slot_txt += "_"
                features = ["+{0}".format(feature) for feature in slot if feature not in ('consonant', 'vowel')]
                if features:
                    body += "{0}({1})".format(slot_txt, ",".join(features))
                else:
                    body += "{0}".format(slot_txt)
                continue
            # verbose
            line = ""
            if type(slot) is list:
                line += "an " if slot[0][0].lower() in ['a', 'e', 'i', 'o', 'u'] else "a "
                for feature in slot:
                    line += ("{0}, ".format(feature))
            elif type(slot) is str:
                if slot == "_":
                    if i == 0:
                        intro_text += "before "
                    elif i == len(self.structure) - 1:
                        intro_text += "after "
                    else:
                        intro_text += "between "
                        line += " and "
                else:
                    line += "a {0}".format(slot)
            else:
                pass
            body_text += line
        if body_text[(len(body_text)-2):] == ", ":
            body_text = body_text[:-2]
        return "{0}{1}".format(intro_text, body_text)

    def set(self, structure):
        # parse short strings like 'C_C'
        if type(structure) is str:
            parsed_structure = []
            short_symbols = {'C': ["consonant"], 'V': ["vowel"], '_': "_"}
            for symbol in structure:
                if symbol in short_symbols.keys():
                    parsed_structure.append(symbol)
                else:
                    print("Environment failed to set - unknown structure symbol {0}".format(symbol))
                    return
            structure = parsed_structure
        # store environment elements as list
        if self.is_structure(structure):
            self.structure = structure
        else:
            self.structure = None
        return self.structure
