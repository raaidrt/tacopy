# Tacopy

**Tail-Call Optimization for Python**

Tacopy is a Python library that provides a decorator to optimize tail-recursive functions by transforming them into iterative loops. This eliminates the risk of stack overflow errors for deep recursion.

## Features

- **Automatic Tail-Call Optimization**: Transforms tail-recursive functions into efficient loops
- **Stack Overflow Prevention**: Handle arbitrarily deep recursion without hitting Python's recursion limit
- **Significant Performance Gains**: **1.41x-2.88x faster** than regular recursion (see [benchmarks](#performance-benchmarks))
- **Validation**: Ensures functions are properly tail-recursive before transformation
- **No Runtime Overhead**: Optimization happens once at decoration time
- **Preservation of Function Metadata**: Keeps docstrings, type hints, and other metadata intact

## Installation

```bash
# Using uv (recommended for development)
uv add tacopy-optimization

# Using pip
pip install tacopy-optimization
```

## Quick Start

```python
from tacopy import tacopy

@tacopy
def factorial_mod_k(acc: int, n: int, k: int) -> int:
    """Calculate (acc * n!) mod k using tail recursion."""
    if n == 0:
        return acc % k
    return factorial_mod_k(acc * n % k, n - 1, k)

# This would normally cause a stack overflow, but works with @tacopy
result = factorial_mod_k(1, 1_000_000, 79)
print(result)  # Output: 0
```

## How It Works

Tacopy uses AST (Abstract Syntax Tree) transformation to convert tail-recursive functions into iterative loops. For example:

**Original function:**
```python
@tacopy
def factorial(n: int, acc: int = 1) -> int:
    if n == 0:
        return acc
    return factorial(n - 1, acc * n)
```

**Transformed to (conceptually):**
```python
def factorial(n: int, acc: int = 1) -> int:
    _n = n
    _acc = acc
    while True:
        if _n == 0:
            return _acc
        _n, _acc = _n - 1, _acc * _n
```

The transformation:
1. Hoists parameters to uniquely-named local variables (using UUIDs to avoid collisions)
2. Wraps the function body in a `while True` loop
3. Replaces tail-recursive calls with variable assignments and `continue` statements

## Examples

### Fibonacci Numbers

```python
@tacopy
def fibonacci(n: int, a: int = 0, b: int = 1) -> int:
    """Calculate the nth Fibonacci number."""
    if n == 0:
        return a
    if n == 1:
        return b
    return fibonacci(n - 1, b, a + b)

# Calculate very large Fibonacci numbers
fib_5000 = fibonacci(5000)
```

### Greatest Common Divisor (GCD)

```python
@tacopy
def gcd(a: int, b: int) -> int:
    """Calculate GCD using Euclidean algorithm."""
    if b == 0:
        return a
    return gcd(b, a % b)

print(gcd(1071, 462))  # Output: 21
```

### Sum with Accumulator

```python
@tacopy
def sum_to_n(n: int, acc: int = 0) -> int:
    """Calculate sum from 1 to n."""
    if n == 0:
        return acc
    return sum_to_n(n - 1, acc + n)

print(sum_to_n(100))  # Output: 5050
```

## Requirements for Tail Recursion

For a function to be optimizable with `@tacopy`, it must be **properly tail-recursive**:

1. **Module-level function** - The function must be defined at module level, not nested inside another function
2. **All recursive calls must be in tail position** - the return value of the recursive call must be immediately returned, with no further operations
3. **No async functions** - Async functions are not supported due to potential issues with shared state

### Valid Tail Recursion

```python
@tacopy
def valid(n, acc):
    if n == 0:
        return acc
    return valid(n - 1, acc + n)  #  Tail call - immediately returned
```

### Invalid (Non-Tail) Recursion

```python
@tacopy
def invalid(n):
    if n == 0:
        return 1
    return n * invalid(n - 1)  #  NOT tail recursive - multiplication after call
```

### Nested Functions Not Allowed

```python
def outer():
    @tacopy  # ❌ Error: nested functions cannot use @tacopy
    def helper(n, acc):
        if n == 0:
            return acc
        return helper(n - 1, acc + n)
    return helper(10, 0)

# ✅ Correct: Extract to module level
@tacopy
def helper(n, acc):
    if n == 0:
        return acc
    return helper(n - 1, acc + n)

def outer():
    return helper(10, 0)
```

The decorator will raise a `TailRecursionError` if the function is not properly tail-recursive or if it is nested inside another function.

## Debugging

You can view the transformed code without executing it:

```python
from tacopy import show_transformed_code

def factorial(n: int, acc: int = 1) -> int:
    if n == 0:
        return acc
    return factorial(n - 1, acc * n)

print(show_transformed_code(factorial))
```

## Performance Benchmarks

Tacopy provides significant performance improvements over regular recursion. Below are benchmark results comparing tail-recursive functions with and without the `@tacopy` decorator (100 runs each, recursion depth of 1000):

| Function | Without tacopy | With tacopy | Speedup | Performance Change |
|----------|-----------------|-------------|---------|--------------------|
| `factorial(1000)` | 0.000230 ± 0.000117s | 0.000163 ± 0.000019s | **1.41x faster** | 29.2% faster |
| `fibonacci(1000)` | 0.000083 ± 0.000008s | 0.000045 ± 0.000013s | **1.86x faster** | 46.4% faster |
| `sum_to_n(1000)` | 0.000074 ± 0.000013s | 0.000026 ± 0.000002s | **2.88x faster** | 65.2% faster |
| `power(2, 1000)` | 0.000087 ± 0.000008s | 0.000044 ± 0.000008s | **1.97x faster** | 49.3% faster |

### Key Takeaways

- **1.41x-2.88x speedup** for typical tail-recursive functions
- **Eliminates stack overflow**: Regular Python recursion is limited to 1000 calls, while tacopy can handle millions
- **Lower variance**: Tacopy-optimized functions show more consistent performance (lower standard deviation)

### Running Benchmarks

You can run the benchmarking suite yourself:

```bash
uv run python benchmarking/benchmark.py
```

The benchmarks use a recursion depth of 1000 for non-tacopy functions and pure integer arithmetic in the sample implementations. See [benchmarking/README.md](benchmarking/README.md) for more details.

## Development

### Setup

```bash
# Clone the repository
git clone https://github.com/yourusername/tacopy.git
cd tacopy

# Install dependencies using uv
uv sync

# Activate virtual environment
source .venv/bin/activate  # On Unix/macOS
# or
.venv\Scripts\activate  # On Windows
```

### Running Tests

```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=tacopy --cov-report=html

# Update snapshots (if you've changed transformation logic)
pytest tests/ --snapshot-update
```

### Project Structure

```
tacopy/
├── src/
│   └── tacopy/
│       ├── __init__.py      # Main decorator and public API
│       ├── validator.py     # Tail recursion validation
│       ├── transformer.py   # AST transformation logic
│       └── unparser.py      # AST to code conversion
├── tests/
│   ├── test_validator.py    # Validator unit tests
│   ├── test_transformer.py  # Transformer unit tests
│   └── test_integration.py  # End-to-end integration tests
├── main.py                  # Example usage
├── DESIGN.md                # Design document
└── README.md                # This file
```

## Limitations

1. **Module-level functions only**: The decorator can only be applied to functions defined at module level, not nested inside other functions. If you need to optimize a helper function, extract it to module level.
2. **Async functions not supported**: The decorator will raise an error if applied to async functions
3. **Source code required**: The function's source code must be accessible via `inspect.getsource()`
4. **No mutual recursion**: Only direct self-recursion is optimized
5. **Python 3.10+**: Requires Python 3.10 or higher

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the GNU General Public License v3.0 - see the [LICENSE](LICENSE) file for details.

## See Also

- [DESIGN.md](DESIGN.md) - Detailed design document
- [Python AST Documentation](https://docs.python.org/3/library/ast.html)
