"""
Unit tests for RM (Reflective Module) architectural compliance validator.

Tests validation of RM interface implementation, size constraints,
health monitoring, and registry integration.
"""

import pytest
import tempfile
import os
from pathlib import Path
from unittest.mock import patch, mock_open

from src.beast_mode.compliance.rm.rm_validator import (
    RMValidator, RMInterfaceResult, SizeConstraintResult, 
    HealthMonitoringResult, RegistryIntegrationResult
)
from src.beast_mode.compliance.models import (
    ComplianceIssueType, IssueSeverity, RMComplianceStatus
)


class TestRMValidator:
    """Test suite for RMValidator class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.validator = RMValidator()
        self.temp_dir = tempfile.mkdtemp()
    
    def teardown_method(self):
        """Clean up test fixtures."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def _create_temp_module(self, content: str, filename: str = "test_module.py") -> str:
        """Create a temporary module file with given content."""
        module_path = os.path.join(self.temp_dir, filename)
        with open(module_path, 'w', encoding='utf-8') as f:
            f.write(content)
        return module_path


class TestRMInterfaceValidation:
    """Test RM interface validation functionality."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.validator = RMValidator()
        self.temp_dir = tempfile.mkdtemp()
    
    def teardown_method(self):
        """Clean up test fixtures."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def _create_temp_module(self, content: str, filename: str = "test_module.py") -> str:
        """Create a temporary module file with given content."""
        module_path = os.path.join(self.temp_dir, filename)
        with open(module_path, 'w', encoding='utf-8') as f:
            f.write(content)
        return module_path
    
    def test_valid_rm_implementation(self):
        """Test validation of a properly implemented RM class."""
        valid_rm_code = '''
from beast_mode.core.reflective_module import ReflectiveModule
from typing import Dict, Any

class TestRM(ReflectiveModule):
    def __init__(self):
        super().__init__("test_rm")
    
    def get_module_status(self) -> Dict[str, Any]:
        return {"status": "healthy", "module": "test_rm"}
    
    def is_healthy(self) -> bool:
        return True
    
    def get_health_indicators(self) -> Dict[str, Any]:
        return {"cpu_usage": 0.1, "memory_usage": 0.2}
    
    def _get_primary_responsibility(self) -> str:
        return "Test RM for validation"
'''
        
        module_path = self._create_temp_module(valid_rm_code)
        result = self.validator.validate_rm_interface_implementation(module_path)
        
        assert isinstance(result, RMInterfaceResult)
        assert result.implements_rm_interface is True
        assert len(result.missing_methods) == 0
        assert result.interface_compliance_score == 1.0
        assert len(result.issues) == 0
    
    def test_missing_required_methods(self):
        """Test validation when required RM methods are missing."""
        incomplete_rm_code = '''
from beast_mode.core.reflective_module import ReflectiveModule

class IncompleteRM(ReflectiveModule):
    def __init__(self):
        super().__init__("incomplete_rm")
    
    def get_module_status(self):
        return {"status": "incomplete"}
    
    # Missing: is_healthy, get_health_indicators, _get_primary_responsibility
'''
        
        module_path = self._create_temp_module(incomplete_rm_code)
        result = self.validator.validate_rm_interface_implementation(module_path)
        
        assert result.implements_rm_interface is False
        assert len(result.missing_methods) == 3
        assert "is_healthy" in result.missing_methods
        assert "get_health_indicators" in result.missing_methods
        assert "_get_primary_responsibility" in result.missing_methods
        assert result.interface_compliance_score == 0.25  # 1/4 methods implemented
        assert len(result.issues) == 3  # One issue per missing method
        
        # Check that all issues are critical and blocking
        for issue in result.issues:
            assert issue.issue_type == ComplianceIssueType.RM_NON_COMPLIANCE
            assert issue.severity == IssueSeverity.CRITICAL
            assert issue.blocking_merge is True
    
    def test_no_rm_class_found(self):
        """Test validation when no ReflectiveModule class is found."""
        non_rm_code = '''
class RegularClass:
    def __init__(self):
        self.name = "not_an_rm"
    
    def some_method(self):
        return "not an RM"
'''
        
        module_path = self._create_temp_module(non_rm_code)
        result = self.validator.validate_rm_interface_implementation(module_path)
        
        assert result.implements_rm_interface is False
        assert len(result.missing_methods) == len(self.validator.REQUIRED_RM_METHODS)
        assert result.interface_compliance_score == 0.0
        assert len(result.issues) == 1
        assert result.issues[0].description == "No ReflectiveModule classes found in module"
    
    def test_syntax_error_handling(self):
        """Test handling of modules with syntax errors."""
        invalid_code = '''
class InvalidRM(ReflectiveModule:  # Missing closing parenthesis
    def __init__(self):
        super().__init__("invalid")
    
    def get_module_status(self):
        return {"status": "invalid"
'''
        
        module_path = self._create_temp_module(invalid_code)
        result = self.validator.validate_rm_interface_implementation(module_path)
        
        assert result.implements_rm_interface is False
        assert result.interface_compliance_score == 0.0
        assert len(result.issues) == 1
        assert "Failed to validate RM interface" in result.issues[0].description
        assert result.issues[0].blocking_merge is True


