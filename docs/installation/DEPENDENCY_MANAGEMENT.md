# 📦 Beast Mode AI Framework - Dependency Management Guide

> **Comprehensive guide to managing dependencies, virtual environments, and package versions for Beast Mode**

This guide covers everything you need to know about managing dependencies in Beast Mode AI Framework, from basic installation to advanced dependency resolution and security practices.

---

## 📋 Overview

Beast Mode uses a carefully curated set of dependencies to provide:
- **Core Framework**: Essential components for systematic AI development
- **AI/ML Libraries**: Machine learning and data processing capabilities
- **Web Framework**: API and web interface components
- **Monitoring**: Observability and health monitoring tools
- **Development Tools**: Testing, linting, and quality assurance

---

## 🎯 Quick Dependency Setup

### Standard Installation
```bash
# Install all dependencies
pip install -r requirements.txt

# Verify installation
pip list | grep -E "(pydantic|typer|rich|fastapi)"
```

### Development Installation
```bash
# Install with development dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Or install in development mode
pip install -e .
```

---

## 📦 Core Dependencies

### Framework Dependencies

| Package | Version | Purpose | Required |
|---------|---------|---------|----------|
| **pydantic** | 2.11.10+ | Data validation and settings | ✅ Yes |
| **typer** | 0.19.2+ | CLI framework | ✅ Yes |
| **rich** | 14.1.0+ | Rich text and formatting | ✅ Yes |
| **click** | 8.1.8+ | Command line interface | ✅ Yes |
| **fastapi** | 0.118.0+ | Web framework | ✅ Yes |
| **uvicorn** | 0.37.0+ | ASGI server | ✅ Yes |

### AI/ML Dependencies

| Package | Version | Purpose | Required |
|---------|---------|---------|----------|
| **transformers** | 4.57.0+ | Transformer models | ✅ Yes |
| **torch** | 2.8.0+ | Deep learning framework | ✅ Yes |
| **scikit-learn** | 1.6.1+ | Machine learning library | ✅ Yes |
| **numpy** | 2.0.2+ | Numerical computing | ✅ Yes |
| **pandas** | 2.3.3+ | Data manipulation | ⚠️ Optional |
| **datasets** | 4.1.1+ | Dataset loading | ⚠️ Optional |

### Infrastructure Dependencies

| Package | Version | Purpose | Required |
|---------|---------|---------|----------|
| **redis** | 6.4.0+ | In-memory data store | ⚠️ Optional* |
| **prometheus-client** | 0.23.1+ | Metrics collection | ✅ Yes |
| **psutil** | 7.1.0+ | System monitoring | ✅ Yes |
| **cryptography** | 46.0.2+ | Security and encryption | ✅ Yes |
| **requests** | 2.32.5+ | HTTP client | ✅ Yes |

*Required for AI Memory Palace functionality

### Development Dependencies

| Package | Version | Purpose | Required |
|---------|---------|---------|----------|
| **pytest** | 8.4.2+ | Testing framework | 🔧 Dev only |
| **pytest-cov** | 7.0.0+ | Coverage reporting | 🔧 Dev only |
| **black** | 23.0.0+ | Code formatting | 🔧 Dev only |
| **ruff** | 0.1.0+ | Linting | 🔧 Dev only |
| **mypy** | 1.0.0+ | Type checking | 🔧 Dev only |

---

## 🔧 Virtual Environment Management

### Why Use Virtual Environments?

Virtual environments provide:
- **Isolation**: Separate dependencies for different projects
- **Reproducibility**: Consistent environments across machines
- **Security**: Avoid conflicts with system packages
- **Flexibility**: Easy to recreate or modify environments

### Creating Virtual Environments

#### Using venv (Recommended)
```bash
# Create virtual environment
python -m venv .venv

# Activate virtual environment
# Linux/macOS:
source .venv/bin/activate
# Windows:
.venv\Scripts\activate

# Verify activation
which python  # Should show .venv/bin/python
which pip     # Should show .venv/bin/pip

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt
```

#### Using conda
```bash
# Create conda environment
conda create -n beast-mode python=3.11

# Activate environment
conda activate beast-mode

# Install dependencies
pip install -r requirements.txt
```

#### Using pyenv + virtualenv
```bash
# Install specific Python version
pyenv install 3.11.5

# Create virtual environment
pyenv virtualenv 3.11.5 beast-mode

# Activate environment
pyenv activate beast-mode

# Install dependencies
pip install -r requirements.txt
```

### Managing Virtual Environments

#### Activation and Deactivation
```bash
# Activate virtual environment
source .venv/bin/activate

# Check if activated
echo $VIRTUAL_ENV

# Deactivate when done
deactivate
```

#### Recreating Virtual Environments
```bash
# Remove existing environment
rm -rf .venv

# Create new environment
python -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt
```

---

## 📋 Requirements Files

