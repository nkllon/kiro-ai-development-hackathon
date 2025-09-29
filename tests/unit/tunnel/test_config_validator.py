"""
Unit tests for ConfigValidator
"""

import pytest

from src.beast_mode.observatory.tunnel.config_validator import (
    ConfigValidator,
    ValidationResult,
    ValidationIssue,
    ValidationLevel
)


class TestValidationLevel:
    """Test ValidationLevel enum"""
    
    def test_validation_levels(self):
        """Test that all validation levels are defined"""
        assert ValidationLevel.INFO.value == "info"
        assert ValidationLevel.WARNING.value == "warning"
        assert ValidationLevel.ERROR.value == "error"
        assert ValidationLevel.CRITICAL.value == "critical"


class TestValidationIssue:
    """Test ValidationIssue data structure"""
    
    def test_validation_issue_creation(self):
        """Test validation issue creation"""
        issue = ValidationIssue(
            level=ValidationLevel.ERROR,
            field="test.field",
            message="Test error message",
            suggestion="Test suggestion"
        )
        
        assert issue.level == ValidationLevel.ERROR
        assert issue.field == "test.field"
        assert issue.message == "Test error message"
        assert issue.suggestion == "Test suggestion"
    
    def test_validation_issue_without_suggestion(self):
        """Test validation issue without suggestion"""
        issue = ValidationIssue(
            level=ValidationLevel.WARNING,
            field="test.field",
            message="Test warning message"
        )
        
        assert issue.level == ValidationLevel.WARNING
        assert issue.field == "test.field"
        assert issue.message == "Test warning message"
        assert issue.suggestion is None


class TestValidationResult:
    """Test ValidationResult data structure"""
    
    def test_validation_result_creation(self):
        """Test validation result creation"""
        issues = [
            ValidationIssue(ValidationLevel.WARNING, "field1", "Warning message"),
            ValidationIssue(ValidationLevel.ERROR, "field2", "Error message")
        ]
        
        result = ValidationResult(
            is_valid=False,
            issues=issues,
            warnings=[issues[0]],
            errors=[issues[1]],
            critical_errors=[],
            summary="Configuration has 1 error that should be fixed"
        )
        
        assert result.is_valid is False
        assert len(result.issues) == 2
        assert len(result.warnings) == 1
        assert len(result.errors) == 1
        assert len(result.critical_errors) == 0
        assert "error" in result.summary


