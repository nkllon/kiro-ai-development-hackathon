#!/usr/bin/env python3
"""
Infrastructure Components Validation Script
===========================================

Validates all DAG orchestration infrastructure components and their integration.

Author: Beast Mode Framework
Date: 2025-01-27
Version: 1.0
"""

import asyncio
import sys
from datetime import datetime
from typing import Dict, Any

from src.dag_orchestration.infrastructure.precondition_validator import InfrastructurePreconditionValidator
from src.dag_orchestration.infrastructure.disk_space_manager import DiskSpaceManager
from src.dag_orchestration.optimization.resource_predictor import ResourcePredictor
from src.dag_orchestration.scheduling.ml_scheduler import MLTaskScheduler, SystemState


async def main():
    """Main validation function."""
    print("🔧 DAG Orchestration Infrastructure Components Validation")
    print("=" * 70)
    
    # Sample task for testing
    sample_task = {
        'id': 'validation_test_task',
        'name': 'Infrastructure Validation Test Task',
        'dependencies': [],
        'resource_requirements': {
            'cpu_cores': 2,
            'memory_mb': 1024,
            'estimated_duration_minutes': 30
        },
        'execution_context': {
            'task_type': 'implementation',
            'priority': 'high'
        }
    }
    
    # Sample system state
    system_state = SystemState(
        available_cpu_cores=8,
        available_memory_mb=16384,
        current_load=0.4,
        active_tasks=2,
        queue_length=5
    )
    
    validation_results = {}
    
    # 1. Test PreconditionValidator
    print("\n🔍 Testing Infrastructure Precondition Validator...")
    try:
        validator = InfrastructurePreconditionValidator()
        
        # Test module info
        module_info = validator.get_module_info()
        print(f"  ✅ Module ID: {module_info['module_id']}")
        
        # Test health status
        health = validator.get_health_status()
        print(f"  ✅ Health Score: {health.health_score:.2f}")
        print(f"  ✅ Status: {health.status.value}")
        
        # Test validation (this may fail due to Redis, but that's expected)
        report = await validator.validate_all_preconditions()
        passed_checks = sum(1 for r in report.precondition_results if r.passed)
        total_checks = len(report.precondition_results)
        print(f"  📊 Validation: {passed_checks}/{total_checks} checks passed")
        
        validation_results['precondition_validator'] = {
            'status': 'success',
            'health_score': health.health_score,
            'checks_passed': passed_checks,
            'total_checks': total_checks
        }
        
    except Exception as e:
        print(f"  ❌ Error: {e}")
        validation_results['precondition_validator'] = {'status': 'error', 'error': str(e)}
    
    # 2. Test DiskSpaceManager
    print("\n💾 Testing Disk Space Manager...")
    try:
        disk_manager = DiskSpaceManager()
        
        # Test module info
        module_info = disk_manager.get_module_info()
        print(f"  ✅ Module ID: {module_info['module_id']}")
        
        # Test health status
        health = disk_manager.get_health_status()
        print(f"  ✅ Health Score: {health.health_score:.2f}")
        print(f"  ✅ Status: {health.status.value}")
        
        # Test disk analysis
        report = disk_manager.analyze_disk_usage()
        print(f"  📊 Disk Usage: {report.usage_percent:.1f}%")
        print(f"  📊 Free Space: {report.free_space_gb:.1f}GB")
        print(f"  📊 Cleanup Recommendations: {len(report.cleanup_recommendations)}")
        
        validation_results['disk_space_manager'] = {
            'status': 'success',
            'health_score': health.health_score,
            'usage_percent': report.usage_percent,
            'free_space_gb': report.free_space_gb
        }
        
    except Exception as e:
        print(f"  ❌ Error: {e}")
        validation_results['disk_space_manager'] = {'status': 'error', 'error': str(e)}
    
    # 3. Test ResourcePredictor
    print("\n🔮 Testing Resource Predictor...")
    try:
        predictor = ResourcePredictor()
        
        # Test module info
        module_info = predictor.get_module_info()
        print(f"  ✅ Module ID: {module_info['module_id']}")
        
        # Test health status
        health = predictor.get_health_status()
        print(f"  ✅ Health Score: {health.health_score:.2f}")
        print(f"  ✅ Status: {health.status.value}")
        
        # Test resource prediction
        requirements = predictor.predict_task_resource_requirements(sample_task)
        print(f"  📊 Predicted CPU: {requirements.cpu_cores:.1f} cores")
        print(f"  📊 Predicted Memory: {requirements.memory_mb}MB")
        print(f"  📊 Predicted Duration: {requirements.duration_minutes:.1f} minutes")
        print(f"  📊 Confidence: {requirements.confidence:.2f}")
        
        # Test capacity planning
        capacity_plan = predictor.generate_capacity_plan([sample_task])
        print(f"  📊 Capacity Plan Confidence: {capacity_plan.confidence_score:.2f}")
        
        validation_results['resource_predictor'] = {
            'status': 'success',
            'health_score': health.health_score,
            'prediction_confidence': requirements.confidence,
            'capacity_confidence': capacity_plan.confidence_score
        }
        
    except Exception as e:
        print(f"  ❌ Error: {e}")
        validation_results['resource_predictor'] = {'status': 'error', 'error': str(e)}
    
    # 4. Test MLTaskScheduler
    print("\n🤖 Testing ML Task Scheduler...")
    try:
        scheduler = MLTaskScheduler()
        
        # Test module info
        module_info = scheduler.get_module_info()
        print(f"  ✅ Module ID: {module_info['module_id']}")
        
        # Test health status
        health = scheduler.get_health_status()
        print(f"  ✅ Health Score: {health.health_score:.2f}")
        print(f"  ✅ Status: {health.status.value}")
        
        # Test execution time prediction
        duration, confidence = scheduler.predict_execution_time(sample_task)
        print(f"  📊 Predicted Duration: {duration:.1f} minutes")
        print(f"  📊 Prediction Confidence: {confidence:.2f}")
        
        # Test priority calculation
        priority = scheduler.calculate_dynamic_priority(sample_task, system_state)
        print(f"  📊 Dynamic Priority: {priority:.2f}")
        
        # Test scheduling recommendations
        recommendations = scheduler.get_scheduling_recommendations([sample_task], system_state)
        if recommendations:
            rec = recommendations[0]
            print(f"  📊 Scheduling Confidence: {rec.confidence_score:.2f}")
            print(f"  📊 Rationale: {rec.scheduling_rationale}")
        
        validation_results['ml_scheduler'] = {
            'status': 'success',
            'health_score': health.health_score,
            'prediction_confidence': confidence,
            'priority_score': priority
        }
        
    except Exception as e:
        print(f"  ❌ Error: {e}")
        validation_results['ml_scheduler'] = {'status': 'error', 'error': str(e)}
    
    # 5. Test Integration
    print("\n🔗 Testing Component Integration...")
    try:
        integration_score = 0.0
        total_components = 0
        
        for component, result in validation_results.items():
            if result['status'] == 'success':
                integration_score += result.get('health_score', 0.0)
                total_components += 1
        
        if total_components > 0:
            avg_integration_score = integration_score / total_components
            print(f"  📊 Average Health Score: {avg_integration_score:.2f}")
            print(f"  📊 Components Working: {total_components}/4")
            
            if avg_integration_score >= 0.8:
                print("  ✅ Integration Status: EXCELLENT")
            elif avg_integration_score >= 0.6:
                print("  ⚠️  Integration Status: GOOD")
            else:
                print("  ❌ Integration Status: NEEDS ATTENTION")
        else:
            print("  ❌ No components working properly")
            
    except Exception as e:
        print(f"  ❌ Integration test error: {e}")
    
    # Summary
    print("\n📋 Validation Summary")
    print("-" * 30)
    
    success_count = sum(1 for r in validation_results.values() if r['status'] == 'success')
    total_count = len(validation_results)
    
    print(f"Components Validated: {success_count}/{total_count}")
    
    for component, result in validation_results.items():
        status_icon = "✅" if result['status'] == 'success' else "❌"
        component_name = component.replace('_', ' ').title()
        print(f"  {status_icon} {component_name}")
        
        if result['status'] == 'success' and 'health_score' in result:
            print(f"    Health Score: {result['health_score']:.2f}")
    
    if success_count == total_count:
        print("\n🎉 All infrastructure components are working correctly!")
        return 0
    else:
        print(f"\n⚠️  {total_count - success_count} component(s) need attention")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)