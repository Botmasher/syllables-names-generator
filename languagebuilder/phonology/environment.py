# TODO store environments in rules
class Environment:
    def __init__(self, structure=None):
        self.set_structure(structure)

    def is_structure(self, structure):
        if isinstance(structure, list) and structure.count('_') == 1:
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
                    elif i == len(self.structure) - 1:
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

    # TODO: allow more complex environments including specific consonant/vowel features
    def set_structure(self, structure):
        """Create an environment structure from a features list or string"""
        # parse string abbreviations like '#_V'
        if isinstance(structure, str):
            short_symbols = {
                'C': ["consonant"],
                'V': ["vowel"],
                '_': "_",
                '#': "#"
            }
            structure = [short_symbols[symbol] for symbol in structure]
            #try:
            #    structure = [short_symbols[symbol] for symbol in structure]
            #except:
            #    print("Environment set_structure failed - unknown symbol {symbol}")
            #    return
        # store environment elements as list
        if self.is_structure(structure):
            self.structure = structure
        else:
            self.structure = None
        return self.structure
