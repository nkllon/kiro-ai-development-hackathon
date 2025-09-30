#!/usr/bin/env python3
"""
Kiro DAG Monitor - Non-blocking Progress Tracking
===============================================

Monitors active Kiro DAG execution without blocking the main session.
"""

import time
import json
import os
from pathlib import Path
from datetime import datetime


def monitor_kiro_dag():
    """Monitor Kiro DAG execution progress."""
    
    print("🔍 KIRO DAG MONITOR STARTED")
    print("=" * 40)
    
    # Find the most recent execution
    logs_dir = Path("logs/kiro-dag")
    if not logs_dir.exists():
        print("❌ No Kiro DAG logs directory found")
        return
    
    # Get most recent execution directory
    execution_dirs = [d for d in logs_dir.iterdir() if d.is_dir()]
    if not execution_dirs:
        print("❌ No execution directories found")
        return
    
    latest_execution = max(execution_dirs, key=lambda d: d.stat().st_mtime)
    execution_id = latest_execution.name
    
    print(f"📋 Monitoring Execution: {execution_id}")
    print(f"📁 Log Directory: {latest_execution}")
    print()
    
    # Monitor for 60 seconds
    start_time = time.time()
    last_task_count = 0
    
    while time.time() - start_time < 60:
        # Count log files (active tasks)
        log_files = list(latest_execution.glob("*.log"))
        current_task_count = len(log_files)
        
        if current_task_count != last_task_count:
            print(f"⏰ {datetime.now().strftime('%H:%M:%S')} - Active Tasks: {current_task_count}")
            
            # Show task details
            for log_file in log_files:
                size = log_file.stat().st_size
                modified = datetime.fromtimestamp(log_file.stat().st_mtime)
                task_name = log_file.stem.split('-')[0]  # Extract task ID
                print(f"   📝 {task_name}: {size} bytes (modified: {modified.strftime('%H:%M:%S')})")
            
            last_task_count = current_task_count
            print()
        
        time.sleep(5)
    
    # Final status
    print("🎯 MONITORING COMPLETE")
    print(f"📊 Final Task Count: {current_task_count}")
    
    # Check for execution report
    report_files = list(Path(".").glob("KIRO_DAG_EXECUTION_REPORT_*.json"))
    if report_files:
        latest_report = max(report_files, key=lambda f: f.stat().st_mtime)
        print(f"📋 Execution Report: {latest_report}")
        
        try:
            with open(latest_report) as f:
                report = json.load(f)
            
            print(f"✅ Completed Tasks: {report.get('completed_tasks', 0)}")
            print(f"❌ Failed Tasks: {report.get('failed_tasks', 0)}")
            print(f"🏃 Running Tasks: {report.get('running_tasks', 0)}")
        except Exception as e:
            print(f"⚠️  Could not read report: {e}")


if __name__ == "__main__":
    monitor_kiro_dag()