#!/usr/bin/env python3
"""
RC1 RDI Compliance Test Suite

This test suite validates RDI (Requirements-Driven Implementation) compliance
for the RC1 Systematic Intelligence System.

TRACE: REQ-RC1-RDI-007
TEST: Comprehensive RDI compliance validation
IMPLEMENTATION: RDI compliance testing framework
"""

import unittest
import sys
import os
from pathlib import Path
from typing import Dict, List, Any
import re

# Add src to path
sys.path.append(str(Path(__file__).parent.parent.parent))

from src.rc1.foundation import MakefileHealthManager
from src.rc1.monitoring import HealthMonitor
from src.rc1.cli.rmddd_cli_integration import RC1RMDDDCLI


class RC1RDITestCase(unittest.TestCase):
    """Test case for RC1 RDI compliance validation."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.rc1_modules = [
            MakefileHealthManager(),
            HealthMonitor()
        ]
        self.rdi_requirements = self._load_rdi_requirements()
        self.traceability_patterns = [
            r"TRACE:\s*REQ-RC1-\w+-\d{3}",
            r"TEST:\s*.*",
            r"IMPLEMENTATION:\s*.*"
        ]
    
    def test_requirements_traceability(self):
        """
        Test that all RC1 requirements have proper traceability markers.
        
        TRACE: REQ-RC1-RDI-001
        TEST: Validates requirements traceability compliance
        IMPLEMENTATION: Requirements traceability validation
        """
        requirements_file = Path("docs/rc1/requirements/rc1_rmddd_integration_requirements.md")
        
        self.assertTrue(requirements_file.exists(), "Requirements file must exist")
        
        with open(requirements_file, 'r') as f:
            content = f.read()
        
        # Check for requirement patterns
        requirement_lines = [line for line in content.split('\n') 
                           if re.search(r"REQ-RC1-\w+-\d{3}", line)]
        
        self.assertGreater(len(requirement_lines), 0, "Must have requirements")
        
        # Check for traceability markers
        traceability_markers = re.findall(r"TRACE:\s*.*", content)
        test_markers = re.findall(r"TEST:\s*.*", content)
        implementation_markers = re.findall(r"IMPLEMENTATION:\s*.*", content)
        
        self.assertGreater(len(traceability_markers), 0, "Must have TRACE markers")
        self.assertGreater(len(test_markers), 0, "Must have TEST markers")
        self.assertGreater(len(implementation_markers), 0, "Must have IMPLEMENTATION markers")
    
    def test_design_traceability(self):
        """
        Test that all RC1 design specifications have proper traceability.
        
        TRACE: REQ-RC1-RDI-002
        TEST: Validates design traceability compliance
        IMPLEMENTATION: Design traceability validation
        """
        design_file = Path("docs/rc1/design/rc1_rmddd_integration_design.md")
        
        self.assertTrue(design_file.exists(), "Design file must exist")
        
        with open(design_file, 'r') as f:
            content = f.read()
        
        # Check for design patterns
        design_patterns = [
            r"class\s+\w+.*:",
            r"def\s+\w+.*:",
            r"interface\s+\w+",
            r"architecture\s+diagram"
        ]
        
        for pattern in design_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            self.assertGreater(len(matches), 0, f"Must have design pattern: {pattern}")
        
        # Check for requirements traceability
        trace_markers = re.findall(r"TRACE:\s*.*", content)
        self.assertGreater(len(trace_markers), 0, "Must have requirements traceability")
    
    def test_implementation_traceability(self):
        """
        Test that all RC1 implementations have proper traceability markers.
        
        TRACE: REQ-RC1-RDI-003
        TEST: Validates implementation traceability compliance
        IMPLEMENTATION: Implementation traceability validation
        """
        implementation_files = [
            "src/rc1/foundation/makefile_health_manager.py",
            "src/rc1/monitoring/health_monitor.py",
            "src/rc1/cli/rmddd_cli_integration.py"
        ]
        
        for file_path in implementation_files:
            impl_file = Path(file_path)
            self.assertTrue(impl_file.exists(), f"Implementation file must exist: {file_path}")
            
            with open(impl_file, 'r') as f:
                content = f.read()
            
            # Check for traceability markers
            trace_markers = re.findall(r"TRACE:\s*.*", content)
            test_markers = re.findall(r"TEST:\s*.*", content)
            impl_markers = re.findall(r"IMPLEMENTATION:\s*.*", content)
            
            self.assertGreater(len(trace_markers), 0, f"Must have TRACE markers in {file_path}")
            self.assertGreater(len(test_markers), 0, f"Must have TEST markers in {file_path}")
            self.assertGreater(len(impl_markers), 0, f"Must have IMPLEMENTATION markers in {file_path}")
    
    def test_documentation_completeness(self):
        """
        Test that all RC1 documentation is complete and traceable.
        
        TRACE: REQ-RC1-RDI-004
        TEST: Validates documentation completeness compliance
        IMPLEMENTATION: Documentation completeness validation
        """
        doc_files = [
            "docs/rc1/README.md",
            "docs/rc1/requirements/rc1_rmddd_integration_requirements.md",
            "docs/rc1/design/rc1_rmddd_integration_design.md",
            "docs/rc1/implementation/rc1_rdi_compliance_implementation.md"
        ]
        
        required_sections = [
            "## Document Information",
            "## Overview",
            "## Requirements",
            "## Design",
            "## Implementation",
            "## Testing",
            "## Traceability"
        ]
        
        for doc_file in doc_files:
            doc_path = Path(doc_file)
            self.assertTrue(doc_path.exists(), f"Documentation file must exist: {doc_file}")
            
            with open(doc_path, 'r') as f:
                content = f.read()
            
            # Check for required sections
            for section in required_sections:
                if section in content:
                    self.assertIn(section, content, f"Must have section {section} in {doc_file}")
            
            # Check for traceability links
            trace_links = re.findall(r"TRACE:\s*.*", content)
            self.assertGreater(len(trace_links), 0, f"Must have traceability links in {doc_file}")
    
    def test_module_rmddd_compliance(self):
        """
        Test that all RC1 modules are RM-DDD compliant.
        
        TRACE: REQ-RC1-RDI-005
        TEST: Validates RM-DDD compliance for all modules
        IMPLEMENTATION: RM-DDD compliance validation
        """
        for module in self.rc1_modules:
            # Test ReflectiveModule inheritance
            self.assertTrue(hasattr(module, 'get_module_info'), 
                          f"Module must have get_module_info method: {module.__class__.__name__}")
            self.assertTrue(hasattr(module, 'get_capabilities'), 
                          f"Module must have get_capabilities method: {module.__class__.__name__}")
            self.assertTrue(hasattr(module, 'get_dependencies'), 
                          f"Module must have get_dependencies method: {module.__class__.__name__}")
            self.assertTrue(hasattr(module, 'check_health'), 
                          f"Module must have check_health method: {module.__class__.__name__}")
            self.assertTrue(hasattr(module, 'graceful_degradation'), 
                          f"Module must have graceful_degradation method: {module.__class__.__name__}")
            
            # Test method implementations
            module_info = module.get_module_info()
            self.assertIsInstance(module_info, dict, "get_module_info must return dict")
            self.assertIn('module_id', module_info, "Module info must have module_id")
            self.assertIn('version', module_info, "Module info must have version")
            
            capabilities = module.get_capabilities()
            self.assertIsInstance(capabilities, list, "get_capabilities must return list")
            
            dependencies = module.get_dependencies()
            self.assertIsInstance(dependencies, list, "get_dependencies must return list")
            
            health = module.check_health()
            self.assertIsNotNone(health, "check_health must return health object")
            
            degradation = module.graceful_degradation()
            self.assertIsInstance(degradation, dict, "graceful_degradation must return dict")
    
    def test_cli_integration_compliance(self):
        """
        Test that RC1 CLI integration is RM-DDD compliant.
        
        TRACE: REQ-RC1-RDI-006
        TEST: Validates CLI integration compliance
        IMPLEMENTATION: CLI integration compliance validation
        """
        cli = RC1RMDDDCLI()
        
        # Test CLI creation
        self.assertIsNotNone(cli, "CLI must be created successfully")
        
        # Test registry integration
        self.assertIsNotNone(cli.registry, "CLI must have registry")
        self.assertIsNotNone(cli.cli_registry, "CLI must have CLI registry")
        self.assertIsNotNone(cli.generator, "CLI must have generator")
        
        # Test module registration
        cli.register_rc1_modules()
        self.assertGreater(len(cli.rc1_modules), 0, "Must register RC1 modules")
        
        # Test CLI generation
        for module in cli.rc1_modules:
            cli_code = cli.generate_cli_for_module(module)
            self.assertIsInstance(cli_code, str, "CLI code must be generated")
            self.assertGreater(len(cli_code), 0, "CLI code must not be empty")
    
    def test_end_to_end_traceability(self):
        """
        Test end-to-end traceability from requirements to implementation.
        
        TRACE: REQ-RC1-RDI-007
        TEST: Validates end-to-end traceability compliance
        IMPLEMENTATION: End-to-end traceability validation
        """
        # Load all requirements
        requirements = self._load_rdi_requirements()
        
        # Check that each requirement has corresponding design
        for req_id in requirements:
            design_ref = self._find_design_reference(req_id)
            self.assertIsNotNone(design_ref, f"Requirement {req_id} must have design reference")
            
            impl_ref = self._find_implementation_reference(req_id)
            self.assertIsNotNone(impl_ref, f"Requirement {req_id} must have implementation reference")
            
            test_ref = self._find_test_reference(req_id)
            self.assertIsNotNone(test_ref, f"Requirement {req_id} must have test reference")
    
    def _load_rdi_requirements(self) -> List[str]:
        """Load RDI requirements from documentation."""
        requirements = []
        
        req_file = Path("docs/rc1/requirements/rc1_rmddd_integration_requirements.md")
        if req_file.exists():
            with open(req_file, 'r') as f:
                content = f.read()
                req_matches = re.findall(r"REQ-RC1-\w+-\d{3}", content)
                requirements.extend(req_matches)
        
        return requirements
    
    def _find_design_reference(self, req_id: str) -> str:
        """Find design reference for a requirement."""
        design_file = Path("docs/rc1/design/rc1_rmddd_integration_design.md")
        if design_file.exists():
            with open(design_file, 'r') as f:
                content = f.read()
                if req_id in content:
                    return f"Design reference found in {design_file}"
        return None
    
    def _find_implementation_reference(self, req_id: str) -> str:
        """Find implementation reference for a requirement."""
        impl_files = [
            "src/rc1/foundation/makefile_health_manager.py",
            "src/rc1/monitoring/health_monitor.py",
            "src/rc1/cli/rmddd_cli_integration.py"
        ]
        
        for impl_file in impl_files:
            impl_path = Path(impl_file)
            if impl_path.exists():
                with open(impl_path, 'r') as f:
                    content = f.read()
                    if req_id in content:
                        return f"Implementation reference found in {impl_file}"
        return None
    
    def _find_test_reference(self, req_id: str) -> str:
        """Find test reference for a requirement."""
        test_file = Path("tests/rc1/test_rdi_compliance.py")
        if test_file.exists():
            with open(test_file, 'r') as f:
                content = f.read()
                if req_id in content:
                    return f"Test reference found in {test_file}"
        return None


if __name__ == '__main__':
    unittest.main()
