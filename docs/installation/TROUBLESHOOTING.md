# 🔧 Beast Mode AI Framework - Installation Troubleshooting Guide

> **Comprehensive solutions for common installation and setup issues**

This guide provides detailed troubleshooting steps for resolving installation problems, configuration issues, and runtime errors when setting up Beast Mode AI Framework.

---

## 🚨 Quick Diagnostic

**Having installation issues?** Run this quick diagnostic first:

```bash
# Quick system check
python -c "
import sys, platform, subprocess, os
print('🔍 Beast Mode Quick Diagnostic')
print('=' * 40)
print(f'Python: {sys.version}')
print(f'OS: {platform.system()} {platform.release()}')
print(f'Working directory: {os.getcwd()}')
print(f'PYTHONPATH: {os.environ.get(\"PYTHONPATH\", \"Not set\")}')

# Check if we're in the right directory
if os.path.exists('requirements.txt'):
    print('✅ Found requirements.txt')
else:
    print('❌ requirements.txt not found - are you in the project root?')

if os.path.exists('.env.example'):
    print('✅ Found .env.example')
else:
    print('❌ .env.example not found')

if os.path.exists('src/'):
    print('✅ Found src/ directory')
else:
    print('❌ src/ directory not found')
"
```

---

## 📋 Common Installation Issues

### Issue 1: `ImportError: No module named 'src'`

**Symptoms:**
```
ImportError: No module named 'src'
ModuleNotFoundError: No module named 'src.beast_mode'
```

**Cause:** Python cannot find the Beast Mode source modules.

**Solutions:**

#### Solution A: Set PYTHONPATH (Quick Fix)
```bash
# Temporary fix (current session only)
export PYTHONPATH="${PYTHONPATH}:$(pwd)"

# Test if it works
python -c "from src.beast_mode.core import BeastModeFramework; print('✅ Import successful')"
```

#### Solution B: Add to Shell Profile (Permanent)
```bash
# For bash users
echo 'export PYTHONPATH="${PYTHONPATH}:$(pwd)"' >> ~/.bashrc
source ~/.bashrc

# For zsh users (macOS default)
echo 'export PYTHONPATH="${PYTHONPATH}:$(pwd)"' >> ~/.zshrc
source ~/.zshrc

# For fish users
echo 'set -x PYTHONPATH $PYTHONPATH (pwd)' >> ~/.config/fish/config.fish
```

#### Solution C: Development Installation (Recommended)
```bash
# Install in development mode
pip install -e .

# This makes the package importable from anywhere
python -c "import beast_mode; print('✅ Development installation successful')"
```

#### Solution D: Create __init__.py Files
```bash
# Ensure all directories have __init__.py files
find src -type d -exec touch {}/__init__.py \;
```

### Issue 2: `pip install -r requirements.txt` Fails

**Symptoms:**
```
ERROR: Could not find a version that satisfies the requirement
ERROR: No matching distribution found
ERROR: Failed building wheel for [package]
```

**Solutions:**

#### Solution A: Update pip and setuptools
```bash
# Update pip to latest version
python -m pip install --upgrade pip setuptools wheel

# Try installation again
pip install -r requirements.txt
```

#### Solution B: Use Different Python Version
```bash
# Check available Python versions
python3 --version
python3.9 --version
python3.10 --version
python3.11 --version

# Use specific version
python3.11 -m pip install -r requirements.txt
```

#### Solution C: Install with Verbose Output
```bash
# See detailed error messages
pip install -r requirements.txt -v

# Install packages one by one to identify problematic package
pip install pydantic
pip install typer
pip install rich
# ... continue with each package
```

#### Solution D: Use Conda Instead of pip
```bash
# Install Miniconda/Anaconda first, then:
conda create -n beast-mode python=3.11
conda activate beast-mode
pip install -r requirements.txt
```

### Issue 3: Redis Connection Errors