class TestSizeConstraintValidation:
    """Test module size constraint validation."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.validator = RMValidator()
        self.temp_dir = tempfile.mkdtemp()
    
    def teardown_method(self):
        """Clean up test fixtures."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def _create_temp_module(self, content: str, filename: str = "test_module.py") -> str:
        """Create a temporary module file with given content."""
        module_path = os.path.join(self.temp_dir, filename)
        with open(module_path, 'w', encoding='utf-8') as f:
            f.write(content)
        return module_path
    
    def test_module_within_size_limit(self):
        """Test validation of module within 200 line limit."""
        small_module = '''
"""Small RM module for testing size constraints."""
from beast_mode.core.reflective_module import ReflectiveModule

class SmallRM(ReflectiveModule):
    def __init__(self):
        super().__init__("small_rm")
    
    def get_module_status(self):
        return {"status": "small"}
    
    def is_healthy(self):
        return True
'''
        
        module_path = self._create_temp_module(small_module)
        result = self.validator.check_size_constraints(module_path)
        
        assert isinstance(result, SizeConstraintResult)
        assert result.meets_size_constraint is True
        assert result.line_count <= 200
        # Should have no issues since it has docstring and meets all constraints
        assert len(result.issues) == 0
    
    def test_module_exceeds_size_limit(self):
        """Test validation of module exceeding 200 line limit."""
        # Create a module with more than 200 lines
        large_module_lines = [
            "from beast_mode.core.reflective_module import ReflectiveModule",
            "",
            "class LargeRM(ReflectiveModule):",
            "    def __init__(self):",
            "        super().__init__('large_rm')",
            ""
        ]
        
        # Add many methods to exceed line limit (need more lines)
        for i in range(80):
            large_module_lines.extend([
                f"    def method_{i}(self):",
                f"        result = 'method_{i}_result'",
                f"        additional_var = {i}",
                f"        return result",
                ""
            ])
        
        large_module = "\n".join(large_module_lines)
        module_path = self._create_temp_module(large_module)
        result = self.validator.check_size_constraints(module_path)
        
        assert result.meets_size_constraint is False
        assert result.line_count > 200
        assert len(result.issues) >= 1
        
        # Check for size constraint violation issue
        size_issues = [
            issue for issue in result.issues 
            if "exceeds size constraint" in issue.description
        ]
        assert len(size_issues) == 1
        assert size_issues[0].severity == IssueSeverity.HIGH
        assert size_issues[0].blocking_merge is True
    
    def test_single_responsibility_score_calculation(self):
        """Test single responsibility score calculation."""
        complex_module = '''
from beast_mode.core.reflective_module import ReflectiveModule
import os
import sys
import json
import yaml
import requests

class ComplexRM(ReflectiveModule):
    def __init__(self):
        super().__init__("complex_rm")
    
    def get_module_status(self):
        if True:
            if True:
                if True:
                    return {"nested": "deep"}
    
    def is_healthy(self):
        return True

class AnotherClass:
    pass

class ThirdClass:
    pass

class FourthClass:
    pass
'''
        
        module_path = self._create_temp_module(complex_module)
        result = self.validator.check_size_constraints(module_path)
        
        assert result.single_responsibility_score < 1.0
        assert 'class_count' in result.complexity_indicators
        assert 'function_count' in result.complexity_indicators
        assert 'max_nesting_depth' in result.complexity_indicators
        
        # Should have low responsibility score due to multiple classes
        if result.single_responsibility_score < 0.7:
            responsibility_issues = [
                issue for issue in result.issues 
                if "single responsibility score" in issue.description
            ]
            assert len(responsibility_issues) == 1
    
    def test_architectural_pattern_violations(self):
        """Test detection of various architectural pattern violations."""
        # Create a module with multiple architectural violations
        violation_module = '''
"""Module with architectural violations for testing."""
import os
import sys
import json
import yaml
import requests
import numpy
import pandas
import matplotlib
import seaborn
import sklearn
import tensorflow
import torch
import flask
import django
import fastapi
import sqlalchemy
import redis
import mongodb
import elasticsearch
import kafka
import rabbitmq

class FirstClass:
    def method1(self): pass
    def method2(self): pass
    def method3(self): pass
    def method4(self): pass
    def method5(self): pass

class SecondClass:
    def method1(self): pass
    def method2(self): pass
    def method3(self): pass
    def method4(self): pass
    def method5(self): pass

class ThirdClass:
    def method1(self): pass
    def method2(self): pass
    def method3(self): pass
    def method4(self): pass
    def method5(self): pass

class FourthClass:
    def method1(self): pass
    def method2(self): pass
    def method3(self): pass
    def method4(self): pass
    def method5(self): pass

class FifthClass:
    def method1(self): pass
    def method2(self): pass
    def method3(self): pass
    def method4(self): pass
    def method5(self): pass

class SixthClass:
    def deeply_nested_method(self):
        if True:
            if True:
                if True:
                    if True:
                        if True:
                            return "too deep"
'''
        
        module_path = self._create_temp_module(violation_module)
        result = self.validator.check_size_constraints(module_path)
        
        # Should detect multiple architectural violations
        architectural_issues = [
            issue for issue in result.issues 
            if issue.issue_type.value == "architectural_violation"
        ]
        
        # Should have issues for:
        # - Too many classes (6 > 5)
        # - Too many imports (>20)
        # - Deep nesting (5 levels > 4)
        assert len(architectural_issues) >= 3
        
        # Check specific violation types
        class_violation = any("Too many classes" in issue.description for issue in architectural_issues)
        import_violation = any("Too many imports" in issue.description for issue in architectural_issues)
        nesting_violation = any("Deep nesting" in issue.description for issue in architectural_issues)
        
        assert class_violation, "Should detect too many classes violation"
        assert import_violation, "Should detect too many imports violation"
        assert nesting_violation, "Should detect deep nesting violation"
    
    def test_god_class_detection(self):
        """Test detection of god class pattern (too many methods)."""
        # Create a class with too many methods
        god_class_lines = [
            "from beast_mode.core.reflective_module import ReflectiveModule",
            "",
            "class GodClass(ReflectiveModule):",
            "    def __init__(self):",
            "        super().__init__('god_class')",
            ""
        ]
        
        # Add many methods to create a god class
        for i in range(30):  # More than 25 methods
            god_class_lines.extend([
                f"    def method_{i}(self):",
                f"        return 'method_{i}_result'",
                ""
            ])
        
        god_class_module = "\n".join(god_class_lines)
        module_path = self._create_temp_module(god_class_module)
        result = self.validator.check_size_constraints(module_path)
        
        # Should detect god class pattern
        god_class_issues = [
            issue for issue in result.issues 
            if "Too many methods" in issue.description
        ]
        assert len(god_class_issues) == 1
        assert god_class_issues[0].severity.value == "high"
    
    def test_missing_docstring_detection(self):
        """Test detection of missing module docstrings."""
        no_docstring_module = '''
from beast_mode.core.reflective_module import ReflectiveModule

class NoDocstringRM(ReflectiveModule):
    def __init__(self):
        super().__init__("no_docstring")
    
    def some_method(self):
        return "no documentation"
'''
        
        module_path = self._create_temp_module(no_docstring_module)
        result = self.validator.check_size_constraints(module_path)
        
        # Should detect missing docstring
        docstring_issues = [
            issue for issue in result.issues 
            if "docstring" in issue.description
        ]
        assert len(docstring_issues) == 1
        assert docstring_issues[0].severity.value == "low"


