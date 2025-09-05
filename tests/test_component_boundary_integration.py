"""
Integration tests for Component Boundary Resolution - Task 5.2

Tests the complete component boundary resolution workflow to ensure all
requirements are met and the system works end-to-end.
"""

import pytest
from pathlib import Path
import tempfile
import shutil

from src.spec_reconciliation.boundary_resolver import (
    ComponentBoundaryResolver, ComponentBoundary, InterfaceContract, 
    DependencyRelationship, BoundaryViolationType, ComponentType,
    ComponentBoundaryResolution
)


class TestComponentBoundaryIntegration:
    """Integration tests for complete component boundary resolution"""
    
    def setup_method(self):
        """Set up test environment"""
        self.temp_dir = tempfile.mkdtemp()
        self.specs_dir = Path(self.temp_dir) / "specs"
        self.specs_dir.mkdir(parents=True)
        
        # Create test resolver
        self.resolver = ComponentBoundaryResolver(str(self.specs_dir))
    
    def teardown_method(self):
        """Clean up test environment"""
        shutil.rmtree(self.temp_dir)
    
    def test_complete_boundary_resolution_workflow(self):
        """Test the complete boundary resolution workflow end-to-end"""
        # Test data - consolidated specs from the analysis
        consolidated_specs = [
            "unified_beast_mode_system",
            "unified_testing_rca_framework", 
            "unified_rdi_rm_analysis_system"
        ]
        
        # Execute complete boundary resolution
        resolution = self.resolver.resolve_component_boundaries(consolidated_specs)
        
        # Verify resolution structure
        assert isinstance(resolution, ComponentBoundaryResolution)
        assert resolution.resolution_id.startswith("boundary_resolution_")
        
        # Verify component boundaries
        assert len(resolution.component_boundaries) == 3
        component_names = [b.component_name for b in resolution.component_boundaries]
        assert "unified_beast_mode_system" in component_names
        assert "unified_testing_rca_framework" in component_names
        assert "unified_rdi_rm_analysis_system" in component_names
        
        # Verify interface contracts
        assert len(resolution.interface_contracts) >= 3  # At least one per component
        
        # Verify dependency graph
        assert len(resolution.dependency_graph) == 3
        total_dependencies = sum(len(deps) for deps in resolution.dependency_graph.values())
        assert total_dependencies > 0  # Should have dependencies
        
        # Verify no boundary violations
        assert len(resolution.boundary_violations) == 0
        
        # Verify validation results
        assert resolution.validation_results['overall_valid'] is True
        assert resolution.validation_results['boundary_separation'] is True
        assert resolution.validation_results['interface_compliance'] is True
        assert resolution.validation_results['dependency_rules'] is True
        
        # Verify integration test plan
        assert resolution.integration_test_plan is not None
        assert 'boundary_tests' in resolution.integration_test_plan
        assert 'contract_tests' in resolution.integration_test_plan
    
    def test_requirement_r3_1_component_boundaries_clearly_defined(self):
        """Test R3.1: Each component SHALL have clearly defined responsibilities and boundaries"""
        consolidated_specs = ["unified_beast_mode_system", "unified_testing_rca_framework"]
        
        boundaries = self.resolver.define_component_boundaries(consolidated_specs)
        
        # Each component should have clearly defined responsibilities
        for boundary in boundaries:
            assert len(boundary.primary_responsibilities) > 0
            assert len(boundary.boundary_constraints) > 0
            assert boundary.component_type in ComponentType
            
            # Responsibilities should be specific and non-empty
            for responsibility in boundary.primary_responsibilities:
                assert isinstance(responsibility, str)
                assert len(responsibility.strip()) > 0
            
            # Constraints should define what component MUST NOT do
            for constraint in boundary.boundary_constraints:
                assert isinstance(constraint, str)
                assert len(constraint.strip()) > 0
    
    def test_requirement_r3_2_interfaces_explicitly_defined(self):
        """Test R3.2: Interfaces SHALL be explicitly defined with clear contracts"""
        consolidated_specs = ["unified_beast_mode_system", "unified_testing_rca_framework"]
        
        boundaries = self.resolver.define_component_boundaries(consolidated_specs)
        contracts = self.resolver.create_interface_contracts(boundaries)
        
        # Each interface contract should be explicit and complete
        for contract in contracts:
            assert isinstance(contract, InterfaceContract)
            assert len(contract.interface_name) > 0
            assert len(contract.provider_component) > 0
            assert len(contract.methods) > 0
            assert len(contract.data_contracts) > 0
            
            # Methods should have clear signatures
            for method in contract.methods:
                assert 'name' in method
                assert 'parameters' in method
                assert 'return_type' in method
                assert 'description' in method
            
            # Data contracts should define structure
            for data_contract in contract.data_contracts:
                assert 'name' in data_contract
                assert 'fields' in data_contract
                assert 'validation' in data_contract
            
            # SLAs should be defined
            assert 'availability' in contract.service_level_agreements
            assert 'response_time' in contract.service_level_agreements
            assert 'throughput' in contract.service_level_agreements
    
    def test_requirement_r3_3_functional_overlap_consolidated(self):
        """Test R3.3: Functional overlap SHALL be consolidated into single components"""
        consolidated_specs = [
            "unified_beast_mode_system",
            "unified_testing_rca_framework", 
            "unified_rdi_rm_analysis_system"
        ]
        
        boundaries = self.resolver.define_component_boundaries(consolidated_specs)
        
        # Check for overlapping responsibilities
        all_responsibilities = []
        for boundary in boundaries:
            all_responsibilities.extend(boundary.primary_responsibilities)
        
        # Should not have duplicate responsibilities
        unique_responsibilities = set(all_responsibilities)
        assert len(unique_responsibilities) == len(all_responsibilities), \
            "Found overlapping responsibilities between components"
        
        # Each component should have distinct focus areas
        beast_mode_responsibilities = next(
            b.primary_responsibilities for b in boundaries 
            if b.component_name == "unified_beast_mode_system"
        )
        testing_rca_responsibilities = next(
            b.primary_responsibilities for b in boundaries 
            if b.component_name == "unified_testing_rca_framework"
        )
        
        # Beast Mode should not have testing/RCA responsibilities
        beast_mode_text = " ".join(beast_mode_responsibilities).lower()
        assert "rca" not in beast_mode_text or "root cause" not in beast_mode_text
        
        # Testing/RCA should not have beast mode responsibilities  
        testing_text = " ".join(testing_rca_responsibilities).lower()
        assert "beast mode" not in testing_text or "pdca" not in testing_text
    
    def test_requirement_r3_4_dependencies_explicitly_documented(self):
        """Test R3.4: Dependencies SHALL be explicitly documented and justified"""
        consolidated_specs = [
            "unified_beast_mode_system",
            "unified_testing_rca_framework", 
            "unified_rdi_rm_analysis_system"
        ]
        
        boundaries = self.resolver.define_component_boundaries(consolidated_specs)
        contracts = self.resolver.create_interface_contracts(boundaries)
        dependency_graph = self.resolver.implement_dependency_management(boundaries, contracts)
        
        # Each dependency should be explicitly documented
        for component, dependencies in dependency_graph.items():
            for dependency in dependencies:
                assert isinstance(dependency, DependencyRelationship)
                assert len(dependency.dependent_component) > 0
                assert len(dependency.dependency_component) > 0
                assert dependency.dependency_type in ["interface", "service", "data"]
                assert dependency.validation_status == "valid"
                
                # Dependency should be in allowed list
                boundary = next(b for b in boundaries if b.component_name == component)
                assert dependency.dependency_component in boundary.allowed_dependencies
        
        # Should detect circular dependencies
        circular_deps = self.resolver._detect_circular_dependencies(dependency_graph)
        assert len(circular_deps) == 0, f"Found circular dependencies: {circular_deps}"
    
    def test_requirement_r3_5_boundaries_clarified_through_validation(self):
        """Test R3.5: Boundaries SHALL be clarified through architectural decision records"""
        consolidated_specs = [
            "unified_beast_mode_system",
            "unified_testing_rca_framework", 
            "unified_rdi_rm_analysis_system"
        ]
        
        boundaries = self.resolver.define_component_boundaries(consolidated_specs)
        contracts = self.resolver.create_interface_contracts(boundaries)
        dependency_graph = self.resolver.implement_dependency_management(boundaries, contracts)
        
        # Validate boundaries through comprehensive testing
        validation_results = self.resolver.validate_component_boundaries(
            boundaries, contracts, dependency_graph
        )
        
        # All validation checks should pass
        assert validation_results['boundary_separation'] is True
        assert validation_results['interface_compliance'] is True
        assert validation_results['dependency_rules'] is True
        assert validation_results['contract_adherence'] is True
        assert validation_results['integration_test_plan'] is True
        assert validation_results['overall_valid'] is True
        
        # Integration test plan should be generated
        test_plan = self.resolver._generate_integration_test_plan(boundaries, contracts)
        assert 'boundary_tests' in test_plan
        assert 'contract_tests' in test_plan
        assert len(test_plan['boundary_tests']) == len(boundaries)
        assert len(test_plan['contract_tests']) == len(contracts)
    
    def test_boundary_violation_detection_and_remediation(self):
        """Test that boundary violations are detected and remediation is provided"""
        consolidated_specs = [
            "unified_beast_mode_system",
            "unified_testing_rca_framework"
        ]
        
        resolution = self.resolver.resolve_component_boundaries(consolidated_specs)
        
        # Should detect any violations
        violations = resolution.boundary_violations
        
        # For well-defined boundaries, should have no violations
        assert len(violations) == 0
        
        # If violations exist, they should have remediation steps
        for violation in violations:
            assert violation.violation_type in BoundaryViolationType
            assert len(violation.description) > 0
            assert violation.severity in ["low", "medium", "high", "critical"]
            assert len(violation.remediation_steps) > 0
    
    def test_integration_test_plan_completeness(self):
        """Test that integration test plan covers all boundary aspects"""
        consolidated_specs = [
            "unified_beast_mode_system",
            "unified_testing_rca_framework", 
            "unified_rdi_rm_analysis_system"
        ]
        
        resolution = self.resolver.resolve_component_boundaries(consolidated_specs)
        test_plan = resolution.integration_test_plan
        
        # Should have tests for each component boundary
        assert len(test_plan['boundary_tests']) == len(resolution.component_boundaries)
        
        # Should have tests for each interface contract
        assert len(test_plan['contract_tests']) == len(resolution.interface_contracts)
        
        # Each boundary test should cover key aspects
        for boundary_test in test_plan['boundary_tests']:
            assert 'component' in boundary_test
            assert 'test_name' in boundary_test
            assert 'test_cases' in boundary_test
            
            # Should test constraint compliance
            test_cases = boundary_test['test_cases']
            assert any('constraint' in case.lower() for case in test_cases)
            assert any('interface' in case.lower() for case in test_cases)
            assert any('dependencies' in case.lower() for case in test_cases)
        
        # Each contract test should validate contract adherence
        for contract_test in test_plan['contract_tests']:
            assert 'contract' in contract_test
            assert 'test_name' in contract_test
            assert 'test_cases' in contract_test
            
            test_cases = contract_test['test_cases']
            assert any('method' in case.lower() for case in test_cases)
            assert any('data' in case.lower() for case in test_cases)
            assert any('sla' in case.lower() or 'service' in case.lower() for case in test_cases)
    
    def test_shared_service_integration(self):
        """Test that shared services are properly integrated across components"""
        consolidated_specs = [
            "unified_beast_mode_system",
            "unified_testing_rca_framework", 
            "unified_rdi_rm_analysis_system"
        ]
        
        resolution = self.resolver.resolve_component_boundaries(consolidated_specs)
        
        # Find shared service contracts
        shared_service_contracts = [
            c for c in resolution.interface_contracts 
            if len(c.consumer_components) > 1
        ]
        
        # Should have shared services
        assert len(shared_service_contracts) > 0
        
        # Shared services should have multiple consumers
        for contract in shared_service_contracts:
            assert len(contract.consumer_components) >= 2
            
            # Should have higher SLA requirements
            availability = contract.service_level_agreements.get('availability', '0%')
            assert '99.99%' in availability  # Shared services need higher availability
    
    def test_component_type_classification(self):
        """Test that components are properly classified by type"""
        consolidated_specs = [
            "unified_beast_mode_system",
            "unified_testing_rca_framework", 
            "unified_rdi_rm_analysis_system"
        ]
        
        boundaries = self.resolver.define_component_boundaries(consolidated_specs)
        
        # Main components should be CORE_COMPONENT type
        for boundary in boundaries:
            if boundary.component_name in consolidated_specs:
                assert boundary.component_type == ComponentType.CORE_COMPONENT
        
        # Should have different component types in the system
        all_types = set(b.component_type for b in boundaries)
        assert ComponentType.CORE_COMPONENT in all_types