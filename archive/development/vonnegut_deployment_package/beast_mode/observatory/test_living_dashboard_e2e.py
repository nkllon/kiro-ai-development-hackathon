#!/usr/bin/env python3
"""
End-to-End Test for Living Observatory Dashboard
Tests the complete integration of performance charts, activity feed, and correlation engine
"""

import asyncio
import json
import sys
import time
import requests
import websockets
from pathlib import Path
from datetime import datetime

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.rm_ddd.core.unified_reflective_module import ReflectiveModule, ModuleHealth, ModuleStatus, ModuleCapability

class LiveDashboardTestModule(ReflectiveModule):
    """Test module for end-to-end dashboard testing"""
    
    def __init__(self):
        super().__init__()
        self.module_id = "live_dashboard_test"
        self.test_operations = 0
    
    def get_module_info(self):
        return {
            "module_id": self.module_id,
            "name": "Live Dashboard Test Module",
            "version": "1.0.0"
        }
    
    def get_capabilities(self):
        return [ModuleCapability.MONITORING, ModuleCapability.CORE_FUNCTIONALITY]
    
    def get_health_status(self):
        return ModuleHealth(
            module_id=self.module_id,
            status=ModuleStatus.HEALTHY,
            health_score=0.95,
            issues=[],
            last_check=self._last_activity,
            uptime_seconds=(self._last_activity - self._start_time).total_seconds(),
            error_count=self._error_count,
            warning_count=self._warning_count
        )
    
    def graceful_degradation(self):
        from src.rm_ddd.core.unified_reflective_module import GracefulDegradationResult
        return GracefulDegradationResult(
            success=True,
            degraded_capabilities=[],
            remaining_capabilities=self.get_capabilities()
        )
    
    def simulate_system_activity(self):
        """Simulate various system activities that should correlate with metrics"""
        
        # Simulate WebSocket connections
        self.emit_observation(
            message="5 new WebSocket connections established",
            event_type="websocket_connect",
            context={"new_connections": 5, "total_connections": 25}
        )
        
        time.sleep(2)
        
        # Simulate performance impact
        self.emit_observation(
            message="Response time increased due to high load",
            event_type="performance",
            context={"response_time_ms": 250, "load_factor": 1.8}
        )
        
        time.sleep(2)
        
        # Simulate certificate operations
        self.emit_observation(
            message="Renewed 12 SSL certificates",
            event_type="certificate_lock",
            context={"certificates_renewed": 12, "operation_duration_ms": 1500}
        )
        
        time.sleep(2)
        
        # Simulate cache operations
        self.emit_observation(
            message="Cache invalidated for user sessions",
            event_type="cache_invalidate",
            context={"cache_entries_cleared": 150, "cache_type": "user_sessions"}
        )
        
        time.sleep(2)
        
        # Simulate recovery
        self.emit_observation(
            message="System performance normalized",
            event_type="success",
            context={"response_time_ms": 120, "load_factor": 0.9}
        )
        
        self.test_operations += 1

async def test_websocket_connection():
    """Test WebSocket connection to observations endpoint"""
    print("🔌 Testing WebSocket connection...")
    
    try:
        uri = "ws://localhost:8000/ws/observations"
        async with websockets.connect(uri) as websocket:
            print("✅ WebSocket connected successfully")
            
            # Send ping
            await websocket.send(json.dumps({"type": "ping"}))
            
            # Wait for response
            response = await asyncio.wait_for(websocket.recv(), timeout=5.0)
            data = json.loads(response)
            
            if data.get("type") == "pong":
                print("✅ WebSocket ping/pong working")
            
            # Listen for a few observations
            print("👂 Listening for observations...")
            for i in range(3):
                try:
                    message = await asyncio.wait_for(websocket.recv(), timeout=10.0)
                    observation = json.loads(message)
                    print(f"📰 Received: {observation.get('message', 'Unknown')} {observation.get('emoji', '')}")
                except asyncio.TimeoutError:
                    print("⏰ Timeout waiting for observation")
                    break
            
            return True
            
    except Exception as e:
        print(f"❌ WebSocket test failed: {e}")
        return False