**Symptoms:**
```
redis.exceptions.ConnectionError: Error connecting to Redis
ConnectionRefusedError: [Errno 61] Connection refused
```

**Solutions:**

#### Solution A: Install and Start Redis

**macOS (using Homebrew):**
```bash
# Install Redis
brew install redis

# Start Redis service
brew services start redis

# Test connection
redis-cli ping
# Should return: PONG
```

**Ubuntu/Debian:**
```bash
# Install Redis
sudo apt update
sudo apt install redis-server

# Start Redis service
sudo systemctl start redis-server
sudo systemctl enable redis-server

# Test connection
redis-cli ping
# Should return: PONG
```

**Windows (using WSL2 or Docker):**
```bash
# Option 1: WSL2
sudo apt install redis-server
sudo service redis-server start

# Option 2: Docker
docker run -d -p 6379:6379 --name redis redis:alpine

# Test connection
redis-cli ping
```

#### Solution B: Configure Redis Connection

Check your `.env` file:
```bash
# Verify Redis configuration
cat .env | grep REDIS

# Should show:
# REDIS_HOST=localhost
# REDIS_PORT=6379
# REDIS_PASSWORD=your_password_here
```

#### Solution C: Test Redis Connection Manually
```bash
# Test Redis connection with Python
python -c "
import redis
try:
    r = redis.Redis(host='localhost', port=6379, decode_responses=True)
    r.ping()
    print('✅ Redis connection successful')
except Exception as e:
    print(f'❌ Redis connection failed: {e}')
"
```

### Issue 4: Permission Denied Errors

**Symptoms:**
```
PermissionError: [Errno 13] Permission denied
OSError: [Errno 13] Permission denied: '.env'
```

**Solutions:**

#### Solution A: Fix File Permissions
```bash
# Fix .env file permissions
chmod 644 .env

# Fix script permissions
chmod +x scripts/*.py

# Fix directory permissions
chmod 755 src/
```

#### Solution B: Use Virtual Environment
```bash
# Create virtual environment (avoids system permission issues)
python -m venv .venv

# Activate virtual environment
source .venv/bin/activate  # Linux/macOS
# or
.venv\Scripts\activate  # Windows

# Install dependencies in virtual environment
pip install -r requirements.txt
```

#### Solution C: Install as User (not system-wide)
```bash
# Install packages for current user only
pip install --user -r requirements.txt

# Add user site-packages to PATH
export PATH="$HOME/.local/bin:$PATH"
```

### Issue 5: Docker Issues

**Symptoms:**
```
docker: command not found
Cannot connect to the Docker daemon
docker-compose: command not found
```

**Solutions:**

#### Solution A: Install Docker

**macOS:**
```bash
# Install Docker Desktop
brew install --cask docker

# Start Docker Desktop from Applications folder
# Wait for Docker to start (whale icon in menu bar)
```

**Ubuntu:**
```bash
# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Add user to docker group
sudo usermod -aG docker $USER

# Install Docker Compose
sudo apt install docker-compose-plugin

# Restart to apply group changes
sudo reboot
```

**Windows:**
```bash
# Download and install Docker Desktop for Windows
# From: https://www.docker.com/products/docker-desktop
```

#### Solution B: Start Docker Service
```bash
# Check Docker status
docker --version
docker ps

# Start Docker service (Linux)
sudo systemctl start docker
sudo systemctl enable docker

# Start Docker Desktop (macOS/Windows)
# Use the application launcher
```

#### Solution C: Fix Docker Permissions
```bash
# Add current user to docker group
sudo usermod -aG docker $USER

# Apply group changes
newgrp docker

# Test Docker without sudo
docker ps
```

### Issue 6: Jupyter Notebook Issues

**Symptoms:**
```
jupyter: command not found
Jupyter server failed to start
Port 8888 is already in use
```

**Solutions:**

#### Solution A: Install Jupyter
```bash
# Install Jupyter
pip install jupyter notebook jupyterlab

# Verify installation
jupyter --version
```

