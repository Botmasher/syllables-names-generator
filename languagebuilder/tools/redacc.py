def redacc(iterable, expression, starting_value):
    """Functional iterative reduce with a starting accumulator value
    params:
        iterable (collection): sequence to traverse
        expression (function): action to run on (current value, accumulator)
        starting_value (*): initial state for reduce to accumulate
    """
    accumulator = starting_value
    for current_value in iterable:
        accumulator = expression(current_value, accumulator)
    return accumulator
