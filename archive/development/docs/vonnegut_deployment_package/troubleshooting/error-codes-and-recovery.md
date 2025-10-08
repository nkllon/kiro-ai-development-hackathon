# Error Codes and Recovery Procedures

## Overview

This comprehensive troubleshooting guide provides systematic error identification, diagnosis, and recovery procedures for the Beast Mode Observatory system. Each error includes specific error codes, root cause analysis, and step-by-step recovery instructions.

## Error Classification System

### Error Code Format: `OBS-[CATEGORY]-[SEVERITY]-[NUMBER]`

**Categories:**
- `WS` - WebSocket related errors
- `TUN` - Tunnel connectivity errors  
- `RED` - Redis coordination errors
- `SYS` - System and process errors
- `AUTH` - Authentication and authorization errors
- `NET` - Network connectivity errors

**Severity Levels:**
- `CRIT` - Critical (system down)
- `HIGH` - High (service degraded)
- `WARN` - Warning (potential issues)
- `INFO` - Informational (monitoring)

---

## WebSocket Connection Errors

### OBS-WS-CRIT-001: WebSocket Server Startup Failure

**Symptoms:**
- Observatory server fails to start
- WebSocket endpoints not accessible
- Error: "Failed to bind to port 8888"

**Root Cause Analysis:**
```bash
# Check port availability
lsof -i :8888
netstat -tulpn | grep :8888

# Common causes:
# 1. Port already in use by another process
# 2. Insufficient permissions
# 3. Network interface not available
```

**Recovery Procedure:**
```bash
# Step 1: Identify conflicting process
sudo lsof -i :8888
# Kill conflicting process if safe
sudo kill -9 [PID]

# Step 2: Verify port availability
telnet localhost 8888
# Should fail to connect

# Step 3: Check permissions
sudo netstat -tulpn | grep :8888
# Ensure user has permission to bind to port

# Step 4: Restart Observatory server
make dashboard-up

# Step 5: Validate WebSocket endpoints
wscat -c ws://localhost:8888/ws/observatory
```

**Prevention:**
- Implement port conflict detection in startup scripts
- Use systemd or process manager for automatic restart
- Monitor port usage with Prometheus metrics

### OBS-WS-HIGH-002: WebSocket Connection Limit Exceeded

**Symptoms:**
- New WebSocket connections rejected
- Error: "Connection limit reached for endpoint"
- Existing connections remain stable

**Root Cause Analysis:**
```python
# Check connection limits
endpoint_limits = {
    "/ws/observatory": 250,
    "/ws/emoji-rain": 250, 
    "/ws/anomalies": 100,
    "/ws/doctor-status": 50
}

# Monitor current connections
curl -s http://localhost:8888/metrics | grep websocket_connections
```

**Recovery Procedure:**
```bash
# Step 1: Check current connection count
curl -s http://localhost:8888/health | jq '.websocket_connections'

# Step 2: Identify stale connections
# Review connection pool for inactive connections
curl -s http://localhost:8888/debug/connections

# Step 3: Clean up stale connections
# Trigger connection cleanup
curl -X POST http://localhost:8888/admin/cleanup-connections

# Step 4: Increase limits if necessary (temporary)
# Edit configuration
vim config/websocket.yml
# Restart service
make dashboard-restart

# Step 5: Monitor connection patterns
# Implement connection monitoring
tail -f logs/websocket-connections.log
```

**Prevention:**
- Implement automatic stale connection cleanup
- Monitor connection patterns and adjust limits
- Implement connection pooling on client side

### OBS-WS-WARN-003: WebSocket Message Delivery Failure

**Symptoms:**
- Messages not reaching connected clients
- Error: "Failed to deliver message to client"
- Client connections appear active

**Root Cause Analysis:**
```bash
# Check WebSocket message queue
curl -s http://localhost:8888/debug/message-queue

# Monitor message delivery metrics
curl -s http://localhost:8888/metrics | grep message_delivery

# Common causes:
# 1. Client connection in bad state
# 2. Message serialization failure
# 3. Network congestion
# 4. Client-side processing delays
```

