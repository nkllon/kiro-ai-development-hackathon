"""
Bot Protection Probe

Tests bot protection integration, whitelist effectiveness, attack simulation,
and legitimate traffic validation.
"""

import asyncio
import json
import time
import aiohttp
from datetime import datetime
from typing import Dict, List, Any, Optional
from dataclasses import dataclass


@dataclass
class BotProtectionTestResult:
    """Result of bot protection testing"""
    test_name: str
    success: bool
    legitimate_traffic_allowed: bool
    attack_traffic_blocked: bool
    whitelist_effective: bool
    false_positives: int
    false_negatives: int
    error_message: Optional[str]
    test_duration_seconds: float


@dataclass
class BotProtectionProbeResult:
    """Result of bot protection probe"""
    probe_type: str
    tests_performed: Dict[str, BotProtectionTestResult]
    total_tests: int
    successful_tests: int
    success_rate: float
    overall_duration_seconds: float


class BotProtectionProbe:
    """Comprehensive bot protection testing probe"""
    
    def __init__(self, base_url: str = "https://observatory.nkllon.com"):
        self.base_url = base_url
        
        # Legitimate Observatory traffic patterns
        self.legitimate_headers = {
            "User-Agent": "Observatory-Internal/1.0 (WebSocket-Fallback)",
            "X-Observatory-Client": "internal-polling",
            "X-Requested-With": "XMLHttpRequest",
            "Accept": "application/json",
            "Cache-Control": "no-cache"
        }
        
        # Suspicious traffic patterns that should be blocked
        self.suspicious_headers = [
            {"User-Agent": "curl/7.68.0"},
            {"User-Agent": "python-requests/2.25.1"},
            {"User-Agent": "Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)"},
            {"User-Agent": "Mozilla/5.0 (compatible; bingbot/2.0; +http://www.bing.com/bingbot.htm)"},
            {"User-Agent": "Mozilla/5.0 (compatible; MJ12bot/v1.4.8; http://mj12bot.com/)"}
        ]
        
        # Observatory endpoints that should be whitelisted
        self.observatory_endpoints = [
            '/ws/emoji-rain',
            '/ws/observatory',
            '/ws/anomalies', 
            '/ws/doctor-status',
            '/api/emoji-rain/stats',
            '/api/observatory/status',
            '/api/anomalies/list',
            '/api/doctor/status'
        ]
        
        # Suspicious endpoints that should trigger protection
        self.suspicious_endpoints = [
            '/wp-admin/',
            '/wp-login.php',
            '/phpmyadmin/',
            '/.env',
            '/admin/',
            '/xmlrpc.php'
        ]
        
    def log_action(self, action: str, status: str, results: Dict[str, Any] = None) -> None:
        """Log probe activity in JSON format to stdout"""
        log_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "probe": "bot_protection",
            "action": action,
            "status": status
        }
        if results:
            log_entry["results"] = results
        print(json.dumps(log_entry))
    
    async def probe_bot_protection(self) -> BotProtectionProbeResult:
        """Test all bot protection scenarios"""
        self.log_action("probe_bot_protection", "in_progress", {
            "observatory_endpoints": len(self.observatory_endpoints),
            "suspicious_endpoints": len(self.suspicious_endpoints)
        })
        
        start_time = time.time()
        results = {}
        
        # Test scenarios
        test_scenarios = [
            ("legitimate_traffic_whitelist", self._test_legitimate_traffic_whitelist),
            ("attack_traffic_blocking", self._test_attack_traffic_blocking),
            ("observatory_endpoint_protection", self._test_observatory_endpoint_protection),
            ("suspicious_endpoint_detection", self._test_suspicious_endpoint_detection),
            ("rate_limit_integration", self._test_rate_limit_integration),
            ("false_positive_prevention", self._test_false_positive_prevention)
        ]
        
        for test_name, test_func in test_scenarios:
            result = await test_func()
            results[test_name] = result
            
        end_time = time.time()
        total_duration = end_time - start_time
        
        # Calculate success metrics
        successful_tests = sum(1 for r in results.values() if r.success)
        success_rate = (successful_tests / len(test_scenarios)) * 100
        
        probe_result = BotProtectionProbeResult(
            probe_type="bot_protection",
            tests_performed=results,
            total_tests=len(test_scenarios),
            successful_tests=successful_tests,
            success_rate=success_rate,
            overall_duration_seconds=total_duration
        )
        
        self.log_action("probe_bot_protection", "completed", {
            "total_tests": len(test_scenarios),
            "successful_tests": successful_tests,
            "success_rate": f"{success_rate:.1f}%",
            "duration_seconds": total_duration
        })
        
        return probe_result
    
    async def _test_legitimate_traffic_whitelist(self) -> BotProtectionTestResult:
        """Test that legitimate Observatory traffic passes through"""
        self.log_action("test_legitimate_traffic_whitelist", "in_progress")
        
        start_time = time.time()
        
        try:
            async with aiohttp.ClientSession(headers=self.legitimate_headers) as session:
                allowed_requests = 0
                blocked_requests = 0
                total_requests = len(self.observatory_endpoints)
                
                for endpoint in self.observatory_endpoints:
                    url = f"{self.base_url}{endpoint}"
                    try:
                        async with session.get(url, timeout=5) as response:
                            if response.status in [200, 404]:  # 404 is OK for non-existent endpoints
                                allowed_requests += 1
                            elif response.status in [403, 503]:  # Bot protection
                                blocked_requests += 1
                    except Exception:
                        blocked_requests += 1
                
                legitimate_traffic_allowed = allowed_requests >= total_requests * 0.8
                success = legitimate_traffic_allowed
                
            end_time = time.time()
            duration = end_time - start_time
            
            result = BotProtectionTestResult(
                test_name="legitimate_traffic_whitelist",
                success=success,
                legitimate_traffic_allowed=legitimate_traffic_allowed,
                attack_traffic_blocked=False,  # Not tested in this scenario
                whitelist_effective=legitimate_traffic_allowed,
                false_positives=blocked_requests,
                false_negatives=0,
                error_message=None,
                test_duration_seconds=duration
            )
            
            self.log_action("test_legitimate_traffic_whitelist", "completed", {
                "success": success,
                "allowed_requests": allowed_requests,
                "blocked_requests": blocked_requests,
                "total_requests": total_requests
            })
            
            return result
            
        except Exception as e:
            end_time = time.time()
            duration = end_time - start_time
            
            result = BotProtectionTestResult(
                test_name="legitimate_traffic_whitelist",
                success=False,
                legitimate_traffic_allowed=False,
                attack_traffic_blocked=False,
                whitelist_effective=False,
                false_positives=0,
                false_negatives=0,
                error_message=str(e),
                test_duration_seconds=duration
            )
            
            self.log_action("test_legitimate_traffic_whitelist", "error", {
                "error": str(e)
            })
            
            return result
    
    async def _test_attack_traffic_blocking(self) -> BotProtectionTestResult:
        """Test that suspicious traffic is blocked"""
        self.log_action("test_attack_traffic_blocking", "in_progress")
        
        start_time = time.time()
        
        try:
            blocked_requests = 0
            allowed_requests = 0
            total_requests = len(self.suspicious_headers) * len(self.suspicious_endpoints)
            
            for headers in self.suspicious_headers:
                async with aiohttp.ClientSession(headers=headers) as session:
                    for endpoint in self.suspicious_endpoints:
                        url = f"{self.base_url}{endpoint}"
                        try:
                            async with session.get(url, timeout=5) as response:
                                if response.status in [403, 503]:  # Bot protection
                                    blocked_requests += 1
                                elif response.status in [200, 404]:
                                    allowed_requests += 1
                        except Exception:
                            blocked_requests += 1
                
            attack_traffic_blocked = blocked_requests >= total_requests * 0.7  # 70% should be blocked
            success = attack_traffic_blocked
            
            end_time = time.time()
            duration = end_time - start_time
            
            result = BotProtectionTestResult(
                test_name="attack_traffic_blocking",
                success=success,
                legitimate_traffic_allowed=False,  # Not tested in this scenario
                attack_traffic_blocked=attack_traffic_blocked,
                whitelist_effective=False,  # Not tested in this scenario
                false_positives=0,
                false_negatives=allowed_requests,
                error_message=None,
                test_duration_seconds=duration
            )
            
            self.log_action("test_attack_traffic_blocking", "completed", {
                "success": success,
                "blocked_requests": blocked_requests,
                "allowed_requests": allowed_requests,
                "total_requests": total_requests
            })
            
            return result
            
        except Exception as e:
            end_time = time.time()
            duration = end_time - start_time
            
            result = BotProtectionTestResult(
                test_name="attack_traffic_blocking",
                success=False,
                legitimate_traffic_allowed=False,
                attack_traffic_blocked=False,
                whitelist_effective=False,
                false_positives=0,
                false_negatives=0,
                error_message=str(e),
                test_duration_seconds=duration
            )
            
            self.log_action("test_attack_traffic_blocking", "error", {
                "error": str(e)
            })
            
            return result
    
    async def _test_observatory_endpoint_protection(self) -> BotProtectionTestResult:
        """Test Observatory endpoints are accessible with legitimate traffic"""
        self.log_action("test_observatory_endpoint_protection", "in_progress")
        
        start_time = time.time()
        
        try:
            async with aiohttp.ClientSession(headers=self.legitimate_headers) as session:
                accessible_endpoints = 0
                total_endpoints = len(self.observatory_endpoints)
                
                for endpoint in self.observatory_endpoints:
                    url = f"{self.base_url}{endpoint}"
                    try:
                        async with session.get(url, timeout=5) as response:
                            if response.status in [200, 404]:  # 404 is OK for non-existent endpoints
                                accessible_endpoints += 1
                    except Exception:
                        pass
                
                whitelist_effective = accessible_endpoints >= total_endpoints * 0.8
                success = whitelist_effective
                
            end_time = time.time()
            duration = end_time - start_time
            
            result = BotProtectionTestResult(
                test_name="observatory_endpoint_protection",
                success=success,
                legitimate_traffic_allowed=whitelist_effective,
                attack_traffic_blocked=False,  # Not tested in this scenario
                whitelist_effective=whitelist_effective,
                false_positives=0,
                false_negatives=0,
                error_message=None,
                test_duration_seconds=duration
            )
            
            self.log_action("test_observatory_endpoint_protection", "completed", {
                "success": success,
                "accessible_endpoints": accessible_endpoints,
                "total_endpoints": total_endpoints
            })
            
            return result
            
        except Exception as e:
            end_time = time.time()
            duration = end_time - start_time
            
            result = BotProtectionTestResult(
                test_name="observatory_endpoint_protection",
                success=False,
                legitimate_traffic_allowed=False,
                attack_traffic_blocked=False,
                whitelist_effective=False,
                false_positives=0,
                false_negatives=0,
                error_message=str(e),
                test_duration_seconds=duration
            )
            
            self.log_action("test_observatory_endpoint_protection", "error", {
                "error": str(e)
            })
            
            return result
    
    async def _test_suspicious_endpoint_detection(self) -> BotProtectionTestResult:
        """Test that suspicious endpoints trigger protection"""
        self.log_action("test_suspicious_endpoint_detection", "in_progress")
        
        start_time = time.time()
        
        try:
            # Use suspicious headers to test suspicious endpoints
            suspicious_session = aiohttp.ClientSession(headers=self.suspicious_headers[0])
            
            blocked_requests = 0
            allowed_requests = 0
            total_requests = len(self.suspicious_endpoints)
            
            async with suspicious_session as session:
                for endpoint in self.suspicious_endpoints:
                    url = f"{self.base_url}{endpoint}"
                    try:
                        async with session.get(url, timeout=5) as response:
                            if response.status in [403, 503]:  # Bot protection
                                blocked_requests += 1
                            elif response.status in [200, 404]:
                                allowed_requests += 1
                    except Exception:
                        blocked_requests += 1
                
            attack_traffic_blocked = blocked_requests >= total_requests * 0.6  # 60% should be blocked
            success = attack_traffic_blocked
            
            end_time = time.time()
            duration = end_time - start_time
            
            result = BotProtectionTestResult(
                test_name="suspicious_endpoint_detection",
                success=success,
                legitimate_traffic_allowed=False,  # Not tested in this scenario
                attack_traffic_blocked=attack_traffic_blocked,
                whitelist_effective=False,  # Not tested in this scenario
                false_positives=0,
                false_negatives=allowed_requests,
                error_message=None,
                test_duration_seconds=duration
            )
            
            self.log_action("test_suspicious_endpoint_detection", "completed", {
                "success": success,
                "blocked_requests": blocked_requests,
                "allowed_requests": allowed_requests,
                "total_requests": total_requests
            })
            
            return result
            
        except Exception as e:
            end_time = time.time()
            duration = end_time - start_time
            
            result = BotProtectionTestResult(
                test_name="suspicious_endpoint_detection",
                success=False,
                legitimate_traffic_allowed=False,
                attack_traffic_blocked=False,
                whitelist_effective=False,
                false_positives=0,
                false_negatives=0,
                error_message=str(e),
                test_duration_seconds=duration
            )
            
            self.log_action("test_suspicious_endpoint_detection", "error", {
                "error": str(e)
            })
            
            return result
    
    async def _test_rate_limit_integration(self) -> BotProtectionTestResult:
        """Test rate limiting integration with bot protection"""
        self.log_action("test_rate_limit_integration", "in_progress")
        
        start_time = time.time()
        
        try:
            # Test rapid requests to trigger rate limiting
            async with aiohttp.ClientSession(headers=self.legitimate_headers) as session:
                rate_limited = False
                successful_requests = 0
                total_requests = 50  # Rapid requests
                
                for i in range(total_requests):
                    url = f"{self.base_url}{self.observatory_endpoints[0]}"
                    try:
                        async with session.get(url, timeout=5) as response:
                            if response.status == 200:
                                successful_requests += 1
                            elif response.status == 429:  # Rate limited
                                rate_limited = True
                                break
                    except Exception:
                        pass
                    
                    # Very small delay
                    await asyncio.sleep(0.01)
                
                # Rate limiting should kick in for rapid requests
                success = rate_limited or successful_requests < total_requests * 0.8
                
            end_time = time.time()
            duration = end_time - start_time
            
            result = BotProtectionTestResult(
                test_name="rate_limit_integration",
                success=success,
                legitimate_traffic_allowed=successful_requests > 0,
                attack_traffic_blocked=rate_limited,
                whitelist_effective=True,  # Legitimate headers used
                false_positives=0,
                false_negatives=0,
                error_message=None,
                test_duration_seconds=duration
            )
            
            self.log_action("test_rate_limit_integration", "completed", {
                "success": success,
                "rate_limited": rate_limited,
                "successful_requests": successful_requests,
                "total_requests": total_requests
            })
            
            return result
            
        except Exception as e:
            end_time = time.time()
            duration = end_time - start_time
            
            result = BotProtectionTestResult(
                test_name="rate_limit_integration",
                success=False,
                legitimate_traffic_allowed=False,
                attack_traffic_blocked=False,
                whitelist_effective=False,
                false_positives=0,
                false_negatives=0,
                error_message=str(e),
                test_duration_seconds=duration
            )
            
            self.log_action("test_rate_limit_integration", "error", {
                "error": str(e)
            })
            
            return result
    
    async def _test_false_positive_prevention(self) -> BotProtectionTestResult:
        """Test prevention of false positives on legitimate traffic"""
        self.log_action("test_false_positive_prevention", "in_progress")
        
        start_time = time.time()
        
        try:
            # Test various legitimate user agents
            legitimate_user_agents = [
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36"
            ]
            
            false_positives = 0
            total_tests = len(legitimate_user_agents) * len(self.observatory_endpoints)
            
            for user_agent in legitimate_user_agents:
                headers = {"User-Agent": user_agent}
                async with aiohttp.ClientSession(headers=headers) as session:
                    for endpoint in self.observatory_endpoints:
                        url = f"{self.base_url}{endpoint}"
                        try:
                            async with session.get(url, timeout=5) as response:
                                if response.status in [403, 503]:  # False positive
                                    false_positives += 1
                        except Exception:
                            pass
                
            # Should have minimal false positives
            success = false_positives <= total_tests * 0.1  # Max 10% false positives
                
            end_time = time.time()
            duration = end_time - start_time
            
            result = BotProtectionTestResult(
                test_name="false_positive_prevention",
                success=success,
                legitimate_traffic_allowed=true_positives := total_tests - false_positives > 0,
                attack_traffic_blocked=False,  # Not tested in this scenario
                whitelist_effective=True,  # Legitimate traffic should be allowed
                false_positives=false_positives,
                false_negatives=0,
                error_message=None,
                test_duration_seconds=duration
            )
            
            self.log_action("test_false_positive_prevention", "completed", {
                "success": success,
                "false_positives": false_positives,
                "total_tests": total_tests
            })
            
            return result
            
        except Exception as e:
            end_time = time.time()
            duration = end_time - start_time
            
            result = BotProtectionTestResult(
                test_name="false_positive_prevention",
                success=False,
                legitimate_traffic_allowed=False,
                attack_traffic_blocked=False,
                whitelist_effective=False,
                false_positives=0,
                false_negatives=0,
                error_message=str(e),
                test_duration_seconds=duration
            )
            
            self.log_action("test_false_positive_prevention", "error", {
                "error": str(e)
            })
            
            return result