# WebSocket Connection Failure Resolution Procedures

## Overview

This document provides comprehensive troubleshooting procedures for WebSocket connection failures within the Beast Mode framework, including WebSocket upgrade negotiation troubleshooting, connection recovery procedures, and systematic resolution approaches for all WebSocket-related issues.

## WebSocket Connection Failure Categories

### 1. Connection Establishment Failures

**Symptoms**:
- Connection refused errors
- Timeout during initial connection
- HTTP 404/500 errors when attempting WebSocket connection
- Browser console errors: "WebSocket connection failed"

**Common Causes**:
- Observatory server not running
- WebSocket endpoints not registered
- Port conflicts or firewall blocking
- Incorrect WebSocket URL format

### 2. WebSocket Upgrade Negotiation Failures

**Symptoms**:
- HTTP 400 Bad Request during upgrade
- HTTP 426 Upgrade Required responses
- Connection established but immediately closed
- Missing or invalid WebSocket headers

**Common Causes**:
- Invalid WebSocket upgrade headers
- Unsupported WebSocket version
- Missing Sec-WebSocket-Key header
- Protocol negotiation failures

### 3. Connection Maintenance Failures

**Symptoms**:
- Frequent connection drops
- Ping/pong timeout failures
- Connection appears established but messages not received
- High connection latency

**Common Causes**:
- Network instability
- Server resource exhaustion
- Client-side connection management issues
- Proxy/firewall interference

## Diagnostic Procedures

### 1. Basic WebSocket Connectivity Test

```bash
#!/bin/bash
# scripts/test_websocket_connectivity.sh

echo "🔍 WebSocket Connectivity Diagnostic"
echo "===================================="

# Test 1: Observatory server health
echo "📡 Testing Observatory server health..."
if curl -s http://localhost:8888/health > /dev/null; then
    echo "✅ Observatory server is running"
else
    echo "❌ Observatory server is not responding"
    echo "   Run: make dashboard-up"
    exit 1
fi

# Test 2: WebSocket endpoints availability
echo "🔗 Testing WebSocket endpoints..."
endpoints=("observatory" "emoji-rain" "anomalies" "doctor-status")

for endpoint in "${endpoints[@]}"; do
    echo "Testing /ws/$endpoint..."
    
    # Use wscat to test connection
    timeout 10 wscat -c "ws://localhost:8888/ws/$endpoint" -x '{"type":"ping"}' 2>/dev/null
    
    if [ $? -eq 0 ]; then
        echo "✅ /ws/$endpoint - Connection successful"
    else
        echo "❌ /ws/$endpoint - Connection failed"
        
        # Additional diagnostics
        echo "   Checking endpoint registration..."
        curl -s http://localhost:8888/websocket/endpoints | jq ".endpoints[] | select(.path == \"/ws/$endpoint\")"
    fi
done

# Test 3: External WebSocket connectivity (if tunnel active)
echo "🌐 Testing external WebSocket connectivity..."
if curl -s https://observatory.nkllon.com/health > /dev/null; then
    echo "✅ External access available, testing WebSocket..."
    
    timeout 10 wscat -c "wss://observatory.nkllon.com/ws/observatory" -x '{"type":"ping"}' 2>/dev/null
    
    if [ $? -eq 0 ]; then
        echo "✅ External WebSocket connection successful"
    else
        echo "❌ External WebSocket connection failed"
        echo "   Check Cloudflare tunnel WebSocket configuration"
    fi
else
    echo "ℹ️  External access not available (tunnel may be down)"
fi

echo "🎯 Diagnostic complete"
```

### 2. WebSocket Upgrade Negotiation Diagnostic

