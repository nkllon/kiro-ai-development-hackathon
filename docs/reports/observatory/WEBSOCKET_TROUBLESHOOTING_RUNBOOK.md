# WebSocket Troubleshooting Runbook

## 🚨 Emergency Response Procedures

### Critical Issue Response (Service Down)

**Response Time**: 5 minutes  
**Escalation Level**: Level 4  
**Team**: Observatory Infrastructure Team

#### **Step 1: Immediate Assessment (2 minutes)**

```bash
# Quick health check
curl -I https://observatory.nkllon.com/health

# Check WebSocket status
curl -I -H "Upgrade: websocket" -H "Connection: Upgrade" \
  https://observatory.nkllon.com/ws/observatory

# Check tunnel status
cloudflared tunnel list
```

**Expected Results:**
- Health endpoint: `HTTP/2 200 OK`
- WebSocket endpoint: `HTTP/1.1 101 Switching Protocols`
- Tunnel status: `ACTIVE`

#### **Step 2: Identify Issue Type (3 minutes)**

| Response | Issue Type | Action |
|----------|------------|--------|
| HTTP/2 404 | WebSocket config missing | Apply WebSocket configuration |
| HTTP/2 503 | Service unavailable | Check Observatory server |
| HTTP/2 403 | Bot protection | Check rate limiting |
| Timeout | Network issue | Check connectivity |

#### **Step 3: Apply Emergency Fix**

**WebSocket Configuration Missing:**
```bash
# Emergency configuration update
cp cloudflare-tunnel-config-websocket.yml ~/.cloudflared/config.yml
pkill -f cloudflared && sleep 2 && cloudflared tunnel run
```

**Service Unavailable:**
```bash
# Restart Observatory server
sudo systemctl restart observatory
# OR
pkill -f observatory && python src/beast_mode/observatory/server.py
```

**Bot Protection Triggered:**
```bash
# Check and adjust rate limiting
python scripts/configure_bot_protection.py --emergency-reset
```

---

## 🔍 Diagnostic Procedures

### WebSocket Connectivity Diagnostics

#### **Test 1: Local WebSocket Test**

```bash
# Test local WebSocket connectivity
curl -I -H "Upgrade: websocket" -H "Connection: Upgrade" \
  http://localhost:8888/ws/observatory

# Expected: HTTP/1.1 101 Switching Protocols
# Problem: HTTP/1.1 404 Not Found
```

**If Local Test Fails:**
- Check Observatory server status
- Verify WebSocket endpoints are registered
- Check server logs for errors

#### **Test 2: Tunnel WebSocket Test**

```bash
# Test WebSocket through tunnel
curl -I -H "Upgrade: websocket" -H "Connection: Upgrade" \
  https://observatory.nkllon.com/ws/observatory

# Expected: HTTP/1.1 101 Switching Protocols
# Problem: HTTP/2 404 Not Found
```

**If Tunnel Test Fails:**
- Check cloudflared configuration
- Verify WebSocket settings in config
- Restart tunnel service

#### **Test 3: Comprehensive Endpoint Test**

```bash
# Test all WebSocket endpoints
python scripts/test_websocket_connectivity.py --comprehensive

# Check specific endpoint
python scripts/test_websocket_connectivity.py --endpoint /ws/observatory
```

### Configuration Validation

#### **Cloudflare Tunnel Configuration Check**

```bash
# Check current configuration
cat ~/.cloudflared/config.yml

# Validate WebSocket settings
grep -A 15 "originRequest:" ~/.cloudflared/config.yml | grep -E "(connectTimeout|tcpKeepAlive|keepAliveConnections)"
```

**Required WebSocket Settings:**
```yaml
originRequest:
  noTLSVerify: true
  connectTimeout: 30s
  tlsTimeout: 10s
  tcpKeepAlive: 30s
  keepAliveConnections: 100
  keepAliveTimeout: 90s
```

#### **Observatory Server Configuration Check**

```bash
# Check Observatory configuration
cat config/observatory.yaml | grep -A 10 "websocket"

# Check WebSocket endpoints
grep -r "websocket" src/beast_mode/observatory/ | grep -E "(route|endpoint)"
```

### Performance Diagnostics

#### **Connection Performance Test**

