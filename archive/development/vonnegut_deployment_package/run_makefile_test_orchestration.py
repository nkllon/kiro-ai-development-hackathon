#!/usr/bin/env python3
"""
Quick Makefile Test Orchestration Runner
========================================

Simplified runner for immediate parallel test creation and execution.
"""

import asyncio
import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

# from scripts.orchestrate_makefile_unit_tests import MakefileTestOrchestrator  # Temporarily disabled due to syntax issues


async def quick_test_creation():
    """Quick test creation for immediate use."""
    print("🚀 Starting Makefile Unit Test Orchestration...")
    
    orchestrator = MakefileTestOrchestrator()
    
    # Just create the tests first
    print("📝 Creating test modules...")
    creation_results = await orchestrator.orchestrate_parallel_test_creation()
    
    print(f"\n✅ Test Creation Results:")
    print(f"   Created: {len(creation_results['created_modules'])} modules")
    print(f"   Failed: {len(creation_results['failed_modules'])} modules")
    
    if creation_results['created_modules']:
        print(f"\n📁 Created Test Files:")
        for module in creation_results['created_modules']:
            print(f"   - {module['test_file']}")
    
    if creation_results['failed_modules']:
        print(f"\n❌ Failed Modules:")
        for module in creation_results['failed_modules']:
            print(f"   - {module['module']}: {module['error']}")
    
    print(f"\n🎯 Next Steps:")
    print(f"   1. Review created test files")
    print(f"   2. Customize test implementations")
    print(f"   3. Run: python scripts/orchestrate_makefile_unit_tests.py")
    
    return creation_results


async def run_existing_tests():
    """Run tests that already exist."""
    print("🧪 Running existing Makefile tests...")
    
    orchestrator = MakefileTestOrchestrator()
    
    # Check which test files exist
    existing_tests = []
    for module in orchestrator.test_modules:
        if module.test_file_path.exists():
            existing_tests.append(module)
    
    if not existing_tests:
        print("❌ No test files found. Run test creation first.")
        return
    
    print(f"Found {len(existing_tests)} existing test files")
    
    # Execute existing tests
    execution_results = await orchestrator.execute_parallel_tests()
    
    print(f"\n📊 Test Execution Results:")
    summary = execution_results['summary']
    print(f"   Success Rate: {summary.get('success_rate', 0):.1f}%")
    print(f"   Total Duration: {summary.get('total_duration', 0):.2f}s")
    print(f"   Test Cases: {summary.get('total_test_count', 0)}")
    
    # Show report
    report = orchestrator.generate_test_report()
    print(f"\n📋 Detailed Report:")
    print(report)
    
    return execution_results


def main():
    """Main entry point with options."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Makefile Test Orchestration")
    parser.add_argument("--create", action="store_true", help="Create test files")
    parser.add_argument("--run", action="store_true", help="Run existing tests")
    parser.add_argument("--full", action="store_true", help="Create and run tests")
    
    args = parser.parse_args()
    
    if args.create or not any([args.run, args.full]):
        # Default to creation
        asyncio.run(quick_test_creation())
    elif args.run:
        asyncio.run(run_existing_tests())
    elif args.full:
        # Use the working orchestrator
        from scripts.orchestrate_makefile_unit_tests import main as full_main
        full_main()


if __name__ == "__main__":
    main()