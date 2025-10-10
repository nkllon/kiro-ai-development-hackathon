# Critical Workflows Documentation

## Overview

This document provides comprehensive step-by-step procedures for critical operational workflows within the Beast Mode framework. Each workflow includes expected outcomes, validation checkpoints, and integration with the systematic observability patterns established by the ReflectiveModule framework.

## Tunnel Management Workflows

### 1. Tunnel Start Workflow

**Objective**: Establish Cloudflare tunnel connectivity for external access to Observatory services.

**Prerequisites**:
- Cloudflare tunnel credentials configured
- Observatory server ready for traffic
- DNS configuration validated

**Workflow Steps**:

```bash
# Step 1: Validate Prerequisites
make tunnel-validate-prerequisites
```

**Expected Output**:
```
✅ Tunnel credentials found: /path/to/tunnel/credentials.json
✅ Observatory server health: http://localhost:8888/health
✅ DNS configuration validated for observatory.nkllon.com
✅ Prerequisites validation complete
```

**Step-by-Step Procedure**:

1. **Execute Tunnel Start Command**:
   ```bash
   make tunnel-start
   ```

2. **Monitor Tunnel Startup Process**:
   ```bash
   # Expected log sequence:
   [INFO] Starting Cloudflare tunnel: d1e53e43-033f-4994-8f46-c83962ae3785
   [INFO] Authenticating with Cloudflare API...
   [INFO] Tunnel authentication successful
   [INFO] Loading ingress rules from configuration
   [INFO] Starting tunnel daemon process
   [INFO] Tunnel established successfully
   [INFO] DNS propagation initiated (30-60 seconds)
   ```

3. **Validation Checkpoints**:
   
   **Checkpoint 1: Tunnel Process Running (5-10 seconds)**
   ```bash
   # Validate tunnel process
   ps aux | grep cloudflared
   # Expected: cloudflared process running with tunnel ID
   ```

   **Checkpoint 2: API Authentication (10-15 seconds)**
   ```bash
   # Check tunnel status via API
   curl -s "https://api.cloudflare.com/client/v4/accounts/{account_id}/cfd_tunnel/{tunnel_id}" \
        -H "Authorization: Bearer {api_token}"
   # Expected: {"success": true, "result": {"status": "healthy"}}
   ```

   **Checkpoint 3: DNS Propagation (30-60 seconds)**
   ```bash
   # Test DNS resolution
   nslookup observatory.nkllon.com
   # Expected: Resolves to Cloudflare IP addresses
   
   # Test subdomain resolution
   nslookup grafana.observatory.nkllon.com
   nslookup prometheus.observatory.nkllon.com
   ```

   **Checkpoint 4: Service Connectivity (60-90 seconds)**
   ```bash
   # Test Observatory connectivity through tunnel
   curl -s https://observatory.nkllon.com/health
   # Expected: {"status": "healthy", "timestamp": "..."}
   
   # Test WebSocket connectivity
   wscat -c wss://observatory.nkllon.com/ws/observatory
   # Expected: WebSocket connection established
   ```

4. **Final Validation**:
   ```bash
   make tunnel-status
   ```

   **Expected Output**:
   ```
   🚀 Tunnel Status: ACTIVE
   📡 Tunnel ID: d1e53e43-033f-4994-8f46-c83962ae3785
   🌐 Domains:
     ✅ observatory.nkllon.com → localhost:8888
     ✅ grafana.observatory.nkllon.com → localhost:3000
     ✅ prometheus.observatory.nkllon.com → localhost:9090
   🔗 WebSocket Endpoints:
     ✅ /ws/observatory (Active connections: 0)
     ✅ /ws/emoji-rain (Active connections: 0)
     ✅ /ws/anomalies (Active connections: 0)
     ✅ /ws/doctor-status (Active connections: 0)
   ⏱️  DNS Propagation: Complete (45 seconds)
   📊 Health Score: 100%
   ```

**Troubleshooting Common Issues**:

- **Authentication Failure**: Verify tunnel credentials file exists and is valid
- **DNS Propagation Timeout**: Wait additional time, DNS can take up to 5 minutes globally
- **Service Connectivity Issues**: Ensure Observatory server is running and healthy
- **WebSocket Connection Failures**: Check WebSocket endpoint configuration in tunnel config

### 2. Tunnel Stop Workflow

**Objective**: Gracefully terminate Cloudflare tunnel with proper cleanup.

**Workflow Steps**:

1. **Execute Tunnel Stop Command**:
   ```bash
   make tunnel-stop
   ```

