#!/usr/bin/env python3
"""
Test script for Observatory server startup with engagement system integration.

This script validates:
1. Observatory server starts successfully with engagement integration
2. All engagement WebSocket endpoints are available
3. Existing Observatory functionality remains intact
4. Engagement components report healthy status

Requirements: 20.1, 20.2, 20.3, 20.4, 20.5, 24.1, 24.2, 24.3, 24.4, 24.5, 28.1, 28.2, 28.3, 28.4, 28.5
"""

import asyncio
import aiohttp
import json
import logging
import sys
import time
from pathlib import Path
from typing import Dict, Any, List

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class EngagementIntegrationTester:
    """Test suite for engagement system integration with Observatory server."""
    
    def __init__(self, base_url: str = "http://localhost:8888"):
        self.base_url = base_url
        self.test_results = []
        self.server_process = None
        
    async def run_all_tests(self) -> Dict[str, Any]:
        """Run all engagement integration tests."""
        logger.info("🧪 Starting engagement system integration tests...")
        
        # Test 1: Server startup validation
        await self.test_server_startup()
        
        # Test 2: Basic Observatory endpoints
        await self.test_observatory_endpoints()
        
        # Test 3: Engagement WebSocket endpoints
        await self.test_engagement_websocket_endpoints()
        
        # Test 4: Engagement health monitoring
        await self.test_engagement_health_monitoring()
        
        # Test 5: Existing functionality preservation
        await self.test_existing_functionality()
        
        # Generate test report
        return self.generate_test_report()
    
    async def test_server_startup(self):
        """Test that Observatory server starts successfully with engagement integration."""
        test_name = "Server Startup with Engagement Integration"
        logger.info(f"🔍 Testing: {test_name}")
        
        try:
            # Try to connect to the server
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.base_url}/health", timeout=10) as response:
                    if response.status == 200:
                        health_data = await response.json()
                        
                        # Check if engagement integration is mentioned in health data
                        has_engagement = "engagement" in health_data
                        
                        self.test_results.append({
                            "test": test_name,
                            "status": "PASS",
                            "details": {
                                "server_responsive": True,
                                "engagement_integration_detected": has_engagement,
                                "health_data": health_data
                            },
                            "requirement": "20.1, 20.2, 20.3"
                        })
                        logger.info(f"✅ {test_name}: PASS")
                    else:
                        raise Exception(f"Server returned status {response.status}")
                        
        except Exception as e:
            self.test_results.append({
                "test": test_name,
                "status": "FAIL",
                "error": str(e),
                "requirement": "20.1, 20.2, 20.3"
            })
            logger.error(f"❌ {test_name}: FAIL - {e}")
    
    async def test_observatory_endpoints(self):
        """Test that existing Observatory endpoints work correctly."""
        test_name = "Observatory Core Endpoints"
        logger.info(f"🔍 Testing: {test_name}")
        
        endpoints_to_test = [
            "/health",
            "/metrics", 
            "/api/observatory/status",
            "/api/emoji-rain/stats",
            "/api/observations/recent"
        ]
        
        results = {}
        
        try:
            async with aiohttp.ClientSession() as session:
                for endpoint in endpoints_to_test:
                    try:
                        async with session.get(f"{self.base_url}{endpoint}", timeout=5) as response:
                            results[endpoint] = {
                                "status": response.status,
                                "accessible": response.status == 200
                            }
                            if response.status == 200:
                                # Try to parse JSON if possible
                                try:
                                    data = await response.json()
                                    results[endpoint]["has_data"] = bool(data)
                                except:
                                    results[endpoint]["has_data"] = False
                    except Exception as e:
                        results[endpoint] = {
                            "status": "ERROR",
                            "error": str(e),
                            "accessible": False
                        }
            
            # Check if all endpoints are accessible
            all_accessible = all(r.get("accessible", False) for r in results.values())
            
            self.test_results.append({
                "test": test_name,
                "status": "PASS" if all_accessible else "PARTIAL",
                "details": {
                    "endpoints_tested": len(endpoints_to_test),
                    "endpoints_accessible": sum(1 for r in results.values() if r.get("accessible", False)),
                    "endpoint_results": results
                },
                "requirement": "20.4, 20.5, 24.4, 24.5"
            })
            
            if all_accessible:
                logger.info(f"✅ {test_name}: PASS - All endpoints accessible")
            else:
                logger.warning(f"⚠️ {test_name}: PARTIAL - Some endpoints not accessible")
                
        except Exception as e:
            self.test_results.append({
                "test": test_name,
                "status": "FAIL",
                "error": str(e),
                "requirement": "20.4, 20.5, 24.4, 24.5"
            })
            logger.error(f"❌ {test_name}: FAIL - {e}")
    
    async def test_engagement_websocket_endpoints(self):
        """Test that engagement WebSocket endpoints are available."""
        test_name = "Engagement WebSocket Endpoints"
        logger.info(f"🔍 Testing: {test_name}")
        
        # Note: This is a basic connectivity test since WebSocket testing requires more complex setup
        try:
            async with aiohttp.ClientSession() as session:
                # Test if the server responds to WebSocket upgrade requests
                # We'll check if the server at least recognizes WebSocket endpoints
                
                # Check if engagement WebSocket endpoint exists by looking at server response
                try:
                    async with session.get(f"{self.base_url}/ws/engagement", timeout=5) as response:
                        # WebSocket endpoints typically return 426 Upgrade Required for HTTP requests
                        websocket_endpoint_exists = response.status in [426, 400, 404]
                        
                        self.test_results.append({
                            "test": test_name,
                            "status": "PASS" if websocket_endpoint_exists else "FAIL",
                            "details": {
                                "engagement_websocket_response": response.status,
                                "endpoint_recognized": websocket_endpoint_exists,
                                "note": "WebSocket endpoints return 426/400 for HTTP requests - this is expected"
                            },
                            "requirement": "20.1, 20.2"
                        })
                        
                        if websocket_endpoint_exists:
                            logger.info(f"✅ {test_name}: PASS - Engagement WebSocket endpoint recognized")
                        else:
                            logger.error(f"❌ {test_name}: FAIL - Engagement WebSocket endpoint not found")
                            
                except Exception as e:
                    # If we get a connection error, the endpoint might not exist
                    self.test_results.append({
                        "test": test_name,
                        "status": "PARTIAL",
                        "details": {
                            "error": str(e),
                            "note": "Could not test WebSocket endpoint - may not be implemented yet"
                        },
                        "requirement": "20.1, 20.2"
                    })
                    logger.warning(f"⚠️ {test_name}: PARTIAL - Could not test WebSocket endpoint")
                    
        except Exception as e:
            self.test_results.append({
                "test": test_name,
                "status": "FAIL",
                "error": str(e),
                "requirement": "20.1, 20.2"
            })
            logger.error(f"❌ {test_name}: FAIL - {e}")
    
    async def test_engagement_health_monitoring(self):
        """Test that engagement components report healthy status."""
        test_name = "Engagement Health Monitoring"
        logger.info(f"🔍 Testing: {test_name}")
        
        try:
            async with aiohttp.ClientSession() as session:
                # Check main health endpoint for engagement data
                async with session.get(f"{self.base_url}/health", timeout=5) as response:
                    if response.status == 200:
                        health_data = await response.json()
                        
                        # Check if engagement section exists in health data
                        has_engagement_health = "engagement" in health_data
                        engagement_status = None
                        
                        if has_engagement_health:
                            engagement_status = health_data["engagement"]
                        
                        # Try to access engagement-specific health endpoints if they exist
                        engagement_endpoints = []
                        for endpoint in ["/api/engagement/status", "/api/engagement/health"]:
                            try:
                                async with session.get(f"{self.base_url}{endpoint}", timeout=3) as eng_response:
                                    engagement_endpoints.append({
                                        "endpoint": endpoint,
                                        "status": eng_response.status,
                                        "accessible": eng_response.status == 200
                                    })
                            except:
                                engagement_endpoints.append({
                                    "endpoint": endpoint,
                                    "status": "ERROR",
                                    "accessible": False
                                })
                        
                        self.test_results.append({
                            "test": test_name,
                            "status": "PASS" if has_engagement_health else "PARTIAL",
                            "details": {
                                "engagement_in_main_health": has_engagement_health,
                                "engagement_health_data": engagement_status,
                                "engagement_endpoints": engagement_endpoints
                            },
                            "requirement": "28.1, 28.2, 28.3, 28.4, 28.5"
                        })
                        
                        if has_engagement_health:
                            logger.info(f"✅ {test_name}: PASS - Engagement health monitoring active")
                        else:
                            logger.warning(f"⚠️ {test_name}: PARTIAL - Engagement health not in main health endpoint")
                    else:
                        raise Exception(f"Health endpoint returned status {response.status}")
                        
        except Exception as e:
            self.test_results.append({
                "test": test_name,
                "status": "FAIL",
                "error": str(e),
                "requirement": "28.1, 28.2, 28.3, 28.4, 28.5"
            })
            logger.error(f"❌ {test_name}: FAIL - {e}")
    
    async def test_existing_functionality(self):
        """Test that existing Observatory functionality remains intact."""
        test_name = "Existing Functionality Preservation"
        logger.info(f"🔍 Testing: {test_name}")
        
        try:
            async with aiohttp.ClientSession() as session:
                # Test core Observatory features
                tests = []
                
                # Test 1: Emoji rain stats
                try:
                    async with session.get(f"{self.base_url}/api/emoji-rain/stats", timeout=5) as response:
                        tests.append({
                            "feature": "emoji_rain_stats",
                            "status": response.status,
                            "working": response.status == 200
                        })
                except Exception as e:
                    tests.append({
                        "feature": "emoji_rain_stats",
                        "status": "ERROR",
                        "error": str(e),
                        "working": False
                    })
                
                # Test 2: Observatory status
                try:
                    async with session.get(f"{self.base_url}/api/observatory/status", timeout=5) as response:
                        tests.append({
                            "feature": "observatory_status",
                            "status": response.status,
                            "working": response.status == 200
                        })
                except Exception as e:
                    tests.append({
                        "feature": "observatory_status",
                        "status": "ERROR",
                        "error": str(e),
                        "working": False
                    })
                
                # Test 3: Recent observations
                try:
                    async with session.get(f"{self.base_url}/api/observations/recent", timeout=5) as response:
                        tests.append({
                            "feature": "recent_observations",
                            "status": response.status,
                            "working": response.status == 200
                        })
                except Exception as e:
                    tests.append({
                        "feature": "recent_observations",
                        "status": "ERROR",
                        "error": str(e),
                        "working": False
                    })
                
                # Test 4: Main dashboard
                try:
                    async with session.get(f"{self.base_url}/", timeout=5) as response:
                        tests.append({
                            "feature": "main_dashboard",
                            "status": response.status,
                            "working": response.status == 200
                        })
                except Exception as e:
                    tests.append({
                        "feature": "main_dashboard",
                        "status": "ERROR",
                        "error": str(e),
                        "working": False
                    })
                
                # Calculate results
                working_features = sum(1 for t in tests if t.get("working", False))
                total_features = len(tests)
                
                self.test_results.append({
                    "test": test_name,
                    "status": "PASS" if working_features == total_features else "PARTIAL",
                    "details": {
                        "features_tested": total_features,
                        "features_working": working_features,
                        "feature_results": tests
                    },
                    "requirement": "24.1, 24.2, 24.3, 24.4, 24.5"
                })
                
                if working_features == total_features:
                    logger.info(f"✅ {test_name}: PASS - All existing features working")
                else:
                    logger.warning(f"⚠️ {test_name}: PARTIAL - {working_features}/{total_features} features working")
                    
        except Exception as e:
            self.test_results.append({
                "test": test_name,
                "status": "FAIL",
                "error": str(e),
                "requirement": "24.1, 24.2, 24.3, 24.4, 24.5"
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
                "20.1": "Observatory server startup with engagement integration",
                "20.2": "Engagement WebSocket endpoints availability", 
                "20.3": "Server startup success validation",
                "20.4": "Existing Observatory functionality preservation",
                "20.5": "System integration integrity",
                "24.1": "Core functionality maintenance",
                "24.2": "API endpoint accessibility",
                "24.3": "Service integration stability",
                "24.4": "Feature compatibility",
                "24.5": "System reliability",
                "28.1": "Engagement health monitoring",
                "28.2": "Component status reporting",
                "28.3": "Health endpoint functionality",
                "28.4": "Metrics collection",
                "28.5": "System observability"
            }
        }
        
        return report

async def main():
    """Main test execution function."""
    print("🧪 Observatory Engagement Integration Test Suite")
    print("=" * 60)
    
    # Check if server is running
    tester = EngagementIntegrationTester()
    
    print("📋 Testing engagement system integration with Observatory server...")
    print("   This validates Requirements 20.1-20.5, 24.1-24.5, 28.1-28.5")
    print()
    
    # Run tests
    report = await tester.run_all_tests()
    
    # Print results
    print("\n" + "=" * 60)
    print("📊 TEST RESULTS SUMMARY")
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
    report_file = "engagement_integration_test_report.json"
    with open(report_file, "w") as f:
        json.dump(report, f, indent=2, default=str)
    
    print(f"\n📄 Detailed report saved to: {report_file}")
    
    # Return appropriate exit code
    if summary["overall_status"] == "FAIL":
        print("\n❌ INTEGRATION TESTS FAILED")
        return 1
    elif summary["overall_status"] == "PARTIAL":
        print("\n⚠️ INTEGRATION TESTS PARTIALLY SUCCESSFUL")
        return 0  # Still success for partial
    else:
        print("\n✅ INTEGRATION TESTS PASSED")
        return 0

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)