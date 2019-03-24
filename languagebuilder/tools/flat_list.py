def flatten(l):
    """"Take a nested list and return a flattened version with no sublists"""
    # reached individual list item or recursion depth
    if not isinstance(l, (list, set, tuple)):
        return [l]

    # reached another list - flatten it
    flat_l = []
    # recurse through sublists
    for l_sub in l:
        flat_l += flatten(l_sub)

    return flat_l