2. **Monitor Graceful Shutdown Process**:
   ```bash
   # Expected log sequence:
   [INFO] Initiating graceful tunnel shutdown
   [INFO] Closing active WebSocket connections (0 connections)
   [INFO] Deregistering tunnel from Cloudflare API
   [INFO] Terminating tunnel daemon process
   [INFO] Tunnel shutdown complete
   ```

3. **Validation Checkpoints**:
   
   **Checkpoint 1: Active Connections Closed (5-10 seconds)**
   ```bash
   # Verify no active WebSocket connections
   curl -s http://localhost:8888/metrics | grep websocket_connections_active
   # Expected: websocket_connections_active 0
   ```

   **Checkpoint 2: Tunnel Process Terminated (15-20 seconds)**
   ```bash
   # Verify tunnel process stopped
   ps aux | grep cloudflared
   # Expected: No cloudflared processes running
   ```

   **Checkpoint 3: External Connectivity Lost (30-45 seconds)**
   ```bash
   # Verify external access no longer works
   curl -s --max-time 10 https://observatory.nkllon.com/health
   # Expected: Connection timeout or refused
   ```

4. **Final Validation**:
   ```bash
   make tunnel-status
   ```

   **Expected Output**:
   ```
   ❌ Tunnel Status: INACTIVE
   📡 Tunnel ID: d1e53e43-033f-4994-8f46-c83962ae3785
   🌐 Domains: Not accessible externally
   🔗 WebSocket Endpoints: Not accessible externally
   📊 Local Services: Still running (localhost access only)
   ```

## Dashboard Management Workflows

### 1. Dashboard Up Workflow

**Objective**: Start Observatory server with full ReflectiveModule initialization and WebSocket endpoints.

**Prerequisites**:
- Python environment activated
- Required dependencies installed
- Configuration files present

**Workflow Steps**:

1. **Execute Dashboard Start Command**:
   ```bash
   make dashboard-up
   ```

2. **Monitor Startup Sequence**:
   ```bash
   # Expected log sequence:
   [INFO] Starting Observatory server initialization
   [INFO] ReflectiveModule base initialization complete
   [INFO] Loading configuration from environment
   [INFO] Initializing health monitoring endpoints
   [INFO] Registering Prometheus metrics collectors
   [INFO] Starting WebSocket handler
   [INFO] Registering WebSocket endpoints: /ws/observatory, /ws/emoji-rain, /ws/anomalies, /ws/doctor-status
   [INFO] Connecting to Redis coordination (192.168.1.119:6379)
   [INFO] Observatory server ready on localhost:8888
   ```

3. **Validation Checkpoints**:

   **Checkpoint 1: Process Started (5-10 seconds)**
   ```bash
   # Verify Observatory process running
   ps aux | grep observatory-daemon
   # Expected: observatory-daemon.py process running
   ```

   **Checkpoint 2: Health Endpoints Active (10-15 seconds)**
   ```bash
   # Test health endpoint
   curl -s http://localhost:8888/health
   # Expected: {"status": "healthy", "module_id": "ObservatoryServer", ...}
   
   # Test readiness endpoint
   curl -s http://localhost:8888/ready
   # Expected: {"ready": true, "initialization_complete": true, ...}
   
   # Test metrics endpoint
   curl -s http://localhost:8888/metrics
   # Expected: Prometheus metrics format output
   ```

   **Checkpoint 3: WebSocket Endpoints Active (15-20 seconds)**
   ```bash
   # Test WebSocket endpoints
   wscat -c ws://localhost:8888/ws/observatory
   # Expected: Connection established, welcome message received
   
   # Test emoji rain endpoint
   wscat -c ws://localhost:8888/ws/emoji-rain
   # Expected: Connection established
   ```

   **Checkpoint 4: Redis Coordination (20-25 seconds)**
   ```bash
   # Test Redis connectivity
   redis-cli -h 192.168.1.119 -p 6379 ping
   # Expected: PONG
   
   # Verify Observatory registered in Redis
   redis-cli -h 192.168.1.119 -p 6379 keys "observatory:*"
   # Expected: Observatory coordination keys present
   ```

4. **Final Validation**:
   ```bash
   make dashboard-status
   ```

   **Expected Output**:
   ```
   🚀 Observatory Server Status: RUNNING
   🏥 Health Status: HEALTHY
   📊 Metrics Collection: ACTIVE
   🔗 WebSocket Endpoints:
     ✅ /ws/observatory (Ready for connections)
     ✅ /ws/emoji-rain (Ready for connections)
     ✅ /ws/anomalies (Ready for connections)
     ✅ /ws/doctor-status (Ready for connections)
   🔄 Redis Coordination: CONNECTED (192.168.1.119:6379)
   📈 Performance:
     - Memory Usage: 45.2 MB
     - CPU Usage: 2.1%
     - Uptime: 00:02:15
     - Active Connections: 0
   ```

