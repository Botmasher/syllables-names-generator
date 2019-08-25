from collections import deque

def tuplify(l):
    """Convert deep lists into deep tuples"""
    if not isinstance(l, (list, set, tuple, deque)):
        return l
    t = tuple(tuplify(sub_l) for sub_l in l)
    return t

def untuplify(t):
    """Revert deep tuples back to deep lists"""
    if not isinstance(t, (tuple)):
        return t
    l = [untuplify(sub_t) for sub_t in t]
    return l

def flatten(l, depth=None):
    """"Take a nested sequence and return a flattened list with no subcollections"""
    # reached individual list item or recursion depth
    if is_primitive(l):
        return [l]

    # optionally break at specific recursion depth
    if isinstance(depth, int):
        if depth <= 0:
            return l
        depth -= 1

    # reached another list - flatten it
    flat_l = []
    # recurse through sublists
    for l_sub in l:
        flat_l += flatten(l_sub, depth)

    return flat_l

def is_primitive(l):
    """Check if the value is considered a flatlist primitive"""
    return not isinstance(l, (list, set, tuple, deque))

def flat_map(expression, l):
    """Flatten and run expression on all elements in all sublists"""
    if is_primitive(l):
        return expression(l)
    return [
        flat_map(expression, l)
        for l_sub in l
    ]

def flat_filter(expression, l):
    """Flatten and filter all elements in all sublists"""
    if is_primitive(l):
        return [l] if expression(l) else None
    return [
        flat_map(expression, sub_l)
        for sub_l in l
        if expression
    ]
