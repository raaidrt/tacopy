"""Utility to convert AST back to Python source code.

This module provides utilities for converting AST nodes back into Python source code,
which is useful for debugging transformations and displaying the optimized code.
"""

import ast


def unparse(tree: ast.AST) -> str:
    """Convert an AST back to Python source code.

    This function uses Python's built-in ``ast.unparse()`` function (available in
    Python 3.9+) to convert an Abstract Syntax Tree back into executable Python code.

    Args:
        tree: The AST to convert. Can be a complete Module or any AST node.

    Returns:
        The Python source code as a string

    Example:
        >>> tree = ast.parse("def foo(): return 42")
        >>> code = unparse(tree)
        >>> print(code)
        def foo():
            return 42

    Note:
        This project requires Python 3.10+, so ``ast.unparse()`` is always available.
    """
    # Python 3.10+ has ast.unparse built-in
    return ast.unparse(tree)


def format_ast(tree: ast.AST, indent: int = 2) -> str:
    """Format an AST as indented source code for debugging.

    This is a convenience function that wraps ``unparse()`` and is primarily
    used for debugging and visualization of transformed code.

    Args:
        tree: The AST to format
        indent: Number of spaces per indentation level (currently unused,
                reserved for future formatting enhancements)

    Returns:
        Formatted Python source code

    Note:
        The ``indent`` parameter is currently not used as ``ast.unparse()``
        handles indentation automatically. It's kept for potential future
        enhancements or custom formatting logic.
    """
    code = unparse(tree)
    # ast.unparse doesn't always format nicely, but it's good enough for debugging
    return code