```bash
# Test connection latency
python scripts/websocket_monitoring.py --test-latency

# Test message throughput
python scripts/websocket_monitoring.py --test-throughput

# Test concurrent connections
python scripts/websocket_monitoring.py --test-concurrency
```

#### **Resource Usage Check**

```bash
# Check memory usage
ps aux | grep observatory | awk '{print $4, $6}'

# Check CPU usage
top -p $(pgrep observatory) -n 1

# Check connection count
netstat -an | grep :8888 | wc -l
```

---

## 🛠️ Common Solutions

### Solution 1: WebSocket Configuration Missing

**Symptoms:**
- WebSocket returns HTTP/2 404
- Local WebSocket works, tunnel WebSocket fails
- Dashboard shows WebSocket unavailable

**Root Cause:**
Missing WebSocket-specific configuration in cloudflared

**Solution:**
```bash
# Apply WebSocket configuration
cp cloudflare-tunnel-config-websocket.yml ~/.cloudflared/config.yml

# Restart tunnel service
pkill -f cloudflared
sleep 2
cloudflared tunnel run

# Verify fix
curl -I -H "Upgrade: websocket" -H "Connection: Upgrade" \
  https://observatory.nkllon.com/ws/observatory
```

**Expected Result:** `HTTP/1.1 101 Switching Protocols`

### Solution 2: Bot Protection Triggered

**Symptoms:**
- Error 1033 service unavailable
- High HTTP polling frequency
- Legitimate traffic blocked

**Root Cause:**
HTTP polling fallback triggers bot protection

**Solution:**
```bash
# Check current request patterns
python scripts/websocket_monitoring.py --analyze-traffic

# Adjust rate limiting
python scripts/configure_bot_protection.py --update-rules

# Whitelist Observatory IP
python scripts/configure_bot_protection.py --whitelist-observatory
```

**Prevention:**
- Implement proper rate limiting in HTTP polling
- Use exponential backoff
- Whitelist Observatory server IPs

### Solution 3: High Resource Usage

**Symptoms:**
- Memory/CPU spikes
- Slow response times
- Connection timeouts

**Root Cause:**
Too many concurrent connections or resource leaks

**Solution:**
```bash
# Check connection count
netstat -an | grep :8888 | wc -l

# Check memory usage
ps aux | grep observatory

# Adjust connection limits
# Edit config/observatory.yaml
max_connections: 50  # Reduce from 100

# Restart Observatory server
sudo systemctl restart observatory
```

### Solution 4: Network Connectivity Issues

**Symptoms:**
- Connection timeouts
- Intermittent failures
- High latency

**Root Cause:**
Network connectivity problems

**Solution:**
```bash
# Test network connectivity
ping observatory.nkllon.com
traceroute observatory.nkllon.com

# Check DNS resolution
nslookup observatory.nkllon.com

# Test tunnel connectivity
cloudflared tunnel run --loglevel debug
```

### Solution 5: Observatory Server Issues

**Symptoms:**
- Local WebSocket fails
- Server not responding
- Health check fails

**Root Cause:**
Observatory server problems

**Solution:**
```bash
# Check server status
curl http://localhost:8888/health

# Check server logs
tail -f logs/observatory.log

# Restart server
sudo systemctl restart observatory
# OR
pkill -f observatory && python src/beast_mode/observatory/server.py
```

---

## 📊 Monitoring & Alerting

### Health Check Procedures

#### **Automated Health Checks**

```bash
# Start continuous monitoring
python scripts/websocket_monitoring.py --daemon

# Check monitoring status
python scripts/websocket_monitoring.py --status

# View health history
python scripts/websocket_monitoring.py --history
```

#### **Manual Health Checks**

```bash
# Quick health check
python scripts/websocket_monitoring.py --quick-check

# Comprehensive health check
python scripts/websocket_monitoring.py --full-check

# Performance benchmark
python scripts/websocket_monitoring.py --benchmark
```

### Alert Configuration

#### **Critical Alerts**

**WebSocket Connection Failure:**
- Trigger: WebSocket endpoint returns non-101 status
- Action: Immediate notification + automatic HTTP polling fallback
- Escalation: Level 4 (5 minutes)

**Service Unavailability:**
- Trigger: Health endpoint returns non-200 status
- Action: Immediate notification + automatic recovery
- Escalation: Level 4 (5 minutes)