class TestHealthMonitoringValidation:
    """Test health monitoring validation functionality."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.validator = RMValidator()
        self.temp_dir = tempfile.mkdtemp()
    
    def teardown_method(self):
        """Clean up test fixtures."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def _create_temp_module(self, content: str, filename: str = "test_module.py") -> str:
        """Create a temporary module file with given content."""
        module_path = os.path.join(self.temp_dir, filename)
        with open(module_path, 'w', encoding='utf-8') as f:
            f.write(content)
        return module_path
    
    def test_complete_health_monitoring(self):
        """Test validation of complete health monitoring implementation."""
        health_monitoring_code = '''
from beast_mode.core.reflective_module import ReflectiveModule

class HealthyRM(ReflectiveModule):
    def __init__(self):
        super().__init__("healthy_rm")
        self._health_indicators = {}
    
    def is_healthy(self):
        return True
    
    def get_health_indicators(self):
        return self._health_indicators
    
    def _update_health_indicator(self, name, status, value, message):
        self._health_indicators[name] = {
            "status": status,
            "value": value,
            "message": message
        }
'''
        
        module_path = self._create_temp_module(health_monitoring_code)
        result = self.validator.validate_health_monitoring(module_path)
        
        assert isinstance(result, HealthMonitoringResult)
        assert result.has_health_monitoring is True
        assert "is_healthy" in result.health_methods_implemented
        assert "get_health_indicators" in result.health_methods_implemented
        assert "_update_health_indicator" in result.health_methods_implemented
        assert len(result.missing_health_methods) == 0
        assert result.health_monitoring_score == 1.0
        assert len(result.issues) == 0
    
    def test_missing_critical_health_methods(self):
        """Test validation when critical health methods are missing."""
        incomplete_health_code = '''
from beast_mode.core.reflective_module import ReflectiveModule

class UnhealthyRM(ReflectiveModule):
    def __init__(self):
        super().__init__("unhealthy_rm")
    
    def some_other_method(self):
        return "not health related"
'''
        
        module_path = self._create_temp_module(incomplete_health_code)
        result = self.validator.validate_health_monitoring(module_path)
        
        assert result.has_health_monitoring is False
        assert len(result.health_methods_implemented) == 0
        assert "is_healthy" in result.missing_health_methods
        assert "get_health_indicators" in result.missing_health_methods
        assert result.health_monitoring_score == 0.0
        
        # Should have critical issues for missing health methods
        critical_issues = [
            issue for issue in result.issues 
            if issue.severity == IssueSeverity.CRITICAL
        ]
        assert len(critical_issues) == 2  # is_healthy and get_health_indicators
    
    def test_missing_health_indicators(self):
        """Test validation when health indicators are not used."""
        no_indicators_code = '''
from beast_mode.core.reflective_module import ReflectiveModule

class NoIndicatorsRM(ReflectiveModule):
    def __init__(self):
        super().__init__("no_indicators_rm")
    
    def is_healthy(self):
        return True
    
    def get_health_indicators(self):
        return {}
'''
        
        module_path = self._create_temp_module(no_indicators_code)
        result = self.validator.validate_health_monitoring(module_path)
        
        # Should have issue about missing health indicators
        indicator_issues = [
            issue for issue in result.issues 
            if "health indicators" in issue.description
        ]
        assert len(indicator_issues) == 1
        assert indicator_issues[0].severity == IssueSeverity.MEDIUM