```python
#!/usr/bin/env python3
"""
WebSocket upgrade negotiation diagnostic tool.
Tests WebSocket handshake process and identifies negotiation issues.
"""

import asyncio
import websockets
import json
import logging
from typing import Dict, Any, Optional
from datetime import datetime

class WebSocketUpgradeDiagnostic:
    """Diagnoses WebSocket upgrade negotiation issues."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.test_results = {}
        
    async def run_comprehensive_diagnostic(self, base_url: str = "ws://localhost:8888") -> Dict[str, Any]:
        """Run comprehensive WebSocket upgrade diagnostic."""
        print("🔍 WebSocket Upgrade Negotiation Diagnostic")
        print("=" * 50)
        
        endpoints = ["/ws/observatory", "/ws/emoji-rain", "/ws/anomalies", "/ws/doctor-status"]
        
        for endpoint in endpoints:
            print(f"\n📡 Testing endpoint: {endpoint}")
            result = await self._test_endpoint_upgrade(f"{base_url}{endpoint}")
            self.test_results[endpoint] = result
            
            if result['success']:
                print(f"✅ {endpoint}: Upgrade successful")
            else:
                print(f"❌ {endpoint}: Upgrade failed - {result['error']}")
                await self._diagnose_upgrade_failure(endpoint, result)
        
        return self.test_results
    
    async def _test_endpoint_upgrade(self, websocket_url: str) -> Dict[str, Any]:
        """Test WebSocket upgrade for specific endpoint."""
        try:
            # Attempt connection with detailed logging
            async with websockets.connect(
                websocket_url,
                timeout=10,
                ping_interval=None,  # Disable ping for testing
                close_timeout=5
            ) as websocket:
                
                # Send test message
                test_message = {"type": "ping", "timestamp": datetime.now().isoformat()}
                await websocket.send(json.dumps(test_message))
                
                # Wait for response
                try:
                    response = await asyncio.wait_for(websocket.recv(), timeout=5)
                    response_data = json.loads(response)
                    
                    return {
                        'success': True,
                        'response_time_ms': self._calculate_response_time(test_message, response_data),
                        'server_response': response_data,
                        'connection_info': {
                            'local_address': websocket.local_address,
                            'remote_address': websocket.remote_address,
                            'subprotocol': websocket.subprotocol
                        }
                    }
                    
                except asyncio.TimeoutError:
                    return {
                        'success': False,
                        'error': 'Response timeout - connection established but no response received',
                        'error_type': 'response_timeout'
                    }
                    
        except websockets.exceptions.InvalidStatusCode as e:
            return {
                'success': False,
                'error': f'Invalid status code: {e.status_code}',
                'error_type': 'invalid_status_code',
                'status_code': e.status_code,
                'headers': dict(e.response_headers) if hasattr(e, 'response_headers') else {}
            }
            
        except websockets.exceptions.InvalidHeader as e:
            return {
                'success': False,
                'error': f'Invalid header: {e}',
                'error_type': 'invalid_header'
            }
            
        except ConnectionRefusedError:
            return {
                'success': False,
                'error': 'Connection refused - server may not be running',
                'error_type': 'connection_refused'
            }
            
        except asyncio.TimeoutError:
            return {
                'success': False,
                'error': 'Connection timeout - server not responding',
                'error_type': 'connection_timeout'
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Unexpected error: {str(e)}',
                'error_type': 'unexpected_error',
                'exception_type': type(e).__name__
            }
    
    async def _diagnose_upgrade_failure(self, endpoint: str, result: Dict[str, Any]):
        """Diagnose specific upgrade failure and provide recommendations."""
        error_type = result.get('error_type', 'unknown')
        
        print(f"🔍 Diagnosing failure for {endpoint}:")
        
        if error_type == 'connection_refused':
            print("   💡 Recommendations:")
            print("      - Verify Observatory server is running: curl http://localhost:8888/health")
            print("      - Check if port 8888 is available: lsof -i :8888")
            print("      - Restart Observatory server: make dashboard-restart")
            
        elif error_type == 'invalid_status_code':
            status_code = result.get('status_code')
            print(f"   📊 HTTP Status Code: {status_code}")
            
            if status_code == 404:
                print("   💡 Recommendations:")
                print("      - Verify WebSocket endpoint is registered")
                print("      - Check Observatory WebSocket handler configuration")
                print("      - Review endpoint routing in Observatory server")
                
            elif status_code == 500:
                print("   💡 Recommendations:")
                print("      - Check Observatory server logs for errors")
                print("      - Verify WebSocket handler initialization")
                print("      - Review server resource usage")
                
        elif error_type == 'connection_timeout':
            print("   💡 Recommendations:")
            print("      - Check network connectivity")
            print("      - Verify firewall settings")
            print("      - Increase connection timeout")
            print("      - Check server load and performance")
            
        elif error_type == 'response_timeout':
            print("   💡 Recommendations:")
            print("      - Check WebSocket message handler implementation")
            print("      - Verify endpoint is processing messages correctly")
            print("      - Review server performance and resource usage")
            
        # Additional diagnostic information
        await self._check_endpoint_configuration(endpoint)
    
    async def _check_endpoint_configuration(self, endpoint: str):
        """Check endpoint configuration and registration."""
        try:
            import aiohttp
            
            async with aiohttp.ClientSession() as session:
                # Check endpoint registration
                async with session.get('http://localhost:8888/websocket/endpoints') as response:
                    if response.status == 200:
                        endpoints_data = await response.json()
                        
                        endpoint_config = None
                        for ep in endpoints_data.get('endpoints', []):
                            if ep.get('path') == endpoint:
                                endpoint_config = ep
                                break
                        
                        if endpoint_config:
                            print(f"   📋 Endpoint Configuration:")
                            print(f"      - Max Connections: {endpoint_config.get('max_connections', 'N/A')}")
                            print(f"      - Rate Limit: {endpoint_config.get('rate_limit_per_minute', 'N/A')}/min")
                            print(f"      - Authentication Required: {endpoint_config.get('authentication_required', 'N/A')}")
                            print(f"      - Status: {endpoint_config.get('status', 'N/A')}")
                        else:
                            print(f"   ❌ Endpoint {endpoint} not found in registration")
                    else:
                        print(f"   ⚠️  Could not retrieve endpoint configuration (HTTP {response.status})")
                        
        except Exception as e:
            print(f"   ⚠️  Could not check endpoint configuration: {e}")

# Usage example
if __name__ == "__main__":
    async def main():
        diagnostic = WebSocketUpgradeDiagnostic()
        results = await diagnostic.run_comprehensive_diagnostic()
        
        print("\n📊 Diagnostic Summary:")
        print("=" * 30)
        
        total_endpoints = len(results)
        successful_endpoints = sum(1 for r in results.values() if r['success'])
        
        print(f"Total Endpoints Tested: {total_endpoints}")
        print(f"Successful Connections: {successful_endpoints}")
        print(f"Failed Connections: {total_endpoints - successful_endpoints}")
        print(f"Success Rate: {(successful_endpoints / total_endpoints) * 100:.1f}%")
    
    asyncio.run(main())
```

