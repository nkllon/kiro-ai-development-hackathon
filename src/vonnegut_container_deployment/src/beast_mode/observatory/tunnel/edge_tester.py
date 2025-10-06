"""
Cloudflare Edge Server Connectivity Testing System

Tests connectivity to multiple Cloudflare edge locations to validate
tunnel routing and identify potential connectivity issues.
"""

import asyncio
import json
import logging
import subprocess
import time
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass

from src.rm_ddd.core.unified_reflective_module import ReflectiveModule, ModuleHealth, ModuleStatus

logger = logging.getLogger(__name__)


@dataclass
class EdgeLocation:
    """Represents a Cloudflare edge location."""
    name: str
    ip_address: str
    region: str
    country: str
    priority: int = 1


class EdgeTester(ReflectiveModule):
    """
    Cloudflare edge server connectivity testing system.
    
    Provides testing capabilities for:
    - Multiple edge location connectivity
    - Latency measurement and analysis
    - Geographic distribution testing
    - Network path validation
    - Performance benchmarking
    """
    
    def __init__(self):
        """Initialize edge tester system."""
        super().__init__()
        self.module_id = "edge_tester"
        
        # Edge locations to test
        self.edge_locations = [
            EdgeLocation("Cloudflare DNS Primary", "1.1.1.1", "Global", "Global", 1),
            EdgeLocation("Cloudflare DNS Secondary", "1.0.0.1", "Global", "Global", 1),
            EdgeLocation("Cloudflare IPv6 Primary", "2606:4700:4700::1111", "Global", "Global", 2),
            EdgeLocation("Cloudflare IPv6 Secondary", "2606:4700:4700::1001", "Global", "Global", 2),
        ]
        
        # Performance tracking
        self._test_count = 0
        self._successful_tests = 0
        self._failed_tests = 0
        self._test_results: List[Dict[str, Any]] = []
        
        logger.info("🌐 EdgeTester initialized - Ready for connectivity testing")
    
    async def test_all_edge_locations(self, timeout_seconds: int = 10) -> Dict[str, Any]:
        """Test connectivity to all edge locations.
        
        Args:
            timeout_seconds: Timeout for each connectivity test
            
        Returns:
            Dictionary containing comprehensive test results
        """
        start_time = time.time()
        self.log_action("edge_connectivity_test", "in_progress")
        
        try:
            results = {
                "timestamp": datetime.now().isoformat(),
                "test_summary": {},
                "location_results": {},
                "performance_metrics": {},
                "recommendations": []
            }
            
            # Test each edge location
            location_results = {}
            total_latency = 0
            successful_locations = 0
            
            for location in self.edge_locations:
                location_result = await self._test_single_location(location, timeout_seconds)
                location_results[location.name] = location_result
                
                if location_result["reachable"]:
                    successful_locations += 1
                    total_latency += location_result.get("latency_ms", 0)
            
            # Calculate summary metrics
            total_locations = len(self.edge_locations)
            success_rate = successful_locations / total_locations if total_locations > 0 else 0
            average_latency = total_latency / successful_locations if successful_locations > 0 else 0
            
            # Determine overall status
            if success_rate >= 0.8:
                overall_status = "healthy"
            elif success_rate >= 0.5:
                overall_status = "warning"
            else:
                overall_status = "error"
            
            # Compile results
            results["test_summary"] = {
                "overall_status": overall_status,
                "success_rate": success_rate,
                "successful_locations": successful_locations,
                "total_locations": total_locations,
                "average_latency_ms": average_latency,
                "test_duration_ms": (time.time() - start_time) * 1000
            }
            
            results["location_results"] = location_results
            
            # Generate performance metrics
            results["performance_metrics"] = self._analyze_performance_metrics(location_results)
            
            # Generate recommendations
            results["recommendations"] = self._generate_edge_recommendations(results)
            
            # Update tracking metrics
            self._test_count += 1
            if overall_status == "healthy":
                self._successful_tests += 1
            else:
                self._failed_tests += 1
            
            self._test_results.append(results)
            
            # Keep only last 50 results
            if len(self._test_results) > 50:
                self._test_results = self._test_results[-50:]
            
            self.log_action("edge_connectivity_test", "completed", {
                "success_rate": success_rate,
                "average_latency_ms": average_latency,
                "overall_status": overall_status
            })
            
            return results
            
        except Exception as e:
            self._failed_tests += 1
            error_msg = f"Edge connectivity test failed: {e}"
            logger.error(error_msg)
            
            self.log_action("edge_connectivity_test", "error", {"error": str(e)})
            
            return {
                "timestamp": datetime.now().isoformat(),
                "test_summary": {
                    "overall_status": "error",
                    "error": error_msg
                },
                "location_results": {},
                "performance_metrics": {},
                "recommendations": ["Fix edge connectivity testing system"]
            }
    
    async def _test_single_location(self, location: EdgeLocation, timeout_seconds: int) -> Dict[str, Any]:
        """Test connectivity to a single edge location.
        
        Args:
            location: Edge location to test
            timeout_seconds: Test timeout
            
        Returns:
            Dictionary containing test results for the location
        """
        try:
            start_time = time.time()
            
            # Use ping for IPv4 addresses
            if ":" not in location.ip_address:
                result = subprocess.run(
                    ["ping", "-c", "1", "-W", str(timeout_seconds), location.ip_address],
                    capture_output=True,
                    text=True,
                    timeout=timeout_seconds + 5
                )
            else:
                # Use ping6 for IPv6 addresses
                result = subprocess.run(
                    ["ping6", "-c", "1", "-W", str(timeout_seconds), location.ip_address],
                    capture_output=True,
                    text=True,
                    timeout=timeout_seconds + 5
                )
            
            latency_ms = (time.time() - start_time) * 1000
            reachable = result.returncode == 0
            
            # Parse ping output for additional details
            response_details = self._parse_ping_output(result.stdout if reachable else result.stderr)
            
            return {
                "location_name": location.name,
                "ip_address": location.ip_address,
                "region": location.region,
                "country": location.country,
                "reachable": reachable,
                "latency_ms": latency_ms,
                "response_details": response_details,
                "timestamp": datetime.now().isoformat()
            }
            
        except subprocess.TimeoutExpired:
            return {
                "location_name": location.name,
                "ip_address": location.ip_address,
                "region": location.region,
                "country": location.country,
                "reachable": False,
                "latency_ms": timeout_seconds * 1000,
                "error": "Connection timeout",
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            return {
                "location_name": location.name,
                "ip_address": location.ip_address,
                "region": location.region,
                "country": location.country,
                "reachable": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def _parse_ping_output(self, ping_output: str) -> Dict[str, Any]:
        """Parse ping command output for additional details.
        
        Args:
            ping_output: Raw ping command output
            
        Returns:
            Dictionary containing parsed ping details
        """
        details = {}
        
        try:
            lines = ping_output.strip().split('\n')
            
            # Look for latency information
            for line in lines:
                if "time=" in line:
                    # Extract time value
                    time_part = line.split("time=")[1].split()[0]
                    if "ms" in time_part:
                        details["ping_time_ms"] = float(time_part.replace("ms", ""))
                    break
            
            # Look for packet loss information
            for line in lines:
                if "packet loss" in line:
                    details["packet_loss_info"] = line.strip()
                    break
            
            # Look for statistics
            for line in lines:
                if "min/avg/max" in line:
                    details["statistics"] = line.strip()
                    break
            
        except Exception as e:
            details["parse_error"] = str(e)
        
        return details
    
    def _analyze_performance_metrics(self, location_results: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze performance metrics from location results.
        
        Args:
            location_results: Results from all location tests
            
        Returns:
            Dictionary containing performance analysis
        """
        metrics = {
            "latency_analysis": {},
            "connectivity_patterns": {},
            "performance_trends": {}
        }
        
        # Analyze latency
        latencies = []
        reachable_locations = []
        
        for location_name, result in location_results.items():
            if result.get("reachable", False):
                latencies.append(result.get("latency_ms", 0))
                reachable_locations.append(location_name)
        
        if latencies:
            metrics["latency_analysis"] = {
                "min_latency_ms": min(latencies),
                "max_latency_ms": max(latencies),
                "average_latency_ms": sum(latencies) / len(latencies),
                "latency_variance": self._calculate_variance(latencies)
            }
        
        # Analyze connectivity patterns
        metrics["connectivity_patterns"] = {
            "total_tested": len(location_results),
            "reachable_count": len(reachable_locations),
            "unreachable_count": len(location_results) - len(reachable_locations),
            "reachable_locations": reachable_locations
        }
        
        return metrics
    
    def _calculate_variance(self, values: List[float]) -> float:
        """Calculate variance of a list of values.
        
        Args:
            values: List of numeric values
            
        Returns:
            Variance value
        """
        if len(values) < 2:
            return 0.0
        
        mean = sum(values) / len(values)
        variance = sum((x - mean) ** 2 for x in values) / len(values)
        return variance
    
    def _generate_edge_recommendations(self, test_results: Dict[str, Any]) -> List[str]:
        """Generate recommendations based on edge test results.
        
        Args:
            test_results: Complete test results
            
        Returns:
            List of actionable recommendations
        """
        recommendations = []
        
        test_summary = test_results.get("test_summary", {})
        success_rate = test_summary.get("success_rate", 0)
        average_latency = test_summary.get("average_latency_ms", 0)
        
        # Connectivity recommendations
        if success_rate < 0.5:
            recommendations.append("Critical connectivity issues: Check network configuration and firewall settings")
        elif success_rate < 0.8:
            recommendations.append("Partial connectivity issues: Some edge locations unreachable")
        
        # Latency recommendations
        if average_latency > 200:
            recommendations.append("High latency detected: Consider optimizing network routing or using closer edge locations")
        elif average_latency > 100:
            recommendations.append("Moderate latency: Monitor network performance and consider optimization")
        
        # Performance recommendations
        performance_metrics = test_results.get("performance_metrics", {})
        latency_analysis = performance_metrics.get("latency_analysis", {})
        
        if latency_analysis.get("latency_variance", 0) > 1000:
            recommendations.append("High latency variance: Network performance is inconsistent")
        
        # General recommendations
        if not recommendations:
            recommendations.append("Edge connectivity tests completed successfully - no issues detected")
        
        return recommendations
    
    async def test_specific_location(self, location_name: str, timeout_seconds: int = 10) -> Dict[str, Any]:
        """Test connectivity to a specific edge location.
        
        Args:
            location_name: Name of the location to test
            timeout_seconds: Test timeout
            
        Returns:
            Dictionary containing test results for the specific location
        """
        self.log_action("specific_location_test", "in_progress", {"location": location_name})
        
        try:
            # Find the location
            location = None
            for loc in self.edge_locations:
                if loc.name == location_name:
                    location = loc
                    break
            
            if not location:
                return {
                    "timestamp": datetime.now().isoformat(),
                    "error": f"Location '{location_name}' not found",
                    "available_locations": [loc.name for loc in self.edge_locations]
                }
            
            # Test the location
            result = await self._test_single_location(location, timeout_seconds)
            
            self.log_action("specific_location_test", "completed", {
                "location": location_name,
                "reachable": result.get("reachable", False)
            })
            
            return result
            
        except Exception as e:
            error_msg = f"Specific location test failed: {e}"
            logger.error(error_msg)
            
            self.log_action("specific_location_test", "error", {"error": str(e)})
            
            return {
                "timestamp": datetime.now().isoformat(),
                "error": error_msg,
                "location": location_name
            }
    
    def get_test_history(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent test history.
        
        Args:
            limit: Maximum number of recent tests to return
            
        Returns:
            List of recent test results
        """
        return self._test_results[-limit:] if self._test_results else []
    
    def log_action(self, action: str, status: str, details: Dict[str, Any] = None):
        """Log action in JSON format as required."""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "task": "3.2",
            "action": action,
            "status": status,
            "details": details or {}
        }
        print(json.dumps(log_entry))
    
    async def get_health_status(self) -> ModuleHealth:
        """Get current module health status.
        
        Returns:
            ModuleHealth object with current status
        """
        try:
            # Calculate success rate
            success_rate = self._successful_tests / self._test_count if self._test_count > 0 else 1.0
            
            # Determine status
            if success_rate >= 0.8:
                status = ModuleStatus.HEALTHY
                health_score = success_rate
                issues = []
            elif success_rate >= 0.5:
                status = ModuleStatus.WARNING
                health_score = success_rate
                issues = ["Edge connectivity warnings detected"]
            else:
                status = ModuleStatus.ERROR
                health_score = success_rate
                issues = ["Edge connectivity failures detected"]
            
            return ModuleHealth(
                module_id=self.module_id,
                status=status,
                health_score=health_score,
                issues=issues,
                last_check=datetime.now(),
                uptime_seconds=(datetime.now() - self._start_time).total_seconds(),
                error_count=self._failed_tests,
                warning_count=0
            )
            
        except Exception as e:
            return ModuleHealth(
                module_id=self.module_id,
                status=ModuleStatus.ERROR,
                health_score=0.0,
                issues=[f"Health status check failed: {e}"],
                last_check=datetime.now(),
                uptime_seconds=(datetime.now() - self._start_time).total_seconds(),
                error_count=self._failed_tests + 1,
                warning_count=0
            )