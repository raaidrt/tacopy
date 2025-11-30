"""
Correctness tests for tacopy decorator.

Each test creates two versions of a function:
1. Manual iterative version (ground truth)
2. Tail-recursive version with @tacopy decorator

Both are tested with the same inputs to ensure identical results.
"""

from tacopy import tacopy

# ============================================================================
# Module-level function definitions (to avoid nested function rejection)
# ============================================================================


# Factorial functions
def factorial_iterative(n: int, acc: int = 1) -> int:
    while n > 0:
        acc = acc * n
        n = n - 1
    return acc


@tacopy
def factorial_recursive(n: int, acc: int = 1) -> int:
    if n == 0:
        return acc
    return factorial_recursive(n - 1, acc * n)


# Factorial mod k functions
def factorial_mod_k_iterative(acc: int, n: int, k: int) -> int:
    while n > 0:
        acc = (acc * n) % k
        n = n - 1
    return acc % k


@tacopy
def factorial_mod_k_recursive(acc: int, n: int, k: int) -> int:
    if n == 0:
        return acc % k
    return factorial_mod_k_recursive(acc * n % k, n - 1, k)


# Fibonacci functions
def fibonacci_iterative(n: int, a: int = 0, b: int = 1) -> int:
    while n > 0:
        if n == 1:
            return b
        a, b = b, a + b
        n = n - 1
    return a


@tacopy
def fibonacci_recursive(n: int, a: int = 0, b: int = 1) -> int:
    if n == 0:
        return a
    if n == 1:
        return b
    return fibonacci_recursive(n - 1, b, a + b)


# GCD functions
def gcd_iterative(a: int, b: int) -> int:
    while b != 0:
        a, b = b, a % b
    return a


@tacopy
def gcd_recursive(a: int, b: int) -> int:
    if b == 0:
        return a
    return gcd_recursive(b, a % b)


# Sum to n functions
def sum_to_n_iterative(n: int, acc: int = 0) -> int:
    while n > 0:
        acc = acc + n
        n = n - 1
    return acc


@tacopy
def sum_to_n_recursive(n: int, acc: int = 0) -> int:
    if n == 0:
        return acc
    return sum_to_n_recursive(n - 1, acc + n)


# List length functions
def list_length_iterative(lst, acc: int = 0) -> int:
    while lst:
        acc = acc + 1
        lst = lst[1:]
    return acc


@tacopy
def list_length_recursive(lst, acc: int = 0) -> int:
    if not lst:
        return acc
    return list_length_recursive(lst[1:], acc + 1)


# List sum functions
def list_sum_iterative(lst, acc: int = 0) -> int:
    while lst:
        acc = acc + lst[0]
        lst = lst[1:]
    return acc


@tacopy
def list_sum_recursive(lst, acc: int = 0) -> int:
    if not lst:
        return acc
    return list_sum_recursive(lst[1:], acc + lst[0])


# List reverse functions
def list_reverse_iterative(lst, acc=None):
    if acc is None:
        acc = []
    while lst:
        acc = [lst[0]] + acc
        lst = lst[1:]
    return acc


@tacopy
def list_reverse_recursive(lst, acc=None):
    if acc is None:
        acc = []
    if not lst:
        return acc
    return list_reverse_recursive(lst[1:], [lst[0]] + acc)


# Power functions
def power_iterative(base: int, exp: int, acc: int = 1) -> int:
    while exp > 0:
        acc = acc * base
        exp = exp - 1
    return acc


@tacopy
def power_recursive(base: int, exp: int, acc: int = 1) -> int:
    if exp == 0:
        return acc
    return power_recursive(base, exp - 1, acc * base)


# Countdown functions
def count_down_iterative(n: int, acc: int = 0) -> int:
    while n > 0:
        acc = acc + 1
        n = n - 1
    return acc


@tacopy
def count_down_recursive(n: int, acc: int = 0) -> int:
    if n <= 0:
        return acc
    return count_down_recursive(n - 1, acc + 1)


# Is even functions
def is_even_iterative(n: int) -> bool:
    while n > 1:
        n = n - 2
    return n == 0


@tacopy
def is_even_recursive(n: int) -> bool:
    if n == 0:
        return True
    if n == 1:
        return False
    return is_even_recursive(n - 2)


# All positive functions
def all_positive_iterative(lst) -> bool:
    while lst:
        if lst[0] <= 0:
            return False
        lst = lst[1:]
    return True


@tacopy
def all_positive_recursive(lst) -> bool:
    if not lst:
        return True
    if lst[0] <= 0:
        return False
    return all_positive_recursive(lst[1:])


