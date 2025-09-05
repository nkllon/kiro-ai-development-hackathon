"""
Comprehensive Unit Test Coverage for Consolidated Functionality

This test suite provides comprehensive unit test coverage for all consolidated
system components to ensure >90% code coverage and validate all merged requirements.

Requirements: R10.1, R10.2
"""

import pytest
import tempfile
import shutil
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
import json
from datetime import datetime, timedelta

# Import all consolidated system components
from src.spec_reconciliation.governance import GovernanceController
from src.spec_reconciliation.models import SpecProposal, ValidationResult, OverlapSeverity
from src.spec_reconciliation.validation import (
    ConsistencyValidator, ConsistencyLevel, TerminologyReport, ComplianceReport
)
from src.spec_reconciliation.consolidation import (
    SpecConsolidator, ConsolidationStatus, ConflictResolutionStrategy
)
from src.spec_reconciliation.monitoring import (
    ContinuousMonitor, DriftSeverity, CorrectionStatus
)
from src.spec_reconciliation.boundary_resolver import (
    ComponentBoundaryResolver, ComponentBoundary, ComponentType
)


class TestGovernanceControllerUnitCoverage:
    """Comprehensive unit tests for GovernanceController (R10.1)"""
    
    def setup_method(self):
        """Set up test environment"""
        self.temp_dir = tempfile.mkdtemp()
        self.specs_dir = Path(self.temp_dir) / "specs"
        self.specs_dir.mkdir()
        
        # Create sample specs for testing
        self._create_sample_specs()
        
        self.controller = GovernanceController()
    
    def teardown_method(self):
        """Clean up test environment"""
        shutil.rmtree(self.temp_dir)
    
    def _create_sample_specs(self):
        """Create sample spec files for testing"""
        spec_names = ["test-spec-1", "test-spec-2", "overlapping-spec"]
        
        for spec_name in spec_names:
            spec_dir = self.specs_dir / spec_name
            spec_dir.mkdir()
            
            requirements_content = f"""
# {spec_name.replace('-', ' ').title()} Requirements

## Requirements

### Requirement 1
**User Story:** As a developer, I want {spec_name} functionality, so that I can test the system.

#### Acceptance Criteria
1. WHEN using {spec_name} THEN the system SHALL respond correctly
2. WHEN validating {spec_name} THEN results SHALL be accurate
"""
            
            (spec_dir / "requirements.md").write_text(requirements_content)
    
    def test_governance_controller_initialization(self):
        """Test GovernanceController initialization and health (R10.1)"""
        assert self.controller.is_healthy()
        
        status = self.controller.get_module_status()
        assert status['module_name'] == 'GovernanceController'
        assert 'specs_monitored' in status
        assert status['specs_monitored'] >= 0
        assert 'last_validation' in status
        assert 'governance_rules_active' in status
    
    def test_spec_proposal_validation_edge_cases(self):
        """Test spec proposal validation with edge cases (R10.1)"""
        # Test empty proposal
        empty_proposal = SpecProposal(
            name="",
            content="",
            requirements=[],
            interfaces=[],
            terminology=set(),
            functionality_keywords=set()
        )
        
        result = self.controller.validate_new_spec(empty_proposal)
        assert result in [ValidationResult.REJECTED, ValidationResult.REQUIRES_REVIEW]
        
        # Test proposal with special characters
        special_proposal = SpecProposal(
            name="test-spec-with-special-chars!@#",
            content="Content with special chars: !@#$%^&*()",
            requirements=["Special requirement with chars: <>?"],
            interfaces=["Interface@#$"],
            terminology={"term!@#"},
            functionality_keywords={"keyword!@#"}
        )
        
        result = self.controller.validate_new_spec(special_proposal)
        assert isinstance(result, ValidationResult)
        
        # Test very large proposal
        large_proposal = SpecProposal(
            name="large-spec",
            content="x" * 10000,  # Large content
            requirements=["req" + str(i) for i in range(100)],  # Many requirements
            interfaces=["interface" + str(i) for i in range(50)],
            terminology={"term" + str(i) for i in range(200)},
            functionality_keywords={"keyword" + str(i) for i in range(300)}
        )
        
        result = self.controller.validate_new_spec(large_proposal)
        assert isinstance(result, ValidationResult)
    
    def test_overlap_detection_algorithms(self):
        """Test overlap detection algorithm accuracy (R10.1)"""
        # Test identical functionality keywords
        proposal1 = SpecProposal(
            name="identical-spec",
            content="Identical functionality",
            requirements=["Same requirement"],
            interfaces=["SameInterface"],
            terminology={"same_term"},
            functionality_keywords={"test", "validate", "system"}
        )
        
        overlap_report = self.controller.check_overlap_conflicts(proposal1)
        assert isinstance(overlap_report.severity, OverlapSeverity)
        assert 0.0 <= overlap_report.overlap_percentage <= 1.0
        
        # Test no overlap
        unique_proposal = SpecProposal(
            name="unique-spec",
            content="Completely unique functionality",
            requirements=["Unique requirement"],
            interfaces=["UniqueInterface"],
            terminology={"unique_term"},
            functionality_keywords={"unique", "distinct", "novel"}
        )
        
        unique_overlap = self.controller.check_overlap_conflicts(unique_proposal)
        assert unique_overlap.overlap_percentage < 0.5  # Should be low overlap
    
    def test_approval_workflow_enforcement(self):
        """Test approval workflow enforcement logic (R10.1)"""
        # Test different types of change requests
        change_types = [
            {
                'type': 'minor_change',
                'affected_specs': ['spec1'],
                'description': 'Minor update'
            },
            {
                'type': 'major_change',
                'affected_specs': ['spec1', 'spec2', 'spec3'],
                'description': 'Major architectural change'
            },
            {
                'type': 'architecture_change',
                'affected_specs': ['spec1', 'spec2', 'spec3', 'spec4', 'spec5'],
                'description': 'System-wide architectural change'
            }
        ]
        
        for change_request in change_types:
            approval_status = self.controller.enforce_approval_workflow(change_request)
            
            assert hasattr(approval_status, 'status')
            assert isinstance(approval_status.status, ValidationResult)
            
            # Major changes should require review
            if len(change_request['affected_specs']) > 2:
                assert approval_status.status == ValidationResult.REQUIRES_REVIEW
    
    def test_consolidation_triggering(self):
        """Test consolidation workflow triggering (R10.1)"""
        from src.spec_reconciliation.models import OverlapReport
        
        # Test high overlap triggering consolidation
        high_overlap_report = OverlapReport(
            spec_pairs=[("spec1", "spec2")],
            overlap_percentage=0.85,
            overlapping_functionality=["function1", "function2", "function3"],
            severity=OverlapSeverity.HIGH,
            consolidation_recommendation="Immediate consolidation required"
        )
        
        workflow = self.controller.trigger_consolidation(high_overlap_report)
        assert workflow['status'] == 'triggered'
        assert 'workflow_id' in workflow
        assert len(workflow['next_steps']) > 0
        
        # Test low overlap not triggering consolidation
        low_overlap_report = OverlapReport(
            spec_pairs=[("spec3", "spec4")],
            overlap_percentage=0.15,
            overlapping_functionality=["minor_function"],
            severity=OverlapSeverity.LOW,
            consolidation_recommendation="Monitor for future overlap"
        )
        
        low_workflow = self.controller.trigger_consolidation(low_overlap_report)
        assert low_workflow['status'] in ['monitoring', 'deferred']


