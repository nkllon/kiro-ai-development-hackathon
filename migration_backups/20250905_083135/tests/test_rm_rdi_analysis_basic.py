"""
Basic validation tests for RM-RDI Analysis System

These tests validate the core framework without external dependencies
"""

import unittest
import os
from pathlib import Path


class TestAnalysisSystemBasic(unittest.TestCase):
    """Basic tests for analysis system structure and safety"""
    
    def test_analysis_system_structure_exists(self):
        """Test that analysis system directory structure exists"""
        base_path = Path("src/beast_mode/analysis/rm_rdi")
        self.assertTrue(base_path.exists(), "Analysis system directory must exist")
        
        # Check core files exist
        core_files = [
            "__init__.py",
            "data_models.py", 
            "safety.py",
            "base.py"
        ]
        
        for file_name in core_files:
            file_path = base_path / file_name
            self.assertTrue(file_path.exists(), f"Core file {file_name} must exist")
            
    def test_operator_control_script_exists(self):
        """Test that operator control script exists and is executable"""
        script_path = Path("scripts/analysis_control.py")
        self.assertTrue(script_path.exists(), "Operator control script must exist")
        self.assertTrue(os.access(script_path, os.X_OK), "Control script must be executable")
        
    def test_makefile_integration_exists(self):
        """Test that Makefile integration exists"""
        makefile_path = Path("makefiles/analysis.mk")
        self.assertTrue(makefile_path.exists(), "Analysis Makefile must exist")
        
        # Check for emergency commands in Makefile
        content = makefile_path.read_text()
        emergency_commands = [
            "analysis-kill:",
            "analysis-throttle:",
            "analysis-stop:",
            "analysis-uninstall:",
            "analysis-status:"
        ]
        
        for command in emergency_commands:
            self.assertIn(command, content, f"Emergency command {command} must exist in Makefile")
            
    def test_safety_guarantees_documented(self):
        """Test that safety guarantees are properly documented"""
        init_path = Path("src/beast_mode/analysis/rm_rdi/__init__.py")
        content = init_path.read_text()
        
        safety_guarantees = [
            "READ_ONLY_OPERATIONS",
            "ISOLATED_PROCESSES",
            "RESOURCE_LIMITED", 
            "KILL_SWITCH_ENABLED",
            "ZERO_DOWNTIME_RISK"
        ]
        
        for guarantee in safety_guarantees:
            self.assertIn(guarantee, content, f"Safety guarantee {guarantee} must be documented")
            
    def test_data_models_are_immutable(self):
        """Test that data models use frozen dataclasses for safety"""
        models_path = Path("src/beast_mode/analysis/rm_rdi/data_models.py")
        content = models_path.read_text()
        
        # Check that dataclasses are frozen
        self.assertIn("@dataclass(frozen=True)", content, "Data models must be immutable")
        
    def test_safety_module_structure(self):
        """Test that safety module has required components"""
        safety_path = Path("src/beast_mode/analysis/rm_rdi/safety.py")
        content = safety_path.read_text()
        
        required_classes = [
            "class KillSwitch:",
            "class ResourceMonitor:",
            "class SafetyValidator:",
            "class OperatorSafetyManager:"
        ]
        
        for class_def in required_classes:
            self.assertIn(class_def, content, f"Safety class {class_def} must exist")
            
    def test_base_analyzer_safety_features(self):
        """Test that base analyzer has safety features"""
        base_path = Path("src/beast_mode/analysis/rm_rdi/base.py")
        content = base_path.read_text()
        
        safety_features = [
            "class SafetyViolationError",
            "def emergency_shutdown",
            "def validate_read_only_access",
            "READ-ONLY"
        ]
        
        for feature in safety_features:
            self.assertIn(feature, content, f"Safety feature {feature} must exist")


class TestOperatorSafetyDocumentation(unittest.TestCase):
    """Test that operator safety documentation is complete"""
    
    def test_operator_safety_guide_exists(self):
        """Test that operator safety guide exists"""
        guide_path = Path(".kiro/specs/rm-rdi-analysis-system/operator-safety.md")
        self.assertTrue(guide_path.exists(), "Operator safety guide must exist")
        
        content = guide_path.read_text()
        
        # Check for emergency commands
        emergency_commands = [
            "make analysis-kill",
            "make analysis-throttle", 
            "make analysis-stop",
            "make analysis-uninstall"
        ]
        
        for command in emergency_commands:
            self.assertIn(command, content, f"Emergency command {command} must be documented")
            
    def test_pdca_plan_includes_safety(self):
        """Test that PDCA plan includes operator safety considerations"""
        pdca_path = Path(".kiro/specs/rm-rdi-analysis-system/pdca-plan.md")
        self.assertTrue(pdca_path.exists(), "PDCA plan must exist")
        
        content = pdca_path.read_text()
        
        safety_topics = [
            "Operational Safety Assessment",
            "ZERO DOWNTIME RISK", 
            "Emergency Procedures",
            "Rollback"
        ]
        
        for topic in safety_topics:
            self.assertIn(topic, content, f"Safety topic {topic} must be in PDCA plan")


if __name__ == "__main__":
    unittest.main()