**Recovery Procedure:**
```bash
# Step 1: Identify problematic connections
curl -s http://localhost:8888/debug/failed-deliveries

# Step 2: Test message serialization
echo '{"type": "test", "data": "hello"}' | \
  curl -X POST -d @- http://localhost:8888/debug/test-message

# Step 3: Force connection reset for problematic clients
curl -X POST http://localhost:8888/admin/reset-connection/[CLIENT_ID]

# Step 4: Verify message delivery recovery
wscat -c ws://localhost:8888/ws/observatory
# Send test message and verify receipt

# Step 5: Monitor delivery success rate
watch 'curl -s http://localhost:8888/metrics | grep delivery_success_rate'
```

---

## Tunnel Connectivity Errors

### OBS-TUN-CRIT-004: Cloudflare Tunnel Authentication Failure

**Symptoms:**
- Tunnel fails to establish connection
- Error: "Authentication failed for tunnel"
- External services not accessible

**Root Cause Analysis:**
```bash
# Check tunnel credentials
ls -la ~/.cloudflared/
cat ~/.cloudflared/cert.pem

# Verify tunnel configuration
cloudflared tunnel list
cloudflared tunnel info d1e53e43-033f-4994-8f46-c83962ae3785

# Common causes:
# 1. Expired or invalid credentials
# 2. Tunnel deleted from Cloudflare dashboard
# 3. Network connectivity to Cloudflare API
# 4. Incorrect tunnel ID in configuration
```

**Recovery Procedure:**
```bash
# Step 1: Verify Cloudflare API connectivity
curl -s https://api.cloudflare.com/client/v4/user/tokens/verify \
  -H "Authorization: Bearer [API_TOKEN]"

# Step 2: Re-authenticate tunnel
cloudflared tunnel login
# Follow browser authentication flow

# Step 3: Verify tunnel exists
cloudflared tunnel list | grep d1e53e43-033f-4994-8f46-c83962ae3785

# Step 4: Update tunnel configuration if needed
cloudflared tunnel route dns d1e53e43-033f-4994-8f46-c83962ae3785 observatory.nkllon.com

# Step 5: Restart tunnel with new credentials
make tunnel-stop
make tunnel-start

# Step 6: Validate external access
curl -s https://observatory.nkllon.com/health
```

**Prevention:**
- Monitor tunnel credential expiration
- Implement automatic credential renewal
- Set up alerts for authentication failures

### OBS-TUN-HIGH-005: DNS Propagation Timeout

**Symptoms:**
- Tunnel starts but domains not resolving
- Error: "DNS propagation timeout exceeded"
- Inconsistent domain resolution

**Root Cause Analysis:**
```bash
# Check DNS propagation status
dig observatory.nkllon.com
dig @8.8.8.8 observatory.nkllon.com
dig @1.1.1.1 observatory.nkllon.com

# Test from multiple locations
curl -s "https://dns.google/resolve?name=observatory.nkllon.com&type=A"

# Common causes:
# 1. Cloudflare DNS propagation delays
# 2. Local DNS cache issues
# 3. ISP DNS server problems
# 4. Incorrect DNS configuration
```

**Recovery Procedure:**
```bash
# Step 1: Clear local DNS cache
sudo dscacheutil -flushcache  # macOS
sudo systemctl restart systemd-resolved  # Linux

# Step 2: Test direct Cloudflare DNS
dig @1.1.1.1 observatory.nkllon.com

# Step 3: Check Cloudflare DNS settings
# Login to Cloudflare dashboard
# Verify DNS records for observatory.nkllon.com

# Step 4: Force DNS update if needed
cloudflared tunnel route dns d1e53e43-033f-4994-8f46-c83962ae3785 observatory.nkllon.com

# Step 5: Wait for propagation and test
sleep 60
curl -s https://observatory.nkllon.com/health

# Step 6: Implement DNS monitoring
# Add DNS resolution checks to monitoring
```

