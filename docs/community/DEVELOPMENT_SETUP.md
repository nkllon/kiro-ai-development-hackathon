# Development Setup Guide

This guide provides detailed instructions for setting up a development environment for the Beast Mode AI Development Framework.

## Prerequisites

### System Requirements

**Minimum Requirements:**
- Python 3.9 or higher
- Git 2.20 or higher
- 4GB RAM
- 2GB disk space

**Recommended Requirements:**
- Python 3.11 or higher
- Git 2.30 or higher
- 8GB RAM
- 10GB disk space
- Docker 20.10 or higher
- Redis 6.0 or higher

### Required Software

1. **Python**: Install from [python.org](https://python.org) or use your system package manager
2. **Git**: Install from [git-scm.com](https://git-scm.com) or use your system package manager
3. **Redis**: Install locally or use a cloud service
4. **Docker** (optional): For containerized development

## Development Environment Setup

### 1. Fork and Clone Repository

```bash
# Fork the repository on GitHub first, then clone your fork
git clone https://github.com/YOUR_USERNAME/beast-mode-ai-framework.git
cd beast-mode-ai-framework

# Add upstream remote
git remote add upstream https://github.com/beast-mode-ai-framework/beast-mode.git
```

### 2. Create Virtual Environment

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate
# On Windows:
venv\Scripts\activate
```

### 3. Install Dependencies

```bash
# Install production dependencies
pip install -r requirements.txt

# Install development dependencies
pip install -r requirements-dev.txt

# Install the package in development mode
pip install -e .
```

### 4. Configure Environment Variables

```bash
# Copy example environment file
cp .env.example ~/.env

# Edit ~/.env with your configuration
# NEVER commit this file to version control
```

**Required Environment Variables:**
```bash
# ~/.env
REDIS_PASSWORD=your_redis_password_here
REDIS_HOST=localhost
REDIS_PORT=6379

# Optional API keys for full functionality
OPENAI_API_KEY=your_openai_key_here
ANTHROPIC_API_KEY=your_anthropic_key_here

# Development settings
ENVIRONMENT=development
DEBUG=true
LOG_LEVEL=DEBUG
```

### 5. Set Up Redis

**Option A: Local Redis Installation**
```bash
# macOS with Homebrew
brew install redis
brew services start redis

# Ubuntu/Debian
sudo apt update
sudo apt install redis-server
sudo systemctl start redis-server

# Set password in Redis
redis-cli
> CONFIG SET requirepass your_redis_password_here
> AUTH your_redis_password_here
> exit
```

**Option B: Docker Redis**
```bash
# Run Redis in Docker
docker run -d \
  --name beast-mode-redis \
  -p 6379:6379 \
  redis:7-alpine \
  redis-server --requirepass your_redis_password_here
```

**Option C: Cloud Redis**
Use a cloud Redis service like:
- Redis Cloud
- AWS ElastiCache
- Google Cloud Memorystore
- Azure Cache for Redis

### 6. Verify Installation

```bash
# Run basic health check
python examples/health_check/basic_check.py

# Run quick start example
python examples/quick_start/basic_example.py

# Run test suite
python -m pytest tests/ --run
```

## Development Tools Setup

### Code Quality Tools

```bash
# Install pre-commit hooks
pip install pre-commit
pre-commit install

# Run code formatting
black src/ tests/ examples/
ruff check src/ tests/ examples/ --fix

# Run type checking
mypy src/

# Run security scanning
bandit -r src/
```

### IDE Configuration

**VS Code Setup:**
1. Install Python extension
2. Install recommended extensions:
   - Python
   - Pylance
   - Black Formatter
   - Ruff
   - GitLens

**VS Code Settings (.vscode/settings.json):**
```json
{
    "python.defaultInterpreterPath": "./venv/bin/python",
    "python.formatting.provider": "black",
    "python.linting.enabled": true,
    "python.linting.ruffEnabled": true,
    "python.linting.mypyEnabled": true,
    "python.testing.pytestEnabled": true,
    "python.testing.pytestArgs": ["tests/"],
    "files.exclude": {
        "**/__pycache__": true,
        "**/.pytest_cache": true,
        "**/.mypy_cache": true,
        "**/.ruff_cache": true
    }
}
```

**PyCharm Setup:**
1. Open project in PyCharm
2. Configure Python interpreter to use virtual environment
3. Enable code inspections for Python
4. Configure code style to use Black
5. Set up run configurations for tests

### Git Configuration

```bash
# Configure Git (if not already done)
git config --global user.name "Your Name"
git config --global user.email "your.email@example.com"

# Set up Git hooks
cp scripts/git-hooks/pre-commit .git/hooks/
chmod +x .git/hooks/pre-commit
```

## Development Workflow

### Branch Management

```bash
# Create feature branch
git checkout -b feature/your-feature-name

# Keep your fork updated
git fetch upstream
git checkout main
git merge upstream/main
git push origin main
```

### Code Development

1. **Write Code**: Follow our [coding standards](../CONTRIBUTING.md#code-standards)
2. **Add Tests**: Write comprehensive tests for new functionality
3. **Update Documentation**: Keep documentation current
4. **Run Quality Checks**: Ensure all checks pass

```bash
# Development cycle
black src/ tests/
ruff check src/ tests/ --fix
mypy src/
python -m pytest tests/ --run
```

### Testing

```bash
# Run all tests
python -m pytest tests/ --run

# Run specific test file
python -m pytest tests/test_memory_palace.py --run

# Run with coverage
python -m pytest tests/ --cov=src --cov-report=html --run

# Run integration tests
python -m pytest tests/integration/ --run

# Run security tests
bandit -r src/
```

### Documentation

```bash
# Build documentation locally
cd docs/
python -m http.server 8000

# Check documentation links
python scripts/check_documentation_links.py

# Generate API documentation
python scripts/generate_api_docs.py
```

## Troubleshooting

### Common Issues

**Issue: Import errors when running examples**
```bash
# Solution: Install package in development mode
pip install -e .
```

**Issue: Redis connection errors**
```bash
# Check Redis is running
redis-cli ping

# Check Redis authentication
redis-cli -a your_password ping

# Verify environment variables
python -c "import os; print(os.getenv('REDIS_PASSWORD'))"
```

**Issue: Test failures**
```bash
# Run tests with verbose output
python -m pytest tests/ -v --run

# Run specific failing test
python -m pytest tests/test_specific.py::test_function -v --run

# Check test dependencies
pip install -r requirements-dev.txt
```

**Issue: Code quality checks failing**
```bash
# Fix formatting issues
black src/ tests/

# Fix linting issues
ruff check src/ tests/ --fix

# Check type issues
mypy src/ --show-error-codes
```

### Environment Issues

**Python Version Issues:**
```bash
# Check Python version
python --version

# Use specific Python version
python3.11 -m venv venv
```

**Virtual Environment Issues:**
```bash
# Recreate virtual environment
rm -rf venv/
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

**Dependency Issues:**
```bash
# Update pip
pip install --upgrade pip

# Clear pip cache
pip cache purge

# Reinstall dependencies
pip uninstall -r requirements.txt -y
pip install -r requirements.txt
```

## Advanced Development Setup

### Docker Development Environment

```bash
# Build development container
docker build -f Dockerfile.dev -t beast-mode-dev .

# Run development container
docker run -it \
  -v $(pwd):/workspace \
  -p 8000:8000 \
  -p 6379:6379 \
  beast-mode-dev
```

### Multi-Python Testing

```bash
# Install pyenv for multiple Python versions
curl https://pyenv.run | bash

# Install multiple Python versions
pyenv install 3.9.18
pyenv install 3.10.13
pyenv install 3.11.6

# Test with tox
pip install tox
tox
```

### Performance Profiling

```bash
# Install profiling tools
pip install py-spy memory-profiler line-profiler

# Profile CPU usage
py-spy record -o profile.svg -- python your_script.py

# Profile memory usage
mprof run your_script.py
mprof plot
```

## Contributing Workflow

### Before Making Changes

1. **Check existing issues** to avoid duplicate work
2. **Create an issue** for significant changes
3. **Discuss approach** with maintainers if needed

### Making Changes

1. **Create feature branch** from main
2. **Make changes** following coding standards
3. **Add tests** for new functionality
4. **Update documentation** as needed
5. **Run quality checks** locally

### Submitting Changes

1. **Push to your fork**
2. **Create pull request** with clear description
3. **Respond to feedback** promptly
4. **Update PR** based on review comments

## Getting Help

### Documentation Resources

- [Contributing Guide](../../CONTRIBUTING.md)
- [API Documentation](../api/README.md)
- [Examples](../../examples/README.md)
- [FAQ](FAQ.md)

### Community Support

- **GitHub Issues**: For bugs and feature requests
- **GitHub Discussions**: For questions and general discussion
- **Code Reviews**: Learn from pull request feedback

### Maintainer Contact

For urgent development questions:
- Create a GitHub Discussion
- Tag relevant maintainers in issues
- Email dev@beast-mode-framework.com for private matters

---

**Happy coding!** Welcome to the Beast Mode AI Development Framework community!