#!/usr/bin/env python3
"""
Simple Prometheus Metrics Test
==============================

Tests that our DAG orchestration components are generating metrics
and that they're accessible through the existing Prometheus setup.

Author: Beast Mode Framework
Date: 2025-01-27
"""

import sys
import asyncio
import requests
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.dag_orchestration.infrastructure.precondition_validator import InfrastructurePreconditionValidator
from src.dag_orchestration.core.infrastructure_validator import InfrastructureValidator
from src.dag_orchestration.execution.parallel_execution_engine import ParallelExecutionEngine, TaskDefinition


async def test_component_metrics():
    """Test that our components generate metrics."""
    print("🧪 Testing DAG Orchestration Component Metrics")
    print("=" * 50)
    
    try:
        # Create and exercise components
        print("1. Creating InfrastructurePreconditionValidator...")
        validator = InfrastructurePreconditionValidator()
        
        # Exercise the component to generate metrics
        report = await validator.validate_all_preconditions()
        health = validator.get_health_status()
        
        print(f"   ✅ Validation: {'PASSED' if report.overall_status else 'FAILED'}")
        print(f"   ✅ Health: {health.status.value} (Score: {health.health_score})")
        
        # Check if Prometheus metrics are enabled
        prometheus_enabled = getattr(validator, '_enable_prometheus', False)
        print(f"   📊 Prometheus Enabled: {prometheus_enabled}")
        
        if prometheus_enabled and hasattr(validator, '_prometheus_exporter'):
            print(f"   📊 Prometheus Exporter: Available")
        else:
            print(f"   📊 Prometheus Exporter: Not available")
        
        print("\n2. Creating ParallelExecutionEngine...")
        engine = ParallelExecutionEngine(max_workers=2)
        
        # Create simple tasks
        tasks = [
            TaskDefinition(
                task_id="test_task_1",
                name="Test Task 1",
                execution_function=lambda: "Task 1 completed"
            ),
            TaskDefinition(
                task_id="test_task_2", 
                name="Test Task 2",
                execution_function=lambda: "Task 2 completed"
            )
        ]
        
        # Execute tasks
        results = await engine.execute_dag_parallel(tasks)
        engine_health = engine.get_health_status()
        stats = engine.get_execution_statistics()
        
        print(f"   ✅ Execution: {len(results)} tasks completed")
        print(f"   ✅ Health: {engine_health.status.value} (Score: {engine_health.health_score})")
        print(f"   ✅ Statistics: {stats['success_rate']:.1%} success rate")
        
        # Check Prometheus integration
        engine_prometheus_enabled = getattr(engine, '_enable_prometheus', False)
        print(f"   📊 Prometheus Enabled: {engine_prometheus_enabled}")
        
        # Cleanup
        engine.shutdown()
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing components: {e}")
        return False


def test_prometheus_endpoints():
    """Test Prometheus endpoint accessibility."""
    print("\n🔍 Testing Prometheus Endpoint Accessibility")
    print("=" * 45)
    
    endpoints = [
        ("Local Prometheus", "http://localhost:9090/api/v1/query?query=up"),
        ("Public Prometheus", "https://prometheus.observatory.nkllon.com/api/v1/query?query=up"),
        ("Local Metrics", "http://localhost:8000/metrics"),
        ("Public Metrics", "https://prometheus.observatory.nkllon.com/metrics")
    ]
    
    accessible_endpoints = []
    
    for name, url in endpoints:
        try:
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                print(f"   ✅ {name}: Accessible")
                accessible_endpoints.append((name, url))
                
                # Check for data
                if 'api/v1/query' in url:
                    data = response.json()
                    if data.get('status') == 'success':
                        results = data.get('data', {}).get('result', [])
                        print(f"      📊 Query results: {len(results)} metrics")
                    else:
                        print(f"      ⚠️ Query failed: {data}")
                elif '/metrics' in url:
                    metrics_count = len([line for line in response.text.split('\n') if line and not line.startswith('#')])
                    print(f"      📊 Metrics available: {metrics_count} lines")
            else:
                print(f"   ❌ {name}: HTTP {response.status_code}")
                
        except Exception as e:
            print(f"   ❌ {name}: {e}")
    
    return accessible_endpoints


