#!/usr/bin/env python3
"""
Comprehensive Security Validator

This script performs thorough security validation to ensure:
1. No hardcoded credentials remain in the repository
2. All configuration uses environment variables or example templates
3. Security compliance with zero-tolerance credential policy
"""

import os
import re
import json
import logging
from pathlib import Path
from typing import List, Dict, Set, Tuple, Optional
from dataclasses import dataclass, field
from enum import Enum

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class SecuritySeverity(Enum):
    """Security issue severity levels"""
    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"
    INFO = "INFO"

class SecurityIssueType(Enum):
    """Types of security issues"""
    HARDCODED_PASSWORD = "HARDCODED_PASSWORD"
    HARDCODED_API_KEY = "HARDCODED_API_KEY"
    HARDCODED_TOKEN = "HARDCODED_TOKEN"
    HARDCODED_SECRET = "HARDCODED_SECRET"
    HARDCODED_CONNECTION_STRING = "HARDCODED_CONNECTION_STRING"
    INSECURE_DEFAULT = "INSECURE_DEFAULT"
    MISSING_ENV_VAR_VALIDATION = "MISSING_ENV_VAR_VALIDATION"
    CREDENTIAL_IN_COMMENT = "CREDENTIAL_IN_COMMENT"
    CREDENTIAL_IN_DOCUMENTATION = "CREDENTIAL_IN_DOCUMENTATION"

@dataclass
class SecurityIssue:
    """Represents a security issue found during scanning"""
    file_path: str
    line_number: int
    line_content: str
    issue_type: SecurityIssueType
    severity: SecuritySeverity
    description: str
    suggested_fix: str
    pattern_matched: str

@dataclass
class SecurityReport:
    """Comprehensive security validation report"""
    total_files_scanned: int = 0
    total_issues: int = 0
    critical_issues: List[SecurityIssue] = field(default_factory=list)
    high_issues: List[SecurityIssue] = field(default_factory=list)
    medium_issues: List[SecurityIssue] = field(default_factory=list)
    low_issues: List[SecurityIssue] = field(default_factory=list)
    info_issues: List[SecurityIssue] = field(default_factory=list)
    files_with_issues: Set[str] = field(default_factory=set)
    compliant_files: Set[str] = field(default_factory=set)
    
    def add_issue(self, issue: SecurityIssue):
        """Add a security issue to the report"""
        self.total_issues += 1
        self.files_with_issues.add(issue.file_path)
        
        if issue.severity == SecuritySeverity.CRITICAL:
            self.critical_issues.append(issue)
        elif issue.severity == SecuritySeverity.HIGH:
            self.high_issues.append(issue)
        elif issue.severity == SecuritySeverity.MEDIUM:
            self.medium_issues.append(issue)
        elif issue.severity == SecuritySeverity.LOW:
            self.low_issues.append(issue)
        else:
            self.info_issues.append(issue)

