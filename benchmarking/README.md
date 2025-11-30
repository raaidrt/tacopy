# Tacopy Benchmarking Suite

This directory contains a benchmarking suite for measuring the performance impact of tacopy's tail-call optimization.

## Structure

```
benchmarking/
├── benchmark.py          # Main benchmark script
├── samples/              # Sample tail-recursive functions
│   ├── factorial.py
│   ├── fibonacci.py
│   ├── gcd.py
│   ├── sum_to_n.py
│   ├── power.py
│   ├── list_length.py
│   └── reverse_string.py
└── README.md            # This file
```

## Running Benchmarks

To run the benchmark suite:

```bash
uv run python benchmarking/benchmark.py
```

The script will:
1. Run each benchmark function 100 times with and without tacopy optimization
2. Calculate mean and standard deviation for execution times
3. Display results in a formatted table
4. Show speedup analysis

## Sample Functions

The benchmarking suite includes the following tail-recursive functions (all using modular arithmetic to prevent integer overflow):

- **factorial_mod_k(900)**: Compute factorial modulo 10^9+7 with accumulator
- **fibonacci_mod_k(900)**: Calculate nth Fibonacci number modulo 10^9+7
- **sum_to_n_mod_k(900)**: Sum from 1 to n modulo 10^9+7 with accumulator
- **power_mod_k(2, 900)**: Exponentiation modulo 10^9+7 with accumulator

## Output Format

The benchmark produces two tables:

### Performance Table
Shows mean ± standard deviation for execution times (in seconds) for each function with and without tacopy.

### Speedup Analysis
Shows the speedup factor and percentage performance improvement for each function.

## Adding New Benchmarks

To add a new benchmark:

1. Create a new file in `samples/` with your tail-recursive function
2. Add a new `BenchmarkCase` in [benchmark.py](benchmark.py) with:
   - Display name
   - File path
   - Function name
   - Test arguments

Example:
```python
BenchmarkCase(
    "my_function(100)",
    samples_dir / "my_function.py",
    "my_function",
    (100,)
)
```

## Notes

- The recursion limit is temporarily set to 2000 for non-tacopy functions
- Each benchmark is run 100 times by default (configurable)
- Benchmarks use 900 iterations (safe for most systems without tacopy)
- Functions without tacopy may hit recursion limits for very large inputs
- Tacopy-optimized functions have no recursion depth limits and can handle millions of iterations
- Modular arithmetic (mod 10^9+7) is used to prevent integer overflow while maintaining computational complexity
