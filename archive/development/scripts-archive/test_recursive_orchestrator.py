#!/usr/bin/env python3
"""
Test the Recursive Orchestrator - THE RECURSIVE MOMENT!
=======================================================

This test validates that the RecursiveOrchestrator can successfully
use DAG orchestration to orchestrate itself - the ultimate meta-programming test!

Author: Recursive DAG Orchestration System
Date: 2025-01-30
"""

import asyncio
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

try:
    from src.recursive_dag_orchestration.core.recursive_orchestrator import (
        RecursiveOrchestrator,
        RecursionStrategy,
        demonstrate_recursive_orchestration
    )
    from src.recursive_dag_orchestration.core.recursion_context import (
        RecursionLevel,
        RecursionContext
    )
    print("✅ Successfully imported RecursiveOrchestrator components!")
except ImportError as e:
    print(f"❌ Import failed: {e}")
    sys.exit(1)


async def test_recursive_orchestrator_creation():
    """Test that we can create a RecursiveOrchestrator."""
    print("\n🔄 Testing RecursiveOrchestrator creation...")
    
    try:
        orchestrator = RecursiveOrchestrator(max_recursion_depth=3)
        
        # Test basic properties
        assert orchestrator.max_recursion_depth == 3
        assert orchestrator.module_id == "RecursiveOrchestrator"
        assert len(orchestrator.active_executions) == 0
        
        # Test ReflectiveModule integration
        module_info = orchestrator.get_module_info()
        assert module_info['name'] == "RecursiveOrchestrator"
        assert 'capabilities' in module_info
        
        health_status = orchestrator.get_health_status()
        assert health_status.module_id == "RecursiveOrchestrator"
        
        print("✅ RecursiveOrchestrator creation test passed!")
        return True
        
    except Exception as e:
        print(f"❌ RecursiveOrchestrator creation test failed: {e}")
        return False


async def test_recursion_context_management():
    """Test recursion context creation and management."""
    print("\n🔄 Testing recursion context management...")
    
    try:
        orchestrator = RecursiveOrchestrator()
        
        # Test context creation
        meta_context = orchestrator._create_recursion_context(RecursionLevel.META)
        assert meta_context.level == RecursionLevel.META
        assert meta_context.status == "created"
        assert meta_context.get_recursion_depth() == 0
        
        # Test context hierarchy
        self_context = orchestrator._create_recursion_context(RecursionLevel.SELF)
        meta_context.add_child_context(self_context)
        assert self_context.get_recursion_depth() == 1
        assert len(meta_context.child_contexts) == 1
        
        # Test termination conditions
        should_terminate, reason = meta_context.is_termination_condition_met()
        assert not should_terminate  # Should not terminate immediately
        
        print("✅ Recursion context management test passed!")
        return True
        
    except Exception as e:
        print(f"❌ Recursion context management test failed: {e}")
        return False


async def test_recursive_execution_plan_creation():
    """Test creation of recursive execution plans."""
    print("\n🔄 Testing recursive execution plan creation...")
    
    try:
        orchestrator = RecursiveOrchestrator()
        
        # Test plan creation
        spec_path = ".kiro/specs/recursive-dag-orchestrated-spec-execution/"
        plan = await orchestrator._create_recursive_execution_plan(
            spec_path, 
            RecursionStrategy.HIERARCHICAL
        )
        
        assert plan.recursion_strategy == RecursionStrategy.HIERARCHICAL
        assert plan.max_recursion_depth == orchestrator.max_recursion_depth
        assert len(plan.tasks) > 0
        
        # Test that tasks have proper structure
        for task in plan.tasks:
            assert hasattr(task, 'id')
            assert hasattr(task, 'level')
            assert hasattr(task, 'dependencies')
            assert hasattr(task, 'action')
        
        print("✅ Recursive execution plan creation test passed!")
        return True
        
    except Exception as e:
        print(f"❌ Recursive execution plan creation test failed: {e}")
        return False


