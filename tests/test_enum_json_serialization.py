"""
Unit tests for enum JSON serialization functionality.

Tests the EnumJSONEncoder and SerializationHandler classes to ensure
proper enum serialization and JSON compatibility.

Requirements: 6.1, 6.4 - Fix enum serialization and JSON compatibility
"""

import json
import pytest
from enum import Enum
from dataclasses import dataclass
from typing import Dict, Any

from src.beast_mode.utils.enum_serialization import (
    EnumJSONEncoder,
    SerializationHandler,
    make_enum_json_serializable,
    dumps_with_enums,
    safe_dumps
)
from src.beast_mode.compliance.models import IssueSeverity, ComplianceIssueType
from src.beast_mode.core.health_monitoring import AlertSeverity


class _TestEnum(Enum):
    """Test enum for serialization testing"""
    VALUE_ONE = "value_one"
    VALUE_TWO = "value_two"
    VALUE_THREE = 42


@dataclass
class _TestDataClass:
    """Test dataclass containing enums"""
    severity: IssueSeverity
    issue_type: ComplianceIssueType
    alert_level: AlertSeverity
    test_enum: _TestEnum
    name: str = "test"


class TestEnumJSONEncoder:
    """Test cases for EnumJSONEncoder class"""
    
    def test_encode_single_enum(self):
        """Test encoding a single enum value"""
        encoder = EnumJSONEncoder()
        result = encoder.default(IssueSeverity.HIGH)
        assert result == "high"
        
    def test_encode_different_enum_types(self):
        """Test encoding different enum types"""
        encoder = EnumJSONEncoder()
        
        # String enum
        assert encoder.default(IssueSeverity.CRITICAL) == "critical"
        
        # String enum from different class
        assert encoder.default(ComplianceIssueType.RDI_VIOLATION) == "rdi_violation"
        
        # String enum from health monitoring
        assert encoder.default(AlertSeverity.WARNING) == "warning"
        
        # Mixed type enum
        assert encoder.default(_TestEnum.VALUE_THREE) == 42
        assert encoder.default(_TestEnum.VALUE_ONE) == "value_one"
    
    def test_encode_non_enum_fallback(self):
        """Test that non-enum objects fall back to default behavior"""
        encoder = EnumJSONEncoder()
        
        # Should raise TypeError for non-serializable objects
        with pytest.raises(TypeError):
            encoder.default(object())
    
    def test_json_dumps_with_encoder(self):
        """Test using EnumJSONEncoder with json.dumps"""
        data = {
            "severity": IssueSeverity.HIGH,
            "issue_type": ComplianceIssueType.TEST_FAILURE,
            "alert": AlertSeverity.CRITICAL,
            "test_value": _TestEnum.VALUE_THREE,
            "regular_string": "normal_value"
        }
        
        result = json.dumps(data, cls=EnumJSONEncoder)
        parsed = json.loads(result)
        
        assert parsed["severity"] == "high"
        assert parsed["issue_type"] == "test_failure"
        assert parsed["alert"] == "critical"
        assert parsed["test_value"] == 42
        assert parsed["regular_string"] == "normal_value"


