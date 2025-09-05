"""
CLI Integration Tests for Spec Reconciliation System

Tests all CLI commands, error handling, user feedback, and backend integration.
"""

import pytest
import subprocess
import sys
import json
import tempfile
import shutil
from pathlib import Path
from unittest.mock import patch, MagicMock
from io import StringIO

from src.spec_reconciliation.cli import main, handle_governance_commands, handle_validation_commands, handle_analysis_commands
from src.spec_reconciliation.governance import GovernanceController
from src.spec_reconciliation.models import SpecProposal, ValidationResult
from src.spec_reconciliation.validation import ConsistencyValidator


class TestCLICommands:
    """Test all CLI commands and their functionality"""
    
    def setup_method(self):
        """Set up test environment"""
        self.temp_dir = tempfile.mkdtemp()
        self.specs_dir = Path(self.temp_dir) / "specs"
        self.specs_dir.mkdir()
        
        # Create sample spec files for testing
        self._create_sample_specs()
    
    def teardown_method(self):
        """Clean up test environment"""
        shutil.rmtree(self.temp_dir)
    
    def _create_sample_specs(self):
        """Create sample spec files for CLI testing"""
        # Create a valid spec
        valid_spec_dir = self.specs_dir / "valid-spec"
        valid_spec_dir.mkdir()
        
        valid_requirements = """
# Valid Spec Requirements

## Requirements

### Requirement 1
**User Story:** As a developer, I want PDCA functionality, so that I can improve systematically.

#### Acceptance Criteria
1. WHEN planning THEN system SHALL use model registry
2. WHEN executing THEN system SHALL follow ReflectiveModule pattern
"""
        (valid_spec_dir / "requirements.md").write_text(valid_requirements)
        
        # Create a spec with terminology issues
        terminology_spec = self.specs_dir / "terminology_test_spec.md"
        terminology_content = """
# Terminology Test Spec

This spec uses RCA, root cause analysis, and Root Cause Analysis inconsistently.
It also mentions PDCA and Plan-Do-Check-Act methodology.
The ReflectiveModule pattern should be used consistently.
"""
        terminology_spec.write_text(terminology_content)
        
        # Create a spec with interface issues
        interface_spec = self.specs_dir / "interface_test_spec.md"
        interface_content = """
# Interface Test Spec

## Interface Definition

class TestModule(ReflectiveModule):
    def get_module_status(self):
        return {"status": "healthy"}
    
    def is_healthy(self):
        return True
        
    def get_health_indicators(self):
        return []

class BadModule:
    def bad_method_name(self):
        pass
"""
        interface_spec.write_text(interface_content)
    
    def test_cli_help_command(self):
        """Test CLI help functionality"""
        with patch('sys.argv', ['cli.py', '--help']):
            with pytest.raises(SystemExit):
                main()
        # Help is printed to stdout by argparse, which we can't easily mock
        # The test passes if SystemExit is raised (normal argparse behavior)
    
    def test_cli_no_command(self):
        """Test CLI behavior when no command is provided"""
        with patch('sys.argv', ['cli.py']):
            # Should print help when no command provided (via argparse)
            main()  # This will print help and return normally
    
    def test_governance_status_command(self):
        """Test governance status command"""
        with patch('sys.argv', ['cli.py', 'governance', '--status']):
            with patch('src.spec_reconciliation.cli.GovernanceController') as mock_controller:
                mock_instance = MagicMock()
                mock_instance.get_module_status.return_value = {
                    'module_name': 'GovernanceController',
                    'specs_monitored': 2,
                    'terminology_terms': 15,
                    'status': 'healthy'
                }
                mock_controller.return_value = mock_instance
                
                with patch('builtins.print') as mock_print:
                    main()
                    
                    # Should print status information
                    mock_print.assert_called()
                    printed_output = str(mock_print.call_args_list)
                    assert 'GovernanceController' in printed_output
    
    def test_governance_check_overlaps_command(self):
        """Test governance check overlaps command"""
        with patch('sys.argv', ['cli.py', 'governance', '--check-overlaps']):
            with patch('src.spec_reconciliation.cli.GovernanceController') as mock_controller:
                mock_instance = MagicMock()
                
                # Mock overlap report
                from src.spec_reconciliation.governance import OverlapReport, OverlapSeverity
                mock_overlap_report = OverlapReport(
                    spec_pairs=[("spec1", "spec2")],
                    overlap_percentage=0.75,
                    overlapping_functionality=["function1", "function2"],
                    severity=OverlapSeverity.HIGH,
                    consolidation_recommendation="Consolidate immediately"
                )
                mock_instance.check_overlap_conflicts.return_value = mock_overlap_report
                mock_controller.return_value = mock_instance
                
                with patch('builtins.print') as mock_print:
                    main()
                    
                    # Should print overlap information
                    mock_print.assert_called()
                    printed_output = str(mock_print.call_args_list)
                    assert 'HIGH' in printed_output or 'Consolidate' in printed_output
    
    def test_governance_validate_spec_command_valid_file(self):
        """Test governance validate spec command with valid file"""
        spec_file = self.specs_dir / "test_spec.md"
        spec_content = """
# Test Spec

This is a test specification for validation.
"""
        spec_file.write_text(spec_content)
        
        with patch('sys.argv', ['cli.py', 'governance', '--validate-spec', str(spec_file)]):
            with patch('src.spec_reconciliation.cli.GovernanceController') as mock_controller:
                mock_instance = MagicMock()
                mock_instance.validate_new_spec.return_value = ValidationResult.APPROVED
                mock_controller.return_value = mock_instance
                
                with patch('builtins.print') as mock_print:
                    main()
                    
                    # Should print validation result
                    mock_print.assert_called()
                    printed_output = str(mock_print.call_args_list)
                    assert 'approved' in printed_output.lower() or 'validation' in printed_output.lower()
    
    def test_governance_validate_spec_command_missing_file(self):
        """Test governance validate spec command with missing file"""
        missing_file = self.specs_dir / "nonexistent_spec.md"
        
        with patch('sys.argv', ['cli.py', 'governance', '--validate-spec', str(missing_file)]):
            with patch('builtins.print') as mock_print:
                main()
                
                # Should print file not found message
                mock_print.assert_called()
                printed_output = str(mock_print.call_args_list)
                assert 'not found' in printed_output
    
    def test_validate_terminology_command_valid_file(self):
        """Test validate terminology command with valid file"""
        terminology_spec = self.specs_dir / "terminology_test_spec.md"
        
        with patch('sys.argv', ['cli.py', 'validate', '--terminology', str(terminology_spec)]):
            with patch('src.spec_reconciliation.cli.ConsistencyValidator') as mock_validator:
                mock_instance = MagicMock()
                
                # Mock terminology report
                from src.spec_reconciliation.validation import TerminologyReport
                mock_report = TerminologyReport(
                    consistent_terms={'PDCA', 'ReflectiveModule'},
                    inconsistent_terms={'RCA': ['root cause analysis', 'Root Cause Analysis']},
                    new_terms={'systematic_improvement'},
                    deprecated_terms=set(),
                    consistency_score=0.85,
                    recommendations=['Standardize RCA terminology']
                )
                mock_instance.validate_terminology.return_value = mock_report
                mock_validator.return_value = mock_instance
                
                with patch('builtins.print') as mock_print:
                    main()
                    
                    # Should print terminology report
                    mock_print.assert_called()
                    printed_output = str(mock_print.call_args_list)
                    assert '0.85' in printed_output or 'Consistency Score' in printed_output
    
    def test_validate_terminology_command_missing_file(self):
        """Test validate terminology command with missing file"""
        missing_file = self.specs_dir / "nonexistent_spec.md"
        
        with patch('sys.argv', ['cli.py', 'validate', '--terminology', str(missing_file)]):
            with patch('builtins.print') as mock_print:
                main()
                
                # Should print file not found message
                mock_print.assert_called()
                printed_output = str(mock_print.call_args_list)
                assert 'not found' in printed_output
    
    def test_validate_interfaces_command_valid_file(self):
        """Test validate interfaces command with valid file"""
        interface_spec = self.specs_dir / "interface_test_spec.md"
        
        with patch('sys.argv', ['cli.py', 'validate', '--interfaces', str(interface_spec)]):
            with patch('src.spec_reconciliation.cli.ConsistencyValidator') as mock_validator:
                mock_instance = MagicMock()
                
                # Mock interface compliance report
                from src.spec_reconciliation.validation import ComplianceReport
                mock_report = ComplianceReport(
                    compliant_interfaces=['TestModule'],
                    non_compliant_interfaces=['BadModule'],
                    missing_methods={},
                    compliance_score=0.75,
                    remediation_steps=['Fix BadModule naming convention']
                )
                mock_instance.check_interface_compliance.return_value = mock_report
                mock_validator.return_value = mock_instance
                
                with patch('builtins.print') as mock_print:
                    main()
                    
                    # Should print interface compliance report
                    mock_print.assert_called()
                    printed_output = str(mock_print.call_args_list)
                    assert '0.75' in printed_output or 'Compliance Score' in printed_output
    
    def test_validate_consistency_score_command(self):
        """Test validate consistency score command"""
        spec_files = [str(self.specs_dir / "terminology_test_spec.md"), 
                     str(self.specs_dir / "interface_test_spec.md")]
        
        with patch('sys.argv', ['cli.py', 'validate', '--consistency-score'] + spec_files):
            with patch('src.spec_reconciliation.cli.ConsistencyValidator') as mock_validator:
                mock_instance = MagicMock()
                
                # Mock consistency metrics
                from src.spec_reconciliation.validation import ConsistencyMetrics, ConsistencyLevel
                mock_metrics = ConsistencyMetrics(
                    overall_score=0.82,
                    consistency_level=ConsistencyLevel.GOOD,
                    terminology_score=0.85,
                    interface_score=0.78,
                    pattern_score=0.83,
                    critical_issues=['Interface naming inconsistency'],
                    improvement_priority=['Standardize interface patterns']
                )
                mock_instance.generate_consistency_score.return_value = mock_metrics
                mock_validator.return_value = mock_instance
                
                with patch('builtins.print') as mock_print:
                    main()
                    
                    # Should print consistency metrics
                    mock_print.assert_called()
                    printed_output = str(mock_print.call_args_list)
                    assert '0.82' in printed_output or 'GOOD' in printed_output
    
    def test_analyze_all_specs_command(self):
        """Test analyze all specs command"""
        with patch('sys.argv', ['cli.py', 'analyze', '--all-specs']):
            with patch('src.spec_reconciliation.cli.GovernanceController') as mock_controller:
                with patch('src.spec_reconciliation.cli.ConsistencyValidator') as mock_validator:
                    # Mock governance controller
                    mock_gov_instance = MagicMock()
                    mock_gov_instance.get_module_status.return_value = {
                        'specs_monitored': 3,
                        'terminology_terms': 25
                    }
                    mock_controller.return_value = mock_gov_instance
                    
                    # Mock consistency validator
                    mock_val_instance = MagicMock()
                    mock_val_instance.get_module_status.return_value = {
                        'terminology_registry_size': 25,
                        'interface_patterns_loaded': 5
                    }
                    mock_validator.return_value = mock_val_instance
                    
                    with patch('builtins.print') as mock_print:
                        main()
                        
                        # Should print analysis information
                        mock_print.assert_called()
                        printed_output = str(mock_print.call_args_list)
                        assert 'specs monitored' in printed_output or '3' in printed_output
    
    def test_analyze_overlap_matrix_command(self):
        """Test analyze overlap matrix command"""
        with patch('sys.argv', ['cli.py', 'analyze', '--overlap-matrix']):
            with patch('src.spec_reconciliation.cli.GovernanceController') as mock_controller:
                mock_instance = MagicMock()
                mock_controller.return_value = mock_instance
                
                with patch('builtins.print') as mock_print:
                    main()
                    
                    # Should print overlap matrix information
                    mock_print.assert_called()
                    printed_output = str(mock_print.call_args_list)
                    assert 'overlap matrix' in printed_output or 'not yet implemented' in printed_output


