#!/usr/bin/env python3
"""
Simple Hello World module for testing Cursor CLI functionality.

This module contains a basic hello world function with proper type hints
and documentation following Python best practices.
"""

from typing import Optional


def hello_world(name: Optional[str] = None) -> str:
    """
    Generate a personalized hello world greeting.
    
    Args:
        name: Optional name to include in the greeting. If None, uses "World".
        
    Returns:
        A formatted greeting string.
        
    Examples:
        >>> hello_world()
        'Hello, World!'
        >>> hello_world("Alice")
        'Hello, Alice!'
    """
    if name is None:
        name = "World"
    
    return f"Hello, {name}!"


def main() -> None:
    """Main function to demonstrate the hello_world function."""
    print(hello_world())
    print(hello_world("Cursor CLI"))
    print(hello_world("Python Developer"))


if __name__ == "__main__":
    main()