"""AST transformer for tail call optimization.

This module implements the core transformation logic that converts tail-recursive
functions into iterative loops using AST manipulation. The transformation eliminates
recursion while preserving the function's semantics and behavior.
"""

import ast
import uuid


class TailCallTransformer(ast.NodeTransformer):
    """AST transformer that converts tail-recursive functions to iterative loops.

    This transformer implements the tail-call optimization by:
    1. Hoisting parameters to uniquely-named temporary variables
    2. Wrapping the function body in a ``while True`` loop
    3. Replacing tail-recursive calls with assignments and ``continue`` statements

    The transformation converts::

        def func(a, b):
            if base_case:
                return result
            return func(new_a, new_b)

    Into::

        def func(a, b):
            _tacopy_<uuid>_a = a
            _tacopy_<uuid>_b = b
            while True:
                if base_case:
                    return result
                _tacopy_<uuid>_a, _tacopy_<uuid>_b = new_a, new_b
                continue

    UUID-based variable names are used to avoid collisions with existing variables
    in the function scope.

    Attributes:
        function_name: Name of the function being transformed
        param_names: List of parameter names extracted from function signature
        transformed: Flag indicating if transformation was applied
        var_prefix: Unique prefix for temporary variables (includes UUID)

    Example:
        >>> transformer = TailCallTransformer("factorial")
        >>> tree = ast.parse(source_code)
        >>> new_tree = transformer.visit(tree)
        >>> assert transformer.transformed
    """

    def __init__(self, function_name: str):
        """Initialize the transformer for a specific function.

        Args:
            function_name: The name of the function to transform
        """
        self.function_name = function_name
        self.param_names = []
        self.transformed = False
        # Generate a unique identifier for this transformation
        self.var_prefix = f"_tacopy_{uuid.uuid4().hex[:8]}_"
        # Track nested loops (both for and while) to handle tail calls inside loops correctly
        # Stack of (loop_type, loop_uuid, loop_flag_name) tuples
        # loop_type is either "for" or "while"
        self.loop_stack: list[tuple[str, str, str]] = []

    def visit_FunctionDef(self, node: ast.FunctionDef) -> ast.FunctionDef:
        """Transform the target function definition into a loop-based version.

        This method performs the complete transformation:
        1. Extracts parameter names from the function signature
        2. Creates temporary variable initializations for each parameter
        3. Transforms the function body (replacing tail calls with assignments)
        4. Wraps the body in a ``while True`` loop

        Args:
            node: The FunctionDef AST node to transform

        Returns:
            The transformed FunctionDef node if this is the target function,
            otherwise returns the node unchanged.
        """
        if node.name != self.function_name:
            return node

        # Extract parameter names
        self.param_names = [arg.arg for arg in node.args.args]

        # Create variable initializations at the start of the function
        # _tacopy_<uuid>_param = param
        init_stmts: list[ast.stmt] = []
        for param in self.param_names:
            temp_name = self._get_temp_name(param)
            init_stmts.append(
                ast.Assign(
                    targets=[ast.Name(id=temp_name, ctx=ast.Store())],
                    value=ast.Name(id=param, ctx=ast.Load()),
                )
            )

        # Transform the function body
        transformed_body: list[ast.stmt] = []
        for stmt in node.body:
            transformed_stmt = self.visit(stmt)
            if isinstance(transformed_stmt, list):
                transformed_body.extend(transformed_stmt)
            else:
                transformed_body.append(transformed_stmt)

        # Wrap the transformed body in a while True loop
        while_loop = ast.While(test=ast.Constant(value=True), body=transformed_body, orelse=[])

        # Combine: initializations + while loop
        new_body: list[ast.stmt] = init_stmts + [while_loop]

        # Create the transformed function
        new_node = ast.FunctionDef(
            name=node.name,
            args=node.args,
            body=new_body,
            decorator_list=node.decorator_list,
            returns=node.returns,
            type_comment=node.type_comment,
        )

        self.transformed = True
        return new_node

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> ast.AsyncFunctionDef:
        """Handle async function definitions (should be rejected by validator).

        Args:
            node: The AsyncFunctionDef AST node

        Returns:
            The node unchanged (validation should prevent this from being called)

        Note:
            Async functions should be caught by the validator before transformation.
        """
        return node

    def visit_Return(self, node: ast.Return) -> ast.AST:
        """Transform return statements with tail calls into assignments + continue/break.

        This is the core of the transformation. When a return statement contains
        a tail-recursive call, it's converted into:
        1. An assignment updating all parameter variables
        2. If inside a for loop: set flag + break
        3. If not inside a for loop: continue to restart the while True loop

        Non-tail returns are left as-is but have parameter references updated.

        Args:
            node: The Return AST node to transform

        Returns:
            Either:
            - A list containing [Assignment, Flag_Set, Break] for tail calls in for loops
            - A list containing [Assignment, Continue] for tail calls outside for loops
            - The original Return node (with updated references) for other returns
        """
        if node.value is None:
            return node

        # Check if this is a tail call
        if isinstance(node.value, ast.Call) and self._is_recursive_call(node.value):
            # This is a tail recursive call
            # Transform: return func(arg1, arg2, ...)
            # Into assignment + (flag + break if in for loop, else continue)

            # Create the assignment
            targets = [self._get_temp_name(param) for param in self.param_names]
            values = node.value.args

            # Handle keyword arguments
            if node.value.keywords:
                # Build a mapping of keyword arguments
                kwarg_map = {kw.arg: kw.value for kw in node.value.keywords}
                # Reorder values to match parameter order
                reordered_values = []
                for param in self.param_names:
                    if param in kwarg_map:
                        reordered_values.append(kwarg_map[param])
                    else:
                        # This parameter is positional
                        # Find its index and use the corresponding positional arg
                        idx = self.param_names.index(param)
                        if idx < len(values):
                            reordered_values.append(values[idx])
                        else:
                            # This shouldn't happen in valid tail calls
                            # The validator should have caught this
                            reordered_values.append(ast.Constant(value=None))
                values = reordered_values

            # Replace parameter references in the values with temp variables
            replaced_values: list[ast.expr] = [
                self._replace_params_in_expr(val)
                for val in values  # type: ignore[misc]
            ]

            assignment = ast.Assign(
                targets=[
                    ast.Tuple(
                        elts=[ast.Name(id=name, ctx=ast.Store()) for name in targets],
                        ctx=ast.Store(),
                    )
                ],
                value=ast.Tuple(
                    elts=replaced_values,
                    ctx=ast.Load(),
                ),
            )

            # Check if we're inside any loop (for or while)
            if self.loop_stack:
                # We're inside a loop, so we need to:
                # 1. Set the flag to True
                # 2. Break out of the loop
                loop_type, loop_uuid, loop_flag_name = self.loop_stack[-1]

                flag_set = ast.Assign(
                    targets=[ast.Name(id=loop_flag_name, ctx=ast.Store())],
                    value=ast.Constant(value=True),
                )

                break_stmt = ast.Break()

                # Return: assignment, flag_set, break
                return [assignment, flag_set, break_stmt]  # type: ignore[return-value]
            else:
                # We're not inside any loop, use continue as before
                continue_stmt = ast.Continue()

                # Return both statements as a list
                return [assignment, continue_stmt]  # type: ignore[return-value]

        # Not a tail call, return as-is (but replace parameter references)
        return self._replace_params_in_return(node)

    def _replace_params_in_return(self, node: ast.Return) -> ast.Return:
        """Replace parameter references with temp variables in non-tail-call returns.

        For return statements that don't contain tail calls, we still need to
        update all parameter references to use the temporary variables created
        at the start of the function.

        Args:
            node: The Return AST node to process

        Returns:
            The Return node with parameter references replaced
        """
        if node.value is None:
            return node

        class ParamReplacer(ast.NodeTransformer):
            def __init__(self, param_map):
                self.param_map = param_map

            def visit_Name(self, node: ast.Name) -> ast.Name:
                if node.id in self.param_map:
                    return ast.Name(id=self.param_map[node.id], ctx=node.ctx)
                return node

        param_map = {param: self._get_temp_name(param) for param in self.param_names}
        replacer = ParamReplacer(param_map)
        new_value = replacer.visit(node.value)

        return ast.Return(value=new_value)

    def visit_For(self, node: ast.For) -> list[ast.stmt] | ast.For:
        """Visit for loops and handle tail calls inside them correctly.

        When a tail call occurs inside a for loop, we can't use continue because
        it would only continue the for loop, not the outer while True loop.
        Instead, we use a flag to track when a tail call happened inside the loop.

        Args:
            node: The For AST node to transform

        Returns:
            A list of statements: [flag_init, for_loop, flag_check]
            or just the transformed For node if at top level of while True
        """
        # Generate unique ID for this for loop
        loop_uuid = uuid.uuid4().hex[:8]
        loop_flag_name = f"__tacopy_returned_in_for_{loop_uuid}"

        # Create flag initialization: __tacopy_returned_in_for_UUID = False
        flag_init = ast.Assign(
            targets=[ast.Name(id=loop_flag_name, ctx=ast.Store())],
            value=ast.Constant(value=False),
        )

        # Push this loop onto the stack
        self.loop_stack.append(("for", loop_uuid, loop_flag_name))

        # Replace parameter references in the loop target and iter
        node.target = self._replace_params_in_target(node.target)  # type: ignore[assignment]
        node.iter = self._replace_params_in_expr(node.iter)  # type: ignore[assignment]

        # Transform the body
        new_body = []
        for stmt in node.body:
            result = self.visit(stmt)
            if isinstance(result, list):
                new_body.extend(result)
            else:
                new_body.append(result)
        node.body = new_body

        # Transform the orelse
        new_orelse = []
        for stmt in node.orelse:
            result = self.visit(stmt)
            if isinstance(result, list):
                new_orelse.extend(result)
            else:
                new_orelse.append(result)
        node.orelse = new_orelse

        # Pop this loop from the stack
        self.loop_stack.pop()

        # Create flag check after the loop
        # If we're inside another loop, propagate the flag and break
        # If we're at top level, continue the while True loop
        if self.loop_stack:
            # We're nested inside another loop
            parent_type, parent_uuid, parent_flag_name = self.loop_stack[-1]
            # if __tacopy_returned_in_for_UUID:
            #     __tacopy_returned_in_<parent_type>_PARENT_UUID = True
            #     break
            flag_check = ast.If(
                test=ast.Name(id=loop_flag_name, ctx=ast.Load()),
                body=[
                    ast.Assign(
                        targets=[ast.Name(id=parent_flag_name, ctx=ast.Store())],
                        value=ast.Constant(value=True),
                    ),
                    ast.Break(),
                ],
                orelse=[],
            )
        else:
            # We're at the top level (directly inside while True)
            # if __tacopy_returned_in_for_UUID:
            #     continue
            flag_check = ast.If(
                test=ast.Name(id=loop_flag_name, ctx=ast.Load()),
                body=[ast.Continue()],
                orelse=[],
            )

        # Return list of statements: flag_init, for loop, flag_check
        return [flag_init, node, flag_check]  # type: ignore[return-value]

    def visit_While(self, node: ast.While) -> list[ast.stmt] | ast.While:
        """Visit while loops and handle tail calls inside them correctly.

        When a tail call occurs inside a while loop, we can't use continue because
        it would only continue the while loop, not the outer while True loop.
        Instead, we use a flag to track when a tail call happened inside the loop.

        Args:
            node: The While AST node to transform

        Returns:
            A list of statements: [flag_init, while_loop, flag_check]
        """
        # Generate unique ID for this while loop
        loop_uuid = uuid.uuid4().hex[:8]
        loop_flag_name = f"__tacopy_returned_in_while_{loop_uuid}"

        # Create flag initialization: __tacopy_returned_in_while_UUID = False
        flag_init = ast.Assign(
            targets=[ast.Name(id=loop_flag_name, ctx=ast.Store())],
            value=ast.Constant(value=False),
        )

        # Push this loop onto the stack
        self.loop_stack.append(("while", loop_uuid, loop_flag_name))

        # Replace parameter references in the loop condition
        node.test = self._replace_params_in_expr(node.test)  # type: ignore[assignment]

        # Transform the body
        new_body = []
        for stmt in node.body:
            result = self.visit(stmt)
            if isinstance(result, list):
                new_body.extend(result)
            else:
                new_body.append(result)
        node.body = new_body

        # Transform the orelse
        new_orelse = []
        for stmt in node.orelse:
            result = self.visit(stmt)
            if isinstance(result, list):
                new_orelse.extend(result)
            else:
                new_orelse.append(result)
        node.orelse = new_orelse

        # Pop this loop from the stack
        self.loop_stack.pop()

        # Create flag check after the loop
        # If we're inside another loop, propagate the flag and break
        # If we're at top level, continue the while True loop
        if self.loop_stack:
            # We're nested inside another loop
            parent_type, parent_uuid, parent_flag_name = self.loop_stack[-1]
            # if __tacopy_returned_in_while_UUID:
            #     __tacopy_returned_in_<parent_type>_PARENT_UUID = True
            #     break
            flag_check = ast.If(
                test=ast.Name(id=loop_flag_name, ctx=ast.Load()),
                body=[
                    ast.Assign(
                        targets=[ast.Name(id=parent_flag_name, ctx=ast.Store())],
                        value=ast.Constant(value=True),
                    ),
                    ast.Break(),
                ],
                orelse=[],
            )
        else:
            # We're at the top level (directly inside while True)
            # if __tacopy_returned_in_while_UUID:
            #     continue
            flag_check = ast.If(
                test=ast.Name(id=loop_flag_name, ctx=ast.Load()),
                body=[ast.Continue()],
                orelse=[],
            )

        # Return list of statements: flag_init, while loop, flag_check
        return [flag_init, node, flag_check]  # type: ignore[return-value]

    def visit_If(self, node: ast.If) -> ast.If:
        """Visit if statements and transform their bodies.

        Args:
            node: The If AST node to transform

        Returns:
            The transformed If node with updated conditions and bodies
        """
        # Replace parameter references in the test condition
        node.test = self._replace_params_in_expr(node.test)  # type: ignore[assignment]

        # Transform body
        new_body = []
        for stmt in node.body:
            result = self.visit(stmt)
            if isinstance(result, list):
                new_body.extend(result)
            else:
                new_body.append(result)
        node.body = new_body

        # Transform orelse
        new_orelse = []
        for stmt in node.orelse:
            result = self.visit(stmt)
            if isinstance(result, list):
                new_orelse.extend(result)
            else:
                new_orelse.append(result)
        node.orelse = new_orelse

        return node

    def visit_Expr(self, node: ast.Expr) -> ast.Expr:
        """Visit expression statements and replace parameter references.

        Args:
            node: The Expr AST node to transform

        Returns:
            The Expr node with parameter references replaced
        """
        node.value = self._replace_params_in_expr(node.value)  # type: ignore[assignment]
        return node

    def visit_Assign(self, node: ast.Assign) -> ast.Assign:
        """Visit assignment statements and replace parameter references.

        Both the left-hand side (targets) and right-hand side (value) of
        assignments need parameter references updated to use temporary variables.

        Args:
            node: The Assign AST node to transform

        Returns:
            The Assign node with parameter references replaced
        """
        # Replace parameter references in the value (RHS)
        node.value = self._replace_params_in_expr(node.value)  # type: ignore[assignment]

        # Replace parameter references in the targets (LHS)
        # If assigning to a parameter, we need to assign to the temp variable instead
        new_targets: list[ast.expr] = []
        for target in node.targets:
            new_targets.append(self._replace_params_in_target(target))  # type: ignore[arg-type]
        node.targets = new_targets

        return node

    def _replace_params_in_target(self, target: ast.AST) -> ast.AST:
        """Replace parameter references in assignment targets.

        When a parameter is assigned to within the function body, we need to
        redirect that assignment to the temporary variable instead.

        Args:
            target: The assignment target AST node

        Returns:
            The target node with parameter references replaced
        """

        class TargetReplacer(ast.NodeTransformer):
            def __init__(self, param_map):
                self.param_map = param_map

            def visit_Name(self, node: ast.Name) -> ast.Name:
                if node.id in self.param_map:
                    return ast.Name(id=self.param_map[node.id], ctx=node.ctx)
                return node

        param_map = {param: self._get_temp_name(param) for param in self.param_names}
        replacer = TargetReplacer(param_map)
        return replacer.visit(target)

    def _replace_params_in_expr(self, expr: ast.AST) -> ast.AST:
        """Replace all parameter references in an expression with temp variables.

        This method is used throughout the transformer to ensure all references
        to function parameters are updated to use the temporary variables created
        at the start of the transformed function.

        Args:
            expr: The expression AST node to process

        Returns:
            The expression with parameter references replaced
        """

        class ParamReplacer(ast.NodeTransformer):
            def __init__(self, param_map):
                self.param_map = param_map

            def visit_Name(self, node: ast.Name) -> ast.Name:
                if node.id in self.param_map:
                    return ast.Name(id=self.param_map[node.id], ctx=node.ctx)
                return node

        param_map = {param: self._get_temp_name(param) for param in self.param_names}
        replacer = ParamReplacer(param_map)
        return replacer.visit(expr)

    def _is_recursive_call(self, call: ast.Call) -> bool:
        """Check if a call node is a recursive call to the target function.

        Args:
            call: The Call AST node to check

        Returns:
            True if this is a recursive call, False otherwise
        """
        if isinstance(call.func, ast.Name) and call.func.id == self.function_name:
            return True
        return False

    def _get_temp_name(self, param: str) -> str:
        """Get the temporary variable name for a parameter.

        Args:
            param: The original parameter name

        Returns:
            The unique temporary variable name with UUID prefix
        """
        return f"{self.var_prefix}{param}"


def transform_function(tree: ast.AST, function_name: str) -> ast.AST:
    """Transform a tail-recursive function into an iterative loop.

    This is the main entry point for the transformation. It creates a
    TailCallTransformer instance and applies it to the given AST, then
    fixes any missing location information in the resulting tree.

    Args:
        tree: The AST of the module containing the function to transform
        function_name: The name of the function to transform

    Returns:
        The transformed AST with the function converted to use iteration

    Example:
        >>> source = '''
        ... def factorial(n, acc=1):
        ...     if n == 0:
        ...         return acc
        ...     return factorial(n - 1, acc * n)
        ... '''
        >>> tree = ast.parse(source)
        >>> new_tree = transform_function(tree, "factorial")
        >>> # new_tree now contains the iterative version
    """
    transformer = TailCallTransformer(function_name)
    new_tree = transformer.visit(tree)
    ast.fix_missing_locations(new_tree)
    return new_tree
