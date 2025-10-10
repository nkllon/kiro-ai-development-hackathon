# Contributing to Beast Mode AI Development Framework

Thank you for your interest in contributing to the Beast Mode AI Development Framework! This document provides guidelines and instructions for contributing to the project.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [Contributing Guidelines](#contributing-guidelines)
- [Code Standards](#code-standards)
- [Testing Procedures](#testing-procedures)
- [Review Process](#review-process)
- [Issue Guidelines](#issue-guidelines)
- [Pull Request Process](#pull-request-process)
- [Community Guidelines](#community-guidelines)

## Code of Conduct

We are committed to providing a welcoming and inclusive environment for all contributors. Please read and follow our [Code of Conduct](docs/community/CODE_OF_CONDUCT.md).

## Getting Started

### Prerequisites

- Python 3.9 or higher
- Git
- Docker (optional, for containerized development)
- Redis (for execution tracking features)

### Quick Setup

1. Fork the repository
2. Clone your fork:
   ```bash
   git clone https://github.com/YOUR_USERNAME/beast-mode-ai-framework.git
   cd beast-mode-ai-framework
   ```
3. Follow the [Installation Guide](docs/installation/INSTALLATION_GUIDE.md)
4. Run the quick start example to verify your setup

## Development Setup

### Environment Configuration

1. **Create environment file**:
   ```bash
   cp .env.example ~/.env
   ```

2. **Configure credentials** (NEVER hardcode in source):
   ```bash
   # Edit ~/.env with your credentials
   REDIS_PASSWORD=your_redis_password_here
   OPENAI_API_KEY=your_openai_key_here
   # Add other required environment variables
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Verify installation**:
   ```bash
   python -m pytest tests/ --run
   ```

### Development Tools

We use the following tools for development:

- **Code Formatting**: `black` for Python code formatting
- **Linting**: `ruff` for fast Python linting
- **Type Checking**: `mypy` for static type analysis
- **Testing**: `pytest` for unit and integration tests
- **Security**: `bandit` for security vulnerability scanning

Install development tools:
```bash
pip install black ruff mypy pytest bandit
```

## Contributing Guidelines

### Types of Contributions

We welcome the following types of contributions:

1. **Bug Reports**: Help us identify and fix issues
2. **Feature Requests**: Suggest new functionality
3. **Code Contributions**: Submit bug fixes or new features
4. **Documentation**: Improve or add documentation
5. **Examples**: Create working examples and tutorials
6. **Testing**: Add or improve test coverage

### Before You Start

1. **Check existing issues** to avoid duplicate work
2. **Create an issue** for significant changes to discuss approach
3. **Fork the repository** and create a feature branch
4. **Follow our coding standards** and security guidelines

## Code Standards

### Python Code Standards

1. **PEP 8 Compliance**: Follow Python PEP 8 style guidelines
2. **Type Hints**: Use type hints for all function parameters and return values
3. **Docstrings**: Use Google-style docstrings for all public functions and classes
4. **Security**: NEVER hardcode credentials - always use environment variables

#### Example Code Structure

```python
"""Module docstring describing the module's purpose."""

import os
from typing import Optional, Dict, Any
from dataclasses import dataclass, field


@dataclass
class ExampleConfig:
    """Configuration class using environment variables."""
    
    api_key: str = field(default_factory=lambda: os.getenv('API_KEY', ''))
    timeout: int = field(default_factory=lambda: int(os.getenv('TIMEOUT', '30')))
    
    def __post_init__(self):
        if not self.api_key:
            raise ValueError("API_KEY environment variable is required")


def example_function(param: str, optional_param: Optional[int] = None) -> Dict[str, Any]:
    """
    Example function demonstrating our coding standards.
    
    Args:
        param: Description of the parameter
        optional_param: Optional parameter with default value
        
    Returns:
        Dictionary containing the result
        
    Raises:
        ValueError: If param is empty
    """
    if not param:
        raise ValueError("param cannot be empty")
    
    return {
        "param": param,
        "optional_param": optional_param,
        "processed": True
    }
```

### Security Standards

**CRITICAL**: Follow our [Security Credentials Governance](docs/security/SECURITY.md):

1. **NEVER hardcode credentials** in source code
2. **ALWAYS use environment variables** for sensitive data
3. **VALIDATE environment variables** are set before using
4. **PROVIDE helpful error messages** when credentials are missing

### Documentation Standards

1. **Clear and Concise**: Write clear, concise documentation
2. **Code Examples**: Include working code examples
3. **Up-to-Date**: Keep documentation current with code changes
4. **Markdown**: Use proper Markdown formatting

## Testing Procedures

### Running Tests

```bash
# Run all tests
python -m pytest tests/ --run

# Run specific test file
python -m pytest tests/test_example.py --run

# Run with coverage
python -m pytest tests/ --cov=src --run

# Run security tests
bandit -r src/
```

### Test Requirements

1. **Unit Tests**: All new functions must have unit tests
2. **Integration Tests**: Complex features need integration tests
3. **Security Tests**: Validate no hardcoded credentials
4. **Example Tests**: All examples must be tested and working

### Writing Tests

```python
"""Test module following our testing standards."""

import pytest
import os
from unittest.mock import patch, MagicMock

from src.example_module import ExampleClass


class TestExampleClass:
    """Test class for ExampleClass."""
    
    def test_example_function_success(self):
        """Test successful execution of example function."""
        # Arrange
        test_input = "test_value"
        expected_output = {"result": "processed"}
        
        # Act
        result = ExampleClass().example_function(test_input)
        
        # Assert
        assert result == expected_output
    
    def test_example_function_with_missing_env_var(self):
        """Test function behavior when environment variable is missing."""
        with patch.dict(os.environ, {}, clear=True):
            with pytest.raises(ValueError, match="API_KEY environment variable is required"):
                ExampleClass()
    
    @patch('src.example_module.external_service')
    def test_example_function_with_mock(self, mock_service):
        """Test function with mocked external dependency."""
        # Arrange
        mock_service.return_value = MagicMock()
        
        # Act & Assert
        result = ExampleClass().call_external_service()
        assert result is not None
        mock_service.assert_called_once()
```

## Review Process

### Code Review Guidelines

1. **Automated Checks**: All PRs must pass automated checks
2. **Security Review**: All code reviewed for security issues
3. **Functionality Review**: Code must work as intended
4. **Documentation Review**: Changes must be properly documented
5. **Test Coverage**: New code must have appropriate test coverage

### Review Checklist

- [ ] Code follows our style guidelines
- [ ] No hardcoded credentials or sensitive data
- [ ] All functions have type hints and docstrings
- [ ] Tests are included and passing
- [ ] Documentation is updated
- [ ] Security scan passes
- [ ] Examples work correctly

## Issue Guidelines

### Bug Reports

Use the [Bug Report Template](.github/ISSUE_TEMPLATE/bug_report.md) and include:

- Clear description of the issue
- Steps to reproduce
- Expected vs actual behavior
- Environment details
- Error messages or logs

### Feature Requests

Use the [Feature Request Template](.github/ISSUE_TEMPLATE/feature_request.md) and include:

- Clear description of the feature
- Use case and motivation
- Proposed implementation approach
- Potential impact on existing functionality

### Security Issues

For security vulnerabilities:

1. **DO NOT** create a public issue
2. **Email** security@beast-mode-framework.com
3. **Include** detailed description and reproduction steps
4. **Wait** for acknowledgment before public disclosure

## Pull Request Process

### Before Submitting

1. **Create feature branch** from main:
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes** following our standards

3. **Run tests locally**:
   ```bash
   python -m pytest tests/ --run
   black src/ tests/
   ruff check src/ tests/
   mypy src/
   bandit -r src/
   ```

4. **Update documentation** as needed

5. **Commit with clear messages**:
   ```bash
   git commit -m "feat: add new feature for X
   
   - Implement feature Y
   - Add tests for Z
   - Update documentation"
   ```

### Submitting Pull Request

1. **Push to your fork**:
   ```bash
   git push origin feature/your-feature-name
   ```

2. **Create pull request** with:
   - Clear title and description
   - Reference to related issues
   - List of changes made
   - Testing performed

3. **Respond to feedback** promptly and professionally

### Pull Request Template

```markdown
## Description
Brief description of changes made.

## Related Issues
Fixes #123
Relates to #456

## Changes Made
- [ ] Feature A implemented
- [ ] Tests added for B
- [ ] Documentation updated for C

## Testing
- [ ] Unit tests pass
- [ ] Integration tests pass
- [ ] Manual testing completed
- [ ] Security scan passes

## Checklist
- [ ] Code follows style guidelines
- [ ] No hardcoded credentials
- [ ] Documentation updated
- [ ] Tests included
```

## Community Guidelines

### Communication

- **Be respectful** and professional in all interactions
- **Be constructive** when providing feedback
- **Be patient** with new contributors
- **Be inclusive** and welcoming to all backgrounds

### Getting Help

- **GitHub Issues**: For bugs and feature requests
- **Discussions**: For questions and general discussion
- **Documentation**: Check existing docs first
- **Examples**: Look at working examples for guidance

### Recognition

We recognize contributors through:

- **Contributors file**: All contributors listed
- **Release notes**: Significant contributions highlighted
- **Community highlights**: Regular contributor spotlights

## Development Workflow

### Branching Strategy

- **main**: Production-ready code
- **develop**: Integration branch for features
- **feature/***: Individual feature branches
- **hotfix/***: Critical bug fixes
- **release/***: Release preparation branches

### Commit Message Format

```
type(scope): short description

Longer description if needed

- Bullet point 1
- Bullet point 2

Fixes #123
```

Types: `feat`, `fix`, `docs`, `style`, `refactor`, `test`, `chore`

## Resources

### Documentation
- [Installation Guide](docs/installation/INSTALLATION_GUIDE.md)
- [API Documentation](docs/api/README.md)
- [Examples](examples/README.md)
- [Security Guidelines](docs/security/SECURITY.md)
- [Architecture Overview](docs/architecture/README.md)

### Community Resources
- [Development Setup Guide](docs/community/DEVELOPMENT_SETUP.md)
- [Testing Procedures](docs/community/TESTING_PROCEDURES.md)
- [Code Review Process](docs/community/CODE_REVIEW_PROCESS.md)
- [Community Guidelines](docs/community/COMMUNITY_GUIDELINES.md)
- [FAQ](docs/community/FAQ.md)

## Questions?

If you have questions about contributing:

1. Check the [FAQ](docs/community/FAQ.md)
2. Search existing [GitHub Issues](https://github.com/beast-mode-ai-framework/issues)
3. Create a new [Discussion](https://github.com/beast-mode-ai-framework/discussions)
4. Contact the maintainers

Thank you for contributing to the Beast Mode AI Development Framework!