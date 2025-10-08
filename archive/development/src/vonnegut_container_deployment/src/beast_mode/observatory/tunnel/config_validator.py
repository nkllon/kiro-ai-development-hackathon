"""
Cloudflare Tunnel Configuration Validator

Validates tunnel configurations for correctness, security, and WebSocket support.
Implements comprehensive validation with detailed error reporting.
"""

import json
import logging
import re
from datetime import datetime
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)


class ValidationLevel(Enum):
    """Validation severity levels"""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


@dataclass
class ValidationIssue:
    """Individual validation issue"""
    level: ValidationLevel
    field: str
    message: str
    suggestion: Optional[str] = None


@dataclass
class ValidationResult:
    """Complete validation result"""
    is_valid: bool
    issues: List[ValidationIssue]
    warnings: List[ValidationIssue]
    errors: List[ValidationIssue]
    critical_errors: List[ValidationIssue]
    summary: str


class ConfigValidator:
    """Validates Cloudflare tunnel configurations"""
    
    def __init__(self):
        # Log initialization
        self._log_action("init", "in_progress", {
            "validation_levels": [level.value for level in ValidationLevel],
            "websocket_validation": True
        })
        
        logger.info("ConfigValidator initialized")
        self._log_action("init", "completed", {"status": "ready"})
    
    def _log_action(self, action: str, status: str, details: Dict[str, Any] = None):
        """Log actions in JSON format as required"""
        log_entry = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "task": "7.1",
            "action": action,
            "status": status
        }
        if details:
            log_entry["details"] = details
        
        print(json.dumps(log_entry))
    
    def validate_config(self, config: Dict[str, Any]) -> ValidationResult:
        """
        Validate complete tunnel configuration
        
        Args:
            config: Configuration dictionary to validate
            
        Returns:
            ValidationResult with detailed validation information
        """
        self._log_action("validate_config", "in_progress", {
            "config_keys": list(config.keys()),
            "validation_type": "complete"
        })
        
        try:
            issues = []
            
            # Validate top-level structure
            issues.extend(self._validate_top_level(config))
            
            # Validate tunnel configuration
            issues.extend(self._validate_tunnel_config(config))
            
            # Validate ingress rules
            issues.extend(self._validate_ingress_rules(config.get("ingress", [])))
            
            # Validate WebSocket support
            issues.extend(self._validate_websocket_support(config))
            
            # Categorize issues
            warnings = [i for i in issues if i.level == ValidationLevel.WARNING]
            errors = [i for i in issues if i.level == ValidationLevel.ERROR]
            critical_errors = [i for i in issues if i.level == ValidationLevel.CRITICAL]
            
            # Determine overall validity
            is_valid = len(critical_errors) == 0 and len(errors) == 0
            
            # Generate summary
            summary = self._generate_validation_summary(issues)
            
            result = ValidationResult(
                is_valid=is_valid,
                issues=issues,
                warnings=warnings,
                errors=errors,
                critical_errors=critical_errors,
                summary=summary
            )
            
            self._log_action("validate_config", "completed", {
                "is_valid": is_valid,
                "total_issues": len(issues),
                "warnings": len(warnings),
                "errors": len(errors),
                "critical_errors": len(critical_errors)
            })
            
            return result
            
        except Exception as e:
            self._log_action("validate_config", "error", {
                "error": str(e),
                "error_type": type(e).__name__
            })
            raise
    
    def _validate_top_level(self, config: Dict[str, Any]) -> List[ValidationIssue]:
        """Validate top-level configuration structure"""
        issues = []
        
        # Required fields
        required_fields = ["tunnel", "credentials-file", "ingress"]
        for field in required_fields:
            if field not in config:
                issues.append(ValidationIssue(
                    level=ValidationLevel.CRITICAL,
                    field=field,
                    message=f"Required field '{field}' is missing",
                    suggestion=f"Add '{field}' to the configuration"
                ))
        
        # Check for unknown fields
        known_fields = {"tunnel", "credentials-file", "ingress", "originRequest"}
        for field in config.keys():
            if field not in known_fields:
                issues.append(ValidationIssue(
                    level=ValidationLevel.WARNING,
                    field=field,
                    message=f"Unknown field '{field}' found",
                    suggestion="Remove or verify this field is supported"
                ))
        
        return issues
    
    def _validate_tunnel_config(self, config: Dict[str, Any]) -> List[ValidationIssue]:
        """Validate tunnel-specific configuration"""
        issues = []
        
        # Validate tunnel name
        tunnel_name = config.get("tunnel")
        if tunnel_name:
            if not isinstance(tunnel_name, str):
                issues.append(ValidationIssue(
                    level=ValidationLevel.ERROR,
                    field="tunnel",
                    message="Tunnel name must be a string",
                    suggestion="Provide a valid string for tunnel name"
                ))
            elif not re.match(r'^[a-zA-Z0-9_-]+$', tunnel_name):
                issues.append(ValidationIssue(
                    level=ValidationLevel.ERROR,
                    field="tunnel",
                    message="Tunnel name contains invalid characters",
                    suggestion="Use only alphanumeric characters, hyphens, and underscores"
                ))
        
        # Validate credentials file path
        credentials_file = config.get("credentials-file")
        if credentials_file:
            if not isinstance(credentials_file, str):
                issues.append(ValidationIssue(
                    level=ValidationLevel.ERROR,
                    field="credentials-file",
                    message="Credentials file path must be a string",
                    suggestion="Provide a valid file path"
                ))
            elif not credentials_file.endswith('.json'):
                issues.append(ValidationIssue(
                    level=ValidationLevel.WARNING,
                    field="credentials-file",
                    message="Credentials file should have .json extension",
                    suggestion="Use .json extension for credentials file"
                ))
        
        return issues
    
    def _validate_ingress_rules(self, ingress_rules: List[Dict[str, Any]]) -> List[ValidationIssue]:
        """Validate ingress rules"""
        issues = []
        
        if not isinstance(ingress_rules, list):
            issues.append(ValidationIssue(
                level=ValidationLevel.CRITICAL,
                field="ingress",
                message="Ingress rules must be a list",
                suggestion="Provide ingress rules as a list"
            ))
            return issues
        
        if len(ingress_rules) == 0:
            issues.append(ValidationIssue(
                level=ValidationLevel.CRITICAL,
                field="ingress",
                message="At least one ingress rule is required",
                suggestion="Add ingress rules to the configuration"
            ))
            return issues
        
        # Check for catch-all rule
        has_catch_all = any(
            rule.get("service") == "http_status:404" 
            for rule in ingress_rules
        )
        
        if not has_catch_all:
            issues.append(ValidationIssue(
                level=ValidationLevel.WARNING,
                field="ingress",
                message="No catch-all rule found",
                suggestion="Add a catch-all rule: {'service': 'http_status:404'}"
            ))
        
        # Validate individual rules
        for i, rule in enumerate(ingress_rules):
            rule_issues = self._validate_single_ingress_rule(rule, i)
            issues.extend(rule_issues)
        
        return issues
    
    def _validate_single_ingress_rule(self, rule: Dict[str, Any], index: int) -> List[ValidationIssue]:
        """Validate a single ingress rule"""
        issues = []
        rule_prefix = f"ingress[{index}]"
        
        # Check for service field
        if "service" not in rule:
            issues.append(ValidationIssue(
                level=ValidationLevel.CRITICAL,
                field=f"{rule_prefix}.service",
                message="Service field is required for ingress rule",
                suggestion="Add 'service' field to the ingress rule"
            ))
        else:
            service = rule["service"]
            if not isinstance(service, str):
                issues.append(ValidationIssue(
                    level=ValidationLevel.ERROR,
                    field=f"{rule_prefix}.service",
                    message="Service must be a string",
                    suggestion="Provide a valid service URL or status code"
                ))
            elif not self._is_valid_service(service):
                issues.append(ValidationIssue(
                    level=ValidationLevel.WARNING,
                    field=f"{rule_prefix}.service",
                    message=f"Service '{service}' may not be valid",
                    suggestion="Verify the service URL or status code is correct"
                ))
        
        # Validate hostname if present
        if "hostname" in rule:
            hostname = rule["hostname"]
            if not isinstance(hostname, str):
                issues.append(ValidationIssue(
                    level=ValidationLevel.ERROR,
                    field=f"{rule_prefix}.hostname",
                    message="Hostname must be a string",
                    suggestion="Provide a valid hostname"
                ))
            elif not self._is_valid_hostname(hostname):
                issues.append(ValidationIssue(
                    level=ValidationLevel.WARNING,
                    field=f"{rule_prefix}.hostname",
                    message=f"Hostname '{hostname}' format may be invalid",
                    suggestion="Use a valid domain name format"
                ))
        
        # Validate originRequest if present
        if "originRequest" in rule:
            origin_issues = self._validate_origin_request(rule["originRequest"], f"{rule_prefix}.originRequest")
            issues.extend(origin_issues)
        
        return issues
    
    def _validate_origin_request(self, origin_request: Dict[str, Any], field_prefix: str) -> List[ValidationIssue]:
        """Validate originRequest configuration"""
        issues = []
        
        if not isinstance(origin_request, dict):
            issues.append(ValidationIssue(
                level=ValidationLevel.ERROR,
                field=field_prefix,
                message="originRequest must be a dictionary",
                suggestion="Provide originRequest as a dictionary"
            ))
            return issues
        
        # Validate timeout values
        timeout_fields = ["connectTimeout", "tlsTimeout", "tcpKeepAlive", "keepAliveTimeout"]
        for field in timeout_fields:
            if field in origin_request:
                timeout_value = origin_request[field]
                if not self._is_valid_timeout(timeout_value):
                    issues.append(ValidationIssue(
                        level=ValidationLevel.WARNING,
                        field=f"{field_prefix}.{field}",
                        message=f"Timeout value '{timeout_value}' format may be invalid",
                        suggestion="Use format like '30s', '1m', or '1000ms'"
                    ))
        
        # Validate numeric values
        numeric_fields = ["keepAliveConnections"]
        for field in numeric_fields:
            if field in origin_request:
                value = origin_request[field]
                if not isinstance(value, int) or value < 0:
                    issues.append(ValidationIssue(
                        level=ValidationLevel.ERROR,
                        field=f"{field_prefix}.{field}",
                        message=f"{field} must be a non-negative integer",
                        suggestion=f"Provide a valid integer for {field}"
                    ))
        
        # Validate proxyType for WebSocket support
        proxy_type = origin_request.get("proxyType")
        if proxy_type is not None and proxy_type != "":
            issues.append(ValidationIssue(
                level=ValidationLevel.WARNING,
                field=f"{field_prefix}.proxyType",
                message="proxyType should be empty string for WebSocket support",
                suggestion="Set proxyType to empty string: ''"
            ))
        
        return issues
    
    def _validate_websocket_support(self, config: Dict[str, Any]) -> List[ValidationIssue]:
        """Validate WebSocket support configuration"""
        issues = []
        
        ingress_rules = config.get("ingress", [])
        websocket_rules = 0
        
        for i, rule in enumerate(ingress_rules):
            if rule.get("service") == "http_status:404":
                continue  # Skip catch-all rules
            
            origin_request = rule.get("originRequest", {})
            proxy_type = origin_request.get("proxyType", "")
            
            if proxy_type == "":
                websocket_rules += 1
                
                # Check for WebSocket-specific settings
                if not origin_request.get("httpHostHeader"):
                    issues.append(ValidationIssue(
                        level=ValidationLevel.WARNING,
                        field=f"ingress[{i}].originRequest.httpHostHeader",
                        message="httpHostHeader recommended for WebSocket connections",
                        suggestion="Add httpHostHeader to originRequest"
                    ))
        
        if websocket_rules == 0:
            issues.append(ValidationIssue(
                level=ValidationLevel.INFO,
                field="ingress",
                message="No WebSocket-enabled rules found",
                suggestion="Consider enabling WebSocket support for real-time applications"
            ))
        
        return issues
    
    def _is_valid_service(self, service: str) -> bool:
        """Check if service value is valid"""
        # HTTP status codes
        if service.startswith("http_status:"):
            try:
                status_code = int(service.split(":")[1])
                return 100 <= status_code <= 599
            except (ValueError, IndexError):
                return False
        
        # HTTP URLs
        if service.startswith("http://") or service.startswith("https://"):
            return True
        
        # Local services
        if service.startswith("localhost:") or service.startswith("127.0.0.1:"):
            return True
        
        return False
    
    def _is_valid_hostname(self, hostname: str) -> bool:
        """Check if hostname format is valid"""
        # Basic hostname validation regex
        pattern = r'^[a-zA-Z0-9]([a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?(\.[a-zA-Z0-9]([a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?)*$'
        return bool(re.match(pattern, hostname))
    
    def _is_valid_timeout(self, timeout: str) -> bool:
        """Check if timeout format is valid"""
        if isinstance(timeout, (int, float)):
            return timeout >= 0
        
        if not isinstance(timeout, str):
            return False
        
        # Check for valid timeout formats: 30s, 1m, 1000ms
        pattern = r'^\d+(\.\d+)?(s|m|ms)$'
        return bool(re.match(pattern, timeout))
    
    def _generate_validation_summary(self, issues: List[ValidationIssue]) -> str:
        """Generate validation summary"""
        critical_count = len([i for i in issues if i.level == ValidationLevel.CRITICAL])
        error_count = len([i for i in issues if i.level == ValidationLevel.ERROR])
        warning_count = len([i for i in issues if i.level == ValidationLevel.WARNING])
        info_count = len([i for i in issues if i.level == ValidationLevel.INFO])
        
        if critical_count > 0:
            return f"Configuration has {critical_count} critical issues that must be fixed"
        elif error_count > 0:
            return f"Configuration has {error_count} errors that should be fixed"
        elif warning_count > 0:
            return f"Configuration has {warning_count} warnings to review"
        elif info_count > 0:
            return f"Configuration is valid with {info_count} informational notes"
        else:
            return "Configuration is valid with no issues"
    
    def validate_websocket_config(self, config: Dict[str, Any]) -> bool:
        """
        Quick WebSocket configuration validation
        
        Args:
            config: Configuration to validate
            
        Returns:
            True if WebSocket configuration is valid
        """
        self._log_action("validate_websocket_config", "in_progress", {})
        
        try:
            ingress_rules = config.get("ingress", [])
            
            for rule in ingress_rules:
                if rule.get("service") == "http_status:404":
                    continue
                
                origin_request = rule.get("originRequest", {})
                proxy_type = origin_request.get("proxyType", "")
                
                if proxy_type == "":
                    self._log_action("validate_websocket_config", "completed", {
                        "websocket_support": True,
                        "valid": True
                    })
                    return True
            
            self._log_action("validate_websocket_config", "completed", {
                "websocket_support": False,
                "valid": False
            })
            return False
            
        except Exception as e:
            self._log_action("validate_websocket_config", "error", {
                "error": str(e),
                "error_type": type(e).__name__
            })
            return False