#### Solution B: Start Jupyter on Different Port
```bash
# Start on different port
jupyter notebook --port=8889 examples/notebook/

# Or let Jupyter find available port
jupyter notebook --port-retries=50 examples/notebook/
```

#### Solution C: Kill Existing Jupyter Processes
```bash
# Find Jupyter processes
ps aux | grep jupyter

# Kill specific process
kill [PID]

# Or kill all Jupyter processes
pkill -f jupyter
```

#### Solution D: Reset Jupyter Configuration
```bash
# Reset Jupyter config
jupyter --config-dir
rm -rf ~/.jupyter

# Regenerate config
jupyter notebook --generate-config
```

---

## 🔧 Configuration Issues

### Issue 1: Environment Variables Not Loading

**Symptoms:**
```
KeyError: 'REDIS_PASSWORD'
ValueError: Environment variable not set
```

**Solutions:**

#### Solution A: Verify .env File Exists
```bash
# Check if .env file exists
ls -la .env

# If not, create from example
cp .env.example .env
```

#### Solution B: Check .env File Format
```bash
# Verify .env file format
cat .env

# Should look like:
# REDIS_PASSWORD=your_password_here
# DEBUG=false
# ENVIRONMENT=development

# Common issues:
# ❌ REDIS_PASSWORD = your_password  # spaces around =
# ❌ REDIS_PASSWORD="your_password"  # quotes (sometimes problematic)
# ✅ REDIS_PASSWORD=your_password    # correct format
```

#### Solution C: Load Environment Variables Manually
```bash
# Test environment variable loading
python -c "
import os
from pathlib import Path

# Load .env file manually
env_file = Path('.env')
if env_file.exists():
    with open(env_file) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, value = line.split('=', 1)
                os.environ[key.strip()] = value.strip()
                print(f'Loaded: {key.strip()}')
else:
    print('❌ .env file not found')

# Test specific variable
redis_password = os.getenv('REDIS_PASSWORD')
if redis_password:
    print(f'✅ REDIS_PASSWORD loaded: {redis_password[:4]}...')
else:
    print('❌ REDIS_PASSWORD not found')
"
```

### Issue 2: Invalid Configuration Values

**Symptoms:**
```
ValueError: invalid literal for int()
TypeError: expected str, got NoneType
```

**Solutions:**

#### Solution A: Validate Configuration
```bash
# Check configuration values
python -c "
import os

# Check required variables
required_vars = ['REDIS_HOST', 'REDIS_PORT', 'REDIS_PASSWORD']
for var in required_vars:
    value = os.getenv(var)
    if value:
        print(f'✅ {var}: {value}')
    else:
        print(f'❌ {var}: Not set')

# Validate types
try:
    port = int(os.getenv('REDIS_PORT', '6379'))
    print(f'✅ REDIS_PORT is valid integer: {port}')
except ValueError:
    print('❌ REDIS_PORT is not a valid integer')
"
```

#### Solution B: Use Default Values
```bash
# Update .env with safe defaults
cat > .env << 'EOF'
# Beast Mode Configuration
DEBUG=false
ENVIRONMENT=development
LOG_LEVEL=INFO

# Redis Configuration
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_PASSWORD=beast_mode_redis_2025

# Optional API Keys (leave empty if not needed)
OPENAI_API_KEY=
ANTHROPIC_API_KEY=

# Security (auto-generated if empty)
JWT_SECRET=
ENCRYPTION_KEY=
EOF
```

---

## 🐍 Python-Specific Issues

### Issue 1: Wrong Python Version

**Symptoms:**
```
SyntaxError: invalid syntax (using Python 2.7)
ModuleNotFoundError: No module named 'typing_extensions'
```

**Solutions:**

#### Solution A: Check Python Version
```bash
# Check all available Python versions
python --version
python3 --version
python3.9 --version
python3.10 --version
python3.11 --version

# Use specific version
python3.11 -m pip install -r requirements.txt
python3.11 examples/quick_start_demo.py
```

