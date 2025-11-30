"""String reversal function with tail recursion."""


def reverse_string(s: str, acc: str = "") -> str:
    """Reverse a string using tail recursion."""
    if not s:
        return acc
    return reverse_string(s[1:], s[0] + acc)
