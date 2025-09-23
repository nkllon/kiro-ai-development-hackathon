"""
Security Core

This module was extracted from security.py
as part of RM-DDD compliance refactoring.
"""

import re
import hashlib
from typing import List, Dict, Any, Optional, Set
from pathlib import Path
import logging
from ..core.interfaces import GhostbustersExpertAgent
from ..core.models import (
    AnalysisResult,
    AnalysisContext,
    Finding,
    Recommendation,
    FindingType,
    Severity,
    CodeLocation,
)
import stat


class SecurityExpert(GhostbustersExpertAgent):
    """
    Expert agent for security analysis.

    Analyzes code for security vulnerabilities, insecure patterns,
    and adherence to security best practices with confidence scoring.
    """

    def __init__(self, name: str = "SecurityExpert", version: str = "1.0.0"):
        super().__init__(name, version)
        self._capabilities = [
            "vulnerability_detection",
            "injection_analysis",
            "authentication_analysis",
            "authorization_analysis",
            "cryptography_analysis",
            "input_validation_analysis",
            "secret_detection",
            "dependency_analysis",
        ]
        self._init_security_patterns()
        logger.info(f"SecurityExpert {version} initialized")

    def _init_security_patterns(self):
        """Initialize security vulnerability patterns"""
        self.sql_injection_patterns = [
            "execute\\s*\\(\\s*[\"\\'].*\\+.*[\"\\']",
            "query\\s*\\(\\s*[\"\\'].*\\+.*[\"\\']",
            "SELECT\\s+.*\\+.*FROM",
            "INSERT\\s+.*\\+.*VALUES",
            "UPDATE\\s+.*SET.*\\+",
            "DELETE\\s+.*WHERE.*\\+",
        ]
        self.xss_patterns = [
            "innerHTML\\s*=\\s*.*\\+",
            "document\\.write\\s*\\(",
            "eval\\s*\\(",
            "setTimeout\\s*\\(\\s*[\"\\'].*\\+",
            "setInterval\\s*\\(\\s*[\"\\'].*\\+",
        ]
        self.command_injection_patterns = [
            "os\\.system\\s*\\(\\s*.*\\+",
            "subprocess\\.\\w+\\s*\\(\\s*.*\\+",
            "exec\\s*\\(\\s*.*\\+",
            "shell_exec\\s*\\(\\s*.*\\+",
        ]
        self.secret_patterns = [
            ("password\\s*=\\s*[\"\\'][^\"\\']{8,}[\"\\']", "hardcoded_password"),
            ("api_key\\s*=\\s*[\"\\'][^\"\\']{16,}[\"\\']", "hardcoded_api_key"),
            ("secret\\s*=\\s*[\"\\'][^\"\\']{16,}[\"\\']", "hardcoded_secret"),
            ("token\\s*=\\s*[\"\\'][^\"\\']{20,}[\"\\']", "hardcoded_token"),
            ("private_key\\s*=\\s*[\"\\']-----BEGIN", "hardcoded_private_key"),
        ]
        self.crypto_patterns = [
            ("md5\\s*\\(", "weak_hash_md5"),
            ("sha1\\s*\\(", "weak_hash_sha1"),
            ("DES\\s*\\(", "weak_cipher_des"),
            ("RC4\\s*\\(", "weak_cipher_rc4"),
            ("random\\(\\)", "weak_random"),
        ]
        self.path_traversal_patterns = [
            "\\.\\./.*\\.\\.",
            "\\.\\.\\\\.*\\.\\.",
            "file:///",
            "/etc/passwd",
            "/etc/shadow",
        ]

    async def analyze(self, context: AnalysisContext) -> AnalysisResult:
        """
        Perform comprehensive security analysis.

        Args:
            context: Analysis context with target path and configuration

        Returns:
            AnalysisResult with security findings and recommendations
        """
        start_time = __import__("time").time()
        findings = []
        recommendations = []
        try:
            target_path = Path(context.target_path)
            if not target_path.exists():
                raise FileNotFoundError(f"Target file not found: {target_path}")
            if target_path.is_dir():
                findings.extend(await self._analyze_directory(target_path))
            else:
                findings.extend(await self._analyze_file(target_path))
            recommendations = await self._generate_security_recommendations(findings)
            confidence = self._calculate_security_confidence(findings, target_path)
            analysis_duration = __import__("time").time() - start_time
            result = AnalysisResult(
                agent_name=self.name,
                confidence=confidence,
                findings=findings,
                recommendations=recommendations,
                analysis_duration=analysis_duration,
                context=context,
                metadata={
                    "security_checks_performed": self._get_checks_performed(),
                    "vulnerability_categories": self._get_vulnerability_categories(
                        findings
                    ),
                    "risk_level": self._calculate_risk_level(findings),
                },
            )
            logger.info(
                f"Security analysis completed for {target_path} with {len(findings)} findings"
            )
            return result
        except Exception as e:
            logger.error(
                f"Security analysis failed for {context.target_path}: {str(e)}"
            )
            analysis_duration = __import__("time").time() - start_time
            return AnalysisResult(
                agent_name=self.name,
                confidence=0.0,
                findings=[
                    Finding(
                        type=FindingType.SECURITY_VULNERABILITY,
                        severity=Severity.CRITICAL,
                        description=f"Security analysis failed: {str(e)}",
                        confidence=1.0,
                    )
                ],
                recommendations=[
                    Recommendation(
                        title="Fix Analysis Error",
                        description=f"Resolve the issue preventing security analysis: {str(e)}",
                        priority=Severity.CRITICAL,
                    )
                ],
                analysis_duration=analysis_duration,
                context=context,
            )

    def get_capabilities(self) -> List[str]:
        """Return list of security analysis capabilities"""
        return self._capabilities.copy()

    def validate_confidence(self, result: AnalysisResult) -> bool:
        """Validate confidence score accuracy"""
        if not 0.0 <= result.confidence <= 1.0:
            return False
        if result.confidence > 0.8:
            return "security_checks_performed" in result.metadata
        if result.confidence < 0.3:
            return any((f.severity == Severity.CRITICAL for f in result.findings))
        return True

    async def _analyze_directory(self, directory: Path) -> List[Finding]:
        """Analyze directory for security issues"""
        findings = []
        for file_path in directory.rglob("*"):
            if file_path.is_file() and self._should_analyze_file(file_path):
                try:
                    findings.extend(await self._analyze_file(file_path))
                except Exception as e:
                    logger.warning(f"Failed to analyze {file_path}: {str(e)}")
        return findings

    async def _analyze_file(self, file_path: Path) -> List[Finding]:
        """Analyze single file for security vulnerabilities"""
        findings = []
        try:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()
            findings.extend(self._check_sql_injection(content, file_path))
            findings.extend(self._check_xss_vulnerabilities(content, file_path))
            findings.extend(self._check_command_injection(content, file_path))
            findings.extend(self._check_hardcoded_secrets(content, file_path))
            findings.extend(self._check_crypto_issues(content, file_path))
            findings.extend(self._check_path_traversal(content, file_path))
            findings.extend(self._check_file_permissions(file_path))
            file_extension = file_path.suffix.lower()
            if file_extension == ".py":
                findings.extend(self._check_python_security(content, file_path))
            elif file_extension in [".js", ".ts"]:
                findings.extend(self._check_javascript_security(content, file_path))
            elif file_extension == ".java":
                findings.extend(self._check_java_security(content, file_path))
        except Exception as e:
            findings.append(
                Finding(
                    type=FindingType.SECURITY_VULNERABILITY,
                    severity=Severity.MEDIUM,
                    location=CodeLocation(str(file_path), 1),
                    description=f"Could not analyze file for security issues: {str(e)}",
                    confidence=0.8,
                )
            )
        return findings

    def _check_sql_injection(self, content: str, file_path: Path) -> List[Finding]:
        """Check for SQL injection vulnerabilities"""
        findings = []
        lines = content.splitlines()
        for line_num, line in enumerate(lines, 1):
            for pattern in self.sql_injection_patterns:
                if re.search(pattern, line, re.IGNORECASE):
                    findings.append(
                        Finding(
                            type=FindingType.SECURITY_VULNERABILITY,
                            severity=Severity.HIGH,
                            location=CodeLocation(str(file_path), line_num),
                            description="Potential SQL injection vulnerability detected",
                            confidence=0.8,
                            evidence={
                                "vulnerability_type": "sql_injection",
                                "pattern_matched": pattern,
                                "line_content": line.strip(),
                            },
                        )
                    )
        return findings

    def _check_xss_vulnerabilities(
        self, content: str, file_path: Path
    ) -> List[Finding]:
        """Check for XSS vulnerabilities"""
        findings = []
        lines = content.splitlines()
        for line_num, line in enumerate(lines, 1):
            for pattern in self.xss_patterns:
                if re.search(pattern, line, re.IGNORECASE):
                    findings.append(
                        Finding(
                            type=FindingType.SECURITY_VULNERABILITY,
                            severity=Severity.HIGH,
                            location=CodeLocation(str(file_path), line_num),
                            description="Potential XSS vulnerability detected",
                            confidence=0.7,
                            evidence={
                                "vulnerability_type": "xss",
                                "pattern_matched": pattern,
                                "line_content": line.strip(),
                            },
                        )
                    )
        return findings

    def _check_command_injection(self, content: str, file_path: Path) -> List[Finding]:
        """Check for command injection vulnerabilities"""
        findings = []
        lines = content.splitlines()
        for line_num, line in enumerate(lines, 1):
            for pattern in self.command_injection_patterns:
                if re.search(pattern, line, re.IGNORECASE):
                    findings.append(
                        Finding(
                            type=FindingType.SECURITY_VULNERABILITY,
                            severity=Severity.CRITICAL,
                            location=CodeLocation(str(file_path), line_num),
                            description="Potential command injection vulnerability detected",
                            confidence=0.8,
                            evidence={
                                "vulnerability_type": "command_injection",
                                "pattern_matched": pattern,
                                "line_content": line.strip(),
                            },
                        )
                    )
        return findings

    def _check_hardcoded_secrets(self, content: str, file_path: Path) -> List[Finding]:
        """Check for hardcoded secrets and credentials"""
        findings = []
        lines = content.splitlines()
        for line_num, line in enumerate(lines, 1):
            for pattern, secret_type in self.secret_patterns:
                if re.search(pattern, line, re.IGNORECASE):
                    findings.append(
                        Finding(
                            type=FindingType.SECURITY_VULNERABILITY,
                            severity=Severity.HIGH,
                            location=CodeLocation(str(file_path), line_num),
                            description=f"Hardcoded {secret_type.replace('_', ' ')} detected",
                            confidence=0.9,
                            evidence={
                                "vulnerability_type": "hardcoded_secret",
                                "secret_type": secret_type,
                                "line_content": line.strip(),
                            },
                        )
                    )
        return findings

    def _check_crypto_issues(self, content: str, file_path: Path) -> List[Finding]:
        """Check for cryptographic issues"""
        findings = []
        lines = content.splitlines()
        for line_num, line in enumerate(lines, 1):
            for pattern, crypto_issue in self.crypto_patterns:
                if re.search(pattern, line, re.IGNORECASE):
                    findings.append(
                        Finding(
                            type=FindingType.SECURITY_VULNERABILITY,
                            severity=Severity.MEDIUM,
                            location=CodeLocation(str(file_path), line_num),
                            description=f"Insecure cryptographic practice: {crypto_issue.replace('_', ' ')}",
                            confidence=0.8,
                            evidence={
                                "vulnerability_type": "crypto_issue",
                                "issue_type": crypto_issue,
                                "line_content": line.strip(),
                            },
                        )
                    )
        return findings

    def _check_path_traversal(self, content: str, file_path: Path) -> List[Finding]:
        """Check for path traversal vulnerabilities"""
        findings = []
        lines = content.splitlines()
        for line_num, line in enumerate(lines, 1):
            for pattern in self.path_traversal_patterns:
                if re.search(pattern, line):
                    findings.append(
                        Finding(
                            type=FindingType.SECURITY_VULNERABILITY,
                            severity=Severity.HIGH,
                            location=CodeLocation(str(file_path), line_num),
                            description="Potential path traversal vulnerability detected",
                            confidence=0.7,
                            evidence={
                                "vulnerability_type": "path_traversal",
                                "pattern_matched": pattern,
                                "line_content": line.strip(),
                            },
                        )
                    )
        return findings

    def _check_file_permissions(self, file_path: Path) -> List[Finding]:
        """Check file permissions for security issues"""
        findings = []
        try:
            import stat

            file_stat = file_path.stat()
            if file_stat.st_mode & stat.S_IWOTH:
                findings.append(
                    Finding(
                        type=FindingType.SECURITY_VULNERABILITY,
                        severity=Severity.MEDIUM,
                        location=CodeLocation(str(file_path), 1),
                        description="File is world-writable (security risk)",
                        confidence=0.9,
                        evidence={
                            "vulnerability_type": "file_permissions",
                            "permissions": oct(file_stat.st_mode)[-3:],
                        },
                    )
                )
            if (
                file_path.suffix.lower() in [".sh", ".bat", ".cmd", ".exe"]
                and file_stat.st_mode & stat.S_IXUSR
            ):
                findings.append(
                    Finding(
                        type=FindingType.SECURITY_VULNERABILITY,
                        severity=Severity.LOW,
                        location=CodeLocation(str(file_path), 1),
                        description="Executable file detected - verify necessity",
                        confidence=0.6,
                        evidence={
                            "vulnerability_type": "executable_file",
                            "file_extension": file_path.suffix,
                        },
                    )
                )
        except Exception as e:
            logger.debug(f"Could not check permissions for {file_path}: {str(e)}")
        return findings

    def _check_python_security(self, content: str, file_path: Path) -> List[Finding]:
        """Python-specific security checks"""
        findings = []
        lines = content.splitlines()
        python_patterns = [
            ("pickle\\.loads?\\s*\\(", "unsafe_deserialization", Severity.HIGH),
            ("yaml\\.load\\s*\\(", "unsafe_yaml_load", Severity.HIGH),
            ("input\\s*\\(\\s*\\)", "unsafe_input", Severity.MEDIUM),
            ("__import__\\s*\\(", "dynamic_import", Severity.MEDIUM),
        ]
        for line_num, line in enumerate(lines, 1):
            for pattern, issue_type, severity in python_patterns:
                if re.search(pattern, line):
                    findings.append(
                        Finding(
                            type=FindingType.SECURITY_VULNERABILITY,
                            severity=severity,
                            location=CodeLocation(str(file_path), line_num),
                            description=f"Python security issue: {issue_type.replace('_', ' ')}",
                            confidence=0.8,
                            evidence={
                                "vulnerability_type": issue_type,
                                "language": "python",
                                "line_content": line.strip(),
                            },
                        )
                    )
        return findings

    def _check_javascript_security(
        self, content: str, file_path: Path
    ) -> List[Finding]:
        """JavaScript-specific security checks"""
        findings = []
        lines = content.splitlines()
        js_patterns = [
            (
                "localStorage\\.setItem\\s*\\(\\s*[\"\\'][^\"\\']*password",
                "password_in_localstorage",
                Severity.HIGH,
            ),
            (
                "sessionStorage\\.setItem\\s*\\(\\s*[\"\\'][^\"\\']*password",
                "password_in_sessionstorage",
                Severity.HIGH,
            ),
            ("window\\.location\\.href\\s*=.*\\+", "open_redirect", Severity.MEDIUM),
            ("postMessage\\s*\\(\\s*.*\\*", "unsafe_postmessage", Severity.MEDIUM),
        ]
        for line_num, line in enumerate(lines, 1):
            for pattern, issue_type, severity in js_patterns:
                if re.search(pattern, line, re.IGNORECASE):
                    findings.append(
                        Finding(
                            type=FindingType.SECURITY_VULNERABILITY,
                            severity=severity,
                            location=CodeLocation(str(file_path), line_num),
                            description=f"JavaScript security issue: {issue_type.replace('_', ' ')}",
                            confidence=0.7,
                            evidence={
                                "vulnerability_type": issue_type,
                                "language": "javascript",
                                "line_content": line.strip(),
                            },
                        )
                    )
        return findings

    def _check_java_security(self, content: str, file_path: Path) -> List[Finding]:
        """Java-specific security checks"""
        findings = []
        lines = content.splitlines()
        java_patterns = [
            ("Runtime\\.getRuntime\\(\\)\\.exec", "runtime_exec", Severity.HIGH),
            ("ObjectInputStream\\s*\\(", "unsafe_deserialization", Severity.HIGH),
            ("Random\\s*\\(\\s*\\)", "weak_random", Severity.MEDIUM),
            (
                "MessageDigest\\.getInstance\\s*\\(\\s*[\"\\']MD5",
                "weak_hash",
                Severity.MEDIUM,
            ),
        ]
        for line_num, line in enumerate(lines, 1):
            for pattern, issue_type, severity in java_patterns:
                if re.search(pattern, line):
                    findings.append(
                        Finding(
                            type=FindingType.SECURITY_VULNERABILITY,
                            severity=severity,
                            location=CodeLocation(str(file_path), line_num),
                            description=f"Java security issue: {issue_type.replace('_', ' ')}",
                            confidence=0.8,
                            evidence={
                                "vulnerability_type": issue_type,
                                "language": "java",
                                "line_content": line.strip(),
                            },
                        )
                    )
        return findings

    async def _generate_security_recommendations(
        self, findings: List[Finding]
    ) -> List[Recommendation]:
        """Generate security-specific recommendations"""
        recommendations = []
        vuln_types = {}
        for finding in findings:
            vuln_type = finding.evidence.get("vulnerability_type", "unknown")
            if vuln_type not in vuln_types:
                vuln_types[vuln_type] = []
            vuln_types[vuln_type].append(finding)
        for vuln_type, vuln_findings in vuln_types.items():
            if vuln_type == "sql_injection":
                recommendations.append(
                    Recommendation(
                        title="Fix SQL Injection Vulnerabilities",
                        description=f"Use parameterized queries or prepared statements for {len(vuln_findings)} SQL injection issue(s)",
                        priority=Severity.HIGH,
                        effort_estimate="30-60 minutes per issue",
                        automated_fix_available=False,
                    )
                )
            elif vuln_type == "xss":
                recommendations.append(
                    Recommendation(
                        title="Fix XSS Vulnerabilities",
                        description=f"Implement proper input sanitization and output encoding for {len(vuln_findings)} XSS issue(s)",
                        priority=Severity.HIGH,
                        effort_estimate="20-40 minutes per issue",
                        automated_fix_available=False,
                    )
                )
            elif vuln_type == "hardcoded_secret":
                recommendations.append(
                    Recommendation(
                        title="Remove Hardcoded Secrets",
                        description=f"Move {len(vuln_findings)} hardcoded secret(s) to environment variables or secure configuration",
                        priority=Severity.HIGH,
                        effort_estimate="15-30 minutes per secret",
                        automated_fix_available=True,
                        fix_command="externalize_secrets",
                    )
                )
            elif vuln_type == "command_injection":
                recommendations.append(
                    Recommendation(
                        title="Fix Command Injection Vulnerabilities",
                        description=f"Use safe command execution methods for {len(vuln_findings)} command injection issue(s)",
                        priority=Severity.CRITICAL,
                        effort_estimate="45-90 minutes per issue",
                        automated_fix_available=False,
                    )
                )
        return recommendations

    def _should_analyze_file(self, file_path: Path) -> bool:
        """Determine if file should be analyzed for security issues"""
        skip_extensions = {
            ".jpg",
            ".jpeg",
            ".png",
            ".gif",
            ".pdf",
            ".zip",
            ".tar",
            ".gz",
        }
        if file_path.suffix.lower() in skip_extensions:
            return False
        try:
            if file_path.stat().st_size > 10 * 1024 * 1024:
                return False
        except:
            pass
        return True

    def _calculate_security_confidence(
        self, findings: List[Finding], target_path: Path
    ) -> float:
        """Calculate confidence score for security analysis"""
        base_confidence = 0.8
        if target_path.is_dir():
            base_confidence = 0.7
        if findings:
            avg_finding_confidence = sum((f.confidence for f in findings)) / len(
                findings
            )
            base_confidence = (base_confidence + avg_finding_confidence) / 2
        return min(1.0, max(0.0, base_confidence))

    def _get_checks_performed(self) -> List[str]:
        """Get list of security checks performed"""
        return [
            "sql_injection",
            "xss_vulnerabilities",
            "command_injection",
            "hardcoded_secrets",
            "crypto_issues",
            "path_traversal",
            "file_permissions",
            "language_specific_checks",
        ]

    def _get_vulnerability_categories(self, findings: List[Finding]) -> List[str]:
        """Get unique vulnerability categories from findings"""
        categories = set()
        for finding in findings:
            vuln_type = finding.evidence.get("vulnerability_type", "unknown")
            categories.add(vuln_type)
        return list(categories)

    def _calculate_risk_level(self, findings: List[Finding]) -> str:
        """Calculate overall risk level based on findings"""
        if not findings:
            return "low"
        critical_count = sum((1 for f in findings if f.severity == Severity.CRITICAL))
        high_count = sum((1 for f in findings if f.severity == Severity.HIGH))
        if critical_count > 0:
            return "critical"
        elif high_count > 2:
            return "high"
        elif high_count > 0:
            return "medium"
        else:
            return "low"


