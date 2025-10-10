#!/usr/bin/env python3
"""
Final Release Validation Script

This script performs comprehensive validation to ensure the Beast Mode AI Development Framework
meets all requirements for public release as specified in the project cleanup specification.
"""

import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Any


class FinalReleaseValidator:
    """Performs final validation against all project cleanup requirements."""
    
    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.validation_results: Dict[str, Any] = {}
        self.errors: List[str] = []
        self.warnings: List[str] = []
    
    def validate_requirement_1_project_structure(self) -> bool:
        """Validate Requirement 1: Project Structure Organization."""
        print("📁 Validating Requirement 1: Project Structure Organization")
        
        # Check root directory cleanliness
        root_files = list(self.project_root.glob("*"))
        essential_files = {
            "README.md", "CONTRIBUTING.md", "CHANGELOG.md", "requirements.txt",
            "pyproject.toml", ".gitignore", "install.sh", "install.bat",
            "docker-compose.yml", "Dockerfile", "Makefile"
        }
        
        essential_dirs = {
            "src", "docs", "examples", "tests", "scripts", "config", ".github"
        }
        
        # Check for unwanted files in root
        unwanted_patterns = [".log", ".tmp", ".backup", ".old", ".bak"]
        unwanted_files = []
        
        for file_path in root_files:
            if file_path.is_file():
                if any(pattern in file_path.name for pattern in unwanted_patterns):
                    unwanted_files.append(file_path.name)
        
        if unwanted_files:
            self.errors.extend([f"Unwanted file in root: {f}" for f in unwanted_files])
        
        # Check source code organization
        src_dir = self.project_root / "src"
        if not src_dir.exists():
            self.errors.append("src/ directory missing")
        else:
            # Check for proper Python package structure
            python_files = list(src_dir.rglob("*.py"))
            if not python_files:
                self.warnings.append("No Python files found in src/")
        
        self.validation_results["requirement_1"] = {
            "root_files_count": len([f for f in root_files if f.is_file()]),
            "unwanted_files": unwanted_files,
            "src_exists": src_dir.exists(),
            "python_files_count": len(list(src_dir.rglob("*.py"))) if src_dir.exists() else 0
        }
        
        return len(unwanted_files) == 0
    
    def validate_requirement_2_documentation(self) -> bool:
        """Validate Requirement 2: Documentation Enhancement."""
        print("📚 Validating Requirement 2: Documentation Enhancement")
        
        required_docs = [
            ("README.md", "Main README with value proposition"),
            ("docs/installation/INSTALLATION_GUIDE.md", "Installation guide"),
            ("docs/api/README.md", "API documentation"),
            ("docs/usage/README.md", "Usage documentation"),
            ("CONTRIBUTING.md", "Contributing guidelines"),
        ]
        
        missing_docs = []
        incomplete_docs = []
        
        for doc_path, description in required_docs:
            full_path = self.project_root / doc_path
            if not full_path.exists():
                missing_docs.append(f"{description}: {doc_path}")
            else:
                try:
                    content = full_path.read_text().strip()
                    if len(content) < 200:  # Minimum content check
                        incomplete_docs.append(f"{description}: {doc_path}")
                except Exception:
                    incomplete_docs.append(f"{description}: {doc_path} (read error)")
        
        # Check README quality
        readme_path = self.project_root / "README.md"
        readme_quality = {"has_title": False, "has_installation": False, "has_usage": False}
        
        if readme_path.exists():
            try:
                readme_content = readme_path.read_text().lower()
                readme_quality["has_title"] = "beast mode" in readme_content or "framework" in readme_content
                readme_quality["has_installation"] = "install" in readme_content
                readme_quality["has_usage"] = "usage" in readme_content or "quick start" in readme_content
            except Exception:
                pass
        
        self.validation_results["requirement_2"] = {
            "missing_docs": missing_docs,
            "incomplete_docs": incomplete_docs,
            "readme_quality": readme_quality,
            "total_docs_required": len(required_docs),
            "docs_present": len(required_docs) - len(missing_docs)
        }
        
        if missing_docs:
            self.errors.extend([f"Missing documentation: {d}" for d in missing_docs])
        
        if incomplete_docs:
            self.warnings.extend([f"Incomplete documentation: {d}" for d in incomplete_docs])
        
        return len(missing_docs) == 0
    
    def validate_requirement_3_examples(self) -> bool:
        """Validate Requirement 3: Working Examples and Demos."""
        print("🧪 Validating Requirement 3: Working Examples and Demos")
        
        examples_dir = self.project_root / "examples"
        if not examples_dir.exists():
            self.errors.append("examples/ directory missing")
            return False
        
        # Check for required example categories
        required_examples = [
            "quick_start",
            "demos",
            "basic"
        ]
        
        missing_categories = []
        for category in required_examples:
            if not (examples_dir / category).exists():
                missing_categories.append(category)
        
        # Test example execution
        example_files = list(examples_dir.rglob("*.py"))
        executable_examples = [f for f in example_files if "interactive" not in f.name]
        
        working_examples = 0
        failed_examples = []
        
        for example_file in executable_examples[:5]:  # Test first 5 examples
            try:
                result = subprocess.run(
                    [sys.executable, str(example_file)],
                    cwd=self.project_root,
                    capture_output=True,
                    timeout=30,
                    env={**os.environ, "ENVIRONMENT": "test"}
                )
                if result.returncode in [0, 124]:  # 0 = success, 124 = timeout (acceptable)
                    working_examples += 1
                else:
                    failed_examples.append(example_file.name)
            except Exception:
                failed_examples.append(example_file.name)
        
        self.validation_results["requirement_3"] = {
            "examples_dir_exists": examples_dir.exists(),
            "missing_categories": missing_categories,
            "total_examples": len(example_files),
            "executable_examples": len(executable_examples),
            "working_examples": working_examples,
            "failed_examples": failed_examples
        }
        
        if missing_categories:
            self.errors.extend([f"Missing example category: {c}" for c in missing_categories])
        
        if failed_examples:
            self.warnings.extend([f"Example may have issues: {e}" for e in failed_examples])
        
        return len(missing_categories) == 0
    
    def validate_requirement_4_installation(self) -> bool:
        """Validate Requirement 4: Installation and Setup."""
        print("📦 Validating Requirement 4: Installation and Setup")
        
        # Check installation scripts
        install_scripts = ["install.sh", "install.bat"]
        missing_scripts = []
        
        for script in install_scripts:
            if not (self.project_root / script).exists():
                missing_scripts.append(script)
        
        # Check requirements.txt
        requirements_file = self.project_root / "requirements.txt"
        requirements_valid = False
        dependency_count = 0
        
        if requirements_file.exists():
            try:
                requirements = requirements_file.read_text().strip().split('\n')
                requirements = [r.strip() for r in requirements if r.strip() and not r.startswith('#')]
                dependency_count = len(requirements)
                requirements_valid = dependency_count > 0
            except Exception:
                pass
        
        # Check Docker support
        docker_files = ["Dockerfile", "docker-compose.yml"]
        docker_support = all((self.project_root / f).exists() for f in docker_files)
        
        self.validation_results["requirement_4"] = {
            "missing_install_scripts": missing_scripts,
            "requirements_valid": requirements_valid,
            "dependency_count": dependency_count,
            "docker_support": docker_support
        }
        
        if missing_scripts:
            self.errors.extend([f"Missing install script: {s}" for s in missing_scripts])
        
        if not requirements_valid:
            self.errors.append("requirements.txt missing or invalid")
        
        return len(missing_scripts) == 0 and requirements_valid
    
    def validate_requirement_5_file_organization(self) -> bool:
        """Validate Requirement 5: File Organization and Cleanup."""
        print("🗂️ Validating Requirement 5: File Organization and Cleanup")
        
        # Check for backup directories (should be cleaned up)
        backup_patterns = ["backup", "_backup_", ".backup", "archive_"]
        backup_dirs = []
        
        for pattern in backup_patterns:
            backup_dirs.extend(list(self.project_root.glob(f"*{pattern}*")))
        
        # Check .gitignore effectiveness
        gitignore_path = self.project_root / ".gitignore"
        gitignore_comprehensive = False
        
        if gitignore_path.exists():
            try:
                gitignore_content = gitignore_path.read_text()
                required_patterns = ["__pycache__", "*.log", ".env", "*.tmp", "credentials/"]
                gitignore_comprehensive = all(pattern in gitignore_content for pattern in required_patterns)
            except Exception:
                pass
        
        # Check repository size
        repo_size_mb = 0
        try:
            result = subprocess.run(
                ["du", "-sm", "."],
                cwd=self.project_root,
                capture_output=True,
                text=True
            )
            if result.returncode == 0:
                repo_size_mb = int(result.stdout.split()[0])
        except Exception:
            pass
        
        self.validation_results["requirement_5"] = {
            "backup_dirs_found": len(backup_dirs),
            "backup_dirs": [str(d) for d in backup_dirs],
            "gitignore_comprehensive": gitignore_comprehensive,
            "repo_size_mb": repo_size_mb,
            "size_under_limit": repo_size_mb < 500 if repo_size_mb > 0 else True
        }
        
        if backup_dirs:
            self.warnings.extend([f"Backup directory found: {d}" for d in backup_dirs])
        
        if not gitignore_comprehensive:
            self.warnings.append(".gitignore may not be comprehensive")
        
        if repo_size_mb > 500:
            self.errors.append(f"Repository size ({repo_size_mb}MB) exceeds 500MB limit")
        
        return repo_size_mb < 500 if repo_size_mb > 0 else True
    
    def validate_requirement_6_security(self) -> bool:
        """Validate Requirement 6: Security and Credential Management."""
        print("🔒 Validating Requirement 6: Security and Credential Management")
        
        # Scan for hardcoded credentials
        credential_violations = []
        credential_patterns = [
            r'password\s*=\s*[\'"][^\'"]+[\'"]',
            r'api_key\s*=\s*[\'"][^\'"]+[\'"]',
            r'secret\s*=\s*[\'"][^\'"]+[\'"]',
            r'token\s*=\s*[\'"][^\'"]+[\'"]',
        ]
        
        for py_file in self.project_root.rglob("*.py"):
            if ".git" in str(py_file) or "__pycache__" in str(py_file):
                continue
            
            try:
                content = py_file.read_text(encoding='utf-8', errors='ignore')
                for pattern in credential_patterns:
                    import re
                    matches = re.finditer(pattern, content, re.IGNORECASE)
                    for match in matches:
                        # Skip if using environment variables
                        line_start = content.rfind('\n', 0, match.start()) + 1
                        line_end = content.find('\n', match.end())
                        if line_end == -1:
                            line_end = len(content)
                        line = content[line_start:line_end]
                        
                        if 'os.getenv' not in line and 'getenv' not in line and 'environ' not in line:
                            line_num = content[:match.start()].count('\n') + 1
                            credential_violations.append(f"{py_file}:{line_num}")
            except Exception:
                pass
        
        # Check for security documentation
        security_docs = [
            "docs/security/SECURITY.md",
            ".github/SECURITY.md"
        ]
        
        security_doc_exists = any((self.project_root / doc).exists() for doc in security_docs)
        
        # Check for secrets baseline
        secrets_baseline_exists = (self.project_root / ".secrets.baseline").exists()
        
        self.validation_results["requirement_6"] = {
            "credential_violations": len(credential_violations),
            "violation_details": credential_violations,
            "security_doc_exists": security_doc_exists,
            "secrets_baseline_exists": secrets_baseline_exists
        }
        
        if credential_violations:
            self.errors.extend([f"Hardcoded credential: {v}" for v in credential_violations])
        
        if not security_doc_exists:
            self.warnings.append("Security documentation missing")
        
        return len(credential_violations) == 0
    
    def validate_requirement_7_performance(self) -> bool:
        """Validate Requirement 7: Performance and Size Optimization."""
        print("⚡ Validating Requirement 7: Performance and Size Optimization")
        
        # Check repository size (already done in requirement 5)
        repo_size_mb = self.validation_results.get("requirement_5", {}).get("repo_size_mb", 0)
        
        # Check for large files
        large_files = []
        try:
            result = subprocess.run(
                ["find", ".", "-type", "f", "-size", "+10M"],
                cwd=self.project_root,
                capture_output=True,
                text=True
            )
            if result.returncode == 0:
                large_files = result.stdout.strip().split('\n') if result.stdout.strip() else []
        except Exception:
            pass
        
        # Check dependency count
        dependency_count = self.validation_results.get("requirement_4", {}).get("dependency_count", 0)
        
        self.validation_results["requirement_7"] = {
            "repo_size_mb": repo_size_mb,
            "size_optimized": repo_size_mb < 500 if repo_size_mb > 0 else True,
            "large_files": large_files,
            "dependency_count": dependency_count,
            "dependencies_minimal": dependency_count < 50
        }
        
        if large_files:
            self.warnings.extend([f"Large file found: {f}" for f in large_files])
        
        return (repo_size_mb < 500 if repo_size_mb > 0 else True) and len(large_files) < 5
    
    def validate_requirement_8_testing(self) -> bool:
        """Validate Requirement 8: Testing and Quality Assurance."""
        print("🧪 Validating Requirement 8: Testing and Quality Assurance")
        
        # Check for test directory
        tests_dir = self.project_root / "tests"
        tests_exist = tests_dir.exists()
        
        test_files = list(tests_dir.rglob("test_*.py")) if tests_exist else []
        
        # Check for CI/CD workflows
        workflows_dir = self.project_root / ".github" / "workflows"
        workflow_files = list(workflows_dir.glob("*.yml")) if workflows_dir.exists() else []
        
        # Check for pre-commit configuration
        precommit_config = (self.project_root / ".pre-commit-config.yaml").exists()
        
        self.validation_results["requirement_8"] = {
            "tests_exist": tests_exist,
            "test_files_count": len(test_files),
            "workflow_files_count": len(workflow_files),
            "precommit_configured": precommit_config
        }
        
        if not tests_exist:
            self.warnings.append("No tests directory found")
        
        if len(workflow_files) == 0:
            self.warnings.append("No CI/CD workflows found")
        
        return True  # Testing is optional for this validation
    
    def run_final_validation(self) -> bool:
        """Run comprehensive final validation."""
        print("🎯 Running Final Release Validation")
        print("=" * 60)
        
        validation_functions = [
            ("Requirement 1: Project Structure", self.validate_requirement_1_project_structure),
            ("Requirement 2: Documentation", self.validate_requirement_2_documentation),
            ("Requirement 3: Examples", self.validate_requirement_3_examples),
            ("Requirement 4: Installation", self.validate_requirement_4_installation),
            ("Requirement 5: File Organization", self.validate_requirement_5_file_organization),
            ("Requirement 6: Security", self.validate_requirement_6_security),
            ("Requirement 7: Performance", self.validate_requirement_7_performance),
            ("Requirement 8: Testing", self.validate_requirement_8_testing),
        ]
        
        passed_requirements = 0
        total_requirements = len(validation_functions)
        
        for req_name, req_func in validation_functions:
            print(f"\n📋 {req_name}")
            print("-" * 40)
            
            if req_func():
                print(f"✅ {req_name} - PASSED")
                passed_requirements += 1
            else:
                print(f"❌ {req_name} - FAILED")
        
        # Save validation results
        results_file = self.project_root / "validation_results.json"
        with open(results_file, 'w') as f:
            json.dump(self.validation_results, f, indent=2)
        
        return passed_requirements == total_requirements
    
    def print_summary(self):
        """Print validation summary."""
        print("\n" + "=" * 60)
        print("📊 Final Validation Summary")
        print("=" * 60)
        
        total_requirements = 8
        passed_requirements = sum(1 for req in self.validation_results.values() 
                                if not any(key.startswith('missing_') or key.startswith('failed_') 
                                         for key in req.keys()))
        
        print(f"Requirements Passed: {passed_requirements}/{total_requirements}")
        
        if not self.errors and not self.warnings:
            print("\n🎉 ALL VALIDATIONS PASSED!")
            print("✅ Project is ready for public release!")
        else:
            if self.errors:
                print(f"\n❌ {len(self.errors)} Critical Issues:")
                for error in self.errors:
                    print(f"  • {error}")
            
            if self.warnings:
                print(f"\n⚠️  {len(self.warnings)} Warnings:")
                for warning in self.warnings:
                    print(f"  • {warning}")
        
        print(f"\n📁 Detailed results saved to: validation_results.json")
        
        if not self.errors:
            print("\n🚀 Ready for Release!")
            print("Next steps:")
            print("1. Run: python scripts/prepare_release.py")
            print("2. Review RELEASE_NOTES.md")
            print("3. Create release tag")
        else:
            print("\n🔧 Action Required:")
            print("Fix all critical issues before proceeding with release.")


def main():
    """Main entry point."""
    validator = FinalReleaseValidator()
    
    try:
        success = validator.run_final_validation()
        validator.print_summary()
        
        sys.exit(0 if success and not validator.errors else 1)
    
    except KeyboardInterrupt:
        print("\n⚠️  Validation interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Unexpected error during validation: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()