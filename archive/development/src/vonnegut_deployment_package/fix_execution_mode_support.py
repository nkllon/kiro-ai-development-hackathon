#!/usr/bin/env python3
"""
Patch Script: Fix Execution Mode Support in Generated Launch Scripts
===================================================================

This script demonstrates the exact fix needed for Requirement 32 & 33.
It can be run to apply the fix or used as reference implementation.

Root Cause: TaskScriptGenerator generates placeholder execution instead of 
real LLM execution with EXECUTION_MODE support.

Fix: Add execution mode checking and LLM execution via kiro CLI.
"""

import os
import sys
from pathlib import Path
from typing import Dict, List, Any

def apply_execution_mode_fix(script_path: str) -> Dict[str, Any]:
    """
    Apply execution mode fix to a generated launch script.
    
    This is the reference implementation for Requirements 32 & 33.
    """
    script_file = Path(script_path)
    if not script_file.exists():
        return {"status": "error", "message": f"Script not found: {script_path}"}
    
    # Read current content
    content = script_file.read_text()
    
    # Fix 1: Add missing imports
    if "import os" not in content:
        content = content.replace(
            "import sys\nimport asyncio",
            "import sys\nimport os\nimport asyncio\nimport subprocess"
        )
    
    # Fix 2: Add LLM execution method with technical debt annotation
    llm_execution_method = '''
    async def _execute_task_via_llm(self, task_definition):
        """
        Execute task via LLM using kiro CLI pattern.
        
        PATCH_START: PATCH-2025-001
        REASON: TaskScriptGenerator was generating placeholder execution instead of real LLM calls
        UPSTREAM: ISSUE-EXECUTION-MODE-SUPPORT
        CLEANUP: Update TaskScriptGenerator to generate real LLM execution by default
        DEBT_LEVEL: Medium
        EXPECTED_RESOLUTION: 2025-01-15
        COMPONENT: spec_framework.generators.task_script_generator
        BYPASS_TYPE: Architecture
        VALIDATION: ["All generated scripts use _execute_task_via_llm", "EXECUTION_MODE properly checked", "Kiro CLI integration working"]
        PATCH_END: PATCH-2025-001
        """
        import subprocess
        import os
        from datetime import datetime
        
        # Create task prompt
        task_prompt = f"""
Task: {task_definition.name}
Task ID: {task_definition.task_id}
Dependencies: {task_definition.dependencies}

Please implement this task according to the specification.
Refer to the requirements and design documents for context.
"""
        
        # Create log filename
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        log_file = f"logs/task_{task_definition.task_id}_{timestamp}.log"
        
        # Ensure logs directory exists
        os.makedirs("logs", exist_ok=True)
        
        try:
            # Execute via kiro CLI using the golden pattern
            result = subprocess.run([
                'bash', '-c', 
                f'echo "{task_prompt}" | tee {log_file} | kiro -'
            ], capture_output=True, text=True, timeout=300)
            
            return {
                'status': 'completed' if result.returncode == 0 else 'failed',
                'message': f'LLM execution completed via kiro CLI',
                'output': result.stdout,
                'log_file': log_file,
                'execution_method': 'llm_via_kiro_cli'
            }
        except subprocess.TimeoutExpired:
            return {
                'status': 'failed',
                'message': 'LLM execution timed out after 5 minutes',
                'log_file': log_file,
                'execution_method': 'llm_via_kiro_cli'
            }
        except Exception as e:
            return {
                'status': 'failed',
                'message': f'LLM execution failed: {str(e)}',
                'log_file': log_file,
                'execution_method': 'llm_via_kiro_cli'
            }'''
    
    # Add the method before the main execution
    if "_execute_task_via_llm" not in content:
        content = content.replace(
            "    async def _execute_task_placeholder",
            llm_execution_method + "\n\n    async def _execute_task_placeholder"
        )
    
    # Fix 3: Add execution mode checking
    execution_mode_check = '''            # Check execution mode
            execution_mode = os.getenv('EXECUTION_MODE', 'full-parallel')
            
            if execution_mode == 'dry-run':
                print("  [DRY RUN] Simulating task execution...")
                group_results = await self.execution_engine.execute_dag_parallel(group_1_tasks)
                execution_results.extend(list(group_results.values()))
            else:
                print("  🤖 Executing tasks via LLM...")
                # Real execution via LLM
                for task in group_1_tasks:
                    result = await self._execute_task_via_llm(task)
                    execution_results.append(result)
                    print(f"    ✅ {task.task_id}: {result['status']} ({result['execution_method']})")'''
    
    # Replace the execution logic
    if "Check execution mode" not in content:
        content = content.replace(
            "            group_results = await self.execution_engine.execute_dag_parallel(group_1_tasks)\n            execution_results.extend(list(group_results.values()))",
            execution_mode_check
        )
    
    # Write the fixed content
    script_file.write_text(content)
    
    return {
        "status": "success",
        "message": f"Applied execution mode fix to {script_path}",
        "fixes_applied": [
            "Added missing imports (os, subprocess)",
            "Added _execute_task_via_llm method with kiro CLI integration",
            "Added EXECUTION_MODE environment variable checking",
            "Added real LLM execution path with proper error handling"
        ]
    }

