def add_numbers(a, b):
    """
    Add two numbers together.
    
    Args:
        a (int or float): First number
        b (int or float): Second number
    
    Returns:
        int or float: The sum of a and b
    """
    return a + b


# Example usage
if __name__ == "__main__":
    # Test with integers
    result1 = add_numbers(5, 3)
    print(f"5 + 3 = {result1}")
    
    # Test with floats
    result2 = add_numbers(2.5, 1.7)
    print(f"2.5 + 1.7 = {result2}")
    
    # Test with mixed types
    result3 = add_numbers(10, 3.14)
    print(f"10 + 3.14 = {result3}")