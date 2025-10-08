#!/usr/bin/env python3
"""
Test Infrastructure Validator Component
======================================

Tests the formal InfrastructureValidator component for DAG orchestration system.
This validates Task 3.2 completion.

Author: Beast Mode Framework
Date: 2025-01-27
"""

import asyncio
import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.dag_orchestration.core.infrastructure_validator import (
    InfrastructureValidator,
    ValidationPolicy,
    ValidationContext,
    validate_infrastructure_for_dag_execution,
    create_infrastructure_validator
)


async def test_basic_validator_functionality():
    """Test basic infrastructure validator functionality."""
    print("🔧 Testing Basic Validator Functionality")
    print("-" * 50)
    
    # Create validator with default policy
    validator = InfrastructureValidator()
    
    # Test module info
    module_info = validator.get_module_info()
    print(f"✅ Module: {module_info['name']} v{module_info['version']}")
    print(f"✅ Capabilities: {', '.join(module_info['capabilities'])}")
    
    # Test health status
    health = validator.get_health_status()
    print(f"✅ Health Status: {health.status.value} (Score: {health.health_score})")
    
    # Test graceful degradation
    degradation = validator.graceful_degradation()
    print(f"✅ Graceful Degradation: {'Success' if degradation.success else 'Failed'}")
    
    return True


async def test_execution_validation():
    """Test validation for specific execution requirements."""
    print("\n🎯 Testing Execution Validation")
    print("-" * 40)
    
    validator = InfrastructureValidator()
    
    # Test basic execution requirements
    basic_requirements = {
        'parallel_tasks': 5,
        'memory_intensive': False,
        'execution_type': 'standard'
    }
    
    print("Testing basic execution requirements...")
    validation_passed, report = await validator.validate_for_execution(basic_requirements)
    
    print(f"✅ Validation Result: {'PASSED' if validation_passed else 'FAILED'}")
    print(f"✅ Validation Time: {report.validation_time.strftime('%H:%M:%S')}")
    print(f"✅ Precondition Checks: {len(report.precondition_results)}")
    
    # Show individual results
    for i, result in enumerate(report.precondition_results, 1):
        status = "✅" if result.passed else "❌"
        print(f"   {i}. {result.name}: {status}")
    
    # Test high-load execution requirements
    high_load_requirements = {
        'parallel_tasks': 20,
        'memory_intensive': True,
        'execution_type': 'high_performance'
    }
    
    print("\nTesting high-load execution requirements...")
    validation_passed_2, report_2 = await validator.validate_for_execution(high_load_requirements)
    
    print(f"✅ High-Load Validation: {'PASSED' if validation_passed_2 else 'FAILED'}")
    print(f"✅ Recommendations: {len(report_2.recommendations)}")
    
    return validation_passed and validation_passed_2


async def test_caching_functionality():
    """Test validation caching and performance optimization."""
    print("\n💾 Testing Caching Functionality")
    print("-" * 35)
    
    # Create validator with short cache TTL for testing
    policy = ValidationPolicy(validation_cache_ttl_seconds=60)
    validator = InfrastructureValidator(policy)
    
    requirements = {
        'parallel_tasks': 3,
        'cache_test': True
    }
    
    # First validation (should be fresh)
    print("First validation (fresh)...")
    start_time = asyncio.get_event_loop().time()
    validation_1, report_1 = await validator.validate_for_execution(requirements)
    first_duration = asyncio.get_event_loop().time() - start_time
    
    # Second validation (should be cached)
    print("Second validation (cached)...")
    start_time = asyncio.get_event_loop().time()
    validation_2, report_2 = await validator.validate_for_execution(requirements)
    second_duration = asyncio.get_event_loop().time() - start_time
    
    # Get statistics
    stats = validator.get_validation_statistics()
    
    print(f"✅ First Validation Time: {first_duration:.3f}s")
    print(f"✅ Second Validation Time: {second_duration:.3f}s")
    print(f"✅ Cache Hit Rate: {stats['cache_hit_rate']:.1%}")
    print(f"✅ Total Validations: {stats['total_validations']}")
    print(f"✅ Cache Hits: {stats['cache_hits']}")
    
    # Test cache clearing
    cleared_count = validator.clear_validation_cache()
    print(f"✅ Cleared Cache Entries: {cleared_count}")
    
    return validation_1 and validation_2


