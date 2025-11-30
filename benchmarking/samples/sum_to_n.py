"""Sum function with tail recursion."""


def sum_to_n(n: int, acc: int = 0) -> int:
    """Calculate the sum from 1 to n using tail recursion.

    Args:
        n: The upper bound of the sum
        acc: Accumulator for tail recursion

    Returns:
        (1 + 2 + ... + n)
    """
    if n == 0:
        return acc
    return sum_to_n(n - 1, acc + n)