class TestRegistryIntegrationValidation:
    """Test registry integration validation functionality."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.validator = RMValidator()
        self.temp_dir = tempfile.mkdtemp()
    
    def teardown_method(self):
        """Clean up test fixtures."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def _create_temp_module(self, content: str, filename: str = "test_module.py") -> str:
        """Create a temporary module file with given content."""
        module_path = os.path.join(self.temp_dir, filename)
        with open(module_path, 'w', encoding='utf-8') as f:
            f.write(content)
        return module_path
    
    def test_proper_registry_integration(self):
        """Test validation of proper registry integration."""
        registry_integrated_code = '''
from beast_mode.core.reflective_module import ReflectiveModule
from beast_mode.documentation.document_management_rm import DocumentManagementRM

class RegisteredRM(ReflectiveModule):
    def __init__(self):
        super().__init__("registered_rm")
        self.register_with_registry()
    
    def register_rm_documentation(self, documents):
        doc_manager = DocumentManagementRM()
        return doc_manager.register_rm_documentation(self.module_name, documents)
    
    def register_with_registry(self):
        self.register_rm_documentation([])
'''
        
        module_path = self._create_temp_module(registry_integrated_code)
        result = self.validator.check_registry_integration(module_path)
        
        assert isinstance(result, RegistryIntegrationResult)
        assert result.properly_registered is True
        assert result.registration_method_present is True
        assert result.registry_compliance_score == 1.0
        assert len(result.issues) == 0
    
    def test_missing_registration_method(self):
        """Test validation when registration method is missing."""
        no_registration_code = '''
from beast_mode.core.reflective_module import ReflectiveModule

class UnregisteredRM(ReflectiveModule):
    def __init__(self):
        super().__init__("unregistered_rm")
    
    def some_method(self):
        return "no registration"
'''
        
        module_path = self._create_temp_module(no_registration_code)
        result = self.validator.check_registry_integration(module_path)
        
        assert result.properly_registered is False
        assert result.registration_method_present is False
        assert result.registry_compliance_score < 1.0
        
        # Should have issue about missing registration method
        registration_issues = [
            issue for issue in result.issues 
            if "registration method" in issue.description
        ]
        assert len(registration_issues) == 1
        assert registration_issues[0].severity == IssueSeverity.MEDIUM
    
    def test_missing_registry_imports(self):
        """Test validation when registry imports are missing."""
        no_imports_code = '''
from beast_mode.core.reflective_module import ReflectiveModule

class NoImportsRM(ReflectiveModule):
    def __init__(self):
        super().__init__("no_imports_rm")
    
    def register_rm_documentation(self, documents):
        # Has method but no proper imports
        return {"registered": False}
'''
        
        module_path = self._create_temp_module(no_imports_code)
        result = self.validator.check_registry_integration(module_path)
        
        assert result.properly_registered is False
        assert result.registration_method_present is True
        
        # Should have issue about missing imports
        import_issues = [
            issue for issue in result.issues 
            if "imports" in issue.description
        ]
        assert len(import_issues) == 1
        assert import_issues[0].severity == IssueSeverity.LOW


