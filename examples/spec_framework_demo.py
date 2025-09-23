#!/usr/bin/env python3
"""
Spec Mode Framework Demonstration

This script demonstrates the systematic specification-driven development workflow
using the Spec Mode Framework based on RM-DDD proven patterns.
"""

import sys
import os

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from spec_framework.core.specification_engine import SpecificationEngine
from spec_framework.managers.requirements_manager import RequirementsManager
from spec_framework.generators.design_generator import DesignGenerator
from spec_framework.orchestrators.task_orchestrator import TaskOrchestrator
from spec_framework.systems.traceability_system import TraceabilitySystem
from spec_framework.engines.validation_engine import ValidationEngine
from spec_framework.core.models import Priority, SpecificationStatus


def main():
    """Demonstrate the complete Spec Mode Framework workflow."""
    print("🚀 Spec Mode Framework Demonstration")
    print("=" * 50)
    print("Based on RM-DDD proven systematic patterns")
    print()
    
    # Initialize framework components
    print("1. Initializing Framework Components...")
    spec_engine = SpecificationEngine()
    req_manager = RequirementsManager()
    design_generator = DesignGenerator()
    task_orchestrator = TaskOrchestrator()
    traceability_system = TraceabilitySystem()
    validation_engine = ValidationEngine()
    
    # Verify all components are healthy
    components = [
        ("Specification Engine", spec_engine),
        ("Requirements Manager", req_manager),
        ("Design Generator", design_generator),
        ("Task Orchestrator", task_orchestrator),
        ("Traceability System", traceability_system),
        ("Validation Engine", validation_engine)
    ]
    
    for name, component in components:
        health = component.health()
        status = component.status()
        print(f"   ✅ {name}: {status} ({health['status']})")
    
    print()
    
    # Create a specification
    print("2. Creating Specification...")
    spec = spec_engine.create_specification(
        name="User Authentication System",
        description="Systematic user authentication with security and compliance",
        created_by="demo_developer"
    )
    print(f"   📋 Created: {spec.name}")
    print(f"   🆔 ID: {spec.id}")
    print(f"   📊 Status: {spec.status.value}")
    print()
    
    # Add requirements
    print("3. Adding Requirements with EARS Format...")
    
    # Requirement 1: Login functionality
    req1 = req_manager.create_requirement(
        role="user",
        feature="login with username and password",
        benefit="access the system securely",
        business_value="Secure system access reduces security risks",
        priority=Priority.HIGH
    )
    
    req_manager.add_acceptance_criterion(
        req1,
        condition="user provides valid credentials",
        system="the authentication system",
        response="grant access and create session token",
        statement_type="WHEN"
    )
    
    req_manager.add_acceptance_criterion(
        req1,
        condition="user provides invalid credentials",
        system="the authentication system", 
        response="deny access and log the attempt",
        statement_type="WHEN"
    )
    
    spec_engine.add_requirement_to_specification(spec.id, req1)
    
    # Requirement 2: Session management
    req2 = req_manager.create_requirement(
        role="system administrator",
        feature="manage user sessions",
        benefit="maintain system security",
        business_value="Session management prevents unauthorized access",
        priority=Priority.MEDIUM
    )
    
    req_manager.add_acceptance_criterion(
        req2,
        condition="user session expires",
        system="the session manager",
        response="invalidate the session and require re-authentication",
        statement_type="WHEN"
    )
    
    spec_engine.add_requirement_to_specification(spec.id, req2)
    
    print(f"   ✅ Added {len(spec.requirements)} requirements")
    for i, req in enumerate(spec.requirements, 1):
        print(f"      {i}. {req.user_story}")
        print(f"         📝 {len(req.acceptance_criteria)} acceptance criteria")
    print()
    
    # Validate requirements
    print("4. Validating Requirements...")
    validation = validation_engine.validate_specification(spec)
    print(f"   📊 Overall Score: {validation.overall_score:.1f}%")
    print(f"   ✅ Structural: {sum(validation.structural_validation.values())}/{len(validation.structural_validation)} passed")
    print(f"   ✅ Content: {sum(validation.content_validation.values())}/{len(validation.content_validation)} passed")
    
    if validation.validation_warnings:
        print("   ⚠️  Warnings:")
        for warning in validation.validation_warnings:
            print(f"      - {warning}")
    print()
    
    # Generate design
    print("5. Generating Design from Requirements...")
    design = design_generator.generate_design_from_requirements(spec)
    spec.design = design
    spec.status = SpecificationStatus.DESIGN_COMPLETE
    
    print(f"   🏗️  Generated design with {len(design.components)} components")
    for component_name, component_info in design.components.items():
        print(f"      - {component_name}: {component_info.get('description', 'Component')}")
    print()
    
    # Build traceability
    print("6. Building Traceability Matrix...")
    matrix = traceability_system.build_traceability_matrix(spec)
    spec.traceability_matrix = matrix
    
    coverage = matrix.get_requirement_coverage()
    print(f"   🔗 Requirement Coverage: {coverage:.1f}%")
    print(f"   📊 Traceability Links: {len(matrix.requirement_to_design)} req→design")
    print()
    
    # Generate tasks
    print("7. Generating Implementation Tasks...")
    tasks = task_orchestrator.generate_tasks_from_design(spec)
    spec.tasks = tasks
    
    print(f"   📋 Generated {len(tasks)} implementation tasks")
    for i, task in enumerate(tasks, 1):
        print(f"      {i}. {task.title}")
        print(f"         ⏱️  Estimated: {task.estimated_effort}h")
        print(f"         🔗 References: {len(task.requirements_references)} requirements")
    print()
    
    # Final validation
    print("8. Final Validation...")
    final_validation = validation_engine.validate_specification(spec)
    print(f"   📊 Final Score: {final_validation.overall_score:.1f}%")
    total_checks = sum([
        sum(final_validation.structural_validation.values()),
        sum(final_validation.content_validation.values()),
        sum(final_validation.traceability_validation.values())
    ])
    print(f"   ✅ All Validations: {total_checks} checks passed")
    print()
    
    # Generate traceability report
    print("9. Generating Traceability Report...")
    report = traceability_system.generate_traceability_report(spec)
    
    print(f"   📄 Report Generated: {report['generated_at']}")
    print(f"   📊 Summary:")
    print(f"      - Requirements: {report['summary']['total_requirements']}")
    print(f"      - Design Components: {report['summary']['total_design_components']}")
    print(f"      - Tasks: {report['summary']['total_tasks']}")
    print(f"   📈 Coverage Metrics:")
    print(f"      - Requirement Coverage: {report['coverage_metrics']['requirement_coverage']:.1f}%")
    print(f"      - Task Coverage: {report['coverage_metrics']['task_coverage']:.1f}%")
    print()
    
    # Framework metrics
    print("10. Framework Metrics...")
    engine_metrics = spec_engine.metrics()
    print(f"   📊 Specifications: {engine_metrics['specifications_total']}")
    print(f"   📊 Requirements: {engine_metrics['requirements_total']}")
    print(f"   📊 Average Completion: {engine_metrics['average_completion']:.1f}%")
    print(f"   📊 Validation Success: {engine_metrics['validation_success_rate']:.1f}%")
    print()
    
    print("🎉 Spec Mode Framework Demonstration Complete!")
    print("=" * 50)
    print("✅ Systematic specification-driven development workflow executed successfully")
    print("✅ Complete traceability from requirements to implementation tasks")
    print("✅ Comprehensive validation and quality assurance")
    print("✅ Based on RM-DDD proven patterns for systematic superiority")
    print()
    print("Next steps:")
    print("- Execute implementation tasks systematically")
    print("- Maintain traceability throughout development")
    print("- Use validation engine for continuous quality assurance")
    print("- Apply patterns to additional specifications")


if __name__ == "__main__":
    main()