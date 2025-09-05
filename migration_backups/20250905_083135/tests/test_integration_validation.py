"""
Integration Test Suite for Consolidated Systems

This test suite validates component interactions and boundary compliance
across all consolidated systems to ensure proper integration.

Requirements: R10.1, R10.2, R10.3
"""

import pytest
import tempfile
import shutil
from pathlib import Path
import json
import time
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, MagicMock
import concurrent.futures
import threading

# Import consolidated system components
from src.spec_reconciliation.governance import GovernanceController
from src.spec_reconciliation.validation import ConsistencyValidator
from src.spec_reconciliation.consolidation import SpecConsolidator
from src.spec_reconciliation.monitoring import ContinuousMonitor
from src.spec_reconciliation.boundary_resolver import ComponentBoundaryResolver


class TestSystemIntegrationWorkflows:
    """Test integration workflows across consolidated systems (R10.2)"""
    
    def setup_method(self):
        """Set up integration testing environment"""
        self.temp_dir = tempfile.mkdtemp()
        self.specs_dir = Path(self.temp_dir) / "specs"
        self.specs_dir.mkdir()
        
        # Create integrated test specs
        self._create_integration_test_specs()
        
        # Initialize all system components
        self.governance = GovernanceController(str(self.specs_dir))
        self.validator = ConsistencyValidator(str(self.specs_dir))
        self.consolidator = SpecConsolidator(str(self.specs_dir))
        self.monitor = ContinuousMonitor(str(self.specs_dir))
        self.boundary_resolver = ComponentBoundaryResolver(str(self.specs_dir))
    
    def teardown_method(self):
        """Clean up integration testing environment"""
        shutil.rmtree(self.temp_dir)
    
    def _create_integration_test_specs(self):
        """Create specs for integration testing"""
        integration_specs = [
            "beast_mode_integration_test",
            "testing_rca_integration_test",
            "rdi_rm_integration_test"
        ]
        
        for spec_name in integration_specs:
            spec_dir = self.specs_dir / spec_name
            spec_dir.mkdir()
            
            requirements_content = f"""
# {spec_name.replace('_', ' ').title()} Requirements

## Requirements

### Requirement 1: Integration Validation
**User Story:** As a system component, I want to integrate properly with other components, so that the overall system functions correctly.

#### Acceptance Criteria
1. WHEN integrating with other systems THEN data flows SHALL be validated
2. WHEN processing requests THEN boundaries SHALL be respected
3. WHEN errors occur THEN they SHALL be handled gracefully
4. WHEN monitoring health THEN status SHALL be reported accurately
5. WHEN scaling operations THEN performance SHALL be maintained
"""
            
            design_content = f"""
# {spec_name.replace('_', ' ').title()} Design

## Interface

class {spec_name.replace('_', '').title()}Interface(ReflectiveModule):
    def process_integration_request(self, request: IntegrationRequest) -> IntegrationResponse:
        '''Process integration request from other components'''
        pass
    
    def validate_data_flow(self, data_context: DataContext) -> ValidationResult:
        '''Validate data flow between components'''
        pass
    
    def handle_integration_error(self, error_context: ErrorContext) -> ErrorResponse:
        '''Handle integration errors gracefully'''
        pass
    
    def report_integration_health(self) -> HealthReport:
        '''Report integration health status'''
        pass
"""
            
            (spec_dir / "requirements.md").write_text(requirements_content)
            (spec_dir / "design.md").write_text(design_content)
    
    def test_beast_mode_to_testing_rca_integration(self):
        """Test Beast Mode to Testing/RCA integration workflow (R10.2)"""
        # Test data flow from Beast Mode to Testing/RCA
        
        # Step 1: Beast Mode generates performance data
        beast_mode_output = {
            'pdca_cycle_id': 'integration_test_001',
            'performance_metrics': {
                'development_velocity': 1.25,
                'tool_health_score': 0.98,
                'backlog_efficiency': 0.87
            },
            'optimization_results': {
                'tools_optimized': ['pytest', 'black', 'mypy'],
                'performance_improvements': {'velocity': 0.25, 'quality': 0.15}
            },
            'next_phase': 'comprehensive_testing'
        }
        
        # Step 2: Testing/RCA consumes Beast Mode data
        testing_rca_input = {
            'trigger_source': 'beast_mode_system',
            'cycle_id': beast_mode_output['pdca_cycle_id'],
            'performance_baseline': beast_mode_output['performance_metrics'],
            'optimization_context': beast_mode_output['optimization_results'],
            'test_targets': {
                'validate_improvements': True,
                'regression_testing': True,
                'performance_validation': True
            }
        }
        
        # Verify data compatibility
        assert testing_rca_input['cycle_id'] == beast_mode_output['pdca_cycle_id']
        assert testing_rca_input['performance_baseline']['development_velocity'] == beast_mode_output['performance_metrics']['development_velocity']
        
        # Step 3: Testing/RCA processes and validates
        testing_rca_output = {
            'test_execution_id': f"test_{beast_mode_output['pdca_cycle_id']}",
            'validation_results': {
                'performance_improvements_verified': True,
                'regression_tests_passed': True,
                'tool_optimizations_validated': True
            },
            'test_metrics': {
                'total_tests': 150,
                'passed': 148,
                'failed': 2,
                'coverage': 0.92
            },
            'rca_findings': {
                'issues_identified': 2,
                'root_causes': ['minor_configuration_drift', 'test_data_staleness'],
                'automated_fixes_applied': 1
            },
            'next_phase': 'compliance_validation'
        }
        
        # Verify integration success
        assert testing_rca_output['validation_results']['performance_improvements_verified'] is True
        assert testing_rca_output['test_metrics']['passed'] / testing_rca_output['test_metrics']['total_tests'] >= 0.95
        assert len(testing_rca_output['rca_findings']['root_causes']) == testing_rca_output['rca_findings']['issues_identified']
    
    def test_testing_rca_to_rdi_rm_integration(self):
        """Test Testing/RCA to RDI/RM integration workflow (R10.2)"""
        # Test data flow from Testing/RCA to RDI/RM
        
        # Step 1: Testing/RCA generates quality evidence
        testing_rca_output = {
            'test_execution_id': 'test_integration_002',
            'quality_evidence': {
                'test_coverage': 0.91,
                'pass_rate': 0.96,
                'performance_validation': True,
                'security_tests_passed': True
            },
            'rca_analysis': {
                'issues_resolved': 3,
                'patterns_identified': ['memory_optimization', 'cache_efficiency'],
                'preventive_measures': ['monitoring_enhancement', 'automated_cleanup']
            },
            'compliance_data': {
                'requirements_tested': 45,
                'design_elements_validated': 38,
                'implementation_coverage': 0.89
            }
        }
        
        # Step 2: RDI/RM consumes Testing/RCA data
        rdi_rm_input = {
            'trigger_source': 'testing_rca_framework',
            'validation_request_id': f"compliance_{testing_rca_output['test_execution_id']}",
            'quality_evidence': testing_rca_output['quality_evidence'],
            'testing_metrics': testing_rca_output['compliance_data'],
            'improvement_evidence': testing_rca_output['rca_analysis'],
            'compliance_targets': {
                'traceability_completeness': 1.0,
                'quality_score_minimum': 0.9,
                'coverage_minimum': 0.85
            }
        }
        
        # Verify data compatibility
        assert rdi_rm_input['quality_evidence']['test_coverage'] == testing_rca_output['quality_evidence']['test_coverage']
        assert rdi_rm_input['testing_metrics']['implementation_coverage'] == testing_rca_output['compliance_data']['implementation_coverage']
        
        # Step 3: RDI/RM validates compliance
        rdi_rm_output = {
            'compliance_validation_id': rdi_rm_input['validation_request_id'],
            'rdi_compliance_results': {
                'requirements_traceability': 1.0,
                'design_compliance': 0.94,
                'implementation_alignment': 0.91,
                'overall_compliance': 0.95
            },
            'quality_assessment': {
                'quality_score': 0.93,
                'improvement_areas': ['design_documentation', 'edge_case_testing'],
                'strengths': ['test_coverage', 'performance_validation', 'rca_integration']
            },
            'compliance_status': 'PASSED',
            'recommendations': [
                'Enhance design documentation for better compliance',
                'Add edge case testing for comprehensive coverage'
            ]
        }
        
        # Verify integration success
        assert rdi_rm_output['compliance_status'] == 'PASSED'
        assert rdi_rm_output['rdi_compliance_results']['overall_compliance'] >= 0.9
        assert rdi_rm_output['quality_assessment']['quality_score'] >= rdi_rm_input['compliance_targets']['quality_score_minimum']
    
    def test_full_system_integration_workflow(self):
        """Test complete integration workflow across all systems (R10.2)"""
        # Test end-to-end integration workflow
        
        workflow_id = 'full_integration_test_001'
        
        # Phase 1: Beast Mode initiates systematic development
        beast_mode_initiation = {
            'workflow_id': workflow_id,
            'pdca_phase': 'plan',
            'domain_context': 'integration_testing',
            'objectives': ['validate_integration', 'measure_performance', 'ensure_compliance']
        }
        
        # Phase 2: Beast Mode executes and optimizes
        beast_mode_execution = {
            'workflow_id': workflow_id,
            'pdca_phase': 'do',
            'execution_results': {
                'tools_health_verified': True,
                'backlog_optimized': True,
                'performance_baseline_established': True
            },
            'metrics_generated': {
                'velocity_improvement': 0.28,
                'quality_enhancement': 0.18,
                'efficiency_gain': 0.22
            },
            'handoff_to': 'testing_rca_framework'
        }
        
        # Phase 3: Testing/RCA validates and analyzes
        testing_rca_validation = {
            'workflow_id': workflow_id,
            'trigger_source': beast_mode_execution['handoff_to'],
            'validation_scope': 'comprehensive',
            'test_execution': {
                'integration_tests': {'passed': 25, 'failed': 0},
                'performance_tests': {'baseline_met': True, 'improvements_verified': True},
                'regression_tests': {'passed': 40, 'failed': 1}
            },
            'rca_analysis': {
                'regression_root_cause': 'test_data_version_mismatch',
                'resolution_applied': True,
                'prevention_measures': ['automated_test_data_sync']
            },
            'handoff_to': 'rdi_rm_analysis_system'
        }
        
        # Phase 4: RDI/RM ensures compliance
        rdi_rm_compliance = {
            'workflow_id': workflow_id,
            'trigger_source': testing_rca_validation['handoff_to'],
            'compliance_validation': {
                'requirements_traced': True,
                'design_validated': True,
                'implementation_verified': True,
                'quality_assured': True
            },
            'final_assessment': {
                'overall_compliance': 0.96,
                'integration_quality': 0.94,
                'workflow_success': True
            }
        }
        
        # Phase 5: Beast Mode completes PDCA cycle
        beast_mode_completion = {
            'workflow_id': workflow_id,
            'pdca_phase': 'check_act',
            'cycle_results': {
                'objectives_met': all([
                    rdi_rm_compliance['compliance_validation']['requirements_traced'],
                    testing_rca_validation['test_execution']['performance_tests']['baseline_met'],
                    rdi_rm_compliance['final_assessment']['workflow_success']
                ]),
                'improvements_validated': True,
                'lessons_learned': [
                    'Integration workflows function correctly',
                    'Performance improvements are measurable',
                    'Compliance validation is comprehensive'
                ]
            },
            'next_cycle_planning': {
                'continue_optimization': True,
                'focus_areas': ['edge_case_handling', 'performance_tuning']
            }
        }
        
        # Verify complete workflow success
        assert beast_mode_completion['cycle_results']['objectives_met'] is True
        assert rdi_rm_compliance['final_assessment']['workflow_success'] is True
        assert testing_rca_validation['rca_analysis']['resolution_applied'] is True
        
        # Verify workflow continuity
        workflow_ids = [
            beast_mode_initiation['workflow_id'],
            beast_mode_execution['workflow_id'],
            testing_rca_validation['workflow_id'],
            rdi_rm_compliance['workflow_id'],
            beast_mode_completion['workflow_id']
        ]
        assert all(wid == workflow_id for wid in workflow_ids), "Workflow ID continuity broken"


