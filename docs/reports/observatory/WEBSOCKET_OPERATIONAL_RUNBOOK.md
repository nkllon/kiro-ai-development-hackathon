# WebSocket Operational Runbook
## Observatory WebSocket Infrastructure Operations

**Target**: observatory.nkllon.com WebSocket infrastructure  
**Purpose**: Daily operational procedures and management  
**Version**: 1.0  
**Last Updated**: 2025-01-27  

---

## 📋 Table of Contents

1. [Daily Operations](#daily-operations)
2. [Weekly Operations](#weekly-operations)
3. [Monthly Operations](#monthly-operations)
4. [Emergency Procedures](#emergency-procedures)
5. [Performance Monitoring](#performance-monitoring)
6. [Health Validation](#health-validation)
7. [Configuration Management](#configuration-management)
8. [Incident Response](#incident-response)

---

## 🌅 Daily Operations

### Morning Health Check (5 minutes)

#### Step 1: System Status Check

```bash
# Check Observatory server status
curl -I http://localhost:8888/health
# Expected: HTTP/2 200 OK

# Check WebSocket endpoints
curl -I -H "Upgrade: websocket" -H "Connection: Upgrade" \
  https://observatory.nkllon.com/ws/observatory
# Expected: HTTP/1.1 101 Switching Protocols

# Check tunnel status
cloudflared tunnel list
# Expected: ACTIVE status
```

#### Step 2: Quick Performance Check

```bash
# Run quick health check
python scripts/websocket_monitoring.py --quick-check

# Check connection latency
python scripts/websocket_monitoring.py --test-latency
# Target: <100ms

# Check active connections
netstat -an | grep :8888 | wc -l
# Target: >5 active connections
```

#### Step 3: Log Review

```bash
# Check Observatory server logs
tail -20 logs/observatory.log | grep -E "(ERROR|WARN|WebSocket)"

# Check tunnel logs
tail -20 logs/cloudflared.log | grep -E "(ERROR|WARN|WebSocket)"

# Check monitoring logs
tail -20 logs/websocket_monitoring.log | grep -E "(ERROR|WARN|ALERT)"
```

### Midday Monitoring (10 minutes)

#### Performance Metrics Review

```bash
# Check performance metrics
python scripts/websocket_monitoring.py --status

# Review health history
python scripts/websocket_monitoring.py --history --hours 6

# Check resource usage
python scripts/monitor_workers.sh --resource-check
```

#### Connection Analysis

```bash
# Analyze connection patterns
python scripts/websocket_monitoring.py --connection-analysis

# Check message throughput
python scripts/websocket_monitoring.py --throughput-check
# Target: >100 msg/sec

# Monitor error rates
python scripts/websocket_monitoring.py --error-rate-check
# Target: <1%
```

### Evening Health Check (5 minutes)

#### End-of-Day Validation

```bash
# Comprehensive health check
python scripts/websocket_monitoring.py --full-check

# Performance benchmark
python scripts/websocket_monitoring.py --benchmark

# Check daily metrics
python scripts/websocket_monitoring.py --daily-summary
```

#### Log Analysis

```bash
# Analyze daily logs
python scripts/websocket_monitoring.py --log-analysis --hours 24

# Check for anomalies
python scripts/websocket_monitoring.py --anomaly-detection

# Review alert history
python scripts/websocket_monitoring.py --alert-history --hours 24
```

---

## 📅 Weekly Operations

### Monday: Configuration Validation

#### Configuration Health Check

```bash
# Validate cloudflared configuration
cloudflared tunnel run --config ~/.cloudflared/config.yml --dry-run

# Validate Observatory configuration
python src/beast_mode/observatory/server.py --validate-config

# Check configuration drift
python scripts/validate_deployment.py
```

#### Security Configuration Review

```bash
# Check SSL/TLS configuration
python scripts/verify_ssl_tls.py

# Validate authentication settings
python scripts/test_websocket_connectivity.py --auth-check

# Review rate limiting configuration
python scripts/websocket_monitoring.py --rate-limit-check
```

### Tuesday: Performance Analysis

#### Performance Metrics Analysis

```bash
# Analyze weekly performance trends
python scripts/websocket_monitoring.py --weekly-analysis

# Check resource usage trends
python scripts/monitor_workers.sh --resource-trends --days 7

# Analyze connection patterns
python scripts/websocket_monitoring.py --connection-trends --days 7
```

#### Capacity Planning

```bash
# Analyze current capacity
python scripts/monitor_workers.sh --capacity-analysis

# Check connection limits
python scripts/monitor_workers.sh --connection-limits

# Plan for growth
python scripts/monitor_workers.sh --scalability-planning
```

### Wednesday: Monitoring Review

#### Monitoring System Health

```bash
# Check monitoring system status
python scripts/websocket_monitoring.py --monitoring-status

# Validate alerting configuration
python scripts/websocket_monitoring.py --alert-config-check

# Test monitoring endpoints
python scripts/websocket_monitoring.py --test-monitoring
```

#### Dashboard Review

```bash
# Check dashboard functionality
python scripts/websocket_monitoring.py --dashboard-check

# Validate metrics collection
python scripts/websocket_monitoring.py --metrics-validation

# Review alert history
python scripts/websocket_monitoring.py --alert-review --days 7
```

### Thursday: Security Review

#### Security Monitoring

```bash
# Review security logs
python scripts/websocket_monitoring.py --security-review

# Check authentication patterns
python scripts/test_websocket_connectivity.py --auth-patterns

# Monitor rate limiting effectiveness
python scripts/websocket_monitoring.py --rate-limit-effectiveness
```

#### Security Validation

```bash
# Test TLS configuration
openssl s_client -connect observatory.nkllon.com:443 -servername observatory.nkllon.com

# Test authentication mechanisms
python scripts/test_websocket_connectivity.py --auth-test

# Test rate limiting
python scripts/test_websocket_connectivity.py --rate-limit-test
```

### Friday: Maintenance Preparation

#### Maintenance Planning

```bash
# Check maintenance requirements
python scripts/monitor_workers.sh --maintenance-check

# Review system health
python scripts/websocket_monitoring.py --system-health

# Plan maintenance activities
python scripts/monitor_workers.sh --maintenance-planning
```

#### Backup Validation

```bash
# Validate backup systems
python scripts/validate_backups.py

# Check backup integrity
python scripts/websocket_monitoring.py --backup-validation

# Test restore procedures
python scripts/test_restore_procedures.py
```

---

## 📆 Monthly Operations

### First Week: Comprehensive Analysis

#### Performance Analysis

```bash
# Monthly performance report
python scripts/websocket_monitoring.py --monthly-report

# Analyze performance trends
python scripts/websocket_monitoring.py --trend-analysis --days 30

# Check capacity utilization
python scripts/monitor_workers.sh --capacity-utilization --days 30
```

#### Security Analysis

```bash
# Monthly security review
python scripts/websocket_monitoring.py --security-monthly-review

# Analyze security incidents
python scripts/websocket_monitoring.py --security-incident-analysis --days 30

# Review authentication patterns
python scripts/test_websocket_connectivity.py --auth-monthly-review
```

### Second Week: Configuration Review

#### Configuration Audit

```bash
# Configuration audit
python scripts/validate_deployment.py --comprehensive

# Check configuration compliance
python scripts/websocket_monitoring.py --config-compliance

# Review configuration changes
python scripts/websocket_monitoring.py --config-change-review --days 30
```

#### Documentation Review

```bash
# Validate documentation accuracy
python scripts/validate_documentation.py

# Check documentation completeness
python scripts/check_documentation_completeness.py

# Test documentation procedures
python scripts/test_documentation_procedures.py
```

### Third Week: Optimization Review

#### Performance Optimization

```bash
# Performance optimization analysis
python scripts/websocket_monitoring.py --optimization-analysis

# Resource optimization review
python scripts/monitor_workers.sh --optimization-review

# Connection optimization
python scripts/websocket_monitoring.py --connection-optimization
```

#### Scalability Planning

```bash
# Scalability analysis
python scripts/monitor_workers.sh --scalability-analysis

# Growth planning
python scripts/monitor_workers.sh --growth-planning

# Capacity planning
python scripts/monitor_workers.sh --capacity-planning
```

### Fourth Week: Maintenance Execution

#### Preventive Maintenance

```bash
# System maintenance
python scripts/monitor_workers.sh --preventive-maintenance

# Configuration updates
python scripts/update_configurations.py

# Security updates
python scripts/security_updates.py
```

#### Performance Tuning

```bash
# Performance tuning
python scripts/websocket_monitoring.py --performance-tuning

# Resource optimization
python scripts/monitor_workers.sh --resource-optimization

# Connection optimization
python scripts/websocket_monitoring.py --connection-tuning
```

---

## 🚨 Emergency Procedures

### Critical Issue Response (Service Down)

#### Immediate Assessment (2 minutes)

```bash
# Quick health check
curl -I https://observatory.nkllon.com/health

# Check WebSocket status
curl -I -H "Upgrade: websocket" -H "Connection: Upgrade" \
  https://observatory.nkllon.com/ws/observatory

# Check tunnel status
cloudflared tunnel list
```

#### Issue Identification (3 minutes)

| Response | Issue Type | Action |
|----------|------------|--------|
| HTTP/2 404 | WebSocket config missing | Apply WebSocket configuration |
| HTTP/2 503 | Service unavailable | Check Observatory server |
| HTTP/2 403 | Bot protection | Check rate limiting |
| Timeout | Network issue | Check connectivity |

#### Emergency Fix Application

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

### High Priority Issue Response (Performance Degraded)

#### Performance Assessment

```bash
# Check performance metrics
python scripts/websocket_monitoring.py --performance-check

# Analyze connection patterns
python scripts/websocket_monitoring.py --connection-analysis

# Check resource usage
python scripts/monitor_workers.sh --resource-check
```

#### Performance Optimization

```bash
# Optimize connection settings
python scripts/websocket_monitoring.py --connection-optimization

# Adjust resource limits
python scripts/monitor_workers.sh --resource-adjustment

# Implement performance tuning
python scripts/websocket_monitoring.py --performance-tuning
```

---

## 📊 Performance Monitoring

### Real-Time Monitoring

#### Continuous Monitoring

```bash
# Start continuous monitoring
python scripts/websocket_monitoring.py --daemon --continuous

# Monitor specific metrics
python scripts/websocket_monitoring.py --monitor-latency
python scripts/websocket_monitoring.py --monitor-throughput
python scripts/websocket_monitoring.py --monitor-connections
```

#### Performance Metrics

| Metric | Target | Warning | Critical |
|--------|--------|---------|----------|
| Connection Latency | <100ms | >500ms | >1000ms |
| Message Throughput | >100 msg/sec | <50 msg/sec | <10 msg/sec |
| Connection Success Rate | >99% | <95% | <90% |
| Concurrent Connections | >10 | <5 | <2 |
| Memory Usage | <50MB | >100MB | >200MB |
| CPU Usage | <10% | >20% | >40% |

### Performance Analysis

#### Trend Analysis

```bash
# Analyze performance trends
python scripts/websocket_monitoring.py --trend-analysis --days 7

# Check capacity trends
python scripts/monitor_workers.sh --capacity-trends --days 7

# Analyze connection trends
python scripts/websocket_monitoring.py --connection-trends --days 7
```

#### Performance Optimization

```bash
# Performance optimization analysis
python scripts/websocket_monitoring.py --optimization-analysis

# Resource optimization
python scripts/monitor_workers.sh --resource-optimization

# Connection optimization
python scripts/websocket_monitoring.py --connection-optimization
```

---

## 🔍 Health Validation

### Automated Health Checks

#### Continuous Health Monitoring

```bash
# Start continuous health monitoring
python scripts/websocket_monitoring.py --daemon --health-monitoring

# Health check validation
python scripts/websocket_monitoring.py --health-validation

# Health trend analysis
python scripts/websocket_monitoring.py --health-trends --days 7
```

#### Health Metrics

| Health Metric | Target | Warning | Critical |
|---------------|--------|---------|----------|
| Endpoint Health | 100% | <95% | <90% |
| Connection Health | 100% | <95% | <90% |
| Service Health | 100% | <95% | <90% |
| Tunnel Health | 100% | <95% | <90% |

### Manual Health Checks

#### Comprehensive Health Check

```bash
# Comprehensive health check
python scripts/websocket_monitoring.py --comprehensive-health-check

# Health check validation
python scripts/websocket_monitoring.py --health-validation

# Health report generation
python scripts/websocket_monitoring.py --health-report
```

#### Health Troubleshooting

```bash
# Health troubleshooting
python scripts/websocket_monitoring.py --health-troubleshooting

# Health issue diagnosis
python scripts/websocket_monitoring.py --health-diagnosis

# Health issue resolution
python scripts/websocket_monitoring.py --health-resolution
```

---

## ⚙️ Configuration Management

### Configuration Validation

#### Daily Configuration Check

```bash
# Validate cloudflared configuration
cloudflared tunnel run --config ~/.cloudflared/config.yml --dry-run

# Validate Observatory configuration
python src/beast_mode/observatory/server.py --validate-config

# Check configuration integrity
python scripts/validate_deployment.py
```

#### Configuration Monitoring

```bash
# Monitor configuration changes
python scripts/websocket_monitoring.py --config-monitoring

# Check configuration drift
python scripts/websocket_monitoring.py --config-drift-check

# Validate configuration compliance
python scripts/websocket_monitoring.py --config-compliance
```

### Configuration Updates

#### Configuration Update Procedure

```bash
# Backup current configuration
cp ~/.cloudflared/config.yml ~/.cloudflared/config.yml.backup.$(date +%Y%m%d_%H%M%S)

# Apply new configuration
cp new-config.yml ~/.cloudflared/config.yml

# Validate configuration
cloudflared tunnel run --config ~/.cloudflared/config.yml --dry-run

# Apply configuration
pkill -f cloudflared && sleep 2 && cloudflared tunnel run

# Verify configuration
python scripts/test_websocket_connectivity.py
```

#### Configuration Rollback

```bash
# Rollback configuration
cp ~/.cloudflared/config.yml.backup ~/.cloudflared/config.yml

# Restart services
pkill -f cloudflared && sleep 2 && cloudflared tunnel run

# Verify rollback
python scripts/test_websocket_connectivity.py
```

---

## 🚨 Incident Response

### Incident Classification

| Severity | Description | Response Time | Escalation |
|----------|-------------|---------------|------------|
| Critical | Service completely down | 5 minutes | Level 4 |
| High | Performance severely degraded | 15 minutes | Level 3 |
| Medium | Minor performance issues | 1 hour | Level 2 |
| Low | Monitoring alerts | 4 hours | Level 1 |

### Incident Response Procedures

#### Critical Incident Response

```bash
# Immediate assessment
python scripts/websocket_monitoring.py --emergency-assessment

# Emergency diagnostics
python scripts/websocket_monitoring.py --emergency-diagnostics

# Emergency recovery
python scripts/websocket_monitoring.py --emergency-recovery
```

#### Incident Documentation

```bash
# Document incident
python scripts/websocket_monitoring.py --incident-documentation

# Generate incident report
python scripts/websocket_monitoring.py --incident-report

# Post-incident analysis
python scripts/websocket_monitoring.py --post-incident-analysis
```

### Post-Incident Procedures

#### Incident Review

```bash
# Incident review
python scripts/websocket_monitoring.py --incident-review

# Lessons learned
python scripts/websocket_monitoring.py --lessons-learned

# Process improvement
python scripts/websocket_monitoring.py --process-improvement
```

#### Documentation Updates

```bash
# Update procedures
python scripts/websocket_monitoring.py --update-procedures

# Update runbooks
python scripts/websocket_monitoring.py --update-runbooks

# Update monitoring
python scripts/websocket_monitoring.py --update-monitoring
```

---

## 📈 Operational Metrics

### Key Performance Indicators

| KPI | Target | Current | Trend |
|-----|--------|---------|-------|
| Service Availability | >99.9% | 99.95% | ↗️ |
| WebSocket Latency | <100ms | 45ms | ↘️ |
| Message Throughput | >100 msg/sec | 250 msg/sec | ↗️ |
| Connection Success Rate | >99% | 99.2% | ↗️ |
| Error Rate | <1% | 0.8% | ↘️ |

### Operational Efficiency

| Metric | Target | Current | Trend |
|--------|--------|---------|-------|
| Incident Response Time | <15 min | 12 min | ↘️ |
| Resolution Time | <60 min | 45 min | ↘️ |
| False Positive Rate | <5% | 3% | ↘️ |
| Documentation Accuracy | >95% | 98% | ↗️ |

---

## 📞 Support & Escalation

### Support Contacts

| Level | Role | Contact | Response Time |
|-------|------|---------|---------------|
| L1 | Operations Team | operations@observatory.com | 1 hour |
| L2 | Infrastructure Team | infrastructure@observatory.com | 30 minutes |
| L3 | Senior Engineer | senior@observatory.com | 15 minutes |
| L4 | On-call Engineer | oncall@observatory.com | 5 minutes |

### Escalation Procedures

#### Escalation Triggers

- **Critical**: Service completely down
- **High**: Performance severely degraded
- **Medium**: Minor performance issues
- **Low**: Monitoring alerts

#### Escalation Process

1. **Initial Assessment** (5 minutes)
2. **Issue Classification** (5 minutes)
3. **Escalation Decision** (5 minutes)
4. **Team Notification** (5 minutes)
5. **Resolution Tracking** (Continuous)

---

## 📋 Operational Checklist

### Daily Checklist

- [ ] **Morning Health Check**
  - [ ] System status check
  - [ ] Quick performance check
  - [ ] Log review

- [ ] **Midday Monitoring**
  - [ ] Performance metrics review
  - [ ] Connection analysis
  - [ ] Resource usage check

- [ ] **Evening Health Check**
  - [ ] End-of-day validation
  - [ ] Log analysis
  - [ ] Daily summary

### Weekly Checklist

- [ ] **Configuration Validation**
  - [ ] Configuration health check
  - [ ] Security configuration review
  - [ ] Configuration drift check

- [ ] **Performance Analysis**
  - [ ] Performance metrics analysis
  - [ ] Capacity planning
  - [ ] Resource usage trends

- [ ] **Monitoring Review**
  - [ ] Monitoring system health
  - [ ] Dashboard review
  - [ ] Alert configuration

### Monthly Checklist

- [ ] **Comprehensive Analysis**
  - [ ] Performance analysis
  - [ ] Security analysis
  - [ ] Capacity analysis

- [ ] **Configuration Review**
  - [ ] Configuration audit
  - [ ] Documentation review
  - [ ] Compliance check

- [ ] **Optimization Review**
  - [ ] Performance optimization
  - [ ] Scalability planning
  - [ ] Resource optimization

---

## 📚 Documentation Maintenance

### Documentation Updates

#### Update Schedule

| Document | Update Frequency | Last Update | Next Update |
|----------|------------------|-------------|-------------|
| Operational Runbook | Monthly | 2025-01-27 | 2025-02-27 |
| Procedures | Monthly | 2025-01-27 | 2025-02-27 |
| Checklists | Monthly | 2025-01-27 | 2025-02-27 |
| Contact Information | Quarterly | 2025-01-27 | 2025-04-27 |

#### Update Procedures

```bash
# Update operational runbook
git add WEBSOCKET_OPERATIONAL_RUNBOOK.md
git commit -m "Update WebSocket operational runbook"

# Update procedures
git add procedures/
git commit -m "Update operational procedures"

# Update checklists
git add checklists/
git commit -m "Update operational checklists"
```

---

*This runbook is maintained as part of the Observatory WebSocket infrastructure operations and should be updated whenever operational procedures change.*

**Last Updated**: 2025-01-27  
**Next Review**: 2025-02-27  
**Version**: 1.0