#!/usr/bin/env python3
"""
Observatory Dependency Management - Requirements Generation Script

This script generates requirements.txt from pyproject.toml using pip-tools,
ensuring single source of truth for Python dependencies.

Usage:
    python scripts/generate_requirements.py [--upgrade] [--output requirements.txt]
"""

import argparse
import subprocess
import sys
from pathlib import Path
import toml


def validate_pyproject_exists():
    """Validate that pyproject.toml exists and is readable."""
    pyproject_path = Path("pyproject.toml")
    if not pyproject_path.exists():
        print("❌ pyproject.toml not found in current directory")
        sys.exit(1)
    
    try:
        with open(pyproject_path, 'r') as f:
            data = toml.load(f)
        
        if 'project' not in data or 'dependencies' not in data['project']:
            print("❌ pyproject.toml missing project.dependencies section")
            sys.exit(1)
            
        print(f"✅ Found {len(data['project']['dependencies'])} dependencies in pyproject.toml")
        return data
    except Exception as e:
        print(f"❌ Error reading pyproject.toml: {e}")
        sys.exit(1)


def check_pip_tools():
    """Check if pip-tools is installed."""
    try:
        result = subprocess.run(['pip-compile', '--version'], 
                              capture_output=True, text=True, check=True)
        print(f"✅ pip-tools available: {result.stdout.strip()}")
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("❌ pip-tools not found. Installing...")
        try:
            subprocess.run([sys.executable, '-m', 'pip', 'install', 'pip-tools'], 
                         check=True)
            print("✅ pip-tools installed successfully")
            return True
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to install pip-tools: {e}")
            return False


def generate_requirements(upgrade=False, output_file="requirements.txt"):
    """Generate requirements.txt from pyproject.toml using pip-compile."""
    cmd = [
        'pip-compile',
        'pyproject.toml',
        '-o', output_file,
        '--resolver=backtracking',
        '--no-header'  # Don't include pip-tools header
    ]
    
    if upgrade:
        cmd.append('--upgrade')
        print("🔄 Upgrading all dependencies to latest versions...")
    else:
        print("📦 Generating requirements.txt from pyproject.toml...")
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        
        # Add custom header to requirements.txt
        with open(output_file, 'r') as f:
            content = f.read()
        
        header = """# This file is auto-generated from pyproject.toml by scripts/generate_requirements.py
# DO NOT EDIT MANUALLY - Run 'make requirements' to regenerate
#
# To upgrade dependencies: make requirements-upgrade
# To validate sync: make requirements-check
#
"""
        
        with open(output_file, 'w') as f:
            f.write(header + content)
        
        print(f"✅ {output_file} generated successfully")
        
        # Count dependencies
        lines = [line.strip() for line in content.split('\n') 
                if line.strip() and not line.startswith('#')]
        print(f"📊 Generated {len(lines)} pinned dependencies")
        
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ pip-compile failed: {e}")
        if e.stderr:
            print(f"Error output: {e.stderr}")
        return False


def validate_critical_dependencies(requirements_file="requirements.txt"):
    """Validate that critical ML dependencies are present."""
    critical_deps = ['numpy', 'scikit-learn', 'pandas', 'scipy']
    
    try:
        with open(requirements_file, 'r') as f:
            content = f.read().lower()
        
        missing = []
        for dep in critical_deps:
            # Check for various forms: numpy==, numpy>=, scikit-learn==, etc.
            if dep.lower() not in content and dep.replace('-', '_').lower() not in content:
                missing.append(dep)
        
        if missing:
            print(f"⚠️  Critical dependencies missing from {requirements_file}:")
            for dep in missing:
                print(f"   - {dep}")
            print("   Add these to pyproject.toml dependencies and regenerate")
            return False
        else:
            print(f"✅ All critical ML dependencies present in {requirements_file}")
            return True
            
    except FileNotFoundError:
        print(f"❌ {requirements_file} not found")
        return False


def main():
    parser = argparse.ArgumentParser(description='Generate requirements.txt from pyproject.toml')
    parser.add_argument('--upgrade', action='store_true', 
                       help='Upgrade all dependencies to latest versions')
    parser.add_argument('--output', default='requirements.txt',
                       help='Output file path (default: requirements.txt)')
    parser.add_argument('--validate-only', action='store_true',
                       help='Only validate critical dependencies, do not generate')
    
    args = parser.parse_args()
    
    print("🔍 Observatory Dependency Management")
    print("=" * 50)
    
    # Validate pyproject.toml
    pyproject_data = validate_pyproject_exists()
    
    if args.validate_only:
        success = validate_critical_dependencies(args.output)
        sys.exit(0 if success else 1)
    
    # Check pip-tools
    if not check_pip_tools():
        sys.exit(1)
    
    # Generate requirements
    success = generate_requirements(upgrade=args.upgrade, output_file=args.output)
    if not success:
        sys.exit(1)
    
    # Validate critical dependencies
    validate_critical_dependencies(args.output)
    
    print("\n🎉 Dependency management completed successfully!")
    print(f"📄 Generated: {args.output}")
    print("🔧 Next steps:")
    print("   - Review the generated requirements.txt")
    print("   - Test with: docker-compose build observatory")
    print("   - Commit changes: git add pyproject.toml requirements.txt")


if __name__ == "__main__":
    main()