### requirements.txt Structure

Beast Mode uses a structured approach to requirements:

```bash
# Core requirements.txt (auto-generated)
# This file is auto-generated from pyproject.toml by scripts/generate_requirements.py
# DO NOT EDIT MANUALLY - Run 'make requirements' to regenerate

# Core Framework
pydantic>=2.11.10
typer>=0.19.2
rich>=14.1.0
click>=8.1.8

# Web Framework
fastapi>=0.118.0
uvicorn>=0.37.0

# AI/ML Libraries
transformers>=4.57.0
torch>=2.8.0
scikit-learn>=1.6.1
numpy>=2.0.2

# Infrastructure
redis>=6.4.0
prometheus-client>=0.23.1
psutil>=7.1.0
cryptography>=46.0.2
requests>=2.32.5

# Testing
pytest>=8.4.2
pytest-cov>=7.0.0
coverage>=7.10.7
```

### Optional Requirements Files

#### requirements-dev.txt
```bash
# Development dependencies
black>=23.0.0
ruff>=0.1.0
mypy>=1.0.0
pre-commit>=3.0.0
jupyter>=1.0.0
notebook>=6.0.0
```

#### requirements-ml.txt
```bash
# Extended ML dependencies
tensorboard>=2.13.0
wandb>=0.15.0
matplotlib>=3.5.0
seaborn>=0.11.0
plotly>=5.0.0
```

#### requirements-monitoring.txt
```bash
# Monitoring and observability
grafana-client>=3.0.0
influxdb-client>=1.36.0
jaeger-client>=4.8.0
```

### Generating Requirements

```bash
# Generate requirements from pyproject.toml
python scripts/generate_requirements.py

# Update requirements with latest versions
pip-compile requirements.in

# Upgrade all dependencies
pip-compile --upgrade requirements.in
```

---

## 🔄 Dependency Updates

### Checking for Updates

```bash
# Check outdated packages
pip list --outdated

# Check specific package
pip show pydantic

# Check security vulnerabilities
pip-audit
```

### Updating Dependencies

#### Safe Updates (Patch Versions)
```bash
# Update to latest patch versions
pip install --upgrade pydantic typer rich

# Update all packages (be careful!)
pip install --upgrade -r requirements.txt
```

#### Major Version Updates
```bash
# Update specific package to new major version
pip install "pydantic>=3.0.0"

# Test compatibility
python -m pytest tests/

# Update requirements file
pip freeze > requirements.txt
```

### Automated Dependency Management

#### Using Dependabot (GitHub)
```yaml
# .github/dependabot.yml
version: 2
updates:
  - package-ecosystem: "pip"
    directory: "/"
    schedule:
      interval: "weekly"
    open-pull-requests-limit: 10
    reviewers:
      - "maintainer-team"
```

#### Using pip-tools
```bash
# Install pip-tools
pip install pip-tools

# Create requirements.in file
cat > requirements.in << 'EOF'
pydantic>=2.0.0
typer>=0.9.0
rich>=13.0.0
fastapi>=0.100.0
EOF

# Generate locked requirements.txt
pip-compile requirements.in

# Update dependencies
pip-compile --upgrade requirements.in
```

---

## 🔒 Security Best Practices

### Dependency Security

#### Scanning for Vulnerabilities
```bash
# Install security scanner
pip install pip-audit

# Scan for vulnerabilities
pip-audit

# Scan specific requirements file
pip-audit -r requirements.txt

# Generate security report
pip-audit --format=json --output=security-report.json
```

#### Pinning Dependencies
```bash
# Pin exact versions for production
pip freeze > requirements-lock.txt

# Use pinned versions
pip install -r requirements-lock.txt
```

### Trusted Sources

#### Configure Trusted PyPI Mirrors
```bash
# Use trusted PyPI mirrors
pip install --trusted-host pypi.org --trusted-host pypi.python.org --trusted-host files.pythonhosted.org -r requirements.txt

# Configure in pip.conf
mkdir -p ~/.pip
cat > ~/.pip/pip.conf << 'EOF'
[global]
trusted-host = pypi.org
               pypi.python.org
               files.pythonhosted.org
index-url = https://pypi.org/simple/
EOF
```

#### Verify Package Integrity
```bash
# Install with hash verification
pip install --require-hashes -r requirements.txt

# Generate hashes
pip-compile --generate-hashes requirements.in
```

---

## 🚨 Troubleshooting Dependencies

### Common Dependency Issues

#### Issue 1: Conflicting Dependencies
```bash
# Check dependency conflicts
pip check

# Show dependency tree
pip install pipdeptree
pipdeptree

# Resolve conflicts
pip install --force-reinstall package_name
```

#### Issue 2: Build Failures
```bash
# Install build dependencies
pip install --upgrade setuptools wheel

# Install with verbose output
pip install -v package_name

# Use pre-compiled wheels
pip install --only-binary=all package_name
```

