def redacc(iterable, expression, starting_value):
    """Functional iterative reduce with a starting accumulator value"""
    accumulator = starting_value
    for current_value in iterable:
        accumulator = expression(current_value, accumulator)
    return accumulator
