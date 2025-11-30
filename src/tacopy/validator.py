"""Validator for tail-recursive functions.

This module provides validation logic to ensure that functions decorated with
@tacopy are properly tail-recursive. It uses AST traversal to detect non-tail
recursive calls and raises TailRecursionError for invalid functions.
"""

import ast
from collections.abc import Callable


class TailRecursionError(Exception):
    """Exception raised when a function is not properly tail-recursive.

    This exception is raised in the following scenarios:
    - A recursive call is not in tail position (e.g., further operations after the call)
    - An async function is decorated with @tacopy (not supported)
    - The decorator is applied to a nested function (not supported)

    Attributes:
        message: Detailed explanation of why the function is not tail-recursive
    """

    pass


class TailRecursionValidator(ast.NodeVisitor):
    """AST visitor that validates tail-recursive functions.

    This validator traverses the AST of a function to ensure all recursive calls
    are in tail position. A call is in tail position if it's the final operation
    before returning - no further computation should occur after the recursive call.

    Valid tail positions:
    1. Direct return value: ``return func(args)``
    2. Within if-expression branches: ``return x if cond else func(args)``
    3. NOT in operations: ``return 1 + func(args)`` is invalid

    Attributes:
        function_name: The name of the function being validated
        errors: List of error messages for non-tail-recursive calls found
        in_return: Flag indicating if currently analyzing a return statement
        return_depth: Nesting depth within return expression (for debugging)

    Raises:
        TailRecursionError: If the function is not properly tail-recursive
    """

    def __init__(self, function_name: str):
        """Initialize the validator for a specific function.

        Args:
            function_name: The name of the function to validate
        """
        self.function_name = function_name
        self.errors = []
        self.in_return = False
        self.return_depth = 0

    def visit_FunctionDef(self, node: ast.FunctionDef):
        """Visit function definition, only analyze the target function.

        Args:
            node: The FunctionDef AST node to visit

        Note:
            Nested function definitions are intentionally not visited to avoid
            false positives from inner functions.
        """
        if node.name == self.function_name:
            # Visit the function body
            for stmt in node.body:
                self.visit(stmt)
        # Don't visit nested function definitions

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef):
        """Reject async functions as they are not supported.

        Args:
            node: The AsyncFunctionDef AST node to visit

        Raises:
            TailRecursionError: Always raised for async functions
        """
        if node.name == self.function_name:
            raise TailRecursionError(
                f"Async function '{self.function_name}' cannot use tail recursion optimization. "
                "Async functions are not supported due to potential issues with shared state."
            )

    def visit_Return(self, node: ast.Return):
        """Visit return statement and validate tail-recursiveness.

        Args:
            node: The Return AST node to visit

        Note:
            This method sets the in_return flag and delegates to _check_tail_position
            to recursively check if any recursive calls are in valid tail positions.
        """
        if node.value is None:
            return

        self.in_return = True
        self.return_depth = 0
        self._check_tail_position(node.value, is_tail=True)
        self.in_return = False

    def _check_tail_position(self, node: ast.AST, is_tail: bool = False):
        """Recursively check if a node is in tail position.

        This method traverses the AST node and its children to identify recursive
        calls and verify they are in tail position. Operations that break tail
        position (arithmetic, comparisons, etc.) are tracked.

        Args:
            node: The AST node to check
            is_tail: Whether this node is currently in tail position

        Note:
            Tail position is preserved through if-expressions but broken by
            operations like arithmetic, boolean logic, comparisons, etc.
        """
        if isinstance(node, ast.Call):
            self._check_call(node, is_tail)
        elif isinstance(node, ast.IfExp):
            # In an if expression: test, body, and orelse can all be in tail position
            self._check_tail_position(node.test, is_tail=False)  # test is never tail
            self._check_tail_position(node.body, is_tail=is_tail)
            self._check_tail_position(node.orelse, is_tail=is_tail)
        elif isinstance(node, (ast.BoolOp, ast.UnaryOp, ast.BinOp, ast.Compare)):
            # These operations break tail position
            if isinstance(node, ast.BoolOp):
                for value in node.values:
                    self._check_tail_position(value, is_tail=False)
            elif isinstance(node, ast.UnaryOp):
                self._check_tail_position(node.operand, is_tail=False)
            elif isinstance(node, ast.BinOp):
                self._check_tail_position(node.left, is_tail=False)
                self._check_tail_position(node.right, is_tail=False)
            elif isinstance(node, ast.Compare):
                self._check_tail_position(node.left, is_tail=False)
                for comparator in node.comparators:
                    self._check_tail_position(comparator, is_tail=False)
        elif isinstance(node, (ast.List, ast.Tuple, ast.Set)):
            # Elements in collections are not in tail position
            for elt in node.elts:
                self._check_tail_position(elt, is_tail=False)
        elif isinstance(node, ast.Dict):
            for key, value in zip(node.keys, node.values, strict=True):
                if key:
                    self._check_tail_position(key, is_tail=False)
                self._check_tail_position(value, is_tail=False)
        elif isinstance(node, ast.Subscript):
            self._check_tail_position(node.value, is_tail=False)
            self._check_tail_position(node.slice, is_tail=False)
        elif isinstance(node, ast.Attribute):
            self._check_tail_position(node.value, is_tail=False)
        # For other node types (constants, names, etc.), no recursive calls are possible

    def _check_call(self, node: ast.Call, is_tail: bool):
        """Check if a function call is recursive and validate tail position.

        This method identifies recursive calls (calls to the function being validated)
        and ensures they appear only in tail position. Non-tail recursive calls are
        recorded as errors.

        Args:
            node: The Call AST node to check
            is_tail: Whether this call is in tail position

        Note:
            Arguments to any function call (recursive or not) are always checked
            with is_tail=False since they cannot be in tail position.
        """
        # Check if this is a recursive call
        is_recursive = False

        if isinstance(node.func, ast.Name) and node.func.id == self.function_name:
            is_recursive = True
        elif isinstance(node.func, ast.Attribute):
            # Could be a method call, check if it's self-referential
            # For now, we'll be conservative and not consider these recursive
            pass

        if is_recursive and not is_tail:
            # Found a recursive call not in tail position
            self.errors.append(
                f"Recursive call to '{self.function_name}' is not in tail position. "
                f"All recursive calls must be direct return values."
            )

        # Check arguments (they're never in tail position)
        for arg in node.args:
            self._check_tail_position(arg, is_tail=False)
        for keyword in node.keywords:
            self._check_tail_position(keyword.value, is_tail=False)


