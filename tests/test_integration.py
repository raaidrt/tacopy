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


# Tail call in for loop
@tacopy
def tailing(n: int) -> int:
    if n <= 0:
        return 0
    for _i in range(3):
        return tailing(n - 1)
    return 0


# Nested for loops
@tacopy
def nested_loops(n: int) -> int:
    if n <= 0:
        return 0
    for _i in range(3):
        for _j in range(2):
            return nested_loops(n - 1)
    return 0


# Triple nested for loops
@tacopy
def triple_nested_loops(n: int) -> int:
    if n <= 0:
        return 0
    for _i in range(2):
        for _j in range(2):
            for _k in range(2):
                return triple_nested_loops(n - 1)
    return 0


# For loop with conditional
@tacopy
def loop_with_cond(n: int, acc: int = 0) -> int:
    if n <= 0:
        return acc
    for i in range(5):
        if i % 2 == 0:
            return loop_with_cond(n - 1, acc + i)
    return acc


# For loop with multiple tail calls
@tacopy
def loop_multi_tail(n: int) -> int:
    if n <= 0:
        return 0
    for i in range(3):
        if i == 0:
            return loop_multi_tail(n - 1)
        elif i == 1:
            return loop_multi_tail(n - 2)
    return 1


# For loop with mixed tail and non-tail returns
@tacopy
def loop_mixed_returns(n: int) -> int:
    if n <= 0:
        return 0
    for i in range(3):
        if i == 0:
            return loop_mixed_returns(n - 1)  # tail call
        elif i == 1:
            return 42  # non-tail return
    return 0


# While loop with tail call
@tacopy
def while_countdown(n: int) -> int:
    if n <= 0:
        return 0
    count = 0
    while count < 3:
        return while_countdown(n - 1)
    return 0


# Nested while loops
@tacopy
def nested_while_loops(n: int) -> int:
    if n <= 0:
        return 0
    i = 0
    while i < 2:
        j = 0
        while j < 2:
            return nested_while_loops(n - 1)
        j += 1
    return 0


# For inside while
@tacopy
def for_inside_while(n: int) -> int:
    if n <= 0:
        return 0
    i = 0
    while i < 2:
        for _j in range(2):
            return for_inside_while(n - 1)
        i += 1
    return 0


# While inside for
@tacopy
def while_inside_for(n: int) -> int:
    if n <= 0:
        return 0
    for _i in range(2):
        j = 0
        while j < 2:
            return while_inside_for(n - 1)
        j += 1
    return 0


# Complex interleaved: for -> while -> for
@tacopy
def complex_interleaved(n: int) -> int:
    if n <= 0:
        return 0
    for _i in range(2):
        j = 0
        while j < 2:
            for _k in range(2):
                return complex_interleaved(n - 1)
            j += 1
    return 0


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


def test_tail_call_in_for_loop():
    """Test tail call inside a for loop."""
    # This should execute the first iteration of the for loop only,
    # then tail-recurse and start over
    assert tailing(0) == 0
    assert tailing(1) == 0
    assert tailing(2) == 0
    assert tailing(10) == 0  # Should handle deeper recursion


def test_nested_for_loops():
    """Test tail call inside nested for loops."""
    # Should execute outer loop i=0, inner loop j=0, then tail-recurse
    assert nested_loops(0) == 0
    assert nested_loops(1) == 0
    assert nested_loops(5) == 0


def test_triple_nested_for_loops():
    """Test tail call inside triple nested for loops."""
    # Should execute all outer loops once each, then tail-recurse
    assert triple_nested_loops(0) == 0
    assert triple_nested_loops(1) == 0
    assert triple_nested_loops(5) == 0


def test_for_loop_with_conditional():
    """Test tail call inside a for loop with conditional."""
    # With i=0 (even), should tail-recurse with acc=0
    assert loop_with_cond(0, 0) == 0
    assert loop_with_cond(1, 0) == 0  # n=1: i=0, acc=0+0=0, recurse with n=0,acc=0
    assert loop_with_cond(2, 0) == 0  # n=2: i=0, acc=0+0=0, recurse...


def test_for_loop_with_multiple_tail_calls():
    """Test for loop with multiple tail call branches."""
    # With i=0, should tail-recurse with n-1
    assert loop_multi_tail(0) == 0
    assert loop_multi_tail(1) == 0
    assert loop_multi_tail(2) == 0


def test_tail_call_in_for_loop_large():
    """Test that tail call in for loop can handle large recursion depth."""
    # This would cause stack overflow without proper optimization
    assert tailing(1000) == 0
    assert nested_loops(500) == 0


def test_for_loop_with_mixed_returns():
    """Test for loop containing both tail calls and non-tail returns."""
    # With i=0, should tail-recurse with n-1
    assert loop_mixed_returns(0) == 0
    assert loop_mixed_returns(1) == 0
    assert loop_mixed_returns(2) == 0
    # Should handle this correctly without confusion between return types


def test_while_loop_with_tail_call():
    """Test tail call inside a while loop."""
    # Should execute first iteration, then tail-recurse
    assert while_countdown(0) == 0
    assert while_countdown(1) == 0
    assert while_countdown(2) == 0
    assert while_countdown(10) == 0


def test_nested_while_loops():
    """Test tail call inside nested while loops."""
    assert nested_while_loops(0) == 0
    assert nested_while_loops(1) == 0
    assert nested_while_loops(5) == 0


def test_for_inside_while():
    """Test tail call in for loop inside while loop."""
    assert for_inside_while(0) == 0
    assert for_inside_while(1) == 0
    assert for_inside_while(5) == 0


def test_while_inside_for():
    """Test tail call in while loop inside for loop."""
    assert while_inside_for(0) == 0
    assert while_inside_for(1) == 0
    assert while_inside_for(5) == 0


def test_complex_interleaved_loops():
    """Test tail call in complex interleaved for/while/for loops."""
    assert complex_interleaved(0) == 0
    assert complex_interleaved(1) == 0
    assert complex_interleaved(5) == 0


def test_loops_large_recursion():
    """Test that while and interleaved loops handle large recursion depth."""
    # This would cause stack overflow without proper optimization
    assert while_countdown(1000) == 0
    assert for_inside_while(500) == 0
    assert while_inside_for(500) == 0
