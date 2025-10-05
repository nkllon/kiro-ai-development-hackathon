#!/usr/bin/env python3
"""
Improved Hardcoded Credential Scanner
====================================

Enhanced version that reduces false positives by:
1. Excluding test files with obvious test patterns
2. Better context awareness for legitimate examples
3. Improved pattern matching for real violations
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
    context: str = ""


class ImprovedCredentialScanner:
    """Enhanced scanner with better false positive detection."""
    
    def __init__(self):
        """Initialize the improved credential scanner."""
        self.violations: List[CredentialViolation] = []
        
        # Patterns for detecting hardcoded credentials
        self.credential_patterns = {
            'password': [
                r'password\s*=\s*["\'][^"\']{3,}["\']',  # At least 3 chars
                r'passwd\s*=\s*["\'][^"\']{3,}["\']',
                r'pwd\s*=\s*["\'][^"\']{3,}["\']',
            ],
            'api_key': [
                r'api_key\s*=\s*["\'][^"\']{10,}["\']',  # At least 10 chars for real keys
                r'apikey\s*=\s*["\'][^"\']{10,}["\']',
                r'key\s*=\s*["\']sk-[^"\']{20,}["\']',  # OpenAI style - longer
                r'key\s*=\s*["\']pk-[^"\']{20,}["\']',  # Stripe style - longer
            ],
            'token': [
                r'token\s*=\s*["\'][^"\']{10,}["\']',  # At least 10 chars
                r'auth_token\s*=\s*["\'][^"\']{10,}["\']',
                r'access_token\s*=\s*["\'][^"\']{10,}["\']',
            ],
            'secret': [
                r'secret\s*=\s*["\'][^"\']{8,}["\']',  # At least 8 chars
                r'client_secret\s*=\s*["\'][^"\']{8,}["\']',
                r'app_secret\s*=\s*["\'][^"\']{8,}["\']',
            ],
            'connection_string': [
                r'["\'][^"\']*://[^"\']*:[^"\']{3,}@[^"\']*["\']',  # Real passwords only
                r'mongodb://[^"\']*:[^"\']{3,}@[^"\']*',
                r'postgresql://[^"\']*:[^"\']{3,}@[^"\']*',
                r'mysql://[^"\']*:[^"\']{3,}@[^"\']*',
            ],
            'redis_password': [
                r'redis_password\s*=\s*["\'][^"\']{3,}["\']',
                r'password.*beastmode',
                r'beastmode2025',
            ]
        }
        
        # Enhanced safe patterns to exclude false positives
        self.safe_patterns = [
            # Environment variable usage
            r'os\.getenv\(',
            r'getenv\(',
            r'env\[',
            r'environ\[',
            
            # Comments and documentation
            r'#.*(?:password|token|key|secret)',
            r'""".*(?:password|token|key|secret).*"""',
            r"'''.*(?:password|token|key|secret).*'''",
            
            # Placeholder values
            r'(?:password|token|key|secret)\s*=\s*["\'](?:your_|placeholder|example|demo|test_|dummy)[^"\']*["\']',
            r'(?:password|token|key|secret)\s*=\s*["\']["\']',  # Empty string
            r'(?:password|token|key|secret)\s*=\s*["\'](?:xxx|yyy|zzz)["\']',
            
            # Test patterns - more comprehensive
            r'(?:password|token|key|secret)\s*=\s*["\']test[^"\']*["\']',
            r'access_token\s*=\s*["\']test[^"\']*["\']',
            r'refresh_token\s*=\s*["\']test[^"\']*["\']',
            
            # Documentation examples
            r'(?:password|token|key|secret)\s*=\s*["\'][^"\']*(?:here|key|token|password)["\']',
            
            # Pattern definitions (in scanner code itself)
            r'r["\'].*(?:password|token|key|secret)',
            
            # Connection string examples with obvious test values
            r'://(?:user|test|demo|invalid):(?:password|test|demo|invalid)@',
        ]
        
        # Test file patterns - files that should be treated more leniently
        self.test_file_patterns = [
            r'/tests?/',
            r'/test_',
            r'_test\.py$',
            r'/examples?/',
            r'/demo',
            r'test.*\.py$',
        ]
        
        # File extensions to scan
        self.scan_extensions = {'.py', '.js', '.ts', '.json', '.yaml', '.yml', '.env', '.cfg', '.ini', '.conf'}
        
        # Directories to skip
        self.skip_directories = {
            '.git', '__pycache__', '.pytest_cache', 'node_modules', 
            '.venv', 'venv', '.env', 'build', 'dist', '.tox'
        }
    
    def is_test_file(self, file_path: str) -> bool:
        """Check if a file is a test file."""
        for pattern in self.test_file_patterns:
            if re.search(pattern, file_path):
                return True
        return False
    
    def is_likely_test_credential(self, line: str, file_path: str) -> bool:
        """Check if this looks like a test credential."""
        line_lower = line.lower()
        
        # Test file with obvious test patterns
        if self.is_test_file(file_path):
            test_indicators = [
                'test-', 'test_', 'dummy', 'fake', 'mock', 'example',
                'invalid', 'expired', 'old-', 'secret-', 'demo-'
            ]
            for indicator in test_indicators:
                if indicator in line_lower:
                    return True
        
        return False
    
    def scan_file(self, file_path: Path) -> List[CredentialViolation]:
        """Scan a single file for credential violations."""
        violations = []
        
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                lines = f.readlines()
                for line_num, line in enumerate(lines, 1):
                    line_violations = self._check_line_for_violations(
                        str(file_path), line_num, line, lines
                    )
                    violations.extend(line_violations)
        except Exception as e:
            print(f"⚠️  Error scanning {file_path}: {e}")
        
        return violations
    
    def _check_line_for_violations(self, file_path: str, line_num: int, line: str, all_lines: List[str]) -> List[CredentialViolation]:
        """Check a single line for credential violations with context."""
        violations = []
        line_lower = line.lower().strip()
        
        # Get context (previous and next lines)
        context_lines = []
        for i in range(max(0, line_num-3), min(len(all_lines), line_num+2)):
            if i != line_num - 1:  # Don't include the current line
                context_lines.append(all_lines[i].strip())
        context = " ".join(context_lines)
        
        # Skip if line matches safe patterns
        for safe_pattern in self.safe_patterns:
            if re.search(safe_pattern, line, re.IGNORECASE):
                return violations
        
        # Skip if this looks like a test credential
        if self.is_likely_test_credential(line, file_path):
            return violations
        
        # Check each credential pattern
        for violation_type, patterns in self.credential_patterns.items():
            for pattern in patterns:
                matches = re.finditer(pattern, line, re.IGNORECASE)
                for match in matches:
                    # Additional filtering for specific cases
                    matched_text = match.group()
                    
                    # Skip scanner's own pattern definitions
                    if 'scan_for_hardcoded_credentials.py' in file_path and 'r["\']' in matched_text:
                        continue
                    
                    # Skip remediation script patterns
                    if any(script in file_path for script in ['remediate_', 'auto_remediate_', 'remove_hardcoded_']):
                        continue
                    
                    # Determine severity with better logic
                    severity = self._determine_severity(violation_type, matched_text, file_path, context)
                    
                    violation = CredentialViolation(
                        file_path=file_path,
                        line_number=line_num,
                        line_content=line.strip(),
                        violation_type=violation_type,
                        severity=severity,
                        pattern_matched=matched_text,
                        context=context[:200]  # Limit context length
                    )
                    violations.append(violation)
        
        return violations
    
    def _determine_severity(self, violation_type: str, matched_text: str, file_path: str, context: str) -> str:
        """Determine the severity of a credential violation with better logic."""
        matched_lower = matched_text.lower()
        
        # Critical patterns that are definitely real credentials
        critical_indicators = [
            'beastmode2025',  # Our specific password
        ]
        
        # Real API key patterns
        if violation_type == 'api_key':
            if re.match(r'sk-[a-zA-Z0-9]{40,}', matched_text):  # Real OpenAI key format
                return 'CRITICAL'
            if re.match(r'pk_[a-zA-Z0-9]{40,}', matched_text):  # Real Stripe key format
                return 'CRITICAL'
        
        for indicator in critical_indicators:
            if indicator in matched_lower:
                return 'CRITICAL'
        
        # Lower severity for test files
        if self.is_test_file(file_path):
            return 'LOW'
        
        # Lower severity for documentation/examples
        if any(path_part in file_path.lower() for path_part in ['example', 'demo', 'doc']):
            return 'LOW'
        
        # High severity for obvious credentials in production code
        if violation_type in ['password', 'api_key', 'secret'] and not self.is_test_file(file_path):
            # But check if it's obviously a placeholder
            placeholder_patterns = [
                r'your[_-]',
                r'[_-]here',
                r'placeholder',
                r'example',
                r'demo[_-]',
            ]
            
            for pattern in placeholder_patterns:
                if re.search(pattern, matched_lower):
                    return 'LOW'
            
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
        by_severity = {'CRITICAL': [], 'HIGH': [], 'MEDIUM': [], 'LOW': []}
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
        
        # Determine overall status
        if by_severity['CRITICAL']:
            status = 'CRITICAL'
        elif by_severity['HIGH']:
            status = 'HIGH'
        elif by_severity['MEDIUM']:
            status = 'MEDIUM'
        else:
            status = 'LOW'
        
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
                    'pattern': v.pattern_matched,
                    'context': v.context
                }
                for v in violations
            ]
        }
    
    def print_report(self, report: Dict, show_low_severity: bool = False) -> None:
        """Print a human-readable report."""
        print("🔍 IMPROVED HARDCODED CREDENTIAL SCAN REPORT")
        print("=" * 55)
        
        if report['status'] == 'CLEAN':
            print("✅ " + report['summary'])
            return
        
        print(f"📊 STATUS: {report['status']}")
        print(f"📈 Total Violations: {report['total_violations']}")
        
        print(f"\n📊 By Severity:")
        for severity, count in report['by_severity'].items():
            if count > 0:
                if severity == "CRITICAL":
                    icon = "🚨"
                elif severity == "HIGH":
                    icon = "⚠️"
                elif severity == "MEDIUM":
                    icon = "ℹ️"
                else:
                    icon = "🔍"
                print(f"  {icon} {severity}: {count}")
        
        print(f"\n📋 By Type:")
        for vtype, count in report['by_type'].items():
            print(f"  • {vtype}: {count}")
        
        # Only show detailed violations for CRITICAL and HIGH by default
        print(f"\n🔍 Detailed Violations (CRITICAL & HIGH only):")
        shown_count = 0
        for violation in report['violations']:
            if violation['severity'] in ['CRITICAL', 'HIGH'] or show_low_severity:
                severity_icon = {
                    'CRITICAL': '🚨',
                    'HIGH': '⚠️',
                    'MEDIUM': 'ℹ️',
                    'LOW': '🔍'
                }.get(violation['severity'], 'ℹ️')
                
                print(f"\n{severity_icon} {violation['severity']} - {violation['type']}")
                print(f"   File: {violation['file']}:{violation['line']}")
                print(f"   Code: {violation['content']}")
                print(f"   Match: {violation['pattern']}")
                if violation.get('context'):
                    print(f"   Context: {violation['context'][:100]}...")
                shown_count += 1
        
        if not show_low_severity and report['by_severity'].get('MEDIUM', 0) + report['by_severity'].get('LOW', 0) > 0:
            print(f"\n🔍 ({report['by_severity'].get('MEDIUM', 0) + report['by_severity'].get('LOW', 0)} lower severity violations hidden. Use --show-all to see them)")
        
        if report['by_severity'].get('CRITICAL', 0) + report['by_severity'].get('HIGH', 0) > 0:
            print(f"\n🚨 REMEDIATION REQUIRED:")
            print("1. Replace hardcoded credentials with environment variables")
            print("2. Use src/security/secure_credentials.py helper")
            print("3. Add credentials to ~/.env file")
            print("4. Never commit credentials to version control")


def main():
    """Main scanning function."""
    scanner = ImprovedCredentialScanner()
    
    # Parse arguments
    show_all = '--show-all' in sys.argv
    
    # Determine scan directory
    scan_dir = Path.cwd()
    for arg in sys.argv[1:]:
        if not arg.startswith('--') and Path(arg).exists():
            scan_dir = Path(arg)
            break
    
    print(f"🔍 Scanning {scan_dir} for hardcoded credentials...")
    print("🧠 Using improved false positive detection...")
    
    # Scan for violations
    violations = scanner.scan_directory(scan_dir)
    
    # Generate and print report
    report = scanner.generate_report(violations)
    scanner.print_report(report, show_low_severity=show_all)
    
    # Save detailed report
    report_file = "improved_credential_scan_report.json"
    with open(report_file, 'w') as f:
        json.dump(report, f, indent=2)
    print(f"\n📄 Detailed report saved to: {report_file}")
    
    # Exit with appropriate code - only fail on CRITICAL or HIGH
    if report['status'] in ['CRITICAL', 'HIGH']:
        print(f"\n❌ Scan failed due to {report['status']} severity violations")
        sys.exit(1)
    else:
        print(f"\n✅ Scan passed - only low/medium severity violations found")
        sys.exit(0)


if __name__ == "__main__":
    main()