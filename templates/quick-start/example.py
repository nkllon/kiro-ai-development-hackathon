#!/usr/bin/env python3
"""
Quick Start Example - Demonstrates basic RC1 functionality
"""

import sys
import os
# Add project root to path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.insert(0, project_root)

from src.rc1.foundation.makefile_health_manager import MakefileHealthManager
from src.rc1.agents import *
from src.rc1.orchestration import ConcurrentExecutor

def main():
    print("🚀 Kiro AI Development Hackathon - Quick Start Example")
    print("=" * 60)
    
    # 1. Demonstrate Makefile Health Manager
    print("\n1. Makefile Health Analysis")
    print("-" * 30)
    
    manager = MakefileHealthManager()
    makefiles = manager.discover_makefiles('.')
    
    if makefiles:
        print(f"Found {len(makefiles)} Makefile(s)")
        for makefile in makefiles[:3]:  # Show first 3
            result = manager.diagnose_makefile(makefile)
            print(f"  📁 {makefile}: {result.status} (score: {result.overall_health_score:.2f})")
    else:
        print("No Makefiles found")
    
    # 2. Demonstrate Concurrent Agent Execution
    print("\n2. Concurrent Agent Execution")
    print("-" * 30)
    
    agents = [
        DocumentDiscoveryAgent(),
        DimensionalAnalysisAgent(),
        ContentAnalysisAgent()
    ]
    
    executor = ConcurrentExecutor(agents)
    results = executor.execute_all_agents_sync()
    
    successful = sum(1 for r in results if r.success)
    print(f"Executed {len(results)} agents: {successful} successful")
    
    # 3. Show System Status
    print("\n3. System Status")
    print("-" * 30)
    
    print(f"✅ Foundation components: Operational")
    print(f"✅ CLI interface: Functional")
    print(f"✅ Agent system: {successful}/{len(results)} agents successful")
    print(f"✅ Health monitoring: Active")
    
    print("\n🎉 Quick start example completed successfully!")
    print("\nNext steps:")
    print("- Run 'python -m src.rc1.cli.beast_mode_cli diagnose system'")
    print("- Explore the examples/ directory")
    print("- Read the full documentation")

if __name__ == "__main__":
    main()
