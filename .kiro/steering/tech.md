---
inclusion: always
---

# Technology Standards & Architecture Policy

## Primary Technology Stack

**Language**: Python 3.9+ (systematic choice for AI/ML ecosystem compatibility)
**Framework**: Beast Mode Framework with Reflective Module pattern
**Quality Gate**: >90% test coverage (DR8 compliance)
**Philosophy**: Systematic over ad-hoc, proven over experimental

## Code Style & Standards

### Python Conventions
- **Imports**: Standard library → third-party → local imports (separated by blank lines)
- **Naming**: `snake_case` for functions/variables, `PascalCase` for classes, `UPPER_SNAKE_CASE` for constants
- **Docstrings**: Required for all public functions/classes using Google style
- **Type hints**: Required for all function signatures and class attributes
- **Line length**: 88 characters (Black formatter standard)

### Module Structure Template
```python
"""Module docstring describing purpose and usage."""

import os
import sys
from typing import Dict, List, Optional

import requests
from pydantic import BaseModel

from beast_mode.core import ReflectiveModule
from src.utils import helper_function

# Constants
DEFAULT_TIMEOUT = 30
MAX_RETRIES = 3

class ComponentName(ReflectiveModule):
    """Component implementing systematic functionality."""
    
    def __init__(self, config: Dict[str, Any]) -> None:
        super().__init__()
        self._config = config
```

## Architecture Patterns

### Reflective Module Pattern (MANDATORY)
All components must inherit from `ReflectiveModule` and implement:
- `health()` → Dict[str, Any]: System health status
- `ready()` → bool: Readiness for traffic
- `metrics()` → Dict[str, float]: Performance metrics
- `status()` → str: Current operational state

### Error Handling Standards
- **Explicit exceptions**: Define custom exception classes for domain errors
- **Structured logging**: Use correlation IDs and structured data
- **Graceful degradation**: Partial functionality during failures
- **Circuit breakers**: For external service calls
- **Retry logic**: Exponential backoff with jitter

### Testing Requirements
- **Unit tests**: >90% coverage, fast execution (<1s per test)
- **Integration tests**: Real dependencies, slower execution acceptable
- **Fixtures**: Shared test data in `tests/fixtures/`
- **Mocking**: Use `unittest.mock` for external dependencies
- **Parametrized tests**: Use `pytest.mark.parametrize` for multiple scenarios

## Implementation Guidelines

### Decision Framework
1. **Consult specifications**: Check `.kiro/specs/` before implementing
2. **Use systematic patterns**: Leverage `src/beast_mode/` framework
3. **Apply PDCA cycles**: Plan-Do-Check-Act for all development tasks
4. **Physics-informed design**: Consider real-world constraints and failure modes
5. **Model-driven decisions**: Base architectural choices on project registry

### Service Integration
- **Health endpoints**: `/health`, `/ready`, `/metrics` required for all services
- **Observability**: Structured logging with correlation IDs and request tracing
- **Configuration**: Environment variables, no hardcoded secrets
- **API design**: RESTful with OpenAPI specifications
- **Versioning**: Semantic versioning (MAJOR.MINOR.PATCH)

### Performance Standards
- **Response times**: <100ms for health checks, <1s for API calls
- **Memory usage**: Monitor and set limits for all components
- **Database queries**: Use connection pooling, implement query timeouts
- **Caching**: Implement with explicit TTL and invalidation strategies
- **Async operations**: Use `asyncio` for I/O-bound operations

## Quality Gates

### Pre-commit Requirements
- [ ] All tests pass (`pytest`)
- [ ] Code coverage >90% (`coverage report`)
- [ ] Type checking passes (`mypy`)
- [ ] Code formatting applied (`black`, `isort`)
- [ ] Linting passes (`flake8`, `pylint`)
- [ ] Security scan clean (`bandit`)

### Code Review Checklist
- [ ] Follows Reflective Module pattern
- [ ] Implements proper error handling
- [ ] Includes comprehensive tests
- [ ] Documents public interfaces
- [ ] Considers failure scenarios
- [ ] Uses systematic patterns from Beast Mode framework

## Critical Rules for AI Assistants

### ALWAYS Do
- Inherit from `ReflectiveModule` for all major components
- Implement health monitoring endpoints
- Use systematic approaches from `src/beast_mode/` framework
- Apply PDCA methodology to development tasks
- Include comprehensive error handling and logging
- Write tests that achieve >90% coverage
- Follow the established project structure in `src/`

### TERMINAL COMMANDS - CRITICAL SAFETY RULES
- **ALWAYS** pipe commands that might have long output to `tee filename` 
- **ALWAYS** use `| head -20` or `| tail -20` for commands that might produce long output
- **NEVER** run `git log` without `| head -20` or `| tee logfile.txt`
- **NEVER** run commands that create interactive prompts (like `more`, `less`, colons for pagination)
- **NEVER** run the same failing command repeatedly - try a different approach
- **ALWAYS** use proper ZSH piping techniques to avoid hanging terminals
- **EXAMPLE SAFE COMMANDS**:
  - `git log --oneline | head -20`
  - `git show commit:file | tee recovered_file.ext`
  - `command_with_output | tee output.log`
- **FORBIDDEN COMMANDS** (will hang terminal):
  - `git log` (without piping)
  - `cat large_file` (without piping)
  - Any command that creates `:` prompts

### NEVER Do
- Create ad-hoc solutions without systematic foundation
- Hardcode configuration values or secrets
- Skip error handling or assume happy path
- Implement without consulting existing patterns
- Place source code outside of `src/` directory
- Create components without health monitoring capabilities
- **NEVER EVER** run terminal commands that can hang or create interactive prompts
- **NEVER EVER** leave the user to deal with hung terminal sessions