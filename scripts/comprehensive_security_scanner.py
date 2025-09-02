#!/usr/bin/env python3
"""
Comprehensive Security Scanner - Detects credential exposure across all file types

This scanner goes beyond Bandit to detect:
- API keys and secrets in any file type
- Hardcoded credentials in documentation
- Exposed tokens in configuration files
- Security misconfigurations
- Credential patterns in text files
"""

import hashlib
import json
import logging
import re
import subprocess
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Set

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class CredentialPattern:
    """Represents a credential pattern to detect"""

    name: str
    pattern: str
    severity: str
    description: str
    examples: list[str]
    false_positive_patterns: list[str] = None


@dataclass
class SecurityFinding:
    """Represents a security finding"""

    file_path: str
    line_number: int
    pattern_name: str
    severity: str
    description: str
    matched_text: str
    context: str
    false_positive: bool = False
    hash: str = ""


class ComprehensiveSecurityScanner:
    """Comprehensive security scanner for all file types"""

    def __init__(self):
        """Initialize the comprehensive security scanner"""
        self.credential_patterns = self._load_credential_patterns()
        self.excluded_patterns = self._load_excluded_patterns()
        self.scan_results = []

    def _load_credential_patterns(self) -> list[CredentialPattern]:
        """Load credential detection patterns"""
        return [
            # API Keys
            CredentialPattern(
                name="OpenAI API Key",
                pattern=r"sk-[a-zA-Z0-9]{48}",
                severity="CRITICAL",
                description="OpenAI API key detected",
                examples=["sk-1234567890abcdef1234567890abcdef1234567890abcdef"],
                false_positive_patterns=[r"sk-test", r"sk-demo", r"YOUR_API_KEY"],
            ),
            CredentialPattern(
                name="Anthropic API Key",
                pattern=r"sk-ant-[a-zA-Z0-9]{48}",
                severity="CRITICAL",
                description="Anthropic API key detected",
                examples=["sk-ant-api03-1234567890abcdef1234567890abcdef1234567890abcdef"],
                false_positive_patterns=[
                    r"sk-ant-test",
                    r"sk-ant-demo",
                    r"YOUR_ANTHROPIC_KEY",
                ],
            ),
            CredentialPattern(
                name="Generic API Key",
                pattern=r"(?:api[_-]?key|apikey|api_key)\s*[=:]\s*['\"]?[a-zA-Z0-9]{20,}['\"]?",
                severity="HIGH",
                description="Generic API key pattern detected",
                examples=["api_key=1234567890abcdef123456", "apikey: abcdef1234567890"],
                false_positive_patterns=[
                    r"YOUR_API_KEY",
                    r"API_KEY_PLACEHOLDER",
                    r"example_key",
                ],
            ),
            # AWS Credentials
            CredentialPattern(
                name="AWS Access Key ID",
                pattern=r"AKIA[0-9A-Z]{16}",
                severity="CRITICAL",
                description="AWS access key ID detected",
                examples=["AKIA1234567890ABCDEF"],
                false_positive_patterns=[r"AKIAEXAMPLE", r"AKIA_DEMO"],
            ),
            CredentialPattern(
                name="AWS Secret Access Key",
                pattern=r"[0-9a-zA-Z/+=]{40}",
                severity="CRITICAL",
                description="AWS secret access key detected",
                examples=["1234567890abcdef1234567890abcdef1234567890"],
                false_positive_patterns=[r"EXAMPLE_KEY", r"DEMO_SECRET"],
            ),
            # Private Keys
            CredentialPattern(
                name="Private Key",
                pattern=r"-----BEGIN\s+(?:RSA\s+)?PRIVATE\s+KEY-----",
                severity="CRITICAL",
                description="Private key detected",
                examples=["-----BEGIN RSA PRIVATE KEY-----"],
                false_positive_patterns=[r"EXAMPLE_KEY", r"DEMO_KEY"],
            ),
            # Database Credentials
            CredentialPattern(
                name="Database Connection String",
                pattern=r"(?:postgresql|mysql|mongodb)://[^:\s]+:[^@\s]+@[^:\s]+",
                severity="HIGH",
                description="Database connection string with credentials detected",
                examples=["postgresql://user:password@localhost:5432/db"],
                false_positive_patterns=[
                    r"user:password",
                    r"admin:admin",
                    r"root:root",
                ],
            ),
            # OAuth Credentials
            CredentialPattern(
                name="OAuth Client Secret",
                pattern=r"client_secret\s*[=:]\s*['\"]?[a-zA-Z0-9]{32,}['\"]?",
                severity="HIGH",
                description="OAuth client secret detected",
                examples=["client_secret=abcdef1234567890abcdef1234567890"],
                false_positive_patterns=[
                    r"YOUR_CLIENT_SECRET",
                    r"CLIENT_SECRET_PLACEHOLDER",
                ],
            ),
            # JWT Tokens
            CredentialPattern(
                name="JWT Token",
                pattern=r"eyJ[A-Za-z0-9-_=]+\.[A-Za-z0-9-_=]+\.?[A-Za-z0-9-_.+/=]*",
                severity="MEDIUM",
                description="JWT token detected",
                examples=["eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c"],
                false_positive_patterns=[r"eyJ0ZXN0", r"eyJkZW1v"],
            ),
            # Generic Secrets
            CredentialPattern(
                name="Generic Secret",
                pattern=r"(?:secret|password|token|key)\s*[=:]\s*['\"]?[a-zA-Z0-9!@#$%^&*()_+\-=\[\]{}|;:,.<>?]{8,}['\"]?",
                severity="MEDIUM",
                description="Generic secret pattern detected",
                examples=["secret=mysecret123", "password: mypassword"],
                false_positive_patterns=[
                    r"YOUR_SECRET",
                    r"SECRET_PLACEHOLDER",
                    r"example_secret",
                ],
            ),
        ]

    def _load_excluded_patterns(self) -> set[str]:
        """Load patterns for files to exclude from scanning"""
        return {
            # Lock files
            "*.lock",
            "package-lock.json",
            "yarn.lock",
            "poetry.lock",
            "uv.lock",
            # Binary files
            "*.exe",
            "*.dll",
            "*.so",
            "*.dylib",
            "*.bin",
            "*.dat",
            # Version control
            ".git/*",
            ".gitignore",
            ".gitattributes",
            # Build artifacts
            "dist/*",
            "build/*",
            "__pycache__/*",
            "*.pyc",
            "*.pyo",
            # Temporary files
            "*.tmp",
            "*.temp",
            "*.log",
            "*.bak",
            "*.backup",
            # Coverage and test artifacts
            ".coverage",
            "coverage.xml",
            "htmlcov/*",
            ".pytest_cache/*",
            # Cache directories
            "cache/*",
            ".cache/*",
            "node_modules/*",
            ".node_modules/*",
            "*.cache",
            "cache.json",
            "api_discovery_cache.json",
            # Environment files (but scan for patterns)
            ".env.example",
            ".env.template",
        }

    def _should_exclude_file(self, file_path: Path) -> bool:
        """Check if file should be excluded from scanning"""
        for pattern in self.excluded_patterns:
            if pattern.startswith("*"):
                if file_path.name.endswith(pattern[1:]):
                    return True
            elif pattern.endswith("/*"):
                if str(file_path.parent).endswith(pattern[:-2]):
                    return True
            elif pattern == file_path.name:
                return True
        return False

    def _is_text_file(self, file_path: Path) -> bool:
        """Check if file is a text file that can be scanned"""
        try:
            with open(file_path, encoding="utf-8") as f:
                f.read(1024)  # Try to read first 1KB
                return True
        except (UnicodeDecodeError, PermissionError, FileNotFoundError):
            return False

    def _scan_file_for_credentials(self, file_path: Path) -> list[SecurityFinding]:
        """Scan a single file for credential patterns"""
        findings = []

        try:
            with open(file_path, encoding="utf-8") as f:
                content = f.read()
                lines = content.split("\n")

                for line_num, line in enumerate(lines, 1):
                    for pattern in self.credential_patterns:
                        matches = re.finditer(pattern.pattern, line, re.IGNORECASE)

                        for match in matches:
                            matched_text = match.group(0)

                            # Check if this is a false positive
                            is_false_positive = self._is_false_positive(pattern, matched_text, line, file_path)

                            # Get context around the match
                            context_start = max(0, line_num - 2)
                            context_end = min(len(lines), line_num + 1)
                            context = "\n".join(lines[context_start:context_end])

                            # Create hash of the matched text for deduplication
                            text_hash = hashlib.md5(matched_text.encode()).hexdigest()

                            finding = SecurityFinding(
                                file_path=str(file_path),
                                line_number=line_num,
                                pattern_name=pattern.name,
                                severity=pattern.severity,
                                description=pattern.description,
                                matched_text=matched_text,
                                context=context,
                                false_positive=is_false_positive,
                                hash=text_hash,
                            )

                            findings.append(finding)

        except Exception as e:
            logger.warning(f"Error scanning {file_path}: {e}")

        return findings

    def _is_false_positive(self, pattern: CredentialPattern, matched_text: str, line: str, file_path: Path) -> bool:
        """Check if a match is a false positive"""

        # Check false positive patterns
        if pattern.false_positive_patterns:
            for fp_pattern in pattern.false_positive_patterns:
                if re.search(fp_pattern, line, re.IGNORECASE):
                    return True

        # Check for common false positive indicators
        false_positive_indicators = [
            "YOUR_",
            "PLACEHOLDER",
            "EXAMPLE_",
            "DEMO_",
            "TEST_",
            "TODO:",
            "FIXME:",
            "NOTE:",
            "WARNING:",
            "example",
            "demo",
            "test",
            "placeholder",
            "template",
        ]

        for indicator in false_positive_indicators:
            if indicator.lower() in line.lower():
                return True

        # Check file path for test/example indicators
        return bool(any(indicator in str(file_path).lower() for indicator in ["test", "example", "demo", "template", "sample"]))

    def scan_project(self, project_path: str = ".") -> dict[str, Any]:
        """Scan entire project for security issues"""
        project_path = Path(project_path)
        all_findings = []
        files_scanned = 0
        files_with_issues = 0

        logger.info(f"Starting comprehensive security scan of {project_path}")

        # Scan all files in project
        for file_path in project_path.rglob("*"):
            if file_path.is_file() and not self._should_exclude_file(file_path):
                if self._is_text_file(file_path):
                    files_scanned += 1
                    findings = self._scan_file_for_credentials(file_path)

                    if findings:
                        files_with_issues += 1
                        all_findings.extend(findings)

                        # Log critical findings immediately
                        for finding in findings:
                            if finding.severity == "CRITICAL" and not finding.false_positive:
                                logger.critical(f"🚨 CRITICAL: {finding.pattern_name} in {finding.file_path}:{finding.line_number}")

        # Deduplicate findings by hash
        unique_findings = self._deduplicate_findings(all_findings)

        # Generate report
        return self._generate_report(unique_findings, files_scanned, files_with_issues)

    def _deduplicate_findings(self, findings: list[SecurityFinding]) -> list[SecurityFinding]:
        """Remove duplicate findings based on hash"""
        seen_hashes = set()
        unique_findings = []

        for finding in findings:
            if finding.hash not in seen_hashes:
                seen_hashes.add(finding.hash)
                unique_findings.append(finding)

        return unique_findings

    def _generate_report(
        self,
        findings: list[SecurityFinding],
        files_scanned: int,
        files_with_issues: int,
    ) -> dict[str, Any]:
        """Generate comprehensive security report"""

        # Group findings by severity
        findings_by_severity = {}
        for finding in findings:
            severity = finding.severity
            if severity not in findings_by_severity:
                findings_by_severity[severity] = []
            findings_by_severity[severity].append(finding)

        # Count findings by pattern
        findings_by_pattern = {}
        for finding in findings:
            pattern = finding.pattern_name
            if pattern not in findings_by_pattern:
                findings_by_pattern[pattern] = 0
            findings_by_pattern[pattern] += 1

        # Separate real issues from false positives
        real_issues = [f for f in findings if not f.false_positive]
        false_positives = [f for f in findings if f.false_positive]

        return {
            "summary": {
                "files_scanned": files_scanned,
                "files_with_issues": files_with_issues,
                "total_findings": len(findings),
                "real_issues": len(real_issues),
                "false_positives": len(false_positives),
                "scan_timestamp": str(Path.cwd() / "security_scan_report.json"),
            },
            "findings_by_severity": {severity: len(finding_list) for severity, finding_list in findings_by_severity.items()},
            "findings_by_pattern": findings_by_pattern,
            "critical_findings": [f for f in real_issues if f.severity == "CRITICAL"],
            "high_findings": [f for f in real_issues if f.severity == "HIGH"],
            "medium_findings": [f for f in real_issues if f.severity == "MEDIUM"],
            "low_findings": [f for f in real_issues if f.severity == "LOW"],
            "all_findings": [asdict(f) for f in findings],
            "recommendations": self._generate_recommendations(findings),
        }

    def _generate_recommendations(self, findings: list[SecurityFinding]) -> list[str]:
        """Generate actionable security recommendations"""
        recommendations = []

        critical_count = len([f for f in findings if f.severity == "CRITICAL" and not f.false_positive])
        high_count = len([f for f in findings if f.severity == "HIGH" and not f.false_positive])

        if critical_count > 0:
            recommendations.append(f"🚨 IMMEDIATE ACTION REQUIRED: {critical_count} critical security issues found. " "Review and fix these immediately before any deployment.")

        if high_count > 0:
            recommendations.append(f"⚠️ HIGH PRIORITY: {high_count} high-severity security issues found. " "Address these before production deployment.")

        # Pattern-specific recommendations
        pattern_counts = {}
        for finding in findings:
            if not finding.false_positive:
                pattern = finding.pattern_name
                pattern_counts[pattern] = pattern_counts.get(pattern, 0) + 1

        for pattern, count in pattern_counts.items():
            if count > 5:
                recommendations.append(f"🔍 PATTERN ALERT: {count} instances of '{pattern}' found. " "Consider implementing automated detection for this pattern.")

        if not recommendations:
            recommendations.append("✅ No immediate security issues detected. Continue with regular security practices.")

        return recommendations

    def save_report(self, report: dict[str, Any], output_file: str = "security_scan_report.json"):
        """Save security report to file"""
        try:
            with open(output_file, "w") as f:
                json.dump(report, f, indent=2)
            logger.info(f"Security report saved to {output_file}")
        except Exception as e:
            logger.error(f"Failed to save report: {e}")

    def print_summary(self, report: dict[str, Any]):
        """Print a summary of the security scan"""
        summary = report["summary"]
        findings_by_severity = report["findings_by_severity"]

        print("\n🔒 Comprehensive Security Scan Report")
        print("=" * 50)
        print(f"Files Scanned: {summary['files_scanned']}")
        print(f"Files with Issues: {summary['files_with_issues']}")
        print(f"Total Findings: {summary['total_findings']}")
        print(f"Real Issues: {summary['real_issues']}")
        print(f"False Positives: {summary['false_positives']}")

        print(f"\n📊 Findings by Severity:")
        for severity in ["CRITICAL", "HIGH", "MEDIUM", "LOW"]:
            if severity in findings_by_severity:
                count = findings_by_severity[severity]
                icon = "🚨" if severity == "CRITICAL" else "⚠️" if severity == "HIGH" else "🔍"
                print(f"  {icon} {severity}: {count}")

        print(f"\n🎯 Critical Findings: {len(report['critical_findings'])}")
        for finding in report["critical_findings"][:3]:  # Show first 3
            print(f"  🚨 {finding.pattern_name} in {finding.file_path}:{finding.line_number}")
            print(f"     {finding.matched_text[:50]}...")

        if len(report["critical_findings"]) > 3:
            print(f"  ... and {len(report['critical_findings']) - 3} more critical findings")

        print(f"\n💡 Recommendations:")
        for rec in report["recommendations"]:
            print(f"  {rec}")


def main():
    """Main entry point for the comprehensive security scanner"""
    import argparse

    parser = argparse.ArgumentParser(description="Comprehensive Security Scanner")
    parser.add_argument("--path", default=".", help="Path to scan (default: current directory)")
    parser.add_argument("--output", default="security_scan_report.json", help="Output file for report")
    parser.add_argument("--report", action="store_true", help="Print detailed report to console")

    args = parser.parse_args()

    scanner = ComprehensiveSecurityScanner()

    try:
        # Run the scan
        report = scanner.scan_project(args.path)

        # Save report
        scanner.save_report(report, args.output)

        # Print summary
        scanner.print_summary(report)

        # Exit with error code if critical issues found
        if len(report["critical_findings"]) > 0:
            print(f"\n🚨 CRITICAL SECURITY ISSUES FOUND! Exiting with error code 1")
            exit(1)
        else:
            print(f"\n✅ No critical security issues found")
            exit(0)

    except Exception as e:
        logger.error(f"Security scan failed: {e}")
        exit(1)


if __name__ == "__main__":
    main()
