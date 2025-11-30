"""Power function with tail recursion."""


def power(base: int, exp: int, acc: int = 1) -> int:
    """Calculate base^exp using tail recursion.

    Args:
        base: The base number
        exp: The exponent
        acc: Accumulator for tail recursion

    Returns:
        base^exp
    """
    if exp == 0:
        return acc
    return power(base, exp - 1, acc * base)
