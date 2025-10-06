"""
Greeting utilities module.

This module provides simple greeting functions for user interaction.
"""


def say_hello(name: str) -> str:
    """
    Generate a greeting message for the given name.
    
    Args:
        name (str): The name to greet
        
    Returns:
        str: A greeting message in the format "Hello, {name}!"
        
    Example:
        >>> say_hello("World")
        'Hello, World!'
        >>> say_hello("Alice")
        'Hello, Alice!'
    """
    return f"Hello, {name}!"