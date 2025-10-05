# WebSocket Troubleshooting Guide
## Observatory WebSocket Infrastructure Troubleshooting

**Target**: observatory.nkllon.com WebSocket infrastructure  
**Purpose**: Comprehensive troubleshooting procedures and solutions  
**Version**: 1.0  
**Last Updated**: 2025-01-27  

---

## 📋 Table of Contents

1. [Quick Diagnostic Procedures](#quick-diagnostic-procedures)
2. [Common Issues & Solutions](#common-issues--solutions)
3. [Advanced Troubleshooting](#advanced-troubleshooting)
4. [Performance Issues](#performance-issues)
5. [Security Issues](#security-issues)
6. [Network Issues](#network-issues)
7. [Configuration Issues](#configuration-issues)
8. [Recovery Procedures](#recovery-procedures)

---

## 🚀 Quick Diagnostic Procedures

### 30-Second Health Check

```bash
# Quick system health check
curl -I https://observatory.nkllon.com/health
curl -I -H "Upgrade: websocket" -H "Connection: Upgrade" \
  https://observatory.nkllon.com/ws/observatory
cloudflared tunnel list
```

**Expected Results:**
- Health endpoint: `HTTP/2 200 OK`
- WebSocket endpoint: `HTTP/1.1 101 Switching Protocols`
- Tunnel status: `ACTIVE`

### 2-Minute Diagnostic

```bash
# Comprehensive diagnostic
python scripts/test_websocket_connectivity.py --quick
python scripts/websocket_monitoring.py --status
python scripts/monitor_workers.sh --quick-check
```

### 5-Minute Deep Diagnostic

```bash
# Deep diagnostic analysis
python scripts/test_websocket_connectivity.py --comprehensive
python scripts/websocket_monitoring.py --full-diagnostic
python scripts/monitor_workers.sh --comprehensive-check
```

---

## 🔧 Common Issues & Solutions

### Issue 1: WebSocket Returns HTTP/2 404

**Symptoms:**
- WebSocket connections return `HTTP/2 404 Not Found`
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

**Prevention:**
- Regular configuration validation
- Automated configuration testing
- Configuration change monitoring

### Issue 2: Error 1033 Service Unavailable

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

### Issue 3: High Resource Usage

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

**Prevention:**
- Monitor connection limits
- Implement connection pooling
- Regular resource monitoring

### Issue 4: Connection Timeouts

**Symptoms:**
- WebSocket connections timeout
- Intermittent connection failures
- High latency

**Root Cause:**
Network connectivity problems or configuration issues

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

**Prevention:**
- Network monitoring
- DNS monitoring
- Tunnel health checks

### Issue 5: Observatory Server Issues

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

**Prevention:**
- Server health monitoring
- Automatic restart mechanisms
- Resource monitoring

---

## 🔍 Advanced Troubleshooting

### WebSocket Protocol Analysis

#### Protocol Upgrade Analysis

```bash
# Analyze WebSocket handshake
curl -v -H "Upgrade: websocket" -H "Connection: Upgrade" \
  -H "Sec-WebSocket-Key: dGhlIHNhbXBsZSBub25jZQ==" \
  -H "Sec-WebSocket-Version: 13" \
  https://observatory.nkllon.com/ws/observatory
```

**Expected Response:**
```
HTTP/1.1 101 Switching Protocols
Upgrade: websocket
Connection: Upgrade
Sec-WebSocket-Accept: s3pPLMBiTxaQ9kYGzzhZRbK+xOo=
```

#### Message Flow Analysis

```bash
# Test WebSocket message flow
python scripts/test_websocket_connectivity.py --message-flow-test

# Analyze message patterns
python scripts/websocket_monitoring.py --message-analysis

# Check message integrity
python scripts/test_websocket_connectivity.py --message-integrity-test
```

### Performance Analysis

#### Latency Analysis

```bash
# Test connection latency
python scripts/websocket_monitoring.py --latency-test --iterations 100

# Analyze latency patterns
python scripts/websocket_monitoring.py --latency-analysis

# Check latency distribution
python scripts/websocket_monitoring.py --latency-distribution
```

#### Throughput Analysis

```bash
# Test message throughput
python scripts/websocket_monitoring.py --throughput-test --duration 60

# Analyze throughput patterns
python scripts/websocket_monitoring.py --throughput-analysis

# Check throughput bottlenecks
python scripts/websocket_monitoring.py --throughput-bottlenecks
```

### Connection Analysis

#### Connection Pool Analysis

```bash
# Analyze connection pool
python scripts/websocket_monitoring.py --connection-pool-analysis

# Check connection reuse
python scripts/websocket_monitoring.py --connection-reuse-analysis

# Monitor connection lifecycle
python scripts/websocket_monitoring.py --connection-lifecycle-monitoring
```

#### Concurrent Connection Analysis

```bash
# Test concurrent connections
python scripts/websocket_monitoring.py --concurrent-connection-test --connections 50

# Analyze connection patterns
python scripts/websocket_monitoring.py --connection-pattern-analysis

# Check connection limits
python scripts/websocket_monitoring.py --connection-limit-check
```

---

## ⚡ Performance Issues

### High Latency Issues

#### Latency Diagnosis

```bash
# Measure end-to-end latency
python scripts/websocket_monitoring.py --end-to-end-latency-test

# Check network latency
ping observatory.nkllon.com
traceroute observatory.nkllon.com

# Measure tunnel latency
python scripts/websocket_monitoring.py --tunnel-latency-test
```

#### Latency Optimization

```bash
# Optimize connection settings
python scripts/websocket_monitoring.py --connection-optimization

# Adjust timeout settings
python scripts/websocket_monitoring.py --timeout-optimization

# Implement connection pooling
python scripts/websocket_monitoring.py --connection-pooling
```

### Low Throughput Issues

#### Throughput Diagnosis

```bash
# Measure message throughput
python scripts/websocket_monitoring.py --throughput-measurement

# Check message processing
python scripts/websocket_monitoring.py --message-processing-analysis

# Analyze bottlenecks
python scripts/websocket_monitoring.py --bottleneck-analysis
```

#### Throughput Optimization

```bash
# Optimize message processing
python scripts/websocket_monitoring.py --message-processing-optimization

# Implement message batching
python scripts/websocket_monitoring.py --message-batching

# Optimize connection handling
python scripts/websocket_monitoring.py --connection-handling-optimization
```

### Resource Exhaustion Issues

#### Resource Monitoring

```bash
# Monitor memory usage
python scripts/monitor_workers.sh --memory-monitoring

# Monitor CPU usage
python scripts/monitor_workers.sh --cpu-monitoring

# Monitor connection count
python scripts/monitor_workers.sh --connection-monitoring
```

#### Resource Optimization

```bash
# Optimize memory usage
python scripts/monitor_workers.sh --memory-optimization

# Optimize CPU usage
python scripts/monitor_workers.sh --cpu-optimization

# Implement resource limits
python scripts/monitor_workers.sh --resource-limits
```

---

## 🔒 Security Issues

### Authentication Issues

#### Authentication Diagnosis

```bash
# Test authentication mechanisms
python scripts/test_websocket_connectivity.py --auth-test

# Check authentication patterns
python scripts/test_websocket_connectivity.py --auth-pattern-analysis

# Validate authentication tokens
python scripts/test_websocket_connectivity.py --token-validation-test
```

#### Authentication Resolution

```bash
# Fix authentication issues
python scripts/test_websocket_connectivity.py --auth-fix

# Update authentication configuration
python scripts/configure_authentication.py --update-config

# Reset authentication tokens
python scripts/configure_authentication.py --reset-tokens
```

### Rate Limiting Issues

#### Rate Limiting Diagnosis

```bash
# Test rate limiting
python scripts/test_websocket_connectivity.py --rate-limit-test

# Analyze rate limiting patterns
python scripts/websocket_monitoring.py --rate-limit-analysis

# Check rate limiting effectiveness
python scripts/websocket_monitoring.py --rate-limit-effectiveness
```

#### Rate Limiting Resolution

```bash
# Adjust rate limiting
python scripts/configure_bot_protection.py --adjust-rate-limits

# Whitelist legitimate traffic
python scripts/configure_bot_protection.py --whitelist-traffic

# Implement adaptive rate limiting
python scripts/configure_bot_protection.py --adaptive-rate-limiting
```

### TLS/SSL Issues

#### TLS Diagnosis

```bash
# Test TLS configuration
openssl s_client -connect observatory.nkllon.com:443 -servername observatory.nkllon.com

# Check certificate validity
python scripts/verify_ssl_tls.py --certificate-check

# Test TLS handshake
python scripts/test_websocket_connectivity.py --tls-handshake-test
```

#### TLS Resolution

```bash
# Fix TLS configuration
python scripts/verify_ssl_tls.py --fix-configuration

# Update certificates
python scripts/verify_ssl_tls.py --update-certificates

# Optimize TLS settings
python scripts/verify_ssl_tls.py --optimize-settings
```

---

## 🌐 Network Issues

### Connectivity Issues

#### Network Diagnosis

```bash
# Test basic connectivity
ping observatory.nkllon.com
traceroute observatory.nkllon.com

# Test DNS resolution
nslookup observatory.nkllon.com
dig observatory.nkllon.com

# Test port connectivity
telnet observatory.nkllon.com 443
```

#### Network Resolution

```bash
# Fix DNS issues
python scripts/fix_dns_issues.py

# Fix connectivity issues
python scripts/fix_connectivity_issues.py

# Optimize network settings
python scripts/optimize_network_settings.py
```

### Tunnel Issues

#### Tunnel Diagnosis

```bash
# Check tunnel status
cloudflared tunnel list

# Check tunnel logs
tail -f logs/cloudflared.log

# Test tunnel connectivity
cloudflared tunnel run --loglevel debug
```

#### Tunnel Resolution

```bash
# Restart tunnel
pkill -f cloudflared && sleep 2 && cloudflared tunnel run

# Fix tunnel configuration
python scripts/fix_cloudflared_websocket.py

# Optimize tunnel settings
python scripts/optimize_tunnel_settings.py
```

### Firewall Issues

#### Firewall Diagnosis

```bash
# Check firewall rules
iptables -L
ufw status

# Test firewall connectivity
python scripts/test_firewall_connectivity.py

# Check blocked connections
python scripts/check_blocked_connections.py
```

#### Firewall Resolution

```bash
# Fix firewall rules
python scripts/fix_firewall_rules.py

# Update firewall configuration
python scripts/update_firewall_config.py

# Optimize firewall settings
python scripts/optimize_firewall_settings.py
```

---

## ⚙️ Configuration Issues

### Configuration Validation

#### Configuration Check

```bash
# Validate cloudflared configuration
cloudflared tunnel run --config ~/.cloudflared/config.yml --dry-run

# Validate Observatory configuration
python src/beast_mode/observatory/server.py --validate-config

# Check configuration integrity
python scripts/validate_deployment.py
```

#### Configuration Fix

```bash
# Fix configuration issues
python scripts/fix_configuration_issues.py

# Update configuration
python scripts/update_configuration.py

# Restore configuration
python scripts/restore_configuration.py
```

### Configuration Drift

#### Drift Detection

```bash
# Detect configuration drift
python scripts/websocket_monitoring.py --config-drift-detection

# Compare configurations
python scripts/compare_configurations.py

# Check configuration compliance
python scripts/websocket_monitoring.py --config-compliance-check
```

#### Drift Resolution

```bash
# Fix configuration drift
python scripts/fix_configuration_drift.py

# Synchronize configurations
python scripts/synchronize_configurations.py

# Update configuration management
python scripts/update_configuration_management.py
```

---

## 🔄 Recovery Procedures

### Automatic Recovery

#### Level 1: Automatic Fallback

**Trigger:** WebSocket connection failure detected  
**Action:** Automatic HTTP polling fallback activation  
**Timeout:** 30 seconds  
**Success Criteria:** Service availability maintained

```bash
# Automatic fallback is handled by Observatory dashboard
# No manual intervention required
```

#### Level 2: Configuration Recovery

**Trigger:** Persistent WebSocket failures (>5 minutes)  
**Action:** Tunnel configuration reload and restart  
**Timeout:** 2 minutes  
**Success Criteria:** WebSocket connectivity restored

```bash
# Automatic configuration recovery
python scripts/fix_cloudflared_websocket.py --auto-recovery
```

#### Level 3: Infrastructure Recovery

**Trigger:** Complete service unavailability  
**Action:** Full infrastructure restart and validation  
**Timeout:** 10 minutes  
**Success Criteria:** All services operational

```bash
# Full infrastructure recovery
python scripts/rollback_deployment.py --emergency-recovery
```

### Manual Recovery

#### Emergency Configuration Update

```bash
# Backup current configuration
cp ~/.cloudflared/config.yml ~/.cloudflared/config.yml.backup.$(date +%Y%m%d_%H%M%S)

# Apply emergency configuration
cp cloudflare-tunnel-config-websocket.yml ~/.cloudflared/config.yml

# Restart services
pkill -f cloudflared && sleep 2 && cloudflared tunnel run
```

#### Service Restart Procedure

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

#### Rollback Procedure

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

## 📊 Diagnostic Tools

### Built-in Diagnostic Scripts

#### WebSocket Connectivity Tester

```bash
# Basic connectivity test
python scripts/test_websocket_connectivity.py

# Comprehensive test
python scripts/test_websocket_connectivity.py --comprehensive

# Specific endpoint test
python scripts/test_websocket_connectivity.py --endpoint /ws/observatory
```

#### WebSocket Monitoring

```bash
# Status check
python scripts/websocket_monitoring.py --status

# Health check
python scripts/websocket_monitoring.py --health-check

# Performance test
python scripts/websocket_monitoring.py --performance-test
```

#### Worker Monitoring

```bash
# Quick check
python scripts/monitor_workers.sh --quick-check

# Comprehensive check
python scripts/monitor_workers.sh --comprehensive-check

# Resource monitoring
python scripts/monitor_workers.sh --resource-monitoring
```

### Custom Diagnostic Commands

#### Connection Analysis

```bash
# Analyze connection patterns
python scripts/websocket_monitoring.py --connection-analysis

# Check connection health
python scripts/websocket_monitoring.py --connection-health

# Monitor connection lifecycle
python scripts/websocket_monitoring.py --connection-lifecycle
```

#### Performance Analysis

```bash
# Analyze performance metrics
python scripts/websocket_monitoring.py --performance-analysis

# Check performance trends
python scripts/websocket_monitoring.py --performance-trends

# Identify performance bottlenecks
python scripts/websocket_monitoring.py --performance-bottlenecks
```

#### Security Analysis

```bash
# Analyze security events
python scripts/websocket_monitoring.py --security-analysis

# Check authentication patterns
python scripts/test_websocket_connectivity.py --auth-analysis

# Monitor rate limiting
python scripts/websocket_monitoring.py --rate-limit-monitoring
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

#### Continuous Health Monitoring

```bash
# Start continuous monitoring
python scripts/websocket_monitoring.py --daemon --continuous

# Monitor specific metrics
python scripts/websocket_monitoring.py --monitor-latency
python scripts/websocket_monitoring.py --monitor-throughput
python scripts/websocket_monitoring.py --monitor-connections
```

#### Automated Testing

```bash
# Run automated WebSocket tests
python scripts/test_websocket_connectivity.py --automated

# Schedule regular tests
crontab -e
# Add: */15 * * * * python scripts/test_websocket_connectivity.py --automated
```

### Configuration Management

#### Configuration Validation

```bash
# Validate cloudflared configuration
cloudflared tunnel run --config ~/.cloudflared/config.yml --dry-run

# Validate Observatory configuration
python src/beast_mode/observatory/server.py --validate-config
```

#### Change Management

```bash
# Track configuration changes
git add ~/.cloudflared/config.yml
git commit -m "Update WebSocket configuration"

# Document changes
echo "$(date): WebSocket configuration updated" >> logs/config_changes.log
```

### Capacity Planning

#### Resource Monitoring

```bash
# Monitor resource usage
python scripts/monitor_workers.sh --resource-monitoring

# Check connection limits
python scripts/monitor_workers.sh --connection-limits

# Monitor performance trends
python scripts/monitor_workers.sh --performance-trends
```

#### Scalability Planning

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

#### Critical Issues

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

*This troubleshooting guide is maintained as part of the Observatory WebSocket infrastructure and should be updated whenever troubleshooting procedures change.*

**Last Updated**: 2025-01-27  
**Next Review**: 2025-02-27  
**Version**: 1.0