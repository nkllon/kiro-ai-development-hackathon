#!/usr/bin/env python3
"""
Observatory Dependency Governance - Security Validation Script

This script validates that the Observatory dependency governance system
is properly implemented and secure.
"""

import os
import sys
import subprocess
from pathlib import Path
import json
from typing import Dict, List, Any


def check_file_exists(filepath: str, description: str) -> bool:
    """Check if a required file exists."""
    if Path(filepath).exists():
        print(f"✅ {description}: {filepath}")
        return True
    else:
        print(f"❌ {description} missing: {filepath}")
        return False


def check_executable(filepath: str, description: str) -> bool:
    """Check if a file exists and is executable."""
    path = Path(filepath)
    if path.exists() and os.access(path, os.X_OK):
        print(f"✅ {description} executable: {filepath}")
        return True
    else:
        print(f"❌ {description} not executable: {filepath}")
        return False


def run_command(cmd: List[str], description: str) -> Dict[str, Any]:
    """Run a command and return results."""
    try:
        result = subprocess.run(
            cmd, capture_output=True, text=True, timeout=30
        )
        success = result.returncode == 0
        print(f"{'✅' if success else '❌'} {description}: {'PASSED' if success else 'FAILED'}")
        
        if not success and result.stderr:
            print(f"   Error: {result.stderr.strip()}")
        
        return {
            "success": success,
            "stdout": result.stdout,
            "stderr": result.stderr,
            "returncode": result.returncode
        }
    except subprocess.TimeoutExpired:
        print(f"❌ {description}: TIMEOUT")
        return {"success": False, "error": "timeout"}
    except Exception as e:
        print(f"❌ {description}: ERROR - {e}")
        return {"success": False, "error": str(e)}


def validate_governance_files() -> bool:
    """Validate that all governance files are present."""
    print("\n🔍 Validating Governance Files")
    print("=" * 50)
    
    files_to_check = [
        (".kiro/specs/observatory-dependency-governance/requirements.md", "Requirements specification"),
        (".kiro/specs/observatory-dependency-governance/design.md", "Design document"),
        (".kiro/specs/observatory-dependency-governance/tasks.md", "Tasks document"),
        ("scripts/generate_requirements.py", "Requirements generation script"),
        (".pre-commit-hooks/validate-dependencies.sh", "Validation hook"),
        ("docs/development/DEPENDENCY-MANAGEMENT.md", "Process documentation"),
        (".github/workflows/validate-dependencies.yml", "CI/CD workflow"),
    ]
    
    all_present = True
    for filepath, description in files_to_check:
        if not check_file_exists(filepath, description):
            all_present = False
    
    return all_present


def validate_executables() -> bool:
    """Validate that scripts are executable."""
    print("\n🔧 Validating Executable Scripts")
    print("=" * 50)
    
    executables = [
        ("scripts/generate_requirements.py", "Requirements generation script"),
        (".pre-commit-hooks/validate-dependencies.sh", "Validation hook"),
    ]
    
    all_executable = True
    for filepath, description in executables:
        if not check_executable(filepath, description):
            all_executable = False
    
    return all_executable


def validate_makefile_targets() -> bool:
    """Validate that Makefile targets exist and work."""
    print("\n🎯 Validating Makefile Targets")
    print("=" * 50)
    
    # Check that targets exist in Makefile
    makefile_content = ""
    try:
        with open("Makefile", "r") as f:
            makefile_content = f.read()
    except FileNotFoundError:
        print("❌ Makefile not found")
        return False
    
    required_targets = [
        "requirements:",
        "requirements-check:",
        "requirements-upgrade:",
        "requirements-validate:",
    ]
    
    targets_present = True
    for target in required_targets:
        if target in makefile_content:
            print(f"✅ Makefile target found: {target}")
        else:
            print(f"❌ Makefile target missing: {target}")
            targets_present = False
    
    return targets_present


def validate_dependency_tools() -> bool:
    """Validate that dependency management tools work."""
    print("\n🛠️ Validating Dependency Management Tools")
    print("=" * 50)
    
    tests = [
        (["python", "scripts/generate_requirements.py", "--help"], "Requirements script help"),
        (["python", "scripts/generate_requirements.py", "--validate-only"], "Critical dependency validation"),
        ([".pre-commit-hooks/validate-dependencies.sh"], "Dependency sync validation"),
    ]
    
    all_working = True
    for cmd, description in tests:
        result = run_command(cmd, description)
        if not result["success"]:
            all_working = False
    
    return all_working


def validate_pyproject_toml() -> bool:
    """Validate pyproject.toml has required dependencies."""
    print("\n📦 Validating pyproject.toml Dependencies")
    print("=" * 50)
    
    try:
        import toml
        with open("pyproject.toml", "r") as f:
            data = toml.load(f)
        
        # Check main dependencies
        dependencies = data.get("project", {}).get("dependencies", [])
        critical_deps = ["numpy", "scikit-learn", "pandas", "scipy"]
        
        deps_present = True
        for dep in critical_deps:
            found = any(dep in d for d in dependencies)
            if found:
                print(f"✅ Critical dependency found: {dep}")
            else:
                print(f"❌ Critical dependency missing: {dep}")
                deps_present = False
        
        # Check dev dependencies
        dev_deps = data.get("project", {}).get("optional-dependencies", {}).get("dev", [])
        pip_tools_found = any("pip-tools" in d for d in dev_deps)
        
        if pip_tools_found:
            print("✅ pip-tools found in dev dependencies")
        else:
            print("❌ pip-tools missing from dev dependencies")
            deps_present = False
        
        return deps_present
        
    except Exception as e:
        print(f"❌ Error validating pyproject.toml: {e}")
        return False


