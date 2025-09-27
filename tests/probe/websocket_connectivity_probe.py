"""
WebSocket Connectivity Probe

Tests all WebSocket endpoints through Cloudflare tunnel, validates message round-trip,
connection stability, and concurrent connection support.
"""

import asyncio
import json
import time
import websockets
from datetime import datetime
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
import aiohttp


@dataclass
class EndpointResult:
    """Result of testing a specific WebSocket endpoint"""
    endpoint: str
    connection_success: bool
    message_round_trip_ms: Optional[float]
    connection_stability_percent: float
    concurrent_connections_supported: int
    error_message: Optional[str]
    test_duration_seconds: float


@dataclass
class ProbeResult:
    """Result of WebSocket connectivity probe"""
    probe_type: str
    endpoints_tested: Dict[str, EndpointResult]
    total_endpoints: int
    successful_endpoints: int
    success_rate: float
    overall_duration_seconds: float


class WebSocketConnectivityProbe:
    """Comprehensive WebSocket connectivity testing probe"""
    
    def __init__(self, base_url: str = "wss://observatory.nkllon.com"):
        self.base_url = base_url
        self.endpoints = [
            '/ws/emoji-rain',
            '/ws/observatory', 
            '/ws/anomalies',
            '/ws/doctor-status'
        ]
        self.test_duration = 300  # 5 minutes for stability testing
        self.concurrent_limit = 10
        
    def log_action(self, action: str, status: str, results: Dict[str, Any] = None) -> None:
        """Log probe activity in JSON format to stdout"""
        log_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "probe": "websocket_connectivity",
            "action": action,
            "status": status
        }
        if results:
            log_entry["results"] = results
        print(json.dumps(log_entry))
    
    async def probe_all_endpoints(self) -> ProbeResult:
        """Test all WebSocket endpoints through Cloudflare tunnel"""
        self.log_action("probe_all_endpoints", "in_progress", {
            "endpoints": self.endpoints,
            "base_url": self.base_url
        })
        
        start_time = time.time()
        results = {}
        
        # Test each endpoint individually
        for endpoint in self.endpoints:
            result = await self.test_endpoint_connectivity(endpoint)
            results[endpoint] = result
            
        end_time = time.time()
        total_duration = end_time - start_time
        
        # Calculate success metrics
        successful_endpoints = sum(1 for r in results.values() if r.connection_success)
        success_rate = (successful_endpoints / len(self.endpoints)) * 100
        
        probe_result = ProbeResult(
            probe_type="websocket_connectivity",
            endpoints_tested=results,
            total_endpoints=len(self.endpoints),
            successful_endpoints=successful_endpoints,
            success_rate=success_rate,
            overall_duration_seconds=total_duration
        )
        
        self.log_action("probe_all_endpoints", "completed", {
            "total_endpoints": len(self.endpoints),
            "successful_endpoints": successful_endpoints,
            "success_rate": f"{success_rate:.1f}%",
            "duration_seconds": total_duration
        })
        
        return probe_result
    
    async def test_endpoint_connectivity(self, endpoint: str) -> EndpointResult:
        """Test specific endpoint connectivity and message round-trip"""
        self.log_action("test_endpoint_connectivity", "in_progress", {
            "endpoint": endpoint
        })
        
        start_time = time.time()
        url = f"{self.base_url}{endpoint}"
        
        try:
            # Test basic connection
            connection_success = await self._test_basic_connection(url)
            
            # Test message round-trip
            round_trip_ms = await self._test_message_round_trip(url)
            
            # Test connection stability
            stability_percent = await self._test_connection_stability(url)
            
            # Test concurrent connections
            concurrent_supported = await self._test_concurrent_connections(url)
            
            end_time = time.time()
            duration = end_time - start_time
            
            result = EndpointResult(
                endpoint=endpoint,
                connection_success=connection_success,
                message_round_trip_ms=round_trip_ms,
                connection_stability_percent=stability_percent,
                concurrent_connections_supported=concurrent_supported,
                error_message=None,
                test_duration_seconds=duration
            )
            
            self.log_action("test_endpoint_connectivity", "completed", {
                "endpoint": endpoint,
                "connection_success": connection_success,
                "round_trip_ms": round_trip_ms,
                "stability_percent": stability_percent,
                "concurrent_supported": concurrent_supported
            })
            
            return result
            
        except Exception as e:
            end_time = time.time()
            duration = end_time - start_time
            
            result = EndpointResult(
                endpoint=endpoint,
                connection_success=False,
                message_round_trip_ms=None,
                connection_stability_percent=0.0,
                concurrent_connections_supported=0,
                error_message=str(e),
                test_duration_seconds=duration
            )
            
            self.log_action("test_endpoint_connectivity", "error", {
                "endpoint": endpoint,
                "error": str(e)
            })
            
            return result
    
    async def _test_basic_connection(self, url: str) -> bool:
        """Test basic WebSocket connection"""
        try:
            async with websockets.connect(url, timeout=10) as websocket:
                return websocket.open
        except Exception:
            return False
    
    async def _test_message_round_trip(self, url: str) -> Optional[float]:
        """Test message round-trip time"""
        try:
            async with websockets.connect(url, timeout=10) as websocket:
                test_message = json.dumps({
                    "type": "ping",
                    "timestamp": time.time(),
                    "test": True
                })
                
                start_time = time.time()
                await websocket.send(test_message)
                
                # Wait for response with timeout
                try:
                    response = await asyncio.wait_for(websocket.recv(), timeout=5.0)
                    end_time = time.time()
                    return (end_time - start_time) * 1000  # Convert to milliseconds
                except asyncio.TimeoutError:
                    return None
                    
        except Exception:
            return None
    
    async def _test_connection_stability(self, url: str) -> float:
        """Test connection stability over time"""
        stable_connections = 0
        total_attempts = 10
        
        for _ in range(total_attempts):
            try:
                async with websockets.connect(url, timeout=5) as websocket:
                    if websocket.open:
                        stable_connections += 1
                        await asyncio.sleep(0.5)  # Brief connection test
            except Exception:
                pass
                
        return (stable_connections / total_attempts) * 100
    
    async def _test_concurrent_connections(self, url: str) -> int:
        """Test concurrent connection support"""
        max_concurrent = 0
        
        for concurrent_count in range(1, self.concurrent_limit + 1):
            try:
                connections = []
                for _ in range(concurrent_count):
                    connection = websockets.connect(url, timeout=5)
                    connections.append(connection)
                
                # Wait for all connections to establish
                websockets_list = await asyncio.gather(*connections, return_exceptions=True)
                
                # Count successful connections
                successful = sum(1 for ws in websockets_list if not isinstance(ws, Exception) and ws.open)
                
                if successful == concurrent_count:
                    max_concurrent = concurrent_count
                else:
                    break
                    
                # Close connections
                for ws in websockets_list:
                    if not isinstance(ws, Exception):
                        await ws.close()
                        
            except Exception:
                break
                
        return max_concurrent
    
    async def test_http_fallback_endpoints(self) -> Dict[str, bool]:
        """Test HTTP fallback endpoints for comparison"""
        self.log_action("test_http_fallback_endpoints", "in_progress")
        
        http_endpoints = [
            '/api/emoji-rain/stats',
            '/api/observatory/status',
            '/api/anomalies/list',
            '/api/doctor/status'
        ]
        
        results = {}
        async with aiohttp.ClientSession() as session:
            for endpoint in http_endpoints:
                url = f"https://observatory.nkllon.com{endpoint}"
                try:
                    async with session.get(url, timeout=10) as response:
                        results[endpoint] = response.status == 200
                except Exception:
                    results[endpoint] = False
        
        self.log_action("test_http_fallback_endpoints", "completed", {
            "endpoints_tested": len(http_endpoints),
            "successful_endpoints": sum(results.values())
        })
        
        return results