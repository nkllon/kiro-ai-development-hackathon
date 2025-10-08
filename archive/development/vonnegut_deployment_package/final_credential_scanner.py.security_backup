#!/usr/bin/env python3
"""
Final Hardcoded Credential Scanner
=================================

Production-ready scanner that minimizes false positives while catching real violations.
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


class FinalCredentialScanner:
    """Production-ready scanner with comprehensive false positive filtering."""
    
    def __init__(self):
        """Initialize the final credential scanner."""
        self.violations: List[CredentialViolation] = []
        
        # Real credential patterns - more restrictive
        self.credential_patterns = {
            'redis_password': [
                r'beastmode2025',  # Our specific password
            ],
            'password': [
                r'password\s*=\s*["\'][^"\']{6,}["\']',  # At least 6 chars, not test patterns
            ],
            'api_key': [
                r'api_key\s*=\s*["\']sk-[a-zA-Z0-9]{40,}["\']',  # Real OpenAI keys
                r'api_key\s*=\s*["\']pk_[a-zA-Z0-9]{40,}["\']',  # Real Stripe keys
            ],
            'secret': [
                r'secret\s*=\s*["\'][^"\']{12,}["\']',  # At least 12 chars for real secrets
            ],
            'connection_string': [
                r'["\'][^"\']*://[^"\']*:beastmode2025@[^"\']*["\']',  # Our specific password in URLs
            ],
        }
        
        # Files to completely skip
        self.skip_files = {
            'credential_scan_report.json',
            'improved_credential_scan_report.json',
            'final_credential_scan_report.json',
        }
        
        # Directories to skip
        self.skip_directories = {
            '.git', '__pycache__', '.pytest_cache', 'node_modules', 
            '.venv', 'venv', '.env', 'build', 'dist', '.tox'
        }
        
        # File extensions to scan
        self.scan_extensions = {'.py', '.js', '.ts', '.json', '.yaml', '.yml', '.env', '.cfg', '.ini', '.conf'}
        
        # Test file patterns - more comprehensive
        self.test_file_patterns = [
            r'/tests?/',
            r'/test_',
            r'_test\.py$',
            r'test.*\.py$',
            r'/examples?/',
            r'/demo',
            r'demo.*\.py$',
        ]
        
        # Files that are known to be templates/examples
        self.template_file_patterns = [
            r'sample\.',
            r'template\.',
            r'example\.',
            r'demo\.',
            r'\.example$',
            r'\.sample$',
            r'\.template$',
        ]
        
        # Scanner/remediation script patterns
        self.scanner_script_patterns = [
            r'scan.*credential',
            r'remediate.*credential',
            r'auto_remediate',
            r'remove_hardcoded',
            r'credential.*scanner',
        ]
    
    def should_skip_file(self, file_path: str) -> Tuple[bool, str]:
        """Check if a file should be completely skipped."""
        file_name = os.path.basename(file_path)
        
        # Skip specific files
        if file_name in self.skip_files:
            return True, "scan report file"
        
        # Skip scanner/remediation scripts
        for pattern in self.scanner_script_patterns:
            if re.search(pattern, file_name, re.IGNORECASE):
                return True, "scanner/remediation script"
        
        return False, ""
    
    def is_test_file(self, file_path: str) -> bool:
        """Check if a file is a test file."""
        for pattern in self.test_file_patterns:
            if re.search(pattern, file_path):
                return True
        return False
    
    def is_template_file(self, file_path: str) -> bool:
        """Check if a file is a template/example file."""
        for pattern in self.template_file_patterns:
            if re.search(pattern, file_path):
                return True
        return False
    
    def scan_file(self, file_path: Path) -> List[CredentialViolation]:
        """Scan a single file for credential violations."""
        violations = []
        file_path_str = str(file_path)
        
        # Check if we should skip this file
        should_skip, skip_reason = self.should_skip_file(file_path_str)
        if should_skip:
            return violations
        
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                lines = f.readlines()
                for line_num, line in enumerate(lines, 1):
                    line_violations = self._check_line_for_violations(
                        file_path_str, line_num, line, lines
                    )
                    violations.extend(line_violations)
        except Exception as e:
            print(f"⚠️  Error scanning {file_path}: {e}")
        
        return violations
    
    def _check_line_for_violations(self, file_path: str, line_num: int, line: str, all_lines: List[str]) -> List[CredentialViolation]:
        """Check a single line for credential violations."""
        violations = []
        
        # Get context
        context_lines = []
        for i in range(max(0, line_num-2), min(len(all_lines), line_num+1)):
            if i != line_num - 1:
                context_lines.append(all_lines[i].strip())
        context = " ".join(context_lines)
        
        # Check each credential pattern
        for violation_type, patterns in self.credential_patterns.items():
            for pattern in patterns:
                matches = re.finditer(pattern, line, re.IGNORECASE)
                for match in matches:
                    matched_text = match.group()
                    
                    # Determine severity
                    severity = self._determine_severity(violation_type, matched_text, file_path, context)
                    
                    # Skip if it's low severity (test/template files)
                    if severity == 'LOW':
                        continue
                    
                    violation = CredentialViolation(
                        file_path=file_path,
                        line_number=line_num,
                        line_content=line.strip(),
                        violation_type=violation_type,
                        severity=severity,
                        pattern_matched=matched_text,
                        context=context[:150]
                    )
                    violations.append(violation)
        
        return violations
    
    def _determine_severity(self, violation_type: str, matched_text: str, file_path: str, context: str) -> str:
        """Determine the severity of a credential violation."""
        
        # Test files get LOW severity (which we filter out)
        if self.is_test_file(file_path):
            return 'LOW'
        
        # Template files get MEDIUM severity
        if self.is_template_file(file_path):
            return 'MEDIUM'
        
        # Our specific password is always CRITICAL in production code
        if 'beastmode2025' in matched_text.lower():
            return 'CRITICAL'
        
        # Real API keys are CRITICAL
        if violation_type == 'api_key':
            if re.match(r'sk-[a-zA-Z0-9]{40,}', matched_text):
                return 'CRITICAL'
            if re.match(r'pk_[a-zA-Z0-9]{40,}', matched_text):
                return 'CRITICAL'
        
        # Production code with credentials is HIGH
        return 'HIGH'
    
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
        else:
            status = 'MEDIUM'
        
        return {
            'status': status,
            'total_violations': len(violations),
            'by_severity': {k: len(v) for k, v in by_severity.items()},
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
    
    def print_report(self, report: Dict) -> None:
        """Print a human-readable report."""
        print("🔍 FINAL CREDENTIAL SCAN REPORT")
        print("=" * 40)
        
        if report['status'] == 'CLEAN':
            print("✅ " + report['summary'])
            return
        
        print(f"📊 STATUS: {report['status']}")
        print(f"📈 Total Violations: {report['total_violations']}")
        
        print(f"\n📊 By Severity:")
        for severity, count in report['by_severity'].items():
            if count > 0:
                icon = "🚨" if severity == "CRITICAL" else ("⚠️" if severity == "HIGH" else "ℹ️")
                print(f"  {icon} {severity}: {count}")
        
        print(f"\n📁 Files with violations:")
        for file_path, count in report['by_file'].items():
            print(f"  • {file_path}: {count}")
        
        print(f"\n🔍 Detailed Violations:")
        for violation in report['violations']:
            severity_icon = "🚨" if violation['severity'] == "CRITICAL" else ("⚠️" if violation['severity'] == "HIGH" else "ℹ️")
            
            print(f"\n{severity_icon} {violation['severity']} - {violation['type']}")
            print(f"   File: {violation['file']}:{violation['line']}")
            print(f"   Code: {violation['content']}")
            print(f"   Match: {violation['pattern']}")
            if violation.get('context'):
                print(f"   Context: {violation['context']}")
        
        if report['by_severity'].get('CRITICAL', 0) + report['by_severity'].get('HIGH', 0) > 0:
            print(f"\n🚨 REMEDIATION REQUIRED:")
            print("1. Replace hardcoded credentials with environment variables")
            print("2. Use os.getenv('REDIS_PASSWORD') instead of hardcoded values")
            print("3. Add credentials to ~/.env file (not committed to git)")
            print("4. Update sample.env to use placeholder values")


def main():
    """Main scanning function."""
    scanner = FinalCredentialScanner()
    
    # Determine scan directory
    scan_dir = Path.cwd()
    if len(sys.argv) > 1 and Path(sys.argv[1]).exists():
        scan_dir = Path(sys.argv[1])
    
    print(f"🔍 Scanning {scan_dir} for hardcoded credentials...")
    print("🎯 Focusing on real violations, filtering test files...")
    
    # Scan for violations
    violations = scanner.scan_directory(scan_dir)
    
    # Generate and print report
    report = scanner.generate_report(violations)
    scanner.print_report(report)
    
    # Save detailed report
    report_file = "final_credential_scan_report.json"
    with open(report_file, 'w') as f:
        json.dump(report, f, indent=2)
    print(f"\n📄 Detailed report saved to: {report_file}")
    
    # Exit with appropriate code
    if report['status'] in ['CRITICAL', 'HIGH']:
        print(f"\n❌ Scan failed due to {report['status']} severity violations")
        sys.exit(1)
    else:
        print(f"\n✅ Scan passed")
        sys.exit(0)


if __name__ == "__main__":
    main()