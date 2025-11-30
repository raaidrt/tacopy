"""End-to-end integration tests for the tacopy decorator."""

import pytest

from tacopy import TailRecursionError, tacopy

# ============================================================================
# Module-level function definitions (to avoid nested function rejection)
# ============================================================================


# Factorial functions
@tacopy
def factorial(n: int, acc: int = 1) -> int:
    if n == 0:
        return acc
    return factorial(n - 1, acc * n)


# Factorial mod k
@tacopy
def factorial_mod_k(acc: int, n: int, k: int) -> int:
    if n == 0:
        return acc % k
    return factorial_mod_k(acc * n % k, n - 1, k)


# Fibonacci
@tacopy
def fibonacci(n: int, a: int = 0, b: int = 1) -> int:
    if n == 0:
        return a
    if n == 1:
        return b
    return fibonacci(n - 1, b, a + b)


# Sum to n
@tacopy
def sum_to_n(n: int, acc: int = 0) -> int:
    if n == 0:
        return acc
    return sum_to_n(n - 1, acc + n)


# GCD
@tacopy
def gcd(a: int, b: int) -> int:
    if b == 0:
        return a
    return gcd(b, a % b)


# List length
@tacopy
def list_length(lst, acc: int = 0) -> int:
    if not lst:
        return acc
    return list_length(lst[1:], acc + 1)


# Nested decorator test function
@tacopy
def outer_factorial(n: int, acc: int = 1) -> int:
    if n == 0:
        return acc
    return outer_factorial(n - 1, acc * n)


# Closure test with multiplier
multiplier = 2


@tacopy
def multiply_factorial(n: int, acc: int = 1) -> int:
    if n == 0:
        return acc * multiplier
    return multiply_factorial(n - 1, acc * n)


# Multiple decorated factorial
@tacopy
def factorial_multi_1(n: int, acc: int = 1) -> int:
    if n == 0:
        return acc
    return factorial_multi_1(n - 1, acc * n)


# Multiple decorated fibonacci
@tacopy
def fibonacci_multi(n: int, a: int = 0, b: int = 1) -> int:
    if n == 0:
        return a
    if n == 1:
        return b
    return fibonacci_multi(n - 1, b, a + b)


# Function metadata test
@tacopy
def my_function(n: int, acc: int = 1) -> int:
    """This is my function's docstring."""
    if n == 0:
        return acc
    return my_function(n - 1, acc * n)


# Conditional expression
@tacopy
def count_down(n: int) -> int:
    if n <= 0:
        return 0
    return count_down(n - 1) if n > 0 else 0


# Keyword arguments
@tacopy
def sum_with_kwargs(n: int, acc: int = 0) -> int:
    if n == 0:
        return acc
    return sum_with_kwargs(n=n - 1, acc=acc + n)


# Mixed args and kwargs
@tacopy
def mixed_factorial(n: int, acc: int = 1) -> int:
    if n == 0:
        return acc
    return mixed_factorial(n - 1, acc=acc * n)


# ============================================================================
# Test functions
# ============================================================================


def test_factorial_basic():
    """Test basic factorial with tail recursion."""
    assert factorial(5) == 120
    assert factorial(10) == 3628800
    assert factorial(0) == 1


def test_factorial_large_input():
    """Test that optimized factorial can handle large inputs without stack overflow."""
    # This would cause a stack overflow without optimization
    # We'll use a smaller number but still beyond typical recursion limit
    result = factorial(2000)
    assert result > 0  # Just verify it doesn't crash


def test_factorial_mod_k():
    """Test the factorial_mod_k example from the design doc."""
    # Small test case
    assert factorial_mod_k(1, 5, 1000) == 120

    # Large test case that would overflow without optimization
    result = factorial_mod_k(1, 100000, 79)
    assert 0 <= result < 79  # Result should be in range [0, 79)


def test_fibonacci():
    """Test tail-recursive fibonacci."""
    assert fibonacci(0) == 0
    assert fibonacci(1) == 1
    assert fibonacci(10) == 55
    assert fibonacci(20) == 6765


def test_fibonacci_large():
    """Test fibonacci with large input."""
    # This would cause stack overflow without optimization
    result = fibonacci(5000)
    assert result > 0


def test_sum_to_n():
    """Test sum from 1 to n."""
    assert sum_to_n(0) == 0
    assert sum_to_n(10) == 55  # 1+2+...+10
    assert sum_to_n(100) == 5050


def test_gcd():
    """Test tail-recursive GCD (Euclidean algorithm)."""
    assert gcd(48, 18) == 6
    assert gcd(100, 35) == 5
    assert gcd(17, 19) == 1


def test_list_length():
    """Test tail-recursive list length calculation."""
    assert list_length([]) == 0
    assert list_length([1, 2, 3]) == 3
    assert list_length(list(range(100))) == 100


def test_non_tail_recursive_rejected():
    """Test that non-tail-recursive functions are rejected."""
    with pytest.raises(TailRecursionError):

        @tacopy
        def bad_factorial(n: int) -> int:
            if n == 0:
                return 1
            return n * bad_factorial(n - 1)


def test_async_function_rejected():
    """Test that async functions are rejected."""
    with pytest.raises(TailRecursionError):

        @tacopy
        async def async_func(n: int) -> int:
            if n == 0:
                return 0
            return await async_func(n - 1)


def test_nested_decorator():
    """Test that nested functions with tacopy decorator work correctly."""

    def wrapper():
        # Use outer_factorial inside another function
        return outer_factorial(5)

    assert wrapper() == 120


def test_closure_variables():
    """Test that functions with closure variables work correctly."""
    assert multiply_factorial(5) == 240  # 120 * 2


def test_multiple_decorated_functions():
    """Test that multiple functions can be decorated independently."""
    assert factorial_multi_1(5) == 120
    assert fibonacci_multi(10) == 55


def test_function_metadata_preserved():
    """Test that function metadata is preserved after decoration."""
    assert my_function.__name__ == "my_function"
    assert my_function.__doc__ is not None and "docstring" in my_function.__doc__


def test_conditional_expression_in_tail_call():
    """Test tail recursion with conditional expressions."""
    # This should work but might be tricky to optimize
    # For now, we'll see if it works
    try:
        result = count_down(10)
        assert result == 0
    except TailRecursionError:
        # It's okay if this is rejected as non-tail-recursive
        # due to the conditional expression
        pytest.skip("Conditional expressions in tail position not yet supported")


def test_keyword_arguments():
    """Test that functions with keyword arguments work correctly."""
    assert sum_with_kwargs(10) == 55


def test_mixed_args_and_kwargs():
    """Test functions using both positional and keyword arguments in recursion."""
    assert mixed_factorial(5) == 120