# Find max functions
def find_max_iterative(lst, current_max=None):
    while lst:
        head = lst[0]
        if current_max is None or head > current_max:
            current_max = head
        lst = lst[1:]
    return current_max


@tacopy
def find_max_recursive(lst, current_max=None):
    if not lst:
        return current_max
    head = lst[0]
    new_max = head if current_max is None else (head if head > current_max else current_max)
    return find_max_recursive(lst[1:], new_max)


# Sum with kwargs functions
def sum_kwargs_iterative(n: int, acc: int = 0) -> int:
    while n > 0:
        acc = acc + n
        n = n - 1
    return acc


@tacopy
def sum_kwargs_recursive(n: int, acc: int = 0) -> int:
    if n == 0:
        return acc
    return sum_kwargs_recursive(n=n - 1, acc=acc + n)


# Mixed args functions
def factorial_mixed_iterative(n: int, acc: int = 1) -> int:
    while n > 0:
        acc = acc * n
        n = n - 1
    return acc


@tacopy
def factorial_mixed_recursive(n: int, acc: int = 1) -> int:
    if n == 0:
        return acc
    return factorial_mixed_recursive(n - 1, acc=acc * n)


# Sum of squares functions
def sum_of_squares_iterative(n: int, acc: int = 0) -> int:
    while n > 0:
        acc = acc + n * n
        n = n - 1
    return acc


@tacopy
def sum_of_squares_recursive(n: int, acc: int = 0) -> int:
    if n == 0:
        return acc
    return sum_of_squares_recursive(n - 1, acc + n * n)


# Collatz length functions
def collatz_length_iterative(n: int, acc: int = 0) -> int:
    while n != 1:
        acc = acc + 1
        if n % 2 == 0:
            n = n // 2
        else:
            n = 3 * n + 1
    return acc