## Resolution Procedures

### 1. Observatory Server WebSocket Issues

**Issue**: WebSocket endpoints not responding

**Resolution Steps**:

```bash
# Step 1: Check Observatory server status
curl -s http://localhost:8888/health | jq '.'

# If server not responding:
make dashboard-status
ps aux | grep observatory-daemon

# Step 2: Check WebSocket handler status
curl -s http://localhost:8888/websocket/status | jq '.'

# Step 3: Review Observatory logs for WebSocket errors
make dashboard-logs FILTER="websocket" | tail -50

# Step 4: Restart WebSocket handler (if server is running)
curl -X POST http://localhost:8888/admin/restart-websocket-handler \
  -H "Authorization: Bearer $ADMIN_TOKEN"

# Step 5: Full server restart if needed
make dashboard-restart

# Step 6: Validate WebSocket endpoints
python scripts/test_websocket_connectivity.py
```

### 2. WebSocket Upgrade Header Issues

**Issue**: HTTP 400 Bad Request during WebSocket upgrade

**Diagnostic Commands**:
```bash
# Test with curl to see raw HTTP response
curl -i -N -H "Connection: Upgrade" \
     -H "Upgrade: websocket" \
     -H "Sec-WebSocket-Version: 13" \
     -H "Sec-WebSocket-Key: x3JJHMbDL1EzLkh9GBhXDw==" \
     http://localhost:8888/ws/observatory

# Expected response should be HTTP 101 Switching Protocols
```