class TestCLIErrorHandling:
    """Test CLI error handling and user feedback"""
    
    def test_cli_exception_handling(self):
        """Test CLI handles exceptions gracefully"""
        with patch('sys.argv', ['cli.py', 'governance', '--status']):
            with patch('src.spec_reconciliation.cli.GovernanceController') as mock_controller:
                # Mock controller to raise exception
                mock_controller.side_effect = Exception("Test exception")
                
                with patch('builtins.print') as mock_print:
                    with patch('sys.exit') as mock_exit:
                        main()
                        
                        # Should print error message and exit with code 1
                        mock_print.assert_called()
                        printed_output = str(mock_print.call_args_list)
                        assert 'Error:' in printed_output
                        mock_exit.assert_called_with(1)
    
    def test_invalid_command_handling(self):
        """Test handling of invalid commands"""
        with patch('sys.argv', ['cli.py', 'invalid-command']):
            with pytest.raises(SystemExit):
                main()
        # Invalid commands cause argparse to exit with error code
    
    def test_missing_required_arguments(self):
        """Test handling of missing required arguments"""
        # Test governance validate-spec without file argument
        with patch('sys.argv', ['cli.py', 'governance', '--validate-spec']):
            with pytest.raises(SystemExit):
                main()
    
    def test_file_permission_errors(self):
        """Test handling of file permission errors"""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create a file and remove read permissions
            test_file = Path(temp_dir) / "no_permission.md"
            test_file.write_text("test content")
            test_file.chmod(0o000)  # Remove all permissions
            
            try:
                with patch('sys.argv', ['cli.py', 'validate', '--terminology', str(test_file)]):
                    with pytest.raises(SystemExit):
                        main()
                # Should exit with error code 1 due to permission error
            finally:
                # Restore permissions for cleanup
                test_file.chmod(0o644)


