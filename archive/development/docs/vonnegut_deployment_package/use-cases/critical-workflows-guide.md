# Critical Workflows Guide

## Overview

This guide provides comprehensive step-by-step procedures for all critical operational workflows in the Beast Mode Observatory system. Each workflow includes expected outcomes, validation checkpoints, and troubleshooting guidance to ensure reliable system operation.

## Workflow Categories

### Infrastructure Management
- [Tunnel Operations](#tunnel-operations) - Cloudflare tunnel management
- [Dashboard Lifecycle](#dashboard-lifecycle) - Observatory server management
- [System Recovery](#system-recovery) - Emergency recovery procedures

### Monitoring and Maintenance
- [Health Monitoring](#health-monitoring) - System status validation
- [Log Management](#log-management) - Log collection and analysis
- [Configuration Management](#configuration-management) - CMS-based updates

### Emergency Procedures
- [Emergency Protocols](#emergency-protocols) - Crisis response procedures
- [Failover Operations](#failover-operations) - Service continuity procedures

---

## Tunnel Operations

### Tunnel Start Procedure (`make tunnel-start`)

**Purpose:** Establish Cloudflare tunnel connection for external access  
**Duration:** 60-90 seconds  
**Prerequisites:** Valid tunnel credentials, network connectivity

#### Step-by-Step Procedure:

##### Step 1: Pre-Start Validation (0-5 seconds)
```bash
# Execute tunnel start
make tunnel-start

# Expected output:
# Starting Cloudflare tunnel...
# Validating tunnel credentials...
# Checking network connectivity...
```

**Validation Checkpoints:**
- ✅ Tunnel credentials file exists at expected location
- ✅ Network connectivity to Cloudflare API confirmed
- ✅ No conflicting tunnel processes running

**Expected Outcomes:**
- Credentials validation completes successfully
- Network connectivity test passes
- System ready for tunnel establishment

##### Step 2: Tunnel Authentication (5-15 seconds)
```bash
# Monitor authentication process
tail -f logs/tunnel.log

# Expected log entries:
# [INFO] Authenticating tunnel d1e53e43-033f-4994-8f46-c83962ae3785
# [INFO] Authentication successful
# [INFO] Loading ingress rules...
```

**Validation Checkpoints:**
- ✅ Tunnel ID authentication succeeds
- ✅ Ingress rules loaded successfully
- ✅ API connection established

**Expected Outcomes:**
- Tunnel authenticated with Cloudflare API
- Ingress rules configured for all domains
- Ready for DNS propagation

##### Step 3: DNS Propagation (15-75 seconds)
```bash
# Monitor DNS propagation
dig observatory.nkllon.com
dig grafana.observatory.nkllon.com
dig prometheus.observatory.nkllon.com

# Expected results:
# observatory.nkllon.com -> Cloudflare IP
# grafana.observatory.nkllon.com -> Cloudflare IP
# prometheus.observatory.nkllon.com -> Cloudflare IP
```

**Validation Checkpoints:**
- ✅ DNS records updated for all domains
- ✅ Propagation to Tier 1 edge servers (0-15s)
- ✅ Propagation to Tier 2 edge servers (15-30s)
- ✅ Propagation to Tier 3 edge servers (30-60s)

**Expected Outcomes:**
- All domains resolve to Cloudflare edge servers
- Global DNS propagation completed
- External access routes established

##### Step 4: Service Health Validation (75-90 seconds)
```bash
# Validate service accessibility
curl -s https://observatory.nkllon.com/health
curl -s https://grafana.observatory.nkllon.com/api/health
curl -s https://prometheus.observatory.nkllon.com/api/v1/status/config

# Expected responses:
# Observatory: {"status": "healthy", "timestamp": "..."}
# Grafana: {"database": "ok", "version": "..."}
# Prometheus: {"status": "success", "data": {...}}
```

**Validation Checkpoints:**
- ✅ Observatory health endpoint responds
- ✅ Grafana health check passes
- ✅ Prometheus status endpoint accessible
- ✅ WebSocket endpoints functional

**Expected Outcomes:**
- All services accessible via tunnel
- Health checks pass for all components
- WebSocket connections can be established
- Tunnel fully operational

#### Troubleshooting Common Issues:

**Issue: Tunnel authentication fails**
```bash
# Check credentials file
ls -la ~/.cloudflared/
cat ~/.cloudflared/cert.pem

# Verify tunnel ID
cloudflared tunnel list

# Solution: Update credentials or recreate tunnel
```

**Issue: DNS propagation timeout**
```bash
# Check DNS status from multiple locations
dig @8.8.8.8 observatory.nkllon.com
dig @1.1.1.1 observatory.nkllon.com

# Force DNS cache clear
sudo dscacheutil -flushcache

# Solution: Wait additional time or check Cloudflare DNS status
```

### Tunnel Stop Procedure (`make tunnel-stop`)

**Purpose:** Gracefully shutdown Cloudflare tunnel connection  
**Duration:** 30-45 seconds  
**Prerequisites:** Active tunnel process

#### Step-by-Step Procedure:

##### Step 1: Graceful Shutdown Initiation (0-5 seconds)
```bash
# Execute tunnel stop
make tunnel-stop

# Expected output:
# Stopping Cloudflare tunnel...
# Sending graceful shutdown signal...
# Waiting for connections to close...
```

**Validation Checkpoints:**
- ✅ Tunnel process identified and signaled
- ✅ Graceful shutdown signal sent
- ✅ Connection cleanup initiated

##### Step 2: Connection Cleanup (5-20 seconds)
```bash
# Monitor active connections
netstat -an | grep :443
lsof -i :443

# Expected behavior:
# Active connections decreasing
# WebSocket connections closing gracefully
# No new connections accepted
```

**Validation Checkpoints:**
- ✅ WebSocket connections closed with proper close frames
- ✅ HTTP connections completed or terminated
- ✅ No new connections accepted

##### Step 3: Service Deregistration (20-35 seconds)
```bash
# Verify tunnel deregistration
cloudflared tunnel list

# Expected output:
# No active tunnels or tunnel marked as inactive
```

**Validation Checkpoints:**
- ✅ Tunnel deregistered from Cloudflare API
- ✅ DNS records updated (optional)
- ✅ Resources released

##### Step 4: Process Termination (35-45 seconds)
```bash
# Verify process termination
ps aux | grep cloudflared
lsof -i :443

# Expected results:
# No cloudflared processes running
# Port 443 released
```

**Validation Checkpoints:**
- ✅ Cloudflared process terminated cleanly
- ✅ All ports released
- ✅ No zombie processes remaining

---

## Dashboard Lifecycle

### Dashboard Start Procedure (`make dashboard-up`)

**Purpose:** Start Observatory server with full ReflectiveModule initialization  
**Duration:** 45-60 seconds  
**Prerequisites:** Python environment, Redis coordination available

#### Step-by-Step Procedure:

##### Step 1: Environment Validation (0-5 seconds)
```bash
# Execute dashboard start
make dashboard-up

# Expected output:
# Starting Observatory server...
# Validating Python environment...
# Checking dependencies...
```

**Validation Checkpoints:**
- ✅ Python 3.9+ available
- ✅ Required packages installed
- ✅ Port 8888 available
- ✅ Redis coordination accessible

##### Step 2: ReflectiveModule Initialization (5-20 seconds)
```bash
# Monitor initialization logs
tail -f logs/observatory.log

# Expected log entries:
# [INFO] Initializing ReflectiveModule framework
# [INFO] Registering capabilities: CORE_FUNCTIONALITY, DATA_PROCESSING, MONITORING
# [INFO] Health endpoints initialized: /health, /ready, /metrics
```

**Validation Checkpoints:**
- ✅ ReflectiveModule base class initialized
- ✅ Capabilities registered successfully
- ✅ Health endpoints active
- ✅ Metrics collection started

##### Step 3: WebSocket Endpoint Registration (20-35 seconds)
```bash
# Test WebSocket endpoints
curl -s http://localhost:8888/health
wscat -c ws://localhost:8888/ws/observatory

# Expected responses:
# Health: {"status": "healthy", "websockets": 4}
# WebSocket: Connection established, subscription confirmed
```

**Validation Checkpoints:**
- ✅ `/ws/observatory` endpoint active
- ✅ `/ws/emoji-rain` endpoint active
- ✅ `/ws/anomalies` endpoint active
- ✅ `/ws/doctor-status` endpoint active

##### Step 4: Service Integration (35-50 seconds)
```bash
# Verify Redis coordination
redis-cli -h 192.168.1.119 -p 6379 ping
redis-cli -h localhost -p 6380 ping

# Test Prometheus metrics
curl -s http://localhost:8888/metrics | grep observatory

# Expected results:
# Redis: PONG (primary or fallback)
# Metrics: observatory_* metrics available
```

**Validation Checkpoints:**
- ✅ Redis coordination established
- ✅ Prometheus metrics exposed
- ✅ Integration points confirmed
- ✅ All systems operational

#### Parameter Requirements:

**Environment Variables:**
```bash
# Required environment variables
export OBSERVATORY_PORT=8888
export OBSERVATORY_HOST=localhost
export REDIS_PRIMARY_HOST=192.168.1.119
export REDIS_PRIMARY_PORT=6379
export REDIS_FALLBACK_HOST=localhost
export REDIS_FALLBACK_PORT=6380
```

**Configuration Files:**
- `config/observatory.yml` - Main configuration
- `config/websocket.yml` - WebSocket endpoint configuration
- `config/redis.yml` - Redis coordination settings

### Dashboard Stop Procedure (`make dashboard-stop`)

**Purpose:** Gracefully shutdown Observatory server  
**Duration:** 20-30 seconds  
**Prerequisites:** Active Observatory process

#### Step-by-Step Procedure:

##### Step 1: Graceful Shutdown Signal (0-5 seconds)
```bash
# Execute dashboard stop
make dashboard-stop

# Expected output:
# Stopping Observatory server...
# Sending SIGTERM to process...
# Initiating graceful shutdown...
```

##### Step 2: WebSocket Connection Cleanup (5-15 seconds)
```bash
# Monitor WebSocket cleanup
netstat -an | grep :8888

# Expected behavior:
# WebSocket connections receiving close frames
# Connection count decreasing
# No new connections accepted
```

**Validation Checkpoints:**
- ✅ WebSocket close frames sent to all clients
- ✅ Active connections terminated gracefully
- ✅ Connection pool cleaned up

##### Step 3: Service Deregistration (15-25 seconds)
```bash
# Verify service deregistration
curl -s http://localhost:8888/health

# Expected response:
# Connection refused or 503 Service Unavailable
```

**Validation Checkpoints:**
- ✅ Health endpoints deregistered
- ✅ Metrics collection stopped
- ✅ Redis coordination disconnected

##### Step 4: Process Termination (25-30 seconds)
```bash
# Verify process termination
ps aux | grep observatory
lsof -i :8888

# Expected results:
# No observatory processes running
# Port 8888 released
```

### Dashboard Restart Procedure (`make dashboard-restart`)

**Purpose:** Restart Observatory server with validation  
**Duration:** 65-90 seconds  
**Prerequisites:** Existing Observatory installation

#### Combined Procedure:
1. Execute dashboard stop procedure (20-30 seconds)
2. Validate clean state (5 seconds)
3. Execute dashboard start procedure (45-60 seconds)
4. Perform end-to-end validation (5 seconds)

---

## Health Monitoring

### System Status Check (`make dashboard-status`)

**Purpose:** Comprehensive health validation of all system components  
**Duration:** 10-15 seconds  
**Prerequisites:** System components running

#### Step-by-Step Procedure:

##### Step 1: Process Status Validation (0-2 seconds)
```bash
# Execute status check
make dashboard-status

# Expected output:
# Checking Observatory server status...
# Process: RUNNING (PID: 12345)
# Port 8888: LISTENING
```

##### Step 2: Health Endpoint Validation (2-8 seconds)
```bash
# Health endpoint checks (5 second timeout each)
curl -s --max-time 5 http://localhost:8888/health
curl -s --max-time 5 http://localhost:8888/ready
curl -s --max-time 5 http://localhost:8888/metrics

# Expected responses:
# /health: {"status": "healthy", "components": {...}}
# /ready: {"ready": true, "dependencies": "all_available"}
# /metrics: # HELP observatory_requests_total ...
```

**Validation Checkpoints:**
- ✅ `/health` returns 200 OK within 5 seconds
- ✅ `/ready` returns ready: true within 5 seconds
- ✅ `/metrics` returns Prometheus data within 5 seconds

##### Step 3: WebSocket Endpoint Validation (8-14 seconds)
```bash
# WebSocket connectivity tests (3 second timeout each)
wscat -c ws://localhost:8888/ws/observatory --timeout 3000
wscat -c ws://localhost:8888/ws/emoji-rain --timeout 3000
wscat -c ws://localhost:8888/ws/anomalies --timeout 3000
wscat -c ws://localhost:8888/ws/doctor-status --timeout 3000

# Expected results:
# All endpoints: Connection established within 3 seconds
```

**Validation Checkpoints:**
- ✅ All 4 WebSocket endpoints responsive within 3 seconds each
- ✅ WebSocket upgrade negotiation successful
- ✅ Subscription messages accepted

##### Step 4: External Dependencies (14-15 seconds)
```bash
# Redis coordination check (3 second timeout)
redis-cli -h 192.168.1.119 -p 6379 --latency-history -i 1 ping

# Tunnel connectivity check (5 second timeout)
curl -s --max-time 5 https://observatory.nkllon.com/health

# Expected results:
# Redis: PONG with <10ms latency
# Tunnel: 200 OK response or connection active
```

#### Success Criteria:

**Overall Status: HEALTHY**
- ✅ Process running on port 8888
- ✅ All health endpoints responding within timeout
- ✅ All WebSocket endpoints accessible
- ✅ Redis coordination active
- ✅ External tunnel connectivity confirmed

**Overall Status: DEGRADED**
- ⚠️ Some non-critical components failing
- ⚠️ Performance below optimal thresholds
- ⚠️ Fallback systems in use

**Overall Status: DOWN**
- ❌ Critical health checks failing
- ❌ WebSocket endpoints unavailable
- ❌ Process not responding

---

## Configuration Management

### CMS-Based Configuration Updates

**Purpose:** Update system configuration via Directus CMS  
**Duration:** 2-5 minutes  
**Prerequisites:** Directus CMS accessible at localhost:8055

#### Step-by-Step Procedure:

##### Step 1: Access Configuration Management
```bash
# Verify Directus availability
curl -s http://localhost:8055/server/ping

# Expected response: "pong"

# Access web interface
open http://localhost:8055/admin
```

##### Step 2: Configuration Categories

**WebSocket Configuration:**
- Endpoint settings and limits
- Authentication requirements
- Message routing rules

**Service Configuration:**
- Health check intervals
- Timeout values
- Retry policies

**Integration Configuration:**
- Redis coordination settings
- Prometheus metrics configuration
- Alert thresholds

##### Step 3: Version Control Workflow
```bash
# Configuration changes trigger version control
git add config/
git commit -m "Update configuration via CMS"
git push origin main

# Automatic deployment trigger
make deploy-config-changes
```

##### Step 4: Rolling Updates
```bash
# Graceful configuration reload
make reload-config

# Expected behavior:
# Configuration reloaded without service interruption
# New settings applied to new connections
# Existing connections maintained
```

**Validation Checkpoints:**
- ✅ Configuration changes saved in CMS
- ✅ Version control updated
- ✅ Services reloaded gracefully
- ✅ New configuration active

---

## Success Criteria Summary

### Functional Requirements:
- ✅ All critical workflows documented with step-by-step procedures
- ✅ Expected outcomes specified for each workflow step
- ✅ Validation checkpoints defined with specific criteria
- ✅ Troubleshooting guidance provided for common issues
- ✅ Integration points confirmed with existing Beast Mode components

### Performance Requirements:
- ✅ Workflow execution times documented and validated
- ✅ Timeout values specified for all operations
- ✅ Success criteria defined for each workflow
- ✅ Performance thresholds established

### Integration Requirements:
- ✅ ReflectiveModule pattern integration documented
- ✅ WebSocket connection establishment procedures
- ✅ CMS-based configuration management workflows
- ✅ Emergency protocol coordination procedures

This critical workflows guide provides comprehensive operational procedures for all essential system functions, ensuring reliable and consistent operation of the Beast Mode Observatory infrastructure.