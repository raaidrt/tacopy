"""Tacopy: Tail-Call Optimization for Python."""

import ast
import functools
import inspect
import textwrap
from collections.abc import Callable
from typing import TypeVar

from .transformer import transform_function
from .unparser import unparse
from .validator import TailRecursionError, validate_tail_recursive

__all__ = ["tacopy", "TailRecursionError", "show_transformed_code"]

F = TypeVar("F", bound=Callable)


def tacopy(func: F) -> F:
    """
    Decorator to apply tail-call optimization to a tail-recursive function.

    This decorator transforms a tail-recursive function into an iterative loop,
    eliminating the risk of stack overflow for deep recursion.

    Example:
        @tacopy
        def factorial_mod_k(acc: int, n: int, k: int) -> int:
            if n == 0:
                return acc % k
            return factorial_mod_k(acc * n % k, n - 1, k)

        # Can now safely call with large n
        result = factorial_mod_k(1, 1_000_000, 79)

    Args:
        func: The tail-recursive function to optimize

    Returns:
        The optimized function

    Raises:
        TailRecursionError: If the function is not properly tail-recursive or
                           if the decorator is applied to a nested function
    """
    # Check if function is nested (not at module level)
    if _is_nested_function(func):
        raise TailRecursionError(
            f"@tacopy decorator cannot be applied to nested function '{func.__name__}'. "
            f"The function must be defined at the module level. "
            f"To optimize a nested helper function, extract it to the module level."
        )

    # Validate that the function is tail-recursive
    validate_tail_recursive(func)

    # Get and dedent source code
    source = inspect.getsource(func)
    source = textwrap.dedent(source)

    # Parse into AST
    tree = ast.parse(source)

    # Remove any @tacopy decorators to prevent infinite recursion
    tree = _remove_tacopy_decorator(tree, func.__name__)

    # Apply tail-call optimization transformation
    tree = transform_function(tree, func.__name__)

    # Fix missing line numbers/col offsets after transformation
    ast.fix_missing_locations(tree)

    # Get the original namespace
    namespace = func.__globals__.copy()

    # Handle closure variables if any
    if func.__code__.co_freevars and func.__closure__:
        for name, cell in zip(func.__code__.co_freevars, func.__closure__, strict=True):
            try:
                namespace[name] = cell.cell_contents
            except ValueError:
                # Cell is empty - this can happen during decoration
                # when the function references itself in its closure
                # We'll let it be resolved from globals
                pass

    # Compile and execute the transformed code
    # Convert AST to code - compile() needs the AST in Module form
    code_obj = compile(tree, inspect.getfile(func), "exec")  # type: ignore[call-overload]
    exec(code_obj, namespace)

    # Get the newly defined function
    new_func = namespace[func.__name__]

    # Preserve metadata
    wrapped_func = functools.wraps(func)(new_func)

    return wrapped_func  # type: ignore[return-value]


def _is_nested_function(func: Callable) -> bool:
    """
    Check if a function is nested inside another function.

    A function is considered nested if it's defined inside another function's body,
    rather than at the module level.

    Args:
        func: The function to check

    Returns:
        True if the function is nested, False if it's at module level
    """
    # __qualname__ contains dots for nested functions
    # e.g., "outer.<locals>.inner" for nested, "factorial" for module-level
    return "<locals>" in func.__qualname__


def _remove_tacopy_decorator(tree: ast.AST, function_name: str) -> ast.AST:
    """
    Remove @tacopy decorator from a function to prevent infinite recursion.

    Args:
        tree: The AST to modify
        function_name: The name of the function to modify

    Returns:
        The modified AST
    """

    class RemoveTacopyDecorator(ast.NodeTransformer):
        """Remove @tacopy decorator to prevent infinite recursion."""

        def __init__(self, target_name: str):
            super().__init__()
            self.target_name = target_name

        def visit_FunctionDef(self, node: ast.FunctionDef) -> ast.FunctionDef:
            if node.name == self.target_name:
                node.decorator_list = [
                    d for d in node.decorator_list if not self._is_tacopy_decorator(d)
                ]
            return node

        def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> ast.AsyncFunctionDef:
            if node.name == self.target_name:
                node.decorator_list = [
                    d for d in node.decorator_list if not self._is_tacopy_decorator(d)
                ]
            return node

        def _is_tacopy_decorator(self, decorator) -> bool:
            """Check if a decorator is @tacopy or @tacopy.tacopy."""
            # @tacopy
            if isinstance(decorator, ast.Name) and decorator.id == "tacopy":
                return True

            # @tacopy.tacopy
            if isinstance(decorator, ast.Attribute):
                if decorator.attr == "tacopy":
                    if isinstance(decorator.value, ast.Name) and decorator.value.id == "tacopy":
                        return True

            # @tacopy() (call with no arguments)
            if isinstance(decorator, ast.Call):
                if isinstance(decorator.func, ast.Name) and decorator.func.id == "tacopy":
                    return True
                if isinstance(decorator.func, ast.Attribute):
                    if decorator.func.attr == "tacopy":
                        if (
                            isinstance(decorator.func.value, ast.Name)
                            and decorator.func.value.id == "tacopy"
                        ):
                            return True

            return False

    remover = RemoveTacopyDecorator(function_name)
    return remover.visit(tree)


# Helper function for debugging
def show_transformed_code(func: Callable) -> str:
    """
    Show the transformed code for a function without executing it.

    This is useful for debugging and understanding what the decorator does.

    Args:
        func: The function to transform

    Returns:
        The transformed Python source code as a string
    """
    # Get and dedent source code
    source = inspect.getsource(func)
    source = textwrap.dedent(source)

    # Parse into AST
    tree = ast.parse(source)

    # Remove any @tacopy decorators
    tree = _remove_tacopy_decorator(tree, func.__name__)

    # Apply tail-call optimization transformation
    tree = transform_function(tree, func.__name__)

    # Convert back to source code
    return unparse(tree)