**Prevention:**
- Monitor DNS propagation times
- Implement multiple DNS resolver checks
- Set up alerts for DNS resolution failures

### OBS-TUN-WARN-006: WebSocket Proxy Configuration Issues

**Symptoms:**
- HTTP requests work but WebSocket connections fail
- Error: "WebSocket upgrade failed through tunnel"
- Connection drops during WebSocket handshake

**Root Cause Analysis:**
```bash
# Check tunnel configuration for WebSocket support
cat cloudflared-config.yml | grep -A 10 "originRequest"

# Test WebSocket upgrade through tunnel
curl -i -N -H "Connection: Upgrade" \
  -H "Upgrade: websocket" \
  -H "Sec-WebSocket-Key: test" \
  https://observatory.nkllon.com/ws/observatory

# Common causes:
# 1. Missing WebSocket proxy configuration
# 2. Incorrect origin request settings
# 3. Timeout values too low
# 4. Connection upgrade not supported
```

**Recovery Procedure:**
```bash
# Step 1: Update tunnel configuration
cat > cloudflared-config.yml << EOF
tunnel: d1e53e43-033f-4994-8f46-c83962ae3785
credentials-file: ~/.cloudflared/credentials.json

ingress:
  - hostname: observatory.nkllon.com
    service: http://localhost:8888
    originRequest:
      noTLSVerify: true
      connectTimeout: 30s
      tlsTimeout: 10s
      keepAliveTimeout: 90s
      keepAliveConnections: 100
EOF

# Step 2: Restart tunnel with new configuration
make tunnel-stop
make tunnel-start

# Step 3: Test WebSocket connection through tunnel
wscat -c wss://observatory.nkllon.com/ws/observatory

# Step 4: Verify all WebSocket endpoints
for endpoint in observatory emoji-rain anomalies doctor-status; do
  echo "Testing /ws/$endpoint"
  wscat -c "wss://observatory.nkllon.com/ws/$endpoint" --timeout 5000
done

# Step 5: Monitor WebSocket proxy performance
curl -s https://observatory.nkllon.com/metrics | grep websocket
```

---

## Redis Coordination Errors

### OBS-RED-CRIT-007: Redis Primary Connection Failure

**Symptoms:**
- Observatory server cannot connect to Redis
- Error: "Failed to connect to Redis primary"
- Coordination features unavailable

**Root Cause Analysis:**
```bash
# Test Redis connectivity
redis-cli -h 192.168.1.119 -p 6379 ping
telnet 192.168.1.119 6379

# Check Redis server status
redis-cli -h 192.168.1.119 -p 6379 info server

# Common causes:
# 1. Redis server down or unreachable
# 2. Network connectivity issues
# 3. Authentication failure
# 4. Redis server overloaded
# 5. Firewall blocking connection
```

**Recovery Procedure:**
```bash
# Step 1: Test network connectivity
ping 192.168.1.119
telnet 192.168.1.119 6379

# Step 2: Check Redis server status on target machine
ssh user@192.168.1.119 "sudo systemctl status redis"

# Step 3: Attempt Redis server restart (if accessible)
ssh user@192.168.1.119 "sudo systemctl restart redis"

# Step 4: Test fallback Redis connection
redis-cli -h localhost -p 6380 ping

# Step 5: Configure Observatory to use fallback
# Update configuration to use fallback Redis
export REDIS_PRIMARY_HOST=localhost
export REDIS_PRIMARY_PORT=6380

# Step 6: Restart Observatory with fallback configuration
make dashboard-restart

# Step 7: Verify coordination functionality
curl -s http://localhost:8888/health | jq '.redis_coordination'
```

**Prevention:**
- Implement Redis health monitoring
- Set up automatic failover to backup Redis
- Monitor Redis performance metrics

### OBS-RED-HIGH-008: Redis Failover Activation

**Symptoms:**
- Primary Redis connection lost
- System automatically switches to fallback
- Warning: "Redis failover activated"

**Root Cause Analysis:**
```bash
# Check failover status
curl -s http://localhost:8888/health | jq '.redis_coordination'

# Monitor Redis failover logs
tail -f logs/redis-coordination.log

# Verify fallback Redis health
redis-cli -h localhost -p 6380 info replication
```

