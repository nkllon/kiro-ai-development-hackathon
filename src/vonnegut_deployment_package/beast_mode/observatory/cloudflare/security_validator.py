"""
Security Validator for Observatory Cloudflare Integration

Validates that Observatory whitelist rules maintain security posture
and don't create vulnerabilities or bypass important protections.
"""

import json
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from enum import Enum

from .api_client import CloudflareAPIClient, CloudflareAPIError
from .rule_manager import RuleManager, ObservatoryRule
from .traffic_analyzer import TrafficAnalyzer, TrafficPattern

logger = logging.getLogger(__name__)


class SecurityLevel(Enum):
    """Security validation levels"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


class ValidationResult(Enum):
    """Validation result status"""
    PASS = "pass"
    FAIL = "fail"
    WARNING = "warning"
    SKIP = "skip"


@dataclass
class SecurityCheck:
    """Individual security check result"""
    check_name: str
    description: str
    result: ValidationResult
    level: SecurityLevel
    details: Dict[str, Any]
    recommendations: List[str]


@dataclass
class SecurityValidationReport:
    """Complete security validation report"""
    overall_status: ValidationResult
    checks_performed: int
    checks_passed: int
    checks_failed: int
    checks_warning: int
    security_score: float
    checks: List[SecurityCheck]
    summary: str
    timestamp: datetime


class SecurityValidator:
    """
    Validates Observatory Cloudflare integration security posture
    
    Ensures that whitelist rules are specific, don't create vulnerabilities,
    and maintain protection against actual threats.
    """
    
    def __init__(self, api_client: CloudflareAPIClient, 
                 rule_manager: RuleManager,
                 traffic_analyzer: TrafficAnalyzer):
        self.api_client = api_client
        self.rule_manager = rule_manager
        self.traffic_analyzer = traffic_analyzer
        self._log_action("security_validator_init", "in_progress", {})
    
    def _log_action(self, action: str, status: str, details: Dict[str, Any]):
        """Log action in JSON format as required"""
        log_entry = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "task": "5.1",
            "action": action,
            "status": status,
            "details": details
        }
        print(json.dumps(log_entry))
        logger.info(f"Security Validator action: {action} - {status}")
    
    async def validate_observatory_integration(self) -> SecurityValidationReport:
        """
        Perform comprehensive security validation of Observatory integration
        
        Returns:
            SecurityValidationReport with all validation results
        """
        self._log_action("validate_observatory_integration", "in_progress", {})
        
        try:
            checks = []
            
            # Perform all security checks
            checks.extend(await self._validate_whitelist_specificity())
            checks.extend(await self._validate_rule_priorities())
            checks.extend(await self._validate_bot_protection_maintenance())
            checks.extend(await self._validate_rate_limiting_integrity())
            checks.extend(await self._validate_traffic_patterns())
            checks.extend(await self._validate_security_monitoring())
            
            # Calculate overall results
            report = self._generate_validation_report(checks)
            
            self._log_action("validate_observatory_integration", "completed", {
                "overall_status": report.overall_status.value,
                "security_score": report.security_score,
                "checks_performed": report.checks_performed
            })
            
            return report
            
        except Exception as e:
            self._log_action("validate_observatory_integration", "error", {
                "error": str(e)
            })
            raise
    
    async def _validate_whitelist_specificity(self) -> List[SecurityCheck]:
        """Validate that whitelist rules are specific to Observatory"""
        checks = []
        
        try:
            firewall_rules, _ = await self.rule_manager.get_existing_observatory_rules()
            
            # Check rule specificity
            overly_broad_rules = []
            for rule in firewall_rules:
                expression = rule.get("expression", "")
                if self._is_expression_too_broad(expression):
                    overly_broad_rules.append(rule)
            
            if overly_broad_rules:
                checks.append(SecurityCheck(
                    check_name="whitelist_specificity",
                    description="Check Observatory whitelist rule specificity",
                    result=ValidationResult.FAIL,
                    level=SecurityLevel.HIGH,
                    details={
                        "overly_broad_rules": len(overly_broad_rules),
                        "rule_ids": [rule.get("id") for rule in overly_broad_rules]
                    },
                    recommendations=[
                        "Review and tighten overly broad whitelist expressions",
                        "Ensure rules only match legitimate Observatory traffic",
                        "Add additional specificity constraints where needed"
                    ]
                ))
            else:
                checks.append(SecurityCheck(
                    check_name="whitelist_specificity",
                    description="Check Observatory whitelist rule specificity",
                    result=ValidationResult.PASS,
                    level=SecurityLevel.HIGH,
                    details={"overly_broad_rules": 0},
                    recommendations=["Whitelist rules are appropriately specific"]
                ))
            
        except Exception as e:
            checks.append(SecurityCheck(
                check_name="whitelist_specificity",
                description="Check Observatory whitelist rule specificity",
                result=ValidationResult.FAIL,
                level=SecurityLevel.CRITICAL,
                details={"error": str(e)},
                recommendations=["Fix API connectivity issues to perform validation"]
            ))
        
        return checks
    
    def _is_expression_too_broad(self, expression: str) -> bool:
        """Check if a Cloudflare expression is too broad"""
        # Patterns that indicate overly broad rules
        broad_patterns = [
            r"http\.host\.name\s*eq\s*\"\*\"",  # Any hostname
            r"http\.request\.uri\.path\s*matches\s*\".*\"",  # Any path
            r"ip\.src\.ip\s*eq\s*0\.0\.0\.0/0",  # Any IP
            r"http\.user_agent\s*contains\s*\"\"",  # Empty user agent
        ]
        
        import re
        return any(re.search(pattern, expression, re.IGNORECASE) for pattern in broad_patterns)
    
    async def _validate_rule_priorities(self) -> List[SecurityCheck]:
        """Validate that Observatory rules have appropriate priorities"""
        checks = []
        
        try:
            firewall_rules, _ = await self.rule_manager.get_existing_observatory_rules()
            
            # Check for priority conflicts
            observatory_priorities = [rule.get("priority", 0) for rule in firewall_rules]
            duplicate_priorities = len(observatory_priorities) != len(set(observatory_priorities))
            
            # Check if Observatory rules have too high priority
            high_priority_rules = [rule for rule in firewall_rules if rule.get("priority", 0) < 10]
            
            if duplicate_priorities:
                checks.append(SecurityCheck(
                    check_name="rule_priorities",
                    description="Check Observatory rule priority conflicts",
                    result=ValidationResult.FAIL,
                    level=SecurityLevel.MEDIUM,
                    details={"duplicate_priorities": True},
                    recommendations=["Resolve priority conflicts between Observatory rules"]
                ))
            elif high_priority_rules:
                checks.append(SecurityCheck(
                    check_name="rule_priorities",
                    description="Check Observatory rule priority conflicts",
                    result=ValidationResult.WARNING,
                    level=SecurityLevel.MEDIUM,
                    details={"high_priority_rules": len(high_priority_rules)},
                    recommendations=["Consider lowering priority of Observatory rules"]
                ))
            else:
                checks.append(SecurityCheck(
                    check_name="rule_priorities",
                    description="Check Observatory rule priority conflicts",
                    result=ValidationResult.PASS,
                    level=SecurityLevel.MEDIUM,
                    details={"duplicate_priorities": False},
                    recommendations=["Rule priorities are appropriately configured"]
                ))
            
        except Exception as e:
            checks.append(SecurityCheck(
                check_name="rule_priorities",
                description="Check Observatory rule priority conflicts",
                result=ValidationResult.FAIL,
                level=SecurityLevel.MEDIUM,
                details={"error": str(e)},
                recommendations=["Fix API connectivity issues"]
            ))
        
        return checks
    
    async def _validate_bot_protection_maintenance(self) -> List[SecurityCheck]:
        """Validate that bot protection remains active"""
        checks = []
        
        try:
            bot_config = await self.api_client.get_bot_management_config()
            
            # Check if bot protection is enabled
            bot_protection_enabled = bot_config.get("enable_js", False) or bot_config.get("enable_cookie", False)
            
            if not bot_protection_enabled:
                checks.append(SecurityCheck(
                    check_name="bot_protection_maintenance",
                    description="Verify bot protection remains active",
                    result=ValidationResult.FAIL,
                    level=SecurityLevel.CRITICAL,
                    details={"bot_protection_enabled": False},
                    recommendations=[
                        "Enable bot protection features",
                        "Ensure Observatory whitelist doesn't disable bot protection"
                    ]
                ))
            else:
                checks.append(SecurityCheck(
                    check_name="bot_protection_maintenance",
                    description="Verify bot protection remains active",
                    result=ValidationResult.PASS,
                    level=SecurityLevel.CRITICAL,
                    details={"bot_protection_enabled": True},
                    recommendations=["Bot protection is properly maintained"]
                ))
            
        except Exception as e:
            checks.append(SecurityCheck(
                check_name="bot_protection_maintenance",
                description="Verify bot protection remains active",
                result=ValidationResult.FAIL,
                level=SecurityLevel.CRITICAL,
                details={"error": str(e)},
                recommendations=["Fix API connectivity to verify bot protection"]
            ))
        
        return checks
    
    async def _validate_rate_limiting_integrity(self) -> List[SecurityCheck]:
        """Validate that rate limiting exceptions are appropriate"""
        checks = []
        
        try:
            _, rate_limit_rules = await self.rule_manager.get_existing_observatory_rules()
            
            # Check for overly permissive rate limits
            overly_permissive = []
            for rule in rate_limit_rules:
                rate = rule.get("rate", 0)
                if rate > 10000:  # Threshold for overly permissive
                    overly_permissive.append(rule)
            
            if overly_permissive:
                checks.append(SecurityCheck(
                    check_name="rate_limiting_integrity",
                    description="Check Observatory rate limiting exceptions",
                    result=ValidationResult.WARNING,
                    level=SecurityLevel.MEDIUM,
                    details={"overly_permissive_rules": len(overly_permissive)},
                    recommendations=[
                        "Review rate limits for Observatory exceptions",
                        "Ensure rate limits are appropriate for legitimate traffic"
                    ]
                ))
            else:
                checks.append(SecurityCheck(
                    check_name="rate_limiting_integrity",
                    description="Check Observatory rate limiting exceptions",
                    result=ValidationResult.PASS,
                    level=SecurityLevel.MEDIUM,
                    details={"overly_permissive_rules": 0},
                    recommendations=["Rate limiting exceptions are appropriately configured"]
                ))
            
        except Exception as e:
            checks.append(SecurityCheck(
                check_name="rate_limiting_integrity",
                description="Check Observatory rate limiting exceptions",
                result=ValidationResult.FAIL,
                level=SecurityLevel.MEDIUM,
                details={"error": str(e)},
                recommendations=["Fix API connectivity issues"]
            ))
        
        return checks
    
    async def _validate_traffic_patterns(self) -> List[SecurityCheck]:
        """Validate Observatory traffic patterns for security"""
        checks = []
        
        try:
            traffic_summary = await self.traffic_analyzer.get_observatory_traffic_summary()
            
            # Check for suspicious activity
            suspicious_count = traffic_summary.get("suspicious_activity_count", 0)
            
            if suspicious_count > 0:
                checks.append(SecurityCheck(
                    check_name="traffic_patterns",
                    description="Check Observatory traffic for suspicious activity",
                    result=ValidationResult.WARNING,
                    level=SecurityLevel.MEDIUM,
                    details={"suspicious_activity_count": suspicious_count},
                    recommendations=[
                        "Investigate suspicious Observatory traffic patterns",
                        "Review whitelist rules for potential abuse"
                    ]
                ))
            else:
                checks.append(SecurityCheck(
                    check_name="traffic_patterns",
                    description="Check Observatory traffic for suspicious activity",
                    result=ValidationResult.PASS,
                    level=SecurityLevel.MEDIUM,
                    details={"suspicious_activity_count": 0},
                    recommendations=["No suspicious Observatory traffic detected"]
                ))
            
            # Check Observatory traffic ratio
            total_requests = traffic_summary.get("total_requests_24h", 0)
            observatory_requests = traffic_summary.get("observatory_requests_24h", 0)
            
            if total_requests > 0:
                observatory_ratio = observatory_requests / total_requests
                if observatory_ratio > 0.9:
                    checks.append(SecurityCheck(
                        check_name="traffic_ratio",
                        description="Check Observatory traffic ratio",
                        result=ValidationResult.WARNING,
                        level=SecurityLevel.LOW,
                        details={"observatory_ratio": observatory_ratio},
                        recommendations=["Monitor for potential abuse of Observatory whitelist"]
                    ))
                else:
                    checks.append(SecurityCheck(
                        check_name="traffic_ratio",
                        description="Check Observatory traffic ratio",
                        result=ValidationResult.PASS,
                        level=SecurityLevel.LOW,
                        details={"observatory_ratio": observatory_ratio},
                        recommendations=["Observatory traffic ratio is within normal range"]
                    ))
            
        except Exception as e:
            checks.append(SecurityCheck(
                check_name="traffic_patterns",
                description="Check Observatory traffic for suspicious activity",
                result=ValidationResult.FAIL,
                level=SecurityLevel.MEDIUM,
                details={"error": str(e)},
                recommendations=["Fix traffic analysis connectivity issues"]
            ))
        
        return checks
    
    async def _validate_security_monitoring(self) -> List[SecurityCheck]:
        """Validate that security monitoring is in place"""
        checks = []
        
        try:
            # Check if we can access security events
            events = await self.api_client.get_security_events(limit=10)
            
            if len(events) == 0:
                checks.append(SecurityCheck(
                    check_name="security_monitoring",
                    description="Verify security event monitoring",
                    result=ValidationResult.WARNING,
                    level=SecurityLevel.MEDIUM,
                    details={"events_available": False},
                    recommendations=["Ensure security event logging is enabled"]
                ))
            else:
                checks.append(SecurityCheck(
                    check_name="security_monitoring",
                    description="Verify security event monitoring",
                    result=ValidationResult.PASS,
                    level=SecurityLevel.MEDIUM,
                    details={"events_available": True, "sample_count": len(events)},
                    recommendations=["Security event monitoring is operational"]
                ))
            
        except Exception as e:
            checks.append(SecurityCheck(
                check_name="security_monitoring",
                description="Verify security event monitoring",
                result=ValidationResult.FAIL,
                level=SecurityLevel.MEDIUM,
                details={"error": str(e)},
                recommendations=["Fix security event monitoring connectivity"]
            ))
        
        return checks
    
    def _generate_validation_report(self, checks: List[SecurityCheck]) -> SecurityValidationReport:
        """Generate comprehensive validation report"""
        checks_performed = len(checks)
        checks_passed = sum(1 for check in checks if check.result == ValidationResult.PASS)
        checks_failed = sum(1 for check in checks if check.result == ValidationResult.FAIL)
        checks_warning = sum(1 for check in checks if check.result == ValidationResult.WARNING)
        
        # Calculate security score (0-100)
        if checks_performed == 0:
            security_score = 0.0
        else:
            security_score = (checks_passed / checks_performed) * 100
        
        # Determine overall status
        if checks_failed > 0:
            overall_status = ValidationResult.FAIL
        elif checks_warning > 0:
            overall_status = ValidationResult.WARNING
        else:
            overall_status = ValidationResult.PASS
        
        # Generate summary
        summary = self._generate_summary(checks, overall_status, security_score)
        
        return SecurityValidationReport(
            overall_status=overall_status,
            checks_performed=checks_performed,
            checks_passed=checks_passed,
            checks_failed=checks_failed,
            checks_warning=checks_warning,
            security_score=security_score,
            checks=checks,
            summary=summary,
            timestamp=datetime.utcnow()
        )
    
    def _generate_summary(self, checks: List[SecurityCheck], 
                         overall_status: ValidationResult, 
                         security_score: float) -> str:
        """Generate human-readable summary"""
        critical_issues = [c for c in checks if c.level == SecurityLevel.CRITICAL and c.result == ValidationResult.FAIL]
        high_issues = [c for c in checks if c.level == SecurityLevel.HIGH and c.result == ValidationResult.FAIL]
        
        if critical_issues:
            return f"CRITICAL: {len(critical_issues)} critical security issues found. Immediate action required."
        elif high_issues:
            return f"HIGH: {len(high_issues)} high-priority security issues found. Review recommended."
        elif overall_status == ValidationResult.WARNING:
            return f"WARNING: Security validation passed with warnings. Monitor recommended."
        else:
            return f"PASS: Observatory integration security validation successful (Score: {security_score:.1f}%)"
    
    async def get_security_status(self) -> Dict[str, Any]:
        """
        Get current security status summary
        
        Returns:
            Dictionary with current security status
        """
        self._log_action("get_security_status", "in_progress", {})
        
        try:
            report = await self.validate_observatory_integration()
            
            status = {
                "overall_status": report.overall_status.value,
                "security_score": report.security_score,
                "checks_performed": report.checks_performed,
                "checks_passed": report.checks_passed,
                "checks_failed": report.checks_failed,
                "checks_warning": report.checks_warning,
                "summary": report.summary,
                "timestamp": report.timestamp.isoformat() + "Z"
            }
            
            self._log_action("get_security_status", "completed", {
                "overall_status": report.overall_status.value,
                "security_score": report.security_score
            })
            
            return status
            
        except Exception as e:
            self._log_action("get_security_status", "error", {
                "error": str(e)
            })
            raise