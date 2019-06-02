def is_string_list(l):
    """Check for a flat list containing only string elements"""
    str_l = filter_string_list(l)
    return len(str_l) == len(l)
    
def filter_string_list(l):
    return [e for e in l if isinstance(e, str)]

def string_listify(elem, segment=False):
    """Turn a string into a one-element string list but
    return string collections as lists."""
    if isinstance(elem, str):
        return list(elem) if segment else [elem]
    if not is_string_list(elem):
        return
    return list(elem)
