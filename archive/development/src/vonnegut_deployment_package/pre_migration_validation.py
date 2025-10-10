#!/usr/bin/env python3
"""
Pre-Migration Validation
=======================

Validates current Observatory deployment is stable before Poe migration.
"""

import asyncio
import json
import sys
import requests
import websockets
from datetime import datetime
from pathlib import Path

async def validate_current_deployment():
    """Validate current Observatory deployment is stable."""
    print("🔍 Pre-Migration Validation")
    print("=" * 30)
    
    validation_results = {
        "timestamp": datetime.now().isoformat(),
        "tests": {},
        "ready_for_migration": False
    }
    
    # Test 1: Observatory health
    try:
        response = requests.get("https://observatory.nkllon.com/health", timeout=10)
        if response.status_code == 200:
            health_data = response.json()
            validation_results["tests"]["observatory_health"] = {
                "status": "pass",
                "details": f"Healthy - {health_data.get('status', 'unknown')}"
            }
            print("✅ Observatory health: PASS")
        else:
            validation_results["tests"]["observatory_health"] = {
                "status": "fail", 
                "details": f"Status {response.status_code}"
            }
            print("❌ Observatory health: FAIL")
    except Exception as e:
        validation_results["tests"]["observatory_health"] = {
            "status": "fail",
            "details": str(e)
        }
        print("❌ Observatory health: FAIL")
    
    # Test 2: Grafana access
    try:
        response = requests.get("https://grafana.observatory.nkllon.com/", timeout=10)
        if response.status_code == 200 and "Grafana" in response.text:
            validation_results["tests"]["grafana_access"] = {
                "status": "pass",
                "details": "Grafana interface accessible"
            }
            print("✅ Grafana access: PASS")
        else:
            validation_results["tests"]["grafana_access"] = {
                "status": "fail",
                "details": f"Status {response.status_code}"
            }
            print("❌ Grafana access: FAIL")
    except Exception as e:
        validation_results["tests"]["grafana_access"] = {
            "status": "fail",
            "details": str(e)
        }
        print("❌ Grafana access: FAIL")
    
    # Test 3: Prometheus API
    try:
        response = requests.get("https://prometheus.observatory.nkllon.com/api/v1/query?query=up", timeout=10)
        if response.status_code == 200:
            data = response.json()
            if data.get("status") == "success":
                validation_results["tests"]["prometheus_api"] = {
                    "status": "pass",
                    "details": "Prometheus API responding"
                }
                print("✅ Prometheus API: PASS")
            else:
                validation_results["tests"]["prometheus_api"] = {
                    "status": "fail",
                    "details": "API error response"
                }
                print("❌ Prometheus API: FAIL")
        else:
            validation_results["tests"]["prometheus_api"] = {
                "status": "fail",
                "details": f"Status {response.status_code}"
            }
            print("❌ Prometheus API: FAIL")
    except Exception as e:
        validation_results["tests"]["prometheus_api"] = {
            "status": "fail",
            "details": str(e)
        }
        print("❌ Prometheus API: FAIL")
    
    # Test 4: WebSocket endpoints
    websocket_endpoints = [
        ("ws://localhost:8888/ws/observatory", "Observatory WebSocket"),
        ("ws://localhost:8888/ws/emoji-rain", "Emoji Rain WebSocket"),
        ("ws://localhost:8888/ws/engagement", "Engagement WebSocket")
    ]
    
    websocket_results = []
    for uri, name in websocket_endpoints:
        try:
            async with websockets.connect(uri, timeout=5) as websocket:
                await websocket.send(json.dumps({"type": "test"}))
                response = await asyncio.wait_for(websocket.recv(), timeout=3)
                websocket_results.append((name, True))
                print(f"✅ {name}: PASS")
        except Exception as e:
            websocket_results.append((name, False))
            print(f"❌ {name}: FAIL")
    
    validation_results["tests"]["websocket_endpoints"] = {
        "status": "pass" if all(result[1] for result in websocket_results) else "fail",
        "details": f"{sum(1 for _, success in websocket_results if success)}/{len(websocket_results)} endpoints working"
    }
    
    # Calculate overall readiness
    all_tests = validation_results["tests"]
    passed_tests = sum(1 for test in all_tests.values() if test["status"] == "pass")
    total_tests = len(all_tests)
    
    validation_results["ready_for_migration"] = passed_tests == total_tests
    validation_results["test_summary"] = {
        "passed": passed_tests,
        "total": total_tests,
        "success_rate": (passed_tests / total_tests * 100) if total_tests > 0 else 0
    }
    
    # Save validation results
    results_file = Path("pre_migration_validation.json")
    with open(results_file, 'w') as f:
        json.dump(validation_results, f, indent=2)
    
    print(f"\n🎯 Pre-Migration Validation Summary")
    print("=" * 40)
    print(f"📊 Tests Passed: {passed_tests}/{total_tests} ({validation_results['test_summary']['success_rate']:.1f}%)")
    print(f"📋 Results: {results_file}")
    
    if validation_results["ready_for_migration"]:
        print("✅ READY FOR MIGRATION TO POE!")
        print("🚀 All systems stable and validated")
    else:
        print("❌ NOT READY FOR MIGRATION")
        print("🔧 Fix failing tests before proceeding")
    
    return validation_results["ready_for_migration"]

if __name__ == "__main__":
    ready = asyncio.run(validate_current_deployment())
    sys.exit(0 if ready else 1)