class TestCLIBackendIntegration:
    """Test CLI integration with all backend components"""
    
    def setup_method(self):
        """Set up test environment"""
        self.temp_dir = tempfile.mkdtemp()
        self.specs_dir = Path(self.temp_dir) / "specs"
        self.specs_dir.mkdir()
        
        # Create sample spec for integration testing
        self._create_integration_test_spec()
    
    def teardown_method(self):
        """Clean up test environment"""
        shutil.rmtree(self.temp_dir)
    
    def _create_integration_test_spec(self):
        """Create spec for integration testing"""
        spec_dir = self.specs_dir / "integration-test-spec"
        spec_dir.mkdir()
        
        requirements_content = """
# Integration Test Spec Requirements

## Requirements

### Requirement 1
**User Story:** As a developer, I want PDCA functionality, so that I can improve systematically.

#### Acceptance Criteria
1. WHEN planning THEN system SHALL use model registry
2. WHEN executing THEN system SHALL follow ReflectiveModule pattern
3. WHEN checking THEN system SHALL validate results
4. WHEN acting THEN system SHALL implement improvements
"""
        (spec_dir / "requirements.md").write_text(requirements_content)
        
        design_content = """
# Integration Test Spec Design

## Interface

class IntegrationTestModule(ReflectiveModule):
    def get_module_status(self):
        return {"status": "healthy"}
    
    def is_healthy(self):
        return True
        
    def get_health_indicators(self):
        return []
    
    def execute_pdca_cycle(self):
        pass
"""
        (spec_dir / "design.md").write_text(design_content)
    
    def test_governance_controller_integration(self):
        """Test CLI integration with GovernanceController"""
        with patch('sys.argv', ['cli.py', 'governance', '--status']):
            # Use real GovernanceController with test specs directory
            with patch('src.spec_reconciliation.cli.GovernanceController') as mock_controller:
                # Create real controller instance for integration test
                real_controller = GovernanceController(str(self.specs_dir))
                mock_controller.return_value = real_controller
                
                with patch('builtins.print') as mock_print:
                    main()
                    
                    # Should successfully integrate with real controller
                    mock_print.assert_called()
                    printed_output = str(mock_print.call_args_list)
                    assert 'GovernanceController' in printed_output
    
    def test_consistency_validator_integration(self):
        """Test CLI integration with ConsistencyValidator"""
        terminology_spec = self.specs_dir / "terminology_test.md"
        terminology_content = """
# Terminology Test

This spec uses PDCA methodology and ReflectiveModule pattern.
It should be consistent with standard terminology.
"""
        terminology_spec.write_text(terminology_content)
        
        with patch('sys.argv', ['cli.py', 'validate', '--terminology', str(terminology_spec)]):
            # Use real ConsistencyValidator with test specs directory
            with patch('src.spec_reconciliation.cli.ConsistencyValidator') as mock_validator:
                # Create real validator instance for integration test
                real_validator = ConsistencyValidator(str(self.specs_dir))
                mock_validator.return_value = real_validator
                
                with patch('builtins.print') as mock_print:
                    main()
                    
                    # Should successfully integrate with real validator
                    mock_print.assert_called()
                    printed_output = str(mock_print.call_args_list)
                    assert 'Consistency Score' in printed_output or 'score' in printed_output
    
    def test_end_to_end_workflow_integration(self):
        """Test end-to-end CLI workflow integration"""
        # Test complete workflow: governance check -> validation -> analysis
        
        # Step 1: Check governance status
        with patch('sys.argv', ['cli.py', 'governance', '--status']):
            with patch('src.spec_reconciliation.cli.GovernanceController') as mock_controller:
                mock_instance = MagicMock()
                mock_instance.get_module_status.return_value = {
                    'module_name': 'GovernanceController',
                    'specs_monitored': 1,
                    'terminology_terms': 10
                }
                mock_controller.return_value = mock_instance
                
                with patch('builtins.print') as mock_print:
                    main()
                    assert mock_print.called
        
        # Step 2: Validate terminology
        terminology_spec = self.specs_dir / "workflow_test.md"
        terminology_spec.write_text("Test content with PDCA and ReflectiveModule")
        
        with patch('sys.argv', ['cli.py', 'validate', '--terminology', str(terminology_spec)]):
            with patch('src.spec_reconciliation.cli.ConsistencyValidator') as mock_validator:
                mock_instance = MagicMock()
                from src.spec_reconciliation.validation import TerminologyReport
                mock_report = TerminologyReport(
                    consistent_terms={'PDCA', 'ReflectiveModule'},
                    inconsistent_terms={},
                    new_terms=set(),
                    deprecated_terms=set(),
                    consistency_score=0.9,
                    recommendations=[]
                )
                mock_instance.validate_terminology.return_value = mock_report
                mock_validator.return_value = mock_instance
                
                with patch('builtins.print') as mock_print:
                    main()
                    assert mock_print.called
        
        # Step 3: Analyze all specs
        with patch('sys.argv', ['cli.py', 'analyze', '--all-specs']):
            with patch('src.spec_reconciliation.cli.GovernanceController') as mock_controller:
                with patch('src.spec_reconciliation.cli.ConsistencyValidator') as mock_validator:
                    mock_gov = MagicMock()
                    mock_gov.get_module_status.return_value = {'specs_monitored': 1}
                    mock_controller.return_value = mock_gov
                    
                    mock_val = MagicMock()
                    mock_val.get_module_status.return_value = {'terminology_registry_size': 10}
                    mock_validator.return_value = mock_val
                    
                    with patch('builtins.print') as mock_print:
                        main()
                        assert mock_print.called