class TestSerializationHandler:
    """Test cases for SerializationHandler class"""
    
    def test_serialize_with_enums_basic(self):
        """Test basic enum serialization"""
        data = {"severity": IssueSeverity.MEDIUM}
        result = SerializationHandler.serialize_with_enums(data)
        parsed = json.loads(result)
        assert parsed["severity"] == "medium"
    
    def test_serialize_with_enums_complex(self):
        """Test complex data structure with enums"""
        data = {
            "issues": [
                {
                    "severity": IssueSeverity.HIGH,
                    "type": ComplianceIssueType.RDI_VIOLATION
                },
                {
                    "severity": IssueSeverity.LOW,
                    "type": ComplianceIssueType.TEST_FAILURE
                }
            ],
            "alerts": {
                "critical": AlertSeverity.CRITICAL,
                "info": AlertSeverity.INFO
            }
        }
        
        result = SerializationHandler.serialize_with_enums(data)
        parsed = json.loads(result)
        
        assert parsed["issues"][0]["severity"] == "high"
        assert parsed["issues"][0]["type"] == "rdi_violation"
        assert parsed["issues"][1]["severity"] == "low"
        assert parsed["issues"][1]["type"] == "test_failure"
        assert parsed["alerts"]["critical"] == "critical"
        assert parsed["alerts"]["info"] == "info"
    
    def test_ensure_enum_serializable(self):
        """Test adding __json__ method to enum classes"""
        # Create a new enum class for testing
        class NewTestEnum(Enum):
            TEST_VALUE = "test"
        
        # Initially should not have __json__ method
        assert not hasattr(NewTestEnum, '__json__')
        
        # Add serialization capability
        SerializationHandler.ensure_enum_serializable(NewTestEnum)
        
        # Should now have __json__ method
        assert hasattr(NewTestEnum, '__json__')
        
        # Test that it works
        enum_instance = NewTestEnum.TEST_VALUE
        assert enum_instance.__json__() == "test"
    
    def test_convert_enums_to_values_dict(self):
        """Test converting enums to values in dictionary"""
        data = {
            "severity": IssueSeverity.CRITICAL,
            "nested": {
                "type": ComplianceIssueType.DESIGN_MISALIGNMENT,
                "alert": AlertSeverity.WARNING
            },
            "regular_value": "unchanged"
        }
        
        result = SerializationHandler.convert_enums_to_values(data)
        
        assert result["severity"] == "critical"
        assert result["nested"]["type"] == "design_misalignment"
        assert result["nested"]["alert"] == "warning"
        assert result["regular_value"] == "unchanged"
    
    def test_convert_enums_to_values_list(self):
        """Test converting enums to values in list"""
        data = [
            IssueSeverity.HIGH,
            ComplianceIssueType.RM_NON_COMPLIANCE,
            "regular_string",
            42,
            [AlertSeverity.EMERGENCY, _TestEnum.VALUE_THREE]
        ]
        
        result = SerializationHandler.convert_enums_to_values(data)
        
        assert result[0] == "high"
        assert result[1] == "rm_non_compliance"
        assert result[2] == "regular_string"
        assert result[3] == 42
        assert result[4][0] == "emergency"
        assert result[4][1] == 42
    
    def test_convert_enums_to_values_single_enum(self):
        """Test converting single enum value"""
        result = SerializationHandler.convert_enums_to_values(IssueSeverity.LOW)
        assert result == "low"
    
    def test_safe_serialize_success(self):
        """Test safe serialization with successful case"""
        data = {"severity": IssueSeverity.MEDIUM}
        result = SerializationHandler.safe_serialize(data)
        parsed = json.loads(result)
        assert parsed["severity"] == "medium"
    
    def test_safe_serialize_fallback(self):
        """Test safe serialization with fallback handling"""
        # Create problematic data that might cause issues
        class ProblematicClass:
            def __init__(self):
                self.enum_value = IssueSeverity.HIGH
        
        data = {
            "severity": IssueSeverity.CRITICAL,
            "problematic": ProblematicClass()
        }
        
        # Should not raise exception, should handle gracefully
        result = SerializationHandler.safe_serialize(data)
        assert isinstance(result, str)
        
        # Should be valid JSON
        parsed = json.loads(result)
        # In fallback mode with default=str, enum gets string representation
        assert isinstance(parsed["severity"], str)
        assert "CRITICAL" in parsed["severity"]  # Should contain the enum value name


class TestDataClassSerialization:
    """Test serialization of dataclasses containing enums"""
    
    def test_serialize_dataclass_with_enums(self):
        """Test serializing dataclass containing enum fields"""
        test_obj = _TestDataClass(
            severity=IssueSeverity.HIGH,
            issue_type=ComplianceIssueType.TEST_FAILURE,
            alert_level=AlertSeverity.CRITICAL,
            test_enum=_TestEnum.VALUE_TWO
        )
        
        # Convert to dict first (dataclasses aren't directly JSON serializable)
        data = {
            "severity": test_obj.severity,
            "issue_type": test_obj.issue_type,
            "alert_level": test_obj.alert_level,
            "test_enum": test_obj.test_enum,
            "name": test_obj.name
        }
        
        result = SerializationHandler.serialize_with_enums(data)
        parsed = json.loads(result)
        
        assert parsed["severity"] == "high"
        assert parsed["issue_type"] == "test_failure"
        assert parsed["alert_level"] == "critical"
        assert parsed["test_enum"] == "value_two"
        assert parsed["name"] == "test"