**Bot Protection Trigger:**
- Trigger: Error 1033 detected
- Action: Immediate notification + rate limiting adjustment
- Escalation: Level 3 (15 minutes)

#### **Warning Alerts**

**High Latency:**
- Trigger: WebSocket latency > 500ms
- Action: Performance investigation
- Escalation: Level 2 (1 hour)

**Low Throughput:**
- Trigger: Message throughput < 50 msg/sec
- Action: Performance optimization
- Escalation: Level 2 (1 hour)

**High Error Rate:**
- Trigger: Error rate > 1%
- Action: Error analysis
- Escalation: Level 2 (1 hour)

### Dashboard Monitoring

#### **Real-Time Status Dashboard**

```javascript
// WebSocket Status Display
const statusDisplay = {
    endpoints: [
        { name: 'emoji-rain', status: 'healthy', latency: '45ms' },
        { name: 'observatory', status: 'healthy', latency: '42ms' },
        { name: 'anomalies', status: 'healthy', latency: '48ms' },
        { name: 'doctor-status', status: 'healthy', latency: '41ms' }
    ],
    overall: 'operational',
    metrics: {
        avgLatency: '45ms',
        throughput: '250 msg/sec',
        successRate: '99.2%',
        activeConnections: 15
    }
};
```

#### **Performance Trends**

- Historical latency trends
- Throughput patterns over time
- Connection success rate history
- Resource usage trends
- Error rate analysis

---

## 🔄 Recovery Procedures

### Automated Recovery

#### **Level 1: Automatic Fallback**

**Trigger:** WebSocket connection failure detected  
**Action:** Automatic HTTP polling fallback activation  
**Timeout:** 30 seconds  
**Success Criteria:** Service availability maintained

```bash
# Automatic fallback is handled by Observatory dashboard
# No manual intervention required
```

#### **Level 2: Configuration Recovery**

**Trigger:** Persistent WebSocket failures (>5 minutes)  
**Action:** Tunnel configuration reload and restart  
**Timeout:** 2 minutes  
**Success Criteria:** WebSocket connectivity restored

```bash
# Automatic configuration recovery
python scripts/fix_cloudflared_websocket.py --auto-recovery
```

#### **Level 3: Infrastructure Recovery**

**Trigger:** Complete service unavailability  
**Action:** Full infrastructure restart and validation  
**Timeout:** 10 minutes  
**Success Criteria:** All services operational

```bash
# Full infrastructure recovery
python scripts/rollback_deployment.py --emergency-recovery
```

### Manual Recovery

#### **Emergency Configuration Update**

```bash
# Backup current configuration
cp ~/.cloudflared/config.yml ~/.cloudflared/config.yml.backup.$(date +%Y%m%d_%H%M%S)

# Apply emergency configuration
cp cloudflare-tunnel-config-websocket.yml ~/.cloudflared/config.yml

# Restart services
pkill -f cloudflared && sleep 2 && cloudflared tunnel run
```

#### **Service Restart Procedure**

```bash
# Stop all services
pkill -f cloudflared
pkill -f observatory

# Wait for processes to stop
sleep 5

# Start Observatory server
python src/beast_mode/observatory/server.py &

# Start cloudflared tunnel
cloudflared tunnel run &

# Verify services are running
sleep 10
curl http://localhost:8888/health
```

#### **Rollback Procedure**

```bash
# Restore backup configuration
cp ~/.cloudflared/config.yml.backup ~/.cloudflared/config.yml

# Restart tunnel service
pkill -f cloudflared && sleep 2 && cloudflared tunnel run

# Verify rollback
curl -I -H "Upgrade: websocket" -H "Connection: Upgrade" \
  https://observatory.nkllon.com/ws/observatory
```

---

## 📋 Troubleshooting Checklist

### Pre-Troubleshooting

- [ ] **Verify Issue Scope**
  - [ ] Check if issue affects all WebSocket endpoints
  - [ ] Determine if issue is local or tunnel-related
  - [ ] Check if issue affects all users or specific users

- [ ] **Gather Information**
  - [ ] Check Observatory server logs
  - [ ] Check cloudflared tunnel logs
  - [ ] Check monitoring dashboard
  - [ ] Gather user reports

### Diagnostic Steps

- [ ] **Test Local Connectivity**
  - [ ] Test WebSocket endpoints locally
  - [ ] Check Observatory server health
  - [ ] Verify local configuration