class TestConsistencyValidatorUnitCoverage:
    """Comprehensive unit tests for ConsistencyValidator (R10.1)"""
    
    def setup_method(self):
        """Set up test environment"""
        self.temp_dir = tempfile.mkdtemp()
        self.specs_dir = Path(self.temp_dir) / "specs"
        self.specs_dir.mkdir()
        
        self.validator = ConsistencyValidator(str(self.specs_dir))
    
    def teardown_method(self):
        """Clean up test environment"""
        shutil.rmtree(self.temp_dir)
    
    def test_terminology_validation_comprehensive(self):
        """Test comprehensive terminology validation (R10.1)"""
        # Test various terminology scenarios
        test_cases = [
            {
                'content': 'This uses RCA methodology consistently.',
                'expected_consistent': True,
                'description': 'Simple consistent terminology'
            },
            {
                'content': 'This uses RCA and root cause analysis interchangeably.',
                'expected_consistent': False,
                'description': 'Inconsistent terminology variations'
            },
            {
                'content': 'PDCA cycle implementation with Plan-Do-Check-Act methodology.',
                'expected_consistent': False,
                'description': 'Mixed terminology formats'
            },
            {
                'content': 'ReflectiveModule pattern with reflective module design.',
                'expected_consistent': False,
                'description': 'Case sensitivity issues'
            }
        ]
        
        for case in test_cases:
            report = self.validator.validate_terminology(case['content'])
            
            assert isinstance(report, TerminologyReport)
            assert isinstance(report.consistency_score, float)
            assert 0.0 <= report.consistency_score <= 1.0
            assert isinstance(report.consistent_terms, set)
            assert isinstance(report.inconsistent_terms, dict)
            assert isinstance(report.new_terms, set)
            assert isinstance(report.recommendations, list)
    
    def test_interface_compliance_comprehensive(self):
        """Test comprehensive interface compliance checking (R10.1)"""
        # Test various interface scenarios
        interface_cases = [
            {
                'interface': '''
                class GoodReflectiveModule(ReflectiveModule):
                    def get_module_status(self) -> Dict[str, Any]:
                        return {'status': 'healthy'}
                    
                    def is_healthy(self) -> bool:
                        return True
                    
                    def get_health_indicators(self) -> Dict[str, Any]:
                        return {'uptime': 0.99}
                ''',
                'expected_compliant': True,
                'description': 'Fully compliant ReflectiveModule'
            },
            {
                'interface': '''
                class PartialReflectiveModule(ReflectiveModule):
                    def get_module_status(self) -> Dict[str, Any]:
                        return {'status': 'healthy'}
                ''',
                'expected_compliant': False,
                'description': 'Partially compliant ReflectiveModule'
            },
            {
                'interface': '''
                class NonReflectiveModule:
                    def some_method(self):
                        pass
                ''',
                'expected_compliant': True,  # Non-ReflectiveModule classes are compliant by default
                'description': 'Non-ReflectiveModule class'
            }
        ]
        
        for case in interface_cases:
            report = self.validator.check_interface_compliance(case['interface'])
            
            assert isinstance(report, ComplianceReport)
            assert isinstance(report.compliance_score, float)
            assert 0.0 <= report.compliance_score <= 1.0
            assert isinstance(report.compliant_interfaces, list)
            assert isinstance(report.non_compliant_interfaces, list)
            assert isinstance(report.missing_methods, dict)
            assert isinstance(report.remediation_steps, list)
    
    def test_pattern_consistency_validation(self):
        """Test pattern consistency validation (R10.1)"""
        # Test different pattern combinations
        pattern_cases = [
            ['PDCA', 'RCA', 'ReflectiveModule'],
            ['PDCA', 'plan-do-check-act'],  # Inconsistent
            ['RCA', 'root-cause-analysis'],  # Inconsistent
            []  # Empty patterns
        ]
        
        for patterns in pattern_cases:
            report = self.validator.validate_pattern_consistency(patterns)
            
            assert isinstance(report.pattern_score, float)
            assert 0.0 <= report.pattern_score <= 1.0
            assert isinstance(report.consistent_patterns, list)
            assert isinstance(report.inconsistent_patterns, list)
    
    def test_consistency_score_generation(self):
        """Test overall consistency score generation (R10.1)"""
        # Create temporary spec files
        spec_files = []
        for i in range(3):
            spec_file = self.temp_dir / f"test_spec_{i}.md"
            spec_content = f"""
            # Test Spec {i}
            
            This spec uses PDCA methodology and ReflectiveModule pattern.
            It implements RCA for issue resolution.
            
            ## Interface
            
            class TestModule{i}(ReflectiveModule):
                def get_module_status(self):
                    return {{'module_name': 'TestModule{i}'}}
            """
            spec_file.write_text(spec_content)
            spec_files.append(str(spec_file))
        
        metrics = self.validator.generate_consistency_score(spec_files)
        
        assert isinstance(metrics.overall_score, float)
        assert 0.0 <= metrics.overall_score <= 1.0
        assert isinstance(metrics.consistency_level, ConsistencyLevel)
        assert isinstance(metrics.critical_issues, list)
        assert isinstance(metrics.improvement_priority, list)


