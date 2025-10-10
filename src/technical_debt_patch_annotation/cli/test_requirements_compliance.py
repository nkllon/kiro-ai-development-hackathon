#!/usr/bin/env python3
"""
Requirements Compliance Test: Technical Debt Patch Annotation CLI

This test validates that the CLI interface meets all specified requirements
for integration with development workflow.

Requirements Coverage:
- 6.1: Code review integration with debt impact assessment
- 6.2: CI/CD pipeline integration with threshold checking
- 6.3: Automated checks preventing merge without proper annotation
- 6.4: Automatic validation of cleanup completion
- 6.5: Technical debt report generation from current codebase state
"""

import unittest
import tempfile
import os
import json
import sys
from pathlib import Path
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, MagicMock

# Add project root to path for imports
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from src.technical_debt_patch_annotation.cli.patch_cli import PatchCLI
from src.technical_debt_patch_annotation.core.models import PatchAnnotation, DebtLevel, BypassType


class TestCLIRequirementsCompliance(unittest.TestCase):
    """Test CLI compliance with integration requirements."""
    
    def setUp(self):
        """Set up test environment."""
        self.cli = PatchCLI()
        self.temp_dir = Path(tempfile.mkdtemp(prefix="cli_test_"))
        self.original_cwd = os.getcwd()
        os.chdir(self.temp_dir)
        
        # Create sample patch annotations
        self.sample_patches = [
            PatchAnnotation(
                patch_id="TEST-001",
                reason="Test patch for validation",
                upstream_issue="ISSUE-001",
                cleanup_task="Remove test patch",
                debt_level=DebtLevel.HIGH,
                created_date=datetime.now(),
                expected_resolution=datetime.now() + timedelta(days=7),
                component="test_component",
                bypass_type=BypassType.ARCHITECTURE,
                file_path="test.py",
                line_start=10,
                line_end=15,
                validation_criteria=["Test passes", "Code review approved"]
            ),
            PatchAnnotation(
                patch_id="TEST-002",
                reason="Critical security patch",
                upstream_issue="SECURITY-001",
                cleanup_task="Implement proper security",
                debt_level=DebtLevel.CRITICAL,
                created_date=datetime.now(),
                expected_resolution=datetime.now() + timedelta(days=1),
                component="security_module",
                bypass_type=BypassType.SECURITY,
                file_path="security.py",
                line_start=25,
                line_end=30,
                validation_criteria=["Security audit passes"]
            )
        ]
    
    def tearDown(self):
        """Clean up test environment."""
        os.chdir(self.original_cwd)
        # Note: temp_dir cleanup handled by system
    
    def create_mock_args(self, **kwargs):
        """Create mock arguments object."""
        class MockArgs:
            def __init__(self, **kwargs):
                # Set defaults
                self.verbose = False
                self.quiet = False
                self.format = "text"
                self.output = None
                
                # Override with provided kwargs
                for key, value in kwargs.items():
                    setattr(self, key, value)
        
        return MockArgs(**kwargs)
    
    def test_requirement_6_1_code_review_integration(self):
        """
        Test Requirement 6.1: Code review integration with debt impact assessment
        
        WHEN code with patches is committed THEN code review SHALL include debt impact assessment
        """
        print("\n🧪 Testing Requirement 6.1: Code review integration")
        
        # Mock scanner to return sample patches
        with patch.object(self.cli.scanner, 'scan_directory') as mock_scan:
            mock_scan.return_value = {"patches": self.sample_patches, "files_scanned": 2}
            
            # Test scan command for code review
            args = self.create_mock_args(
                command="scan",
                path=".",
                recursive=True,
                validate=True,
                summary=False
            )
            
            result = self.cli._execute_scan(args)
            
            # Verify scan executed successfully
            self.assertEqual(result, 0, "Scan command should succeed")
            mock_scan.assert_called_once()
            
            # Verify patches are available for code review assessment
            self.assertEqual(len(self.cli._current_patches), 2)
            
            # Test debt impact assessment report
            args = self.create_mock_args(
                command="report",
                type="inventory",
                format="json"
            )
            
            result = self.cli._execute_report(args)
            self.assertEqual(result, 0, "Report generation should succeed")
        
        print("✅ Requirement 6.1 validated: Code review integration available")
    
    def test_requirement_6_2_cicd_pipeline_integration(self):
        """
        Test Requirement 6.2: CI/CD pipeline integration with threshold checking
        
        WHEN patches exceed debt thresholds THEN CI/CD pipelines SHALL flag for review
        """
        print("\n🧪 Testing Requirement 6.2: CI/CD pipeline integration")
        
        # Mock scanner to return patches that exceed thresholds
        with patch.object(self.cli.scanner, 'scan_directory') as mock_scan:
            mock_scan.return_value = {"patches": self.sample_patches, "files_scanned": 2}
            
            # Test CI check with low thresholds (should fail)
            args = self.create_mock_args(
                command="ci-check",
                threshold_low=50,
                threshold_medium=20,
                threshold_high=0,  # This should trigger violation
                threshold_critical=0,  # This should trigger violation
                block_merge=True,
                changed_files=None
            )
            
            result = self.cli._execute_ci_check(args)
            
            # Should return 1 (failure) due to threshold violations
            self.assertEqual(result, 1, "CI check should fail when thresholds exceeded")
            
            # Test CI check with high thresholds (should pass)
            args.threshold_high = 10
            args.threshold_critical = 5
            args.block_merge = False
            
            result = self.cli._execute_ci_check(args)
            
            # Should return 0 (success) when thresholds are met
            self.assertEqual(result, 0, "CI check should pass when thresholds met")
        
        print("✅ Requirement 6.2 validated: CI/CD pipeline integration with thresholds")
    
    def test_requirement_6_3_automated_merge_prevention(self):
        """
        Test Requirement 6.3: Automated checks preventing merge without proper annotation
        
        WHEN patches are added without proper annotation THEN automated checks SHALL prevent merge
        """
        print("\n🧪 Testing Requirement 6.3: Automated merge prevention")
        
        # Create invalid patch (missing required fields)
        invalid_patch = PatchAnnotation(
            patch_id="INVALID-001",
            reason="",  # Missing reason
            upstream_issue="",  # Missing upstream issue
            cleanup_task="",  # Missing cleanup task
            debt_level=DebtLevel.LOW,
            created_date=datetime.now(),
            expected_resolution=None,  # Missing resolution date
            component="",  # Missing component
            bypass_type=BypassType.ARCHITECTURE,
            file_path="invalid.py",
            line_start=1,
            line_end=1,
            validation_criteria=[]  # Missing validation criteria
        )
        
        # Mock scanner to return invalid patch
        with patch.object(self.cli.scanner, 'scan_directory') as mock_scan, \
             patch.object(self.cli.scanner, 'validate_patch_annotation') as mock_validate:
            
            mock_scan.return_value = {"patches": [invalid_patch], "files_scanned": 1}
            
            # Mock validation to return failure
            from src.technical_debt_patch_annotation.core.models import ValidationResult
            mock_validate.return_value = ValidationResult(
                is_valid=False,
                errors=["Missing reason", "Missing upstream issue", "Missing cleanup task"],
                warnings=["Missing expected resolution date"]
            )
            
            # Test validation command
            args = self.create_mock_args(
                command="validate",
                all=True,
                strict=True
            )
            
            result = self.cli._execute_validate(args)
            
            # Should return 1 (failure) due to validation errors
            self.assertEqual(result, 1, "Validation should fail for improperly annotated patches")
            mock_validate.assert_called()
        
        print("✅ Requirement 6.3 validated: Automated checks prevent merge without proper annotation")
    
    def test_requirement_6_4_cleanup_validation(self):
        """
        Test Requirement 6.4: Automatic validation of cleanup completion
        
        WHEN cleanup tasks are completed THEN patches SHALL be automatically validated for removal
        """
        print("\n🧪 Testing Requirement 6.4: Cleanup validation")
        
        # Mock cleanup orchestrator
        with patch.object(self.cli.cleanup_orchestrator, 'create_cleanup_plan') as mock_plan:
            mock_plan.return_value = {
                "plan_id": "CLEANUP-001",
                "patches_included": [p.patch_id for p in self.sample_patches],
                "estimated_effort": "2 hours"
            }
            
            # Test cleanup plan generation
            args = self.create_mock_args(
                command="cleanup",
                plan=True,
                component=None,
                priority="high"
            )
            
            result = self.cli._execute_cleanup(args)
            
            # Should succeed in generating cleanup plan
            self.assertEqual(result, 0, "Cleanup plan generation should succeed")
            mock_plan.assert_called_once()
            
            # Test cleanup execution (dry run)
            args = self.create_mock_args(
                command="cleanup",
                plan=False,
                execute="CLEANUP-001",
                dry_run=True
            )
            
            result = self.cli._execute_cleanup(args)
            
            # Should succeed in dry run mode
            self.assertEqual(result, 0, "Cleanup dry run should succeed")
        
        print("✅ Requirement 6.4 validated: Cleanup validation functionality available")
    
    def test_requirement_6_5_technical_debt_reporting(self):
        """
        Test Requirement 6.5: Technical debt report generation from current codebase state
        
        WHEN technical debt reports are needed THEN they SHALL be generated from current codebase state
        """
        print("\n🧪 Testing Requirement 6.5: Technical debt reporting")
        
        # Mock scanner to return sample patches
        with patch.object(self.cli.scanner, 'scan_directory') as mock_scan:
            mock_scan.return_value = {"patches": self.sample_patches, "files_scanned": 2}
            
            # Test inventory report
            args = self.create_mock_args(
                command="report",
                type="inventory",
                format="json",
                output="test_inventory.json"
            )
            
            result = self.cli._execute_report(args)
            self.assertEqual(result, 0, "Inventory report generation should succeed")
            
            # Verify report file was created
            self.assertTrue(os.path.exists("test_inventory.json"), "Report file should be created")
            
            # Verify report content
            with open("test_inventory.json", 'r') as f:
                report_data = json.load(f)
            
            self.assertEqual(report_data["report_type"], "inventory")
            self.assertEqual(report_data["total_patches"], 2)
            self.assertIn("by_debt_level", report_data)
            self.assertIn("by_component", report_data)
            
            # Test executive report
            args = self.create_mock_args(
                command="report",
                type="executive",
                format="text"
            )
            
            result = self.cli._execute_report(args)
            self.assertEqual(result, 0, "Executive report generation should succeed")
            
            # Test trends report
            args = self.create_mock_args(
                command="report",
                type="trends",
                format="json"
            )
            
            result = self.cli._execute_report(args)
            self.assertEqual(result, 0, "Trends report generation should succeed")
            
            # Test cleanup report
            args = self.create_mock_args(
                command="report",
                type="cleanup",
                format="json"
            )
            
            result = self.cli._execute_report(args)
            self.assertEqual(result, 0, "Cleanup report generation should succeed")
        
        print("✅ Requirement 6.5 validated: Technical debt reporting from current codebase")
    
    def test_cli_parser_creation(self):
        """Test that CLI parser is created with all required commands."""
        print("\n🧪 Testing CLI parser creation")
        
        parser = self.cli.create_cli_parser()
        
        # Verify parser exists
        self.assertIsNotNone(parser, "CLI parser should be created")
        
        # Test help generation (should not raise exception)
        try:
            help_text = parser.format_help()
            self.assertIn("Technical Debt Patch Annotation System CLI", help_text)
        except Exception as e:
            self.fail(f"Parser help generation failed: {e}")
        
        print("✅ CLI parser creation validated")
    
    def test_cli_health_and_capabilities(self):
        """Test CLI health monitoring and capability reporting."""
        print("\n🧪 Testing CLI health and capabilities")
        
        # Test health status
        health = self.cli.get_health_status()
        self.assertIsNotNone(health, "Health status should be available")
        self.assertIn(health.status.value, ["healthy", "warning", "error", "degraded"])
        
        # Test capabilities
        capabilities = self.cli.get_capabilities()
        self.assertIsInstance(capabilities, list, "Capabilities should be a list")
        self.assertGreater(len(capabilities), 0, "Should have at least one capability")
        
        # Test module info
        module_info = self.cli.get_module_info()
        self.assertIsInstance(module_info, dict, "Module info should be a dictionary")
        self.assertIn("module_id", module_info)
        self.assertIn("commands", module_info)
        
        # Verify expected commands are present
        expected_commands = [
            "scan", "annotate", "validate", "cleanup", "report",
            "batch", "interactive", "ci-check", "export", "import"
        ]
        
        for cmd in expected_commands:
            self.assertIn(cmd, module_info["commands"], f"Command '{cmd}' should be available")
        
        print("✅ CLI health and capabilities validated")
    
    def test_graceful_degradation(self):
        """Test CLI graceful degradation functionality."""
        print("\n🧪 Testing CLI graceful degradation")
        
        # Test graceful degradation
        degradation_result = self.cli.graceful_degradation()
        
        self.assertIsNotNone(degradation_result, "Degradation result should be available")
        self.assertIsInstance(degradation_result.success, bool, "Success should be boolean")
        self.assertIsInstance(degradation_result.remaining_capabilities, list, "Remaining capabilities should be list")
        self.assertIsInstance(degradation_result.degraded_capabilities, list, "Degraded capabilities should be list")
        
        print("✅ CLI graceful degradation validated")
    
    def test_export_import_functionality(self):
        """Test export and import functionality."""
        print("\n🧪 Testing export/import functionality")
        
        # Mock scanner for export test
        with patch.object(self.cli.scanner, 'scan_directory') as mock_scan:
            mock_scan.return_value = {"patches": self.sample_patches, "files_scanned": 2}
            
            # Test export
            args = self.create_mock_args(
                command="export",
                format="json",
                output="test_export.json",
                include_resolved=False
            )
            
            result = self.cli._execute_export(args)
            self.assertEqual(result, 0, "Export should succeed")
            
            # Verify export file exists
            self.assertTrue(os.path.exists("test_export.json"), "Export file should be created")
            
            # Test import
            args = self.create_mock_args(
                command="import",
                file="test_export.json",
                format="json",
                merge=False,
                validate=True
            )
            
            result = self.cli._execute_import(args)
            self.assertEqual(result, 0, "Import should succeed")
        
        print("✅ Export/import functionality validated")
    
    def test_batch_operations(self):
        """Test batch operations functionality."""
        print("\n🧪 Testing batch operations")
        
        # Mock scanner for batch operations
        with patch.object(self.cli.scanner, 'scan_directory') as mock_scan:
            mock_scan.return_value = {"patches": self.sample_patches, "files_scanned": 2}
            
            # Test batch operations
            args = self.create_mock_args(
                command="batch",
                expire_days=30,
                notify=True,
                update_status=None,
                bulk_edit=None,
                archive=False
            )
            
            result = self.cli._execute_batch(args)
            self.assertEqual(result, 0, "Batch operations should succeed")
        
        print("✅ Batch operations validated")


def run_compliance_tests():
    """Run all compliance tests."""
    print("🧪 Running Technical Debt Patch Annotation CLI Requirements Compliance Tests")
    print("=" * 80)
    
    # Create test suite
    suite = unittest.TestLoader().loadTestsFromTestCase(TestCLIRequirementsCompliance)
    
    # Run tests with detailed output
    runner = unittest.TextTestRunner(verbosity=2, stream=sys.stdout)
    result = runner.run(suite)
    
    # Print summary
    print("\n" + "=" * 80)
    print("📊 Test Results Summary")
    print("=" * 80)
    
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Success rate: {((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100):.1f}%")
    
    if result.failures:
        print(f"\n❌ Failures:")
        for test, traceback in result.failures:
            print(f"  • {test}: {traceback}")
    
    if result.errors:
        print(f"\n💥 Errors:")
        for test, traceback in result.errors:
            print(f"  • {test}: {traceback}")
    
    if not result.failures and not result.errors:
        print(f"\n✅ All requirements compliance tests passed!")
        print(f"The CLI interface fully meets all integration requirements.")
    
    return len(result.failures) == 0 and len(result.errors) == 0


if __name__ == "__main__":
    success = run_compliance_tests()
    sys.exit(0 if success else 1)