**Resolution Steps**:
```python
# Fix WebSocket upgrade handler
class WebSocketUpgradeValidator:
    """Validates and fixes WebSocket upgrade issues."""
    
    def validate_upgrade_headers(self, headers: Dict[str, str]) -> Dict[str, Any]:
        """Validate WebSocket upgrade headers."""
        issues = []
        recommendations = []
        
        # Check required headers
        required_headers = {
            'Upgrade': 'websocket',
            'Connection': 'upgrade',
            'Sec-WebSocket-Version': '13'
        }
        
        for header, expected_value in required_headers.items():
            if header not in headers:
                issues.append(f"Missing required header: {header}")
                recommendations.append(f"Add header: {header}: {expected_value}")
            elif headers[header].lower() != expected_value.lower():
                issues.append(f"Invalid {header} header: {headers[header]}")
                recommendations.append(f"Set {header} header to: {expected_value}")
        
        # Check WebSocket key
        if 'Sec-WebSocket-Key' not in headers:
            issues.append("Missing Sec-WebSocket-Key header")
            recommendations.append("Client must generate and send Sec-WebSocket-Key")
        elif len(headers['Sec-WebSocket-Key']) != 24:
            issues.append("Invalid Sec-WebSocket-Key length")
            recommendations.append("Sec-WebSocket-Key must be 24 characters (base64 encoded 16 bytes)")
        
        return {
            'valid': len(issues) == 0,
            'issues': issues,
            'recommendations': recommendations
        }
```

### 3. Connection Limit and Rate Limiting Issues

**Issue**: HTTP 503 Service Unavailable or connection rejected

**Diagnostic Commands**:
```bash
# Check current WebSocket connections
curl -s http://localhost:8888/websocket/connections | jq '.'

# Check connection limits
curl -s http://localhost:8888/websocket/config | jq '.endpoints[] | {path, max_connections, current_connections}'

# Check rate limiting status
curl -s http://localhost:8888/websocket/rate-limits | jq '.'
```

**Resolution Steps**:
```bash
# Step 1: Increase connection limits (temporary)
curl -X PATCH http://localhost:8888/admin/websocket-config \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -d '{
    "max_connections_multiplier": 1.5,
    "rate_limit_multiplier": 1.2
  }'

# Step 2: Clear rate limiting (if needed)
curl -X POST http://localhost:8888/admin/clear-rate-limits \
  -H "Authorization: Bearer $ADMIN_TOKEN"

# Step 3: Update configuration permanently (via Directus CMS)
curl -X PATCH "http://localhost:8055/items/websocket_config/1" \
  -H "Authorization: Bearer $DIRECTUS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "max_connections": 300,
    "rate_limit_per_minute": 120
  }'

# Step 4: Reload configuration
curl -X POST http://localhost:8888/admin/reload-config \
  -H "Authorization: Bearer $ADMIN_TOKEN"
```

### 4. Cloudflare Tunnel WebSocket Issues

**Issue**: External WebSocket connections failing through tunnel

**Diagnostic Commands**:
```bash
# Test external WebSocket connectivity
wscat -c wss://observatory.nkllon.com/ws/observatory

# Check Cloudflare tunnel configuration
cat /path/to/cloudflared-config.yml | grep -A 10 -B 10 websocket

# Test tunnel connectivity
curl -s https://observatory.nkllon.com/health
```