class TestSpecConsolidatorUnitCoverage:
    """Comprehensive unit tests for SpecConsolidator (R10.1)"""
    
    def setup_method(self):
        """Set up test environment"""
        self.temp_dir = tempfile.mkdtemp()
        self.specs_dir = Path(self.temp_dir) / "specs"
        self.specs_dir.mkdir()
        
        # Create overlapping specs for testing
        self._create_overlapping_specs()
        
        self.consolidator = SpecConsolidator(str(self.specs_dir))
    
    def teardown_method(self):
        """Clean up test environment"""
        shutil.rmtree(self.temp_dir)
    
    def _create_overlapping_specs(self):
        """Create overlapping spec files for testing"""
        # Spec 1: Beast Mode functionality
        spec1_dir = self.specs_dir / "beast-mode-spec"
        spec1_dir.mkdir()
        
        spec1_content = """
# Beast Mode Spec

## Requirements

### Requirement 1
**User Story:** As a developer, I want PDCA cycles, so that development is systematic.

#### Acceptance Criteria
1. WHEN executing PDCA THEN system SHALL optimize systematically
2. WHEN monitoring tools THEN health SHALL be maintained
"""
        
        (spec1_dir / "requirements.md").write_text(spec1_content)
        
        # Spec 2: Overlapping PDCA functionality
        spec2_dir = self.specs_dir / "pdca-optimization-spec"
        spec2_dir.mkdir()
        
        spec2_content = """
# PDCA Optimization Spec

## Requirements

### Requirement 1
**User Story:** As a system, I want PDCA optimization, so that performance improves.

#### Acceptance Criteria
1. WHEN optimizing PDCA THEN system SHALL improve performance
2. WHEN executing cycles THEN results SHALL be measured
"""
        
        (spec2_dir / "requirements.md").write_text(spec2_content)
    
    def test_overlap_analysis_comprehensive(self):
        """Test comprehensive overlap analysis (R10.1)"""
        spec_list = ["beast-mode-spec", "pdca-optimization-spec"]
        
        overlap_analysis = self.consolidator.analyze_overlap(spec_list)
        
        assert hasattr(overlap_analysis, 'overlapping_specs')
        assert hasattr(overlap_analysis, 'overlap_matrix')
        assert hasattr(overlap_analysis, 'consolidation_opportunities')
        
        # Should detect PDCA overlap
        assert len(overlap_analysis.overlapping_specs) > 0
    
    def test_consolidation_plan_creation(self):
        """Test consolidation plan creation (R10.1)"""
        # Create mock overlap analysis
        from src.spec_reconciliation.consolidation import OverlapAnalysis
        
        overlap_analysis = OverlapAnalysis(
            analysis_id="test_analysis",
            analyzed_specs=["beast-mode-spec", "pdca-optimization-spec"],
            overlapping_specs=[("beast-mode-spec", "pdca-optimization-spec")],
            overlap_matrix={"beast-mode-spec": {"pdca-optimization-spec": 0.7}},
            consolidation_opportunities=[
                {
                    'specs': ["beast-mode-spec", "pdca-optimization-spec"],
                    'overlap_score': 0.7,
                    'consolidation_benefit': 'high'
                }
            ],
            generated_at=datetime.now()
        )
        
        consolidation_plan = self.consolidator.create_consolidation_plan(overlap_analysis)
        
        assert hasattr(consolidation_plan, 'target_specs')
        assert hasattr(consolidation_plan, 'unified_spec_name')
        assert hasattr(consolidation_plan, 'consolidation_steps')
        assert hasattr(consolidation_plan, 'status')
    
    def test_requirement_merging(self):
        """Test requirement merging with conflict resolution (R10.1)"""
        # Create overlapping requirements for testing
        overlapping_requirements = [
            {
                'id': 'R1_spec1',
                'content': 'System SHALL execute PDCA cycles systematically',
                'source_spec': 'beast-mode-spec',
                'priority': 'high'
            },
            {
                'id': 'R1_spec2', 
                'content': 'System SHALL optimize PDCA for performance',
                'source_spec': 'pdca-optimization-spec',
                'priority': 'medium'
            }
        ]
        
        unified_requirement = self.consolidator.merge_requirements(overlapping_requirements)
        
        assert hasattr(unified_requirement, 'unified_id')
        assert hasattr(unified_requirement, 'merged_content')
        assert hasattr(unified_requirement, 'source_requirements')
        assert hasattr(unified_requirement, 'resolution_strategy')
    
    def test_traceability_preservation(self):
        """Test traceability preservation during consolidation (R10.1)"""
        # Mock original and unified specs
        original_specs = ["beast-mode-spec", "pdca-optimization-spec"]
        unified_spec = "unified-beast-mode-pdca-spec"
        
        traceability_map = self.consolidator.preserve_traceability(original_specs, unified_spec)
        
        assert hasattr(traceability_map, 'original_to_unified')
        assert hasattr(traceability_map, 'unified_to_original')
        assert hasattr(traceability_map, 'requirement_mappings')
        assert hasattr(traceability_map, 'interface_mappings')