**Recovery Procedure:**
```bash
# Step 1: Verify fallback Redis is functioning
redis-cli -h localhost -p 6380 ping
redis-cli -h localhost -p 6380 info stats

# Step 2: Test primary Redis recovery
redis-cli -h 192.168.1.119 -p 6379 ping

# Step 3: If primary recovered, test failback
# Check if automatic failback is configured
curl -s http://localhost:8888/debug/redis-config

# Step 4: Manual failback if needed
curl -X POST http://localhost:8888/admin/redis-failback

# Step 5: Verify coordination is working
# Test coordination functionality
curl -X POST http://localhost:8888/debug/test-coordination

# Step 6: Monitor for stability
watch 'curl -s http://localhost:8888/health | jq .redis_coordination'
```

---

## System and Process Errors

### OBS-SYS-CRIT-009: Observatory Process Crash

**Symptoms:**
- Observatory server process terminated unexpectedly
- All WebSocket connections lost
- Health endpoints not responding

**Root Cause Analysis:**
```bash
# Check system logs for crash information
journalctl -u observatory --since "1 hour ago"
tail -f /var/log/syslog | grep observatory

# Check for core dumps
ls -la /var/crash/
ls -la core.*

# Monitor system resources
free -h
df -h
top -p $(pgrep observatory)

# Common causes:
# 1. Out of memory (OOM killer)
# 2. Segmentation fault
# 3. Unhandled exception
# 4. Resource exhaustion
# 5. System shutdown/reboot
```

**Recovery Procedure:**
```bash
# Step 1: Check system resources
free -h
df -h
uptime

# Step 2: Clear any remaining processes
pkill -f observatory
sleep 5

# Step 3: Check port availability
lsof -i :8888

# Step 4: Restart Observatory server
make dashboard-up

# Step 5: Verify startup success
curl -s http://localhost:8888/health
wscat -c ws://localhost:8888/ws/observatory

# Step 6: Monitor for stability
tail -f logs/observatory.log

# Step 7: Investigate crash cause
# Analyze logs for error patterns
grep -i "error\|exception\|crash" logs/observatory.log

# Step 8: Implement monitoring
# Add process monitoring to prevent future crashes
```

**Prevention:**
- Implement process monitoring and automatic restart
- Monitor system resources and set alerts
- Implement graceful error handling
- Regular log analysis for early warning signs

---

## Network Connectivity Errors

### OBS-NET-HIGH-010: External Network Connectivity Loss

**Symptoms:**
- Cannot reach external services
- Tunnel connection fails
- DNS resolution failures

**Root Cause Analysis:**
```bash
# Test basic connectivity
ping 8.8.8.8
ping google.com
curl -s https://api.cloudflare.com/client/v4/

# Check network interface status
ip addr show
route -n

# Test DNS resolution
nslookup google.com
dig @8.8.8.8 google.com

# Common causes:
# 1. Internet connection down
# 2. DNS server issues
# 3. Firewall blocking connections
# 4. Network interface problems
# 5. ISP issues
```

**Recovery Procedure:**
```bash
# Step 1: Test basic network connectivity
ping -c 4 8.8.8.8

# Step 2: Check network interface
sudo ip link show
sudo ip addr show

# Step 3: Restart network interface if needed
sudo ip link set eth0 down
sudo ip link set eth0 up

# Step 4: Test DNS resolution
dig @8.8.8.8 observatory.nkllon.com

# Step 5: Restart network services if needed
sudo systemctl restart networking  # Debian/Ubuntu
sudo systemctl restart NetworkManager  # CentOS/RHEL

# Step 6: Verify Observatory connectivity
make tunnel-start
curl -s https://observatory.nkllon.com/health

# Step 7: Monitor network stability
ping -i 5 8.8.8.8 | tee network-monitor.log
```

---

## Error Recovery Automation

### Automated Recovery Scripts

