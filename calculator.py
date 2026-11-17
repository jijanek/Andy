"""Basic arithmetic for integers and floating-point numbers."""

Number = int | float


def add(left: Number, right: Number) -> Number:
    """Return the sum of two numbers."""
    return left + right


def subtract(left: Number, right: Number) -> Number:
    """Subtract right from left."""
    return left - right


def multiply(left: Number, right: Number) -> Number:
    """Return the product of two numbers."""
    return left * right


def divide(left: Number, right: Number) -> float:
    """Return true division; a zero divisor raises ZeroDivisionError."""
    return left / right
