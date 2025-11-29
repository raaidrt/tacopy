# Tacopy

**Author:** Raaid Tanveer  
**Date:** 2025-11-15

## Introduction

Python is an interpreted language. This means that any Python programs that are run are not privy to any and all of the modern compiler optimizations that make modern programming languages fast.

In the spirit of creating a library of common compiler optimizations that we can apply to Python functions, we are creating Tacopy, a Tail-Call Optimization Decorator.

## Goal

Tacopy should be used with the decorator `tacopy.tacopy`
```python
from tacopy import tacopy

@tacopy.tacopy
def factorial_mod_k(acc: int, n: int, k: int) -> int:
    if n == 0:
        return acc % k
    return factorial_mod_k(acc * n % k, n - 1, k)
```

The above function `factorial_mod_k` is supposed to calculate $\mathsf{acc} \cdot n! \bmod k$. This would clearly stack overflow if provided a high enough $n$.

For example, when running the following code
```python
factorial_mod_k(1, 1_000_000, 79)
```

We would encounter the following error
```
Traceback (most recent call last):
File "/tmp/sessions/3adb0068dda83218/main.py", line 4, in <module>
  print(factorial_mod_k(1, 1_000_000, 79))
File "/tmp/sessions/3adb0068dda83218/main.py", line 2, in factorial_mod_k
  return factorial_mod_k(acc * n % k, n - 1, k)
File "/tmp/sessions/3adb0068dda83218/main.py", line 2, in factorial_mod_k
  return factorial_mod_k(acc * n % k, n - 1, k)
File "/tmp/sessions/3adb0068dda83218/main.py", line 2, in factorial_mod_k
  return factorial_mod_k(acc * n % k, n - 1, k)
[Previous line repeated 996 more times]
RecursionError: maximum recursion depth exceeded
```

## AST Modification

A really simple way of enabling tail-recursion optimization on Python code is by hoisting the function arguments to the top level, and just looping within the code. For example, the function `factorial_mod_k` would become
```python
def factorial_mod_k(acc: int, n: int, k: int) -> int:
    _acc = acc
    _n = n
    _k = k
    while True:
        if (_n == 0):
            return _acc % _k
        _acc, _n, _k = _acc * _n % _k, _n - 1, _k
```

The problem with this implementation is that the symbols `_acc`, `_n`, and `_k` might be used as globals in the rest of the python program, or these symbols may already be used in the function body elsewhere.

A way to get around this problem is by using a dictionary that is maintained within the `tacopy` namespace. This dictionary should be able to map (namespace, function, argument) triples to their corresponding values during function execution for that particular run. We need to figure out a way to bind the values to a specific execution of the function, since multiple function executions sharing the same set of variables may be a problem with async functions in python. If the binding problem is not solvable, we must disallow async functions to use the `tacopy` decorator. 

A further edge case that must be considered in the implementation of this project is nested function definitions with `tacopy` decorators added on the nested functions as well. Please make sure to test those cases. 

## Tail Recursion Validation 
We need to be able to validate that the function that the `tacopy` decorator is being attached to is indeed a tail-recursive function (i.e. all recursive invocations of the function are indeed within return statements). If such is not the case, then an Exception with an informative error message must be raised.

## General Guidelines
### Visualization of Data Structures
We must be able to visualize the transformed AST's succinctly. We might be able to use the [astpretty](https://github.com/asottile/astpretty) Python library, but even that has a lot of extraneous information. It might be worth just converting the AST's into Python code to be able to examine the emitted AST's for testing purposes. 

### Testing 
The components of the decorator must be modular, and each module must be tested sufficiently with unit tests. Furthermore, we must have a sufficient suite of end-to-end tests. Please use Python's `pytest` framework to write the tests. You may consider using a snapshot testing framework, like [syrupy](https://github.com/syrupy-project/syrupy) to help us test code emissions accurately. 