# DeepSeek Code Generation Instructions

## Mission
Generate high-quality Python code that passes Claude's review on first or second iteration. Learn from feedback to continuously improve code generation quality.

## Core Principles

### 1. Code Quality First
- **Type Hints**: Always include complete type annotations
- **Docstrings**: Every function/class must have comprehensive docstrings
- **Error Handling**: Proper try/except with specific exceptions
- **Validation**: Input validation and edge case handling

### 2. Python Best Practices
- **PEP 8 Compliance**: Follow Python style guide strictly
- **Black Formatting**: Code must be black-formatted
- **Meaningful Names**: Clear, descriptive variable/function names
- **DRY Principle**: Don't repeat yourself

### 3. Security & Safety
- **No Hardcoded Secrets**: Use environment variables
- **Input Sanitization**: Validate all external inputs
- **Resource Management**: Proper context managers and cleanup
- **Thread Safety**: Use appropriate locking mechanisms

### 4. Architecture Patterns
- **SOLID Principles**: Single responsibility, dependency injection
- **Async/Await**: Proper async patterns, no sync/async mixing
- **Type Safety**: Leverage Python's type system
- **Separation of Concerns**: Clear module boundaries

## ⚠️ CRITICAL: Claude Rejects 100% of Code Without These

**ANALYSIS OF 59 REVIEWS: 0% APPROVAL RATE**

Every single rejection included these issues. Fix them FIRST:

### 🔴 MANDATORY (100% of rejections):
1. **Missing Docstrings** (100%)
   - EVERY class, function, and module MUST have comprehensive docstrings
   - Include: purpose, parameters, return values, exceptions, usage examples
   - No exceptions - even simple functions need docstrings

2. **Weak Error Handling** (100%)
   - NEVER use bare `except:` or generic exception catching
   - ALWAYS catch specific exceptions (ValueError, TypeError, etc.)
   - ALWAYS log errors with context
   - Include proper error messages for users

3. **Missing Input Validation** (98.3%)
   - Validate EVERY input parameter at function entry
   - Check for None, empty strings, invalid types, out-of-range values
   - Raise ValueError/TypeError with clear messages
   - Never assume inputs are valid

### 🟠 CRITICAL (80%+ of rejections):
4. **Security Concerns** (83.1%)
   - Input sanitization on ALL external data
   - No hardcoded credentials anywhere
   - SQL injection prevention (parameterized queries)
   - Path traversal prevention

5. **Incomplete Implementation** (83.1%)
   - NO `pass` statements in production code
   - NO TODO comments left unaddressed
   - Implement ALL required functionality
   - No placeholder methods

6. **Missing Logging** (81.4%)
   - Import logging module
   - Create logger: `logger = logging.getLogger(__name__)`
   - Log errors, warnings, and key operations
   - Include context in log messages

7. **Incomplete Type Hints** (74.6%)
   - Type ALL parameters and return values
   - Use `typing` module: `Optional`, `Union`, `List`, `Dict`, `Any`
   - No missing type hints anywhere

4. **Security Concerns**
   - Never hardcode credentials
   - Sanitize inputs
   - Use secure defaults
   - Implement rate limiting where appropriate

5. **Async/Sync Mixing**
   - Don't mix `threading.Lock` with `asyncio`
   - Use `asyncio.Lock()` for async code
   - Be consistent with async/await patterns

6. **Incomplete Implementations**
   - Don't leave `pass` statements in production code
   - Implement all required methods
   - Complete all TODO comments before submission

## Code Generation Template

```python
"""
Module docstring explaining purpose and usage.
"""

from typing import Optional, List, Dict, Any
import asyncio
import logging

logger = logging.getLogger(__name__)


class YourClass:
    """
    Class docstring with purpose and usage examples.

    Args:
        param1: Description of parameter
        param2: Description of parameter

    Example:
        >>> obj = YourClass("value")
        >>> obj.method()
    """

    def __init__(self, param1: str, param2: Optional[int] = None) -> None:
        """Initialize with validation."""
        if not param1:
            raise ValueError("param1 cannot be empty")

        self.param1 = param1
        self.param2 = param2

    async def async_method(self, input_data: Dict[str, Any]) -> List[str]:
        """
        Method docstring explaining what it does.

        Args:
            input_data: Dictionary containing input parameters

        Returns:
            List of processed results

        Raises:
            ValueError: If input_data is invalid
        """
        try:
            # Validate input
            if not input_data:
                raise ValueError("input_data cannot be empty")

            # Implementation
            results = []
            # ... actual logic here

            return results

        except Exception as e:
            logger.error(f"Error in async_method: {e}")
            raise
```

## Review Optimization

### First Iteration Goals
- Complete type hints
- Comprehensive docstrings
- Basic error handling
- Core functionality implemented

### Second Iteration (if needed)
- Enhanced error handling
- Edge case coverage
- Performance optimization
- Security hardening

### Approval Criteria
Claude approves when code has:
- ✅ Complete type annotations
- ✅ Comprehensive docstrings
- ✅ Proper error handling
- ✅ Security best practices
- ✅ No obvious bugs or issues
- ✅ Clean, readable structure

## Learning Feedback Loop

Review `deepseek_learning.md` to understand:
- What Claude consistently flags
- Common patterns in rejections
- Successful patterns in approvals
- Task-specific improvements

**Goal**: Achieve >80% first-iteration approval rate through continuous learning.

## Task-Specific Guidelines

### API Clients
- Use `requests` or `httpx` appropriately
- Implement retry logic with exponential backoff
- Handle timeouts and network errors
- Include proper authentication

### Data Processing
- Validate inputs thoroughly
- Handle edge cases (empty, None, invalid types)
- Use appropriate data structures
- Optimize for performance

### Async Code
- Use `asyncio.Lock()` not `threading.Lock()`
- Proper `async with` context managers
- Handle concurrent operations safely
- Implement timeouts

### Testing Code
- Use `pytest` framework
- Include fixtures for setup/teardown
- Test edge cases and errors
- Aim for >90% coverage

## Success Metrics

Track these metrics via `deepseek_learning.md`:
- First-iteration approval rate
- Average iterations to approval
- Common rejection reasons
- Time to generate quality code

**Target**: <2 iterations average, >80% first-pass approval rate

---

**Remember**: Quality over speed. It's better to take 10 more seconds and generate code that passes review immediately than to rush and require 5 revision cycles.
