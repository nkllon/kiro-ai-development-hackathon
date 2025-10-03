#!/usr/bin/env python3
"""
Patch Script: Fix DAG Executor Hardcoded Prompt Template
Root Cause: configurable_llm_dag_executor.py has hardcoded "SYSTEM ARCHITECTURE WIRING DIAGRAM" 
Fix: Make prompt template dynamic based on loaded DAG configuration
"""

import json
from pathlib import Path
from typing import Dict, Any

def apply_fix(executor_path: str = "configurable_llm_dag_executor.py") -> Dict[str, Any]:
    """Apply the specific fix with detailed logging."""
    
    # Read the current executor file
    with open(executor_path, 'r') as f:
        content = f.read()
    
    # Find the hardcoded prompt template
    old_prompt_start = '''        prompt = f"""
SYSTEM ARCHITECTURE WIRING DIAGRAM IMPLEMENTATION
Task ID: {task_id}
Task: {task_name}
{dependencies_text}
Execution ID: {self.execution_id}
LLM Provider: {self.llm_config.provider.value}

CONTEXT:
You are implementing the System Architecture Wiring Diagram specification.
- Spec Location: .kiro/specs/system-architecture-wiring-diagram/'''
    
    # Create dynamic prompt template
    new_prompt_start = '''        # Get spec name from loaded configuration
        config = load_system_architecture_tasks()
        spec_name = config.get("dag_configuration", {}).get("spec_name", "system-architecture-wiring-diagram")
        spec_title = spec_name.replace("-", " ").title()
        
        prompt = f"""
{spec_title.upper()} IMPLEMENTATION
Task ID: {task_id}
Task: {task_name}
{dependencies_text}
Execution ID: {self.execution_id}
LLM Provider: {self.llm_config.provider.value}

CONTEXT:
You are implementing the {spec_title} specification.
- Spec Location: .kiro/specs/{spec_name}/'''
    
    if old_prompt_start in content:
        # Apply the fix
        new_content = content.replace(old_prompt_start, new_prompt_start)
        
        # Write the fixed file
        with open(executor_path, 'w') as f:
            f.write(new_content)
        
        return {
            "status": "success", 
            "fixes_applied": [
                "Made prompt template dynamic based on DAG configuration",
                "Spec name now read from dag_configuration.spec_name",
                "Spec location path now uses actual spec name",
                "Prompt title now reflects actual specification being implemented"
            ]
        }
    else:
        return {
            "status": "error",
            "message": "Hardcoded prompt template not found - may have been already fixed or changed"
        }

def validate_fix(executor_path: str = "configurable_llm_dag_executor.py") -> Dict[str, Any]:
    """Validate the fix was applied correctly."""
    
    with open(executor_path, 'r') as f:
        content = f.read()
    
    # Check that hardcoded reference is gone
    has_hardcoded = "SYSTEM ARCHITECTURE WIRING DIAGRAM IMPLEMENTATION" in content
    
    # Check that dynamic template is present
    has_dynamic = "spec_name = config.get" in content and "{spec_title.upper()} IMPLEMENTATION" in content
    
    if not has_hardcoded and has_dynamic:
        return {
            "status": "passed",
            "validation_results": {
                "hardcoded_template_removed": True,
                "dynamic_template_added": True,
                "spec_name_extraction": True
            }
        }
    else:
        return {
            "status": "failed",
            "validation_results": {
                "hardcoded_template_removed": not has_hardcoded,
                "dynamic_template_added": has_dynamic,
                "issues": "Fix not properly applied"
            }
        }

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "--validate":
        result = validate_fix()
        print(f"Validation: {result['status']}")
        print(f"Results: {result['validation_results']}")
    else:
        result = apply_fix()
        print(f"Fix: {result['status']}")
        if result['status'] == 'success':
            print("Fixes applied:")
            for fix in result['fixes_applied']:
                print(f"  - {fix}")
        else:
            print(f"Error: {result['message']}")
        
        # Validate the fix
        validation = validate_fix()
        print(f"\nValidation: {validation['status']}")