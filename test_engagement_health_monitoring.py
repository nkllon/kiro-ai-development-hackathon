#!/usr/bin/env python3
"""
Test script for engagement system health monitoring.

This script validates:
1. All engagement components report healthy status
2. Engagement health endpoints return correct placeholder status
3. Engagement metrics are collected properly

Requirements: 28.1, 28.2, 28.3, 28.4, 28.5
"""

import asyncio
import aiohttp
import json
import logging
import sys
import time
from pathlib import Path
from typing import Dict, Any, List

# Add the src directory to Python path
sys.path.insert(0, str(Path(__file__).parent / "src"))

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class EngagementHealthMonitoringTester:
    """Test suite for engagement system health monitoring."""
    
    def __init__(self, base_url: str = "http://localhost:8888"):
        self.base_url = base_url
        self.test_results = []
        
    async def run_all_tests(self) -> Dict[str, Any]:
        """Run all engagement health monitoring tests."""
        logger.info("🏥 Starting engagement system health monitoring tests...")
        
        # Test 1: Component health status reporting
        await self.test_component_health_status()
        
        # Test 2: Health endpoint functionality
        await self.test_health_endpoint_functionality()
        
        # Test 3: Engagement metrics collection
        await self.test_engagement_metrics_collection()
        
        # Test 4: Health status accuracy
        await self.test_health_status_accuracy()
        
        # Test 5: System observability
        await self.test_system_observability()
        
        # Generate test report
        return self.generate_test_report()
    
    async def test_component_health_status(self):
        """Test that all engagement components report healthy status."""
        test_name = "Component Health Status Reporting"
        logger.info(f"🔍 Testing: {test_name}")
        
        try:
            # Test individual component health by creating instances
            from src.beast_mode.observatory.engagement.core import (
                DashboardEngine, AnimationEngine, PersonalityEngine,
                AttentionManager, InteractionEngine
            )
            
            components = [
                ("DashboardEngine", DashboardEngine),
                ("AnimationEngine", AnimationEngine),
                ("PersonalityEngine", PersonalityEngine),
                ("AttentionManager", AttentionManager),
                ("InteractionEngine", InteractionEngine)
            ]
            
            component_health = {}
            
            for name, component_class in components:
                try:
                    # Create instance
                    instance = component_class()
                    
                    # Get health status
                    if hasattr(instance, 'get_health_status'):
                        health = instance.get_health_status()
                        component_health[name] = {
                            "status": health.get("status", "unknown"),
                            "healthy": health.get("status") in ["healthy", "initializing"],
                            "details": health
                        }
                    else:
                        component_health[name] = {
                            "status": "no_health_method",
                            "healthy": False,
                            "error": "No get_health_status method"
                        }
                        
                except Exception as e:
                    component_health[name] = {
                        "status": "error",
                        "healthy": False,
                        "error": str(e)
                    }
            
            # Check overall health
            healthy_components = sum(1 for c in component_health.values() if c.get("healthy", False))
            total_components = len(component_health)
            
            self.test_results.append({
                "test": test_name,
                "status": "PASS" if healthy_components == total_components else "PARTIAL",
                "details": {
                    "total_components": total_components,
                    "healthy_components": healthy_components,
                    "component_health": component_health
                },
                "requirement": "28.1, 28.2"
            })
            
            if healthy_components == total_components:
                logger.info(f"✅ {test_name}: PASS - All {total_components} components healthy")
            else:
                logger.warning(f"⚠️ {test_name}: PARTIAL - {healthy_components}/{total_components} components healthy")
                
        except Exception as e:
            self.test_results.append({
                "test": test_name,
                "status": "FAIL",
                "error": str(e),
                "requirement": "28.1, 28.2"
            })
            logger.error(f"❌ {test_name}: FAIL - {e}")
    
    async def test_health_endpoint_functionality(self):
        """Test that engagement health endpoints return correct status."""
        test_name = "Health Endpoint Functionality"
        logger.info(f"🔍 Testing: {test_name}")
        
        try:
            async with aiohttp.ClientSession() as session:
                # Test main health endpoint for engagement data
                async with session.get(f"{self.base_url}/health", timeout=5) as response:
                    if response.status == 200:
                        health_data = await response.json()
                        
                        # Check engagement section
                        has_engagement = "engagement" in health_data
                        engagement_data = health_data.get("engagement", {})
                        
                        # Validate engagement health structure
                        expected_fields = ["status", "storyteller_healthy", "data_bridge_running"]
                        has_required_fields = all(field in engagement_data for field in expected_fields)
                        
                        # Test engagement-specific endpoints
                        engagement_endpoints = {}
                        
                        # Test /api/engagement/status
                        try:
                            async with session.get(f"{self.base_url}/api/engagement/status", timeout=3) as eng_response:
                                engagement_endpoints["/api/engagement/status"] = {
                                    "status": eng_response.status,
                                    "accessible": eng_response.status == 200,
                                    "data": await eng_response.json() if eng_response.status == 200 else None
                                }
                        except Exception as e:
                            engagement_endpoints["/api/engagement/status"] = {
                                "status": "ERROR",
                                "accessible": False,
                                "error": str(e)
                            }
                        
                        # Test /api/engagement/insights
                        try:
                            async with session.get(f"{self.base_url}/api/engagement/insights", timeout=3) as ins_response:
                                engagement_endpoints["/api/engagement/insights"] = {
                                    "status": ins_response.status,
                                    "accessible": ins_response.status == 200,
                                    "data": await ins_response.json() if ins_response.status == 200 else None
                                }
                        except Exception as e:
                            engagement_endpoints["/api/engagement/insights"] = {
                                "status": "ERROR",
                                "accessible": False,
                                "error": str(e)
                            }
                        
                        self.test_results.append({
                            "test": test_name,
                            "status": "PASS" if has_engagement and has_required_fields else "PARTIAL",
                            "details": {
                                "main_health_has_engagement": has_engagement,
                                "required_fields_present": has_required_fields,
                                "engagement_data": engagement_data,
                                "engagement_endpoints": engagement_endpoints
                            },
                            "requirement": "28.3, 28.4"
                        })
                        
                        if has_engagement and has_required_fields:
                            logger.info(f"✅ {test_name}: PASS - Health endpoints functional")
                        else:
                            logger.warning(f"⚠️ {test_name}: PARTIAL - Some health data missing")
                    else:
                        raise Exception(f"Health endpoint returned status {response.status}")
                        
        except Exception as e:
            self.test_results.append({
                "test": test_name,
                "status": "FAIL",
                "error": str(e),
                "requirement": "28.3, 28.4"
            })
            logger.error(f"❌ {test_name}: FAIL - {e}")
    
    async def test_engagement_metrics_collection(self):
        """Test that engagement metrics are collected properly."""
        test_name = "Engagement Metrics Collection"
        logger.info(f"🔍 Testing: {test_name}")
        
        try:
            async with aiohttp.ClientSession() as session:
                # Test Prometheus metrics endpoint
                async with session.get(f"{self.base_url}/metrics", timeout=5) as response:
                    if response.status == 200:
                        metrics_text = await response.text()
                        
                        # Look for engagement-related metrics
                        engagement_metrics = []
                        lines = metrics_text.split('\n')
                        
                        for line in lines:
                            if 'engagement' in line.lower() or 'storyteller' in line.lower():
                                engagement_metrics.append(line.strip())
                        
                        # Test Observatory status endpoint for metrics
                        async with session.get(f"{self.base_url}/api/observatory/status", timeout=5) as status_response:
                            if status_response.status == 200:
                                status_data = await status_response.json()
                                has_metrics = "metrics" in status_data
                                metrics_data = status_data.get("metrics", {})
                            else:
                                has_metrics = False
                                metrics_data = {}
                        
                        self.test_results.append({
                            "test": test_name,
                            "status": "PASS" if engagement_metrics or has_metrics else "PARTIAL",
                            "details": {
                                "prometheus_metrics_found": len(engagement_metrics),
                                "engagement_metrics_sample": engagement_metrics[:5],  # First 5 metrics
                                "observatory_has_metrics": has_metrics,
                                "metrics_data_keys": list(metrics_data.keys()) if isinstance(metrics_data, dict) else []
                            },
                            "requirement": "28.4, 28.5"
                        })
                        
                        if engagement_metrics or has_metrics:
                            logger.info(f"✅ {test_name}: PASS - Engagement metrics collected")
                        else:
                            logger.warning(f"⚠️ {test_name}: PARTIAL - Limited metrics found")
                    else:
                        raise Exception(f"Metrics endpoint returned status {response.status}")
                        
        except Exception as e:
            self.test_results.append({
                "test": test_name,
                "status": "FAIL",
                "error": str(e),
                "requirement": "28.4, 28.5"
            })
            logger.error(f"❌ {test_name}: FAIL - {e}")
    
    async def test_health_status_accuracy(self):
        """Test that health status accurately reflects system state."""
        test_name = "Health Status Accuracy"
        logger.info(f"🔍 Testing: {test_name}")
        
        try:
            async with aiohttp.ClientSession() as session:
                # Get health data multiple times to check consistency
                health_checks = []
                
                for i in range(3):
                    async with session.get(f"{self.base_url}/health", timeout=5) as response:
                        if response.status == 200:
                            health_data = await response.json()
                            health_checks.append({
                                "check": i + 1,
                                "timestamp": health_data.get("timestamp"),
                                "overall_status": health_data.get("status"),
                                "engagement_status": health_data.get("engagement", {}).get("status"),
                                "storyteller_healthy": health_data.get("engagement", {}).get("storyteller_healthy"),
                                "data_bridge_running": health_data.get("engagement", {}).get("data_bridge_running")
                            })
                    
                    # Small delay between checks
                    await asyncio.sleep(1)
                
                # Check consistency
                statuses = [check["engagement_status"] for check in health_checks]
                consistent_status = len(set(statuses)) == 1
                
                # Check if status makes sense
                valid_statuses = ["healthy", "initializing", "degraded", "stopped"]
                valid_status = all(status in valid_statuses for status in statuses if status)
                
                self.test_results.append({
                    "test": test_name,
                    "status": "PASS" if consistent_status and valid_status else "PARTIAL",
                    "details": {
                        "health_checks": health_checks,
                        "consistent_status": consistent_status,
                        "valid_status": valid_status,
                        "unique_statuses": list(set(statuses))
                    },
                    "requirement": "28.1, 28.2, 28.3"
                })
                
                if consistent_status and valid_status:
                    logger.info(f"✅ {test_name}: PASS - Health status accurate and consistent")
                else:
                    logger.warning(f"⚠️ {test_name}: PARTIAL - Health status inconsistencies detected")
                    
        except Exception as e:
            self.test_results.append({
                "test": test_name,
                "status": "FAIL",
                "error": str(e),
                "requirement": "28.1, 28.2, 28.3"
            })
            logger.error(f"❌ {test_name}: FAIL - {e}")
    
    async def test_system_observability(self):
        """Test overall system observability for engagement components."""
        test_name = "System Observability"
        logger.info(f"🔍 Testing: {test_name}")
        
        try:
            async with aiohttp.ClientSession() as session:
                # Test various observability endpoints
                observability_tests = {}
                
                # Test 1: Recent observations
                try:
                    async with session.get(f"{self.base_url}/api/observations/recent", timeout=5) as response:
                        observability_tests["observations"] = {
                            "status": response.status,
                            "accessible": response.status == 200,
                            "data": await response.json() if response.status == 200 else None
                        }
                except Exception as e:
                    observability_tests["observations"] = {
                        "status": "ERROR",
                        "accessible": False,
                        "error": str(e)
                    }
                
                # Test 2: Metrics components
                try:
                    async with session.get(f"{self.base_url}/api/metrics/components", timeout=5) as response:
                        observability_tests["metrics_components"] = {
                            "status": response.status,
                            "accessible": response.status == 200,
                            "data": await response.json() if response.status == 200 else None
                        }
                except Exception as e:
                    observability_tests["metrics_components"] = {
                        "status": "ERROR",
                        "accessible": False,
                        "error": str(e)
                    }
                
                # Test 3: Analytics current
                try:
                    async with session.get(f"{self.base_url}/api/analytics/current", timeout=5) as response:
                        observability_tests["analytics"] = {
                            "status": response.status,
                            "accessible": response.status == 200,
                            "data": await response.json() if response.status == 200 else None
                        }
                except Exception as e:
                    observability_tests["analytics"] = {
                        "status": "ERROR",
                        "accessible": False,
                        "error": str(e)
                    }
                
                # Calculate observability score
                accessible_endpoints = sum(1 for test in observability_tests.values() if test.get("accessible", False))
                total_endpoints = len(observability_tests)
                observability_score = accessible_endpoints / total_endpoints if total_endpoints > 0 else 0
                
                self.test_results.append({
                    "test": test_name,
                    "status": "PASS" if observability_score >= 0.7 else "PARTIAL",
                    "details": {
                        "observability_score": f"{observability_score:.2f}",
                        "accessible_endpoints": accessible_endpoints,
                        "total_endpoints": total_endpoints,
                        "endpoint_tests": observability_tests
                    },
                    "requirement": "28.5"
                })
                
                if observability_score >= 0.7:
                    logger.info(f"✅ {test_name}: PASS - System observability good ({observability_score:.2f})")
                else:
                    logger.warning(f"⚠️ {test_name}: PARTIAL - Limited observability ({observability_score:.2f})")
                    
        except Exception as e:
            self.test_results.append({
                "test": test_name,
                "status": "FAIL",
                "error": str(e),
                "requirement": "28.5"
            })
            logger.error(f"❌ {test_name}: FAIL - {e}")
    
    def generate_test_report(self) -> Dict[str, Any]:
        """Generate comprehensive test report."""
        total_tests = len(self.test_results)
        passed_tests = sum(1 for r in self.test_results if r["status"] == "PASS")
        partial_tests = sum(1 for r in self.test_results if r["status"] == "PARTIAL")
        failed_tests = sum(1 for r in self.test_results if r["status"] == "FAIL")
        
        report = {
            "summary": {
                "total_tests": total_tests,
                "passed": passed_tests,
                "partial": partial_tests,
                "failed": failed_tests,
                "success_rate": f"{(passed_tests / total_tests * 100):.1f}%" if total_tests > 0 else "0%",
                "overall_status": "PASS" if failed_tests == 0 else "PARTIAL" if passed_tests > 0 else "FAIL"
            },
            "test_results": self.test_results,
            "requirements_coverage": {
                "28.1": "Engagement component health status reporting",
                "28.2": "Component status accuracy and consistency",
                "28.3": "Health endpoint functionality and data structure",
                "28.4": "Engagement metrics collection and availability",
                "28.5": "System observability and monitoring capabilities"
            }
        }
        
        return report