def test_http_api():
    """Test HTTP API endpoints"""
    print("🌐 Testing HTTP API endpoints...")
    
    base_url = "http://localhost:8000"
    
    # Test health endpoint
    try:
        response = requests.get(f"{base_url}/health", timeout=5)
        if response.status_code == 200:
            print("✅ Health endpoint working")
        else:
            print(f"❌ Health endpoint failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Health endpoint error: {e}")
    
    # Test observations API
    try:
        response = requests.get(f"{base_url}/api/observations/recent", timeout=5)
        if response.status_code == 200:
            observations = response.json()
            print(f"✅ Observations API working ({len(observations)} observations)")
            
            # Show recent observations
            for obs in observations[-3:]:
                print(f"   📰 {obs.get('message', 'Unknown')} {obs.get('emoji', '')}")
        else:
            print(f"❌ Observations API failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Observations API error: {e}")
    
    # Test dashboard data endpoint
    try:
        response = requests.get(f"{base_url}/api/dashboard/all-data", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print("✅ Dashboard data API working")
            
            # Check for metrics
            if "metrics" in data:
                metrics = data["metrics"]
                print(f"   📊 Response time: {metrics.get('responseTime', 'N/A')}ms")
                print(f"   📊 Error rate: {metrics.get('errorRate', 'N/A')}%")
                print(f"   📊 Throughput: {metrics.get('throughput', 'N/A')} ops/sec")
        else:
            print(f"❌ Dashboard data API failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Dashboard data API error: {e}")

def test_dashboard_access():
    """Test dashboard web interface"""
    print("🌐 Testing dashboard web interface...")
    
    try:
        response = requests.get("http://localhost:8000/", timeout=5)
        if response.status_code == 200:
            content = response.text
            
            # Check for key components
            checks = [
                ("Performance Chart", "performanceChart" in content),
                ("Activity Feed", "activityFeed" in content or "ActivityFeedRenderer" in content),
                ("Correlation Engine", "correlationEngine" in content or "CorrelationEngine" in content),
                ("Observation Stream", "observationStream" in content or "ObservationStreamHandler" in content)
            ]
            
            print("✅ Dashboard accessible")
            for component, found in checks:
                status = "✅" if found else "❌"
                print(f"   {status} {component}: {'Found' if found else 'Not found'}")
                
        else:
            print(f"❌ Dashboard not accessible: {response.status_code}")
    except Exception as e:
        print(f"❌ Dashboard access error: {e}")

async def main():
    """Run comprehensive end-to-end test"""
    print("🎬 Living Observatory Dashboard - End-to-End Test")
    print("=" * 60)
    print()
    
    # Check if Observatory server is running
    try:
        response = requests.get("http://localhost:8000/health", timeout=5)
        if response.status_code != 200:
            print("❌ Observatory server not running or not healthy")
            print("💡 Start the server with: python start_observatory.py")
            return
    except Exception:
        print("❌ Observatory server not accessible at http://localhost:8000")
        print("💡 Start the server with: python start_observatory.py")
        return
    
    print("✅ Observatory server is running")
    print()
    
    # Test 1: HTTP API endpoints
    test_http_api()
    print()
    
    # Test 2: Dashboard web interface
    test_dashboard_access()
    print()
    
    # Test 3: Create test module and emit observations
    print("🔄 Creating test module and emitting observations...")
    test_module = LiveDashboardTestModule()
    test_module.simulate_system_activity()
    print("✅ Test observations emitted")
    print()
    
    # Test 4: WebSocket connection
    websocket_success = await test_websocket_connection()
    print()
    
    # Test 5: Wait and check for observations again
    print("⏳ Waiting 5 seconds for observations to propagate...")
    await asyncio.sleep(5)
    
    try:
        response = requests.get("http://localhost:8000/api/observations/recent", timeout=5)
        if response.status_code == 200:
            observations = response.json()
            print(f"📊 Final observation count: {len(observations)}")
            
            # Show most recent observations
            print("📰 Most recent observations:")
            for obs in observations[-5:]:
                timestamp = obs.get('timestamp', '')[:19]  # Truncate timestamp
                print(f"   {timestamp} | {obs.get('module', 'Unknown')} | {obs.get('message', 'Unknown')} {obs.get('emoji', '')}")
    except Exception as e:
        print(f"❌ Final observation check failed: {e}")
    
    print()
    print("🎯 End-to-End Test Summary")
    print("-" * 30)
    print("✅ HTTP API endpoints tested")
    print("✅ Dashboard web interface tested")
    print("✅ Observation emission tested")
    print(f"{'✅' if websocket_success else '❌'} WebSocket connection tested")
    print()
    print("🌐 Visit http://localhost:8000 to see the Living Observatory Dashboard")
    print("📊 The dashboard should show:")
    print("   - Performance charts (left side)")
    print("   - Live activity feed (right side)")
    print("   - Real-time correlation between events and metrics")
    print("   - Emoji-rich observation display")

if __name__ == "__main__":
    asyncio.run(main())