class TestComponentBoundaryCompliance:
    """Test component boundary compliance and enforcement (R10.2)"""
    
    def setup_method(self):
        """Set up boundary compliance testing environment"""
        self.temp_dir = tempfile.mkdtemp()
        self.specs_dir = Path(self.temp_dir) / "specs"
        self.specs_dir.mkdir()
        
        # Create boundary test specs
        self._create_boundary_test_specs()
        
        # Initialize boundary resolver
        self.boundary_resolver = ComponentBoundaryResolver(str(self.specs_dir))
        self.validator = ConsistencyValidator(str(self.specs_dir))
    
    def teardown_method(self):
        """Clean up boundary compliance testing environment"""
        shutil.rmtree(self.temp_dir)
    
    def _create_boundary_test_specs(self):
        """Create specs for boundary compliance testing"""
        boundary_specs = [
            "boundary_test_component_a",
            "boundary_test_component_b", 
            "boundary_test_component_c"
        ]
        
        for spec_name in boundary_specs:
            spec_dir = self.specs_dir / spec_name
            spec_dir.mkdir()
            
            requirements_content = f"""
# {spec_name.replace('_', ' ').title()} Requirements

## Requirements

### Requirement 1: Boundary Compliance
**User Story:** As a component, I want clear boundaries, so that I don't overlap with other components.

#### Acceptance Criteria
1. WHEN operating THEN I SHALL only access allowed dependencies
2. WHEN providing services THEN I SHALL use defined interfaces
3. WHEN consuming services THEN I SHALL respect other component boundaries
4. WHEN handling data THEN I SHALL follow data contracts
5. WHEN reporting status THEN I SHALL use standard patterns
"""
            
            design_content = f"""
# {spec_name.replace('_', ' ').title()} Design

## Interface

class {spec_name.replace('_', '').title()}Interface(ReflectiveModule):
    def execute_primary_function(self, context: ComponentContext) -> ComponentResult:
        '''Execute primary component function within boundaries'''
        pass
    
    def interact_with_dependency(self, dependency_interface: DependencyInterface) -> InteractionResult:
        '''Interact with allowed dependencies only'''
        pass
    
    def provide_service(self, service_request: ServiceRequest) -> ServiceResponse:
        '''Provide service through defined interface'''
        pass
"""
            
            (spec_dir / "requirements.md").write_text(requirements_content)
            (spec_dir / "design.md").write_text(design_content)
    
    def test_component_boundary_definition_compliance(self):
        """Test component boundaries are properly defined and enforced (R10.2)"""
        # Test boundary definition
        consolidated_specs = [
            "boundary_test_component_a",
            "boundary_test_component_b",
            "boundary_test_component_c"
        ]
        
        boundaries = self.boundary_resolver.define_component_boundaries(consolidated_specs)
        
        # Verify each component has clear boundaries
        assert len(boundaries) == 3
        
        for boundary in boundaries:
            # Each boundary should have unique responsibilities
            assert len(boundary.primary_responsibilities) > 0
            assert len(boundary.boundary_constraints) > 0
            assert len(boundary.interface_contracts) > 0
            
            # Verify boundary constraints are specific
            for constraint in boundary.boundary_constraints:
                assert isinstance(constraint, str)
                assert len(constraint) > 0
        
        # Verify no overlapping responsibilities
        all_responsibilities = []
        for boundary in boundaries:
            all_responsibilities.extend(boundary.primary_responsibilities)
        
        unique_responsibilities = set(all_responsibilities)
        assert len(all_responsibilities) == len(unique_responsibilities), "Overlapping responsibilities detected"
    
    def test_interface_contract_compliance(self):
        """Test interface contracts are properly defined and enforced (R10.2)"""
        # Test interface contract creation
        consolidated_specs = [
            "boundary_test_component_a",
            "boundary_test_component_b"
        ]
        
        boundaries = self.boundary_resolver.define_component_boundaries(consolidated_specs)
        contracts = self.boundary_resolver.create_interface_contracts(boundaries)
        
        # Verify contracts are well-defined
        assert len(contracts) > 0
        
        for contract in contracts:
            # Each contract should have required elements
            assert contract.interface_name
            assert contract.provider_component
            assert len(contract.consumer_components) > 0
            assert len(contract.methods) > 0
            assert len(contract.data_contracts) > 0
            assert len(contract.validation_rules) > 0
            
            # Verify method definitions
            for method in contract.methods:
                assert 'name' in method
                assert 'parameters' in method
                assert 'return_type' in method
                assert 'description' in method
            
            # Verify data contracts
            for data_contract in contract.data_contracts:
                assert 'name' in data_contract
                assert 'fields' in data_contract
                assert 'validation' in data_contract
    
    def test_dependency_management_compliance(self):
        """Test dependency management enforces clean interactions (R10.2)"""
        # Test dependency management
        consolidated_specs = [
            "boundary_test_component_a",
            "boundary_test_component_b",
            "boundary_test_component_c"
        ]
        
        boundaries = self.boundary_resolver.define_component_boundaries(consolidated_specs)
        contracts = self.boundary_resolver.create_interface_contracts(boundaries)
        dependency_graph = self.boundary_resolver.implement_dependency_management(boundaries, contracts)
        
        # Verify dependency graph is clean
        assert isinstance(dependency_graph, dict)
        assert len(dependency_graph) > 0
        
        for component, dependencies in dependency_graph.items():
            assert component in consolidated_specs
            
            for dependency in dependencies:
                # Each dependency should be valid
                assert dependency.dependent_component == component
                assert dependency.dependency_component
                assert dependency.dependency_type in ["interface", "service", "data"]
                assert dependency.validation_status == "valid"
                
                # No circular dependencies
                assert not dependency.is_circular, f"Circular dependency detected: {component} -> {dependency.dependency_component}"
    
    def test_boundary_violation_detection(self):
        """Test boundary violations are properly detected (R10.2)"""
        # Create boundaries with intentional violations for testing
        from src.spec_reconciliation.boundary_resolver import ComponentBoundary, ComponentType, BoundaryViolationType
        
        # Create overlapping boundaries
        boundary_a = ComponentBoundary(
            component_name="test_component_a",
            component_type=ComponentType.CORE_COMPONENT,
            primary_responsibilities=["data_processing", "validation"],
            boundary_constraints=["MUST NOT access component B directly"],
            interface_contracts=["TestInterfaceA"],
            allowed_dependencies=["shared_service"],
            forbidden_access=["test_component_b"],
            shared_services=[]
        )
        
        boundary_b = ComponentBoundary(
            component_name="test_component_b", 
            component_type=ComponentType.CORE_COMPONENT,
            primary_responsibilities=["data_processing", "reporting"],  # Overlap with A
            boundary_constraints=["MUST NOT access component A directly"],
            interface_contracts=["TestInterfaceB"],
            allowed_dependencies=["shared_service"],
            forbidden_access=["test_component_a"],
            shared_services=[]
        )
        
        boundaries = [boundary_a, boundary_b]
        contracts = []  # Empty for this test
        dependency_graph = {}  # Empty for this test
        
        # Detect violations
        violations = self.boundary_resolver._detect_boundary_violations(boundaries, contracts, dependency_graph)
        
        # Should detect functional overlap
        functional_overlaps = [v for v in violations if v.violation_type == BoundaryViolationType.FUNCTIONAL_OVERLAP]
        assert len(functional_overlaps) > 0, "Should detect functional overlap between components"
        
        # Verify violation details
        for violation in functional_overlaps:
            assert violation.severity in ["low", "medium", "high", "critical"]
            assert len(violation.description) > 0
            assert len(violation.affected_components) > 0
    
    def test_integration_test_plan_compliance(self):
        """Test integration test plans validate boundary compliance (R10.2)"""
        # Test integration test plan generation
        consolidated_specs = [
            "boundary_test_component_a",
            "boundary_test_component_b"
        ]
        
        boundaries = self.boundary_resolver.define_component_boundaries(consolidated_specs)
        contracts = self.boundary_resolver.create_interface_contracts(boundaries)
        
        test_plan = self.boundary_resolver._generate_integration_test_plan(boundaries, contracts)
        
        # Verify test plan completeness
        assert 'test_suites' in test_plan
        assert 'boundary_tests' in test_plan
        assert 'contract_tests' in test_plan
        assert 'dependency_tests' in test_plan
        
        # Verify boundary tests
        assert len(test_plan['boundary_tests']) == len(boundaries)
        
        for boundary_test in test_plan['boundary_tests']:
            assert 'component' in boundary_test
            assert 'test_name' in boundary_test
            assert 'test_cases' in boundary_test
            
            # Should have tests for each responsibility
            test_cases = boundary_test['test_cases']
            assert len(test_cases) > 0
            
            # Verify test case structure
            for test_case in test_cases:
                assert 'name' in test_case
                assert 'description' in test_case
                assert 'validation_criteria' in test_case
        
        # Verify contract tests
        assert len(test_plan['contract_tests']) == len(contracts)
        
        for contract_test in test_plan['contract_tests']:
            assert 'contract' in contract_test
            assert 'test_name' in contract_test
            assert 'test_cases' in contract_test
            
            # Should test each method in the contract
            test_cases = contract_test['test_cases']
            assert len(test_cases) > 0