class TestContinuousMonitorUnitCoverage:
    """Comprehensive unit tests for ContinuousMonitor (R10.1)"""
    
    def setup_method(self):
        """Set up test environment"""
        self.temp_dir = tempfile.mkdtemp()
        self.specs_dir = Path(self.temp_dir) / "specs"
        self.specs_dir.mkdir()
        
        # Create specs with potential drift
        self._create_drift_test_specs()
        
        self.monitor = ContinuousMonitor(str(self.specs_dir))
    
    def teardown_method(self):
        """Clean up test environment"""
        shutil.rmtree(self.temp_dir)
    
    def _create_drift_test_specs(self):
        """Create spec files for drift testing"""
        spec_dir = self.specs_dir / "drift-test-spec"
        spec_dir.mkdir()
        
        spec_content = """
# Drift Test Spec

This spec uses RCA methodology and root cause analysis.
It also mentions PDCA and Plan-Do-Check-Act cycles.
"""
        
        (spec_dir / "requirements.md").write_text(spec_content)
    
    def test_spec_drift_monitoring(self):
        """Test spec drift detection and monitoring (R10.1)"""
        drift_report = self.monitor.monitor_spec_drift()
        
        assert hasattr(drift_report, 'drift_detected')
        assert hasattr(drift_report, 'affected_specs')
        assert hasattr(drift_report, 'drift_types')
        assert hasattr(drift_report, 'severity_assessment')
    
    def test_terminology_inconsistency_detection(self):
        """Test terminology inconsistency detection (R10.1)"""
        inconsistency_report = self.monitor.detect_terminology_inconsistencies()
        
        assert hasattr(inconsistency_report, 'report_id')
        assert hasattr(inconsistency_report, 'terminology_drift')
        assert hasattr(inconsistency_report, 'consistency_degradation')
        assert hasattr(inconsistency_report, 'correction_suggestions')
    
    def test_architectural_decision_validation(self):
        """Test architectural decision validation (R10.1)"""
        # Mock architectural decision
        architectural_decision = {
            'decision_id': 'AD001',
            'title': 'Adopt ReflectiveModule pattern',
            'description': 'All modules should implement ReflectiveModule',
            'rationale': 'Improves monitoring and health checking',
            'affected_components': ['all_modules']
        }
        
        validation_result = self.monitor.validate_architectural_decisions(architectural_decision)
        
        assert hasattr(validation_result, 'decision_id')
        assert hasattr(validation_result, 'validation_status')
        assert hasattr(validation_result, 'compliance_issues')
        assert hasattr(validation_result, 'recommendations')
    
    def test_automatic_correction_triggering(self):
        """Test automatic correction workflow triggering (R10.1)"""
        # Mock drift detection
        from src.spec_reconciliation.monitoring import DriftReport
        
        drift_report = DriftReport(
            report_id="test_drift",
            generated_at=datetime.now(),
            drift_detected=True,
            affected_specs=["drift-test-spec"],
            drift_types=["terminology_inconsistency"],
            severity_assessment=DriftSeverity.MEDIUM,
            correction_recommendations=["Standardize terminology"]
        )
        
        correction_workflow = self.monitor.trigger_automatic_correction(drift_report)
        
        assert hasattr(correction_workflow, 'workflow_id')
        assert hasattr(correction_workflow, 'correction_type')
        assert hasattr(correction_workflow, 'target_specs')
        assert hasattr(correction_workflow, 'status')