**Resolution Steps**:

1. **Update Cloudflare Tunnel Configuration**:
```yaml
# cloudflared-config.yml
tunnel: d1e53e43-033f-4994-8f46-c83962ae3785
credentials-file: /path/to/credentials.json

ingress:
  - hostname: observatory.nkllon.com
    service: http://localhost:8888
    originRequest:
      noTLSVerify: true
      connectTimeout: 30s
      tlsTimeout: 10s
      # WebSocket specific settings
      httpHostHeader: localhost:8888
      originServerName: localhost
      # Enable WebSocket support
      disableChunkedEncoding: true
      
  - service: http_status:404
```

2. **Restart Tunnel with WebSocket Support**:
```bash
# Stop current tunnel
make tunnel-stop

# Update tunnel configuration
cp cloudflared-config-websocket.yml /path/to/cloudflared-config.yml

# Start tunnel with new configuration
make tunnel-start

# Test WebSocket connectivity
wscat -c wss://observatory.nkllon.com/ws/observatory -x '{"type":"ping"}'
```

### 5. Client-Side Connection Recovery

**Issue**: Client WebSocket connections frequently dropping

**Client-Side Recovery Implementation**:
```javascript
class RobustWebSocketClient {
    constructor(url, options = {}) {
        this.url = url;
        this.options = {
            maxRetries: options.maxRetries || 10,
            retryDelay: options.retryDelay || 1000,
            maxRetryDelay: options.maxRetryDelay || 30000,
            heartbeatInterval: options.heartbeatInterval || 30000,
            ...options
        };
        
        this.retryCount = 0;
        this.connection = null;
        this.heartbeatTimer = null;
        this.reconnectTimer = null;
        this.isConnecting = false;
        
        this.connect();
    }
    
    connect() {
        if (this.isConnecting) return;
        
        this.isConnecting = true;
        
        try {
            console.log(`Connecting to WebSocket: ${this.url}`);
            this.connection = new WebSocket(this.url);
            
            this.connection.onopen = (event) => {
                console.log('WebSocket connected successfully');
                this.retryCount = 0;
                this.isConnecting = false;
                this.startHeartbeat();
                
                if (this.options.onOpen) {
                    this.options.onOpen(event);
                }
            };
            
            this.connection.onmessage = (event) => {
                const message = JSON.parse(event.data);
                
                // Handle heartbeat responses
                if (message.type === 'pong') {
                    console.log('Heartbeat response received');
                    return;
                }
                
                if (this.options.onMessage) {
                    this.options.onMessage(message);
                }
            };
            
            this.connection.onclose = (event) => {
                console.log(`WebSocket closed: ${event.code} - ${event.reason}`);
                this.isConnecting = false;
                this.stopHeartbeat();
                
                if (!event.wasClean && this.retryCount < this.options.maxRetries) {
                    this.scheduleReconnect();
                } else if (this.options.onClose) {
                    this.options.onClose(event);
                }
            };
            
            this.connection.onerror = (error) => {
                console.error('WebSocket error:', error);
                this.isConnecting = false;
                
                if (this.options.onError) {
                    this.options.onError(error);
                }
            };
            
        } catch (error) {
            console.error('Failed to create WebSocket connection:', error);
            this.isConnecting = false;
            this.scheduleReconnect();
        }
    }
    
    scheduleReconnect() {
        if (this.retryCount >= this.options.maxRetries) {
            console.error('Max reconnection attempts reached');
            return;
        }
        
        const delay = Math.min(
            this.options.retryDelay * Math.pow(2, this.retryCount),
            this.options.maxRetryDelay
        );
        
        console.log(`Scheduling reconnection attempt ${this.retryCount + 1} in ${delay}ms`);
        
        this.reconnectTimer = setTimeout(() => {
            this.retryCount++;
            this.connect();
        }, delay);
    }
    
    startHeartbeat() {
        this.heartbeatTimer = setInterval(() => {
            if (this.connection && this.connection.readyState === WebSocket.OPEN) {
                this.send({ type: 'ping', timestamp: Date.now() });
            }
        }, this.options.heartbeatInterval);
    }
    
    stopHeartbeat() {
        if (this.heartbeatTimer) {
            clearInterval(this.heartbeatTimer);
            this.heartbeatTimer = null;
        }
    }
    
    send(message) {
        if (this.connection && this.connection.readyState === WebSocket.OPEN) {
            this.connection.send(JSON.stringify(message));
        } else {
            console.warn('Cannot send message: WebSocket not connected');
        }
    }
    
    disconnect() {
        if (this.reconnectTimer) {
            clearTimeout(this.reconnectTimer);
        }
        
        this.stopHeartbeat();
        
        if (this.connection) {
            this.connection.close(1000, 'Client disconnect');
        }
    }
}

// Usage
const wsClient = new RobustWebSocketClient('ws://localhost:8888/ws/observatory', {
    onOpen: (event) => console.log('Connected to Observatory'),
    onMessage: (message) => console.log('Received:', message),
    onClose: (event) => console.log('Disconnected from Observatory'),
    onError: (error) => console.error('Connection error:', error)
});
```

