#!/usr/bin/env python3
"""
Run RDI Analysis - Safe Shell Command
====================================

Uses the safe shell command system to run comprehensive RDI analysis.
"""

import sys
sys.path.append('.')

from src.shell_command_fix import safe_shell_command

def run_analysis():
    """Run the comprehensive RDI analysis safely."""
    print("🚨 RUNNING COMPREHENSIVE RDI ANALYSIS")
    print("=" * 50)
    
    # Analysis command
    analysis_command = "python3 comprehensive_rdi_analysis.py"
    
    print(f"Executing: {analysis_command}")
    print()
    
    # Execute safely
    success, stdout, stderr = safe_shell_command(analysis_command)
    
    if success:
        print("✅ RDI ANALYSIS SUCCESSFUL")
        print("=" * 35)
        print(stdout)
        return True
    else:
        print("❌ RDI ANALYSIS FAILED")
        print("=" * 30)
        print(f"STDERR: {stderr}")
        return False

if __name__ == "__main__":
    success = run_analysis()
    sys.exit(0 if success else 1)
