#!/usr/bin/env python3
"""
Demo: Automatic Technical Debt Annotation in Executable Patches
==============================================================

This demonstrates how the LLM automatically generates technical debt annotations
when creating executable patch scripts, integrating the two governance systems.
"""

import uuid
from datetime import datetime, timedelta
from typing import Dict, Any

def generate_patch_annotation(
    problem_description: str, 
    component: str, 
    bypass_type: str = "Architecture",
    debt_level: str = None
) -> str:
    """
    Generate technical debt annotation for patch code.
    
    This is the reference implementation for Requirement 8 of the
    executable-patch-code-governance spec.
    """
    
    # Generate unique patch ID
    patch_id = f"PATCH-{datetime.now().year}-{str(uuid.uuid4())[:8].upper()}"
    
    # Auto-assess debt level if not provided
    if not debt_level:
        debt_level = assess_debt_level(bypass_type, component)
    
    # Generate cleanup guidance
    cleanup_guidance = generate_cleanup_guidance(problem_description, component)
    
    # Generate validation criteria
    validation_criteria = generate_validation_criteria(problem_description)
    
    # Calculate expected resolution date (30-90 days based on debt level)
    resolution_days = {"Low": 90, "Medium": 60, "High": 30, "Critical": 14}
    expected_resolution = (datetime.now() + timedelta(days=resolution_days.get(debt_level, 60))).strftime("%Y-%m-%d")
    
    return f'''
    PATCH_START: {patch_id}
    REASON: {problem_description}
    UPSTREAM: {derive_upstream_issue(problem_description)}
    CLEANUP: {cleanup_guidance}
    DEBT_LEVEL: {debt_level}
    EXPECTED_RESOLUTION: {expected_resolution}
    COMPONENT: {component}
    BYPASS_TYPE: {bypass_type}
    VALIDATION: {validation_criteria}
    PATCH_END: {patch_id}
    '''

def assess_debt_level(bypass_type: str, component: str) -> str:
    """Automatically assess debt level based on bypass type and component."""
    
    # Core system components get higher debt levels
    core_components = ["spec_framework", "dag_orchestration", "execution_tracking", "redis"]
    is_core = any(core in component.lower() for core in core_components)
    
    # Bypass type severity mapping
    bypass_severity = {
        "Architecture": "Medium" if not is_core else "High",
        "Security": "High",
        "Performance": "Medium",
        "Integration": "Low" if not is_core else "Medium",
        "Configuration": "Low"
    }
    
    return bypass_severity.get(bypass_type, "Medium")

def generate_cleanup_guidance(problem_description: str, component: str) -> str:
    """Generate specific cleanup guidance based on the problem."""
    
    if "script generator" in problem_description.lower():
        return f"Update {component} to generate real LLM execution by default instead of placeholder methods"
    elif "execution mode" in problem_description.lower():
        return "Implement proper EXECUTION_MODE checking in all generated scripts"
    elif "import" in problem_description.lower():
        return "Fix import dependencies and ensure all required modules are properly imported"
    else:
        return f"Systematically address the root cause in {component} to prevent similar issues"

def generate_validation_criteria(problem_description: str) -> list:
    """Generate comprehensive validation criteria for patch removal."""
    
    criteria = []
    
    if "execution mode" in problem_description.lower():
        criteria.extend([
            "All generated scripts check EXECUTION_MODE environment variable",
            "Both dry-run and full-parallel modes work correctly",
            "LLM execution via kiro CLI is functional"
        ])
    
    if "script generator" in problem_description.lower():
        criteria.extend([
            "TaskScriptGenerator generates real LLM execution methods",
            "No placeholder execution functions in generated scripts",
            "All generated scripts pass validation tests"
        ])
    
    if "import" in problem_description.lower():
        criteria.extend([
            "All required modules are properly imported",
            "No ImportError exceptions during execution",
            "Scripts execute successfully without missing dependencies"
        ])
    
    # Always include general validation criteria
    criteria.extend([
        "Patch removal doesn't break existing functionality",
        "All tests pass after patch removal",
        "No regression in system behavior"
    ])
    
    return criteria

def derive_upstream_issue(problem_description: str) -> str:
    """Derive upstream issue reference from problem description."""
    
    if "execution mode" in problem_description.lower():
        return "ISSUE-EXECUTION-MODE-SUPPORT"
    elif "script generator" in problem_description.lower():
        return "ISSUE-TASK-SCRIPT-GENERATOR-PLACEHOLDERS"
    elif "import" in problem_description.lower():
        return "ISSUE-IMPORT-DEPENDENCIES"
    else:
        return "ISSUE-GENERAL-PATCH"

def demo_annotated_patch_generation():
    """Demonstrate automatic annotation generation for different patch scenarios."""
    
    print("🏷️  Demo: Automatic Technical Debt Annotation Generation")
    print("=" * 60)
    
    # Scenario 1: Execution Mode Fix
    print("\n📋 Scenario 1: Execution Mode Support Fix")
    annotation1 = generate_patch_annotation(
        problem_description="TaskScriptGenerator was generating placeholder execution instead of real LLM calls",
        component="spec_framework.generators.task_script_generator",
        bypass_type="Architecture"
    )
    print(annotation1)
    
    # Scenario 2: Import Dependencies Fix
    print("\n📋 Scenario 2: Import Dependencies Fix")
    annotation2 = generate_patch_annotation(
        problem_description="Generated scripts missing required imports for os and subprocess modules",
        component="spec_framework.generators.task_script_generator",
        bypass_type="Integration"
    )
    print(annotation2)
    
    # Scenario 3: Security Credentials Fix
    print("\n📋 Scenario 3: Security Credentials Fix")
    annotation3 = generate_patch_annotation(
        problem_description="Hardcoded Redis password in execution tracking scripts",
        component="execution_tracking.redis_execution_tracker",
        bypass_type="Security"
    )
    print(annotation3)
    
    print("\n✅ Demo Complete!")
    print("\nKey Benefits:")
    print("- 🤖 Automatic annotation generation by LLM")
    print("- 📊 Consistent debt level assessment")
    print("- 🎯 Specific cleanup guidance")
    print("- ✅ Comprehensive validation criteria")
    print("- 🔗 Integration with technical debt tracking")

if __name__ == "__main__":
    demo_annotated_patch_generation()