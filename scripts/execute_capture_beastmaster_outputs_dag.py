#!/usr/bin/env python3
"""
Execute Capture Beastmaster Outputs DAG

This script executes the capture-beastmaster-outputs DAG following
the systematic development governance principles.
"""

import subprocess
import sys
from pathlib import Path
from datetime import datetime

def execute_dag():
    """Execute the capture-beastmaster-outputs DAG."""
    
    print("🚀 Starting Capture Beastmaster Outputs DAG Execution")
    print(f"📅 Started at: {datetime.now().isoformat()}")
    
    # Use the configurable DAG executor
    dag_executor = "configurable_llm_dag_executor.py"
    spec_path = ".kiro/specs/capture-beastmaster-outputs"
    
    if not Path(dag_executor).exists():
        print(f"❌ DAG executor not found: {dag_executor}")
        return False
    
    try:
        # Execute the DAG
        result = subprocess.run([
            sys.executable, dag_executor,
            "--spec-path", spec_path,
            "--execution-mode", "systematic",
            "--parallel-execution", "true",
            "--output-capture", "true"
        ], capture_output=True, text=True, timeout=14400)  # 4 hour timeout
        
        if result.returncode == 0:
            print("✅ DAG execution completed successfully")
            print(result.stdout)
            return True
        else:
            print("❌ DAG execution failed")
            print(result.stderr)
            return False
            
    except subprocess.TimeoutExpired:
        print("⏰ DAG execution timed out after 4 hours")
        return False
    except Exception as e:
        print(f"💥 DAG execution error: {e}")
        return False

if __name__ == "__main__":
    success = execute_dag()
    sys.exit(0 if success else 1)