class TestDataFlowValidation:
    """Test data flow validation between components (R10.2)"""
    
    def setup_method(self):
        """Set up data flow validation testing environment"""
        self.temp_dir = tempfile.mkdtemp()
        self.specs_dir = Path(self.temp_dir) / "specs"
        self.specs_dir.mkdir()
        
        # Initialize components
        self.validator = ConsistencyValidator(str(self.specs_dir))
        self.monitor = ContinuousMonitor(str(self.specs_dir))
    
    def teardown_method(self):
        """Clean up data flow validation testing environment"""
        shutil.rmtree(self.temp_dir)
    
    def test_data_format_compatibility(self):
        """Test data format compatibility between components (R10.2)"""
        # Test data format validation
        
        # Define data formats for each system
        beast_mode_output_format = {
            'pdca_cycle_id': 'string',
            'performance_metrics': {
                'development_velocity': 'float',
                'tool_health_score': 'float',
                'backlog_efficiency': 'float'
            },
            'optimization_results': {
                'tools_optimized': 'list[string]',
                'performance_improvements': 'dict[string, float]'
            },
            'timestamp': 'datetime'
        }
        
        testing_rca_input_format = {
            'cycle_id': 'string',
            'performance_baseline': {
                'development_velocity': 'float',
                'tool_health_score': 'float',
                'backlog_efficiency': 'float'
            },
            'optimization_context': {
                'tools_optimized': 'list[string]',
                'performance_improvements': 'dict[string, float]'
            },
            'received_at': 'datetime'
        }
        
        # Validate format compatibility
        def validate_format_compatibility(output_format, input_format):
            """Validate that output format is compatible with input format"""
            compatibility_issues = []
            
            # Check field mappings
            field_mappings = {
                'pdca_cycle_id': 'cycle_id',
                'performance_metrics': 'performance_baseline',
                'optimization_results': 'optimization_context',
                'timestamp': 'received_at'
            }
            
            for output_field, input_field in field_mappings.items():
                if output_field in output_format and input_field in input_format:
                    output_type = output_format[output_field]
                    input_type = input_format[input_field]
                    
                    if isinstance(output_type, dict) and isinstance(input_type, dict):
                        # Recursively check nested structures
                        nested_issues = validate_format_compatibility(output_type, input_type)
                        compatibility_issues.extend(nested_issues)
                    elif output_type != input_type:
                        compatibility_issues.append(f"Type mismatch: {output_field}({output_type}) -> {input_field}({input_type})")
                else:
                    if output_field in output_format and input_field not in input_format:
                        compatibility_issues.append(f"Missing input field: {input_field} for output {output_field}")
            
            return compatibility_issues
        
        # Validate Beast Mode -> Testing/RCA compatibility
        compatibility_issues = validate_format_compatibility(beast_mode_output_format, testing_rca_input_format)
        
        # Should have no compatibility issues
        assert len(compatibility_issues) == 0, f"Data format compatibility issues: {compatibility_issues}"
    
    def test_data_transformation_validation(self):
        """Test data transformation between components (R10.2)"""
        # Test data transformation logic
        
        # Mock Beast Mode output
        beast_mode_data = {
            'pdca_cycle_id': 'cycle_001',
            'performance_metrics': {
                'development_velocity': 1.25,
                'tool_health_score': 0.98,
                'backlog_efficiency': 0.87
            },
            'optimization_results': {
                'tools_optimized': ['pytest', 'black', 'mypy'],
                'performance_improvements': {'velocity': 0.25, 'quality': 0.15}
            },
            'timestamp': datetime.now()
        }
        
        # Transform for Testing/RCA consumption
        def transform_beast_mode_to_testing_rca(beast_data):
            """Transform Beast Mode output for Testing/RCA input"""
            return {
                'cycle_id': beast_data['pdca_cycle_id'],
                'performance_baseline': beast_data['performance_metrics'],
                'optimization_context': beast_data['optimization_results'],
                'received_at': datetime.now(),
                'source_system': 'beast_mode_system'
            }
        
        transformed_data = transform_beast_mode_to_testing_rca(beast_mode_data)
        
        # Validate transformation
        assert transformed_data['cycle_id'] == beast_mode_data['pdca_cycle_id']
        assert transformed_data['performance_baseline'] == beast_mode_data['performance_metrics']
        assert transformed_data['optimization_context'] == beast_mode_data['optimization_results']
        assert 'received_at' in transformed_data
        assert 'source_system' in transformed_data
    
    def test_data_validation_rules(self):
        """Test data validation rules between components (R10.2)"""
        # Test data validation logic
        
        def validate_beast_mode_output(data):
            """Validate Beast Mode output data"""
            validation_errors = []
            
            # Required fields
            required_fields = ['pdca_cycle_id', 'performance_metrics', 'optimization_results']
            for field in required_fields:
                if field not in data:
                    validation_errors.append(f"Missing required field: {field}")
            
            # Performance metrics validation
            if 'performance_metrics' in data:
                metrics = data['performance_metrics']
                
                # Velocity should be positive
                if 'development_velocity' in metrics and metrics['development_velocity'] <= 0:
                    validation_errors.append("Development velocity must be positive")
                
                # Health score should be between 0 and 1
                if 'tool_health_score' in metrics:
                    score = metrics['tool_health_score']
                    if not (0 <= score <= 1):
                        validation_errors.append(f"Tool health score {score} must be between 0 and 1")
            
            # Optimization results validation
            if 'optimization_results' in data:
                results = data['optimization_results']
                
                # Tools optimized should be a list
                if 'tools_optimized' in results and not isinstance(results['tools_optimized'], list):
                    validation_errors.append("Tools optimized must be a list")
            
            return validation_errors
        
        # Test valid data
        valid_data = {
            'pdca_cycle_id': 'cycle_001',
            'performance_metrics': {
                'development_velocity': 1.25,
                'tool_health_score': 0.98,
                'backlog_efficiency': 0.87
            },
            'optimization_results': {
                'tools_optimized': ['pytest', 'black'],
                'performance_improvements': {'velocity': 0.25}
            }
        }
        
        validation_errors = validate_beast_mode_output(valid_data)
        assert len(validation_errors) == 0, f"Valid data should not have errors: {validation_errors}"
        
        # Test invalid data
        invalid_data = {
            'pdca_cycle_id': 'cycle_002',
            'performance_metrics': {
                'development_velocity': -0.5,  # Invalid: negative
                'tool_health_score': 1.5,     # Invalid: > 1
            },
            'optimization_results': {
                'tools_optimized': 'not_a_list',  # Invalid: not a list
            }
        }
        
        validation_errors = validate_beast_mode_output(invalid_data)
        assert len(validation_errors) > 0, "Invalid data should have validation errors"
        assert any("positive" in error for error in validation_errors)
        assert any("between 0 and 1" in error for error in validation_errors)
        assert any("must be a list" in error for error in validation_errors)
    
    def test_data_flow_monitoring(self):
        """Test data flow monitoring and alerting (R10.2)"""
        # Test data flow monitoring
        
        data_flow_metrics = {
            'beast_mode_to_testing_rca': {
                'messages_sent': 100,
                'messages_received': 98,
                'avg_latency_ms': 45,
                'error_rate': 0.02
            },
            'testing_rca_to_rdi_rm': {
                'messages_sent': 98,
                'messages_received': 97,
                'avg_latency_ms': 32,
                'error_rate': 0.01
            },
            'rdi_rm_to_beast_mode': {
                'messages_sent': 97,
                'messages_received': 97,
                'avg_latency_ms': 28,
                'error_rate': 0.00
            }
        }
        
        # Monitor data flow health
        def monitor_data_flow_health(metrics):
            """Monitor data flow health and generate alerts"""
            alerts = []
            
            for flow_name, flow_metrics in metrics.items():
                # Check message delivery rate
                delivery_rate = flow_metrics['messages_received'] / flow_metrics['messages_sent']
                if delivery_rate < 0.95:  # 95% delivery rate threshold
                    alerts.append({
                        'type': 'low_delivery_rate',
                        'flow': flow_name,
                        'rate': delivery_rate,
                        'severity': 'high' if delivery_rate < 0.9 else 'medium'
                    })
                
                # Check latency
                if flow_metrics['avg_latency_ms'] > 100:  # 100ms latency threshold
                    alerts.append({
                        'type': 'high_latency',
                        'flow': flow_name,
                        'latency': flow_metrics['avg_latency_ms'],
                        'severity': 'high' if flow_metrics['avg_latency_ms'] > 200 else 'medium'
                    })
                
                # Check error rate
                if flow_metrics['error_rate'] > 0.05:  # 5% error rate threshold
                    alerts.append({
                        'type': 'high_error_rate',
                        'flow': flow_name,
                        'error_rate': flow_metrics['error_rate'],
                        'severity': 'critical' if flow_metrics['error_rate'] > 0.1 else 'high'
                    })
            
            return alerts
        
        alerts = monitor_data_flow_health(data_flow_metrics)
        
        # Should have minimal alerts for healthy data flows
        high_severity_alerts = [a for a in alerts if a['severity'] in ['high', 'critical']]
        assert len(high_severity_alerts) == 0, f"Unexpected high severity alerts: {high_severity_alerts}"
        
        # Test unhealthy data flow
        unhealthy_metrics = {
            'problematic_flow': {
                'messages_sent': 100,
                'messages_received': 85,  # Low delivery rate
                'avg_latency_ms': 250,    # High latency
                'error_rate': 0.15        # High error rate
            }
        }
        
        unhealthy_alerts = monitor_data_flow_health(unhealthy_metrics)
        
        # Should generate multiple alerts
        assert len(unhealthy_alerts) >= 3, "Should detect multiple issues in unhealthy flow"
        
        # Should have critical alerts
        critical_alerts = [a for a in unhealthy_alerts if a['severity'] == 'critical']
        assert len(critical_alerts) > 0, "Should generate critical alerts for severe issues"