class TestConvenienceFunctions:
    """Test convenience functions"""
    
    def test_make_enum_json_serializable(self):
        """Test making multiple enums serializable at once"""
        class Enum1(Enum):
            VALUE = "one"
        
        class Enum2(Enum):
            VALUE = "two"
        
        # Initially should not have __json__ methods
        assert not hasattr(Enum1, '__json__')
        assert not hasattr(Enum2, '__json__')
        
        # Make both serializable
        make_enum_json_serializable(Enum1, Enum2)
        
        # Both should now have __json__ methods
        assert hasattr(Enum1, '__json__')
        assert hasattr(Enum2, '__json__')
        
        # Test functionality
        assert Enum1.VALUE.__json__() == "one"
        assert Enum2.VALUE.__json__() == "two"
    
    def test_dumps_with_enums_shorthand(self):
        """Test dumps_with_enums convenience function"""
        data = {"severity": IssueSeverity.LOW}
        result = dumps_with_enums(data)
        parsed = json.loads(result)
        assert parsed["severity"] == "low"
    
    def test_safe_dumps_shorthand(self):
        """Test safe_dumps convenience function"""
        data = {"severity": IssueSeverity.CRITICAL}
        result = safe_dumps(data)
        parsed = json.loads(result)
        assert parsed["severity"] == "critical"


class TestRealWorldScenarios:
    """Test real-world usage scenarios"""
    
    def test_health_alert_serialization(self):
        """Test serializing health alert data with enums"""
        alert_data = {
            "module_name": "test_module",
            "severity": AlertSeverity.CRITICAL,
            "message": "Test alert",
            "metric_value": 0.5,
            "threshold_value": 0.8,
            "resolved": False
        }
        
        result = SerializationHandler.serialize_with_enums(alert_data)
        parsed = json.loads(result)
        
        assert parsed["severity"] == "critical"
        assert parsed["module_name"] == "test_module"
        assert parsed["metric_value"] == 0.5
    
    def test_compliance_issue_serialization(self):
        """Test serializing compliance issue data with enums"""
        issue_data = {
            "issue_type": ComplianceIssueType.ARCHITECTURAL_VIOLATION,
            "severity": IssueSeverity.HIGH,
            "description": "Test compliance issue",
            "affected_files": ["file1.py", "file2.py"],
            "blocking_merge": True
        }
        
        result = SerializationHandler.serialize_with_enums(issue_data)
        parsed = json.loads(result)
        
        assert parsed["issue_type"] == "architectural_violation"
        assert parsed["severity"] == "high"
        assert parsed["description"] == "Test compliance issue"
        assert parsed["affected_files"] == ["file1.py", "file2.py"]
        assert parsed["blocking_merge"] is True
    
    def test_mixed_enum_types_serialization(self):
        """Test serializing data with multiple enum types"""
        mixed_data = {
            "compliance": {
                "issue_type": ComplianceIssueType.RDI_VIOLATION,
                "severity": IssueSeverity.MEDIUM
            },
            "health": {
                "alert_severity": AlertSeverity.WARNING,
                "status": "degraded"
            },
            "test_data": {
                "enum_value": _TestEnum.VALUE_THREE,
                "string_value": "normal"
            }
        }
        
        result = SerializationHandler.serialize_with_enums(mixed_data)
        parsed = json.loads(result)
        
        assert parsed["compliance"]["issue_type"] == "rdi_violation"
        assert parsed["compliance"]["severity"] == "medium"
        assert parsed["health"]["alert_severity"] == "warning"
        assert parsed["test_data"]["enum_value"] == 42
        assert parsed["test_data"]["string_value"] == "normal"