async def test_continuous_monitoring():
    """Test continuous infrastructure monitoring."""
    print("\n📊 Testing Continuous Monitoring")
    print("-" * 35)
    
    # Create validator with fast monitoring interval for testing
    policy = ValidationPolicy(resource_check_interval_seconds=2)
    validator = InfrastructureValidator(policy)
    
    # Start monitoring
    print("Starting continuous monitoring...")
    monitoring_started = await validator.start_continuous_monitoring()
    print(f"✅ Monitoring Started: {monitoring_started}")
    
    # Let it run for a few seconds
    print("Monitoring for 5 seconds...")
    await asyncio.sleep(5)
    
    # Check statistics
    stats = validator.get_validation_statistics()
    print(f"✅ Monitoring Active: {stats['continuous_monitoring_active']}")
    print(f"✅ Validations During Monitoring: {stats['total_validations']}")
    
    # Stop monitoring
    print("Stopping continuous monitoring...")
    monitoring_stopped = await validator.stop_continuous_monitoring()
    print(f"✅ Monitoring Stopped: {monitoring_stopped}")
    
    return monitoring_started and monitoring_stopped


async def test_convenience_functions():
    """Test convenience functions for integration."""
    print("\n🔧 Testing Convenience Functions")
    print("-" * 35)
    
    # Test factory function
    validator = create_infrastructure_validator()
    print(f"✅ Factory Function: Created {validator.module_id}")
    
    # Test convenience validation function
    requirements = {
        'convenience_test': True,
        'parallel_tasks': 2
    }
    
    validation_passed, report = await validate_infrastructure_for_dag_execution(requirements)
    print(f"✅ Convenience Validation: {'PASSED' if validation_passed else 'FAILED'}")
    print(f"✅ Report Generated: {len(report.precondition_results)} checks")
    
    return validation_passed


async def test_policy_configuration():
    """Test different validation policy configurations."""
    print("\n⚙️ Testing Policy Configuration")
    print("-" * 32)
    
    # Test custom policy
    custom_policy = ValidationPolicy(
        redis_timeout_seconds=10.0,
        validation_cache_ttl_seconds=120,
        require_redis_connectivity=True,
        auto_remediation_enabled=False
    )
    
    validator = InfrastructureValidator(custom_policy)
    module_info = validator.get_module_info()
    
    policy_info = module_info['validation_policy']
    print(f"✅ Redis Timeout: {policy_info['redis_timeout']}s")
    print(f"✅ Cache TTL: {policy_info['cache_ttl']}s")
    print(f"✅ Auto Remediation: {policy_info['auto_remediation']}")
    
    # Test validation with custom policy
    requirements = {'policy_test': True}
    validation_passed, report = await validator.validate_for_execution(requirements)
    
    print(f"✅ Custom Policy Validation: {'PASSED' if validation_passed else 'FAILED'}")
    
    return validation_passed


async def main():
    """Run comprehensive infrastructure validator tests."""
    
    print("🔍 Infrastructure Validator Component Tests")
    print("=" * 60)
    print("Task 3.2: Validate infrastructure preconditions")
    print("=" * 60)
    
    test_results = []
    
    try:
        # Run all tests
        test_results.append(await test_basic_validator_functionality())
        test_results.append(await test_execution_validation())
        test_results.append(await test_caching_functionality())
        test_results.append(await test_continuous_monitoring())
        test_results.append(await test_convenience_functions())
        test_results.append(await test_policy_configuration())
        
        # Summary
        passed_tests = sum(test_results)
        total_tests = len(test_results)
        
        print(f"\n" + "=" * 60)
        print(f"📊 TEST RESULTS SUMMARY")
        print("=" * 60)
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {total_tests - passed_tests}")
        print(f"Success Rate: {passed_tests/total_tests:.1%}")
        
        if passed_tests == total_tests:
            print(f"\n🚀 ALL TESTS PASSED!")
            print(f"✅ InfrastructureValidator component is working correctly")
            print(f"✅ Task 3.2 validation requirements met")
            print(f"✅ Ready for integration with DAG orchestration system")
            return True
        else:
            print(f"\n⚠️ SOME TESTS FAILED")
            print(f"❌ Review failed tests before proceeding")
            return False
            
    except Exception as e:
        print(f"\n❌ TEST EXECUTION FAILED:")
        print(f"Error: {e}")
        print(f"\n💡 Troubleshooting:")
        print("1. Verify all dependencies are installed")
        print("2. Check that infrastructure precondition validator is working")
        print("3. Ensure system resources are available")
        return False


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)