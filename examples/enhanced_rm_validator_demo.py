#!/usr/bin/env python3
"""
Enhanced RM Validator Demo

Demonstrates the enhanced size constraint and architectural validation
capabilities of the RM validator, including detection of various
architectural violations and patterns.
"""

import tempfile
import os
from pathlib import Path

from src.beast_mode.compliance.rm.rm_validator import RMValidator


def create_demo_modules():
    """Create demo modules with various architectural patterns."""
    temp_dir = tempfile.mkdtemp()
    
    # Good module - follows all architectural principles
    good_module = '''
"""
Well-designed RM module demonstrating good architectural practices.

This module follows single responsibility principle, has proper documentation,
and maintains reasonable complexity levels.
"""
from beast_mode.core.reflective_module import ReflectiveModule
from typing import Dict, Any


class WellDesignedRM(ReflectiveModule):
    """A well-designed RM that follows all architectural principles."""
    
    def __init__(self):
        super().__init__("well_designed_rm")
        self._health_indicators = {}
    
    def get_module_status(self) -> Dict[str, Any]:
        """Get the current status of this module."""
        return {
            "status": "healthy",
            "module": self.module_name,
            "responsibility": self._get_primary_responsibility()
        }
    
    def is_healthy(self) -> bool:
        """Check if the module is healthy."""
        return all(
            indicator.status == "healthy" 
            for indicator in self._health_indicators.values()
        )
    
    def get_health_indicators(self) -> Dict[str, Any]:
        """Get detailed health indicators."""
        return {
            name: {
                "status": indicator.status,
                "value": indicator.value,
                "message": indicator.message
            }
            for name, indicator in self._health_indicators.items()
        }
    
    def _get_primary_responsibility(self) -> str:
        """Get the primary responsibility of this module."""
        return "Demonstrate good architectural practices in RM design"
'''
    
    # Bad module - violates multiple architectural principles
    bad_module_lines = [
        "# Bad module with no docstring and many violations",
        "import os",
        "import sys", 
        "import json",
        "import yaml",
        "import requests",
        "import numpy",
        "import pandas",
        "import matplotlib",
        "import seaborn",
        "import sklearn",
        "import tensorflow",
        "import torch",
        "import flask",
        "import django",
        "import fastapi",
        "import sqlalchemy",
        "import redis",
        "import mongodb",
        "import elasticsearch",
        "import kafka",
        "import rabbitmq",
        "",
        "class FirstClass:",
        "    def __init__(self): pass",
    ]
    
    # Add many methods to create god class
    for i in range(30):
        bad_module_lines.extend([
            f"    def method_{i}(self):",
            f"        if True:",
            f"            if True:",
            f"                if True:",
            f"                    if True:",
            f"                        if True:",
            f"                            return 'method_{i}_deeply_nested'",
            ""
        ])
    
    # Add more classes to violate class count
    for class_num in range(2, 8):
        bad_module_lines.extend([
            f"class Class{class_num}:",
            f"    def method(self): pass",
            ""
        ])
    
    bad_module = "\n".join(bad_module_lines)
    
    # Write modules to temp files
    good_path = os.path.join(temp_dir, "good_module.py")
    bad_path = os.path.join(temp_dir, "bad_module.py")
    
    with open(good_path, 'w') as f:
        f.write(good_module)
    
    with open(bad_path, 'w') as f:
        f.write(bad_module)
    
    return temp_dir, good_path, bad_path


def demonstrate_architectural_validation():
    """Demonstrate the enhanced architectural validation capabilities."""
    print("🏗️  Enhanced RM Architectural Validation Demo")
    print("=" * 60)
    
    validator = RMValidator()
    temp_dir, good_path, bad_path = create_demo_modules()
    
    try:
        # Test good module
        print("\n✅ Testing Well-Designed Module:")
        print(f"   File: {Path(good_path).name}")
        
        good_result = validator.check_size_constraints(good_path)
        
        print(f"   📏 Line count: {good_result.line_count}")
        print(f"   📐 Size constraint met: {good_result.meets_size_constraint}")
        print(f"   🎯 Single responsibility score: {good_result.single_responsibility_score:.2f}")
        print(f"   🔍 Issues found: {len(good_result.issues)}")
        
        if good_result.issues:
            for issue in good_result.issues:
                print(f"      - {issue.severity.value.upper()}: {issue.description}")
        
        # Test bad module
        print("\n❌ Testing Poorly-Designed Module:")
        print(f"   File: {Path(bad_path).name}")
        
        bad_result = validator.check_size_constraints(bad_path)
        
        print(f"   📏 Line count: {bad_result.line_count}")
        print(f"   📐 Size constraint met: {bad_result.meets_size_constraint}")
        print(f"   🎯 Single responsibility score: {bad_result.single_responsibility_score:.2f}")
        print(f"   🔍 Issues found: {len(bad_result.issues)}")
        
        print("\n   🚨 Architectural Violations Detected:")
        for issue in bad_result.issues:
            print(f"      - {issue.severity.value.upper()}: {issue.description}")
            if issue.remediation_steps:
                print(f"        💡 Remediation: {issue.remediation_steps[0]}")
        
        # Show complexity analysis
        print(f"\n   📊 Complexity Analysis:")
        complexity = bad_result.complexity_indicators
        print(f"      - Classes: {complexity.get('class_count', 0)}")
        print(f"      - Functions: {complexity.get('function_count', 0)}")
        print(f"      - Imports: {complexity.get('import_count', 0)}")
        print(f"      - Max nesting depth: {complexity.get('max_nesting_depth', 0)}")
        print(f"      - Complexity score: {complexity.get('complexity_score', 0):.2f}")
        
        # Demonstrate comprehensive RM validation
        print("\n🔍 Comprehensive RM Validation:")
        comprehensive_result = validator.validate_rm_compliance(bad_path)
        
        print(f"   📋 Overall compliance score: {comprehensive_result.compliance_score:.2f}")
        print(f"   🔌 Interface implemented: {comprehensive_result.interface_implemented}")
        print(f"   📏 Size constraints met: {comprehensive_result.size_constraints_met}")
        print(f"   💓 Health monitoring present: {comprehensive_result.health_monitoring_present}")
        print(f"   📝 Registry integrated: {comprehensive_result.registry_integrated}")
        
        critical_issues = [
            issue for issue in comprehensive_result.issues 
            if issue.severity.value == "critical"
        ]
        print(f"   🚨 Critical issues: {len(critical_issues)}")
        
        print("\n✨ Enhanced Architectural Validation Features:")
        print("   - Size constraint validation (≤200 lines)")
        print("   - Single responsibility principle checking")
        print("   - God class pattern detection")
        print("   - Excessive coupling detection (imports)")
        print("   - Deep nesting analysis")
        print("   - Documentation compliance checking")
        print("   - Comprehensive remediation guidance")
        
    finally:
        # Cleanup
        import shutil
        shutil.rmtree(temp_dir, ignore_errors=True)


if __name__ == "__main__":
    demonstrate_architectural_validation()