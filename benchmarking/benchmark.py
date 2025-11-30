"""Benchmarking suite for tacopy tail recursion optimization."""

import importlib.util
import sys
import time
from collections.abc import Callable
from pathlib import Path
from statistics import mean, stdev

from tqdm import tqdm

from tacopy import tacopy


def load_function_from_file(file_path: Path, function_name: str) -> Callable:
    """Dynamically load a function from a Python file.

    Args:
        file_path: Path to the Python file
        function_name: Name of the function to load

    Returns:
        The loaded function
    """
    spec = importlib.util.spec_from_file_location(file_path.stem, file_path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Cannot load module from {file_path}")

    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return getattr(module, function_name)


def apply_tacopy_decorator(func: Callable) -> Callable:
    """Apply the tacopy decorator to a function.

    Args:
        func: The function to decorate

    Returns:
        The decorated function
    """
    return tacopy(func)


def time_function(func: Callable, args: tuple, num_runs: int = 100, desc: str = "") -> list[float]:
    """Time a function execution multiple times.

    Args:
        func: The function to time
        args: Arguments to pass to the function
        num_runs: Number of times to run the function
        desc: Description for progress bar

    Returns:
        List of execution times in seconds
    """
    times = []
    for _ in tqdm(range(num_runs), desc=desc, leave=False, ncols=80):
        start = time.perf_counter()
        func(*args)
        end = time.perf_counter()
        times.append(end - start)
    return times


class BenchmarkCase:
    """Represents a single benchmark case."""

    def __init__(self, name: str, file_path: Path, function_name: str, args: tuple):
        """Initialize a benchmark case.

        Args:
            name: Display name for the benchmark
            file_path: Path to the file containing the function
            function_name: Name of the function
            args: Arguments to pass to the function
        """
        self.name = name
        self.file_path = file_path
        self.function_name = function_name
        self.args = args


def run_benchmark_suite(num_runs: int = 100) -> None:
    """Run the complete benchmark suite and display results.

    Args:
        num_runs: Number of times to run each benchmark
    """
    samples_dir = Path(__file__).parent / "samples"

    # Define benchmark cases
    # Note: Regular recursion uses 1000 iterations (safe with increased recursion limit)
    SMALL_N = 1000  # Safe recursion depth for non-tacopy

    benchmark_cases = [
        BenchmarkCase("factorial(1000)", samples_dir / "factorial.py", "factorial", (SMALL_N,)),
        BenchmarkCase("fibonacci(1000)", samples_dir / "fibonacci.py", "fibonacci", (SMALL_N,)),
        BenchmarkCase("sum_to_n(1000)", samples_dir / "sum_to_n.py", "sum_to_n", (SMALL_N,)),
        BenchmarkCase("power(2, 1000)", samples_dir / "power.py", "power", (2, SMALL_N)),
    ]

    # Increase recursion limit for non-tacopy versions
    original_limit = sys.getrecursionlimit()
    sys.setrecursionlimit(2000)

    print("=" * 100)
    print(f"TACOPY BENCHMARKING SUITE - {num_runs} runs per case")
    print("=" * 100)
    print()

    # Table header
    print(f"{'Function':<30} | {'Without tacopy':<30} | {'With tacopy':<30}")
    print(f"{'':<30} | {'Mean ± StdDev (seconds)':<30} | {'Mean ± StdDev (seconds)':<30}")
    print("-" * 100)

    results = []

    for case in tqdm(benchmark_cases, desc="Overall Progress", ncols=100):
        # Load the function
        func_without_tacopy = load_function_from_file(case.file_path, case.function_name)

        # Create a tacopy-decorated version
        func_with_tacopy = apply_tacopy_decorator(
            load_function_from_file(case.file_path, case.function_name)
        )

        # Run benchmarks
        tqdm.write(f"\n{'=' * 80}")
        tqdm.write(f"Benchmarking: {case.name}")
        tqdm.write(f"{'=' * 80}")

        times_without = time_function(
            func_without_tacopy, case.args, num_runs, desc="  Without tacopy"
        )
        times_with = time_function(func_with_tacopy, case.args, num_runs, desc="  With tacopy   ")

        # Calculate statistics
        mean_without = mean(times_without)
        stdev_without = stdev(times_without) if len(times_without) > 1 else 0

        mean_with = mean(times_with)
        stdev_with = stdev(times_with) if len(times_with) > 1 else 0

        results.append(
            {
                "name": case.name,
                "mean_without": mean_without,
                "stdev_without": stdev_without,
                "mean_with": mean_with,
                "stdev_with": stdev_with,
            }
        )

        speedup = mean_without / mean_with
        tqdm.write(f"  Speedup: {speedup:.2f}x\n")

    print()

    # Display results table
    print(f"{'Function':<30} | {'Without tacopy':<30} | {'With tacopy':<30}")
    print(f"{'':<30} | {'Mean ± StdDev (seconds)':<30} | {'Mean ± StdDev (seconds)':<30}")
    print("-" * 100)

    for result in results:
        name = result["name"]
        without_str = f"{result['mean_without']:.6f} ± {result['stdev_without']:.6f}"
        with_str = f"{result['mean_with']:.6f} ± {result['stdev_with']:.6f}"

        print(f"{name:<30} | {without_str:<30} | {with_str:<30}")

    print("-" * 100)
    print()

    # Calculate and display speedup statistics
    print("SPEEDUP ANALYSIS:")
    print("-" * 100)
    print(f"{'Function':<30} | {'Speedup Factor':<20} | {'Performance Change':<20}")
    print("-" * 100)

    for result in results:
        speedup = result["mean_without"] / result["mean_with"]
        percentage = ((result["mean_with"] - result["mean_without"]) / result["mean_without"]) * 100

        if speedup > 1:
            change = f"{percentage:.1f}% faster"
        elif speedup < 1:
            change = f"{abs(percentage):.1f}% slower"
        else:
            change = "No change"

        print(f"{result['name']:<30} | {speedup:.2f}x{'':<15} | {change:<20}")

    print("-" * 100)
    print()

    # Restore original recursion limit
    sys.setrecursionlimit(original_limit)

    print(f"Benchmarking complete! Each case was run {num_runs} times.")
    print(f"Recursion limit was set to {sys.getrecursionlimit()} for non-tacopy functions.")


if __name__ == "__main__":
    run_benchmark_suite(num_runs=100)
