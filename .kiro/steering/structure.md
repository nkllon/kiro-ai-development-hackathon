---
inclusion: always
---

# Project Structure & Organization

## File Placement Rules

### Root Directory Structure
```
kiro-ai-development-hackathon/
├── .kiro/                      # REQUIRED: Kiro configuration (NOT in .gitignore)
│   ├── specs/                  # Feature specifications
│   ├── hooks/                  # Agent automation hooks
│   └── steering/               # AI assistant guidance rules
├── src/                        # All source code
├── tests/                      # Test suite (mirrors src/ structure)
├── scripts/                    # Utility and automation scripts
├── docs/                       # Documentation
├── examples/                   # Usage examples and demos
├── assessment_results/         # Beast Mode assessment outputs
└── metrics_data/               # Performance metrics
```

### Source Code Organization (`src/`)

**Beast Mode Framework** (`src/beast_mode/`):
- `analysis/` - RCA engines and failure analysis
- `assessment/` - Production readiness evaluation
- `autonomous/` - Self-managing components
- `cli/` - Command-line interfaces
- `core/` - PDCA orchestrator and base classes
- `execution/` - Task execution engines
- `ghostbusters/` - AI agent framework
- `orchestration/` - Tool and workflow coordination
- `quality/` - Automated quality gates
- `testing/` - Test framework and validation

**Spec Reconciliation** (`src/spec_reconciliation/`):
- Specification validation and governance
- Cross-spec consistency checking
- Requirements traceability

## Code Organization Standards

### File Placement Rules
- **Source code**: Always in `src/` with appropriate subdirectory
- **Tests**: Mirror `src/` structure in `tests/` (e.g., `src/beast_mode/core/` → `tests/unit/beast_mode/core/`)
- **Scripts**: Utility scripts in `scripts/`, not scattered in root
- **Documentation**: Technical docs in `docs/`, not mixed with code
- **Examples**: Working examples in `examples/`, not inline in source

### Naming Conventions
- **Python modules**: `snake_case.py`
- **Classes**: `PascalCase` (e.g., `ReflectiveModule`)
- **Functions/methods**: `snake_case`
- **Constants**: `UPPER_SNAKE_CASE`
- **Directories**: `snake_case` or `kebab-case` for multi-word

### Module Structure
Every Python module should follow this pattern:
```python
"""Module docstring describing purpose and usage."""

import os
import sys
from typing import Dict, List, Optional, Any

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

### Reflective Module Pattern
All major components must inherit from `ReflectiveModule`:
- Implement health monitoring endpoints (`/health`, `/ready`, `/metrics`)
- Provide status reporting capabilities
- Support systematic debugging and analysis
- Include structured logging with correlation IDs

### Systematic Organization
- **No ad-hoc placement**: Every file has a designated location
- **Consistent patterns**: Follow established naming and structure
- **Model-driven**: Consult project registry for architectural decisions
- **Separation of concerns**: Clear boundaries between components

### Testing Requirements
- **Test coverage**: >90% for all new code
- **Test structure**: Mirror source structure in `tests/` (e.g., `src/beast_mode/core/` → `tests/unit/beast_mode/core/`)
- **Test types**: Unit (`tests/unit/`), integration (`tests/integration/`)
- **Fixtures**: Shared test data in `tests/fixtures/`
- **Mocking**: Use `unittest.mock` for external dependencies
- **Parametrized tests**: Use `pytest.mark.parametrize` for multiple scenarios

## Specifications Structure (`.kiro/specs/`)

Each specification follows this structure:
```
spec-name/
├── requirements.md    # Functional and non-functional requirements
├── design.md         # Architecture and design decisions
└── tasks.md          # Implementation tasks and dependencies
```

## Critical Requirements

### Kiro Integration
- `.kiro/` directory MUST be at project root
- `.kiro/` MUST NOT be in `.gitignore` (hackathon requirement)
- All steering rules in `.kiro/steering/` guide AI behavior

### Beast Mode Compliance
- All modules inherit from `ReflectiveModule`
- Use systematic approaches, never ad-hoc solutions
- Apply PDCA methodology to all development tasks
- Make model-driven decisions using project registry

### Quality Gates
- All code must pass existing test suite
- New features require corresponding tests
- Documentation must be updated with code changes
- Health endpoints required for all services