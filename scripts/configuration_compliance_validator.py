#!/usr/bin/env python3
"""
Configuration Compliance Validator

This script validates that all configuration in the repository follows
secure practices by using environment variables or example templates.
"""

import os
import re
import json
import yaml
from pathlib import Path
from typing import List, Dict, Set, Optional
from dataclasses import dataclass, field

@dataclass
class ConfigurationIssue:
    """Represents a configuration compliance issue"""
    file_path: str
    line_number: int
    line_content: str
    issue_description: str
    suggested_fix: str
    severity: str

@dataclass
class ConfigurationReport:
    """Configuration compliance report"""
    total_config_files: int = 0
    compliant_files: Set[str] = field(default_factory=set)
    non_compliant_files: Set[str] = field(default_factory=set)
    issues: List[ConfigurationIssue] = field(default_factory=list)
    
    def add_issue(self, issue: ConfigurationIssue):
        """Add a configuration issue"""
        self.issues.append(issue)
        self.non_compliant_files.add(issue.file_path)

class ConfigurationComplianceValidator:
    """Validates configuration compliance across the repository"""
    
    def __init__(self, root_path: str = "."):
        self.root_path = Path(root_path)
        self.report = ConfigurationReport()
        
        # Configuration file patterns
        self.config_patterns = [
            r'.*\.env$',
            r'.*\.env\..*$',
            r'.*config.*\.py$',
            r'.*config.*\.json$',
            r'.*config.*\.yaml$',
            r'.*config.*\.yml$',
            r'docker-compose.*\.yml$',
            r'Dockerfile.*$',
        ]
        
        # Patterns that indicate secure configuration
        self.secure_patterns = [
            r'os\.getenv\(',
            r'os\.environ\[',
            r'env\.',
            r'\$\{[A-Z_]+\}',  # Environment variable substitution
            r'example',  # Example files are OK
            r'template',  # Template files are OK
        ]
        
        # Patterns that indicate insecure configuration
        self.insecure_patterns = [
            (r'password\s*[:=]\s*["\'][^"\'$\{]+["\']', "Hardcoded password in configuration"),
            (r'secret\s*[:=]\s*["\'][^"\'$\{]+["\']', "Hardcoded secret in configuration"),
            (r'key\s*[:=]\s*["\'][^"\'$\{]+["\']', "Hardcoded key in configuration"),
            (r'token\s*[:=]\s*["\'][^"\'$\{]+["\']', "Hardcoded token in configuration"),
            (r'api_key\s*[:=]\s*["\'][^"\'$\{]+["\']', "Hardcoded API key in configuration"),
        ]
    
    def is_config_file(self, file_path: Path) -> bool:
        """Check if a file is a configuration file"""
        file_str = str(file_path).lower()
        return any(re.search(pattern, file_str) for pattern in self.config_patterns)
    
    def is_example_or_template(self, file_path: Path) -> bool:
        """Check if a file is an example or template file"""
        file_str = str(file_path).lower()
        return 'example' in file_str or 'template' in file_str
    
    def validate_file(self, file_path: Path) -> List[ConfigurationIssue]:
        """Validate a single configuration file"""
        issues = []
        
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                lines = f.readlines()
        except Exception as e:
            return issues
        
        is_example = self.is_example_or_template(file_path)
        
        for line_num, line in enumerate(lines, 1):
            line_content = line.strip()
            
            if not line_content or line_content.startswith('#'):
                continue
            
            # Check for insecure patterns (unless it's an example file)
            if not is_example:
                for pattern, description in self.insecure_patterns:
                    if re.search(pattern, line_content, re.IGNORECASE):
                        # Check if the line also contains secure patterns
                        has_secure_pattern = any(
                            re.search(secure_pattern, line_content, re.IGNORECASE)
                            for secure_pattern in self.secure_patterns
                        )
                        
                        if not has_secure_pattern:
                            issues.append(ConfigurationIssue(
                                file_path=str(file_path),
                                line_number=line_num,
                                line_content=line_content,
                                issue_description=description,
                                suggested_fix="Use environment variable or move to .env.example",
                                severity="HIGH"
                            ))
        
        return issues
    
    def validate_environment_variable_usage(self) -> List[ConfigurationIssue]:
        """Validate that environment variables are properly used throughout the codebase"""
        issues = []
        
        # Check Python files for proper environment variable usage
        for py_file in self.root_path.rglob('*.py'):
            if '.git' in str(py_file) or '__pycache__' in str(py_file):
                continue
            
            try:
                with open(py_file, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                    lines = content.split('\n')
            except Exception:
                continue
            
            # Look for environment variable usage without validation
            for line_num, line in enumerate(lines, 1):
                line_content = line.strip()
                
                # Check for os.getenv without validation
                getenv_match = re.search(r'os\.getenv\(["\']([^"\']+)["\'](?:,\s*["\'][^"\']*["\'])?\)', line_content)
                if getenv_match:
                    var_name = getenv_match.group(1)
                    
                    # Look for validation in the next few lines
                    validation_found = False
                    for check_line_num in range(line_num, min(line_num + 5, len(lines))):
                        check_line = lines[check_line_num - 1] if check_line_num <= len(lines) else ""
                        if any(keyword in check_line.lower() for keyword in ['if not', 'raise', 'assert', 'required']):
                            validation_found = True
                            break
                    
                    if not validation_found and 'password' in var_name.lower() or 'key' in var_name.lower() or 'secret' in var_name.lower():
                        issues.append(ConfigurationIssue(
                            file_path=str(py_file),
                            line_number=line_num,
                            line_content=line_content,
                            issue_description=f"Environment variable {var_name} used without validation",
                            suggested_fix="Add validation to ensure required environment variables are set",
                            severity="MEDIUM"
                        ))
        
        return issues
    
    def validate_repository(self) -> ConfigurationReport:
        """Validate configuration compliance across the repository"""
        print("Validating configuration compliance...")
        
        # Find and validate all configuration files
        for file_path in self.root_path.rglob('*'):
            if file_path.is_file() and self.is_config_file(file_path):
                self.report.total_config_files += 1
                
                issues = self.validate_file(file_path)
                
                if issues:
                    for issue in issues:
                        self.report.add_issue(issue)
                else:
                    self.report.compliant_files.add(str(file_path))
        
        # Validate environment variable usage
        env_var_issues = self.validate_environment_variable_usage()
        for issue in env_var_issues:
            self.report.add_issue(issue)
        
        print(f"Configuration validation complete.")
        print(f"Scanned {self.report.total_config_files} configuration files.")
        print(f"Found {len(self.report.issues)} configuration issues.")
        
        return self.report
    
    def generate_report(self) -> Dict:
        """Generate configuration compliance report"""
        return {
            "summary": {
                "total_config_files": self.report.total_config_files,
                "compliant_files": len(self.report.compliant_files),
                "non_compliant_files": len(self.report.non_compliant_files),
                "total_issues": len(self.report.issues),
                "compliance_rate": len(self.report.compliant_files) / self.report.total_config_files * 100 if self.report.total_config_files > 0 else 0
            },
            "issues": [
                {
                    "file": issue.file_path,
                    "line": issue.line_number,
                    "content": issue.line_content,
                    "description": issue.issue_description,
                    "fix": issue.suggested_fix,
                    "severity": issue.severity
                }
                for issue in self.report.issues
            ],
            "compliant_files": sorted(list(self.report.compliant_files)),
            "non_compliant_files": sorted(list(self.report.non_compliant_files))
        }
    
    def print_report(self):
        """Print human-readable configuration compliance report"""
        print("\n" + "="*80)
        print("CONFIGURATION COMPLIANCE VALIDATION REPORT")
        print("="*80)
        
        print(f"\nSUMMARY:")
        print(f"  Configuration Files Scanned: {self.report.total_config_files}")
        print(f"  Compliant Files: {len(self.report.compliant_files)}")
        print(f"  Non-Compliant Files: {len(self.report.non_compliant_files)}")
        print(f"  Total Issues: {len(self.report.issues)}")
        
        compliance_rate = len(self.report.compliant_files) / self.report.total_config_files * 100 if self.report.total_config_files > 0 else 0
        print(f"  Compliance Rate: {compliance_rate:.1f}%")
        
        # Print issues by severity
        high_issues = [issue for issue in self.report.issues if issue.severity == "HIGH"]
        medium_issues = [issue for issue in self.report.issues if issue.severity == "MEDIUM"]
        
        if high_issues:
            print(f"\n🚨 HIGH SEVERITY ISSUES:")
            for issue in high_issues:
                print(f"  ❌ {issue.file_path}:{issue.line_number}")
                print(f"     {issue.issue_description}")
                print(f"     Line: {issue.line_content}")
                print(f"     Fix: {issue.suggested_fix}")
                print()
        
        if medium_issues:
            print(f"\n⚠️  MEDIUM SEVERITY ISSUES:")
            for issue in medium_issues:
                print(f"  ⚠️  {issue.file_path}:{issue.line_number}")
                print(f"     {issue.issue_description}")
                print(f"     Fix: {issue.suggested_fix}")
                print()
        
        # Configuration compliance status
        if high_issues:
            print(f"\n❌ CONFIGURATION COMPLIANCE: FAILED")
            print(f"   Found {len(high_issues)} high severity configuration issues.")
        else:
            print(f"\n✅ CONFIGURATION COMPLIANCE: PASSED")
            print(f"   All configuration files follow secure practices.")
        
        print("\n" + "="*80)

def main():
    """Main function to run configuration compliance validation"""
    validator = ConfigurationComplianceValidator()
    
    # Perform validation
    report = validator.validate_repository()
    
    # Print human-readable report
    validator.print_report()
    
    # Save detailed report
    report_data = validator.generate_report()
    report_file = Path("data/configuration_compliance_report.json")
    report_file.parent.mkdir(exist_ok=True)
    
    with open(report_file, 'w') as f:
        json.dump(report_data, f, indent=2)
    
    print(f"\nDetailed report saved to: {report_file}")
    
    # Return appropriate exit code
    high_issues = [issue for issue in report.issues if issue.severity == "HIGH"]
    if high_issues:
        print(f"\n🚨 CONFIGURATION COMPLIANCE FAILED")
        return 1
    else:
        print(f"\n✅ CONFIGURATION COMPLIANCE PASSED")
        return 0

if __name__ == "__main__":
    exit(main())