class ComprehensiveSecurityValidator:
    """Comprehensive security validator for the entire repository"""
    
    def __init__(self, root_path: str = "."):
        self.root_path = Path(root_path)
        self.report = SecurityReport()
        
        # Critical credential patterns - these are NEVER allowed
        self.critical_patterns = [
            # Redis passwords (the specific incident we're preventing)
            (r'redis_password\s*=\s*["\']([^"\']+)["\']', SecurityIssueType.HARDCODED_PASSWORD, 
             "Hardcoded Redis password detected", "Use os.getenv('REDIS_PASSWORD')"),
            (r'password\s*=\s*["\']beastmode\d+["\']', SecurityIssueType.HARDCODED_PASSWORD,
             "Hardcoded Beast Mode password detected", "Use environment variable"),
            
            # API Keys
            (r'api_key\s*=\s*["\']sk-[a-zA-Z0-9]+["\']', SecurityIssueType.HARDCODED_API_KEY,
             "Hardcoded OpenAI API key detected", "Use os.getenv('OPENAI_API_KEY')"),
            (r'anthropic.*key\s*=\s*["\'][^"\']+["\']', SecurityIssueType.HARDCODED_API_KEY,
             "Hardcoded Anthropic API key detected", "Use os.getenv('ANTHROPIC_API_KEY')"),
            
            # Generic secrets
            (r'secret\s*=\s*["\'](?!.*\$\{|.*getenv)[^"\']{8,}["\']', SecurityIssueType.HARDCODED_SECRET,
             "Hardcoded secret detected", "Use environment variable"),
            (r'token\s*=\s*["\'](?!.*\$\{|.*getenv)[^"\']{16,}["\']', SecurityIssueType.HARDCODED_TOKEN,
             "Hardcoded token detected", "Use environment variable"),
        ]
        
        # High severity patterns
        self.high_patterns = [
            # Connection strings with embedded credentials
            (r'postgresql://[^:]+:[^@]+@', SecurityIssueType.HARDCODED_CONNECTION_STRING,
             "Database connection string with embedded credentials", "Use environment variables"),
            (r'mysql://[^:]+:[^@]+@', SecurityIssueType.HARDCODED_CONNECTION_STRING,
             "MySQL connection string with embedded credentials", "Use environment variables"),
            
            # Default credential values
            (r'getenv\(["\'][^"\']+["\'],\s*["\'][^"\']+["\']', SecurityIssueType.INSECURE_DEFAULT,
             "Environment variable with insecure default value", "Remove default or use empty string"),
        ]
        
        # Medium severity patterns
        self.medium_patterns = [
            # Missing environment variable validation
            (r'os\.getenv\(["\'][^"\']+["\']\)(?!\s*or\s|\s*if\s)', SecurityIssueType.MISSING_ENV_VAR_VALIDATION,
             "Environment variable used without validation", "Add validation for required variables"),
        ]
        
        # Files to exclude from scanning
        self.excluded_patterns = [
            r'\.git/',
            r'__pycache__/',
            r'\.pyc$',
            r'node_modules/',
            r'\.env$',  # .env files are expected to have credentials
            r'\.env\.example$',  # Example files are OK
            r'\.secrets\.baseline$',  # Secrets baseline is OK
            r'\.security_cleanup_backup/',  # Backup directory
        ]
        
        # File extensions to scan
        self.scannable_extensions = {'.py', '.js', '.ts', '.json', '.yaml', '.yml', '.md', '.txt', '.sh', '.bat'}
    
    def should_scan_file(self, file_path: Path) -> bool:
        """Determine if a file should be scanned for security issues"""
        file_str = str(file_path)
        
        # Check excluded patterns
        for pattern in self.excluded_patterns:
            if re.search(pattern, file_str):
                return False
        
        # Check if file extension is scannable
        return file_path.suffix.lower() in self.scannable_extensions
    
    def scan_file_content(self, file_path: Path) -> List[SecurityIssue]:
        """Scan a single file for security issues"""
        issues = []
        
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                lines = f.readlines()
        except Exception as e:
            logger.warning(f"Could not read file {file_path}: {e}")
            return issues
        
        for line_num, line in enumerate(lines, 1):
            line_content = line.strip()
            
            # Skip empty lines and comments (but scan comments for credentials)
            if not line_content:
                continue
            
            # Check critical patterns
            for pattern, issue_type, description, fix in self.critical_patterns:
                if re.search(pattern, line_content, re.IGNORECASE):
                    issues.append(SecurityIssue(
                        file_path=str(file_path),
                        line_number=line_num,
                        line_content=line_content,
                        issue_type=issue_type,
                        severity=SecuritySeverity.CRITICAL,
                        description=description,
                        suggested_fix=fix,
                        pattern_matched=pattern
                    ))
            
            # Check high severity patterns
            for pattern, issue_type, description, fix in self.high_patterns:
                if re.search(pattern, line_content, re.IGNORECASE):
                    issues.append(SecurityIssue(
                        file_path=str(file_path),
                        line_number=line_num,
                        line_content=line_content,
                        issue_type=issue_type,
                        severity=SecuritySeverity.HIGH,
                        description=description,
                        suggested_fix=fix,
                        pattern_matched=pattern
                    ))
            
            # Check medium severity patterns
            for pattern, issue_type, description, fix in self.medium_patterns:
                if re.search(pattern, line_content, re.IGNORECASE):
                    issues.append(SecurityIssue(
                        file_path=str(file_path),
                        line_number=line_num,
                        line_content=line_content,
                        issue_type=issue_type,
                        severity=SecuritySeverity.MEDIUM,
                        description=description,
                        suggested_fix=fix,
                        pattern_matched=pattern
                    ))
        
        return issues
    
    def validate_repository(self) -> SecurityReport:
        """Perform comprehensive security validation of the repository"""
        logger.info("Starting comprehensive security validation...")
        
        # Scan all files in the repository
        for file_path in self.root_path.rglob('*'):
            if file_path.is_file() and self.should_scan_file(file_path):
                self.report.total_files_scanned += 1
                
                issues = self.scan_file_content(file_path)
                
                if issues:
                    for issue in issues:
                        self.report.add_issue(issue)
                else:
                    self.report.compliant_files.add(str(file_path))
        
        logger.info(f"Security validation complete. Scanned {self.report.total_files_scanned} files.")
        logger.info(f"Found {self.report.total_issues} security issues in {len(self.report.files_with_issues)} files.")
        
        return self.report
    
    def generate_report(self) -> Dict:
        """Generate a comprehensive security report"""
        return {
            "summary": {
                "total_files_scanned": self.report.total_files_scanned,
                "total_issues": self.report.total_issues,
                "critical_issues": len(self.report.critical_issues),
                "high_issues": len(self.report.high_issues),
                "medium_issues": len(self.report.medium_issues),
                "low_issues": len(self.report.low_issues),
                "info_issues": len(self.report.info_issues),
                "files_with_issues": len(self.report.files_with_issues),
                "compliant_files": len(self.report.compliant_files),
                "compliance_rate": len(self.report.compliant_files) / self.report.total_files_scanned * 100 if self.report.total_files_scanned > 0 else 0
            },
            "critical_issues": [
                {
                    "file": issue.file_path,
                    "line": issue.line_number,
                    "content": issue.line_content,
                    "type": issue.issue_type.value,
                    "description": issue.description,
                    "fix": issue.suggested_fix
                }
                for issue in self.report.critical_issues
            ],
            "high_issues": [
                {
                    "file": issue.file_path,
                    "line": issue.line_number,
                    "content": issue.line_content,
                    "type": issue.issue_type.value,
                    "description": issue.description,
                    "fix": issue.suggested_fix
                }
                for issue in self.report.high_issues
            ],
            "files_with_issues": sorted(list(self.report.files_with_issues)),
            "compliant_files": sorted(list(self.report.compliant_files))
        }
    
    def print_report(self):
        """Print a human-readable security report"""
        print("\n" + "="*80)
        print("COMPREHENSIVE SECURITY VALIDATION REPORT")
        print("="*80)
        
        print(f"\nSUMMARY:")
        print(f"  Files Scanned: {self.report.total_files_scanned}")
        print(f"  Total Issues: {self.report.total_issues}")
        print(f"  Critical Issues: {len(self.report.critical_issues)}")
        print(f"  High Issues: {len(self.report.high_issues)}")
        print(f"  Medium Issues: {len(self.report.medium_issues)}")
        print(f"  Files with Issues: {len(self.report.files_with_issues)}")
        print(f"  Compliant Files: {len(self.report.compliant_files)}")
        
        compliance_rate = len(self.report.compliant_files) / self.report.total_files_scanned * 100 if self.report.total_files_scanned > 0 else 0
        print(f"  Compliance Rate: {compliance_rate:.1f}%")
        
        # Print critical issues (these MUST be fixed)
        if self.report.critical_issues:
            print(f"\n🚨 CRITICAL ISSUES (MUST FIX IMMEDIATELY):")
            for issue in self.report.critical_issues:
                print(f"  ❌ {issue.file_path}:{issue.line_number}")
                print(f"     {issue.description}")
                print(f"     Line: {issue.line_content}")
                print(f"     Fix: {issue.suggested_fix}")
                print()
        
        # Print high issues
        if self.report.high_issues:
            print(f"\n⚠️  HIGH SEVERITY ISSUES:")
            for issue in self.report.high_issues:
                print(f"  ⚠️  {issue.file_path}:{issue.line_number}")
                print(f"     {issue.description}")
                print(f"     Fix: {issue.suggested_fix}")
                print()
        
        # Security status
        if self.report.critical_issues or self.report.high_issues:
            print(f"\n❌ SECURITY STATUS: FAILED")
            print(f"   Repository contains {len(self.report.critical_issues)} critical and {len(self.report.high_issues)} high severity security issues.")
            print(f"   These MUST be resolved before public release.")
        else:
            print(f"\n✅ SECURITY STATUS: PASSED")
            print(f"   No critical or high severity security issues detected.")
        
        print("\n" + "="*80)

def main():
    """Main function to run comprehensive security validation"""
    validator = ComprehensiveSecurityValidator()
    
    # Perform validation
    report = validator.validate_repository()
    
    # Print human-readable report
    validator.print_report()
    
    # Save detailed report to file
    report_data = validator.generate_report()
    report_file = Path("data/comprehensive_security_validation_report.json")
    report_file.parent.mkdir(exist_ok=True)
    
    with open(report_file, 'w') as f:
        json.dump(report_data, f, indent=2)
    
    print(f"\nDetailed report saved to: {report_file}")
    
    # Exit with error code if critical or high issues found
    if report.critical_issues or report.high_issues:
        print(f"\n🚨 SECURITY VALIDATION FAILED")
        print(f"   Found {len(report.critical_issues)} critical and {len(report.high_issues)} high severity issues.")
        print(f"   Repository is NOT ready for public release.")
        return 1
    else:
        print(f"\n✅ SECURITY VALIDATION PASSED")
        print(f"   Repository meets security compliance requirements.")
        return 0

if __name__ == "__main__":
    exit(main())