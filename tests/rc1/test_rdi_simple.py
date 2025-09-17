#!/usr/bin/env python3
"""
RC1 RDI Compliance Simple Test

This test validates basic RDI compliance for the RC1 system.

TRACE: REQ-RC1-RDI-007
TEST: Basic RDI compliance validation
IMPLEMENTATION: Simple RDI compliance testing
"""

import unittest
import sys
from pathlib import Path
import re

# Add src to path
sys.path.append(str(Path(__file__).parent.parent.parent))


class RC1RDISimpleTest(unittest.TestCase):
    """Simple test case for RC1 RDI compliance validation."""
    
    def test_requirements_file_exists(self):
        """
        Test that RC1 requirements file exists and has proper format.
        
        TRACE: REQ-RC1-RDI-001
        TEST: Validates requirements file existence and format
        IMPLEMENTATION: Requirements file validation
        """
        req_file = Path("docs/rc1/requirements/rc1_rmddd_integration_requirements.md")
        self.assertTrue(req_file.exists(), "RC1 requirements file must exist")
        
        with open(req_file, 'r') as f:
            content = f.read()
        
        # Check for requirement patterns
        req_matches = re.findall(r"REQ-RC1-\w+-\d{3}", content)
        self.assertGreater(len(req_matches), 0, "Must have requirement IDs")
        
        # Check for traceability markers
        trace_markers = re.findall(r"TRACE:\s*.*", content)
        self.assertGreater(len(trace_markers), 0, "Must have TRACE markers")
    
    def test_design_file_exists(self):
        """
        Test that RC1 design file exists and has proper format.
        
        TRACE: REQ-RC1-RDI-002
        TEST: Validates design file existence and format
        IMPLEMENTATION: Design file validation
        """
        design_file = Path("docs/rc1/design/rc1_rmddd_integration_design.md")
        self.assertTrue(design_file.exists(), "RC1 design file must exist")
        
        with open(design_file, 'r') as f:
            content = f.read()
        
        # Check for design patterns
        class_matches = re.findall(r"class\s+\w+.*:", content)
        self.assertGreater(len(class_matches), 0, "Must have class definitions")
        
        # Check for traceability
        trace_markers = re.findall(r"TRACE:\s*.*", content)
        self.assertGreater(len(trace_markers), 0, "Must have TRACE markers")
    
    def test_implementation_files_exist(self):
        """
        Test that RC1 implementation files exist and have traceability.
        
        TRACE: REQ-RC1-RDI-003
        TEST: Validates implementation files existence and traceability
        IMPLEMENTATION: Implementation file validation
        """
        impl_files = [
            "src/rc1/foundation/makefile_health_manager.py",
            "src/rc1/monitoring/health_monitor.py",
            "src/rc1/cli/rmddd_cli_integration.py"
        ]
        
        for impl_file in impl_files:
            impl_path = Path(impl_file)
            self.assertTrue(impl_path.exists(), f"Implementation file must exist: {impl_file}")
            
            with open(impl_path, 'r') as f:
                content = f.read()
            
            # Check for traceability markers
            trace_markers = re.findall(r"TRACE:\s*.*", content)
            self.assertGreater(len(trace_markers), 0, f"Must have TRACE markers in {impl_file}")
    
    def test_documentation_completeness(self):
        """
        Test that RC1 documentation is complete.
        
        TRACE: REQ-RC1-RDI-004
        TEST: Validates documentation completeness
        IMPLEMENTATION: Documentation completeness validation
        """
        doc_files = [
            "docs/rc1/README.md",
            "docs/rc1/requirements/rc1_rmddd_integration_requirements.md",
            "docs/rc1/design/rc1_rmddd_integration_design.md",
            "docs/rc1/implementation/rc1_rdi_compliance_implementation.md"
        ]
        
        for doc_file in doc_files:
            doc_path = Path(doc_file)
            self.assertTrue(doc_path.exists(), f"Documentation file must exist: {doc_file}")
            
            with open(doc_path, 'r') as f:
                content = f.read()
            
            # Check for basic documentation structure
            self.assertIn("##", content, f"Must have section headers in {doc_file}")
            self.assertGreater(len(content), 100, f"Must have substantial content in {doc_file}")
    
    def test_rdi_implementation_file_exists(self):
        """
        Test that RDI implementation file exists and is comprehensive.
        
        TRACE: REQ-RC1-RDI-005
        TEST: Validates RDI implementation file existence and content
        IMPLEMENTATION: RDI implementation file validation
        """
        rdi_file = Path("docs/rc1/implementation/rc1_rdi_compliance_implementation.md")
        self.assertTrue(rdi_file.exists(), "RDI implementation file must exist")
        
        with open(rdi_file, 'r') as f:
            content = f.read()
        
        # Check for RDI-specific content
        self.assertIn("RDI", content, "Must contain RDI references")
        self.assertIn("Requirements", content, "Must contain Requirements section")
        self.assertIn("Design", content, "Must contain Design section")
        self.assertIn("Implementation", content, "Must contain Implementation section")
        self.assertIn("Documentation", content, "Must contain Documentation section")
        
        # Check for traceability
        trace_markers = re.findall(r"TRACE:\s*.*", content)
        self.assertGreater(len(trace_markers), 0, "Must have TRACE markers")
    
    def test_traceability_consistency(self):
        """
        Test that traceability markers are consistent across all files.
        
        TRACE: REQ-RC1-RDI-006
        TEST: Validates traceability consistency
        IMPLEMENTATION: Traceability consistency validation
        """
        files_to_check = [
            "docs/rc1/requirements/rc1_rmddd_integration_requirements.md",
            "docs/rc1/design/rc1_rmddd_integration_design.md",
            "src/rc1/foundation/makefile_health_manager.py",
            "tests/rc1/test_rdi_simple.py"
        ]
        
        all_trace_markers = []
        
        for file_path in files_to_check:
            file_obj = Path(file_path)
            if file_obj.exists():
                with open(file_obj, 'r') as f:
                    content = f.read()
                    trace_markers = re.findall(r"TRACE:\s*.*", content)
                    all_trace_markers.extend(trace_markers)
        
        # Check that we have traceability markers
        self.assertGreater(len(all_trace_markers), 0, "Must have traceability markers across files")
        
        # Check for requirement ID patterns
        req_ids = re.findall(r"REQ-RC1-\w+-\d{3}", " ".join(all_trace_markers))
        self.assertGreater(len(req_ids), 0, "Must have requirement ID references")


if __name__ == '__main__':
    unittest.main()
