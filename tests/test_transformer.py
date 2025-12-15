"""Unit tests for the AST transformer."""

import ast
import re

from tacopy.transformer import transform_function
from tacopy.unparser import unparse


def _normalize_uuids(code: str) -> str:
    """Replace UUIDs with numbered placeholders for consistent snapshots.

    This ensures each unique UUID gets a unique number (UUID1, UUID2, etc.)
    so that nested loops with different flags are clearly distinguishable.
    """
    # Find all unique UUIDs in order of appearance
    uuids_found = []

    def get_uuid_number(uuid: str) -> int:
        if uuid not in uuids_found:
            uuids_found.append(uuid)
        return uuids_found.index(uuid) + 1

    # Replace parameter variable UUIDs: _tacopy_XXXXXXXX_
    def replace_param_uuid(match):
        uuid = match.group(1)
        return f"_tacopy_UUID{get_uuid_number(uuid)}_"

    # Replace for loop flag UUIDs: __tacopy_returned_in_for_XXXXXXXX
    def replace_for_flag_uuid(match):
        uuid = match.group(1)
        return f"__tacopy_returned_in_for_UUID{get_uuid_number(uuid)}"

    # Replace while loop flag UUIDs: __tacopy_returned_in_while_XXXXXXXX
    def replace_while_flag_uuid(match):
        uuid = match.group(1)
        return f"__tacopy_returned_in_while_UUID{get_uuid_number(uuid)}"

    code = re.sub(r"_tacopy_([a-f0-9]{8})_", replace_param_uuid, code)
    code = re.sub(r"__tacopy_returned_in_for_([a-f0-9]{8})", replace_for_flag_uuid, code)
    code = re.sub(r"__tacopy_returned_in_while_([a-f0-9]{8})", replace_while_flag_uuid, code)

    return code


def test_transform_simple_factorial():
    """Test transformation of a simple factorial function."""
    source = """
def factorial(n: int, acc: int = 1) -> int:
    if n == 0:
        return acc
    return factorial(n - 1, acc * n)
"""
    tree = ast.parse(source)
    transformed = transform_function(tree, "factorial")
    code = unparse(transformed)

    # Check that a while True loop was added
    assert "while True:" in code
    # Check that parameters are captured with unique names
    assert "_tacopy_" in code
    # Check that continue is used instead of recursive call
    assert "continue" in code


def test_transform_factorial_mod_k():
    """Test transformation of the factorial_mod_k example from the design doc."""
    source = """
def factorial_mod_k(acc: int, n: int, k: int) -> int:
    if n == 0:
        return acc % k
    return factorial_mod_k(acc * n % k, n - 1, k)
"""
    tree = ast.parse(source)
    transformed = transform_function(tree, "factorial_mod_k")
    code = unparse(transformed)

    # Check key transformations
    assert "while True:" in code
    assert "_tacopy_" in code
    assert "continue" in code

    # Verify the function can be compiled
    compile(transformed, "<test>", "exec")  # type: ignore[call-overload]


def test_transform_multiple_base_cases():
    """Test transformation with multiple return statements."""
    source = """
def fibonacci_tail(n: int, a: int = 0, b: int = 1) -> int:
    if n == 0:
        return a
    if n == 1:
        return b
    return fibonacci_tail(n - 1, b, a + b)
"""
    tree = ast.parse(source)
    transformed = transform_function(tree, "fibonacci_tail")
    code = unparse(transformed)

    # Check transformations
    assert "while True:" in code
    assert "_tacopy_" in code

    # Should have continue for the tail call
    assert "continue" in code

    # Verify compilation
    compile(transformed, "<test>", "exec")  # type: ignore[call-overload]


def test_unique_variable_names():
    """Test that generated variable names are unique across multiple transformations."""
    source = """
def func(x: int) -> int:
    if x == 0:
        return 0
    return func(x - 1)
"""

    # Transform the same function twice
    tree1 = ast.parse(source)
    transformed1 = transform_function(tree1, "func")
    code1 = unparse(transformed1)

    tree2 = ast.parse(source)
    transformed2 = transform_function(tree2, "func")
    code2 = unparse(transformed2)

    # Extract the UUID parts from the variable names
    import re

    uuid_pattern = r"_tacopy_([a-f0-9]{8})_"

    uuids1 = re.findall(uuid_pattern, code1)
    uuids2 = re.findall(uuid_pattern, code2)

    # The UUIDs should be different between transformations
    assert len(uuids1) > 0
    assert len(uuids2) > 0
    assert uuids1[0] != uuids2[0]


