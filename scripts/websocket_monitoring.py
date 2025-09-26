#!/usr/bin/env python3
"""
WebSocket Connectivity Monitoring and Alerting

This script provides comprehensive monitoring for WebSocket connectivity
through Cloudflare tunnels with alerting and health checks.
"""

import asyncio
import json
import sys
import time
import websockets
import requests
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/websocket_monitoring.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

@dataclass
class WebSocketHealthCheck:
    """WebSocket health check result"""
    timestamp: str
    endpoint: str
    status: str  # 'healthy', 'unhealthy', 'timeout', 'error'
    response_time_ms: float
    error_message: Optional[str] = None
    connection_id: Optional[str] = None
    data_received: Optional[int] = None

@dataclass
class MonitoringConfig:
    """Monitoring configuration"""
    check_interval: float = 30.0  # seconds
    timeout: float = 10.0  # seconds
    max_retries: int = 3
    alert_threshold: int = 3  # consecutive failures before alert
    endpoints: List[str] = None
    alert_webhook: Optional[str] = None
    
    def __post_init__(self):
        if self.endpoints is None:
            self.endpoints = [
                "wss://observatory.nkllon.com/ws/emoji-rain",
                "ws://localhost:8888/ws/emoji-rain"
            ]

class WebSocketMonitor:
    """WebSocket connectivity monitor"""
    
    def __init__(self, config: MonitoringConfig):
        self.config = config
        self.health_history: List[WebSocketHealthCheck] = []
        self.consecutive_failures = 0
        self.last_alert_time = None
        self.monitoring_active = False
        
        # Create logs directory
        Path("logs").mkdir(exist_ok=True)
        
        logger.info(f"🔧 WebSocket Monitor initialized with {len(config.endpoints)} endpoints")
    
    async def check_websocket_health(self, endpoint: str) -> WebSocketHealthCheck:
        """Check health of a single WebSocket endpoint"""
        start_time = time.time()
        timestamp = datetime.now().isoformat()
        
        try:
            # Determine if this is a secure WebSocket
            if endpoint.startswith('wss://'):
                # Test through Cloudflare tunnel
                result = await self._test_secure_websocket(endpoint, start_time, timestamp)
            else:
                # Test local WebSocket
                result = await self._test_local_websocket(endpoint, start_time, timestamp)
            
            return result
            
        except Exception as e:
            response_time = (time.time() - start_time) * 1000
            logger.error(f"❌ WebSocket health check failed for {endpoint}: {e}")
            
            return WebSocketHealthCheck(
                timestamp=timestamp,
                endpoint=endpoint,
                status='error',
                response_time_ms=response_time,
                error_message=str(e)
            )
    
    async def _test_secure_websocket(self, endpoint: str, start_time: float, timestamp: str) -> WebSocketHealthCheck:
        """Test secure WebSocket through Cloudflare tunnel"""
        try:
            # First, test HTTP endpoint to verify tunnel is working
            http_endpoint = endpoint.replace('wss://', 'https://').replace('/ws/', '/health')
            http_response = requests.get(http_endpoint, timeout=5)
            
            if http_response.status_code != 200:
                raise Exception(f"HTTP health check failed: {http_response.status_code}")
            
            # Test WebSocket connection
            async with websockets.connect(
                endpoint,
                timeout=self.config.timeout,
                ping_interval=20,
                ping_timeout=10
            ) as websocket:
                # Send test message
                test_message = json.dumps({
                    "type": "health_check",
                    "timestamp": timestamp,
                    "source": "monitoring"
                })
                
                await websocket.send(test_message)
                
                # Wait for response
                response = await asyncio.wait_for(websocket.recv(), timeout=5)
                response_data = json.loads(response)
                
                response_time = (time.time() - start_time) * 1000
                
                return WebSocketHealthCheck(
                    timestamp=timestamp,
                    endpoint=endpoint,
                    status='healthy',
                    response_time_ms=response_time,
                    connection_id=response_data.get('connection_id'),
                    data_received=len(response)
                )
                
        except asyncio.TimeoutError:
            response_time = (time.time() - start_time) * 1000
            return WebSocketHealthCheck(
                timestamp=timestamp,
                endpoint=endpoint,
                status='timeout',
                response_time_ms=response_time,
                error_message="Connection timeout"
            )
        
        except Exception as e:
            response_time = (time.time() - start_time) * 1000
            return WebSocketHealthCheck(
                timestamp=timestamp,
                endpoint=endpoint,
                status='unhealthy',
                response_time_ms=response_time,
                error_message=str(e)
            )
    
    async def _test_local_websocket(self, endpoint: str, start_time: float, timestamp: str) -> WebSocketHealthCheck:
        """Test local WebSocket endpoint"""
        try:
            async with websockets.connect(
                endpoint,
                timeout=self.config.timeout,
                ping_interval=20,
                ping_timeout=10
            ) as websocket:
                # Send test message
                test_message = json.dumps({
                    "type": "health_check",
                    "timestamp": timestamp,
                    "source": "monitoring"
                })
                
                await websocket.send(test_message)
                
                # Wait for response
                response = await asyncio.wait_for(websocket.recv(), timeout=5)
                response_data = json.loads(response)
                
                response_time = (time.time() - start_time) * 1000
                
                return WebSocketHealthCheck(
                    timestamp=timestamp,
                    endpoint=endpoint,
                    status='healthy',
                    response_time_ms=response_time,
                    connection_id=response_data.get('connection_id'),
                    data_received=len(response)
                )
                
        except asyncio.TimeoutError:
            response_time = (time.time() - start_time) * 1000
            return WebSocketHealthCheck(
                timestamp=timestamp,
                endpoint=endpoint,
                status='timeout',
                response_time_ms=response_time,
                error_message="Connection timeout"
            )
        
        except Exception as e:
            response_time = (time.time() - start_time) * 1000
            return WebSocketHealthCheck(
                timestamp=timestamp,
                endpoint=endpoint,
                status='unhealthy',
                response_time_ms=response_time,
                error_message=str(e)
            )
    
    async def run_health_checks(self) -> List[WebSocketHealthCheck]:
        """Run health checks for all endpoints"""
        logger.info("🔍 Running WebSocket health checks")
        
        tasks = []
        for endpoint in self.config.endpoints:
            task = asyncio.create_task(self.check_websocket_health(endpoint))
            tasks.append(task)
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Process results
        health_checks = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                endpoint = self.config.endpoints[i]
                health_check = WebSocketHealthCheck(
                    timestamp=datetime.now().isoformat(),
                    endpoint=endpoint,
                    status='error',
                    response_time_ms=0,
                    error_message=str(result)
                )
                health_checks.append(health_check)
            else:
                health_checks.append(result)
        
        return health_checks
    
    def process_health_results(self, health_checks: List[WebSocketHealthCheck]):
        """Process health check results and update monitoring state"""
        healthy_count = sum(1 for check in health_checks if check.status == 'healthy')
        total_count = len(health_checks)
        
        logger.info(f"📊 Health check results: {healthy_count}/{total_count} endpoints healthy")
        
        # Update consecutive failures
        if healthy_count == 0:
            self.consecutive_failures += 1
        else:
            self.consecutive_failures = 0
        
        # Check for alert conditions
        if self.consecutive_failures >= self.config.alert_threshold:
            self.send_alert(health_checks)
        
        # Store health history
        self.health_history.extend(health_checks)
        
        # Keep only last 100 health checks
        if len(self.health_history) > 100:
            self.health_history = self.health_history[-100:]
        
        # Log individual results
        for check in health_checks:
            status_emoji = "✅" if check.status == 'healthy' else "❌"
            logger.info(f"{status_emoji} {check.endpoint}: {check.status} ({check.response_time_ms:.1f}ms)")
    
    def send_alert(self, health_checks: List[WebSocketHealthCheck]):
        """Send alert for WebSocket connectivity issues"""
        current_time = datetime.now()
        
        # Rate limit alerts (max 1 per hour)
        if (self.last_alert_time and 
            current_time - self.last_alert_time < timedelta(hours=1)):
            return
        
        self.last_alert_time = current_time
        
        # Prepare alert message
        failed_endpoints = [check for check in health_checks if check.status != 'healthy']
        
        alert_message = {
            "timestamp": current_time.isoformat(),
            "type": "websocket_connectivity_alert",
            "severity": "high",
            "message": f"WebSocket connectivity issues detected: {len(failed_endpoints)}/{len(health_checks)} endpoints failing",
            "failed_endpoints": [
                {
                    "endpoint": check.endpoint,
                    "status": check.status,
                    "error": check.error_message
                }
                for check in failed_endpoints
            ],
            "consecutive_failures": self.consecutive_failures,
            "recommendations": [
                "Check Cloudflare tunnel status",
                "Verify WebSocket support in Cloudflare dashboard",
                "Check Observatory server status",
                "Review bot protection settings"
            ]
        }
        
        logger.error(f"🚨 ALERT: {alert_message['message']}")
        
        # Send webhook alert if configured
        if self.config.alert_webhook:
            try:
                response = requests.post(
                    self.config.alert_webhook,
                    json=alert_message,
                    timeout=10
                )
                if response.status_code == 200:
                    logger.info("✅ Alert sent successfully")
                else:
                    logger.error(f"❌ Failed to send alert: {response.status_code}")
            except Exception as e:
                logger.error(f"❌ Error sending alert: {e}")
        
        # Save alert to file
        alert_file = Path("logs/websocket_alerts.jsonl")
        with open(alert_file, "a") as f:
            f.write(json.dumps(alert_message) + "\n")
    
    def get_health_summary(self) -> Dict[str, Any]:
        """Get health monitoring summary"""
        if not self.health_history:
            return {"status": "no_data", "message": "No health checks performed yet"}
        
        recent_checks = self.health_history[-10:]  # Last 10 checks
        healthy_count = sum(1 for check in recent_checks if check.status == 'healthy')
        total_count = len(recent_checks)
        
        avg_response_time = sum(check.response_time_ms for check in recent_checks) / total_count
        
        return {
            "status": "healthy" if healthy_count == total_count else "degraded",
            "healthy_endpoints": healthy_count,
            "total_endpoints": total_count,
            "success_rate": healthy_count / total_count,
            "average_response_time_ms": avg_response_time,
            "consecutive_failures": self.consecutive_failures,
            "last_check": recent_checks[-1].timestamp if recent_checks else None,
            "monitoring_active": self.monitoring_active
        }
    
    async def start_monitoring(self):
        """Start continuous monitoring"""
        self.monitoring_active = True
        logger.info("🚀 Starting WebSocket monitoring")
        
        try:
            while self.monitoring_active:
                health_checks = await self.run_health_checks()
                self.process_health_results(health_checks)
                
                # Wait for next check
                await asyncio.sleep(self.config.check_interval)
                
        except KeyboardInterrupt:
            logger.info("🛑 Monitoring stopped by user")
        except Exception as e:
            logger.error(f"❌ Monitoring error: {e}")
        finally:
            self.monitoring_active = False
    
    def stop_monitoring(self):
        """Stop monitoring"""
        self.monitoring_active = False
        logger.info("🛑 Stopping WebSocket monitoring")

def main():
    """Main monitoring script"""
    print("🔧 WebSocket Connectivity Monitor")
    print("=" * 50)
    
    # Load configuration
    config = MonitoringConfig()
    
    # Create monitor
    monitor = WebSocketMonitor(config)
    
    try:
        # Run monitoring
        asyncio.run(monitor.start_monitoring())
    except KeyboardInterrupt:
        print("\n🛑 Monitoring stopped")
    except Exception as e:
        print(f"❌ Monitoring error: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