def fix_task_script_generator() -> Dict[str, Any]:
    """
    Fix the TaskScriptGenerator to generate LLM execution instead of placeholders.
    
    This is the reference implementation for Requirement 33.
    """
    generator_path = Path("src/spec_framework/generators/task_script_generator.py")
    if not generator_path.exists():
        return {"status": "error", "message": "TaskScriptGenerator not found"}
    
    content = generator_path.read_text()
    
    # Fix: Change placeholder to LLM execution
    if "execution_function=self._execute_task_placeholder" in content:
        content = content.replace(
            "execution_function=self._execute_task_placeholder",
            "execution_function=self._execute_task_via_llm"
        )
        
        generator_path.write_text(content)
        
        return {
            "status": "success",
            "message": "Fixed TaskScriptGenerator to use LLM execution",
            "fix_applied": "Changed execution_function from placeholder to _execute_task_via_llm"
        }
    
    return {
        "status": "no_change",
        "message": "TaskScriptGenerator already uses LLM execution"
    }

def validate_fix(script_path: str) -> Dict[str, Any]:
    """
    Validate that the execution mode fix has been properly applied.
    
    This demonstrates the validation criteria for Requirements 32 & 33.
    """
    script_file = Path(script_path)
    if not script_file.exists():
        return {"status": "error", "message": f"Script not found: {script_path}"}
    
    content = script_file.read_text()
    
    validation_results = {
        "imports_fixed": "import os" in content and "import subprocess" in content,
        "llm_method_added": "_execute_task_via_llm" in content,
        "execution_mode_check": "os.getenv('EXECUTION_MODE'" in content,
        "kiro_cli_integration": "kiro -" in content,
        "error_handling": "TimeoutExpired" in content and "try:" in content,
        "logging_support": "logs/" in content and "tee" in content
    }
    
    all_passed = all(validation_results.values())
    
    return {
        "status": "passed" if all_passed else "failed",
        "validation_results": validation_results,
        "message": "All fixes validated" if all_passed else "Some fixes missing"
    }

if __name__ == "__main__":
    print("🔧 Execution Mode Fix Script")
    print("=" * 50)
    
    if len(sys.argv) < 2:
        print("Usage: python fix_execution_mode_support.py <script_path>")
        print("   or: python fix_execution_mode_support.py --fix-generator")
        print("   or: python fix_execution_mode_support.py --validate <script_path>")
        sys.exit(1)
    
    if sys.argv[1] == "--fix-generator":
        result = fix_task_script_generator()
        print(f"Generator Fix: {result}")
    elif sys.argv[1] == "--validate":
        if len(sys.argv) < 3:
            print("Error: --validate requires script path")
            sys.exit(1)
        result = validate_fix(sys.argv[2])
        print(f"Validation: {result}")
    else:
        script_path = sys.argv[1]
        result = apply_execution_mode_fix(script_path)
        print(f"Script Fix: {result}")
        
        # Also validate the fix
        validation = validate_fix(script_path)
        print(f"Validation: {validation}")