## Monitoring and Prevention

### WebSocket Health Monitoring

```python
class WebSocketHealthMonitor(ReflectiveModule):
    """Monitors WebSocket connection health and prevents issues."""
    
    def __init__(self):
        super().__init__()
        self.module_id = "WebSocketHealthMonitor"
        self._connection_metrics = {}
        self._health_thresholds = {
            'max_connection_failures_per_minute': 10,
            'max_upgrade_failures_per_minute': 5,
            'min_success_rate_percentage': 95.0,
            'max_average_latency_ms': 200.0
        }
    
    def get_websocket_health_metrics(self) -> Dict[str, float]:
        """Get WebSocket health metrics for monitoring."""
        return {
            "websocket_connections_total": self._get_total_connections(),
            "websocket_connection_failures_per_minute": self._get_connection_failures_rate(),
            "websocket_upgrade_failures_per_minute": self._get_upgrade_failures_rate(),
            "websocket_success_rate_percentage": self._calculate_success_rate(),
            "websocket_average_latency_ms": self._calculate_average_latency(),
            "websocket_message_throughput_per_second": self._get_message_throughput()
        }
    
    async def check_websocket_health(self) -> Dict[str, Any]:
        """Comprehensive WebSocket health check."""
        health_issues = []
        
        # Check connection failure rate
        failure_rate = self._get_connection_failures_rate()
        if failure_rate > self._health_thresholds['max_connection_failures_per_minute']:
            health_issues.append(f"High connection failure rate: {failure_rate}/min")
        
        # Check upgrade failure rate
        upgrade_failure_rate = self._get_upgrade_failures_rate()
        if upgrade_failure_rate > self._health_thresholds['max_upgrade_failures_per_minute']:
            health_issues.append(f"High upgrade failure rate: {upgrade_failure_rate}/min")
        
        # Check success rate
        success_rate = self._calculate_success_rate()
        if success_rate < self._health_thresholds['min_success_rate_percentage']:
            health_issues.append(f"Low success rate: {success_rate:.1f}%")
        
        # Check latency
        avg_latency = self._calculate_average_latency()
        if avg_latency > self._health_thresholds['max_average_latency_ms']:
            health_issues.append(f"High average latency: {avg_latency:.1f}ms")
        
        return {
            'healthy': len(health_issues) == 0,
            'issues': health_issues,
            'metrics': self.get_websocket_health_metrics(),
            'recommendations': self._get_health_recommendations(health_issues)
        }
```

This comprehensive WebSocket connection failure resolution documentation provides systematic troubleshooting procedures and recovery mechanisms for all WebSocket-related issues within the Beast Mode framework.