#### Solution B: Create Alias
```bash
# Create alias for correct Python version
echo 'alias python=python3.11' >> ~/.bashrc
echo 'alias pip=python3.11 -m pip' >> ~/.bashrc
source ~/.bashrc
```

#### Solution C: Use pyenv (Python Version Manager)
```bash
# Install pyenv
curl https://pyenv.run | bash

# Install Python 3.11
pyenv install 3.11.5
pyenv global 3.11.5

# Verify
python --version
```

### Issue 2: Virtual Environment Issues

**Symptoms:**
```
ModuleNotFoundError after activating venv
pip installs to wrong location
```

**Solutions:**

#### Solution A: Recreate Virtual Environment
```bash
# Remove existing virtual environment
rm -rf .venv

# Create new virtual environment
python3.11 -m venv .venv

# Activate virtual environment
source .venv/bin/activate

# Verify activation
which python
which pip

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt
```

#### Solution B: Fix Virtual Environment Path
```bash
# Check if virtual environment is activated
echo $VIRTUAL_ENV

# If not activated, activate it
source .venv/bin/activate

# Verify Python and pip paths
which python  # Should show .venv/bin/python
which pip     # Should show .venv/bin/pip
```

---

## 🖥️ Operating System Specific Issues

### macOS Issues

#### Issue: Command Line Tools Missing
```bash
# Install Xcode command line tools
xcode-select --install

# Verify installation
xcode-select -p
```

#### Issue: Homebrew Issues
```bash
# Install Homebrew
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Update Homebrew
brew update
brew upgrade

# Fix permissions
sudo chown -R $(whoami) /usr/local/var/homebrew
```

#### Issue: Apple Silicon (M1/M2) Compatibility
```bash
# Check architecture
uname -m  # Should show arm64 for Apple Silicon

# Install Rosetta 2 if needed
softwareupdate --install-rosetta

# Use native Python
brew install python@3.11
```

### Linux Issues

#### Issue: Missing System Dependencies
```bash
# Ubuntu/Debian
sudo apt update
sudo apt install -y \
    python3-dev \
    python3-pip \
    python3-venv \
    build-essential \
    libssl-dev \
    libffi-dev \
    git \
    curl \
    wget

# CentOS/RHEL
sudo yum update
sudo yum install -y \
    python3-devel \
    python3-pip \
    gcc \
    gcc-c++ \
    openssl-devel \
    libffi-devel \
    git \
    curl \
    wget
```

#### Issue: SELinux Issues
```bash
# Check SELinux status
sestatus

# Temporarily disable SELinux (if needed)
sudo setenforce 0

# Or configure SELinux policies for Python
sudo setsebool -P httpd_can_network_connect 1
```

### Windows Issues

#### Issue: WSL2 Setup
```bash
# Enable WSL2
wsl --install

# Set WSL2 as default
wsl --set-default-version 2

# Install Ubuntu
wsl --install -d Ubuntu

# Update WSL2
wsl --update
```

#### Issue: Path Issues
```bash
# Check PATH in WSL2
echo $PATH

# Add Windows paths if needed
export PATH="$PATH:/mnt/c/Windows/System32"
```

---

## 🔍 Advanced Diagnostics

### Complete System Diagnostic

Run this comprehensive diagnostic script:

