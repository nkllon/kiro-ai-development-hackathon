#!/usr/bin/env python3
"""
Bot Protection Whitelist Validation Script

Validates the Observatory bot protection whitelist configuration
and tests traffic patterns to ensure Error 1033 prevention.
"""

import json
import asyncio
import aiohttp
import time
from datetime import datetime
from typing import Dict, List, Any, Optional
from pathlib import Path


class BotProtectionValidator:
    """Validates Observatory bot protection whitelist configuration"""
    
    def __init__(self, domain: str = "observatory.nkllon.com"):
        self.domain = domain
        self.base_url = f"https://{domain}"
        self.validation_results = {}
        
    def _log_action(self, action: str, status: str, details: Optional[Dict[str, Any]] = None):
        """Log action in JSON format to stdout"""
        log_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "task": "4.0",
            "action": action,
            "status": status,
            "details": details or {}
        }
        print(json.dumps(log_entry))
        
    async def test_observatory_user_agents(self) -> Dict[str, Any]:
        """Test Observatory user agent whitelisting"""
        self._log_action("test_observatory_user_agents", "in_progress")
        
        user_agents = [
            "Observatory-Internal/1.0 (WebSocket-Fallback)",
            "BeastMode-Observatory/1.0",
            "Observatory-Polling/1.0",
            "Observatory-Health-Check/1.0"
        ]
        
        results = {
            "allowed_requests": 0,
            "blocked_requests": 0,
            "total_requests": len(user_agents),
            "user_agent_results": {}
        }
        
        async with aiohttp.ClientSession() as session:
            for user_agent in user_agents:
                headers = {"User-Agent": user_agent}
                try:
                    async with session.get(f"{self.base_url}/health", headers=headers, timeout=10) as response:
                        if response.status in [200, 404, 405]:  # Allowed
                            results["allowed_requests"] += 1
                            results["user_agent_results"][user_agent] = "allowed"
                        else:
                            results["blocked_requests"] += 1
                            results["user_agent_results"][user_agent] = f"blocked_{response.status}"
                except Exception as e:
                    results["blocked_requests"] += 1
                    results["user_agent_results"][user_agent] = f"error_{str(e)}"
                    
        success = results["allowed_requests"] >= results["total_requests"] * 0.8
        
        self._log_action("test_observatory_user_agents", "completed" if success else "error", {
            "success": success,
            "allowed_requests": results["allowed_requests"],
            "blocked_requests": results["blocked_requests"]
        })
        
        return results
        
    async def test_observatory_headers(self) -> Dict[str, Any]:
        """Test Observatory header-based whitelisting"""
        self._log_action("test_observatory_headers", "in_progress")
        
        headers_configs = [
            {
                "X-Observatory-Client": "internal-polling",
                "X-Polling-Reason": "websocket-fallback"
            },
            {
                "X-Observatory-Client": "internal-polling",
                "X-Observatory-Version": "1.0.0"
            },
            {
                "X-Observatory-Client": "internal-polling",
                "X-Observatory-Session": "internal-session"
            }
        ]
        
        results = {
            "allowed_requests": 0,
            "blocked_requests": 0,
            "total_requests": len(headers_configs),
            "header_results": {}
        }
        
        async with aiohttp.ClientSession() as session:
            for i, headers in enumerate(headers_configs):
                headers["User-Agent"] = "Observatory-Internal/1.0 (WebSocket-Fallback)"
                try:
                    async with session.get(f"{self.base_url}/api/observatory/status", headers=headers, timeout=10) as response:
                        if response.status in [200, 404, 405]:  # Allowed
                            results["allowed_requests"] += 1
                            results["header_results"][f"config_{i}"] = "allowed"
                        else:
                            results["blocked_requests"] += 1
                            results["header_results"][f"config_{i}"] = f"blocked_{response.status}"
                except Exception as e:
                    results["blocked_requests"] += 1
                    results["header_results"][f"config_{i}"] = f"error_{str(e)}"
                    
        success = results["allowed_requests"] >= results["total_requests"] * 0.8
        
        self._log_action("test_observatory_headers", "completed" if success else "error", {
            "success": success,
            "allowed_requests": results["allowed_requests"],
            "blocked_requests": results["blocked_requests"]
        })
        
        return results
        
    async def test_websocket_endpoints(self) -> Dict[str, Any]:
        """Test WebSocket endpoint whitelisting"""
        self._log_action("test_websocket_endpoints", "in_progress")
        
        websocket_endpoints = [
            "/ws/emoji-rain",
            "/ws/observatory",
            "/ws/anomalies",
            "/ws/doctor-status"
        ]
        
        results = {
            "allowed_requests": 0,
            "blocked_requests": 0,
            "total_requests": len(websocket_endpoints),
            "endpoint_results": {}
        }
        
        async with aiohttp.ClientSession() as session:
            for endpoint in websocket_endpoints:
                headers = {
                    "User-Agent": "Observatory-Internal/1.0 (WebSocket-Fallback)",
                    "Connection": "Upgrade",
                    "Upgrade": "websocket",
                    "Sec-WebSocket-Key": "dGhlIHNhbXBsZSBub25jZQ==",
                    "Sec-WebSocket-Version": "13"
                }
                try:
                    async with session.get(f"{self.base_url}{endpoint}", headers=headers, timeout=10) as response:
                        if response.status in [101, 200, 404, 405]:  # WebSocket upgrade or allowed
                            results["allowed_requests"] += 1
                            results["endpoint_results"][endpoint] = "allowed"
                        else:
                            results["blocked_requests"] += 1
                            results["endpoint_results"][endpoint] = f"blocked_{response.status}"
                except Exception as e:
                    results["blocked_requests"] += 1
                    results["endpoint_results"][endpoint] = f"error_{str(e)}"
                    
        success = results["allowed_requests"] >= results["total_requests"] * 0.8
        
        self._log_action("test_websocket_endpoints", "completed" if success else "error", {
            "success": success,
            "allowed_requests": results["allowed_requests"],
            "blocked_requests": results["blocked_requests"]
        })
        
        return results
        
    async def test_api_endpoints(self) -> Dict[str, Any]:
        """Test Observatory API endpoint whitelisting"""
        self._log_action("test_api_endpoints", "in_progress")
        
        api_endpoints = [
            "/api/emoji-rain/stats",
            "/api/observatory/status",
            "/api/anomalies/list",
            "/api/doctor/status",
            "/health"
        ]
        
        results = {
            "allowed_requests": 0,
            "blocked_requests": 0,
            "total_requests": len(api_endpoints),
            "endpoint_results": {}
        }
        
        async with aiohttp.ClientSession() as session:
            for endpoint in api_endpoints:
                headers = {
                    "User-Agent": "Observatory-Internal/1.0 (WebSocket-Fallback)",
                    "X-Observatory-Client": "internal-polling",
                    "X-Polling-Reason": "websocket-fallback"
                }
                try:
                    async with session.get(f"{self.base_url}{endpoint}", headers=headers, timeout=10) as response:
                        if response.status in [200, 404, 405]:  # Allowed
                            results["allowed_requests"] += 1
                            results["endpoint_results"][endpoint] = "allowed"
                        else:
                            results["blocked_requests"] += 1
                            results["endpoint_results"][endpoint] = f"blocked_{response.status}"
                except Exception as e:
                    results["blocked_requests"] += 1
                    results["endpoint_results"][endpoint] = f"error_{str(e)}"
                    
        success = results["allowed_requests"] >= results["total_requests"] * 0.8
        
        self._log_action("test_api_endpoints", "completed" if success else "error", {
            "success": success,
            "allowed_requests": results["allowed_requests"],
            "blocked_requests": results["blocked_requests"]
        })
        
        return results
        
    async def test_suspicious_traffic_blocking(self) -> Dict[str, Any]:
        """Test that suspicious traffic is properly blocked"""
        self._log_action("test_suspicious_traffic_blocking", "in_progress")
        
        suspicious_configs = [
            {
                "user_agent": "curl/7.68.0",
                "endpoint": "/wp-admin/"
            },
            {
                "user_agent": "python-requests/2.25.1", 
                "endpoint": "/admin/"
            },
            {
                "user_agent": "Mozilla/5.0 (compatible; Googlebot/2.1)",
                "endpoint": "/.env"
            }
        ]
        
        results = {
            "blocked_requests": 0,
            "allowed_requests": 0,
            "total_requests": len(suspicious_configs),
            "suspicious_results": {}
        }
        
        async with aiohttp.ClientSession() as session:
            for i, config in enumerate(suspicious_configs):
                headers = {"User-Agent": config["user_agent"]}
                try:
                    async with session.get(f"{self.base_url}{config['endpoint']}", headers=headers, timeout=10) as response:
                        if response.status in [403, 503, 429]:  # Blocked
                            results["blocked_requests"] += 1
                            results["suspicious_results"][f"config_{i}"] = "blocked"
                        else:
                            results["allowed_requests"] += 1
                            results["suspicious_results"][f"config_{i}"] = f"allowed_{response.status}"
                except Exception as e:
                    results["blocked_requests"] += 1
                    results["suspicious_results"][f"config_{i}"] = f"error_{str(e)}"
                    
        success = results["blocked_requests"] >= results["total_requests"] * 0.6  # 60% should be blocked
        
        self._log_action("test_suspicious_traffic_blocking", "completed" if success else "error", {
            "success": success,
            "blocked_requests": results["blocked_requests"],
            "allowed_requests": results["allowed_requests"]
        })
        
        return results
        
    async def test_rate_limiting(self) -> Dict[str, Any]:
        """Test rate limiting for Observatory traffic"""
        self._log_action("test_rate_limiting", "in_progress")
        
        headers = {
            "User-Agent": "Observatory-Internal/1.0 (WebSocket-Fallback)",
            "X-Observatory-Client": "internal-polling"
        }
        
        results = {
            "successful_requests": 0,
            "rate_limited_requests": 0,
            "total_requests": 20,  # Rapid requests
            "rate_limiting_effective": False
        }
        
        async with aiohttp.ClientSession() as session:
            for i in range(results["total_requests"]):
                try:
                    async with session.get(f"{self.base_url}/api/observatory/status", headers=headers, timeout=5) as response:
                        if response.status == 200:
                            results["successful_requests"] += 1
                        elif response.status == 429:  # Rate limited
                            results["rate_limited_requests"] += 1
                            results["rate_limiting_effective"] = True
                            break
                except Exception:
                    pass
                    
                # Small delay between requests
                await asyncio.sleep(0.1)
                
        success = results["rate_limiting_effective"] or results["successful_requests"] < results["total_requests"] * 0.8
        
        self._log_action("test_rate_limiting", "completed" if success else "error", {
            "success": success,
            "rate_limiting_effective": results["rate_limiting_effective"],
            "successful_requests": results["successful_requests"]
        })
        
        return results
        
    async def run_comprehensive_validation(self) -> Dict[str, Any]:
        """Run comprehensive bot protection validation"""
        self._log_action("run_comprehensive_validation", "in_progress")
        
        start_time = time.time()
        
        # Run all validation tests
        validation_tests = [
            ("user_agents", self.test_observatory_user_agents()),
            ("headers", self.test_observatory_headers()),
            ("websocket_endpoints", self.test_websocket_endpoints()),
            ("api_endpoints", self.test_api_endpoints()),
            ("suspicious_traffic", self.test_suspicious_traffic_blocking()),
            ("rate_limiting", self.test_rate_limiting())
        ]
        
        results = {}
        total_tests = len(validation_tests)
        passed_tests = 0
        
        for test_name, test_coro in validation_tests:
            try:
                test_result = await test_coro
                results[test_name] = test_result
                
                # Determine if test passed based on success criteria
                if test_name in ["user_agents", "headers", "websocket_endpoints", "api_endpoints"]:
                    test_passed = test_result.get("allowed_requests", 0) >= test_result.get("total_requests", 1) * 0.8
                elif test_name == "suspicious_traffic":
                    test_passed = test_result.get("blocked_requests", 0) >= test_result.get("total_requests", 1) * 0.6
                elif test_name == "rate_limiting":
                    test_passed = test_result.get("rate_limiting_effective", False) or test_result.get("successful_requests", 0) < test_result.get("total_requests", 1) * 0.8
                else:
                    test_passed = True
                    
                if test_passed:
                    passed_tests += 1
                    
            except Exception as e:
                results[test_name] = {"error": str(e)}
                
        end_time = time.time()
        duration = end_time - start_time
        
        # Calculate overall success
        success_rate = (passed_tests / total_tests) * 100
        overall_success = success_rate >= 80  # 80% pass rate required
        
        validation_summary = {
            "overall_success": overall_success,
            "success_rate": success_rate,
            "passed_tests": passed_tests,
            "total_tests": total_tests,
            "duration_seconds": duration,
            "test_results": results,
            "recommendations": []
        }
        
        # Generate recommendations
        if not overall_success:
            validation_summary["recommendations"].extend([
                "Review bot protection whitelist rules",
                "Check Cloudflare dashboard configuration",
                "Verify Observatory traffic patterns",
                "Test in staging environment"
            ])
        else:
            validation_summary["recommendations"].extend([
                "Monitor bot protection events",
                "Regular validation of whitelist rules",
                "Update rules as Observatory evolves"
            ])
            
        self._log_action("run_comprehensive_validation", "completed" if overall_success else "error", {
            "overall_success": overall_success,
            "success_rate": f"{success_rate:.1f}%",
            "passed_tests": passed_tests,
            "total_tests": total_tests,
            "duration_seconds": duration
        })
        
        return validation_summary


