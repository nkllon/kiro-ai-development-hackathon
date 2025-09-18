"""
Integration tests for Spec Mode Framework workflow.

Tests the complete systematic workflow from requirements to implementation.
"""

import pytest
from src.spec_framework.core.specification_engine import SpecificationEngine
from src.spec_framework.managers.requirements_manager import RequirementsManager
from src.spec_framework.generators.design_generator import DesignGenerator
from src.spec_framework.orchestrators.task_orchestrator import TaskOrchestrator
from src.spec_framework.systems.traceability_system import TraceabilitySystem
from src.spec_framework.engines.validation_engine import ValidationEngine
from src.spec_framework.core.models import (
    SpecificationStatus,
    Priority,
    DependencyType
)


class TestSpecFrameworkWorkflow:
    """Test complete specification framework workflow."""
    
    def setup_method(self):
        """Set up test components."""
        self.spec_engine = SpecificationEngine()
        self.req_manager = RequirementsManager()
        self.design_generator = DesignGenerator()
        self.task_orchestrator = TaskOrchestrator()
        self.traceability_system = TraceabilitySystem()
        self.validation_engine = ValidationEngine()
    
    def test_complete_specification_workflow(self):
        """Test complete workflow from requirements to tasks."""
        # 1. Create specification
        spec = self.spec_engine.create_specification(
            name="User Authentication System",
            description="Systematic user authentication with security",
            created_by="test_developer"
        )
        
        assert spec.name == "User Authentication System"
        assert spec.status == SpecificationStatus.DRAFT
        
        # 2. Add requirements using requirements manager
        req1 = self.req_manager.create_requirement(
            role="user",
            feature="login with username and password",
            benefit="access the system securely",
            business_value="Secure system access",
            priority=Priority.HIGH
        )
        
        # Add acceptance criteria
        success = self.req_manager.add_acceptance_criterion(
            req1,
            condition="user provides valid credentials",
            system="the authentication system",
            response="grant access and create session",
            statement_type="WHEN"
        )
        assert success
        
        # Add requirement to specification
        success = self.spec_engine.add_requirement_to_specification(spec.id, req1)
        assert success
        
        # 3. Validate requirements phase
        validation = self.validation_engine.validate_specification(spec)
        assert validation.overall_score > 50.0  # Should be reasonable quality for requirements phase
        
        # Check that core validations pass
        assert validation.structural_validation['has_minimum_requirements']
        assert validation.content_validation['all_requirements_are_complete']
        
        # 4. Generate design
        design = self.design_generator.generate_design_from_requirements(spec)
        spec.design = design
        
        assert design.overview
        assert design.architecture
        assert len(design.components) > 0
        
        # Progress to design phase
        spec.status = SpecificationStatus.DESIGN_COMPLETE
        
        # 5. Build traceability matrix
        matrix = self.traceability_system.build_traceability_matrix(spec)
        spec.traceability_matrix = matrix
        
        # 6. Generate tasks
        tasks = self.task_orchestrator.generate_tasks_from_design(spec)
        spec.tasks = tasks
        
        assert len(tasks) > 0
        assert all(task.requirements_references for task in tasks)
        
        # 7. Final validation
        final_validation = self.validation_engine.validate_specification(spec)
        assert final_validation.overall_score > 60.0  # More realistic for complete workflow
        
        # 8. Generate traceability report
        report = self.traceability_system.generate_traceability_report(spec)
        assert report['specification_name'] == "User Authentication System"
        assert report['summary']['total_requirements'] == 1
        assert report['summary']['total_tasks'] > 0
    
    def test_multi_specification_dependencies(self):
        """Test handling of dependencies between specifications."""
        # Create two related specifications
        auth_spec = self.spec_engine.create_specification(
            name="Authentication Service",
            description="Core authentication functionality"
        )
        
        user_spec = self.spec_engine.create_specification(
            name="User Management",
            description="User profile management"
        )
        
        # Add dependency
        success = self.spec_engine.add_specification_dependency(
            user_spec.id,
            auth_spec.id,
            DependencyType.REQUIRES,
            "User management requires authentication"
        )
        assert success
        
        # Verify dependency was added
        user_spec_retrieved = self.spec_engine.get_specification(user_spec.id)
        assert len(user_spec_retrieved.dependencies) == 1
        assert user_spec_retrieved.dependencies[0].dependency_spec == auth_spec.id
        assert user_spec_retrieved.dependencies[0].dependency_type == DependencyType.REQUIRES
    
    def test_requirement_quality_validation(self):
        """Test requirement quality validation."""
        # Create high-quality requirement
        good_req = self.req_manager.create_requirement(
            role="administrator",
            feature="manage user accounts",
            benefit="maintain system security",
            business_value="Secure user management"
        )
        
        self.req_manager.add_acceptance_criterion(
            good_req,
            condition="administrator creates new user account",
            system="the user management system",
            response="create account with proper permissions"
        )
        
        # Validate requirement quality
        quality_results = self.validation_engine.validate_requirement_quality(good_req)
        assert quality_results['is_high_quality']
        assert quality_results['has_complete_user_story']
        assert quality_results['has_acceptance_criteria']
        assert quality_results['all_criteria_testable']
    
    def test_cross_spec_impact_analysis(self):
        """Test cross-specification impact analysis."""
        # Create specifications with dependency
        spec1 = self.spec_engine.create_specification(name="Core Service")
        spec2 = self.spec_engine.create_specification(name="Dependent Service")
        
        self.spec_engine.add_specification_dependency(
            spec2.id, spec1.id, DependencyType.REQUIRES
        )
        
        # Create a change in spec1
        from src.spec_framework.core.models import SpecificationChange
        change = SpecificationChange(
            specification_id=spec1.id,
            change_type="requirement_modified",
            description="Modified core requirement"
        )
        
        # Analyze impact
        impact = self.spec_engine.analyze_cross_spec_impact(change)
        assert spec2.id in impact.impacted_specs
        assert len(impact.recommended_actions) > 0
    
    def test_framework_health_monitoring(self):
        """Test health monitoring of all framework components."""
        # Check health of all components
        components = [
            self.spec_engine,
            self.req_manager,
            self.design_generator,
            self.task_orchestrator,
            self.traceability_system,
            self.validation_engine
        ]
        
        for component in components:
            health = component.health()
            assert health['status'] == 'healthy'
            assert component.ready()
            
            metrics = component.metrics()
            assert isinstance(metrics, dict)
            
            status = component.status()
            assert status in ['ready', 'active', 'initializing']