```bash
# Create diagnostic script
cat > diagnostic.py << 'EOF'
#!/usr/bin/env python3
"""
Beast Mode AI Framework - Comprehensive Diagnostic Tool
"""
import sys
import os
import platform
import subprocess
import importlib.util
from pathlib import Path

def run_command(cmd):
    """Run command and return result"""
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        return result.returncode == 0, result.stdout.strip(), result.stderr.strip()
    except Exception as e:
        return False, "", str(e)

def check_python():
    """Check Python installation"""
    print("🐍 Python Environment")
    print("-" * 30)
    print(f"Python version: {sys.version}")
    print(f"Python executable: {sys.executable}")
    print(f"Python path: {sys.path[:3]}...")
    
    # Check version compatibility
    if sys.version_info >= (3, 9):
        print("✅ Python version compatible")
    else:
        print("❌ Python version too old (need 3.9+)")
    
    print()

def check_system():
    """Check system information"""
    print("💻 System Information")
    print("-" * 30)
    print(f"OS: {platform.system()} {platform.release()}")
    print(f"Architecture: {platform.machine()}")
    print(f"Processor: {platform.processor()}")
    
    # Check system resources
    try:
        import psutil
        print(f"CPU cores: {psutil.cpu_count()}")
        print(f"RAM: {psutil.virtual_memory().total / 1024**3:.1f} GB")
        print(f"Disk free: {psutil.disk_usage('/').free / 1024**3:.1f} GB")
        print("✅ System resources adequate")
    except ImportError:
        print("⚠️  psutil not available for resource check")
    
    print()

def check_dependencies():
    """Check system dependencies"""
    print("📦 System Dependencies")
    print("-" * 30)
    
    deps = ['git', 'curl', 'pip']
    for dep in deps:
        success, stdout, stderr = run_command(f"{dep} --version")
        if success:
            version = stdout.split('\n')[0]
            print(f"✅ {dep}: {version}")
        else:
            print(f"❌ {dep}: Not available")
    
    print()

def check_project_structure():
    """Check project structure"""
    print("📁 Project Structure")
    print("-" * 30)
    
    required_files = [
        'requirements.txt',
        '.env.example',
        'src/',
        'examples/',
        'docs/',
        'Makefile'
    ]
    
    for item in required_files:
        path = Path(item)
        if path.exists():
            print(f"✅ {item}: Found")
        else:
            print(f"❌ {item}: Missing")
    
    print()

def check_python_packages():
    """Check Python package installation"""
    print("🐍 Python Packages")
    print("-" * 30)
    
    core_packages = [
        'pydantic',
        'typer',
        'rich',
        'fastapi',
        'redis',
        'pytest'
    ]
    
    for package in core_packages:
        try:
            spec = importlib.util.find_spec(package)
            if spec:
                print(f"✅ {package}: Installed")
            else:
                print(f"❌ {package}: Not found")
        except ImportError:
            print(f"❌ {package}: Import error")
    
    print()

def check_environment():
    """Check environment configuration"""
    print("⚙️  Environment Configuration")
    print("-" * 30)
    
    # Check .env file
    env_file = Path('.env')
    if env_file.exists():
        print("✅ .env file exists")
        
        # Load and check variables
        env_vars = {}
        with open(env_file) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    env_vars[key.strip()] = value.strip()
        
        required_vars = ['REDIS_HOST', 'REDIS_PORT']
        for var in required_vars:
            if var in env_vars:
                print(f"✅ {var}: Set")
            else:
                print(f"⚠️  {var}: Not set")
    else:
        print("❌ .env file missing")
    
    print()

def check_services():
    """Check external services"""
    print("🔧 External Services")
    print("-" * 30)
    
    # Check Redis
    try:
        import redis
        r = redis.Redis(host='localhost', port=6379, decode_responses=True)
        r.ping()
        print("✅ Redis: Connected")
    except Exception as e:
        print(f"❌ Redis: {e}")
    
    # Check Docker
    success, stdout, stderr = run_command("docker --version")
    if success:
        print(f"✅ Docker: {stdout}")
    else:
        print("⚠️  Docker: Not available")
    
    print()

def main():
    """Run all diagnostic checks"""
    print("🔍 Beast Mode AI Framework - System Diagnostic")
    print("=" * 60)
    print()
    
    check_python()
    check_system()
    check_dependencies()
    check_project_structure()
    check_python_packages()
    check_environment()
    check_services()
    
    print("🎯 Diagnostic Complete")
    print("=" * 60)
    print()
    print("If you see ❌ errors above, refer to the troubleshooting guide:")
    print("docs/installation/TROUBLESHOOTING.md")

if __name__ == "__main__":
    main()
EOF

# Run diagnostic
python diagnostic.py
```

