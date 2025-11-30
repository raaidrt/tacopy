"""List length function with tail recursion."""


def list_length(lst: list, acc: int = 0) -> int:
    """Calculate the length of a list using tail recursion."""
    if not lst:
        return acc
    return list_length(lst[1:], acc + 1)
