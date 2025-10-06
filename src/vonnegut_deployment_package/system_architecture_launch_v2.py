#!/usr/bin/env python3
"""
Simple launch script for System Architecture Wiring Diagram implementation.
Provides easy access to different execution modes.
Generated using proven spec-creation-dag-compliance patterns v2.0.
"""

import sys
import os
import subprocess
from pathlib import Path
from datetime import datetime

def show_help():
    """Show help information."""
    print("""
🚀 System Architecture Wiring Diagram - Launch Control v2.0

USAGE:
    python scripts/system_architecture_launch_v2.py [MODE] [OPTIONS]

EXECUTION MODES:
    --full-parallel     Full parallel execution (67h, 36% time reduction) [DEFAULT]
    --critical-path     Critical path only (42h, core functionality)
    --sequential        Sequential execution (104h, maximum safety)
    --validate-only     Prelaunch validation only
    --dry-run          Show execution plan without running

EXECUTION OPTIONS:
    --llm=kiro         Use Kiro LLM provider
    --llm=claude       Use Claude LLM provider
    --background       Run in background with logging
    --track            Enable Redis execution tracking

MONITORING:
    --status           Show execution status
    --logs             Show recent log entries
    --stop             Stop background execution

EXAMPLES:
    python scripts/system_architecture_launch_v2.py
    python scripts/system_architecture_launch_v2.py --full-parallel --llm=kiro
    python scripts/system_architecture_launch_v2.py --critical-path --background
    python scripts/system_architecture_launch_v2.py --validate-only
    python scripts/system_architecture_launch_v2.py --status

EXECUTION DETAILS:
    • Total tasks: 26 (22 core + 4 optional testing)
    • Full parallel: 67 hours with 4-way parallelization
    • Critical path: 42 hours through 10 key tasks
    • Sequential: 104 hours (safe mode)
    • Efficiency gain: 36% time reduction with parallel execution

INFRASTRUCTURE:
    • Directus CMS (localhost:8055) - Optional, file-based fallback
    • Redis Coordination (192.168.1.119:6379 + localhost:6380) - Optional
    • Observatory Server (localhost:8888) - Optional, static discovery fallback
    • Prometheus (localhost:9090) - Optional, metrics validation disabled
    • Grafana (localhost:3000) - Optional, dashboard validation disabled

DELIVERABLES:
    • UML Component Diagrams - Complete system architecture
    • Sequence Diagrams - Observatory operational workflows
    • Network Topology Maps - IP allocations, port mappings, routing
    • Use Case Documentation - Step-by-step procedures for 50+ Makefile targets
    • Troubleshooting Guides - Error propagation paths with correlation IDs
    • Security Documentation - Authentication, access control, credential management
    • Disaster Recovery - RTO/RPO requirements, recovery procedures
""")

def main():
    """Main execution function."""
    args = sys.argv[1:]
    
    # Handle help
    if not args or '--help' in args or '-h' in args:
        show_help()
        return
    
    # Parse arguments
    mode = 'full-parallel'  # Default mode
    llm_provider = None
    background = False
    track = True  # Enable tracking by default
    
    # Handle monitoring commands first
    if '--status' in args:
        subprocess.run(['bash', 'scripts/system_architecture_background_launch_v2.sh', '--status'])
        return
    
    if '--logs' in args:
        subprocess.run(['bash', 'scripts/system_architecture_background_launch_v2.sh', '--logs'])
        return
    
    if '--stop' in args:
        subprocess.run(['bash', 'scripts/system_architecture_background_launch_v2.sh', '--stop'])
        return
    
    # Parse execution mode
    if '--full-parallel' in args:
        mode = 'full-parallel'
    elif '--critical-path' in args:
        mode = 'critical-path'
    elif '--sequential' in args:
        mode = 'sequential'
    elif '--validate-only' in args:
        mode = 'validate-only'
    elif '--dry-run' in args:
        mode = 'dry-run'
    
    # Parse options
    for arg in args:
        if arg.startswith('--llm='):
            llm_provider = arg.split('=')[1]
        elif arg == '--background':
            background = True
        elif arg == '--track':
            track = True
        elif arg == '--no-track':
            track = False
    
    # Show execution plan
    print("🚀 System Architecture Wiring Diagram - Launch Execution v2.0")
    print("=" * 70)
    print(f"📋 Execution Mode: {mode}")
    if llm_provider:
        print(f"🤖 LLM Provider: {llm_provider}")
    print(f"📊 Redis Tracking: {'Enabled' if track else 'Disabled'}")
    print(f"🔄 Background Mode: {'Enabled' if background else 'Disabled'}")
    print(f"⏰ Start Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Execute based on mode
    if mode == 'validate-only':
        print("🔍 Running prelaunch validation only...")
        result = subprocess.run(['python3', 'scripts/system_architecture_prelaunch_check_v2.py'])
        sys.exit(result.returncode)
    
    elif mode == 'dry-run':
        print("🔍 Dry run mode - showing execution plan...")
        result = subprocess.run(['bash', 'scripts/system_architecture_background_launch_v2.sh', '--dry-run'])
        sys.exit(result.returncode)
    
    elif background:
        print("🔄 Starting background execution...")
        result = subprocess.run(['bash', 'scripts/system_architecture_background_launch_v2.sh'])
        sys.exit(result.returncode)
    
    else:
        # Direct execution
        print(f"🚀 Starting {mode} execution...")
        
        # Set environment variables
        env = os.environ.copy()
        if llm_provider:
            env['LLM_PROVIDER'] = llm_provider
        if not track:
            env['DISABLE_TRACKING'] = '1'
        env['EXECUTION_MODE'] = mode
        
        # Execute the tracked launch script
        result = subprocess.run(['python3', 'scripts/system_architecture_launch_v2_tracked.py'], env=env)
        
        if result.returncode == 0:
            print("\n🎉 SUCCESS: System Architecture Wiring Diagram execution completed")
            print("📊 Check logs/ directory for detailed execution reports")
            print("📁 Generated artifacts available in generated_docs/ and generated_diagrams/")
        else:
            print("\n💥 EXECUTION FAILED: Check logs for details")
            print("💡 Try running with --validate-only first to check prerequisites")
        
        sys.exit(result.returncode)

if __name__ == "__main__":
    main()