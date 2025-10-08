#!/bin/bash
# Setup Prevention Framework - Comprehensive installation script
# ============================================================
# This script sets up the complete prevention framework to prevent
# future indentation issues and maintain code quality.

set -e  # Exit on any error

echo "🛡️ SETTING UP COMPREHENSIVE PREVENTION FRAMEWORK"
echo "================================================"

# Check if we're in the right directory
if [ ! -f "pyproject.toml" ] && [ ! -f "requirements.txt" ]; then
    echo "❌ Error: Please run this script from the project root directory"
    exit 1
fi

# Check Python version
echo "🔍 Checking Python version..."
python3 --version

# Install required dependencies
echo "📦 Installing required dependencies..."
pip3 install --upgrade pip
pip3 install pre-commit black isort flake8 mypy pyyaml

# Make scripts executable
echo "🔧 Making scripts executable..."
chmod +x scripts/*.py
chmod +x scripts/code_generation_validator.py
chmod +x scripts/indentation_validator.py
chmod +x scripts/code_generation_templates.py
chmod +x scripts/integration_test_runner.py
chmod +x scripts/prevention_framework_manager.py

# Install pre-commit hooks
echo "🔧 Installing pre-commit hooks..."
pre-commit install

# Validate all components
echo "🔍 Validating prevention framework components..."
python3 scripts/prevention_framework_manager.py --validate

# Run initial validation
echo "🔍 Running initial validation..."
python3 scripts/prevention_framework_manager.py --run-validation

# Test code generation templates
echo "🧪 Testing code generation templates..."
python3 scripts/code_generation_templates.py --list

# Test syntax validation
echo "🧪 Testing syntax validation..."
python3 scripts/code_generation_validator.py scripts/code_generation_validator.py

# Test indentation validation
echo "🧪 Testing indentation validation..."
python3 scripts/indentation_validator.py scripts/indentation_validator.py

# Run integration tests
echo "🧪 Running integration tests..."
python3 scripts/integration_test_runner.py

# Generate final report
echo "📊 Generating prevention framework report..."
python3 scripts/prevention_framework_manager.py --report --output prevention_framework_setup_report.txt

echo ""
echo "✅ PREVENTION FRAMEWORK SETUP COMPLETE!"
echo "======================================"
echo ""
echo "📋 FRAMEWORK COMPONENTS INSTALLED:"
echo "• Code Generation Validator"
echo "• Indentation Validator"
echo "• Code Generation Templates"
echo "• Pre-commit Hooks"
echo "• GitHub Actions Workflow"
echo "• Integration Test Runner"
echo "• Prevention Framework Manager"
echo ""
echo "🔧 NEXT STEPS:"
echo "1. Pre-commit hooks are now active"
echo "2. All commits will be validated automatically"
echo "3. CI/CD pipeline will run on push/PR"
echo "4. Use 'python3 scripts/prevention_framework_manager.py --validate' to check status"
echo ""
echo "📄 Report saved to: prevention_framework_setup_report.txt"
echo ""
echo "🛡️ Your codebase is now protected against indentation issues!"