def test_transform_preserves_non_recursive_returns():
    """Test that non-recursive return statements are preserved."""
    source = """
def func(n: int, acc: int) -> int:
    if n == 0:
        return acc
    if n < 0:
        return -1
    return func(n - 1, acc + n)
"""
    tree = ast.parse(source)
    transformed = transform_function(tree, "func")
    code = unparse(transformed)

    # The non-recursive returns should still be there
    # (though they'll reference temp variables)
    assert "return" in code
    assert "while True:" in code


def test_transformed_code_uses_temp_variables():
    """Test that the transformed code uses temporary variables for parameters."""
    source = """
def sum_tail(n: int, acc: int = 0) -> int:
    if n == 0:
        return acc
    return sum_tail(n - 1, acc + n)
"""
    tree = ast.parse(source)
    transformed = transform_function(tree, "sum_tail")
    code = unparse(transformed)

    # Should initialize temp variables
    assert "_tacopy_" in code
    # Should use them in conditions and returns
    # The exact format depends on ast.unparse, but we should see assignments


def test_snapshot_factorial_transformation(snapshot):
    """Snapshot test for factorial transformation."""
    source = """
def factorial(n: int, acc: int = 1) -> int:
    if n == 0:
        return acc
    return factorial(n - 1, acc * n)
"""
    tree = ast.parse(source)
    transformed = transform_function(tree, "factorial")
    code = unparse(transformed)

    # Replace UUIDs with numbered placeholders for consistent snapshots
    code = _normalize_uuids(code)

    assert code == snapshot


def test_snapshot_fibonacci_transformation(snapshot):
    """Snapshot test for fibonacci transformation."""
    source = """
def fibonacci_tail(n: int, a: int = 0, b: int = 1) -> int:
    if n == 0:
        return a
    if n == 1:
        return b
    return fibonacci_tail(n - 1, b, a + b)
"""
    tree = ast.parse(source)
    transformed = transform_function(tree, "fibonacci_tail")
    code = unparse(transformed)

    # Replace UUIDs with numbered placeholders for consistent snapshots
    code = _normalize_uuids(code)

    assert code == snapshot


def test_snapshot_factorial_mod_k_transformation(snapshot):
    """Snapshot test for factorial_mod_k transformation."""
    source = """
def factorial_mod_k(acc: int, n: int, k: int) -> int:
    if n == 0:
        return acc % k
    return factorial_mod_k(acc * n % k, n - 1, k)
"""
    tree = ast.parse(source)
    transformed = transform_function(tree, "factorial_mod_k")
    code = unparse(transformed)

    # Replace UUIDs with numbered placeholders for consistent snapshots
    code = _normalize_uuids(code)

    assert code == snapshot


def test_snapshot_list_reverse_with_parameter_assignment(snapshot):
    """Snapshot test for list reverse with parameter assignment (tests bug fix)."""
    source = """
def list_reverse_recursive(lst, acc=None):
    if acc is None:
        acc = []
    if not lst:
        return acc
    return list_reverse_recursive(lst[1:], [lst[0]] + acc)
"""
    tree = ast.parse(source)
    transformed = transform_function(tree, "list_reverse_recursive")
    code = unparse(transformed)

    # Replace UUIDs with numbered placeholders for consistent snapshots
    code = _normalize_uuids(code)

    assert code == snapshot


def test_snapshot_tuple_builder_with_parameter_assignment(snapshot):
    """Snapshot test for tuple builder with parameter assignment (tests bug fix)."""
    source = """
def build_tuple_recursive(n: int, acc=None):
    if acc is None:
        acc = ()
    if n == 0:
        return acc
    return build_tuple_recursive(n - 1, (n,) + acc)
"""
    tree = ast.parse(source)
    transformed = transform_function(tree, "build_tuple_recursive")
    code = unparse(transformed)

    # Replace UUIDs with numbered placeholders for consistent snapshots
    code = _normalize_uuids(code)

    assert code == snapshot


