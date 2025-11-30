"""Unit tests for the tail recursion validator."""

import pytest

from tacopy.validator import TailRecursionError, validate_tail_recursive


def test_valid_simple_tail_recursion():
    """Test that a simple tail-recursive function is accepted."""

    def factorial(n: int, acc: int = 1) -> int:
        if n == 0:
            return acc
        return factorial(n - 1, acc * n)

    # Should not raise
    validate_tail_recursive(factorial)


def test_valid_tail_recursion_with_multiple_returns():
    """Test that a tail-recursive function with multiple base cases is accepted."""

    def fibonacci_tail(n: int, a: int = 0, b: int = 1) -> int:
        if n == 0:
            return a
        if n == 1:
            return b
        return fibonacci_tail(n - 1, b, a + b)

    # Should not raise
    validate_tail_recursive(fibonacci_tail)


def test_valid_tail_recursion_with_conditional_expression():
    """Test that tail recursion with conditional expressions is accepted."""

    def max_list(lst, current_max=None):
        if not lst:
            return current_max
        head = lst[0]
        new_max = head if current_max is None else (head if head > current_max else current_max)
        return max_list(lst[1:], new_max)

    # Should not raise
    validate_tail_recursive(max_list)


def test_invalid_not_tail_recursive():
    """Test that a non-tail-recursive function is rejected."""

    def factorial(n: int) -> int:
        if n == 0:
            return 1
        return n * factorial(n - 1)  # NOT tail recursive - multiplication after call

    with pytest.raises(TailRecursionError) as exc_info:
        validate_tail_recursive(factorial)

    assert "not in tail position" in str(exc_info.value)


def test_invalid_recursive_in_arithmetic():
    """Test that recursive calls in arithmetic expressions are rejected."""

    def sum_to_n(n: int) -> int:
        if n == 0:
            return 0
        return n + sum_to_n(n - 1)  # NOT tail recursive

    with pytest.raises(TailRecursionError) as exc_info:
        validate_tail_recursive(sum_to_n)

    assert "not in tail position" in str(exc_info.value)


def test_invalid_recursive_in_function_call():
    """Test that recursive calls as arguments to other functions are rejected."""

    def bad_function(n: int) -> int:
        if n == 0:
            return 0
        return abs(bad_function(n - 1))  # NOT tail recursive

    with pytest.raises(TailRecursionError) as exc_info:
        validate_tail_recursive(bad_function)

    assert "not in tail position" in str(exc_info.value)


def test_async_function_rejected():
    """Test that async functions are rejected."""

    async def async_factorial(n: int, acc: int = 1) -> int:
        if n == 0:
            return acc
        return await async_factorial(n - 1, acc * n)

    with pytest.raises(TailRecursionError) as exc_info:
        validate_tail_recursive(async_factorial)

    assert "Async function" in str(exc_info.value)
    assert "not supported" in str(exc_info.value)


def test_valid_with_modulo():
    """Test the example from the design doc."""

    def factorial_mod_k(acc: int, n: int, k: int) -> int:
        if n == 0:
            return acc % k
        return factorial_mod_k(acc * n % k, n - 1, k)

    # Should not raise
    validate_tail_recursive(factorial_mod_k)


def test_non_recursive_function():
    """Test that non-recursive functions are accepted."""

    def not_recursive(n: int) -> int:
        return n * 2

    # Should not raise (no recursive calls found)
    validate_tail_recursive(not_recursive)


def test_mutually_recursive_not_detected():
    """Test that mutually recursive functions are not detected as self-recursive."""

    def even(n: int) -> bool:
        if n == 0:
            return True
        return odd(n - 1)

    def odd(n: int) -> bool:
        if n == 0:
            return False
        return even(n - 1)

    # Should not raise - each function doesn't call itself
    validate_tail_recursive(even)
    validate_tail_recursive(odd)