class TestComprehensiveRMValidation:
    """Test comprehensive RM compliance validation."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.validator = RMValidator()
        self.temp_dir = tempfile.mkdtemp()
    
    def teardown_method(self):
        """Clean up test fixtures."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def _create_temp_module(self, content: str, filename: str = "test_module.py") -> str:
        """Create a temporary module file with given content."""
        module_path = os.path.join(self.temp_dir, filename)
        with open(module_path, 'w', encoding='utf-8') as f:
            f.write(content)
        return module_path
    
    def test_fully_compliant_rm(self):
        """Test validation of fully compliant RM implementation."""
        compliant_rm_code = '''
from beast_mode.core.reflective_module import ReflectiveModule
from beast_mode.documentation.document_management_rm import DocumentManagementRM
from typing import Dict, Any

class CompliantRM(ReflectiveModule):
    def __init__(self):
        super().__init__("compliant_rm")
        self._health_indicators = {}
        self.register_rm_documentation([])
    
    def get_module_status(self) -> Dict[str, Any]:
        return {
            "status": "healthy",
            "module": self.module_name,
            "compliance": "full"
        }
    
    def is_healthy(self) -> bool:
        return len(self._health_indicators) == 0 or all(
            indicator.status == "healthy" 
            for indicator in self._health_indicators.values()
        )
    
    def get_health_indicators(self) -> Dict[str, Any]:
        return {
            name: {
                "status": indicator.status,
                "value": indicator.value,
                "message": indicator.message
            }
            for name, indicator in self._health_indicators.items()
        }
    
    def _get_primary_responsibility(self) -> str:
        return "Demonstrate full RM compliance for validation testing"
    
    def register_rm_documentation(self, documents):
        doc_manager = DocumentManagementRM()
        return doc_manager.register_rm_documentation(self.module_name, documents)
    
    def _update_health_indicator(self, name, status, value, message):
        from beast_mode.core.reflective_module import HealthIndicator
        self._health_indicators[name] = HealthIndicator(
            name=name,
            status=status,
            value=value,
            message=message,
            timestamp=0.0
        )
'''
        
        module_path = self._create_temp_module(compliant_rm_code)
        result = self.validator.validate_rm_compliance(module_path)
        
        assert isinstance(result, RMComplianceStatus)
        assert result.interface_implemented is True
        assert result.size_constraints_met is True
        assert result.health_monitoring_present is True
        assert result.registry_integrated is True
        assert result.compliance_score >= 0.9  # Should be very high
        
        # Should have minimal or no issues
        critical_issues = [
            issue for issue in result.issues 
            if issue.severity == IssueSeverity.CRITICAL
        ]
        assert len(critical_issues) == 0
    
    def test_non_compliant_rm(self):
        """Test validation of non-compliant RM implementation."""
        # Create a large non-compliant module
        non_compliant_lines = [
            "# This is not even a proper RM class",
            "class BadClass:",
            "    def __init__(self):",
            "        self.name = 'bad'",
            "",
            "    def bad_method(self):",
            "        return 'very bad'",
            ""
        ]
        
        # Add many lines to exceed size limit
        for i in range(60):
            non_compliant_lines.extend([
                f"    def bad_method_{i}(self):",
                f"        result = 'bad_method_{i}_result'",
                f"        value = {i}",
                f"        return result + str(value)",
                ""
            ])
        
        non_compliant_code = '\n'.join(non_compliant_lines)
        
        module_path = self._create_temp_module(non_compliant_code)
        result = self.validator.validate_rm_compliance(module_path)
        
        assert result.interface_implemented is False
        assert result.size_constraints_met is False
        assert result.health_monitoring_present is False
        assert result.registry_integrated is False
        assert result.compliance_score == 0.0
        
        # Should have multiple critical issues
        assert len(result.issues) > 0
        critical_issues = [
            issue for issue in result.issues 
            if issue.severity == IssueSeverity.CRITICAL
        ]
        assert len(critical_issues) > 0


if __name__ == "__main__":
    pytest.main([__file__])