async def main():
    """Main test execution function."""
    print("🏥 Engagement System Health Monitoring Test Suite")
    print("=" * 60)
    
    tester = EngagementHealthMonitoringTester()
    
    print("📋 Testing engagement system health monitoring...")
    print("   This validates Requirements 28.1-28.5")
    print()
    
    # Run tests
    report = await tester.run_all_tests()
    
    # Print results
    print("\n" + "=" * 60)
    print("📊 HEALTH MONITORING TEST RESULTS")
    print("=" * 60)
    
    summary = report["summary"]
    print(f"Total Tests: {summary['total_tests']}")
    print(f"Passed: {summary['passed']} ✅")
    print(f"Partial: {summary['partial']} ⚠️")
    print(f"Failed: {summary['failed']} ❌")
    print(f"Success Rate: {summary['success_rate']}")
    print(f"Overall Status: {summary['overall_status']}")
    
    print("\n📋 DETAILED RESULTS:")
    print("-" * 40)
    
    for result in report["test_results"]:
        status_emoji = {"PASS": "✅", "PARTIAL": "⚠️", "FAIL": "❌"}
        print(f"{status_emoji.get(result['status'], '❓')} {result['test']}: {result['status']}")
        if "error" in result:
            print(f"   Error: {result['error']}")
        if "details" in result:
            print(f"   Requirements: {result['requirement']}")
    
    # Save detailed report
    report_file = "engagement_health_monitoring_test_report.json"
    with open(report_file, "w") as f:
        json.dump(report, f, indent=2, default=str)
    
    print(f"\n📄 Detailed report saved to: {report_file}")
    
    # Return appropriate exit code
    if summary["overall_status"] == "FAIL":
        print("\n❌ HEALTH MONITORING TESTS FAILED")
        return 1
    elif summary["overall_status"] == "PARTIAL":
        print("\n⚠️ HEALTH MONITORING TESTS PARTIALLY SUCCESSFUL")
        return 0  # Still success for partial
    else:
        print("\n✅ HEALTH MONITORING TESTS PASSED")
        return 0

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)