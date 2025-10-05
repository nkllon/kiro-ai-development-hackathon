"""
Cloudflared Version Compatibility Checker

Verifies cloudflared version compatibility for WebSocket support and ensures
the installed version supports all required features for observatory deployment.
"""

import json
import re
import subprocess
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple
from packaging import version


class VersionChecker:
    """Checks cloudflared version compatibility for WebSocket support."""

    # Minimum version requirements
    MIN_VERSION_WEBSOCKET = "2023.5.0"  # First stable WebSocket support
    MIN_VERSION_RECOMMENDED = "2025.9.1"  # Recommended minimum for latest features
    MIN_VERSION_TLS13 = "2023.8.0"  # TLS 1.3 support

    # Known version compatibility issues
    KNOWN_ISSUES = {
        "2023.3.0": ["WebSocket connection drops", "Limited keep-alive support"],
        "2023.4.0": ["Intermittent WebSocket timeouts"],
        "2024.1.0": ["Performance regression in WebSocket handling"]
    }

    # Feature support matrix
    FEATURE_MATRIX = {
        "websocket_proxy": "2023.5.0",
        "keep_alive_connections": "2023.6.0",
        "tls_1_3": "2023.8.0",
        "improved_websocket_performance": "2024.6.0",
        "websocket_compression": "2024.8.0",
        "enhanced_keep_alive": "2025.9.1"
    }

    def __init__(self):
        """Initialize version checker."""
        self.log_action("version_checker_init", "completed", {"initialized": True})

    def log_action(self, action: str, status: str, details: Dict[str, Any] = None):
        """Log action in JSON format as required."""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "task": "1",
            "action": f"VersionChecker.{action}",
            "status": status,
            "details": details or {}
        }
        print(json.dumps(log_entry))

    def get_installed_version(self) -> Tuple[bool, Optional[str], Optional[str]]:
        """
        Get the currently installed cloudflared version.

        Returns:
            Tuple of (found, version_string, error_message)
        """
        self.log_action("get_installed_version", "in_progress")

        try:
            # Try to get version from cloudflared command
            result = subprocess.run(
                ["cloudflared", "--version"],
                capture_output=True,
                text=True,
                timeout=10
            )

            if result.returncode == 0:
                # Parse version from output
                version_output = result.stdout.strip()
                version_match = re.search(r'cloudflared version (\d+\.\d+\.\d+)', version_output)

                if version_match:
                    version_str = version_match.group(1)
                    self.log_action("get_installed_version", "completed", {
                        "version": version_str,
                        "full_output": version_output
                    })
                    return True, version_str, None
                else:
                    error_msg = f"Could not parse version from output: {version_output}"
                    self.log_action("get_installed_version", "error", {"error": error_msg})
                    return False, None, error_msg

            else:
                error_msg = f"cloudflared command failed: {result.stderr}"
                self.log_action("get_installed_version", "error", {"error": error_msg})
                return False, None, error_msg

        except subprocess.TimeoutExpired:
            error_msg = "Timeout getting cloudflared version"
            self.log_action("get_installed_version", "error", {"error": error_msg})
            return False, None, error_msg

        except FileNotFoundError:
            error_msg = "cloudflared not found in PATH"
            self.log_action("get_installed_version", "error", {"error": error_msg})
            return False, None, error_msg

        except Exception as e:
            error_msg = f"Unexpected error getting cloudflared version: {str(e)}"
            self.log_action("get_installed_version", "error", {
                "error": error_msg,
                "error_type": type(e).__name__
            })
            return False, None, error_msg

    def check_websocket_compatibility(self, version_str: str) -> Tuple[bool, List[str], List[str]]:
        """
        Check WebSocket compatibility for a given version.

        Args:
            version_str: Version string to check (e.g., "2025.9.1")

        Returns:
            Tuple of (is_compatible, warnings, errors)
        """
        self.log_action("check_websocket_compatibility", "in_progress", {
            "version": version_str
        })

        warnings = []
        errors = []

        try:
            current_version = version.parse(version_str)
            min_websocket = version.parse(self.MIN_VERSION_WEBSOCKET)
            recommended = version.parse(self.MIN_VERSION_RECOMMENDED)

            # Check minimum WebSocket support
            if current_version < min_websocket:
                errors.append(f"Version {version_str} does not support WebSocket proxy (minimum: {self.MIN_VERSION_WEBSOCKET})")
                is_compatible = False
            else:
                is_compatible = True

                # Check if version is below recommended
                if current_version < recommended:
                    warnings.append(f"Version {version_str} is below recommended minimum ({self.MIN_VERSION_RECOMMENDED}) for optimal WebSocket performance")

                # Check for known issues
                if version_str in self.KNOWN_ISSUES:
                    issues = self.KNOWN_ISSUES[version_str]
                    warnings.extend([f"Known issue in {version_str}: {issue}" for issue in issues])

                # Check feature support
                missing_features = []
                for feature, required_version in self.FEATURE_MATRIX.items():
                    if current_version < version.parse(required_version):
                        missing_features.append(f"{feature} (requires {required_version})")

                if missing_features:
                    warnings.append(f"Missing features: {', '.join(missing_features)}")

            self.log_action("check_websocket_compatibility", "completed", {
                "version": version_str,
                "is_compatible": is_compatible,
                "warning_count": len(warnings),
                "error_count": len(errors)
            })

            return is_compatible, warnings, errors

        except Exception as e:
            error_msg = f"Error checking version compatibility: {str(e)}"
            errors.append(error_msg)
            self.log_action("check_websocket_compatibility", "error", {
                "error": error_msg,
                "error_type": type(e).__name__
            })
            return False, warnings, errors

    def check_feature_support(self, version_str: str, feature: str) -> Tuple[bool, Optional[str]]:
        """
        Check if a specific feature is supported in the given version.

        Args:
            version_str: Version string to check
            feature: Feature name to check

        Returns:
            Tuple of (is_supported, required_version_or_error)
        """
        self.log_action("check_feature_support", "in_progress", {
            "version": version_str,
            "feature": feature
        })

        try:
            if feature not in self.FEATURE_MATRIX:
                error_msg = f"Unknown feature: {feature}"
                self.log_action("check_feature_support", "error", {"error": error_msg})
                return False, error_msg

            current_version = version.parse(version_str)
            required_version = version.parse(self.FEATURE_MATRIX[feature])

            is_supported = current_version >= required_version
            required_version_str = self.FEATURE_MATRIX[feature]

            self.log_action("check_feature_support", "completed", {
                "version": version_str,
                "feature": feature,
                "is_supported": is_supported,
                "required_version": required_version_str
            })

            return is_supported, required_version_str if not is_supported else None

        except Exception as e:
            error_msg = f"Error checking feature support: {str(e)}"
            self.log_action("check_feature_support", "error", {
                "error": error_msg,
                "error_type": type(e).__name__
            })
            return False, error_msg

    def get_upgrade_recommendations(self, current_version: str) -> Dict[str, Any]:
        """
        Get upgrade recommendations for the current version.

        Args:
            current_version: Current version string

        Returns:
            Dictionary with upgrade recommendations
        """
        self.log_action("get_upgrade_recommendations", "in_progress", {
            "current_version": current_version
        })

        try:
            current = version.parse(current_version)
            recommended = version.parse(self.MIN_VERSION_RECOMMENDED)

            recommendations = {
                "current_version": current_version,
                "recommended_version": self.MIN_VERSION_RECOMMENDED,
                "should_upgrade": current < recommended,
                "upgrade_priority": "low",
                "benefits": [],
                "risks": [],
                "missing_features": []
            }

            # Determine upgrade priority
            min_websocket = version.parse(self.MIN_VERSION_WEBSOCKET)
            if current < min_websocket:
                recommendations["upgrade_priority"] = "critical"
                recommendations["benefits"].append("Enable WebSocket support")
            elif current_version in self.KNOWN_ISSUES:
                recommendations["upgrade_priority"] = "high"
                recommendations["benefits"].append("Fix known compatibility issues")
            elif current < recommended:
                recommendations["upgrade_priority"] = "medium"
                recommendations["benefits"].append("Improved WebSocket performance")
                recommendations["benefits"].append("Enhanced stability")

            # List missing features
            for feature, required_version in self.FEATURE_MATRIX.items():
                if current < version.parse(required_version):
                    recommendations["missing_features"].append({
                        "feature": feature,
                        "required_version": required_version
                    })

            # Add potential risks
            if recommendations["should_upgrade"]:
                recommendations["risks"].extend([
                    "Configuration changes may be required",
                    "Service restart needed",
                    "Potential brief downtime during upgrade"
                ])

            # Add benefits based on missing features
            if any(f["feature"] == "websocket_compression" for f in recommendations["missing_features"]):
                recommendations["benefits"].append("WebSocket compression support")

            if any(f["feature"] == "enhanced_keep_alive" for f in recommendations["missing_features"]):
                recommendations["benefits"].append("Enhanced connection keep-alive")

            self.log_action("get_upgrade_recommendations", "completed", {
                "current_version": current_version,
                "should_upgrade": recommendations["should_upgrade"],
                "upgrade_priority": recommendations["upgrade_priority"],
                "missing_features_count": len(recommendations["missing_features"])
            })

            return recommendations

        except Exception as e:
            self.log_action("get_upgrade_recommendations", "error", {
                "error": str(e),
                "error_type": type(e).__name__
            })
            return {
                "error": str(e),
                "current_version": current_version
            }

    def validate_system_compatibility(self) -> Dict[str, Any]:
        """
        Perform comprehensive system compatibility check.

        Returns:
            Dictionary with complete compatibility assessment
        """
        self.log_action("validate_system_compatibility", "in_progress")

        compatibility_report = {
            "timestamp": datetime.now().isoformat(),
            "cloudflared_found": False,
            "version": None,
            "websocket_compatible": False,
            "tls_1_3_support": False,
            "overall_status": "unknown",
            "warnings": [],
            "errors": [],
            "recommendations": {},
            "supported_features": [],
            "missing_features": []
        }

        try:
            # Check if cloudflared is installed
            found, version_str, error = self.get_installed_version()

            if not found:
                compatibility_report["errors"].append(error or "cloudflared not found")
                compatibility_report["overall_status"] = "incompatible"
                self.log_action("validate_system_compatibility", "completed", {
                    "overall_status": "incompatible",
                    "reason": "cloudflared not found"
                })
                return compatibility_report

            compatibility_report["cloudflared_found"] = True
            compatibility_report["version"] = version_str

            # Check WebSocket compatibility
            ws_compatible, ws_warnings, ws_errors = self.check_websocket_compatibility(version_str)
            compatibility_report["websocket_compatible"] = ws_compatible
            compatibility_report["warnings"].extend(ws_warnings)
            compatibility_report["errors"].extend(ws_errors)

            # Check TLS 1.3 support
            tls_support, _ = self.check_feature_support(version_str, "tls_1_3")
            compatibility_report["tls_1_3_support"] = tls_support

            # Get supported and missing features
            for feature, required_version in self.FEATURE_MATRIX.items():
                is_supported, _ = self.check_feature_support(version_str, feature)
                if is_supported:
                    compatibility_report["supported_features"].append(feature)
                else:
                    compatibility_report["missing_features"].append({
                        "feature": feature,
                        "required_version": required_version
                    })

            # Get upgrade recommendations
            compatibility_report["recommendations"] = self.get_upgrade_recommendations(version_str)

            # Determine overall status
            if ws_errors:
                compatibility_report["overall_status"] = "incompatible"
            elif ws_warnings or not tls_support:
                compatibility_report["overall_status"] = "compatible_with_warnings"
            else:
                compatibility_report["overall_status"] = "fully_compatible"

            self.log_action("validate_system_compatibility", "completed", {
                "overall_status": compatibility_report["overall_status"],
                "version": version_str,
                "websocket_compatible": ws_compatible,
                "tls_1_3_support": tls_support,
                "supported_features_count": len(compatibility_report["supported_features"]),
                "missing_features_count": len(compatibility_report["missing_features"])
            })

            return compatibility_report

        except Exception as e:
            error_msg = f"System compatibility check failed: {str(e)}"
            compatibility_report["errors"].append(error_msg)
            compatibility_report["overall_status"] = "error"

            self.log_action("validate_system_compatibility", "error", {
                "error": error_msg,
                "error_type": type(e).__name__
            })

            return compatibility_report

    def get_version_info(self) -> Dict[str, Any]:
        """
        Get comprehensive version information and requirements.

        Returns:
            Dictionary with version requirements and compatibility matrix
        """
        self.log_action("get_version_info", "in_progress")

        version_info = {
            "requirements": {
                "minimum_websocket": self.MIN_VERSION_WEBSOCKET,
                "recommended": self.MIN_VERSION_RECOMMENDED,
                "minimum_tls_1_3": self.MIN_VERSION_TLS13
            },
            "feature_matrix": self.FEATURE_MATRIX,
            "known_issues": self.KNOWN_ISSUES,
            "compatibility_check_timestamp": datetime.now().isoformat()
        }

        # Add current system status
        found, current_version, _ = self.get_installed_version()
        if found:
            version_info["current_system"] = {
                "version": current_version,
                "compatibility": self.validate_system_compatibility()
            }

        self.log_action("get_version_info", "completed", {
            "has_current_version": found,
            "feature_count": len(self.FEATURE_MATRIX),
            "known_issues_count": len(self.KNOWN_ISSUES)
        })

        return version_info