class TestCLIHelpDocumentation:
    """Test CLI help documentation and usage examples"""
    
    def test_main_help_documentation(self):
        """Test main CLI help documentation"""
        with patch('sys.argv', ['cli.py', '--help']):
            with pytest.raises(SystemExit):
                main()
        # Help documentation is handled by argparse and printed to stdout
    
    def test_governance_subcommand_help(self):
        """Test governance subcommand help"""
        with patch('sys.argv', ['cli.py', 'governance', '--help']):
            with pytest.raises(SystemExit):
                main()
        # Subcommand help is handled by argparse
    
    def test_validate_subcommand_help(self):
        """Test validate subcommand help"""
        with patch('sys.argv', ['cli.py', 'validate', '--help']):
            with pytest.raises(SystemExit):
                main()
        # Subcommand help is handled by argparse
    
    def test_analyze_subcommand_help(self):
        """Test analyze subcommand help"""
        with patch('sys.argv', ['cli.py', 'analyze', '--help']):
            with pytest.raises(SystemExit):
                main()
        # Subcommand help is handled by argparse


class TestCLIUsageExamples:
    """Test CLI usage examples and common workflows"""
    
    def setup_method(self):
        """Set up test environment"""
        self.temp_dir = tempfile.mkdtemp()
        self.specs_dir = Path(self.temp_dir) / "specs"
        self.specs_dir.mkdir()
    
    def teardown_method(self):
        """Clean up test environment"""
        shutil.rmtree(self.temp_dir)
    
    def test_typical_governance_workflow(self):
        """Test typical governance workflow usage"""
        # Create test spec
        test_spec = self.specs_dir / "example_spec.md"
        test_spec.write_text("""
# Example Spec

This is an example specification for testing governance workflow.

## Requirements
- PDCA methodology implementation
- ReflectiveModule pattern compliance
""")
        
        # Test governance workflow: status -> validate -> check overlaps
        commands = [
            ['cli.py', 'governance', '--status'],
            ['cli.py', 'governance', '--validate-spec', str(test_spec)],
            ['cli.py', 'governance', '--check-overlaps']
        ]
        
        for cmd in commands:
            with patch('sys.argv', cmd):
                with patch('src.spec_reconciliation.cli.GovernanceController') as mock_controller:
                    mock_instance = MagicMock()
                    mock_instance.get_module_status.return_value = {'status': 'healthy'}
                    mock_instance.validate_new_spec.return_value = ValidationResult.APPROVED
                    
                    from src.spec_reconciliation.governance import OverlapReport, OverlapSeverity
                    mock_overlap = OverlapReport(
                        spec_pairs=[],
                        overlap_percentage=0.1,
                        overlapping_functionality=[],
                        severity=OverlapSeverity.LOW,
                        consolidation_recommendation="No action needed"
                    )
                    mock_instance.check_overlap_conflicts.return_value = mock_overlap
                    mock_controller.return_value = mock_instance
                    
                    with patch('builtins.print') as mock_print:
                        main()
                        assert mock_print.called
    
    def test_typical_validation_workflow(self):
        """Test typical validation workflow usage"""
        # Create test specs
        spec1 = self.specs_dir / "spec1.md"
        spec1.write_text("Content with PDCA and ReflectiveModule")
        
        spec2 = self.specs_dir / "spec2.md"
        spec2.write_text("""
class TestModule(ReflectiveModule):
    def get_module_status(self): pass
    def is_healthy(self): pass
""")
        
        # Test validation workflow: terminology -> interfaces -> consistency score
        commands = [
            ['cli.py', 'validate', '--terminology', str(spec1)],
            ['cli.py', 'validate', '--interfaces', str(spec2)],
            ['cli.py', 'validate', '--consistency-score', str(spec1), str(spec2)]
        ]
        
        for cmd in commands:
            with patch('sys.argv', cmd):
                with patch('src.spec_reconciliation.cli.ConsistencyValidator') as mock_validator:
                    mock_instance = MagicMock()
                    
                    # Mock different report types
                    from src.spec_reconciliation.validation import (
                        TerminologyReport, ComplianceReport, 
                        ConsistencyMetrics, ConsistencyLevel
                    )
                    
                    mock_instance.validate_terminology.return_value = TerminologyReport(
                        consistent_terms=set(), inconsistent_terms={}, 
                        new_terms=set(), deprecated_terms=set(),
                        consistency_score=0.9, recommendations=[]
                    )
                    
                    mock_instance.check_interface_compliance.return_value = ComplianceReport(
                        compliant_interfaces=[], non_compliant_interfaces=[], 
                        missing_methods={}, compliance_score=0.8, remediation_steps=[]
                    )
                    
                    mock_instance.generate_consistency_score.return_value = ConsistencyMetrics(
                        overall_score=0.85, consistency_level=ConsistencyLevel.GOOD,
                        terminology_score=0.9, interface_score=0.8, pattern_score=0.85,
                        critical_issues=[], improvement_priority=[]
                    )
                    
                    mock_validator.return_value = mock_instance
                    
                    with patch('builtins.print') as mock_print:
                        main()
                        assert mock_print.called
    
    def test_typical_analysis_workflow(self):
        """Test typical analysis workflow usage"""
        commands = [
            ['cli.py', 'analyze', '--all-specs'],
            ['cli.py', 'analyze', '--overlap-matrix']
        ]
        
        for cmd in commands:
            with patch('sys.argv', cmd):
                with patch('src.spec_reconciliation.cli.GovernanceController') as mock_controller:
                    with patch('src.spec_reconciliation.cli.ConsistencyValidator') as mock_validator:
                        mock_gov = MagicMock()
                        mock_gov.get_module_status.return_value = {'specs_monitored': 5}
                        mock_controller.return_value = mock_gov
                        
                        mock_val = MagicMock()
                        mock_val.get_module_status.return_value = {'terminology_registry_size': 50}
                        mock_validator.return_value = mock_val
                        
                        with patch('builtins.print') as mock_print:
                            main()
                            assert mock_print.called


def test_cli_module_import():
    """Test that CLI module imports correctly"""
    from src.spec_reconciliation import cli
    assert hasattr(cli, 'main')
    assert hasattr(cli, 'handle_governance_commands')
    assert hasattr(cli, 'handle_validation_commands')
    assert hasattr(cli, 'handle_analysis_commands')


def test_cli_argument_parsing():
    """Test CLI argument parsing functionality"""
    import argparse
    from src.spec_reconciliation.cli import main
    
    # Test that argument parser is set up correctly
    with patch('sys.argv', ['cli.py']):
        with patch('builtins.print'):
            main()  # Should not crash


if __name__ == '__main__':
    pytest.main([__file__])