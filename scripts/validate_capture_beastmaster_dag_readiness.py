#!/usr/bin/env python3
"""
Validate Capture Beastmaster Outputs DAG Readiness

This script validates that all prerequisites are in place for successful DAG execution.
"""

import os
import sys
import json
from pathlib import Path
from datetime import datetime

def validate_beastmaster_logs() -> bool:
    """Validate that beastmaster log files exist and are accessible."""
    
    log_base = Path("logs/beastmaster-dag/beastmaster-20250930-102354")
    expected_logs = [
        "1.4_cloudflare_tunnel_discovery-beastmaster-102354.log",
        "1.5_makefile_analysis_system-beastmaster-102354.log", 
        "1.6_network_topology_discovery-beastmaster-102354.log"
    ]
    
    print("🔍 Validating Beastmaster Log Files:")
    
    if not log_base.exists():
        print(f"❌ Beastmaster log directory not found: {log_base}")
        return False
    
    for log_file in expected_logs:
        log_path = log_base / log_file
        if not log_path.exists():
            print(f"❌ Missing log file: {log_path}")
            return False
        else:
            size = log_path.stat().st_size
            print(f"✅ Found: {log_file} ({size} bytes)")
    
    return True

def validate_specification_files() -> bool:
    """Validate that all specification files are present and complete."""
    
    spec_base = Path(".kiro/specs/capture-beastmaster-outputs")
    required_files = ["requirements.md", "design.md", "tasks.md"]
    
    print("\n📋 Validating Specification Files:")
    
    for file in required_files:
        file_path = spec_base / file
        if not file_path.exists():
            print(f"❌ Missing specification file: {file_path}")
            return False
        else:
            size = file_path.stat().st_size
            print(f"✅ Found: {file} ({size} bytes)")
    
    return True

def validate_dag_specification() -> bool:
    """Validate that DAG specification was created correctly."""
    
    dag_spec_path = Path("logs/dag-specifications/capture-beastmaster-outputs-dag.json")
    
    print("\n🔧 Validating DAG Specification:")
    
    if not dag_spec_path.exists():
        print(f"❌ DAG specification not found: {dag_spec_path}")
        return False
    
    try:
        with open(dag_spec_path, 'r') as f:
            dag_spec = json.load(f)
        
        # Validate required fields
        required_fields = ["dag_id", "tasks", "parallel_groups", "critical_path"]
        for field in required_fields:
            if field not in dag_spec:
                print(f"❌ Missing DAG specification field: {field}")
                return False
        
        # Validate task count
        if len(dag_spec["tasks"]) != 6:
            print(f"❌ Expected 6 tasks, found {len(dag_spec['tasks'])}")
            return False
        
        print(f"✅ DAG specification valid: {len(dag_spec['tasks'])} tasks")
        print(f"✅ Estimated duration: {dag_spec.get('estimated_duration', 'N/A')}")
        
        return True
        
    except json.JSONDecodeError as e:
        print(f"❌ Invalid JSON in DAG specification: {e}")
        return False
    except Exception as e:
        print(f"❌ Error validating DAG specification: {e}")
        return False

def validate_execution_script() -> bool:
    """Validate that execution script exists and is executable."""
    
    script_path = Path("scripts/execute_capture_beastmaster_outputs_dag.py")
    
    print("\n🚀 Validating Execution Script:")
    
    if not script_path.exists():
        print(f"❌ Execution script not found: {script_path}")
        return False
    
    if not os.access(script_path, os.X_OK):
        print(f"⚠️  Execution script not executable: {script_path}")
        # Try to make it executable
        try:
            script_path.chmod(0o755)
            print(f"✅ Made script executable: {script_path}")
        except Exception as e:
            print(f"❌ Failed to make script executable: {e}")
            return False
    else:
        print(f"✅ Execution script ready: {script_path}")
    
    return True

def validate_dependencies() -> bool:
    """Validate that required dependencies and tools are available."""
    
    print("\n🔗 Validating Dependencies:")
    
    # Check for configurable DAG executor
    dag_executor = Path("configurable_llm_dag_executor.py")
    if not dag_executor.exists():
        print(f"❌ DAG executor not found: {dag_executor}")
        return False
    else:
        print(f"✅ DAG executor available: {dag_executor}")
    
    # Check for system architecture spec
    sys_arch_spec = Path(".kiro/specs/system-architecture-wiring-diagram")
    if not sys_arch_spec.exists():
        print(f"⚠️  System architecture spec not found: {sys_arch_spec}")
        print("   This may affect validation but won't block execution")
    else:
        print(f"✅ System architecture spec available: {sys_arch_spec}")
    
    return True

def validate_environment() -> bool:
    """Validate that execution environment is properly set up."""
    
    print("\n🏗️  Validating Execution Environment:")
    
    # Check investigation directory
    investigation_dir = Path("investigation")
    if not investigation_dir.exists():
        print(f"⚠️  Investigation directory not found, creating: {investigation_dir}")
        investigation_dir.mkdir(exist_ok=True)
    print(f"✅ Investigation directory ready: {investigation_dir}")
    
    # Check system architecture directory
    sys_arch_dir = Path("src/system_architecture")
    if not sys_arch_dir.exists():
        print(f"⚠️  System architecture directory not found, creating: {sys_arch_dir}")
        sys_arch_dir.mkdir(parents=True, exist_ok=True)
    print(f"✅ System architecture directory ready: {sys_arch_dir}")
    
    # Check DAG tracking directory
    dag_tracking_dir = Path("logs/dag-execution/capture-beastmaster-outputs")
    if not dag_tracking_dir.exists():
        print(f"⚠️  DAG tracking directory not found, creating: {dag_tracking_dir}")
        dag_tracking_dir.mkdir(parents=True, exist_ok=True)
    print(f"✅ DAG tracking directory ready: {dag_tracking_dir}")
    
    return True

def main():
    """Main validation function."""
    
    print("🔍 Validating Capture Beastmaster Outputs DAG Readiness")
    print(f"📅 Validation started at: {datetime.now().isoformat()}")
    print("=" * 60)
    
    validation_results = []
    
    # Run all validations
    validation_results.append(("Beastmaster Logs", validate_beastmaster_logs()))
    validation_results.append(("Specification Files", validate_specification_files()))
    validation_results.append(("DAG Specification", validate_dag_specification()))
    validation_results.append(("Execution Script", validate_execution_script()))
    validation_results.append(("Dependencies", validate_dependencies()))
    validation_results.append(("Environment", validate_environment()))
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 Validation Summary:")
    
    all_passed = True
    for name, result in validation_results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"   {status}: {name}")
        if not result:
            all_passed = False
    
    print("\n" + "=" * 60)
    
    if all_passed:
        print("🎉 All validations passed! DAG is ready for execution.")
        print("\n🚀 To execute the DAG, run:")
        print("   python scripts/execute_capture_beastmaster_outputs_dag.py")
        return True
    else:
        print("❌ Some validations failed. Please address the issues before execution.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)