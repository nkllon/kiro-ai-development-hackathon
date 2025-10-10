#!/usr/bin/env python3
"""
Test Infrastructure Preconditions for DAG Orchestration
======================================================

Validates all infrastructure preconditions before proceeding with DAG orchestration implementation.
This is Task 0 from the implementation plan.

Author: Beast Mode Framework
Date: 2025-01-27
"""

import asyncio
import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.dag_orchestration.infrastructure.precondition_validator import (
    InfrastructurePreconditionValidator,
    validate_infrastructure_preconditions
)


async def main():
    """Run comprehensive infrastructure precondition validation."""
    
    print("🔍 DAG Orchestration Infrastructure Precondition Validation")
    print("=" * 70)
    print("Task 0: Validate infrastructure preconditions and readiness")
    print("=" * 70)
    
    try:
        # Create validator
        validator = InfrastructurePreconditionValidator()
        
        # Show validator info
        module_info = validator.get_module_info()
        print(f"\n📋 Validator Info:")
        print(f"  Module: {module_info['name']}")
        print(f"  Version: {module_info['version']}")
        print(f"  Redis Target: {module_info['redis_config']['host']}:{module_info['redis_config']['port']}")
        
        # Check validator health
        health = validator.get_health_status()
        print(f"\n🏥 Validator Health:")
        print(f"  Status: {health.status.value}")
        print(f"  Health Score: {health.health_score}")
        if health.issues:
            print(f"  Issues: {', '.join(health.issues)}")
        
        # Run comprehensive validation
        print(f"\n🔍 Running Comprehensive Infrastructure Validation...")
        print("-" * 50)
        
        report = await validator.validate_all_preconditions()
        
        # Display results
        print(f"\n📊 VALIDATION RESULTS")
        print("=" * 50)
        print(f"Overall Status: {'✅ PASSED' if report.overall_status else '❌ FAILED'}")
        print(f"Validation Time: {report.validation_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Total Checks: {len(report.precondition_results)}")
        
        passed_count = sum(1 for r in report.precondition_results if r.passed)
        failed_count = len(report.precondition_results) - passed_count
        print(f"Passed: {passed_count}, Failed: {failed_count}")
        
        # Individual check results
        print(f"\n🔍 INDIVIDUAL CHECKS")
        print("-" * 30)
        
        for i, result in enumerate(report.precondition_results, 1):
            status_icon = "✅" if result.passed else "❌"
            print(f"{i}. {result.name}: {status_icon}")
            
            if result.passed:
                # Show key details for passed checks
                if 'connection_test' in result.details:
                    print(f"   Connection: {result.details['connection_test']}")
                if 'cpu_cores' in result.details:
                    print(f"   CPU Cores: {result.details['cpu_cores']}")
                    print(f"   Memory: {result.details['memory_gb']}GB")
                    print(f"   Disk Free: {result.details['disk_free_gb']}GB")
                if 'available_count' in result.details:
                    print(f"   Available: {result.details['available_count']}/{result.details['total_required']}")
            else:
                # Show error details for failed checks
                if result.error_message:
                    print(f"   ❌ Error: {result.error_message}")
                
                if result.remediation_steps:
                    print(f"   💡 Remediation:")
                    for step in result.remediation_steps:
                        print(f"      - {step}")
        
        # System information
        print(f"\n💻 SYSTEM INFORMATION")
        print("-" * 25)
        print(f"Python Version: {report.system_info['python_version'].split()[0]}")
        print(f"Platform: {report.system_info['platform']}")
        print(f"CPU Cores: {report.system_info['cpu_count']}")
        print(f"Memory: {report.system_info['memory_gb']}GB")
        
        # Recommendations
        print(f"\n💡 RECOMMENDATIONS")
        print("-" * 20)
        for i, rec in enumerate(report.recommendations, 1):
            print(f"{i}. {rec}")
        
        # Final status
        print(f"\n" + "=" * 70)
        if report.overall_status:
            print("🚀 INFRASTRUCTURE READY FOR DAG ORCHESTRATION DEPLOYMENT!")
            print("✅ All preconditions met - proceed to next implementation task")
            return True
        else:
            print("⚠️  INFRASTRUCTURE NOT READY")
            print("❌ Address precondition failures before proceeding")
            return False
            
    except Exception as e:
        print(f"\n❌ VALIDATION FAILED WITH EXCEPTION:")
        print(f"Error: {e}")
        print(f"\n💡 Troubleshooting:")
        print("1. Verify Python environment is properly configured")
        print("2. Check that Beast Mode framework components are accessible")
        print("3. Ensure required packages are installed")
        return False


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)