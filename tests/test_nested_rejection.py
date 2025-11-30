"""
Test that @tacopy correctly rejects nested functions.

The @tacopy decorator can only be applied to module-level functions,
not to functions nested inside other functions.
"""

import pytest

from tacopy import TailRecursionError, tacopy


def test_nested_decorator_rejected():
    """Test that @tacopy on a nested function raises TailRecursionError."""
    with pytest.raises(TailRecursionError) as exc_info:

        def outer(n: int) -> int:
            @tacopy  # This should raise an error
            def inner(m: int) -> int:
                if m == 0:
                    return 0
                return inner(m - 1)

            return inner(n)

        # Trigger the decorator
        outer(5)

    # Verify the error message is helpful
    assert "nested function" in str(exc_info.value).lower()
    assert "module level" in str(exc_info.value).lower()


def test_nested_in_outer_function_rejected():
    """Test that nested function inside a regular function is rejected."""

    def outer_regular_function():
        @tacopy  # Should raise error - nested inside outer_regular_function
        def nested_tail_recursive(n: int, acc: int = 0) -> int:
            if n == 0:
                return acc
            return nested_tail_recursive(n - 1, acc + n)

        return nested_tail_recursive(10)

    with pytest.raises(TailRecursionError) as exc_info:
        outer_regular_function()

    assert "nested function" in str(exc_info.value).lower()


def test_error_message_includes_function_name():
    """Test that error message includes the nested function's name."""

    def container():
        @tacopy
        def my_special_function(n: int) -> int:
            if n == 0:
                return 0
            return my_special_function(n - 1)

        return my_special_function(5)

    with pytest.raises(TailRecursionError) as exc_info:
        container()

    assert "my_special_function" in str(exc_info.value)


# Module-level function for testing lambdas
@tacopy
def outer_with_lambda(n: int, acc: int = 0) -> int:
    """Tail-recursive function that uses a lambda (not decorated with @tacopy)."""
    # Lambda is fine (not decorated with @tacopy)
    helper = lambda x: x * 2  # noqa: E731

    if n == 0:
        return acc
    return outer_with_lambda(n - 1, acc + helper(n))


def test_lambda_inside_function_not_affected():
    """Test that lambdas and non-decorated nested functions still work."""
    # Should work without errors
    result = outer_with_lambda(5)
    assert result == 2 + 4 + 6 + 8 + 10  # 30


# Module-level helper functions for testing the workaround
@tacopy
def factorial_mod_helper(acc: int, m: int, mod: int) -> int:
    """Helper function at module level."""
    if m == 0:
        return acc % mod
    return factorial_mod_helper((acc * m) % mod, m - 1, mod)


@tacopy
def compute_factorial_mod(n: int, k: int, acc: int = 1) -> int:
    """Main function that uses the module-level helper."""
    if n == 0:
        # Call the module-level helper
        return factorial_mod_helper(acc, 0, k)
    return compute_factorial_mod(n - 1, k, (acc * n) % k)


def test_workaround_extract_to_module_level():
    """Test the recommended workaround: extract nested function to module level."""
    # Both functions work because they're at module level
    result = factorial_mod_helper(1, 10, 100)
    assert 0 <= result < 100

    result2 = compute_factorial_mod(10, 100)
    assert 0 <= result2 < 100
