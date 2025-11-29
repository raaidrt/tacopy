from typing import Callable, Any
import ast
import inspect
import textwrap
import functools

def hello() -> str:
    return "Hello from tacopy!"

__tacopy_input_parameters_dict: dict[str, Any] = {}

class ReturnVisitor(ast.NodeVisitor):
    def __init__(self):
        super().__init__()

    def visit_Return(self, node: ast.Return):
        print(f"visited return! {node}")

def validate_tail_recursive(func: Callable):
    pass

def generate_code(tree: ast.AST) -> ast.AST:
    # Your AST transformations here
    return tree


class RemoveTacopyDecorator(ast.NodeTransformer):
    """Remove @tacopy decorator to prevent infinite recursion."""
    def __init__(self, function_name: str):
        super().__init__()
        self.function_name = function_name

    def visit_FunctionDef(self, node: ast.FunctionDef) -> ast.FunctionDef:
        # Then filter out the @tacopy decorator
        if node.name == self.function_name:
            node.decorator_list = [
                d for d in node.decorator_list
                if not self._is_tacopy_decorator(d)
            ]

        return node

    def _is_tacopy_decorator(self, decorator) -> bool:
        """Check if a decorator is @tacopy, @tacopy(), or @tacopy.tacopy or @tacopy.tacopy()"""
        # @tacopy
        if isinstance(decorator, ast.Name) and decorator.id == 'tacopy':
            return True

        # @tacopy.tacopy
        if isinstance(decorator, ast.Attribute):
            if decorator.attr == 'tacopy':
                if isinstance(decorator.value, ast.Name) and decorator.value.id == 'tacopy':
                    return True

        # @tacopy() or @tacopy.tacopy()
        if isinstance(decorator, ast.Call):
            # @tacopy()
            if isinstance(decorator.func, ast.Name) and decorator.func.id == 'tacopy':
                return True
            # @tacopy.tacopy()
            if isinstance(decorator.func, ast.Attribute):
                if decorator.func.attr == 'tacopy':
                    if isinstance(decorator.func.value, ast.Name) and decorator.func.value.id == 'tacopy':
                        return True

        return False

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> ast.AsyncFunctionDef:
        # Then filter out the @tacopy decorator
        if node.name == self.function_name:
            node.decorator_list = [
                d for d in node.decorator_list
                if not self._is_tacopy_decorator(d)
            ]

        return node

def tacopy(func: Callable | None = None, *, prefix: str = "") -> Callable:
    # Handle being called with or without arguments: @tacopy vs @tacopy(prefix="x")
    def decorator(fn: Callable) -> Callable:
        validate_tail_recursive(fn)
        
        # Get and dedent source code
        source = inspect.getsource(fn)
        source = textwrap.dedent(source)
        
        # Parse into AST
        tree: ast.AST = ast.parse(source)
        
        # Remove the @tacopy decorator to prevent infinite recursion
        tree = RemoveTacopyDecorator().visit(tree)

        ReturnVisitor().visit(tree)
        
        # Apply your transformations
        tree = generate_code(tree)

        # Fix missing line numbers/col offsets after transformation
        ast.fix_missing_locations(tree)
        
        # Get the original namespace
        namespace = fn.__globals__.copy()
        
        # Handle closure variables if any
        if fn.__code__.co_freevars and fn.__closure__:
            for name, cell in zip(fn.__code__.co_freevars, fn.__closure__):
                namespace[name] = cell.cell_contents
        
        # Compile and execute
        code = compile(tree, inspect.getfile(fn), 'exec')
        exec(code, namespace)
        
        # Get the newly defined function
        new_func = namespace[fn.__name__]
        
        # Preserve metadata and wrap if you need pre/post logic
        @functools.wraps(fn)
        def wrapper(*args, **kwargs):
            result = new_func(*args, **kwargs)
            return result
        
        return wrapper
    
    if func is not None:
        # Called as @tacopy without parentheses
        return decorator(func)
    else:
        # Called as @tacopy(...) with arguments
        return decorator