@tacopy
def collatz_length_recursive(n: int, acc: int = 0) -> int:
    if n == 1:
        return acc
    if n % 2 == 0:
        return collatz_length_recursive(n // 2, acc + 1)
    else:
        return collatz_length_recursive(3 * n + 1, acc + 1)


# Sum of digits functions
def sum_of_digits_iterative(n: int, acc: int = 0) -> int:
    while n > 0:
        acc = acc + n % 10
        n = n // 10
    return acc


@tacopy
def sum_of_digits_recursive(n: int, acc: int = 0) -> int:
    if n == 0:
        return acc
    return sum_of_digits_recursive(n // 10, acc + n % 10)


# Digit count functions
def digit_count_iterative(n: int, acc: int = 0) -> int:
    if n == 0 and acc == 0:
        return 1
    while n > 0:
        acc = acc + 1
        n = n // 10
    return acc


@tacopy
def digit_count_recursive(n: int, acc: int = 0) -> int:
    if n == 0 and acc == 0:
        return 1
    if n == 0:
        return acc
    return digit_count_recursive(n // 10, acc + 1)


# Sign sum functions
def sign_sum_iterative(lst, acc: int = 0):
    while lst:
        val = lst[0]
        if val > 0:
            acc = acc + 1
        elif val < 0:
            acc = acc - 1
        # val == 0: no change to acc
        lst = lst[1:]
    return acc


@tacopy
def sign_sum_recursive(lst, acc: int = 0):
    if not lst:
        return acc
    val = lst[0]
    if val > 0:
        return sign_sum_recursive(lst[1:], acc + 1)
    elif val < 0:
        return sign_sum_recursive(lst[1:], acc - 1)
    else:
        return sign_sum_recursive(lst[1:], acc)


# Deep factorial functions
def factorial_mod_iterative(n: int, k: int, acc: int = 1) -> int:
    while n > 0:
        acc = (acc * n) % k
        n = n - 1
    return acc


@tacopy
def factorial_mod_recursive(n: int, k: int, acc: int = 1) -> int:
    if n == 0:
        return acc
    return factorial_mod_recursive(n - 1, k, (acc * n) % k)


# Deep sum functions
def sum_deep_iterative(n: int, acc: int = 0) -> int:
    while n > 0:
        acc = acc + n
        n = n - 1
    return acc


@tacopy
def sum_deep_recursive(n: int, acc: int = 0) -> int:
    if n == 0:
        return acc
    return sum_deep_recursive(n - 1, acc + n)


# Immediate return functions
def immediate_iterative(n: int) -> int:
    return n


@tacopy
def immediate_recursive(n: int) -> int:
    return n


# Decrement to zero functions
def decrement_to_zero_iterative(n: int) -> int:
    while n > 0:
        n = n - 1
    return n


@tacopy
def decrement_to_zero_recursive(n: int) -> int:
    if n <= 0:
        return n
    return decrement_to_zero_recursive(n - 1)


# Abs sum functions
def abs_sum_iterative(n: int, acc: int = 0) -> int:
    if n < 0:
        n = -n
    while n > 0:
        acc = acc + n
        n = n - 1
    return acc


@tacopy
def abs_sum_recursive(n: int, acc: int = 0) -> int:
    if n < 0:
        return abs_sum_recursive(-n, acc)
    if n == 0:
        return acc
    return abs_sum_recursive(n - 1, acc + n)


# String repeat functions
def repeat_string_iterative(s: str, n: int, acc: str = "") -> str:
    while n > 0:
        acc = acc + s
        n = n - 1
    return acc


@tacopy
def repeat_string_recursive(s: str, n: int, acc: str = "") -> str:
    if n == 0:
        return acc
    return repeat_string_recursive(s, n - 1, acc + s)


# Tuple builder functions
def build_tuple_iterative(n: int, acc=None):
    if acc is None:
        acc = ()
    while n > 0:
        acc = (n,) + acc
        n = n - 1
    return acc


@tacopy
def build_tuple_recursive(n: int, acc=None):
    if acc is None:
        acc = ()
    if n == 0:
        return acc
    return build_tuple_recursive(n - 1, (n,) + acc)


# ============================================================================
# Test classes
# ============================================================================


class TestBasicFactorial:
    """Test factorial computation."""

    def test_factorial_correctness(self):
        """Compare tail-recursive factorial with manual iterative version."""
        # Test various inputs
        test_cases = [0, 1, 2, 5, 10, 20, 100, 500]
        for n in test_cases:
            assert factorial_iterative(n) == factorial_recursive(n), f"Mismatch for n={n}"

    def test_factorial_with_non_default_accumulator(self):
        """Test factorial with custom initial accumulator."""
        # Test with different starting accumulators
        test_cases = [(5, 1), (5, 2), (10, 3), (0, 999)]
        for n, acc in test_cases:
            assert factorial_iterative(n, acc) == factorial_recursive(n, acc), (
                f"Mismatch for n={n}, acc={acc}"
            )


class TestFactorialModK:
    """Test factorial with modulo operation."""

    def test_factorial_mod_k_correctness(self):
        """Compare tail-recursive factorial_mod_k with manual version."""
        # Test various inputs
        test_cases = [
            (1, 0, 79),
            (1, 5, 79),
            (1, 10, 100),
            (1, 100, 79),
            (1, 1000, 79),
            (2, 50, 97),
            (1, 10000, 1009),  # Large input
        ]
        for acc, n, k in test_cases:
            result_iter = factorial_mod_k_iterative(acc, n, k)
            result_rec = factorial_mod_k_recursive(acc, n, k)
            assert result_iter == result_rec, f"Mismatch for acc={acc}, n={n}, k={k}"


class TestFibonacci:
    """Test Fibonacci computation."""

    def test_fibonacci_correctness(self):
        """Compare tail-recursive fibonacci with manual version."""
        # Test various inputs
        test_cases = [0, 1, 2, 5, 10, 20, 50, 100, 500, 1000]
        for n in test_cases:
            assert fibonacci_iterative(n) == fibonacci_recursive(n), f"Mismatch for n={n}"

    def test_fibonacci_with_custom_start(self):
        """Test fibonacci with custom starting values."""
        # Test with different starting values
        test_cases = [
            (10, 0, 1),
            (10, 1, 1),  # Starting with 1, 1
            (10, 2, 3),  # Starting with 2, 3
            (5, 5, 10),
        ]
        for n, a, b in test_cases:
            assert fibonacci_iterative(n, a, b) == fibonacci_recursive(n, a, b), (
                f"Mismatch for n={n}, a={a}, b={b}"
            )


class TestGCD:
    """Test greatest common divisor."""

    def test_gcd_correctness(self):
        """Compare tail-recursive GCD with manual version."""
        # Test various inputs
        test_cases = [
            (48, 18),
            (100, 35),
            (17, 19),
            (1071, 462),
            (270, 192),
            (1000000, 500000),
            (123456, 789012),
            (1, 1),
            (100, 1),
            (0, 5),  # Edge case: gcd(0, 5) = 5
        ]
        for a, b in test_cases:
            assert gcd_iterative(a, b) == gcd_recursive(a, b), f"Mismatch for a={a}, b={b}"


class TestSumToN:
    """Test sum computation."""

    def test_sum_to_n_correctness(self):
        """Compare tail-recursive sum with manual version."""
        # Test various inputs
        test_cases = [0, 1, 10, 100, 1000, 5000, 10000]
        for n in test_cases:
            assert sum_to_n_iterative(n) == sum_to_n_recursive(n), f"Mismatch for n={n}"


class TestListOperations:
    """Test operations on lists."""

    def test_list_length_correctness(self):
        """Compare tail-recursive list length with manual version."""
        # Test various lists
        test_cases = [
            [],
            [1],
            [1, 2, 3],
            list(range(10)),
            list(range(100)),
            ["a", "b", "c", "d"],
        ]
        for lst in test_cases:
            assert list_length_iterative(lst) == list_length_recursive(lst), (
                f"Mismatch for list of length {len(lst)}"
            )

    def test_list_sum_correctness(self):
        """Compare tail-recursive list sum with manual version."""
        # Test various lists
        test_cases = [
            [],
            [1],
            [1, 2, 3],
            list(range(10)),
            list(range(100)),
            [5, -3, 10, -1, 0],
        ]
        for lst in test_cases:
            assert list_sum_iterative(lst) == list_sum_recursive(lst), f"Mismatch for list {lst}"

    def test_list_reverse_correctness(self):
        """Compare tail-recursive list reverse with manual version."""
        # Test various lists
        test_cases = [
            [],
            [1],
            [1, 2, 3],
            [1, 2, 3, 4, 5],
            list(range(20)),
        ]
        for lst in test_cases:
            assert list_reverse_iterative(lst.copy()) == list_reverse_recursive(lst.copy()), (
                f"Mismatch for list {lst}"
            )


class TestPowerFunction:
    """Test exponentiation."""

    def test_power_correctness(self):
        """Compare tail-recursive power function with manual version."""
        # Test various inputs
        test_cases = [
            (2, 0),
            (2, 1),
            (2, 10),
            (3, 5),
            (10, 3),
            (5, 7),
            (2, 20),
        ]
        for base, exp in test_cases:
            assert power_iterative(base, exp) == power_recursive(base, exp), (
                f"Mismatch for base={base}, exp={exp}"
            )


class TestCountDown:
    """Test countdown function."""

    def test_count_down_correctness(self):
        """Compare tail-recursive countdown with manual version."""
        # Test various inputs
        test_cases = [0, 1, 5, 10, 100, 1000]
        for n in test_cases:
            assert count_down_iterative(n) == count_down_recursive(n), f"Mismatch for n={n}"


class TestBooleanFunctions:
    """Test functions returning booleans."""

    def test_is_even_correctness(self):
        """Compare tail-recursive even check with manual version."""
        # Test various inputs
        test_cases = [0, 1, 2, 5, 10, 99, 100, 500, 501]
        for n in test_cases:
            assert is_even_iterative(n) == is_even_recursive(n), f"Mismatch for n={n}"

    def test_all_positive_correctness(self):
        """Compare tail-recursive all-positive check with manual version."""
        # Test various lists
        test_cases = [
            [],
            [1],
            [1, 2, 3],
            [1, 2, 0, 3],
            [1, 2, -1, 3],
            [-1],
            [5, 10, 15, 20],
        ]
        for lst in test_cases:
            assert all_positive_iterative(lst.copy()) == all_positive_recursive(lst.copy()), (
                f"Mismatch for list {lst}"
            )


class TestFindMax:
    """Test finding maximum in a list."""

    def test_find_max_correctness(self):
        """Compare tail-recursive find max with manual version."""
        # Test various lists
        test_cases = [
            [1],
            [1, 2, 3],
            [3, 2, 1],
            [1, 5, 3, 9, 2],
            [-5, -1, -10],
            [0, 0, 0],
            list(range(50)),
        ]
        for lst in test_cases:
            assert find_max_iterative(lst.copy()) == find_max_recursive(lst.copy()), (
                f"Mismatch for list {lst}"
            )


class TestKeywordArguments:
    """Test functions using keyword arguments."""

    def test_sum_with_kwargs_correctness(self):
        """Test tail recursion with keyword arguments."""
        # Test various inputs
        test_cases = [0, 1, 5, 10, 50, 100]
        for n in test_cases:
            assert sum_kwargs_iterative(n) == sum_kwargs_recursive(n), f"Mismatch for n={n}"

    def test_mixed_args_and_kwargs_correctness(self):
        """Test tail recursion with mixed positional and keyword arguments."""
        # Test various inputs
        test_cases = [0, 1, 5, 10, 20]
        for n in test_cases:
            assert factorial_mixed_iterative(n) == factorial_mixed_recursive(n), (
                f"Mismatch for n={n}"
            )


class TestComplexExpressions:
    """Test functions with complex expressions."""

    def test_sum_of_squares_correctness(self):
        """Test tail-recursive sum of squares."""
        # Test various inputs
        test_cases = [0, 1, 5, 10, 50, 100]
        for n in test_cases:
            assert sum_of_squares_iterative(n) == sum_of_squares_recursive(n), f"Mismatch for n={n}"

    def test_collatz_length_correctness(self):
        """Test tail-recursive Collatz sequence length."""
        # Test various starting values
        test_cases = [1, 2, 3, 5, 10, 27, 100]
        for n in test_cases:
            assert collatz_length_iterative(n) == collatz_length_recursive(n), f"Mismatch for n={n}"


class TestDigitOperations:
    """Test functions operating on digits."""

    def test_sum_of_digits_correctness(self):
        """Test tail-recursive sum of digits."""
        # Test various inputs
        test_cases = [0, 1, 9, 10, 123, 456, 9999, 123456789]
        for n in test_cases:
            assert sum_of_digits_iterative(n) == sum_of_digits_recursive(n), f"Mismatch for n={n}"

    def test_digit_count_correctness(self):
        """Test tail-recursive digit counting."""
        # Test various inputs
        test_cases = [0, 1, 9, 10, 99, 100, 999, 1000, 123456]
        for n in test_cases:
            assert digit_count_iterative(n) == digit_count_recursive(n), f"Mismatch for n={n}"


class TestMultipleConditions:
    """Test functions with multiple conditional branches."""

    def test_sign_sum_correctness(self):
        """Test tail-recursive sum with sign handling."""
        # Test various lists
        test_cases = [
            [],
            [1],
            [-1],
            [0],
            [1, -1, 0],
            [5, -3, 2, -1, 0, 4],
            list(range(-10, 11)),
        ]
        for lst in test_cases:
            assert sign_sum_iterative(lst.copy()) == sign_sum_recursive(lst.copy()), (
                f"Mismatch for list {lst}"
            )


class TestDeepRecursion:
    """Test that tacopy prevents stack overflow for deep recursion."""

    def test_deep_factorial_no_stack_overflow(self):
        """Verify that deep recursion works with tacopy."""
        # Test with very large n that would cause stack overflow without optimization
        large_n = 10000
        k = 1000000007
        assert factorial_mod_iterative(large_n, k) == factorial_mod_recursive(large_n, k)

    def test_deep_sum_no_stack_overflow(self):
        """Verify that deep sum recursion works with tacopy."""
        # Test with very large n
        large_n = 50000
        assert sum_deep_iterative(large_n) == sum_deep_recursive(large_n)


class TestEdgeCases:
    """Test edge cases and boundary conditions."""

    def test_immediate_return(self):
        """Test function that returns immediately."""
        test_cases = [0, 1, 5, 100, -5]
        for n in test_cases:
            assert immediate_iterative(n) == immediate_recursive(n)

    def test_single_recursive_call(self):
        """Test function with single recursive case."""
        test_cases = [0, 1, 5, 100]
        for n in test_cases:
            assert decrement_to_zero_iterative(n) == decrement_to_zero_recursive(n)

    def test_negative_numbers(self):
        """Test functions handling negative numbers."""
        test_cases = [0, 5, -5, 10, -10]
        for n in test_cases:
            assert abs_sum_iterative(n) == abs_sum_recursive(n), f"Mismatch for n={n}"

    def test_string_concatenation(self):
        """Test tail recursion with string operations."""
        test_cases = [
            ("a", 0),
            ("a", 1),
            ("ab", 5),
            ("xyz", 10),
            ("", 100),
        ]
        for s, n in test_cases:
            assert repeat_string_iterative(s, n) == repeat_string_recursive(s, n), (
                f"Mismatch for s='{s}', n={n}"
            )


class TestTupleReturns:
    """Test functions that build and return tuples."""

    def test_tuple_builder_correctness(self):
        """Test tail-recursive tuple building."""
        # Test various inputs
        test_cases = [0, 1, 5, 10, 20]
        for n in test_cases:
            assert build_tuple_iterative(n) == build_tuple_recursive(n), f"Mismatch for n={n}"