#### Issue 3: Version Conflicts
```bash
# Show installed versions
pip list | grep package_name

# Install specific version
pip install "package_name==1.2.3"

# Allow pre-release versions
pip install --pre package_name
```

### Platform-Specific Issues

#### macOS Issues
```bash
# Install Xcode command line tools
xcode-select --install

# Fix OpenSSL issues
export LDFLAGS="-L$(brew --prefix openssl)/lib"
export CPPFLAGS="-I$(brew --prefix openssl)/include"
```

#### Linux Issues
```bash
# Install build dependencies
sudo apt install python3-dev build-essential

# Fix SSL issues
sudo apt install libssl-dev libffi-dev
```

#### Windows Issues
```bash
# Install Visual Studio Build Tools
# Download from: https://visualstudio.microsoft.com/visual-cpp-build-tools/

# Use pre-compiled wheels
pip install --only-binary=all -r requirements.txt
```

---

## 📊 Dependency Monitoring

### Monitoring Tools

#### pip-audit for Security
```bash
# Regular security scans
pip-audit --format=json --output=audit-$(date +%Y%m%d).json

# Set up automated scanning
echo "0 2 * * * cd /path/to/project && pip-audit" | crontab -
```

#### pipdeptree for Dependencies
```bash
# Visualize dependency tree
pipdeptree --graph-output png > dependencies.png

# Check for circular dependencies
pipdeptree --warn silence
```

### Automated Monitoring

#### GitHub Actions Workflow
```yaml
# .github/workflows/dependencies.yml
name: Dependency Check
on:
  schedule:
    - cron: '0 2 * * 1'  # Weekly on Monday
  push:
    paths:
      - 'requirements*.txt'
      - 'pyproject.toml'

jobs:
  security-scan:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - name: Install dependencies
        run: pip install pip-audit
      - name: Security scan
        run: pip-audit -r requirements.txt
```

---

## 🎯 Best Practices

### Development Workflow

1. **Always use virtual environments**
2. **Pin dependencies in production**
3. **Regular security scans**
4. **Test dependency updates**
5. **Document dependency choices**

### Production Deployment

```bash
# Production dependency installation
pip install --no-deps -r requirements-lock.txt

# Verify installation
pip check

# Security scan
pip-audit

# Performance check
python -c "import time; start=time.time(); import torch, transformers; print(f'Import time: {time.time()-start:.2f}s')"
```

### Dependency Documentation

```markdown
# Dependency Decisions

## Core Framework
- **pydantic**: Chosen for robust data validation and settings management
- **typer**: Provides excellent CLI experience with type hints
- **rich**: Enhanced terminal output and formatting

## AI/ML Stack
- **transformers**: Industry standard for transformer models
- **torch**: PyTorch for deep learning capabilities
- **scikit-learn**: Classical ML algorithms and utilities

## Infrastructure
- **redis**: High-performance in-memory storage for AI Memory Palace
- **fastapi**: Modern, fast web framework with automatic API docs
- **prometheus-client**: Industry standard metrics collection
```

---

## 📋 Dependency Checklist

### Before Installation
- [ ] **Python 3.9+** installed
- [ ] **Virtual environment** created and activated
- [ ] **pip** updated to latest version
- [ ] **System dependencies** installed (build tools, etc.)

### During Installation
- [ ] **Requirements file** exists and is readable
- [ ] **Network connectivity** to PyPI
- [ ] **Sufficient disk space** for packages
- [ ] **No conflicting packages** in environment

### After Installation
- [ ] **All packages** installed successfully
- [ ] **No dependency conflicts** (run `pip check`)
- [ ] **Security scan** passed (run `pip-audit`)
- [ ] **Import tests** successful
- [ ] **Version compatibility** verified

### Production Deployment
- [ ] **Pinned versions** in requirements-lock.txt
- [ ] **Security scan** clean
- [ ] **Performance testing** completed
- [ ] **Monitoring** configured
- [ ] **Rollback plan** prepared

---

## 🎉 Summary

Proper dependency management is crucial for:
- **Reproducible builds** across environments
- **Security** through vulnerability scanning
- **Performance** with optimized package versions
- **Maintainability** with clear dependency documentation

**Key takeaways:**
1. Always use virtual environments
2. Pin dependencies for production
3. Regular security scans
4. Document dependency decisions
5. Test updates before deployment

---

**Ready to manage dependencies like a pro? 🐺**

**Next steps:**
- 🚀 **Install dependencies**: `pip install -r requirements.txt`
- 🔒 **Security scan**: `pip-audit`
- 📊 **Check dependencies**: `pip check`
- 🎯 **Start building**: Follow the [Installation Guide](INSTALLATION_GUIDE.md)

---

*Dependency management mastered! Time to build amazing AI applications with Beast Mode! 🚀*