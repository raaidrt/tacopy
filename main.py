import tacopy

@tacopy.tacopy
def factorial_mod_k(acc: int, n: int, k: int) -> int:
    @tacopy.tacopy 
    def inner_function():
        pass
    global a, b
    a = 1
    b = 2
    if n == 0:
        return acc % k
    return factorial_mod_k(acc * n % k, n - 1, k)

print(factorial_mod_k(1, 10, 1_000_000_007))