def test_snapshot_tail_call_in_for_loop(snapshot):
    """Snapshot test for tail call inside a for loop."""
    source = """
def tailing(n: int) -> int:
    if n <= 0:
        return 0
    for i in range(3):
        return tailing(n - 1)
    return 0
"""
    tree = ast.parse(source)
    transformed = transform_function(tree, "tailing")
    code = unparse(transformed)

    # Replace UUIDs with numbered placeholders for consistent snapshots
    code = _normalize_uuids(code)

    assert code == snapshot


def test_snapshot_tail_call_in_nested_for_loops(snapshot):
    """Snapshot test for tail call inside nested for loops."""
    source = """
def nested_loops(n: int) -> int:
    if n <= 0:
        return 0
    for i in range(3):
        for j in range(2):
            return nested_loops(n - 1)
    return 0
"""
    tree = ast.parse(source)
    transformed = transform_function(tree, "nested_loops")
    code = unparse(transformed)

    # Replace UUIDs with numbered placeholders for consistent snapshots
    code = _normalize_uuids(code)

    assert code == snapshot


def test_snapshot_tail_call_in_for_with_conditional(snapshot):
    """Snapshot test for tail call inside a for loop with conditional."""
    source = """
def loop_with_cond(n: int) -> int:
    if n <= 0:
        return 0
    for i in range(5):
        if i % 2 == 0:
            return loop_with_cond(n - 1)
    return 1
"""
    tree = ast.parse(source)
    transformed = transform_function(tree, "loop_with_cond")
    code = unparse(transformed)

    # Replace UUIDs with numbered placeholders for consistent snapshots
    code = _normalize_uuids(code)

    assert code == snapshot


def test_snapshot_tail_call_in_triple_nested_for_loops(snapshot):
    """Snapshot test for tail call inside triple nested for loops."""
    source = """
def triple_nested(n: int) -> int:
    if n <= 0:
        return 0
    for i in range(2):
        for j in range(2):
            for k in range(2):
                return triple_nested(n - 1)
    return 0
"""
    tree = ast.parse(source)
    transformed = transform_function(tree, "triple_nested")
    code = unparse(transformed)

    # Replace UUIDs with numbered placeholders for consistent snapshots
    code = _normalize_uuids(code)

    assert code == snapshot


def test_snapshot_tail_call_in_while_loop(snapshot):
    """Snapshot test for tail call inside a while loop."""
    source = """
def while_countdown(n: int) -> int:
    if n <= 0:
        return 0
    count = 0
    while count < 3:
        return while_countdown(n - 1)
    return 0
"""
    tree = ast.parse(source)
    transformed = transform_function(tree, "while_countdown")
    code = unparse(transformed)

    # Replace UUIDs with numbered placeholders for consistent snapshots
    code = _normalize_uuids(code)

    assert code == snapshot


def test_snapshot_tail_call_in_nested_while_loops(snapshot):
    """Snapshot test for tail call inside nested while loops."""
    source = """
def nested_while(n: int) -> int:
    if n <= 0:
        return 0
    i = 0
    while i < 2:
        j = 0
        while j < 2:
            return nested_while(n - 1)
        j += 1
    return 0
"""
    tree = ast.parse(source)
    transformed = transform_function(tree, "nested_while")
    code = unparse(transformed)

    # Replace UUIDs with numbered placeholders for consistent snapshots
    code = _normalize_uuids(code)

    assert code == snapshot


def test_snapshot_for_inside_while(snapshot):
    """Snapshot test for for loop inside while loop."""
    source = """
def for_in_while(n: int) -> int:
    if n <= 0:
        return 0
    i = 0
    while i < 2:
        for j in range(2):
            return for_in_while(n - 1)
        i += 1
    return 0
"""
    tree = ast.parse(source)
    transformed = transform_function(tree, "for_in_while")
    code = unparse(transformed)

    # Replace UUIDs with numbered placeholders for consistent snapshots
    code = _normalize_uuids(code)

    assert code == snapshot


def test_snapshot_while_inside_for(snapshot):
    """Snapshot test for while loop inside for loop."""
    source = """
def while_in_for(n: int) -> int:
    if n <= 0:
        return 0
    for i in range(2):
        j = 0
        while j < 2:
            return while_in_for(n - 1)
        j += 1
    return 0
"""
    tree = ast.parse(source)
    transformed = transform_function(tree, "while_in_for")
    code = unparse(transformed)

    # Replace UUIDs with numbered placeholders for consistent snapshots
    code = _normalize_uuids(code)

    assert code == snapshot
