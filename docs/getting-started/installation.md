# 🚀 Beast Mode Installation Guide

Get Beast Mode AI Framework up and running in minutes with this comprehensive installation guide.

> **📚 Complete Installation Documentation:**
> - **[📋 System Requirements](../installation/SYSTEM_REQUIREMENTS.md)** - Detailed technical specifications
> - **[📦 Installation Guide](../installation/INSTALLATION_GUIDE.md)** - Comprehensive installation instructions  
> - **[🔧 Troubleshooting](../installation/TROUBLESHOOTING.md)** - Solutions for common issues
> - **[📦 Dependency Management](../installation/DEPENDENCY_MANAGEMENT.md)** - Advanced dependency handling

## 📋 System Requirements

### Minimum Requirements
- **Python**: 3.9 or higher
- **Memory**: 4GB RAM 
- **Storage**: 2GB free space
- **OS**: Linux, macOS, or Windows with WSL

### Recommended Requirements
- **Python**: 3.11+
- **Memory**: 8GB RAM
- **Storage**: 5GB free space
- **OS**: Linux or macOS for best performance

## 🎯 Quick Installation (Recommended)

The fastest way to get started:

```bash
# 1. Clone the repository
git clone https://github.com/your-org/beast-mode-ai-framework.git
cd beast-mode-ai-framework

# 2. One-command setup
make install

# 3. Run the quick demo
make quick-start
```

That's it! You're ready to build with Beast Mode.

## 📦 Installation Options

### Option 1: Standard Installation

```bash
# Clone repository
git clone https://github.com/your-org/beast-mode-ai-framework.git
cd beast-mode-ai-framework

# Install dependencies
pip install -r requirements.txt

# Set up environment
cp .env.example .env
# Edit .env with your configuration

# Verify installation
python examples/quick_start_demo.py
```

### Option 2: Virtual Environment (Recommended for Development)

```bash
# Clone repository
git clone https://github.com/your-org/beast-mode-ai-framework.git
cd beast-mode-ai-framework

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment
cp .env.example .env

# Verify installation
python examples/quick_start_demo.py
```

### Option 3: Docker Installation

```bash
# Clone repository
git clone https://github.com/your-org/beast-mode-ai-framework.git
cd beast-mode-ai-framework

# Build and run with Docker
docker-compose up -d

# Run examples
docker-compose exec app python examples/quick_start_demo.py

# Access Jupyter notebooks
docker-compose exec app jupyter notebook --ip=0.0.0.0 --port=8888 --allow-root
```

### Option 4: Development Installation

For contributors and advanced users:

```bash
# Clone repository
git clone https://github.com/your-org/beast-mode-ai-framework.git
cd beast-mode-ai-framework

# Install in development mode
pip install -e .
pip install -r requirements-dev.txt

# Set up pre-commit hooks
pre-commit install

# Run tests to verify
pytest tests/

# Run quality checks
make lint
make test
```

## ⚙️ Environment Configuration

Beast Mode uses environment variables for configuration. Copy the example file and customize:

```bash
cp .env.example .env
```

### Required Configuration

Edit `.env` with your settings:

```bash
# Application Configuration
DEBUG=false
ENVIRONMENT=development

# Redis Configuration (for AI Memory Palace)
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_PASSWORD=your_redis_password_here

# Optional: API Keys for external integrations
OPENAI_API_KEY=your_openai_api_key_here
ANTHROPIC_API_KEY=your_anthropic_api_key_here
```

### Configuration Options

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `DEBUG` | Enable debug mode | `false` | No |
| `ENVIRONMENT` | Environment name | `development` | No |
| `REDIS_HOST` | Redis server host | `localhost` | Yes* |
| `REDIS_PORT` | Redis server port | `6379` | Yes* |
| `REDIS_PASSWORD` | Redis password | - | Yes* |
| `OPENAI_API_KEY` | OpenAI API key | - | No |
| `ANTHROPIC_API_KEY` | Anthropic API key | - | No |

*Required for AI Memory Palace functionality

## 🔧 Optional Dependencies

### Redis (for AI Memory Palace)

Beast Mode's AI Memory Palace requires Redis for persistent memory:

#### Install Redis on macOS:
```bash
brew install redis
brew services start redis
```

#### Install Redis on Ubuntu/Debian:
```bash
sudo apt update
sudo apt install redis-server
sudo systemctl start redis-server
```

#### Install Redis on Windows:
```bash
# Using WSL or Docker is recommended
docker run -d -p 6379:6379 redis:alpine
```

### Jupyter (for Interactive Notebooks)

For the best Beast Mode experience with interactive notebooks:

```bash
pip install jupyter notebook
jupyter notebook examples/notebook/
```

## ✅ Verify Installation

Run these commands to verify everything is working:

### 1. Quick Start Demo
```bash
python examples/quick_start_demo.py
```
Expected: Demo runs successfully showing Beast Mode features

### 2. Health Check
```bash
python -c "from src.rm_ddd.core.unified_reflective_module import ReflectiveModule; print('✅ Beast Mode core imported successfully')"
```

### 3. Run Tests (if installed in dev mode)
```bash
pytest tests/ -v
```
Expected: All tests pass

### 4. Interactive Notebooks
```bash
jupyter notebook examples/notebook/
```
Expected: Jupyter opens with Beast Mode example notebooks

## 🚨 Troubleshooting

### Common Issues

#### ImportError: No module named 'src'
**Solution**: Make sure you're in the project root directory and Python can find the modules:
```bash
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
# Or add to your .bashrc/.zshrc
```

#### Redis Connection Error
**Solution**: Make sure Redis is running and configured correctly:
```bash
# Check if Redis is running
redis-cli ping
# Should return: PONG

# Check your .env file has correct Redis settings
cat .env | grep REDIS
```

#### Permission Denied Errors
**Solution**: Make sure you have write permissions:
```bash
# Check permissions
ls -la .env

# Fix permissions if needed
chmod 644 .env
```

#### Python Version Issues
**Solution**: Verify you're using Python 3.9+:
```bash
python --version
# Should show Python 3.9.0 or higher

# If not, try:
python3 --version
python3.9 --version
```

### Getting Help

If you encounter issues:

1. **Check the logs**: Most Beast Mode components provide detailed error messages
2. **Review the documentation**: See [docs/guides/](../guides/) for detailed guides
3. **Search existing issues**: Check [GitHub Issues](https://github.com/your-org/beast-mode-ai-framework/issues)
4. **Ask for help**: Create a new issue with:
   - Your operating system
   - Python version
   - Complete error message
   - Steps to reproduce

## 🎉 Next Steps

Once installation is complete:

1. **🚀 Run the Quick Start**: `python examples/quick_start_demo.py`
2. **📚 Explore Notebooks**: `jupyter notebook examples/notebook/`
3. **📖 Read the Guides**: Start with [docs/guides/quick-start.md](../guides/quick-start.md)
4. **🏗️ Build Your First Agent**: Follow the [tutorial](../guides/building-your-first-agent.md)

Welcome to systematic AI development with Beast Mode! 🐺