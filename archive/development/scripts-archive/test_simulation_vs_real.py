#!/usr/bin/env python3
"""
Minimal test to prove simulation vs real execution issue.
"""

import subprocess
import os
from pathlib import Path

def test_simulation_issue():
    """Test that proves the launch scripts are simulation engines."""
    
    print("🧪 TESTING: Simulation vs Real Execution")
    print("=" * 50)
    
    # Test 1: Check if infrastructure discoverer actually works
    print("\n1. Testing REAL infrastructure discoverer...")
    result = subprocess.run(['python', 'src/system_architecture/discovery/infrastructure_discoverer.py'], 
                          capture_output=True, text=True)
    
    if result.returncode == 0:
        print("   ✅ REAL CODE: Infrastructure discoverer works and creates files")
        # Check if it actually created files
        output_dir = Path("generated_docs/system_architecture")
        files_created = list(output_dir.glob("infrastructure_discovery_*.json"))
        print(f"   📁 Files created: {len(files_created)}")
    else:
        print("   ❌ REAL CODE: Infrastructure discoverer failed")
        print(f"   Error: {result.stderr}")
    
    # Test 2: Check what the launch script actually does
    print("\n2. Testing SIMULATION launch script...")
    
    # Count files before
    before_files = set()
    for pattern in ["generated_docs/**/*", "generated_diagrams/**/*", "src/**/*.py"]:
        before_files.update(Path(".").glob(pattern))
    
    print(f"   📊 Files before launch: {len(before_files)}")
    
    # Run the launch script in critical-path mode (should be fastest)
    result = subprocess.run(['python', 'scripts/system_architecture_launch_v2.py', '--critical-path'], 
                          capture_output=True, text=True)
    
    # Count files after
    after_files = set()
    for pattern in ["generated_docs/**/*", "generated_diagrams/**/*", "src/**/*.py"]:
        after_files.update(Path(".").glob(pattern))
    
    print(f"   📊 Files after launch: {len(after_files)}")
    print(f"   📊 New files created: {len(after_files - before_files)}")
    
    # Check the output for simulation indicators
    if "simulated" in result.stdout.lower() or "simulation" in result.stdout.lower():
        print("   🚨 SIMULATION DETECTED: Launch script contains simulation keywords")
    
    if result.returncode == 0:
        print("   ✅ SIMULATION: Launch script reports success")
        print("   📝 But did it actually create any implementation files?")
        
        new_files = after_files - before_files
        implementation_files = [f for f in new_files if f.suffix == '.py' and 'src/' in str(f)]
        print(f"   🔍 New implementation files: {len(implementation_files)}")
        
        if len(implementation_files) == 0:
            print("   🚨 PROOF: Launch script did NO ACTUAL IMPLEMENTATION")
        else:
            print("   ✅ Launch script created real implementation files")
            for f in implementation_files:
                print(f"      - {f}")
    else:
        print("   ❌ SIMULATION: Launch script failed")
    
    print("\n🎯 CONCLUSION:")
    if len(implementation_files) == 0:
        print("   🚨 CONFIRMED: Launch scripts are SIMULATION ENGINES")
        print("   💡 They generate convincing reports but do no actual work")
        print("   🔧 Need to fix the simulation flag or implement real execution")
    else:
        print("   ✅ Launch scripts appear to do real work")

if __name__ == "__main__":
    test_simulation_issue()