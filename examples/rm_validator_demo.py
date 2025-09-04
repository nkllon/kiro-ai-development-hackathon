#!/usr/bin/env python3
"""
Demo script showing RM (Reflective Module) architectural compliance validation.

This script demonstrates how to use the RMValidator to check compliance
with Beast Mode Framework RM standards.
"""

import tempfile
import os
from pathlib import Path

from src.beast_mode.compliance.rm.rm_validator import RMValidator


def create_sample_rm_module(compliant: bool = True) -> str:
    """Create a sample RM module for testing."""
    if compliant:
        content = '''
from beast_mode.core.reflective_module import ReflectiveModule
from beast_mode.documentation.document_management_rm import DocumentManagementRM
from typing import Dict, Any

class SampleRM(ReflectiveModule):
    """A compliant RM implementation for demonstration."""
    
    def __init__(self):
        super().__init__("sample_rm")
        self._health_indicators = {}
        self.register_rm_documentation([])
    
    def get_module_status(self) -> Dict[str, Any]:
        return {
            "status": "healthy",
            "module": self.module_name,
            "compliance": "full"
        }
    
    def is_healthy(self) -> bool:
        return True
    
    def get_health_indicators(self) -> Dict[str, Any]:
        return self._health_indicators
    
    def _get_primary_responsibility(self) -> str:
        return "Demonstrate RM compliance validation"
    
    def register_rm_documentation(self, documents):
        doc_manager = DocumentManagementRM()
        return doc_manager.register_rm_documentation(self.module_name, documents)
    
    def _update_health_indicator(self, name, status, value, message):
        self._health_indicators[name] = {
            "status": status,
            "value": value,
            "message": message
        }
'''
    else:
        # Create a non-compliant module
        content = '''
class BadModule:
    """A non-compliant module that doesn't follow RM standards."""
    
    def __init__(self):
        self.name = "bad_module"
    
    def some_method(self):
        return "not compliant"
'''
        # Add many lines to exceed size limit
        for i in range(60):
            content += f'''
    def method_{i}(self):
        result = "method_{i}_result"
        value = {i}
        return result + str(value)
'''
    
    return content


def demo_rm_validation():
    """Demonstrate RM validation capabilities."""
    print("🔍 Beast Mode RM Architectural Compliance Validator Demo")
    print("=" * 60)
    
    validator = RMValidator()
    
    # Test compliant RM
    print("\n✅ Testing Compliant RM Module:")
    print("-" * 40)
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
        f.write(create_sample_rm_module(compliant=True))
        compliant_path = f.name
    
    try:
        result = validator.validate_rm_compliance(compliant_path)
        
        print(f"Interface Implemented: {result.interface_implemented}")
        print(f"Size Constraints Met: {result.size_constraints_met}")
        print(f"Health Monitoring Present: {result.health_monitoring_present}")
        print(f"Registry Integrated: {result.registry_integrated}")
        print(f"Overall Compliance Score: {result.compliance_score:.2f}")
        print(f"Issues Found: {len(result.issues)}")
        
        if result.issues:
            print("\nIssues:")
            for issue in result.issues:
                print(f"  - {issue.severity.value.upper()}: {issue.description}")
    
    finally:
        os.unlink(compliant_path)
    
    # Test non-compliant RM
    print("\n❌ Testing Non-Compliant Module:")
    print("-" * 40)
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
        f.write(create_sample_rm_module(compliant=False))
        non_compliant_path = f.name
    
    try:
        result = validator.validate_rm_compliance(non_compliant_path)
        
        print(f"Interface Implemented: {result.interface_implemented}")
        print(f"Size Constraints Met: {result.size_constraints_met}")
        print(f"Health Monitoring Present: {result.health_monitoring_present}")
        print(f"Registry Integrated: {result.registry_integrated}")
        print(f"Overall Compliance Score: {result.compliance_score:.2f}")
        print(f"Issues Found: {len(result.issues)}")
        
        if result.issues:
            print("\nCritical Issues:")
            critical_issues = [i for i in result.issues if i.severity.value == 'critical']
            for issue in critical_issues[:3]:  # Show first 3 critical issues
                print(f"  - {issue.severity.value.upper()}: {issue.description}")
                print(f"    Remediation: {issue.remediation_steps[0] if issue.remediation_steps else 'N/A'}")
    
    finally:
        os.unlink(non_compliant_path)
    
    print("\n🎯 RM Validation Demo Complete!")
    print("\nThe RMValidator ensures all Beast Mode components follow:")
    print("  • ReflectiveModule interface compliance")
    print("  • Size constraints (≤200 lines)")
    print("  • Health monitoring implementation")
    print("  • Registry integration")


if __name__ == "__main__":
    demo_rm_validation()