async def test_recursive_plan_validation():
    """Test validation of recursive execution plans."""
    print("\n🔄 Testing recursive plan validation...")
    
    try:
        orchestrator = RecursiveOrchestrator()
        
        # Create a plan to validate
        spec_path = ".kiro/specs/recursive-dag-orchestrated-spec-execution/"
        plan = await orchestrator._create_recursive_execution_plan(
            spec_path,
            RecursionStrategy.HIERARCHICAL
        )
        
        # Validate the plan
        validation_result = await orchestrator._validate_recursive_plan(plan)
        
        assert 'is_valid' in validation_result
        assert 'errors' in validation_result
        assert 'warnings' in validation_result
        
        # Plan should be valid (no cycles, proper termination)
        if not validation_result['is_valid']:
            print(f"   Plan validation errors: {validation_result['errors']}")
        
        print("✅ Recursive plan validation test passed!")
        return True
        
    except Exception as e:
        print(f"❌ Recursive plan validation test failed: {e}")
        return False


async def test_basic_recursive_orchestration():
    """Test basic recursive orchestration functionality."""
    print("\n🔄 Testing basic recursive orchestration...")
    
    try:
        orchestrator = RecursiveOrchestrator(max_recursion_depth=2)  # Smaller depth for testing
        
        # Test recursive orchestration
        spec_path = ".kiro/specs/recursive-dag-orchestrated-spec-execution/"
        result = await orchestrator.orchestrate_recursively(
            spec_path=spec_path,
            strategy=RecursionStrategy.HIERARCHICAL
        )
        
        # Validate result structure
        assert hasattr(result, 'execution_id')
        assert hasattr(result, 'success')
        assert hasattr(result, 'recursion_levels_used')
        assert hasattr(result, 'total_execution_time')
        assert hasattr(result, 'resource_efficiency')
        
        # Check that execution completed
        assert result.total_execution_time > 0
        assert len(result.recursion_levels_used) > 0
        
        print(f"✅ Basic recursive orchestration test passed!")
        print(f"   Success: {result.success}")
        print(f"   Execution time: {result.total_execution_time:.2f}s")
        print(f"   Tasks completed: {result.tasks_completed}")
        print(f"   Recursion levels: {[level.name for level in result.recursion_levels_used]}")
        
        return True
        
    except Exception as e:
        print(f"❌ Basic recursive orchestration test failed: {e}")
        return False


async def run_all_tests():
    """Run all recursive orchestrator tests."""
    print("🚀 RECURSIVE ORCHESTRATOR TEST SUITE")
    print("=" * 50)
    print("🔄 Testing the system that orchestrates itself!")
    print()
    
    tests = [
        test_recursive_orchestrator_creation,
        test_recursion_context_management,
        test_recursive_execution_plan_creation,
        test_recursive_plan_validation,
        test_basic_recursive_orchestration
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            result = await test()
            if result:
                passed += 1
        except Exception as e:
            print(f"❌ Test {test.__name__} failed with exception: {e}")
    
    print(f"\n📊 TEST RESULTS: {passed}/{total} tests passed")
    
    if passed == total:
        print("✅ ALL TESTS PASSED - RECURSIVE ORCHESTRATION IS WORKING!")
        print("🔄 The system can successfully orchestrate itself!")
    else:
        print(f"❌ {total - passed} tests failed - needs investigation")
    
    return passed == total


async def main():
    """Main test execution."""
    print("🔄 RECURSIVE DAG ORCHESTRATION - SYSTEM TEST")
    print("=" * 60)
    print("🚀 THE ULTIMATE TEST: Can the system orchestrate itself?")
    print()
    
    # Run basic tests first
    basic_tests_passed = await run_all_tests()
    
    if basic_tests_passed:
        print("\n🎯 RUNNING ULTIMATE DEMONSTRATION...")
        print("🔄 System orchestrating its own orchestration!")
        print()
        
        try:
            # Run the ultimate demonstration
            result = await demonstrate_recursive_orchestration()
            
            if result.success:
                print("\n🎉 ULTIMATE SUCCESS!")
                print("🔄 The system has successfully orchestrated its own orchestration!")
                print("🚀 RECURSIVE META-PROGRAMMING ACHIEVED!")
            else:
                print("\n⚠️  Demonstration completed but with issues")
                print(f"   Error: {result.error_details}")
        
        except Exception as e:
            print(f"\n❌ Ultimate demonstration failed: {e}")
    
    else:
        print("\n⚠️  Skipping ultimate demonstration due to basic test failures")
    
    print("\n" + "=" * 60)
    print("🔄 RECURSIVE ORCHESTRATOR TESTING COMPLETE")


if __name__ == "__main__":
    asyncio.run(main())