def __init__(self, name: str = "SecurityExpert", version: str = "1.0.0"):
    super().__init__(name, version)
    self._capabilities = [
        "vulnerability_detection",
        "injection_analysis",
        "authentication_analysis",
        "authorization_analysis",
        "cryptography_analysis",
        "input_validation_analysis",
        "secret_detection",
        "dependency_analysis",
    ]
    self._init_security_patterns()
    logger.info(f"SecurityExpert {version} initialized")


def _init_security_patterns(self):
    """Initialize security vulnerability patterns"""
    self.sql_injection_patterns = [
        "execute\\s*\\(\\s*[\"\\'].*\\+.*[\"\\']",
        "query\\s*\\(\\s*[\"\\'].*\\+.*[\"\\']",
        "SELECT\\s+.*\\+.*FROM",
        "INSERT\\s+.*\\+.*VALUES",
        "UPDATE\\s+.*SET.*\\+",
        "DELETE\\s+.*WHERE.*\\+",
    ]
    self.xss_patterns = [
        "innerHTML\\s*=\\s*.*\\+",
        "document\\.write\\s*\\(",
        "eval\\s*\\(",
        "setTimeout\\s*\\(\\s*[\"\\'].*\\+",
        "setInterval\\s*\\(\\s*[\"\\'].*\\+",
    ]
    self.command_injection_patterns = [
        "os\\.system\\s*\\(\\s*.*\\+",
        "subprocess\\.\\w+\\s*\\(\\s*.*\\+",
        "exec\\s*\\(\\s*.*\\+",
        "shell_exec\\s*\\(\\s*.*\\+",
    ]
    self.secret_patterns = [
        ("password\\s*=\\s*[\"\\'][^\"\\']{8,}[\"\\']", "hardcoded_password"),
        ("api_key\\s*=\\s*[\"\\'][^\"\\']{16,}[\"\\']", "hardcoded_api_key"),
        ("secret\\s*=\\s*[\"\\'][^\"\\']{16,}[\"\\']", "hardcoded_secret"),
        ("token\\s*=\\s*[\"\\'][^\"\\']{20,}[\"\\']", "hardcoded_token"),
        ("private_key\\s*=\\s*[\"\\']-----BEGIN", "hardcoded_private_key"),
    ]
    self.crypto_patterns = [
        ("md5\\s*\\(", "weak_hash_md5"),
        ("sha1\\s*\\(", "weak_hash_sha1"),
        ("DES\\s*\\(", "weak_cipher_des"),
        ("RC4\\s*\\(", "weak_cipher_rc4"),
        ("random\\(\\)", "weak_random"),
    ]
    self.path_traversal_patterns = [
        "\\.\\./.*\\.\\.",
        "\\.\\.\\\\.*\\.\\.",
        "file:///",
        "/etc/passwd",
        "/etc/shadow",
    ]


