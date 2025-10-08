"""
Tunnel Configuration Validator

Validates cloudflared configuration syntax and WebSocket settings for
optimal performance and security compliance.
"""

import json
import re
import yaml
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple
from urllib.parse import urlparse


class ValidationError(Exception):
    """Raised when configuration validation fails."""
    pass


class TunnelValidator:
    """Validates cloudflared tunnel configurations with WebSocket support."""

    # Required fields for tunnel configuration
    REQUIRED_FIELDS = ["tunnel", "ingress"]

    # Valid service types
    VALID_SERVICE_TYPES = [
        "http://", "https://", "ssh://", "rdp://", "tcp://",
        "unix:", "http_status:", "hello_world"
    ]

    # WebSocket-specific validation rules
    WEBSOCKET_PROXY_TYPE = ""  # Empty string enables WebSocket
    MAX_CONNECT_TIMEOUT = 300  # seconds
    MAX_TLS_TIMEOUT = 60      # seconds

    def __init__(self):
        """Initialize the validator."""
        self.log_action("init", "completed")

    def log_action(self, action: str, status: str, details: Dict[str, Any] = None):
        """Log action in JSON format as required."""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "task": "1",
            "action": action,
            "status": status,
            "details": details or {}
        }
        print(json.dumps(log_entry))

    def validate_config(self, config: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """Validate complete tunnel configuration.

        Args:
            config: Configuration dictionary to validate

        Returns:
            Tuple of (is_valid, error_messages)
        """
        self.log_action("validate_config", "in_progress", {
            "config_keys": list(config.keys()) if config else []
        })

        errors = []

        try:
            # Basic structure validation
            basic_errors = self._validate_basic_structure(config)
            errors.extend(basic_errors)

            # Ingress validation
            if "ingress" in config:
                ingress_errors = self._validate_ingress(config["ingress"])
                errors.extend(ingress_errors)

            # WebSocket-specific validation
            websocket_errors = self._validate_websocket_settings(config)
            errors.extend(websocket_errors)

            # Security validation
            security_errors = self._validate_security_settings(config)
            errors.extend(security_errors)

            is_valid = len(errors) == 0

            self.log_action("validate_config", "completed", {
                "is_valid": is_valid,
                "error_count": len(errors),
                "validation_categories": ["basic", "ingress", "websocket", "security"]
            })

            return is_valid, errors

        except Exception as e:
            error_msg = f"Validation failed with exception: {str(e)}"
            errors.append(error_msg)

            self.log_action("validate_config", "error", {
                "error": str(e),
                "error_type": type(e).__name__
            })

            return False, errors

    def _validate_basic_structure(self, config: Dict[str, Any]) -> List[str]:
        """Validate basic configuration structure."""
        errors = []

        if not isinstance(config, dict):
            errors.append("Configuration must be a dictionary")
            return errors

        # Check required fields
        for field in self.REQUIRED_FIELDS:
            if field not in config:
                errors.append(f"Required field '{field}' is missing")

        # Validate tunnel name
        if "tunnel" in config:
            if not isinstance(config["tunnel"], str):
                errors.append("Tunnel name must be a string")
            elif not re.match(r'^[a-zA-Z0-9-]+$', config["tunnel"]):
                errors.append("Tunnel name must contain only alphanumeric characters and hyphens")

        # Validate credentials file if present
        if "credentials-file" in config:
            if not isinstance(config["credentials-file"], str):
                errors.append("Credentials file path must be a string")

        return errors

    def _validate_ingress(self, ingress: List[Dict[str, Any]]) -> List[str]:
        """Validate ingress rules."""
        errors = []

        if not isinstance(ingress, list):
            errors.append("Ingress must be a list")
            return errors

        if len(ingress) < 1:
            errors.append("At least one ingress rule is required")
            return errors

        # Last rule must be a catch-all
        last_rule = ingress[-1]
        if "hostname" in last_rule:
            errors.append("Last ingress rule must be a catch-all (no hostname)")

        if "service" not in last_rule:
            errors.append("Last ingress rule must have a service")

        # Validate each ingress rule
        hostnames = set()
        for i, rule in enumerate(ingress):
            rule_errors = self._validate_ingress_rule(rule, i)
            errors.extend(rule_errors)

            # Check for duplicate hostnames
            hostname = rule.get("hostname")
            if hostname:
                if hostname in hostnames:
                    errors.append(f"Duplicate hostname '{hostname}' in ingress rules")
                hostnames.add(hostname)

        return errors

    def _validate_ingress_rule(self, rule: Dict[str, Any], index: int) -> List[str]:
        """Validate individual ingress rule."""
        errors = []

        if not isinstance(rule, dict):
            errors.append(f"Ingress rule {index} must be a dictionary")
            return errors

        # Validate service
        if "service" not in rule:
            errors.append(f"Ingress rule {index} missing required 'service' field")
        else:
            service_errors = self._validate_service(rule["service"], index)
            errors.extend(service_errors)

        # Validate hostname if present
        if "hostname" in rule:
            hostname_errors = self._validate_hostname(rule["hostname"], index)
            errors.extend(hostname_errors)

        # Validate originRequest if present
        if "originRequest" in rule:
            origin_errors = self._validate_origin_request(rule["originRequest"], index)
            errors.extend(origin_errors)

        return errors

    def _validate_service(self, service: str, rule_index: int) -> List[str]:
        """Validate service URL or type."""
        errors = []

        if not isinstance(service, str):
            errors.append(f"Service in rule {rule_index} must be a string")
            return errors

        # Check if it's a valid service type
        is_valid_type = any(service.startswith(stype) for stype in self.VALID_SERVICE_TYPES)

        if not is_valid_type:
            errors.append(f"Invalid service type in rule {rule_index}: {service}")
            return errors

        # Validate HTTP/HTTPS URLs
        if service.startswith(("http://", "https://")):
            try:
                parsed = urlparse(service)
                if not parsed.netloc:
                    errors.append(f"Invalid URL in rule {rule_index}: missing netloc")
                if not parsed.port and service.startswith("http://localhost"):
                    errors.append(f"Local HTTP service in rule {rule_index} should specify port")
            except Exception as e:
                errors.append(f"Invalid URL in rule {rule_index}: {str(e)}")

        return errors

    def _validate_hostname(self, hostname: str, rule_index: int) -> List[str]:
        """Validate hostname format."""
        errors = []

        if not isinstance(hostname, str):
            errors.append(f"Hostname in rule {rule_index} must be a string")
            return errors

        # Basic hostname validation
        if not re.match(r'^[a-zA-Z0-9.-]+$', hostname):
            errors.append(f"Invalid hostname format in rule {rule_index}: {hostname}")

        if hostname.startswith('.') or hostname.endswith('.'):
            errors.append(f"Hostname in rule {rule_index} cannot start or end with dot")

        if '..' in hostname:
            errors.append(f"Hostname in rule {rule_index} cannot contain consecutive dots")

        return errors

    def _validate_origin_request(self, origin_request: Dict[str, Any], rule_index: int) -> List[str]:
        """Validate originRequest settings."""
        errors = []

        if not isinstance(origin_request, dict):
            errors.append(f"originRequest in rule {rule_index} must be a dictionary")
            return errors

        # Validate timeout values
        timeout_fields = ["connectTimeout", "tlsTimeout", "keepAliveTimeout"]
        for field in timeout_fields:
            if field in origin_request:
                timeout_errors = self._validate_timeout(origin_request[field], field, rule_index)
                errors.extend(timeout_errors)

        # Validate numeric fields
        if "keepAliveConnections" in origin_request:
            keep_alive = origin_request["keepAliveConnections"]
            if not isinstance(keep_alive, int) or keep_alive < 0:
                errors.append(f"keepAliveConnections in rule {rule_index} must be a non-negative integer")

        # Validate httpHostHeader
        if "httpHostHeader" in origin_request:
            host_header = origin_request["httpHostHeader"]
            if not isinstance(host_header, str):
                errors.append(f"httpHostHeader in rule {rule_index} must be a string")

        return errors

    def _validate_timeout(self, timeout: str, field_name: str, rule_index: int) -> List[str]:
        """Validate timeout format and value."""
        errors = []

        if not isinstance(timeout, str):
            errors.append(f"{field_name} in rule {rule_index} must be a string")
            return errors

        # Parse timeout format (e.g., "30s", "5m", "1h")
        timeout_pattern = r'^\d+[smh]$'
        if not re.match(timeout_pattern, timeout):
            errors.append(f"Invalid {field_name} format in rule {rule_index}: {timeout} (use format like '30s', '5m', '1h')")
            return errors

        # Extract numeric value and unit
        value = int(timeout[:-1])
        unit = timeout[-1]

        # Convert to seconds for validation
        multipliers = {'s': 1, 'm': 60, 'h': 3600}
        seconds = value * multipliers[unit]

        # Validate reasonable timeout values
        if field_name == "connectTimeout" and seconds > self.MAX_CONNECT_TIMEOUT:
            errors.append(f"{field_name} in rule {rule_index} exceeds maximum ({self.MAX_CONNECT_TIMEOUT}s): {timeout}")
        elif field_name == "tlsTimeout" and seconds > self.MAX_TLS_TIMEOUT:
            errors.append(f"{field_name} in rule {rule_index} exceeds maximum ({self.MAX_TLS_TIMEOUT}s): {timeout}")

        return errors

    def _validate_websocket_settings(self, config: Dict[str, Any]) -> List[str]:
        """Validate WebSocket-specific settings."""
        errors = []

        websocket_rules = []

        # Find ingress rules with WebSocket settings
        for i, rule in enumerate(config.get("ingress", [])):
            origin_request = rule.get("originRequest", {})
            proxy_type = origin_request.get("proxyType")

            if proxy_type == self.WEBSOCKET_PROXY_TYPE:
                websocket_rules.append((i, rule))

        if not websocket_rules:
            self.log_action("websocket_validation", "completed", {
                "websocket_enabled": False,
                "message": "No WebSocket rules found"
            })
            return errors

        # Validate WebSocket rules
        for rule_index, rule in websocket_rules:
            origin_request = rule.get("originRequest", {})

            # Check for recommended WebSocket settings
            if "keepAliveConnections" not in origin_request:
                errors.append(f"WebSocket rule {rule_index} should specify keepAliveConnections for optimal performance")

            if "keepAliveTimeout" not in origin_request:
                errors.append(f"WebSocket rule {rule_index} should specify keepAliveTimeout for connection management")

            # Validate the service is HTTP/HTTPS for WebSocket upgrade
            service = rule.get("service", "")
            if not service.startswith(("http://", "https://")):
                errors.append(f"WebSocket rule {rule_index} service must be HTTP/HTTPS for WebSocket upgrade")

        self.log_action("websocket_validation", "completed", {
            "websocket_enabled": True,
            "websocket_rules_count": len(websocket_rules),
            "websocket_errors": len([e for e in errors if "WebSocket" in e])
        })

        return errors

    def _validate_security_settings(self, config: Dict[str, Any]) -> List[str]:
        """Validate security-related settings."""
        errors = []

        # Check for credentials file
        if "credentials-file" not in config:
            errors.append("Missing credentials-file for secure tunnel authentication")

        # Validate TLS settings in origin requests
        for i, rule in enumerate(config.get("ingress", [])):
            origin_request = rule.get("originRequest", {})

            # Check for reasonable TLS timeout
            tls_timeout = origin_request.get("tlsTimeout")
            if tls_timeout and self._parse_timeout_seconds(tls_timeout) < 5:
                errors.append(f"TLS timeout in rule {i} is too low for secure connections: {tls_timeout}")

            # Validate HTTPS usage for production
            service = rule.get("service", "")
            hostname = rule.get("hostname")
            if hostname and service.startswith("http://") and not service.startswith("http://localhost"):
                errors.append(f"Rule {i} uses HTTP for external service - consider HTTPS for security")

        self.log_action("security_validation", "completed", {
            "security_errors": len(errors),
            "has_credentials": "credentials-file" in config
        })

        return errors

    def _parse_timeout_seconds(self, timeout: str) -> int:
        """Parse timeout string to seconds."""
        if not isinstance(timeout, str):
            return 0

        try:
            value = int(timeout[:-1])
            unit = timeout[-1]
            multipliers = {'s': 1, 'm': 60, 'h': 3600}
            return value * multipliers.get(unit, 1)
        except (ValueError, IndexError):
            return 0

    def validate_yaml_syntax(self, yaml_content: str) -> Tuple[bool, Optional[str]]:
        """Validate YAML syntax.

        Args:
            yaml_content: YAML content as string

        Returns:
            Tuple of (is_valid, error_message)
        """
        self.log_action("validate_yaml_syntax", "in_progress")

        try:
            yaml.safe_load(yaml_content)
            self.log_action("validate_yaml_syntax", "completed", {"is_valid": True})
            return True, None

        except yaml.YAMLError as e:
            error_msg = f"YAML syntax error: {str(e)}"
            self.log_action("validate_yaml_syntax", "error", {"error": error_msg})
            return False, error_msg

    def get_validation_summary(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Get comprehensive validation summary.

        Args:
            config: Configuration to analyze

        Returns:
            Dictionary with validation summary
        """
        self.log_action("get_validation_summary", "in_progress")

        is_valid, errors = self.validate_config(config)

        # Count WebSocket rules
        websocket_count = 0
        for rule in config.get("ingress", []):
            origin_request = rule.get("originRequest", {})
            if origin_request.get("proxyType") == self.WEBSOCKET_PROXY_TYPE:
                websocket_count += 1

        summary = {
            "is_valid": is_valid,
            "error_count": len(errors),
            "errors": errors,
            "tunnel_name": config.get("tunnel"),
            "ingress_rules_count": len(config.get("ingress", [])),
            "websocket_rules_count": websocket_count,
            "has_credentials": "credentials-file" in config,
            "validation_timestamp": datetime.now().isoformat()
        }

        self.log_action("get_validation_summary", "completed", {
            "summary_keys": list(summary.keys()),
            "is_valid": is_valid
        })

        return summary