### 2. Dashboard Stop Workflow

**Objective**: Gracefully shutdown Observatory server with proper cleanup.

**Workflow Steps**:

1. **Execute Dashboard Stop Command**:
   ```bash
   make dashboard-stop
   ```

2. **Monitor Shutdown Sequence**:
   ```bash
   # Expected log sequence:
   [INFO] Initiating graceful Observatory shutdown
   [INFO] Closing WebSocket connections (0 active connections)
   [INFO] Deregistering from Redis coordination
   [INFO] Stopping metrics collection
   [INFO] Deregistering health endpoints
   [INFO] ReflectiveModule cleanup complete
   [INFO] Observatory server shutdown complete
   ```

3. **Validation Checkpoints**:

   **Checkpoint 1: WebSocket Connections Closed (5-10 seconds)**
   ```bash
   # Verify WebSocket endpoints no longer accessible
   timeout 5 wscat -c ws://localhost:8888/ws/observatory
   # Expected: Connection refused or timeout
   ```

   **Checkpoint 2: Health Endpoints Deregistered (10-15 seconds)**
   ```bash
   # Verify health endpoints no longer respond
   curl -s --max-time 5 http://localhost:8888/health
   # Expected: Connection refused
   ```

   **Checkpoint 3: Process Terminated (15-20 seconds)**
   ```bash
   # Verify Observatory process stopped
   ps aux | grep observatory-daemon
   # Expected: No observatory-daemon processes running
   ```

4. **Final Validation**:
   ```bash
   make dashboard-status
   ```

   **Expected Output**:
   ```
   ❌ Observatory Server Status: STOPPED
   🏥 Health Status: NOT ACCESSIBLE
   📊 Metrics Collection: INACTIVE
   🔗 WebSocket Endpoints: NOT ACCESSIBLE
   🔄 Redis Coordination: DISCONNECTED
   ```

### 3. Dashboard Restart Workflow

**Objective**: Perform complete restart of Observatory server with validation.

**Workflow Steps**:

1. **Execute Dashboard Restart Command**:
   ```bash
   make dashboard-restart
   ```

2. **Monitor Restart Sequence**:
   ```bash
   # Expected log sequence:
   [INFO] Starting Observatory server restart
   [INFO] Executing graceful shutdown...
   [INFO] Shutdown complete, starting fresh initialization...
   [INFO] Observatory server restart complete
   ```

3. **Validation Process**:
   - Follows same validation checkpoints as Dashboard Stop (steps 1-3)
   - Followed by same validation checkpoints as Dashboard Up (steps 1-4)

4. **Final Validation**:
   ```bash
   make dashboard-status
   ```

   **Expected Output**: Same as Dashboard Up final validation, with restart timestamp.

## System Recovery Workflows

### 1. Redis Coordination Recovery

**Objective**: Recover Redis coordination connectivity with automatic failover.

**Scenario**: Primary Redis (192.168.1.119:6379) becomes unavailable.

**Recovery Steps**:

1. **Detect Redis Failure**:
   ```bash
   # Test primary Redis connectivity
   redis-cli -h 192.168.1.119 -p 6379 ping
   # Expected: Connection timeout or refused
   ```

2. **Automatic Failover Activation**:
   ```bash
   # Observatory automatically attempts failover
   # Monitor Observatory logs:
   [WARN] Primary Redis connection failed: 192.168.1.119:6379
   [INFO] Initiating automatic failover to localhost:6380
   [INFO] Failover successful, coordination restored
   ```

3. **Validate Failover Success**:
   ```bash
   # Test failover Redis connectivity
   redis-cli -h localhost -p 6380 ping
   # Expected: PONG
   
   # Verify Observatory coordination active
   curl -s http://localhost:8888/health | jq '.coordination_status'
   # Expected: {"status": "connected", "endpoint": "localhost:6380"}
   ```

4. **Primary Redis Recovery**:
   ```bash
   # When primary Redis becomes available again
   redis-cli -h 192.168.1.119 -p 6379 ping
   # Expected: PONG
   
   # Observatory automatically fails back
   [INFO] Primary Redis available, initiating failback
   [INFO] Failback successful, coordination restored to primary
   ```

### 2. WebSocket Connection Recovery