def get_capabilities(self) -> List[str]:
    """Return list of security analysis capabilities"""
    return self._capabilities.copy()


def _should_analyze_file(self, file_path: Path) -> bool:
    """Determine if file should be analyzed for security issues"""
    skip_extensions = {".jpg", ".jpeg", ".png", ".gif", ".pdf", ".zip", ".tar", ".gz"}
    if file_path.suffix.lower() in skip_extensions:
        return False
    try:
        if file_path.stat().st_size > 10 * 1024 * 1024:
            return False
    except:
        pass
    return True


def _calculate_security_confidence(
    self, findings: List[Finding], target_path: Path
) -> float:
    """Calculate confidence score for security analysis"""
    base_confidence = 0.8
    if target_path.is_dir():
        base_confidence = 0.7
    if findings:
        avg_finding_confidence = sum((f.confidence for f in findings)) / len(findings)
        base_confidence = (base_confidence + avg_finding_confidence) / 2
    return min(1.0, max(0.0, base_confidence))


def _get_vulnerability_categories(self, findings: List[Finding]) -> List[str]:
    """Get unique vulnerability categories from findings"""
    categories = set()
    for finding in findings:
        vuln_type = finding.evidence.get("vulnerability_type", "unknown")
        categories.add(vuln_type)
    return list(categories)


def _calculate_risk_level(self, findings: List[Finding]) -> str:
    """Calculate overall risk level based on findings"""
    if not findings:
        return "low"
    critical_count = sum((1 for f in findings if f.severity == Severity.CRITICAL))
    high_count = sum((1 for f in findings if f.severity == Severity.HIGH))
    if critical_count > 0:
        return "critical"
    elif high_count > 2:
        return "high"
    elif high_count > 0:
        return "medium"
    else:
        return "low"
