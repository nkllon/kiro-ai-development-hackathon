# Test Prompt for Hook System

## Task Request
Create a simple Python function that says hello to a given name.

## Requirements
- Function should be named `say_hello`
- Takes a `name` parameter
- Returns a greeting string
- Include basic docstring
- Save to `src/utils/greetings.py`

## Expected Output
A working Python function with proper documentation that can be imported and used.

## Test
The function should work like this:
```python
from src.utils.greetings import say_hello
result = say_hello("World")
print(result)  # Should output: "Hello, World!"
```