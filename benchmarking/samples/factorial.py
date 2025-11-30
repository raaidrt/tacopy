"""Factorial function with tail recursion."""


def factorial(n: int, acc: int = 1) -> int:
    """Calculate n! using tail recursion with an accumulator.

    Args:
        n: The number to compute factorial for
        acc: Accumulator for tail recursion

    Returns:
        n!
    """
    if n == 0:
        return acc
    return factorial(n - 1, acc * n)