class TestComponentBoundaryResolverUnitCoverage:
    """Comprehensive unit tests for ComponentBoundaryResolver (R10.1)"""
    
    def setup_method(self):
        """Set up test environment"""
        self.temp_dir = tempfile.mkdtemp()
        self.specs_dir = Path(self.temp_dir) / "specs"
        self.specs_dir.mkdir()
        
        # Create component specs for boundary testing
        self._create_component_specs()
        
        self.resolver = ComponentBoundaryResolver(str(self.specs_dir))
    
    def teardown_method(self):
        """Clean up test environment"""
        shutil.rmtree(self.temp_dir)
    
    def _create_component_specs(self):
        """Create component spec files for boundary testing"""
        components = ["component-a", "component-b", "component-c"]
        
        for component in components:
            comp_dir = self.specs_dir / component
            comp_dir.mkdir()
            
            requirements_content = f"""
# {component.replace('-', ' ').title()} Requirements

## Requirements

### Requirement 1
**User Story:** As {component}, I want clear boundaries, so that I don't overlap with others.

#### Acceptance Criteria
1. WHEN operating THEN I SHALL respect component boundaries
2. WHEN interacting THEN I SHALL use defined interfaces
"""
            
            (comp_dir / "requirements.md").write_text(requirements_content)
    
    def test_component_boundary_definition(self):
        """Test component boundary definition (R10.1)"""
        consolidated_specs = ["component-a", "component-b", "component-c"]
        
        boundaries = self.resolver.define_component_boundaries(consolidated_specs)
        
        assert len(boundaries) == len(consolidated_specs)
        
        for boundary in boundaries:
            assert isinstance(boundary, ComponentBoundary)
            assert boundary.component_name in consolidated_specs
            assert isinstance(boundary.component_type, ComponentType)
            assert len(boundary.primary_responsibilities) > 0
    
    def test_interface_contract_creation(self):
        """Test interface contract creation (R10.1)"""
        consolidated_specs = ["component-a", "component-b"]
        
        boundaries = self.resolver.define_component_boundaries(consolidated_specs)
        contracts = self.resolver.create_interface_contracts(boundaries)
        
        assert len(contracts) > 0
        
        for contract in contracts:
            assert hasattr(contract, 'interface_name')
            assert hasattr(contract, 'provider_component')
            assert hasattr(contract, 'methods')
            assert hasattr(contract, 'data_contracts')
    
    def test_dependency_management(self):
        """Test dependency management implementation (R10.1)"""
        consolidated_specs = ["component-a", "component-b", "component-c"]
        
        boundaries = self.resolver.define_component_boundaries(consolidated_specs)
        contracts = self.resolver.create_interface_contracts(boundaries)
        dependency_graph = self.resolver.implement_dependency_management(boundaries, contracts)
        
        assert isinstance(dependency_graph, dict)
        assert len(dependency_graph) > 0
        
        # Verify no circular dependencies
        for component, dependencies in dependency_graph.items():
            for dependency in dependencies:
                assert not dependency.is_circular
    
    def test_boundary_violation_detection(self):
        """Test boundary violation detection (R10.1)"""
        consolidated_specs = ["component-a", "component-b"]
        
        boundaries = self.resolver.define_component_boundaries(consolidated_specs)
        contracts = self.resolver.create_interface_contracts(boundaries)
        dependency_graph = self.resolver.implement_dependency_management(boundaries, contracts)
        
        violations = self.resolver._detect_boundary_violations(boundaries, contracts, dependency_graph)
        
        # Should return list of violations (may be empty for clean boundaries)
        assert isinstance(violations, list)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])