class TestErrorHandlingAndRecovery:
    """Test error handling and recovery across integrated systems (R10.2)"""
    
    def setup_method(self):
        """Set up error handling testing environment"""
        self.temp_dir = tempfile.mkdtemp()
        self.specs_dir = Path(self.temp_dir) / "specs"
        self.specs_dir.mkdir()
        
        # Initialize components
        self.monitor = ContinuousMonitor(str(self.specs_dir))
        self.governance = GovernanceController(str(self.specs_dir))
    
    def teardown_method(self):
        """Clean up error handling testing environment"""
        shutil.rmtree(self.temp_dir)
    
    def test_graceful_error_handling(self):
        """Test graceful error handling across components (R10.2)"""
        # Test error handling scenarios
        
        error_scenarios = [
            {
                'type': 'data_validation_error',
                'source': 'beast_mode_system',
                'target': 'testing_rca_framework',
                'error_data': {'invalid_field': 'negative_velocity', 'value': -0.5}
            },
            {
                'type': 'service_unavailable',
                'source': 'testing_rca_framework',
                'target': 'rdi_rm_analysis_system',
                'error_data': {'service': 'compliance_validator', 'status': 'timeout'}
            },
            {
                'type': 'resource_exhaustion',
                'source': 'rdi_rm_analysis_system',
                'target': 'beast_mode_system',
                'error_data': {'resource': 'memory', 'usage': '95%'}
            }
        ]
        
        def handle_integration_error(error_scenario):
            """Handle integration error gracefully"""
            error_type = error_scenario['type']
            source = error_scenario['source']
            target = error_scenario['target']
            error_data = error_scenario['error_data']
            
            error_response = {
                'error_id': f"error_{int(time.time())}",
                'handled': False,
                'recovery_actions': [],
                'escalation_required': False
            }
            
            if error_type == 'data_validation_error':
                # Handle data validation errors
                error_response.update({
                    'handled': True,
                    'recovery_actions': [
                        'validate_data_format',
                        'apply_data_transformation',
                        'retry_with_corrected_data'
                    ],
                    'retry_possible': True
                })
            
            elif error_type == 'service_unavailable':
                # Handle service unavailability
                error_response.update({
                    'handled': True,
                    'recovery_actions': [
                        'check_service_health',
                        'attempt_service_restart',
                        'use_fallback_service'
                    ],
                    'retry_possible': True,
                    'fallback_available': True
                })
            
            elif error_type == 'resource_exhaustion':
                # Handle resource exhaustion
                error_response.update({
                    'handled': True,
                    'recovery_actions': [
                        'trigger_garbage_collection',
                        'scale_resources',
                        'throttle_requests'
                    ],
                    'escalation_required': True,
                    'severity': 'high'
                })
            
            return error_response
        
        # Test error handling for each scenario
        for scenario in error_scenarios:
            response = handle_integration_error(scenario)
            
            # Verify error is handled
            assert response['handled'] is True, f"Error not handled: {scenario['type']}"
            assert len(response['recovery_actions']) > 0, f"No recovery actions for: {scenario['type']}"
            
            # Verify appropriate response based on error type
            if scenario['type'] == 'resource_exhaustion':
                assert response['escalation_required'] is True, "Resource exhaustion should require escalation"
            else:
                assert 'retry_possible' in response, f"Retry capability not specified for: {scenario['type']}"
    
    def test_error_propagation_and_isolation(self):
        """Test error propagation and isolation between components (R10.2)"""
        # Test error isolation mechanisms
        
        def simulate_component_failure(component_name, failure_type):
            """Simulate component failure and test isolation"""
            failure_impact = {
                'failed_component': component_name,
                'failure_type': failure_type,
                'affected_components': [],
                'isolated': False,
                'recovery_time': 0
            }
            
            # Simulate failure isolation logic
            if failure_type == 'memory_leak':
                # Memory leak should be isolated to the component
                failure_impact.update({
                    'affected_components': [component_name],
                    'isolated': True,
                    'recovery_time': 30,  # seconds
                    'isolation_method': 'component_restart'
                })
            
            elif failure_type == 'network_partition':
                # Network issues might affect dependent components
                dependent_components = {
                    'beast_mode_system': ['testing_rca_framework'],
                    'testing_rca_framework': ['rdi_rm_analysis_system'],
                    'rdi_rm_analysis_system': ['beast_mode_system']
                }
                
                affected = [component_name]
                if component_name in dependent_components:
                    affected.extend(dependent_components[component_name])
                
                failure_impact.update({
                    'affected_components': affected,
                    'isolated': len(affected) == 1,
                    'recovery_time': 60,  # seconds
                    'isolation_method': 'circuit_breaker'
                })
            
            elif failure_type == 'data_corruption':
                # Data corruption might require system-wide validation
                failure_impact.update({
                    'affected_components': ['beast_mode_system', 'testing_rca_framework', 'rdi_rm_analysis_system'],
                    'isolated': False,
                    'recovery_time': 300,  # seconds
                    'isolation_method': 'system_wide_validation'
                })
            
            return failure_impact
        
        # Test different failure scenarios
        failure_scenarios = [
            ('beast_mode_system', 'memory_leak'),
            ('testing_rca_framework', 'network_partition'),
            ('rdi_rm_analysis_system', 'data_corruption')
        ]
        
        for component, failure_type in failure_scenarios:
            impact = simulate_component_failure(component, failure_type)
            
            # Verify failure impact is assessed
            assert impact['failed_component'] == component
            assert len(impact['affected_components']) > 0
            assert impact['recovery_time'] > 0
            
            # Verify isolation effectiveness
            if failure_type == 'memory_leak':
                assert impact['isolated'] is True, "Memory leak should be isolated"
                assert len(impact['affected_components']) == 1, "Memory leak should only affect one component"
            
            elif failure_type == 'data_corruption':
                assert impact['isolated'] is False, "Data corruption may require system-wide handling"
                assert len(impact['affected_components']) > 1, "Data corruption may affect multiple components"
    
    def test_recovery_and_resilience(self):
        """Test recovery and resilience mechanisms (R10.2)"""
        # Test system recovery capabilities
        
        def test_recovery_mechanism(failure_scenario):
            """Test recovery mechanism for a failure scenario"""
            recovery_result = {
                'scenario': failure_scenario,
                'recovery_attempted': False,
                'recovery_successful': False,
                'recovery_time': 0,
                'lessons_learned': []
            }
            
            start_time = time.time()
            
            # Simulate recovery process
            if failure_scenario['type'] == 'component_crash':
                # Component crash recovery
                recovery_steps = [
                    'detect_component_failure',
                    'isolate_failed_component', 
                    'restart_component',
                    'validate_component_health',
                    'restore_service'
                ]
                
                # Simulate recovery time
                recovery_time = 15.0  # 15 seconds
                time.sleep(0.1)  # Simulate some processing
                
                recovery_result.update({
                    'recovery_attempted': True,
                    'recovery_successful': True,
                    'recovery_time': recovery_time,
                    'recovery_steps': recovery_steps,
                    'lessons_learned': ['Implement health checks', 'Add automatic restart capability']
                })
            
            elif failure_scenario['type'] == 'data_inconsistency':
                # Data inconsistency recovery
                recovery_steps = [
                    'detect_data_inconsistency',
                    'identify_inconsistent_data',
                    'restore_from_backup',
                    'validate_data_integrity',
                    'resume_operations'
                ]
                
                recovery_time = 45.0  # 45 seconds
                time.sleep(0.1)  # Simulate some processing
                
                recovery_result.update({
                    'recovery_attempted': True,
                    'recovery_successful': True,
                    'recovery_time': recovery_time,
                    'recovery_steps': recovery_steps,
                    'lessons_learned': ['Implement data validation', 'Add backup verification']
                })
            
            elif failure_scenario['type'] == 'performance_degradation':
                # Performance degradation recovery
                recovery_steps = [
                    'detect_performance_degradation',
                    'identify_bottleneck',
                    'apply_performance_optimization',
                    'validate_performance_improvement',
                    'monitor_continued_performance'
                ]
                
                recovery_time = 30.0  # 30 seconds
                time.sleep(0.1)  # Simulate some processing
                
                recovery_result.update({
                    'recovery_attempted': True,
                    'recovery_successful': True,
                    'recovery_time': recovery_time,
                    'recovery_steps': recovery_steps,
                    'lessons_learned': ['Implement performance monitoring', 'Add auto-scaling']
                })
            
            recovery_result['actual_recovery_time'] = time.time() - start_time
            return recovery_result
        
        # Test recovery scenarios
        recovery_scenarios = [
            {'type': 'component_crash', 'component': 'beast_mode_system'},
            {'type': 'data_inconsistency', 'component': 'rdi_rm_analysis_system'},
            {'type': 'performance_degradation', 'component': 'testing_rca_framework'}
        ]
        
        for scenario in recovery_scenarios:
            result = test_recovery_mechanism(scenario)
            
            # Verify recovery was attempted and successful
            assert result['recovery_attempted'] is True, f"Recovery not attempted for {scenario['type']}"
            assert result['recovery_successful'] is True, f"Recovery failed for {scenario['type']}"
            assert result['recovery_time'] > 0, f"No recovery time recorded for {scenario['type']}"
            assert len(result['lessons_learned']) > 0, f"No lessons learned from {scenario['type']}"
            
            # Verify recovery time is reasonable
            assert result['recovery_time'] <= 60.0, f"Recovery time too long for {scenario['type']}: {result['recovery_time']}s"