def check_grafana_datasource():
    """Check Grafana data source configuration."""
    print("\n🎯 Testing Grafana Data Source")
    print("=" * 35)
    
    try:
        # Test Grafana health
        grafana_health = requests.get("https://grafana.observatory.nkllon.com/api/health", timeout=10)
        if grafana_health.status_code == 200:
            print("   ✅ Grafana: Accessible")
            
            # Try to test data source (this might require auth)
            try:
                # Test if we can reach Grafana's datasource proxy
                proxy_test = requests.get(
                    "https://grafana.observatory.nkllon.com/api/datasources/proxy/1/api/v1/query?query=up",
                    timeout=10
                )
                if proxy_test.status_code == 200:
                    data = proxy_test.json()
                    if data.get('status') == 'success':
                        print("   ✅ Grafana → Prometheus: Data source working")
                        return True
                    else:
                        print(f"   ⚠️ Grafana → Prometheus: Query failed - {data}")
                else:
                    print(f"   ⚠️ Grafana → Prometheus: HTTP {proxy_test.status_code}")
            except Exception as e:
                print(f"   ⚠️ Grafana → Prometheus: {e}")
                
        else:
            print(f"   ❌ Grafana: HTTP {grafana_health.status_code}")
            
    except Exception as e:
        print(f"   ❌ Grafana: {e}")
    
    return False


async def main():
    """Main test execution."""
    print("🔍 Prometheus Metrics Diagnostic")
    print("=" * 40)
    print("Checking why Grafana shows 'no data'")
    print("=" * 40)
    
    # Test component metrics generation
    components_ok = await test_component_metrics()
    
    # Test endpoint accessibility
    accessible_endpoints = test_prometheus_endpoints()
    
    # Test Grafana data source
    grafana_ok = check_grafana_datasource()
    
    # Summary and recommendations
    print(f"\n📋 DIAGNOSTIC SUMMARY")
    print("=" * 25)
    print(f"✅ Components Working: {components_ok}")
    print(f"✅ Accessible Endpoints: {len(accessible_endpoints)}")
    print(f"✅ Grafana Data Source: {grafana_ok}")
    
    if not accessible_endpoints:
        print(f"\n❌ ISSUE: No Prometheus endpoints accessible")
        print(f"💡 SOLUTION: Start Prometheus server")
        print(f"   - Check if Prometheus is running")
        print(f"   - Verify port configuration")
        print(f"   - Ensure tunnel is forwarding correctly")
        
    elif not grafana_ok:
        print(f"\n❌ ISSUE: Grafana cannot connect to Prometheus")
        print(f"💡 SOLUTION: Fix Grafana data source configuration")
        print(f"   - Run: python3 fix_grafana_prometheus_datasource.py")
        print(f"   - Verify data source URL in Grafana settings")
        print(f"   - Check authentication requirements")
        
    else:
        print(f"\n✅ DIAGNOSIS: Infrastructure appears healthy")
        print(f"💡 POSSIBLE ISSUES:")
        print(f"   - Metrics may not be actively generated")
        print(f"   - Dashboard queries may be incorrect")
        print(f"   - Time range may be too narrow")
        print(f"   - Prometheus may need time to scrape metrics")
    
    print(f"\n🔧 NEXT STEPS:")
    print(f"   1. Check Prometheus targets: https://prometheus.observatory.nkllon.com/targets")
    print(f"   2. Check Prometheus metrics: https://prometheus.observatory.nkllon.com/metrics")
    print(f"   3. Verify Grafana data source: https://grafana.observatory.nkllon.com")
    print(f"   4. Check dashboard time range and queries")
    
    return components_ok and len(accessible_endpoints) > 0


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)