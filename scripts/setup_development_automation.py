#!/usr/bin/env python3
"""
Development Automation Setup Script

This script sets up comprehensive development automation including:
- Pre-commit hooks
- Git hooks
- CI/CD validation
- Security scanning
- Code quality checks
"""

import os
import subprocess
import sys
from pathlib import Path
from typing import List, Tuple


class DevelopmentAutomationSetup:
    """Sets up development automation tools and workflows."""
    
    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.errors: List[str] = []
        self.warnings: List[str] = []
    
    def run_command(self, command: List[str], description: str) -> Tuple[bool, str]:
        """Run a command and return success status and output."""
        try:
            result = subprocess.run(
                command,
                cwd=self.project_root,
                capture_output=True,
                text=True,
                check=True
            )
            print(f"✅ {description}")
            return True, result.stdout
        except subprocess.CalledProcessError as e:
            error_msg = f"❌ {description}: {e.stderr}"
            self.errors.append(error_msg)
            print(error_msg)
            return False, e.stderr
        except FileNotFoundError:
            error_msg = f"❌ {description}: Command not found"
            self.errors.append(error_msg)
            print(error_msg)
            return False, "Command not found"
    
    def check_prerequisites(self) -> bool:
        """Check if required tools are installed."""
        print("🔍 Checking prerequisites...")
        
        prerequisites = [
            (["python", "--version"], "Python"),
            (["git", "--version"], "Git"),
            (["pip", "--version"], "Pip"),
        ]
        
        all_good = True
        for command, name in prerequisites:
            success, _ = self.run_command(command, f"Checking {name}")
            if not success:
                all_good = False
        
        return all_good
    
    def install_development_dependencies(self) -> bool:
        """Install development dependencies."""
        print("📦 Installing development dependencies...")
        
        # Install pre-commit
        success, _ = self.run_command(
            ["pip", "install", "pre-commit"],
            "Installing pre-commit"
        )
        if not success:
            return False
        
        # Install security tools
        security_tools = [
            "bandit",
            "detect-secrets",
            "safety",
            "pip-audit"
        ]
        
        for tool in security_tools:
            success, _ = self.run_command(
                ["pip", "install", tool],
                f"Installing {tool}"
            )
            if not success:
                self.warnings.append(f"Failed to install {tool}")
        
        # Install code quality tools
        quality_tools = [
            "black",
            "isort",
            "ruff",
            "mypy"
        ]
        
        for tool in quality_tools:
            success, _ = self.run_command(
                ["pip", "install", tool],
                f"Installing {tool}"
            )
            if not success:
                self.warnings.append(f"Failed to install {tool}")
        
        return True
    
    def setup_pre_commit_hooks(self) -> bool:
        """Set up pre-commit hooks."""
        print("🪝 Setting up pre-commit hooks...")
        
        # Install pre-commit hooks
        success, _ = self.run_command(
            ["pre-commit", "install"],
            "Installing pre-commit hooks"
        )
        if not success:
            return False
        
        # Install commit-msg hook for conventional commits
        success, _ = self.run_command(
            ["pre-commit", "install", "--hook-type", "commit-msg"],
            "Installing commit-msg hook"
        )
        if not success:
            self.warnings.append("Failed to install commit-msg hook")
        
        # Run pre-commit on all files to test
        print("🧪 Testing pre-commit hooks...")
        success, output = self.run_command(
            ["pre-commit", "run", "--all-files"],
            "Testing pre-commit hooks"
        )
        if not success:
            print("⚠️  Pre-commit hooks found issues. This is normal for first run.")
            print("Run 'pre-commit run --all-files' to fix issues.")
        
        return True
    
    def setup_git_hooks(self) -> bool:
        """Set up additional Git hooks."""
        print("🔗 Setting up Git hooks...")
        
        hooks_dir = self.project_root / ".git" / "hooks"
        hooks_dir.mkdir(exist_ok=True)
        
        # Create pre-push hook for security validation
        pre_push_hook = hooks_dir / "pre-push"
        pre_push_content = '''#!/bin/bash
# Pre-push hook for security validation

echo "🔒 Running security validation before push..."

# Run credential scan
if command -v detect-secrets &> /dev/null; then
    echo "Scanning for credentials..."
    detect-secrets scan --all-files --baseline .secrets.baseline
    if [ $? -ne 0 ]; then
        echo "❌ Credential scan failed. Push aborted."
        exit 1
    fi
fi

# Run security scan
if command -v bandit &> /dev/null; then
    echo "Running security scan..."
    bandit -r src/ -ll
    if [ $? -ne 0 ]; then
        echo "❌ Security scan found high/medium issues. Push aborted."
        exit 1
    fi
fi

echo "✅ Security validation passed"
exit 0
'''
        
        pre_push_hook.write_text(pre_push_content)
        pre_push_hook.chmod(0o755)
        print("✅ Created pre-push security hook")
        
        return True
    
    def setup_secrets_baseline(self) -> bool:
        """Set up secrets baseline for detect-secrets."""
        print("🔐 Setting up secrets baseline...")
        
        baseline_file = self.project_root / ".secrets.baseline"
        if not baseline_file.exists():
            success, _ = self.run_command(
                ["detect-secrets", "scan", "--all-files", "--baseline", ".secrets.baseline"],
                "Creating secrets baseline"
            )
            if not success:
                return False
        else:
            print("✅ Secrets baseline already exists")
        
        return True
    
    def validate_ci_workflows(self) -> bool:
        """Validate CI/CD workflow files."""
        print("🔄 Validating CI/CD workflows...")
        
        workflows_dir = self.project_root / ".github" / "workflows"
        if not workflows_dir.exists():
            self.warnings.append("No .github/workflows directory found")
            return True
        
        workflow_files = list(workflows_dir.glob("*.yml")) + list(workflows_dir.glob("*.yaml"))
        
        for workflow_file in workflow_files:
            # Basic YAML validation
            try:
                import yaml
                with open(workflow_file, 'r') as f:
                    yaml.safe_load(f)
                print(f"✅ Validated {workflow_file.name}")
            except ImportError:
                self.warnings.append("PyYAML not installed, skipping workflow validation")
                break
            except yaml.YAMLError as e:
                self.errors.append(f"Invalid YAML in {workflow_file.name}: {e}")
                return False
        
        return True
    
    def create_automation_documentation(self) -> bool:
        """Create documentation for automation setup."""
        print("📚 Creating automation documentation...")
        
        docs_dir = self.project_root / "docs" / "development"
        docs_dir.mkdir(parents=True, exist_ok=True)
        
        automation_doc = docs_dir / "AUTOMATION_SETUP.md"
        doc_content = '''# Development Automation Setup

This document describes the automated development tools and workflows set up for the Beast Mode AI Development Framework.

## Overview

The project uses comprehensive automation to ensure code quality, security, and consistency:

- **Pre-commit hooks**: Automated checks before each commit
- **CI/CD workflows**: Continuous integration and deployment
- **Security scanning**: Automated credential and vulnerability detection
- **Code quality**: Formatting, linting, and type checking
- **Documentation**: Automated documentation generation and validation

## Pre-commit Hooks

Pre-commit hooks run automatically before each commit to catch issues early:

### Security Checks
- **detect-secrets**: Scans for hardcoded credentials
- **credential-check**: Custom validation for credential patterns
- **environment-variable-check**: Ensures proper environment variable usage

### Code Quality
- **black**: Python code formatting
- **isort**: Import sorting
- **ruff**: Fast Python linting
- **mypy**: Type checking

### General Checks
- **trailing-whitespace**: Removes trailing whitespace
- **end-of-file-fixer**: Ensures files end with newline
- **check-yaml/json/toml**: Validates file formats
- **check-private-key**: Prevents committing private keys
- **check-added-large-files**: Prevents large file commits

## CI/CD Workflows

### Main CI Pipeline (`.github/workflows/ci.yml`)
- **Security scan**: Comprehensive security analysis
- **Code quality**: Formatting, linting, type checking
- **Tests**: Unit, integration, and security tests
- **Documentation**: Validates documentation and examples
- **Build**: Package building and validation

### Security Pipeline (`.github/workflows/security.yml`)
- **Credential scanning**: Deep credential detection
- **Dependency scanning**: Vulnerability analysis
- **Code security**: Static security analysis
- **Daily scans**: Scheduled security validation

### Documentation Pipeline (`.github/workflows/documentation.yml`)
- **Documentation validation**: Markdown and link checking
- **Example testing**: Validates all code examples
- **API documentation**: Auto-generates API docs

### Release Pipeline (`.github/workflows/release.yml`)
- **Release validation**: Comprehensive pre-release testing
- **Package building**: Creates distribution packages
- **Release creation**: Automated GitHub releases
- **Changelog generation**: Auto-generated release notes

## Git Hooks

### Pre-push Hook
Runs security validation before pushing:
- Credential scanning with detect-secrets
- Security analysis with bandit
- Prevents pushing code with security issues

## Setup Commands

### Initial Setup
```bash
# Install development dependencies
pip install -r requirements-dev.txt

# Set up automation
python scripts/setup_development_automation.py

# Install pre-commit hooks
pre-commit install
```

### Manual Commands
```bash
# Run all pre-commit hooks
pre-commit run --all-files

# Run security scan
bandit -r src/ -ll

# Run credential scan
detect-secrets scan --all-files --baseline .secrets.baseline

# Run tests
python -m pytest tests/ --cov=src
```

## Configuration Files

- **`.pre-commit-config.yaml`**: Pre-commit hook configuration
- **`.secrets.baseline`**: Baseline for detect-secrets
- **`.github/workflows/`**: CI/CD workflow definitions
- **`pyproject.toml`**: Python project configuration
- **`requirements-dev.txt`**: Development dependencies

## Troubleshooting

### Pre-commit Issues
```bash
# Update hooks
pre-commit autoupdate

# Clear cache
pre-commit clean

# Skip hooks (emergency only)
git commit --no-verify
```

### Security Scan Issues
```bash
# Update secrets baseline
detect-secrets scan --all-files --baseline .secrets.baseline

# Audit secrets
detect-secrets audit .secrets.baseline
```

### CI/CD Issues
- Check workflow logs in GitHub Actions
- Validate YAML syntax locally
- Test workflows with act (GitHub Actions local runner)

## Best Practices

1. **Never skip security checks** without proper justification
2. **Keep dependencies updated** regularly
3. **Review automation failures** carefully
4. **Document any exceptions** or workarounds
5. **Test changes locally** before pushing

## Maintenance

- **Weekly**: Review and update dependencies
- **Monthly**: Update pre-commit hooks and tools
- **Quarterly**: Review and optimize workflows
- **As needed**: Add new checks for emerging issues
'''
        
        automation_doc.write_text(doc_content)
        print("✅ Created automation documentation")
        
        return True
    
    def run_setup(self) -> bool:
        """Run the complete automation setup."""
        print("🚀 Setting up development automation for Beast Mode AI Framework")
        print("=" * 60)
        
        steps = [
            ("Prerequisites", self.check_prerequisites),
            ("Development Dependencies", self.install_development_dependencies),
            ("Pre-commit Hooks", self.setup_pre_commit_hooks),
            ("Git Hooks", self.setup_git_hooks),
            ("Secrets Baseline", self.setup_secrets_baseline),
            ("CI/CD Validation", self.validate_ci_workflows),
            ("Documentation", self.create_automation_documentation),
        ]
        
        for step_name, step_func in steps:
            print(f"\n📋 {step_name}")
            print("-" * 40)
            if not step_func():
                print(f"❌ Failed to complete {step_name}")
                return False
        
        return True
    
    def print_summary(self):
        """Print setup summary."""
        print("\n" + "=" * 60)
        print("🎉 Development Automation Setup Complete!")
        print("=" * 60)
        
        if not self.errors and not self.warnings:
            print("✅ All automation tools set up successfully!")
        else:
            if self.errors:
                print(f"❌ {len(self.errors)} errors occurred:")
                for error in self.errors:
                    print(f"  {error}")
            
            if self.warnings:
                print(f"⚠️  {len(self.warnings)} warnings:")
                for warning in self.warnings:
                    print(f"  {warning}")
        
        print("\n📋 Next Steps:")
        print("1. Run 'pre-commit run --all-files' to test hooks")
        print("2. Make a test commit to verify automation")
        print("3. Review .github/workflows/ for CI/CD configuration")
        print("4. Check docs/development/AUTOMATION_SETUP.md for details")
        
        print("\n🔧 Useful Commands:")
        print("- pre-commit run --all-files  # Run all hooks")
        print("- bandit -r src/ -ll          # Security scan")
        print("- detect-secrets scan         # Credential scan")
        print("- python -m pytest tests/    # Run tests")


def main():
    """Main entry point."""
    setup = DevelopmentAutomationSetup()
    
    try:
        success = setup.run_setup()
        setup.print_summary()
        
        if success:
            sys.exit(0)
        else:
            print("\n❌ Setup completed with errors. Please review and fix issues.")
            sys.exit(1)
    
    except KeyboardInterrupt:
        print("\n⚠️  Setup interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Unexpected error during setup: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()