#### WebSocket Connection Recovery
```bash
#!/bin/bash
# websocket-recovery.sh

echo "Starting WebSocket connection recovery..."

# Check WebSocket endpoints
endpoints=("observatory" "emoji-rain" "anomalies" "doctor-status")
failed_endpoints=()

for endpoint in "${endpoints[@]}"; do
    if ! wscat -c "ws://localhost:8888/ws/$endpoint" --timeout 3000 2>/dev/null; then
        failed_endpoints+=("$endpoint")
    fi
done

if [ ${#failed_endpoints[@]} -gt 0 ]; then
    echo "Failed endpoints: ${failed_endpoints[*]}"
    echo "Restarting Observatory server..."
    make dashboard-restart
    
    # Wait for restart
    sleep 30
    
    # Verify recovery
    for endpoint in "${failed_endpoints[@]}"; do
        if wscat -c "ws://localhost:8888/ws/$endpoint" --timeout 5000 2>/dev/null; then
            echo "✅ $endpoint recovered"
        else
            echo "❌ $endpoint still failing"
        fi
    done
else
    echo "✅ All WebSocket endpoints healthy"
fi
```

#### Redis Coordination Recovery
```bash
#!/bin/bash
# redis-recovery.sh

echo "Starting Redis coordination recovery..."

# Test primary Redis
if redis-cli -h 192.168.1.119 -p 6379 ping >/dev/null 2>&1; then
    echo "✅ Primary Redis healthy"
    
    # Check if Observatory is using primary
    redis_host=$(curl -s http://localhost:8888/debug/redis-config | jq -r '.current_host')
    if [ "$redis_host" != "192.168.1.119" ]; then
        echo "Switching back to primary Redis..."
        curl -X POST http://localhost:8888/admin/redis-failback
    fi
else
    echo "⚠️ Primary Redis unavailable"
    
    # Test fallback Redis
    if redis-cli -h localhost -p 6380 ping >/dev/null 2>&1; then
        echo "✅ Fallback Redis healthy"
        
        # Ensure Observatory is using fallback
        redis_host=$(curl -s http://localhost:8888/debug/redis-config | jq -r '.current_host')
        if [ "$redis_host" != "localhost" ]; then
            echo "Switching to fallback Redis..."
            curl -X POST http://localhost:8888/admin/redis-failover
        fi
    else
        echo "❌ Both Redis instances unavailable - manual intervention required"
        exit 1
    fi
fi
```

### Monitoring Integration

#### Prometheus Alerts
```yaml
# alerts.yml
groups:
  - name: observatory_errors
    rules:
      - alert: WebSocketConnectionFailure
        expr: websocket_connection_failures_total > 10
        for: 5m
        labels:
          severity: critical
        annotations:
          summary: "High WebSocket connection failure rate"
          description: "WebSocket connections failing at {{ $value }} per minute"
      
      - alert: RedisConnectionLoss
        expr: redis_connection_status == 0
        for: 1m
        labels:
          severity: critical
        annotations:
          summary: "Redis connection lost"
          description: "Observatory cannot connect to Redis coordination"
      
      - alert: TunnelConnectivityFailure
        expr: tunnel_connectivity_status == 0
        for: 2m
        labels:
          severity: high
        annotations:
          summary: "Cloudflare tunnel connectivity lost"
          description: "External access via tunnel is unavailable"
```

## Success Criteria

### Error Documentation:
- ✅ Comprehensive error codes for all major failure scenarios
- ✅ Root cause analysis procedures for each error type
- ✅ Step-by-step recovery instructions with validation
- ✅ Prevention strategies to avoid recurrence
- ✅ Automated recovery scripts for common issues

### Integration Requirements:
- ✅ Error codes integrated with monitoring systems
- ✅ Recovery procedures tested and validated
- ✅ Automation scripts functional and reliable
- ✅ Prometheus alerts configured for all critical errors

This error codes and recovery guide provides systematic troubleshooting capabilities for all major failure scenarios in the Beast Mode Observatory system, ensuring rapid diagnosis and recovery from operational issues.