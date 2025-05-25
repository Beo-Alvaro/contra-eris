"""
Sample module for testing Contra Eris
"""

import math
from datetime import datetime

# Define a constant
PI = 3.14159

class Calculator:
    """A simple calculator class for testing"""
    
    def __init__(self, initial_value=0):
        """Initialize with an optional starting value"""
        self.value = initial_value
        self.history = []
    
    def add(self, x):
        """Add a number to the current value"""
        self.history.append(f"Added {x}")
        self.value += x
        return self.value
    
    def subtract(self, x):
        """Subtract a number from the current value"""
        self.history.append(f"Subtracted {x}")
        self.value -= x
        return self.value
    
    def multiply(self, x):
        """Multiply the current value by a number"""
        self.history.append(f"Multiplied by {x}")
        self.value *= x
        return self.value
    
    def divide(self, x):
        """Divide the current value by a number"""
        if x == 0:
            raise ValueError("Cannot divide by zero")
        self.history.append(f"Divided by {x}")
        self.value /= x
        return self.value
    
    def get_history(self):
        """Return operation history"""
        return self.history


def square_root(x):
    """Calculate square root of a number"""
    if x < 0:
        raise ValueError("Cannot calculate square root of negative number")
    return math.sqrt(x)


def factorial(n):
    """Calculate factorial of n"""
    if n < 0:
        raise ValueError("Factorial not defined for negative numbers")
    if n == 0:
        return 1
    return n * factorial(n - 1)


def get_current_time():
    """Return current timestamp"""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


if __name__ == "__main__":
    # Example usage
    calc = Calculator(10)
    calc.add(5)
    calc.multiply(2)
    print(f"Result: {calc.value}")
    print(f"History: {calc.get_history()}")
    
    print(f"Square root of 16: {square_root(16)}")
    print(f"Factorial of 5: {factorial(5)}")
    print(f"Current time: {get_current_time()}") 