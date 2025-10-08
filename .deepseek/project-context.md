# DeepSeek Project Context - Kiro AI Development Hackathon

## Project Overview
This is the **Kiro AI Development Hackathon** project - a systematic development framework called **Beast Mode** that demonstrates 10x velocity through systematic approaches.

## Tech Stack & Tools
- **Language**: Python 3.9+
- **Package Manager**: UV (not pip!)
- **Framework**: Beast Mode (systematic development)
- **Database**: SQLite for activity logging
- **Key Libraries**: anthropic, requests, redis, prometheus_client

## Critical Patterns You Must Follow

### 1. ReflectiveModule Pattern
All major components implement the ReflectiveModule base class:

```python
from src.beast_mode.reflective_module import ReflectiveModule
import logging

class YourComponent(ReflectiveModule):
    """Your component docstring"""

    def __init__(self):
        super().__init__()
        self.logger = logging.getLogger(__name__)
        self.module_name = "your_component"

    def validate(self) -> bool:
        """Validate component state"""
        # Implement validation logic
        return True
```

### 2. Logging Pattern
```python
import logging

logger = logging.getLogger(__name__)

# Use structured logging
logger.info(f"Operation started: {operation_name}")
logger.error(f"Error in {function_name}: {error}", exc_info=True)
```

### 3. Error Handling Pattern
```python
from typing import Optional

def your_function(param: str) -> Optional[Result]:
    """
    Function with proper error handling.

    Args:
        param: Description

    Returns:
        Result on success, None on failure

    Raises:
        ValueError: If param is invalid
        RuntimeError: If operation fails
    """
    # Validate inputs
    if not param:
        raise ValueError("param cannot be empty")

    try:
        # Implementation
        result = process(param)
        logger.info(f"Success: {result}")
        return result

    except SpecificException as e:
        logger.error(f"Error processing {param}: {e}", exc_info=True)
        raise RuntimeError(f"Failed to process: {e}") from e
```

### 4. Type Hints - Required Everywhere
```python
from typing import List, Dict, Optional, Any, Union
from pathlib import Path

def process_data(
    items: List[Dict[str, Any]],
    config_path: Path,
    timeout: Optional[int] = None
) -> Union[str, None]:
    """Always type everything"""
    pass
```

### 5. Validation Pattern
```python
def validate_input(data: Dict[str, Any]) -> bool:
    """Validate all inputs at function entry"""
    if not data:
        raise ValueError("data cannot be None or empty")

    if 'required_field' not in data:
        raise ValueError("Missing required_field")

    if not isinstance(data['required_field'], str):
        raise TypeError("required_field must be string")

    return True
```

## Project-Specific Context

### Beast Mode Framework
- **Purpose**: Systematic development methodology
- **Key Features**: ReflectiveModule, DAG orchestration, PDCA cycles
- **Location**: `src/beast_mode/`

### Hybrid Code Generator
- **Purpose**: DeepSeek + Claude hybrid code generation
- **Cost**: 80% savings vs Claude-only
- **Pattern**: Generate → Review → Refine (max 5 iterations)

### Common Task Types

#### 1. Tests (pytest format)
```python
import pytest
from your_module import YourClass

class TestYourClass:
    """Test suite for YourClass"""

    def test_basic_functionality(self):
        """Test basic operation"""
        obj = YourClass()
        result = obj.method()
        assert result is not None

    def test_error_handling(self):
        """Test error conditions"""
        obj = YourClass()
        with pytest.raises(ValueError):
            obj.method(invalid_param)
```

#### 2. Integration Components
Must integrate with existing Beast Mode infrastructure:
```python
from src.beast_mode.reflective_module import ReflectiveModule
import redis
import logging

class YourIntegration(ReflectiveModule):
    """Integration component"""

    def __init__(self, redis_client: redis.Redis):
        super().__init__()
        self.redis = redis_client
        self.logger = logging.getLogger(__name__)
```

#### 3. GitHub Synchronization
When working with GitHub APIs:
```python
import os
import requests
from typing import Dict, Any

class GitHubClient:
    """GitHub API client"""

    def __init__(self):
        self.token = os.environ.get('GITHUB_TOKEN')
        if not self.token:
            raise ValueError("GITHUB_TOKEN environment variable required")

        self.base_url = "https://api.github.com"
        self.logger = logging.getLogger(__name__)

    def make_request(self, endpoint: str) -> Dict[str, Any]:
        """Make authenticated GitHub API request"""
        headers = {
            'Authorization': f'token {self.token}',
            'Accept': 'application/vnd.github.v3+json'
        }

        try:
            response = requests.get(
                f"{self.base_url}/{endpoint}",
                headers=headers,
                timeout=30
            )
            response.raise_for_status()
            return response.json()

        except requests.RequestException as e:
            self.logger.error(f"GitHub API error: {e}", exc_info=True)
            raise
```

## Security Requirements

### Never Hardcode Credentials
```python
import os

# ✅ CORRECT
api_key = os.environ.get('API_KEY')
if not api_key:
    raise ValueError("API_KEY environment variable required")

# ❌ WRONG
api_key = "sk-1234567890"  # NEVER DO THIS
```

### Input Sanitization
```python
import re
from pathlib import Path

def sanitize_path(user_input: str) -> Path:
    """Prevent path traversal attacks"""
    # Remove dangerous characters
    sanitized = re.sub(r'[^a-zA-Z0-9_\-.]', '', user_input)

    # Validate no path traversal
    if '..' in user_input or user_input.startswith('/'):
        raise ValueError("Invalid path")

    return Path(sanitized)
```

## What Makes Code Production-Ready

### Checklist for Every Task:
- ✅ Comprehensive docstrings (module, class, function)
- ✅ Complete type hints on all parameters and returns
- ✅ Input validation at function entry
- ✅ Specific exception handling (no bare except)
- ✅ Logging with context
- ✅ No `pass` statements or TODOs
- ✅ No hardcoded credentials
- ✅ Security considerations (sanitization, validation)
- ✅ Integration with Beast Mode patterns when applicable
- ✅ Tests if task requires them

## Common Rejection Reasons

1. **"Doesn't meet requirements"** - You generated generic code instead of task-specific implementation
2. **"Incomplete implementation"** - pass statements or TODOs left in code
3. **"Missing docstrings"** - No documentation for classes/functions
4. **"Weak error handling"** - Using bare `except:` or not catching exceptions
5. **"No validation"** - Not checking inputs at function entry
6. **"Security concerns"** - Hardcoded secrets, no input sanitization

## Remember
You don't have access to the full codebase context like Claude does. Focus on:
1. **Read the task description carefully** - implement exactly what's asked
2. **Use the patterns shown above** - they match the project's style
3. **Be complete** - no shortcuts, no placeholders
4. **Validate everything** - inputs, outputs, state
5. **Document everything** - docstrings are mandatory

Your goal: Pass Claude's review in ≤2 iterations by being thorough from the start.