- [ ] **Test Tunnel Connectivity**
  - [ ] Test WebSocket endpoints through tunnel
  - [ ] Check tunnel configuration
  - [ ] Verify tunnel status

- [ ] **Check Performance**
  - [ ] Measure connection latency
  - [ ] Check message throughput
  - [ ] Monitor resource usage

### Resolution Steps

- [ ] **Apply Configuration Fix**
  - [ ] Update cloudflared configuration
  - [ ] Restart tunnel service
  - [ ] Verify WebSocket connectivity

- [ ] **Apply Service Fix**
  - [ ] Restart Observatory server
  - [ ] Check service health
  - [ ] Verify endpoint accessibility

- [ ] **Apply Performance Fix**
  - [ ] Adjust connection limits
  - [ ] Optimize resource usage
  - [ ] Monitor performance metrics

### Post-Resolution

- [ ] **Verify Resolution**
  - [ ] Test all WebSocket endpoints
  - [ ] Check performance metrics
  - [ ] Verify user experience

- [ ] **Document Incident**
  - [ ] Record issue details
  - [ ] Document resolution steps
  - [ ] Update runbook if needed

- [ ] **Prevent Recurrence**
  - [ ] Implement monitoring improvements
  - [ ] Update configuration validation
  - [ ] Schedule regular health checks

---

## 🎯 Prevention Measures

### Proactive Monitoring

#### **Continuous Health Monitoring**

```bash
# Start continuous monitoring
python scripts/websocket_monitoring.py --daemon --continuous

# Monitor specific metrics
python scripts/websocket_monitoring.py --monitor-latency
python scripts/websocket_monitoring.py --monitor-throughput
python scripts/websocket_monitoring.py --monitor-connections
```

#### **Automated Testing**

```bash
# Run automated WebSocket tests
python scripts/test_websocket_connectivity.py --automated

# Schedule regular tests
crontab -e
# Add: */15 * * * * python scripts/test_websocket_connectivity.py --automated
```

### Configuration Management

#### **Configuration Validation**

```bash
# Validate cloudflared configuration
cloudflared tunnel run --config ~/.cloudflared/config.yml --dry-run

# Validate Observatory configuration
python src/beast_mode/observatory/server.py --validate-config
```

#### **Change Management**

```bash
# Track configuration changes
git add ~/.cloudflared/config.yml
git commit -m "Update WebSocket configuration"

# Document changes
echo "$(date): WebSocket configuration updated" >> logs/config_changes.log
```

### Capacity Planning

#### **Resource Monitoring**

```bash
# Monitor resource usage
python scripts/monitor_workers.sh --resource-monitoring

# Check connection limits
python scripts/monitor_workers.sh --connection-limits

# Monitor performance trends
python scripts/monitor_workers.sh --performance-trends
```

#### **Scalability Planning**

```bash
# Analyze current capacity
python scripts/monitor_workers.sh --capacity-analysis

# Plan for growth
python scripts/monitor_workers.sh --scalability-planning
```

---

## 📞 Escalation Procedures

### Escalation Matrix

| Issue Severity | Response Time | Escalation Level | Contact |
|----------------|---------------|------------------|---------|
| Critical (Service Down) | 5 minutes | Level 4 | On-call Engineer |
| High (Performance Degraded) | 15 minutes | Level 3 | Senior Engineer |
| Medium (Monitoring Alert) | 1 hour | Level 2 | Infrastructure Team |
| Low (Documentation Update) | 24 hours | Level 1 | Team Lead |

### Contact Information

**Primary Support**: Observatory Infrastructure Team  
**Escalation**: Senior Infrastructure Engineer  
**Emergency**: 24/7 On-call Engineer  
**Management**: Infrastructure Manager

### Communication Procedures

#### **Critical Issues**

1. **Immediate Notification**
   - Alert on-call engineer
   - Notify team lead
   - Update status page

2. **Status Updates**
   - Every 15 minutes during incident
   - Post-incident report within 24 hours
   - Lessons learned documentation

3. **Resolution Communication**
   - Notify all stakeholders
   - Update documentation
   - Schedule post-incident review

---

*This runbook is maintained as part of the Observatory infrastructure and should be updated whenever WebSocket-related procedures change.*

**Last Updated**: 2024-12-19  
**Next Review**: 2025-01-19  
**Version**: 1.0