**Objective**: Recover WebSocket connectivity after connection failures.

**Recovery Steps**:

1. **Detect WebSocket Issues**:
   ```bash
   # Test WebSocket connectivity
   timeout 10 wscat -c ws://localhost:8888/ws/observatory
   # Expected: Connection timeout or error
   ```

2. **Restart WebSocket Handler**:
   ```bash
   # Observatory automatically restarts WebSocket handler
   [WARN] WebSocket handler unresponsive
   [INFO] Restarting WebSocket handler
   [INFO] WebSocket endpoints restored
   ```

3. **Validate Recovery**:
   ```bash
   # Test all WebSocket endpoints
   for endpoint in observatory emoji-rain anomalies doctor-status; do
     echo "Testing /ws/$endpoint"
     timeout 5 wscat -c "ws://localhost:8888/ws/$endpoint" -x '{"type":"ping"}'
   done
   # Expected: All endpoints respond with pong
   ```

## Emergency Protocol Workflows

### 1. Emergency System Isolation

**Objective**: Isolate affected components during critical system failures.

**Trigger**: Critical system failure detected (CPU > 95%, Memory > 90%, or service crash).

**Emergency Steps**:

1. **Automatic Emergency Detection**:
   ```bash
   # Observatory detects critical condition
   [CRITICAL] Emergency condition detected: CPU usage 97%
   [CRITICAL] Initiating emergency isolation protocol
   ```

2. **Component Isolation**:
   ```bash
   # Isolate affected components
   [INFO] Isolating high-CPU components
   [INFO] Reducing WebSocket connection limits
   [INFO] Enabling graceful degradation mode
   ```

3. **Emergency Notification**:
   ```bash
   # WebSocket emergency broadcast
   {
     "type": "emergency_notification",
     "level": "critical",
     "message": "System isolation activated due to resource exhaustion",
     "affected_components": ["websocket_handler", "metrics_collector"],
     "estimated_recovery_time": "5-10 minutes"
   }
   ```

4. **Recovery Validation**:
   ```bash
   # Monitor system recovery
   [INFO] CPU usage normalized: 15%
   [INFO] Memory usage normalized: 45%
   [INFO] Disabling emergency isolation
   [INFO] Restoring normal operations
   ```

## Integration Point Confirmations

### ACE Reporter Integration

**Validation Steps**:
```bash
# Test ACE Reporter connectivity
curl -s http://localhost:8888/ace-reporter/status
# Expected: {"status": "connected", "last_report": "..."}

# Verify progress broadcasting
curl -s http://localhost:8888/ace-reporter/broadcast-test
# Expected: Test broadcast successful
```

### AI Memory Palace Integration

**Validation Steps**:
```bash
# Test AI Memory Palace connectivity
curl -s http://localhost:8888/ai-memory-palace/status
# Expected: {"status": "connected", "context_storage": "active"}

# Verify context storage
curl -s http://localhost:8888/ai-memory-palace/store-test
# Expected: Context storage test successful
```

### DAG Registry Integration

**Validation Steps**:
```bash
# Test DAG Registry connectivity
curl -s http://localhost:8888/dag-registry/status
# Expected: {"status": "connected", "dependency_validation": "active"}

# Verify dependency validation
curl -s http://localhost:8888/dag-registry/validate-test
# Expected: Dependency validation test successful
```

## Troubleshooting Quick Reference

### Common Issues and Solutions

**Tunnel Won't Start**:
- Check credentials: `ls -la /path/to/tunnel/credentials.json`
- Verify Observatory health: `curl http://localhost:8888/health`
- Check port conflicts: `lsof -i :8888`

**Dashboard Won't Start**:
- Check Python environment: `which python`
- Verify dependencies: `pip list | grep -E "(fastapi|websockets|redis)"`
- Check configuration: `cat .env | grep -E "(REDIS|OBSERVATORY)"`

**WebSocket Connections Failing**:
- Test local connectivity: `wscat -c ws://localhost:8888/ws/observatory`
- Check firewall rules: `sudo ufw status`
- Verify WebSocket handler: `curl http://localhost:8888/health | jq '.websocket_status'`

**Redis Coordination Issues**:
- Test primary Redis: `redis-cli -h 192.168.1.119 -p 6379 ping`
- Test fallback Redis: `redis-cli -h localhost -p 6380 ping`
- Check Redis logs: `redis-cli -h 192.168.1.119 -p 6379 monitor`

This comprehensive workflow documentation ensures systematic and reliable operation of all critical Beast Mode framework components with clear validation procedures and troubleshooting guidance.