"""Fibonacci function with tail recursion."""


def fibonacci(n: int, a: int = 0, b: int = 1) -> int:
    """Calculate the nth Fibonacci number using tail recursion.

    Args:
        n: The index of the Fibonacci number to compute
        a: First accumulator (default 0)
        b: Second accumulator (default 1)

    Returns:
        fib(n)
    """
    if n == 0:
        return a
    if n == 1:
        return b
    return fibonacci(n - 1, b, a + b)
