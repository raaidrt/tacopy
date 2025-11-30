"""GCD function with tail recursion."""


def gcd(a: int, b: int) -> int:
    """Calculate the greatest common divisor using Euclidean algorithm (tail recursive)."""
    if b == 0:
        return a
    return gcd(b, a % b)