def validate_requirements_txt() -> bool:
    """Validate requirements.txt is properly generated."""
    print("\n📄 Validating requirements.txt")
    print("=" * 50)
    
    if not Path("requirements.txt").exists():
        print("❌ requirements.txt not found")
        return False
    
    try:
        with open("requirements.txt", "r") as f:
            content = f.read()
        
        # Check for auto-generated header
        if "auto-generated from pyproject.toml" in content:
            print("✅ Auto-generated header found")
        else:
            print("❌ Auto-generated header missing")
            return False
        
        # Check for critical dependencies
        critical_deps = ["numpy", "scikit-learn", "pandas", "scipy"]
        deps_found = True
        
        for dep in critical_deps:
            if dep in content.lower():
                print(f"✅ Critical dependency in requirements.txt: {dep}")
            else:
                print(f"❌ Critical dependency missing from requirements.txt: {dep}")
                deps_found = False
        
        # Count total dependencies
        lines = [line.strip() for line in content.split('\n') 
                if line.strip() and not line.startswith('#')]
        print(f"📊 Total pinned dependencies: {len(lines)}")
        
        return deps_found
        
    except Exception as e:
        print(f"❌ Error validating requirements.txt: {e}")
        return False


def validate_docker_integration() -> bool:
    """Validate Docker integration."""
    print("\n🐳 Validating Docker Integration")
    print("=" * 50)
    
    dockerfile_path = "deployment/observatory/Dockerfile"
    if not Path(dockerfile_path).exists():
        print(f"❌ Dockerfile not found: {dockerfile_path}")
        return False
    
    try:
        with open(dockerfile_path, "r") as f:
            content = f.read()
        
        # Check for import validation
        if "import numpy" in content and "import sklearn" in content:
            print("✅ Docker import validation found")
        else:
            print("❌ Docker import validation missing")
            return False
        
        # Check for failure handling
        if "sys.exit(1)" in content:
            print("✅ Docker failure handling found")
        else:
            print("❌ Docker failure handling missing")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Error validating Dockerfile: {e}")
        return False


def validate_security_practices() -> bool:
    """Validate security practices are followed."""
    print("\n🔒 Validating Security Practices")
    print("=" * 50)
    
    security_checks = []
    
    # Check for hardcoded credentials
    sensitive_files = [
        "scripts/generate_requirements.py",
        ".pre-commit-hooks/validate-dependencies.sh",
        "pyproject.toml",
        "requirements.txt"
    ]
    
    hardcoded_patterns = ["password", "secret", "key", "token"]
    
    for filepath in sensitive_files:
        if Path(filepath).exists():
            try:
                with open(filepath, "r") as f:
                    content = f.read().lower()
                
                found_patterns = []
                for pattern in hardcoded_patterns:
                    if pattern in content:
                        # Check for actual assignment patterns, not package names
                        lines = content.split('\n')
                        for line in lines:
                            line_stripped = line.strip()
                            if (pattern in line and "=" in line and 
                                not line_stripped.startswith('#') and
                                not line_stripped.startswith(pattern) and  # Not a package name
                                ("password=" in line or "secret=" in line or "key=" in line or "token=" in line)):
                                found_patterns.append(pattern)
                
                if found_patterns:
                    print(f"⚠️  Potential hardcoded secrets in {filepath}: {found_patterns}")
                    security_checks.append(False)
                else:
                    print(f"✅ No hardcoded secrets found in {filepath}")
                    security_checks.append(True)
                    
            except Exception as e:
                print(f"❌ Error checking {filepath}: {e}")
                security_checks.append(False)
    
    return all(security_checks)


def generate_summary_report() -> Dict[str, Any]:
    """Generate a comprehensive summary report."""
    print("\n📊 Observatory Dependency Governance Validation Summary")
    print("=" * 60)
    
    validations = [
        ("Governance Files", validate_governance_files()),
        ("Executable Scripts", validate_executables()),
        ("Makefile Targets", validate_makefile_targets()),
        ("Dependency Tools", validate_dependency_tools()),
        ("pyproject.toml", validate_pyproject_toml()),
        ("requirements.txt", validate_requirements_txt()),
        ("Docker Integration", validate_docker_integration()),
        ("Security Practices", validate_security_practices()),
    ]
    
    passed = sum(1 for _, result in validations if result)
    total = len(validations)
    
    print(f"\n🎯 Overall Results: {passed}/{total} validations passed")
    
    if passed == total:
        print("🎉 All validations PASSED - Observatory Dependency Governance is ready!")
        status = "READY"
    else:
        print("⚠️  Some validations FAILED - Review and fix issues before deployment")
        status = "NEEDS_FIXES"
    
    return {
        "status": status,
        "passed": passed,
        "total": total,
        "validations": dict(validations)
    }


def main():
    """Main validation function."""
    print("🔍 Observatory Dependency Governance Security Validation")
    print("=" * 60)
    print("Validating implementation of permanent dependency management fixes...")
    
    # Run all validations
    report = generate_summary_report()
    
    # Save report
    report_file = "observatory_dependency_governance_validation_report.json"
    try:
        with open(report_file, "w") as f:
            json.dump(report, f, indent=2)
        print(f"\n📄 Detailed report saved to: {report_file}")
    except Exception as e:
        print(f"⚠️  Could not save report: {e}")
    
    # Exit with appropriate code
    if report["status"] == "READY":
        print("\n✅ Observatory Dependency Governance validation SUCCESSFUL")
        sys.exit(0)
    else:
        print("\n❌ Observatory Dependency Governance validation FAILED")
        sys.exit(1)


if __name__ == "__main__":
    main()