def validate_tail_recursive(func: Callable) -> None:
    """Validate that a function is properly tail-recursive.

    This function parses the source code of the given function and uses
    TailRecursionValidator to check that all recursive calls are in tail position.
    If any non-tail recursive calls are found, or if the function is async,
    a TailRecursionError is raised with detailed error messages.

    Args:
        func: The function to validate. Must have accessible source code
              via inspect.getsource().

    Raises:
        TailRecursionError: If the function is not properly tail-recursive,
                           is an async function, or has any non-tail recursive calls.

    Example:
        >>> def factorial(n, acc=1):
        ...     if n == 0:
        ...         return acc
        ...     return factorial(n - 1, acc * n)  # Valid tail call
        >>> validate_tail_recursive(factorial)  # Passes

        >>> def bad_factorial(n):
        ...     if n == 0:
        ...         return 1
        ...     return n * bad_factorial(n - 1)  # Invalid - not tail position
        >>> validate_tail_recursive(bad_factorial)  # Raises TailRecursionError
    """
    import inspect
    import textwrap

    # Get function source and parse it
    source = inspect.getsource(func)
    source = textwrap.dedent(source)
    tree = ast.parse(source)

    # Validate
    validator = TailRecursionValidator(func.__name__)
    validator.visit(tree)

    if validator.errors:
        error_msg = f"Function '{func.__name__}' is not properly tail-recursive:\n"
        error_msg += "\n".join(f"  - {err}" for err in validator.errors)
        raise TailRecursionError(error_msg)