### Performance Diagnostic

```bash
# Test system performance
python -c "
import time
import sys
import os

print('⚡ Performance Diagnostic')
print('=' * 40)

# CPU test
print('Testing CPU performance...')
start = time.time()
result = sum(i*i for i in range(1000000))
cpu_time = time.time() - start
print(f'CPU test: {cpu_time:.3f}s')

# Memory test
print('Testing memory performance...')
start = time.time()
data = [i for i in range(1000000)]
del data
mem_time = time.time() - start
print(f'Memory test: {mem_time:.3f}s')

# Import test
print('Testing import performance...')
start = time.time()
try:
    import numpy
    import pandas
    import torch
    import transformers
    import_time = time.time() - start
    print(f'Import test: {import_time:.3f}s')
    print('✅ All major packages imported successfully')
except ImportError as e:
    print(f'❌ Import failed: {e}')

# Overall assessment
total_time = cpu_time + mem_time
if total_time < 1.0:
    print('🚀 Excellent performance expected')
elif total_time < 3.0:
    print('✅ Good performance expected')
else:
    print('⚠️  Performance may be limited')
"
```

---

## 🆘 Getting Help

### Before Asking for Help

1. **Run the diagnostic script** above to gather system information
2. **Check the error logs** for detailed error messages
3. **Search existing issues** in the GitHub repository
4. **Try the suggested solutions** in this guide

### How to Report Issues

When creating a GitHub issue, include:

```bash
# System Information Template
**System Information:**
- OS: [e.g., Ubuntu 22.04, macOS 13.0, Windows 11]
- Python version: [output of `python --version`]
- Architecture: [output of `uname -m`]
- Installation method: [pip, Docker, development]

**Error Details:**
- Full error message: [paste complete error]
- Command that failed: [exact command you ran]
- Expected behavior: [what should have happened]
- Actual behavior: [what actually happened]

**Environment:**
- Virtual environment: [yes/no]
- .env file configured: [yes/no]
- Redis running: [yes/no]
- Docker available: [yes/no]

**Diagnostic Output:**
[paste output of diagnostic.py script]

**Additional Context:**
[any other relevant information]
```

### Community Resources

- **📚 Documentation**: [docs/](../README.md)
- **💬 GitHub Discussions**: For questions and community help
- **🐛 GitHub Issues**: For bug reports and feature requests
- **📧 Email Support**: [support@beastmode.dev](mailto:support@beastmode.dev)

---

## ✅ Verification Checklist

After resolving issues, verify your installation:

- [ ] **Python 3.9+** installed and accessible
- [ ] **Dependencies** installed without errors
- [ ] **Project structure** complete and accessible
- [ ] **Environment variables** configured correctly
- [ ] **Redis connection** working (if using AI Memory Palace)
- [ ] **Quick start demo** runs successfully
- [ ] **Import tests** pass without errors
- [ ] **System performance** adequate for your use case

### Final Verification

```bash
# Run complete verification
make quick-start

# If successful, you should see:
# 🐺 Beast Mode AI Framework - Quick Start Demo
# ✅ Core framework loaded successfully
# ✅ ReflectiveModule pattern working
# ✅ AI Memory Palace connected
# ✅ Health monitoring active
# ✅ Demo completed successfully!
```

---

**🎉 Installation issues resolved? You're ready to build with Beast Mode! 🐺**

**Next steps:**
- 🚀 **Try the examples**: `jupyter notebook examples/notebook/`
- 📖 **Read the guides**: [docs/guides/](../guides/)
- 🏗️ **Build your first agent**: Follow the quick start tutorial

---

*Still having issues? Don't hesitate to reach out to the community for help!*