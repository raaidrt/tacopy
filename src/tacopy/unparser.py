"""Utility to convert AST back to Python source code."""
import ast
import sys


def unparse(tree: ast.AST) -> str:
    """
    Convert an AST back to Python source code.

    Args:
        tree: The AST to convert

    Returns:
        The Python source code as a string
    """
    # Python 3.9+ has ast.unparse built-in
    if sys.version_info >= (3, 9):
        return ast.unparse(tree)
    else:
        # For older versions, we'd need a third-party library
        # But since the project requires Python 3.10+, we can use ast.unparse
        return ast.unparse(tree)


def format_ast(tree: ast.AST, indent: int = 2) -> str:
    """
    Format an AST as indented source code for debugging.

    Args:
        tree: The AST to format
        indent: Number of spaces per indentation level

    Returns:
        Formatted Python source code
    """
    code = unparse(tree)
    # ast.unparse doesn't always format nicely, but it's good enough for debugging
    return code
