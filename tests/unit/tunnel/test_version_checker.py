"""
Unit tests for VersionChecker - Cloudflared Version Compatibility
"""

import json
import pytest
from unittest.mock import patch, MagicMock
from src.beast_mode.observatory.tunnel.version_checker import VersionChecker


class TestVersionChecker:
    """Test cases for VersionChecker class."""

    def setup_method(self):
        """Set up test fixtures."""
        self.checker = VersionChecker()

    def test_init(self):
        """Test VersionChecker initialization."""
        assert self.checker is not None
        assert self.checker.MIN_VERSION_WEBSOCKET == "2023.5.0"
        assert self.checker.MIN_VERSION_RECOMMENDED == "2025.9.1"
        assert self.checker.MIN_VERSION_TLS13 == "2023.8.0"
        assert len(self.checker.FEATURE_MATRIX) > 0
        assert len(self.checker.KNOWN_ISSUES) > 0

    def test_log_action(self, capsys):
        """Test JSON logging functionality."""
        self.checker.log_action("test_action", "completed", {"key": "value"})
        
        captured = capsys.readouterr()
        log_entry = json.loads(captured.out.strip())
        
        assert log_entry["task"] == "1"
        assert log_entry["action"] == "VersionChecker.test_action"
        assert log_entry["status"] == "completed"
        assert log_entry["details"]["key"] == "value"
        assert "timestamp" in log_entry

    @patch('subprocess.run')
    def test_get_installed_version_success(self, mock_run):
        """Test successful version detection."""
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = "cloudflared version 2025.9.1 (built 2025-01-15)"
        mock_result.stderr = ""
        mock_run.return_value = mock_result
        
        found, version_str, error = self.checker.get_installed_version()
        
        assert found is True
        assert version_str == "2025.9.1"
        assert error is None
        
        mock_run.assert_called_once_with(
            ["cloudflared", "--version"],
            capture_output=True,
            text=True,
            timeout=10
        )

    @patch('subprocess.run')
    def test_get_installed_version_parse_error(self, mock_run):
        """Test version detection with unparseable output."""
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = "unexpected output format"
        mock_result.stderr = ""
        mock_run.return_value = mock_result
        
        found, version_str, error = self.checker.get_installed_version()
        
        assert found is False
        assert version_str is None
        assert "Could not parse version" in error

    @patch('subprocess.run')
    def test_get_installed_version_command_failed(self, mock_run):
        """Test version detection when command fails."""
        mock_result = MagicMock()
        mock_result.returncode = 1
        mock_result.stdout = ""
        mock_result.stderr = "cloudflared: command not found"
        mock_run.return_value = mock_result
        
        found, version_str, error = self.checker.get_installed_version()
        
        assert found is False
        assert version_str is None
        assert "cloudflared command failed" in error

    @patch('subprocess.run')
    def test_get_installed_version_timeout(self, mock_run):
        """Test version detection timeout."""
        mock_run.side_effect = TimeoutError("Command timed out")
        
        found, version_str, error = self.checker.get_installed_version()
        
        assert found is False
        assert version_str is None
        assert "Timeout getting cloudflared version" in error

    @patch('subprocess.run')
    def test_get_installed_version_not_found(self, mock_run):
        """Test version detection when cloudflared not found."""
        mock_run.side_effect = FileNotFoundError("cloudflared not found")
        
        found, version_str, error = self.checker.get_installed_version()
        
        assert found is False
        assert version_str is None
        assert "cloudflared not found in PATH" in error

    def test_check_websocket_compatibility_minimum_version(self):
        """Test WebSocket compatibility check with minimum version."""
        is_compatible, warnings, errors = self.checker.check_websocket_compatibility("2023.5.0")
        
        assert is_compatible is True
        assert len(errors) == 0
        assert len(warnings) > 0  # Should have warnings about being below recommended

    def test_check_websocket_compatibility_below_minimum(self):
        """Test WebSocket compatibility check below minimum version."""
        is_compatible, warnings, errors = self.checker.check_websocket_compatibility("2023.4.0")
        
        assert is_compatible is False
        assert len(errors) > 0
        assert "does not support WebSocket proxy" in errors[0]

    def test_check_websocket_compatibility_recommended_version(self):
        """Test WebSocket compatibility check with recommended version."""
        is_compatible, warnings, errors = self.checker.check_websocket_compatibility("2025.9.1")
        
        assert is_compatible is True
        assert len(errors) == 0
        assert len(warnings) == 0  # Should have no warnings

    def test_check_websocket_compatibility_known_issues(self):
        """Test WebSocket compatibility check with known issues."""
        is_compatible, warnings, errors = self.checker.check_websocket_compatibility("2023.3.0")
        
        assert is_compatible is True  # Above minimum
        assert len(errors) == 0
        assert len(warnings) > 0
        assert any("Known issue" in warning for warning in warnings)

    def test_check_websocket_compatibility_missing_features(self):
        """Test WebSocket compatibility check with missing features."""
        is_compatible, warnings, errors = self.checker.check_websocket_compatibility("2023.5.0")
        
        assert is_compatible is True
        assert len(errors) == 0
        assert len(warnings) > 0
        assert any("Missing features" in warning for warning in warnings)

    def test_check_websocket_compatibility_invalid_version(self):
        """Test WebSocket compatibility check with invalid version."""
        is_compatible, warnings, errors = self.checker.check_websocket_compatibility("invalid.version")
        
        assert is_compatible is False
        assert len(errors) > 0
        assert "Error checking version compatibility" in errors[0]

    def test_check_feature_support_supported(self):
        """Test feature support check for supported feature."""
        is_supported, required_version = self.checker.check_feature_support("2025.9.1", "websocket_proxy")
        
        assert is_supported is True
        assert required_version is None

    def test_check_feature_support_not_supported(self):
        """Test feature support check for unsupported feature."""
        is_supported, required_version = self.checker.check_feature_support("2023.5.0", "websocket_compression")
        
        assert is_supported is False
        assert required_version == "2024.8.0"

    def test_check_feature_support_unknown_feature(self):
        """Test feature support check for unknown feature."""
        is_supported, required_version = self.checker.check_feature_support("2025.9.1", "unknown_feature")
        
        assert is_supported is False
        assert "Unknown feature" in required_version

    def test_check_feature_support_invalid_version(self):
        """Test feature support check with invalid version."""
        is_supported, required_version = self.checker.check_feature_support("invalid.version", "websocket_proxy")
        
        assert is_supported is False
        assert "Error checking feature support" in required_version

    def test_get_upgrade_recommendations_current_version(self):
        """Test upgrade recommendations for current recommended version."""
        recommendations = self.checker.get_upgrade_recommendations("2025.9.1")
        
        assert recommendations["current_version"] == "2025.9.1"
        assert recommendations["should_upgrade"] is False
        assert recommendations["upgrade_priority"] == "low"
        assert len(recommendations["benefits"]) == 0
        assert len(recommendations["missing_features"]) == 0

    def test_get_upgrade_recommendations_critical_upgrade(self):
        """Test upgrade recommendations for critical upgrade needed."""
        recommendations = self.checker.get_upgrade_recommendations("2023.4.0")
        
        assert recommendations["current_version"] == "2023.4.0"
        assert recommendations["should_upgrade"] is True
        assert recommendations["upgrade_priority"] == "critical"
        assert "Enable WebSocket support" in recommendations["benefits"]

    def test_get_upgrade_recommendations_high_priority(self):
        """Test upgrade recommendations for high priority upgrade."""
        recommendations = self.checker.get_upgrade_recommendations("2023.3.0")
        
        assert recommendations["current_version"] == "2023.3.0"
        assert recommendations["should_upgrade"] is True
        assert recommendations["upgrade_priority"] == "high"
        assert "Fix known compatibility issues" in recommendations["benefits"]

    def test_get_upgrade_recommendations_medium_priority(self):
        """Test upgrade recommendations for medium priority upgrade."""
        recommendations = self.checker.get_upgrade_recommendations("2024.1.0")
        
        assert recommendations["current_version"] == "2024.1.0"
        assert recommendations["should_upgrade"] is True
        assert recommendations["upgrade_priority"] == "medium"
        assert "Improved WebSocket performance" in recommendations["benefits"]

    def test_get_upgrade_recommendations_missing_features(self):
        """Test upgrade recommendations with missing features."""
        recommendations = self.checker.get_upgrade_recommendations("2023.5.0")
        
        assert recommendations["should_upgrade"] is True
        assert len(recommendations["missing_features"]) > 0
        assert len(recommendations["benefits"]) > 0

    def test_get_upgrade_recommendations_invalid_version(self):
        """Test upgrade recommendations with invalid version."""
        recommendations = self.checker.get_upgrade_recommendations("invalid.version")
        
        assert "error" in recommendations
        assert recommendations["current_version"] == "invalid.version"

    @patch.object(VersionChecker, 'get_installed_version')
    def test_validate_system_compatibility_not_found(self, mock_get_version):
        """Test system compatibility validation when cloudflared not found."""
        mock_get_version.return_value = (False, None, "cloudflared not found")
        
        report = self.checker.validate_system_compatibility()
        
        assert report["cloudflared_found"] is False
        assert report["overall_status"] == "incompatible"
        assert "cloudflared not found" in report["errors"]

    @patch.object(VersionChecker, 'get_installed_version')
    def test_validate_system_compatibility_incompatible(self, mock_get_version):
        """Test system compatibility validation with incompatible version."""
        mock_get_version.return_value = (True, "2023.4.0", None)
        
        report = self.checker.validate_system_compatibility()
        
        assert report["cloudflared_found"] is True
        assert report["version"] == "2023.4.0"
        assert report["websocket_compatible"] is False
        assert report["overall_status"] == "incompatible"

    @patch.object(VersionChecker, 'get_installed_version')
    def test_validate_system_compatibility_with_warnings(self, mock_get_version):
        """Test system compatibility validation with warnings."""
        mock_get_version.return_value = (True, "2023.5.0", None)
        
        report = self.checker.validate_system_compatibility()
        
        assert report["cloudflared_found"] is True
        assert report["version"] == "2023.5.0"
        assert report["websocket_compatible"] is True
        assert report["overall_status"] == "compatible_with_warnings"
        assert len(report["warnings"]) > 0

    @patch.object(VersionChecker, 'get_installed_version')
    def test_validate_system_compatibility_fully_compatible(self, mock_get_version):
        """Test system compatibility validation fully compatible."""
        mock_get_version.return_value = (True, "2025.9.1", None)
        
        report = self.checker.validate_system_compatibility()
        
        assert report["cloudflared_found"] is True
        assert report["version"] == "2025.9.1"
        assert report["websocket_compatible"] is True
        assert report["tls_1_3_support"] is True
        assert report["overall_status"] == "fully_compatible"
        assert len(report["warnings"]) == 0
        assert len(report["errors"]) == 0

    @patch.object(VersionChecker, 'get_installed_version')
    def test_validate_system_compatibility_error(self, mock_get_version):
        """Test system compatibility validation error handling."""
        mock_get_version.side_effect = Exception("Test exception")
        
        report = self.checker.validate_system_compatibility()
        
        assert report["overall_status"] == "error"
        assert "System compatibility check failed" in report["errors"]

    @patch.object(VersionChecker, 'get_installed_version')
    def test_get_version_info_with_current_version(self, mock_get_version):
        """Test getting version info with current version."""
        mock_get_version.return_value = (True, "2025.9.1", None)
        
        version_info = self.checker.get_version_info()
        
        assert "requirements" in version_info
        assert "feature_matrix" in version_info
        assert "known_issues" in version_info
        assert "current_system" in version_info
        assert version_info["current_system"]["version"] == "2025.9.1"

    @patch.object(VersionChecker, 'get_installed_version')
    def test_get_version_info_without_current_version(self, mock_get_version):
        """Test getting version info without current version."""
        mock_get_version.return_value = (False, None, "not found")
        
        version_info = self.checker.get_version_info()
        
        assert "requirements" in version_info
        assert "feature_matrix" in version_info
        assert "known_issues" in version_info
        assert "current_system" not in version_info

    def test_version_checker_integration(self):
        """Test complete VersionChecker workflow."""
        # Test feature support matrix
        for feature, required_version in self.checker.FEATURE_MATRIX.items():
            is_supported, _ = self.checker.check_feature_support(required_version, feature)
            assert is_supported is True
        
        # Test known issues
        for version, issues in self.checker.KNOWN_ISSUES.items():
            is_compatible, warnings, errors = self.checker.check_websocket_compatibility(version)
            assert len(warnings) > 0  # Should have warnings about known issues
        
        # Test version requirements
        assert self.checker.MIN_VERSION_WEBSOCKET < self.checker.MIN_VERSION_TLS13
        assert self.checker.MIN_VERSION_TLS13 < self.checker.MIN_VERSION_RECOMMENDED
        
        # Test upgrade recommendations for different scenarios
        critical_rec = self.checker.get_upgrade_recommendations("2023.4.0")
        assert critical_rec["upgrade_priority"] == "critical"
        
        high_rec = self.checker.get_upgrade_recommendations("2023.3.0")
        assert high_rec["upgrade_priority"] == "high"
        
        medium_rec = self.checker.get_upgrade_recommendations("2024.1.0")
        assert medium_rec["upgrade_priority"] == "medium"
        
        low_rec = self.checker.get_upgrade_recommendations("2025.9.1")
        assert low_rec["upgrade_priority"] == "low"

    def test_version_comparison_edge_cases(self):
        """Test version comparison edge cases."""
        # Test exact version match
        is_compatible, warnings, errors = self.checker.check_websocket_compatibility("2023.5.0")
        assert is_compatible is True
        
        # Test patch version differences
        is_compatible, warnings, errors = self.checker.check_websocket_compatibility("2023.5.1")
        assert is_compatible is True
        
        # Test minor version differences
        is_compatible, warnings, errors = self.checker.check_websocket_compatibility("2023.6.0")
        assert is_compatible is True
        
        # Test major version differences
        is_compatible, warnings, errors = self.checker.check_websocket_compatibility("2024.1.0")
        assert is_compatible is True