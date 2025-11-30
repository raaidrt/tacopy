"""Validator for tail-recursive functions."""
import ast
from typing import Callable


class TailRecursionError(Exception):
    """Raised when a function is not properly tail-recursive."""
    pass


class TailRecursionValidator(ast.NodeVisitor):
    """
    Validates that all recursive calls in a function are in tail position.

    A call is in tail position if:
    1. It's the direct return value of a return statement
    2. It's in the test/body/orelse of an if expression that's being returned
    3. It's not nested in any other expression (like arithmetic, function calls, etc.)
    """

    def __init__(self, function_name: str):
        self.function_name = function_name
        self.errors = []
        self.in_return = False
        self.return_depth = 0

    def visit_FunctionDef(self, node: ast.FunctionDef):
        """Visit function definition, only analyze the target function."""
        if node.name == self.function_name:
            # Visit the function body
            for stmt in node.body:
                self.visit(stmt)
        # Don't visit nested function definitions

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef):
        """Async functions are not supported for tail recursion optimization."""
        if node.name == self.function_name:
            raise TailRecursionError(
                f"Async function '{self.function_name}' cannot use tail recursion optimization. "
                "Async functions are not supported due to potential issues with shared state."
            )

    def visit_Return(self, node: ast.Return):
        """Visit return statement and check if the value is tail-recursive."""
        if node.value is None:
            return

        self.in_return = True
        self.return_depth = 0
        self._check_tail_position(node.value, is_tail=True)
        self.in_return = False

    def _check_tail_position(self, node: ast.AST, is_tail: bool = False):
        """
        Check if a node is in tail position.

        Args:
            node: The AST node to check
            is_tail: Whether this node is currently in tail position
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
            for key, value in zip(node.keys, node.values):
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
        """
        Check if a function call is a recursive call and if it's in tail position.

        Args:
            node: The Call node
            is_tail: Whether this call is in tail position
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
    """
    Validate that a function is tail-recursive.

    Args:
        func: The function to validate

    Raises:
        TailRecursionError: If the function is not properly tail-recursive
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
