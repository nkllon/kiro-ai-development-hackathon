# Contributing to Beast Mode Framework

Welcome to the Beast Mode Framework! We're thrilled that you want to contribute to our AI-Powered Spec-Driven Development Framework. This guide will help you get started.

## 📋 Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [Framework Architecture](#framework-architecture)
- [Contributing Guidelines](#contributing-guidelines)
- [Pull Request Process](#pull-request-process)
- [Testing Requirements](#testing-requirements)
- [Documentation](#documentation)

## Code of Conduct

This project and everyone participating in it is governed by our [Code of Conduct](CODE_OF_CONDUCT.md). By participating, you are expected to uphold this code.

## Getting Started

### Prerequisites

- Python 3.9 or higher
- Git
- Docker (for MCP service development)
- Make (for build automation)

### Development Setup

1. **Fork and Clone**
   ```bash
   git clone https://github.com/your-username/kiro-ai-development-hackathon.git
   cd kiro-ai-development-hackathon
   ```

2. **Set up Python Environment**
   ```bash
   make venv          # Create virtual environment
   make install       # Install dependencies
   ```

3. **Verify Installation**
   ```bash
   make quality       # Run linting, type checking, and tests
   beast-mode --help  # Test CLI
   ```

4. **Run Tests**
   ```bash
   make test          # Run all tests
   make test-unit     # Run unit tests only
   make test-integration  # Run integration tests only
   ```

## Framework Architecture

Beast Mode Framework follows **Reflective Module (RM) Architecture** with these key principles:

### Core Components

- **`src/beast_mode/`** - Main framework implementation
  - `analysis/` - Root Cause Analysis and safety analysis
  - `api/` - REST API endpoints
  - `autonomous/` - PDCA orchestration and autonomous agents
  - `backlog/` - Task and dependency management
  - `cli/` - Command-line interface

- **`.kiro/specs/`** - Feature specifications with requirements, design, and tasks
- **Docker services** - MCP integrations for external services

### Development Patterns

- **PDCA-Driven Development**: All features follow Plan-Do-Check-Act cycles
- **Spec-Driven Development**: Features defined through comprehensive specifications
- **Reflective Modules**: Components decomposed into focused, single-responsibility modules

## Contributing Guidelines

### Types of Contributions

We welcome several types of contributions:

- 🐛 **Bug fixes**
- ✨ **New features**
- 📝 **Documentation improvements**
- 🧪 **Test coverage improvements**
- 🏗️ **Infrastructure improvements**
- 🔧 **Tool and CI/CD enhancements**

### Contribution Process

1. **Check Existing Issues**
   - Search for existing issues before creating new ones
   - Comment on issues you'd like to work on

2. **Create Feature Specifications**
   - For new features, create specs in `.kiro/specs/[feature-name]/`
   - Include: `requirements.md`, `design.md`, `tasks.md`
   - Follow RM principles - avoid monolithic specifications

3. **Branch Naming Convention**
   ```
   feat/feature-name        # New features
   fix/bug-description      # Bug fixes
   docs/improvement-area    # Documentation
   refactor/component-name  # Refactoring
   ```

4. **Commit Message Format**
   ```
   type(scope): brief description

   Detailed explanation if needed

   - Additional context
   - References to issues: fixes #123
   ```

### Code Style Requirements

- **Python**: Follow PEP 8, use Black formatter (line length: 88)
- **Type Hints**: Required for all functions and methods
- **Documentation**: Docstrings for all public APIs
- **Testing**: Unit tests required for new functionality

### Quality Gates

All contributions must pass:

```bash
make quality  # Runs all quality checks:
# - Black formatting
# - Ruff linting
# - MyPy type checking
# - Pytest test suite
```

## Pull Request Process

### Before Submitting

1. **Ensure Quality Gates Pass**
   ```bash
   make quality
   make coverage  # Ensure test coverage
   ```

2. **Update Documentation**
   - Update docstrings
   - Update README if needed
   - Add/update specification files

3. **Test Thoroughly**
   ```bash
   make test              # Full test suite
   beast-mode --help      # Test CLI functionality
   kiro-discovery --help  # Test discovery tools
   ```

### PR Template

When creating a pull request:

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Documentation update
- [ ] Refactoring
- [ ] Performance improvement

## Testing
- [ ] Unit tests pass
- [ ] Integration tests pass
- [ ] Manual testing completed
- [ ] Quality gates pass

## Checklist
- [ ] Code follows project style guidelines
- [ ] Self-review completed
- [ ] Documentation updated
- [ ] Tests added/updated
- [ ] Specifications updated (if applicable)
```

### Review Process

1. **Automated Checks**: CI pipeline must pass
2. **Code Review**: Maintainer review required
3. **Testing**: Functionality verified
4. **Documentation**: Completeness checked

## Testing Requirements

### Test Categories

- **Unit Tests** (`tests/unit/`): Test individual components
- **Integration Tests** (`tests/integration/`): Test component interactions
- **Slow Tests** (`@pytest.mark.slow`): Long-running tests

### Test Guidelines

```python
# Use pytest markers
@pytest.mark.unit
def test_component_function():
    """Test individual component functionality."""
    pass

@pytest.mark.integration
def test_component_integration():
    """Test component interactions."""
    pass

@pytest.mark.slow
def test_long_running_process():
    """Test that takes significant time."""
    pass
```

### Coverage Requirements

- **Minimum Coverage**: 80% for new code
- **Critical Paths**: 95% coverage required
- **Documentation**: All public APIs must have docstrings

## Documentation

### Documentation Types

- **API Documentation**: Docstrings in code
- **User Guides**: In `docs/` directory
- **Specifications**: In `.kiro/specs/`
- **Architecture**: In `CLAUDE.md` and `docs/`

### Documentation Standards

- Use **Google-style docstrings**
- Include **examples** in docstrings
- Keep **README.md** updated
- Update **specifications** when changing functionality

## Development Commands Reference

```bash
# Setup and Installation
make venv                 # Create virtual environment
make install             # Install dependencies
make clean               # Clean build artifacts

# Quality Assurance
make lint                # Run linting (Ruff)
make format              # Format code (Black)
make mypy                # Type checking
make quality             # All quality checks
make coverage            # Test coverage report

# Testing
make test                # Run all tests
make test-unit          # Unit tests only
make test-integration   # Integration tests only
make test-slow          # Slow tests only

# Beast Mode Framework
make beast-mode-help    # Framework help
make beast-mode-status  # System status
make pdca-cycle         # Execute PDCA cycle
```

## Getting Help

- **Documentation**: Check existing docs first
- **Issues**: Search GitHub issues
- **Discussions**: Use GitHub Discussions for questions
- **Community**: Join our community channels

## Recognition

Contributors are recognized through:

- **Contributors list** in README.md
- **Release notes** mention significant contributions
- **Community recognition** for ongoing contributions

Thank you for contributing to Beast Mode Framework! 🚀

---

For questions about this guide, please open an issue or start a discussion.