async def main():
    """Main validation function"""
    print("🔍 Observatory Bot Protection Whitelist Validation")
    print("=" * 60)
    
    validator = BotProtectionValidator()
    
    # Run comprehensive validation
    validation_results = await validator.run_comprehensive_validation()
    
    # Print summary
    print(f"\n📊 Validation Summary:")
    print(f"   Overall Success: {'✅' if validation_results['overall_success'] else '❌'}")
    print(f"   Success Rate: {validation_results['success_rate']:.1f}%")
    print(f"   Tests Passed: {validation_results['passed_tests']}/{validation_results['total_tests']}")
    print(f"   Duration: {validation_results['duration_seconds']:.2f}s")
    
    print(f"\n📋 Recommendations:")
    for recommendation in validation_results['recommendations']:
        print(f"   • {recommendation}")
    
    # Save validation results
    results_file = Path("config/bot_protection/validation_results.json")
    results_file.parent.mkdir(parents=True, exist_ok=True)
    
    with open(results_file, "w") as f:
        json.dump(validation_results, f, indent=2)
        
    print(f"\n💾 Validation results saved to: {results_file}")
    
    # Final completion log
    validator._log_action("main", "completed", {
        "summary": "Bot protection whitelist validation completed",
        "overall_success": validation_results['overall_success'],
        "success_rate": validation_results['success_rate']
    })
    
    return 0 if validation_results['overall_success'] else 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    exit(exit_code)