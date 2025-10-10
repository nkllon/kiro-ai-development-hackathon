#!/usr/bin/env python3
"""
Security Credential Scanner - Comprehensive security and credential cleanup.

This script scans the entire codebase for hardcoded credentials, API keys, 
and other sensitive information that should not be in version control.
"""

import os
import re
import json
from pathlib import Path
from typing import Dict, List, Set, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime

@dataclass
class SecurityIssue:
    """Represents a potential security issue found in the codebase."""
    file_path: str
    line_number: int
    line_content: str
    issue_type: str
    severity: str  # HIGH, MEDIUM, LOW
    description: str
    suggested_fix: str

class SecurityCredentialScanner:
    """Scans for security issues and hardcoded credentials."""
    
    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root)
        self.issues: List[SecurityIssue] = []
        
        # Patterns for different types of credentials and sensitive data
        self.credential_patterns = {
            "api_key": [
                r"api[_-]?key\s*[=:]\s*['\"]([^'\"]{20,})['\"]",
                r"apikey\s*[=:]\s*['\"]([^'\"]{20,})['\"]",
                r"key\s*[=:]\s*['\"]([A-Za-z0-9]{20,})['\"]"
            ],
            "password": [
                r"password\s*[=:]\s*['\"]([^'\"]{8,})['\"]",
                r"passwd\s*[=:]\s*['\"]([^'\"]{8,})['\"]",
                r"pwd\s*[=:]\s*['\"]([^'\"]{8,})['\"]"
            ],
            "secret": [
                r"secret\s*[=:]\s*['\"]([^'\"]{16,})['\"]",
                r"client[_-]?secret\s*[=:]\s*['\"]([^'\"]{16,})['\"]"
            ],
            "token": [
                r"token\s*[=:]\s*['\"]([^'\"]{20,})['\"]",
                r"access[_-]?token\s*[=:]\s*['\"]([^'\"]{20,})['\"]",
                r"auth[_-]?token\s*[=:]\s*['\"]([^'\"]{20,})['\"]"
            ],
            "private_key": [
                r"-----BEGIN\s+(RSA\s+)?PRIVATE\s+KEY-----",
                r"private[_-]?key\s*[=:]\s*['\"]([^'\"]{50,})['\"]"
            ],
            "database_url": [
                r"(postgresql|mysql|mongodb)://[^/\s]+:[^@\s]+@[^/\s]+",
                r"database[_-]?url\s*[=:]\s*['\"]([^'\"]*://[^'\"]*)['\"]"
            ]
        }
        
        # Suspicious hardcoded values
        self.suspicious_patterns = {
            "hardcoded_ip": [
                r"\b(?:192\.168\.|10\.|172\.(?:1[6-9]|2[0-9]|3[01])\.)[\d.]+\b",
                r"\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b"
            ],
            "hardcoded_port": [
                r":\s*[0-9]{4,5}\b"
            ],
            "email_addresses": [
                r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b"
            ]
        }
        
        # Files to skip (binary, generated, etc.)
        self.skip_patterns = [
            r".*\.pyc$",
            r".*\.pyo$",
            r".*\.so$",
            r".*\.dll$",
            r".*\.exe$",
            r".*\.bin$",
            r".*\.png$",
            r".*\.jpg$",
            r".*\.jpeg$",
            r".*\.gif$",
            r".*\.pdf$",
            r".*\.zip$",
            r".*\.tar\.gz$",
            r".*\.db$",
            r".*\.sqlite.*$",
            r".*/__pycache__/.*",
            r".*/node_modules/.*",
            r".*/\.git/.*",
            r".*/\.venv/.*",
            r".*/venv/.*"
        ]
        
        # Safe patterns to ignore (environment variable usage, examples, etc.)
        self.safe_patterns = [
            r"os\.getenv\(",
            r"os\.environ\[",
            r"getenv\(",
            r"ENV\[",
            r"process\.env\.",
            r"YOUR_API_KEY",
            r"EXAMPLE_",
            r"PLACEHOLDER_",
            r"<YOUR_",
            r"\$\{.*\}",  # Environment variable substitution
            r"example\.com",
            r"localhost",
            r"127\.0\.0\.1"
        ]

    def should_skip_file(self, file_path: Path) -> bool:
        """Check if file should be skipped."""
        path_str = str(file_path)
        return any(re.match(pattern, path_str) for pattern in self.skip_patterns)

    def is_safe_line(self, line: str) -> bool:
        """Check if line contains safe patterns that should be ignored."""
        return any(re.search(pattern, line, re.IGNORECASE) for pattern in self.safe_patterns)

    def scan_file_for_credentials(self, file_path: Path) -> List[SecurityIssue]:
        """Scan a single file for credentials and security issues."""
        issues = []
        
        if self.should_skip_file(file_path):
            return issues
        
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                lines = f.readlines()
        except (OSError, UnicodeDecodeError):
            return issues
        
        for line_num, line in enumerate(lines, 1):
            line = line.strip()
            
            # Skip empty lines and comments
            if not line or line.startswith('#') or line.startswith('//'):
                continue
            
            # Skip lines with safe patterns
            if self.is_safe_line(line):
                continue
            
            # Check for credential patterns
            for cred_type, patterns in self.credential_patterns.items():
                for pattern in patterns:
                    if re.search(pattern, line, re.IGNORECASE):
                        issues.append(SecurityIssue(
                            file_path=str(file_path.relative_to(self.project_root)),
                            line_number=line_num,
                            line_content=line[:100] + "..." if len(line) > 100 else line,
                            issue_type=cred_type,
                            severity="HIGH",
                            description=f"Potential {cred_type.replace('_', ' ')} found",
                            suggested_fix=f"Replace with environment variable: os.getenv('{cred_type.upper()}')"
                        ))
            
            # Check for suspicious patterns
            for susp_type, patterns in self.suspicious_patterns.items():
                for pattern in patterns:
                    if re.search(pattern, line):
                        # Lower severity for suspicious patterns
                        severity = "MEDIUM" if susp_type == "hardcoded_ip" else "LOW"
                        issues.append(SecurityIssue(
                            file_path=str(file_path.relative_to(self.project_root)),
                            line_number=line_num,
                            line_content=line[:100] + "..." if len(line) > 100 else line,
                            issue_type=susp_type,
                            severity=severity,
                            description=f"Suspicious {susp_type.replace('_', ' ')} found",
                            suggested_fix="Review if this should be configurable"
                        ))
        
        return issues

    def scan_project(self) -> None:
        """Scan the entire project for security issues."""
        print("🔒 Scanning project for security issues and credentials...")
        
        # Get all text files to scan
        text_extensions = {'.py', '.js', '.ts', '.json', '.yaml', '.yml', '.toml', 
                          '.cfg', '.conf', '.ini', '.env', '.sh', '.bash', '.md', 
                          '.txt', '.sql', '.xml', '.html', '.css'}
        
        files_scanned = 0
        for file_path in self.project_root.rglob("*"):
            if file_path.is_file() and (file_path.suffix in text_extensions or file_path.name.startswith('.')):
                if not self.should_skip_file(file_path):
                    file_issues = self.scan_file_for_credentials(file_path)
                    self.issues.extend(file_issues)
                    files_scanned += 1
                    
                    if files_scanned % 1000 == 0:
                        print(f"   Scanned {files_scanned} files...")
        
        print(f"✅ Scanned {files_scanned} files")

    def generate_security_report(self) -> Dict:
        """Generate comprehensive security report."""
        # Group issues by severity and type
        by_severity = {"HIGH": [], "MEDIUM": [], "LOW": []}
        by_type = {}
        
        for issue in self.issues:
            by_severity[issue.severity].append(issue)
            if issue.issue_type not in by_type:
                by_type[issue.issue_type] = []
            by_type[issue.issue_type].append(issue)
        
        # Generate summary statistics
        summary = {
            "total_issues": len(self.issues),
            "high_severity": len(by_severity["HIGH"]),
            "medium_severity": len(by_severity["MEDIUM"]),
            "low_severity": len(by_severity["LOW"]),
            "issues_by_type": {k: len(v) for k, v in by_type.items()},
            "files_with_issues": len(set(issue.file_path for issue in self.issues))
        }
        
        return {
            "scan_timestamp": datetime.now().isoformat(),
            "project_root": str(self.project_root),
            "summary": summary,
            "issues_by_severity": {k: [asdict(issue) for issue in v] for k, v in by_severity.items()},
            "issues_by_type": {k: [asdict(issue) for issue in v] for k, v in by_type.items()},
            "recommendations": self.generate_recommendations(summary)
        }

    def generate_recommendations(self, summary: Dict) -> List[str]:
        """Generate security recommendations based on findings."""
        recommendations = []
        
        if summary["high_severity"] > 0:
            recommendations.append(
                f"🚨 CRITICAL: {summary['high_severity']} high-severity security issues found. "
                "Address immediately before public release."
            )
        
        if summary["medium_severity"] > 0:
            recommendations.append(
                f"⚠️  {summary['medium_severity']} medium-severity issues found. "
                "Review and address before public release."
            )
        
        if "password" in summary["issues_by_type"]:
            recommendations.append(
                "🔑 Hardcoded passwords detected. Replace with environment variables or secure configuration."
            )
        
        if "api_key" in summary["issues_by_type"]:
            recommendations.append(
                "🔐 API keys detected. Move to environment variables and rotate if exposed."
            )
        
        if "database_url" in summary["issues_by_type"]:
            recommendations.append(
                "🗄️ Database URLs with credentials detected. Use environment variables for connection strings."
            )
        
        if summary["total_issues"] == 0:
            recommendations.append("✅ No security issues detected. Project appears secure for public release.")
        
        return recommendations

    def save_security_report(self, output_file: str) -> None:
        """Save security report to file."""
        report = self.generate_security_report()
        
        with open(output_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"📄 Security report saved to {output_file}")

    def print_security_summary(self) -> None:
        """Print security scan summary."""
        report = self.generate_security_report()
        summary = report["summary"]
        
        print("\n" + "="*60)
        print("🔒 SECURITY SCAN SUMMARY")
        print("="*60)
        
        print(f"\n📊 Scan Results:")
        print(f"   Total issues found: {summary['total_issues']}")
        print(f"   Files with issues: {summary['files_with_issues']}")
        
        print(f"\n🚨 Issues by Severity:")
        print(f"   HIGH:   {summary['high_severity']} (requires immediate action)")
        print(f"   MEDIUM: {summary['medium_severity']} (should be addressed)")
        print(f"   LOW:    {summary['low_severity']} (review recommended)")
        
        if summary["issues_by_type"]:
            print(f"\n🔍 Issues by Type:")
            for issue_type, count in summary["issues_by_type"].items():
                print(f"   {issue_type.replace('_', ' ').title()}: {count}")
        
        print(f"\n💡 Recommendations:")
        for rec in report["recommendations"]:
            print(f"   {rec}")
        
        # Show some high-severity examples
        high_issues = [issue for issue in self.issues if issue.severity == "HIGH"]
        if high_issues:
            print(f"\n🚨 High-Severity Issues (first 5):")
            for issue in high_issues[:5]:
                print(f"   {issue.file_path}:{issue.line_number} - {issue.description}")
        
        print("\n" + "="*60)

def main():
    """Main execution function."""
    print("🚀 Starting Security Credential Scan...")
    
    scanner = SecurityCredentialScanner()
    
    # Scan project
    scanner.scan_project()
    
    # Print summary
    scanner.print_security_summary()
    
    # Save detailed report
    output_file = "security_scan_report.json"
    scanner.save_security_report(output_file)
    
    print(f"\n✅ Security scan complete! Review {output_file} for detailed findings.")
    
    # Return exit code based on findings
    high_severity_count = len([issue for issue in scanner.issues if issue.severity == "HIGH"])
    if high_severity_count > 0:
        print(f"\n❌ SECURITY ALERT: {high_severity_count} high-severity issues must be resolved!")
        return 1
    else:
        print("\n✅ No high-severity security issues found.")
        return 0

if __name__ == "__main__":
    exit(main())