class TestConfigValidator:
    """Test ConfigValidator functionality"""
    
    @pytest.fixture
    def validator(self):
        """Create validator instance for tests"""
        return ConfigValidator()
    
    @pytest.fixture
    def valid_config(self):
        """Valid tunnel configuration"""
        return {
            "tunnel": "test_tunnel",
            "credentials-file": "/tmp/test_credentials.json",
            "ingress": [
                {
                    "hostname": "test.example.com",
                    "service": "http://localhost:8080",
                    "originRequest": {
                        "httpHostHeader": "test.example.com",
                        "connectTimeout": "30s",
                        "proxyType": ""
                    }
                },
                {
                    "service": "http_status:404"
                }
            ]
        }
    
    def test_validator_initialization(self, validator):
        """Test validator initialization"""
        assert validator is not None
    
    def test_validate_config_valid(self, validator, valid_config):
        """Test validation of valid configuration"""
        result = validator.validate_config(valid_config)
        
        assert result.is_valid is True
        assert len(result.critical_errors) == 0
        assert len(result.errors) == 0
    
    def test_validate_config_missing_tunnel(self, validator):
        """Test validation of config missing tunnel field"""
        config = {
            "credentials-file": "/tmp/test.json",
            "ingress": [
                {"hostname": "test.com", "service": "http://localhost:8080"},
                {"service": "http_status:404"}
            ]
        }
        
        result = validator.validate_config(config)
        
        assert result.is_valid is False
        assert len(result.critical_errors) == 1
        assert result.critical_errors[0].field == "tunnel"
        assert "Required field 'tunnel' is missing" in result.critical_errors[0].message
    
    def test_validate_config_missing_credentials_file(self, validator):
        """Test validation of config missing credentials-file field"""
        config = {
            "tunnel": "test_tunnel",
            "ingress": [
                {"hostname": "test.com", "service": "http://localhost:8080"},
                {"service": "http_status:404"}
            ]
        }
        
        result = validator.validate_config(config)
        
        assert result.is_valid is False
        assert len(result.critical_errors) == 1
        assert result.critical_errors[0].field == "credentials-file"
    
    def test_validate_config_missing_ingress(self, validator):
        """Test validation of config missing ingress field"""
        config = {
            "tunnel": "test_tunnel",
            "credentials-file": "/tmp/test.json"
        }
        
        result = validator.validate_config(config)
        
        assert result.is_valid is False
        assert len(result.critical_errors) == 1
        assert result.critical_errors[0].field == "ingress"
    
    def test_validate_config_invalid_tunnel_name(self, validator):
        """Test validation of invalid tunnel name"""
        config = {
            "tunnel": "invalid tunnel name!",  # Invalid characters
            "credentials-file": "/tmp/test.json",
            "ingress": [
                {"hostname": "test.com", "service": "http://localhost:8080"},
                {"service": "http_status:404"}
            ]
        }
        
        result = validator.validate_config(config)
        
        assert result.is_valid is False
        assert len(result.errors) == 1
        assert result.errors[0].field == "tunnel"
        assert "invalid characters" in result.errors[0].message.lower()
    
    def test_validate_config_tunnel_name_not_string(self, validator):
        """Test validation of tunnel name that's not a string"""
        config = {
            "tunnel": 123,  # Not a string
            "credentials-file": "/tmp/test.json",
            "ingress": [
                {"hostname": "test.com", "service": "http://localhost:8080"},
                {"service": "http_status:404"}
            ]
        }
        
        result = validator.validate_config(config)
        
        assert result.is_valid is False
        assert len(result.errors) == 1
        assert result.errors[0].field == "tunnel"
        assert "must be a string" in result.errors[0].message
    
    def test_validate_config_credentials_file_not_string(self, validator):
        """Test validation of credentials file that's not a string"""
        config = {
            "tunnel": "test_tunnel",
            "credentials-file": 123,  # Not a string
            "ingress": [
                {"hostname": "test.com", "service": "http://localhost:8080"},
                {"service": "http_status:404"}
            ]
        }
        
        result = validator.validate_config(config)
        
        assert result.is_valid is False
        assert len(result.errors) == 1
        assert result.errors[0].field == "credentials-file"
        assert "must be a string" in result.errors[0].message
    
    def test_validate_config_credentials_file_no_json_extension(self, validator):
        """Test validation of credentials file without .json extension"""
        config = {
            "tunnel": "test_tunnel",
            "credentials-file": "/tmp/test_credentials.txt",  # Wrong extension
            "ingress": [
                {"hostname": "test.com", "service": "http://localhost:8080"},
                {"service": "http_status:404"}
            ]
        }
        
        result = validator.validate_config(config)
        
        assert result.is_valid is True  # Should be valid but with warning
        assert len(result.warnings) == 1
        assert result.warnings[0].field == "credentials-file"
        assert ".json extension" in result.warnings[0].message
    
    def test_validate_config_empty_ingress(self, validator):
        """Test validation of config with empty ingress list"""
        config = {
            "tunnel": "test_tunnel",
            "credentials-file": "/tmp/test.json",
            "ingress": []
        }
        
        result = validator.validate_config(config)
        
        assert result.is_valid is False
        assert len(result.critical_errors) == 1
        assert result.critical_errors[0].field == "ingress"
        assert "At least one ingress rule is required" in result.critical_errors[0].message
    
    def test_validate_config_ingress_not_list(self, validator):
        """Test validation of config with ingress that's not a list"""
        config = {
            "tunnel": "test_tunnel",
            "credentials-file": "/tmp/test.json",
            "ingress": "not_a_list"
        }
        
        result = validator.validate_config(config)
        
        assert result.is_valid is False
        assert len(result.critical_errors) == 1
        assert result.critical_errors[0].field == "ingress"
        assert "must be a list" in result.critical_errors[0].message
    
    def test_validate_config_missing_catch_all(self, validator):
        """Test validation of config without catch-all rule"""
        config = {
            "tunnel": "test_tunnel",
            "credentials-file": "/tmp/test.json",
            "ingress": [
                {"hostname": "test.com", "service": "http://localhost:8080"}
            ]
        }
        
        result = validator.validate_config(config)
        
        assert result.is_valid is True  # Should be valid but with warning
        assert len(result.warnings) == 1
        assert result.warnings[0].field == "ingress"
        assert "No catch-all rule found" in result.warnings[0].message
    
    def test_validate_config_ingress_missing_service(self, validator):
        """Test validation of ingress rule missing service"""
        config = {
            "tunnel": "test_tunnel",
            "credentials-file": "/tmp/test.json",
            "ingress": [
                {"hostname": "test.com"},  # Missing service
                {"service": "http_status:404"}
            ]
        }
        
        result = validator.validate_config(config)
        
        assert result.is_valid is False
        assert len(result.critical_errors) == 1
        assert "ingress[0].service" in result.critical_errors[0].field
    
    def test_validate_config_ingress_service_not_string(self, validator):
        """Test validation of ingress service that's not a string"""
        config = {
            "tunnel": "test_tunnel",
            "credentials-file": "/tmp/test.json",
            "ingress": [
                {"hostname": "test.com", "service": 123},  # Not a string
                {"service": "http_status:404"}
            ]
        }
        
        result = validator.validate_config(config)
        
        assert result.is_valid is False
        assert len(result.errors) == 1
        assert "ingress[0].service" in result.errors[0].field
        assert "must be a string" in result.errors[0].message
    
    def test_validate_config_invalid_service_format(self, validator):
        """Test validation of invalid service format"""
        config = {
            "tunnel": "test_tunnel",
            "credentials-file": "/tmp/test.json",
            "ingress": [
                {"hostname": "test.com", "service": "invalid_service_format"},
                {"service": "http_status:404"}
            ]
        }
        
        result = validator.validate_config(config)
        
        assert result.is_valid is True  # Should be valid but with warning
        assert len(result.warnings) == 1
        assert "ingress[0].service" in result.warnings[0].field
        assert "may not be valid" in result.warnings[0].message
    
    def test_validate_config_invalid_hostname_format(self, validator):
        """Test validation of invalid hostname format"""
        config = {
            "tunnel": "test_tunnel",
            "credentials-file": "/tmp/test.json",
            "ingress": [
                {"hostname": "invalid..hostname", "service": "http://localhost:8080"},
                {"service": "http_status:404"}
            ]
        }
        
        result = validator.validate_config(config)
        
        assert result.is_valid is True  # Should be valid but with warning
        assert len(result.warnings) == 1
        assert "ingress[0].hostname" in result.warnings[0].field
        assert "format may be invalid" in result.warnings[0].message
    
    def test_validate_config_origin_request_not_dict(self, validator):
        """Test validation of originRequest that's not a dictionary"""
        config = {
            "tunnel": "test_tunnel",
            "credentials-file": "/tmp/test.json",
            "ingress": [
                {
                    "hostname": "test.com",
                    "service": "http://localhost:8080",
                    "originRequest": "not_a_dict"
                },
                {"service": "http_status:404"}
            ]
        }
        
        result = validator.validate_config(config)
        
        assert result.is_valid is False
        assert len(result.errors) == 1
        assert "ingress[0].originRequest" in result.errors[0].field
        assert "must be a dictionary" in result.errors[0].message
    
    def test_validate_config_invalid_timeout_format(self, validator):
        """Test validation of invalid timeout format"""
        config = {
            "tunnel": "test_tunnel",
            "credentials-file": "/tmp/test.json",
            "ingress": [
                {
                    "hostname": "test.com",
                    "service": "http://localhost:8080",
                    "originRequest": {
                        "connectTimeout": "invalid_timeout_format"
                    }
                },
                {"service": "http_status:404"}
            ]
        }
        
        result = validator.validate_config(config)
        
        assert result.is_valid is True  # Should be valid but with warning
        assert len(result.warnings) == 1
        assert "ingress[0].originRequest.connectTimeout" in result.warnings[0].field
        assert "format may be invalid" in result.warnings[0].message
    
    def test_validate_config_invalid_numeric_value(self, validator):
        """Test validation of invalid numeric value"""
        config = {
            "tunnel": "test_tunnel",
            "credentials-file": "/tmp/test.json",
            "ingress": [
                {
                    "hostname": "test.com",
                    "service": "http://localhost:8080",
                    "originRequest": {
                        "keepAliveConnections": -5  # Negative value
                    }
                },
                {"service": "http_status:404"}
            ]
        }
        
        result = validator.validate_config(config)
        
        assert result.is_valid is False
        assert len(result.errors) == 1
        assert "ingress[0].originRequest.keepAliveConnections" in result.errors[0].field
        assert "non-negative integer" in result.errors[0].message
    
    def test_validate_config_proxy_type_warning(self, validator):
        """Test validation warning for non-empty proxyType"""
        config = {
            "tunnel": "test_tunnel",
            "credentials-file": "/tmp/test.json",
            "ingress": [
                {
                    "hostname": "test.com",
                    "service": "http://localhost:8080",
                    "originRequest": {
                        "proxyType": "http"  # Should be empty for WebSocket
                    }
                },
                {"service": "http_status:404"}
            ]
        }
        
        result = validator.validate_config(config)
        
        assert result.is_valid is True  # Should be valid but with warning
        assert len(result.warnings) == 1
        assert "ingress[0].originRequest.proxyType" in result.warnings[0].field
        assert "should be empty string" in result.warnings[0].message
    
    def test_validate_websocket_support_no_websocket_rules(self, validator):
        """Test validation when no WebSocket rules are found"""
        config = {
            "tunnel": "test_tunnel",
            "credentials-file": "/tmp/test.json",
            "ingress": [
                {
                    "hostname": "test.com",
                    "service": "http://localhost:8080",
                    "originRequest": {
                        "proxyType": "http"  # WebSocket not enabled
                    }
                },
                {"service": "http_status:404"}
            ]
        }
        
        result = validator.validate_config(config)
        
        assert result.is_valid is True
        # Should have info message about no WebSocket rules
        info_issues = [i for i in result.issues if i.level == ValidationLevel.INFO]
        assert len(info_issues) == 1
        assert "No WebSocket-enabled rules found" in info_issues[0].message
    
    def test_validate_websocket_support_missing_http_host_header(self, validator):
        """Test validation warning for missing httpHostHeader in WebSocket rules"""
        config = {
            "tunnel": "test_tunnel",
            "credentials-file": "/tmp/test.json",
            "ingress": [
                {
                    "hostname": "test.com",
                    "service": "http://localhost:8080",
                    "originRequest": {
                        "proxyType": ""  # WebSocket enabled
                        # Missing httpHostHeader
                    }
                },
                {"service": "http_status:404"}
            ]
        }
        
        result = validator.validate_config(config)
        
        assert result.is_valid is True  # Should be valid but with warning
        assert len(result.warnings) == 1
        assert "ingress[0].originRequest.httpHostHeader" in result.warnings[0].field
        assert "recommended for WebSocket connections" in result.warnings[0].message
    
    def test_validate_websocket_config_quick_validation(self, validator, valid_config):
        """Test quick WebSocket configuration validation"""
        is_valid = validator.validate_websocket_config(valid_config)
        assert is_valid is True
    
    def test_validate_websocket_config_no_websocket_support(self, validator):
        """Test quick WebSocket validation with no WebSocket support"""
        config = {
            "tunnel": "test_tunnel",
            "credentials-file": "/tmp/test.json",
            "ingress": [
                {
                    "hostname": "test.com",
                    "service": "http://localhost:8080",
                    "originRequest": {
                        "proxyType": "http"  # WebSocket not enabled
                    }
                },
                {"service": "http_status:404"}
            ]
        }
        
        is_valid = validator.validate_websocket_config(config)
        assert is_valid is False
    
    def test_validate_config_with_unknown_field(self, validator):
        """Test validation of config with unknown field"""
        config = {
            "tunnel": "test_tunnel",
            "credentials-file": "/tmp/test.json",
            "unknown_field": "unknown_value",
            "ingress": [
                {"hostname": "test.com", "service": "http://localhost:8080"},
                {"service": "http_status:404"}
            ]
        }
        
        result = validator.validate_config(config)
        
        assert result.is_valid is True  # Should be valid but with warning
        assert len(result.warnings) == 1
        assert result.warnings[0].field == "unknown_field"
        assert "Unknown field" in result.warnings[0].message
    
    def test_validate_config_multiple_issues(self, validator):
        """Test validation with multiple issues"""
        config = {
            "tunnel": 123,  # Not a string
            "credentials-file": 456,  # Not a string
            "ingress": "not_a_list"  # Not a list
        }
        
        result = validator.validate_config(config)
        
        assert result.is_valid is False
        assert len(result.critical_errors) == 1  # Missing ingress
        assert len(result.errors) == 2  # tunnel and credentials-file type errors