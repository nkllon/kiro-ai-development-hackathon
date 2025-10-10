#!/usr/bin/env python3
"""
Focused Security Validation Script
Validates security compliance for main project directories only (excludes archives)
"""

import os
import re
import json
from pathlib import Path
from typing import List, Dict, Any
from dataclasses import dataclass

@dataclass
class SecurityIssue:
    file_path: str
    line_number: int
    line_content: str
    issue_type: str
    severity: str
    description: str

class FocusedSecurityValidator:
    def __init__(self):
        self.project_root = Path(".")
        self.issues = []
        
        # Focus on main project directories only
        self.scan_directories = [
            "src/",
            "scripts/",
            "examples/",
            "docs/",
            "tests/",
            ".kiro/",
            "deployment/",
            "config/"
        ]
        
        # Exclude archived and development directories
        self.exclude_patterns = [
            "archive/",
            "vonnegut_deployment_package/",
            "scripts-archive/",
            "__pycache__/",
            ".git/",
            "node_modules/",
            ".venv/",
            "*.pyc"
        ]
        
        # High-severity patterns to detect
        self.high_severity_patterns = {
            'password': [
                r'password\s*=\s*["\'][^"\']{3,}["\']',
                r'PASSWORD\s*=\s*["\'][^"\']{3,}["\']',
                r'pwd\s*=\s*["\'][^"\']{3,}["\']'
            ],
            'api_key': [
                r'api_key\s*=\s*["\'][^"\']{10,}["\']',
                r'API_KEY\s*=\s*["\'][^"\']{10,}["\']',
                r'apikey\s*=\s*["\'][^"\']{10,}["\']'
            ],
            'token': [
                r'token\s*=\s*["\'][^"\']{10,}["\']',
                r'TOKEN\s*=\s*["\'][^"\']{10,}["\']',
                r'auth_token\s*=\s*["\'][^"\']{10,}["\']'
            ],
            'secret': [
                r'secret\s*=\s*["\'][^"\']{8,}["\']',
                r'SECRET\s*=\s*["\'][^"\']{8,}["\']',
                r'client_secret\s*=\s*["\'][^"\']{8,}["\']'
            ],
            'database_url': [
                r'postgresql://[^:]+:[^@]+@[^/]+/\w+',
                r'mysql://[^:]+:[^@]+@[^/]+/\w+',
                r'mongodb://[^:]+:[^@]+@[^/]+/\w+'
            ]
        }

    def should_exclude_file(self, file_path: str) -> bool:
        """Check if file should be excluded from scanning"""
        for pattern in self.exclude_patterns:
            if pattern in file_path:
                return True
        return False

    def scan_file(self, file_path: Path) -> List[SecurityIssue]:
        """Scan a single file for security issues"""
        issues = []
        
        if self.should_exclude_file(str(file_path)):
            return issues
            
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                lines = f.readlines()
                
            for line_num, line in enumerate(lines, 1):
                line_content = line.strip()
                
                # Skip empty lines and comments
                if not line_content or line_content.startswith('#'):
                    continue
                
                # Check for high-severity patterns
                for issue_type, patterns in self.high_severity_patterns.items():
                    for pattern in patterns:
                        if re.search(pattern, line_content, re.IGNORECASE):
                            issues.append(SecurityIssue(
                                file_path=str(file_path),
                                line_number=line_num,
                                line_content=line_content,
                                issue_type=issue_type,
                                severity="HIGH",
                                description=f"Potential {issue_type} found"
                            ))
                            
        except Exception as e:
            print(f"Error scanning {file_path}: {e}")
            
        return issues

    def scan_project(self) -> Dict[str, Any]:
        """Scan the main project directories for security issues"""
        print("🔒 Starting Focused Security Validation...")
        
        all_issues = []
        files_scanned = 0
        
        for scan_dir in self.scan_directories:
            scan_path = self.project_root / scan_dir
            if not scan_path.exists():
                continue
                
            print(f"📁 Scanning {scan_dir}...")
            
            for file_path in scan_path.rglob("*"):
                if file_path.is_file() and file_path.suffix in ['.py', '.js', '.ts', '.json', '.yaml', '.yml', '.env', '.conf', '.config']:
                    if not self.should_exclude_file(str(file_path)):
                        issues = self.scan_file(file_path)
                        all_issues.extend(issues)
                        files_scanned += 1
        
        # Categorize issues by severity
        high_severity = [issue for issue in all_issues if issue.severity == "HIGH"]
        
        results = {
            "scan_summary": {
                "files_scanned": files_scanned,
                "total_issues": len(all_issues),
                "high_severity_issues": len(high_severity)
            },
            "high_severity_issues": [
                {
                    "file_path": issue.file_path,
                    "line_number": issue.line_number,
                    "line_content": issue.line_content[:100] + "..." if len(issue.line_content) > 100 else issue.line_content,
                    "issue_type": issue.issue_type,
                    "description": issue.description
                }
                for issue in high_severity[:20]  # Show first 20 high-severity issues
            ]
        }
        
        return results

    def generate_security_report(self) -> str:
        """Generate a focused security validation report"""
        results = self.scan_project()
        
        print("\n" + "="*60)
        print("🔒 FOCUSED SECURITY VALIDATION REPORT")
        print("="*60)
        
        print(f"\n📊 Scan Summary:")
        print(f"   Files scanned: {results['scan_summary']['files_scanned']}")
        print(f"   Total issues found: {results['scan_summary']['total_issues']}")
        print(f"   High-severity issues: {results['scan_summary']['high_severity_issues']}")
        
        if results['scan_summary']['high_severity_issues'] > 0:
            print(f"\n🚨 High-Severity Issues (first 20):")
            for issue in results['high_severity_issues']:
                print(f"   {issue['file_path']}:{issue['line_number']} - {issue['description']}")
                print(f"      Content: {issue['line_content']}")
                print()
        else:
            print("\n✅ No high-severity security issues found in main project directories!")
        
        # Save detailed report
        report_file = "focused_security_report.json"
        with open(report_file, 'w') as f:
            json.dump(results, f, indent=2)
        
        print(f"\n📄 Detailed report saved to {report_file}")
        
        return report_file

def main():
    validator = FocusedSecurityValidator()
    report_file = validator.generate_security_report()
    
    # Return appropriate exit code
    with open(report_file, 'r') as f:
        results = json.load(f)
    
    if results['scan_summary']['high_severity_issues'] > 0:
        print("\n❌ SECURITY VALIDATION FAILED: High-severity issues found!")
        return 1
    else:
        print("\n✅ SECURITY VALIDATION PASSED: No high-severity issues in main directories!")
        return 0

if __name__ == "__main__":
    exit(main())