"""Example usage of the tacopy tail-call optimization decorator."""

import tacopy


@tacopy.tacopy
def factorial_mod_k(acc: int, n: int, k: int) -> int:
    """
    Calculate (acc * n!) mod k using tail recursion.

    This function would normally cause a stack overflow for large n,
    but with the @tacopy decorator, it's transformed into an iterative loop.
    """
    if n == 0:
        return acc % k
    return factorial_mod_k(acc * n % k, n - 1, k)


@tacopy.tacopy
def fibonacci(n: int, a: int = 0, b: int = 1) -> int:
    """
    Calculate the nth Fibonacci number using tail recursion.

    Args:
        n: Which Fibonacci number to calculate
        a: First accumulator (default 0)
        b: Second accumulator (default 1)

    Returns:
        The nth Fibonacci number
    """
    if n == 0:
        return a
    if n == 1:
        return b
    return fibonacci(n - 1, b, a + b)


@tacopy.tacopy
def gcd(a: int, b: int) -> int:
    """
    Calculate the greatest common divisor using Euclidean algorithm.

    This is a classic example of tail recursion.
    """
    if b == 0:
        return a
    return gcd(b, a % b)


def main():
    """Run example calculations."""
    print("Tacopy - Tail-Call Optimization for Python")
    print("=" * 50)

    # Example 1: Large factorial mod k (would normally stack overflow)
    print("\n1. Factorial mod k:")
    result = factorial_mod_k(1, 1_000_000, 79)
    print(f"   factorial_mod_k(1, 1_000_000, 79) = {result}")

    # Example 2: Large Fibonacci number
    print("\n2. Fibonacci:")
    print(f"   fibonacci(10) = {fibonacci(10)}")
    print(f"   fibonacci(100) = {fibonacci(100)}")
    print(f"   fibonacci(5000) = {fibonacci(5000)}")

    # Example 3: GCD
    print("\n3. GCD (Euclidean algorithm):")
    print(f"   gcd(48, 18) = {gcd(48, 18)}")
    print(f"   gcd(1071, 462) = {gcd(1071, 462)}")

    print("\n" + "=" * 50)
    print("All examples completed successfully!")
    print("\nThe @tacopy decorator transformed these recursive")
    print("functions into iterative loops, preventing stack overflow.")


if __name__ == "__main__":
    main()
