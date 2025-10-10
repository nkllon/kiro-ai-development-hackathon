#!/usr/bin/env python3
"""
Hardcoded Credential Scanner
===========================

Scans codebase for hardcoded credentials and security violations.
Part of the security governance enforcement system.
"""

import os
import re
import sys
from pathlib import Path
from typing import List, Dict, Tuple, Set
from dataclasses import dataclass
import json


@dataclass
class CredentialViolation:
    """Represents a potential credential violation."""
    file_path: str
    line_number: int
    line_content: str
    violation_type: str
    severity: str
    pattern_matched: str


class CredentialScanner:
    """Scans for hardcoded credentials in source code."""
    
    def __init__(self):
        """Initialize the credential scanner."""
        self.violations: List[CredentialViolation] = []
        
        # Patterns for detecting hardcoded credentials
        self.credential_patterns = {
            'password': [
                r'password\s*=\s*["\'][^"\']+["\']',
                r'passwd\s*=\s*["\'][^"\']+["\']',
                r'pwd\s*=\s*["\'][^"\']+["\']',
            ],
            'api_key': [
                r'api_key\s*=\s*["\'][^"\']+["\']',
                r'apikey\s*=\s*["\'][^"\']+["\']',
                r'key\s*=\s*["\']sk-[^"\']+["\']',  # OpenAI style
                r'key\s*=\s*["\']pk-[^"\']+["\']',  # Stripe style
            ],
            'token': [
                r'token\s*=\s*["\'][^"\']+["\']',
                r'auth_token\s*=\s*["\'][^"\']+["\']',
                r'access_token\s*=\s*["\'][^"\']+["\']',
            ],
            'secret': [
                r'secret\s*=\s*["\'][^"\']+["\']',
                r'client_secret\s*=\s*["\'][^"\']+["\']',
                r'app_secret\s*=\s*["\'][^"\']+["\']',
            ],
            'connection_string': [
                r'["\'][^"\']*://[^"\']*:[^"\']*@[^"\']*["\']',  # DB connection strings
                r'mongodb://[^"\']*:[^"\']*@[^"\']*',
                r'postgresql://[^"\']*:[^"\']*@[^"\']*',
                r'mysql://[^"\']*:[^"\']*@[^"\']*',
            ],
            'redis_password': [
                r'redis_password\s*=\s*["\'][^"\']+["\']',
                r'password.*beastmode',
                ros.getenv('REDIS_PASSWORD', ''),
            ]
        }
        
        # Known safe patterns to exclude
        self.safe_patterns = [
            r'password\s*=\s*["\']your_password_here["\']',
            r'password\s*=\s*["\']placeholder["\']',
            r'password\s*=\s*["\']example["\']',
            r'password\s*=\s*["\']["\']',  # Empty string
            r'os\.getenv\(',  # Environment variable usage
            r'getenv\(',      # Environment variable usage
            r'env\[',         # Environment variable usage
            r'#.*password',   # Comments
            r'""".*password.*"""',  # Docstrings
        ]
        
        # File extensions to scan
        self.scan_extensions = {'.py', '.js', '.ts', '.json', '.yaml', '.yml', '.env', '.cfg', '.ini', '.conf'}
        
        # Directories to skip
        self.skip_directories = {
            '.git', '__pycache__', '.pytest_cache', 'node_modules', 
            '.venv', 'venv', '.env', 'build', 'dist', '.tox'
        }
    
    def scan_file(self, file_path: Path) -> List[CredentialViolation]:
        """Scan a single file for credential violations."""
        violations = []
        
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                for line_num, line in enumerate(f, 1):
                    line_violations = self._check_line_for_violations(
                        str(file_path), line_num, line
                    )
                    violations.extend(line_violations)
        except Exception as e:
            print(f"⚠️  Error scanning {file_path}: {e}")
        
        return violations
    
    def _check_line_for_violations(self, file_path: str, line_num: int, line: str) -> List[CredentialViolation]:
        """Check a single line for credential violations."""
        violations = []
        line_lower = line.lower().strip()
        
        # Skip if line matches safe patterns
        for safe_pattern in self.safe_patterns:
            if re.search(safe_pattern, line, re.IGNORECASE):
                return violations
        
        # Check each credential pattern
        for violation_type, patterns in self.credential_patterns.items():
            for pattern in patterns:
                matches = re.finditer(pattern, line, re.IGNORECASE)
                for match in matches:
                    # Determine severity
                    severity = self._determine_severity(violation_type, match.group())
                    
                    violation = CredentialViolation(
                        file_path=file_path,
                        line_number=line_num,
                        line_content=line.strip(),
                        violation_type=violation_type,
                        severity=severity,
                        pattern_matched=match.group()
                    )
                    violations.append(violation)
        
        return violations
    
    def _determine_severity(self, violation_type: str, matched_text: str) -> str:
        """Determine the severity of a credential violation."""
        # Critical patterns
        critical_indicators = [
            os.getenv('REDIS_PASSWORD', ''),
            'sk-',  # OpenAI API keys
            'pk_',  # Stripe keys
            '://.*:.*@',  # Connection strings with credentials
        ]
        
        for indicator in critical_indicators:
            if indicator in matched_text.lower():
                return 'CRITICAL'
        
        # High severity for obvious credentials
        if violation_type in ['password', 'api_key', 'secret']:
            return 'HIGH'
        
        return 'MEDIUM'
    
    def scan_directory(self, directory: Path) -> List[CredentialViolation]:
        """Scan a directory recursively for credential violations."""
        all_violations = []
        
        for root, dirs, files in os.walk(directory):
            # Skip certain directories
            dirs[:] = [d for d in dirs if d not in self.skip_directories]
            
            for file in files:
                file_path = Path(root) / file
                
                # Only scan files with relevant extensions
                if file_path.suffix in self.scan_extensions:
                    violations = self.scan_file(file_path)
                    all_violations.extend(violations)
        
        return all_violations
    
    def generate_report(self, violations: List[CredentialViolation]) -> Dict:
        """Generate a comprehensive report of violations."""
        if not violations:
            return {
                'status': 'CLEAN',
                'total_violations': 0,
                'summary': 'No hardcoded credentials found! ✅',
                'violations': []
            }
        
        # Group violations by severity
        by_severity = {'CRITICAL': [], 'HIGH': [], 'MEDIUM': []}
        for violation in violations:
            by_severity[violation.severity].append(violation)
        
        # Group violations by type
        by_type = {}
        for violation in violations:
            if violation.violation_type not in by_type:
                by_type[violation.violation_type] = []
            by_type[violation.violation_type].append(violation)
        
        # Group violations by file
        by_file = {}
        for violation in violations:
            if violation.file_path not in by_file:
                by_file[violation.file_path] = []
            by_file[violation.file_path].append(violation)
        
        status = 'CRITICAL' if by_severity['CRITICAL'] else ('HIGH' if by_severity['HIGH'] else 'MEDIUM')
        
        return {
            'status': status,
            'total_violations': len(violations),
            'by_severity': {k: len(v) for k, v in by_severity.items()},
            'by_type': {k: len(v) for k, v in by_type.items()},
            'by_file': {k: len(v) for k, v in by_file.items()},
            'violations': [
                {
                    'file': v.file_path,
                    'line': v.line_number,
                    'content': v.line_content,
                    'type': v.violation_type,
                    'severity': v.severity,
                    'pattern': v.pattern_matched
                }
                for v in violations
            ]
        }
    
    def print_report(self, report: Dict) -> None:
        """Print a human-readable report."""
        print("🔍 HARDCODED CREDENTIAL SCAN REPORT")
        print("=" * 50)
        
        if report['status'] == 'CLEAN':
            print("✅ " + report['summary'])
            return
        
        print(f"❌ STATUS: {report['status']}")
        print(f"📊 Total Violations: {report['total_violations']}")
        
        print(f"\n📈 By Severity:")
        for severity, count in report['by_severity'].items():
            if count > 0:
                icon = "🚨" if severity == "CRITICAL" else ("⚠️" if severity == "HIGH" else "ℹ️")
                print(f"  {icon} {severity}: {count}")
        
        print(f"\n📋 By Type:")
        for vtype, count in report['by_type'].items():
            print(f"  • {vtype}: {count}")
        
        print(f"\n📁 By File:")
        for file_path, count in report['by_file'].items():
            print(f"  • {file_path}: {count}")
        
        print(f"\n🔍 Detailed Violations:")
        for violation in report['violations']:
            severity_icon = "🚨" if violation['severity'] == "CRITICAL" else ("⚠️" if violation['severity'] == "HIGH" else "ℹ️")
            print(f"\n{severity_icon} {violation['severity']} - {violation['type']}")
            print(f"   File: {violation['file']}:{violation['line']}")
            print(f"   Code: {violation['content']}")
            print(f"   Match: {violation['pattern']}")
        
        print(f"\n🚨 REMEDIATION REQUIRED:")
        print("1. Replace hardcoded credentials with environment variables")
        print("2. Use src/security/secure_credentials.py helper")
        print("3. Add credentials to ~/.env file")
        print("4. Never commit credentials to version control")


def main():
    """Main scanning function."""
    scanner = CredentialScanner()
    
    # Determine scan directory
    scan_dir = Path.cwd()
    if len(sys.argv) > 1:
        scan_dir = Path(sys.argv[1])
    
    print(f"🔍 Scanning {scan_dir} for hardcoded credentials...")
    
    # Scan for violations
    violations = scanner.scan_directory(scan_dir)
    
    # Generate and print report
    report = scanner.generate_report(violations)
    scanner.print_report(report)
    
    # Save detailed report
    report_file = "credential_scan_report.json"
    with open(report_file, 'w') as f:
        json.dump(report, f, indent=2)
    print(f"\n📄 Detailed report saved to: {report_file}")
    
    # Exit with appropriate code
    if report['status'] == 'CLEAN':
        sys.exit(0)
    elif report['status'] in ['CRITICAL', 'HIGH']:
        sys.exit(1)
    else:
        sys.exit(0)


if __name__ == "__main__":
    main()