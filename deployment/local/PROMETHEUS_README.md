# Prometheus Monitoring Setup for Kiro AI Development Hackathon

This directory contains a complete Prometheus monitoring setup for the Kiro AI Development Hackathon project, designed to monitor the systematic PDCA orchestrator and related services.

## 🚀 Quick Start

### Prerequisites

- Docker and Docker Compose installed
- `jq` command-line JSON processor (for testing)
- `curl` for API testing

### Start Prometheus

```bash
# Navigate to the deployment directory
cd deployment/local

# Start Prometheus with monitoring profile
./prometheus-manager.sh start

# Or use Docker Compose directly
docker-compose --profile monitoring up -d prometheus
```

### Access Prometheus

- **Prometheus UI**: http://localhost:9090
- **Grafana UI**: http://localhost:3000 (admin/systematic)

## 📁 File Structure

```
deployment/local/
├── docker-compose.yml          # Docker Compose configuration
├── prometheus.yml              # Prometheus configuration
├── alert_rules.yml             # Alert rules definition
├── prometheus-manager.sh       # Management script
├── test-prometheus.sh          # Test script
└── PROMETHEUS_README.md        # This documentation
```

## 🔧 Configuration

### Prometheus Configuration (`prometheus.yml`)

The Prometheus configuration includes:

- **Global settings**: 15-second scrape and evaluation intervals
- **Scrape targets**:
  - Prometheus self-monitoring
  - Systematic PDCA Orchestrator (port 8080)
  - Node exporter (if available)
  - Redis monitoring (if available)
- **Alert rules**: Comprehensive alerting for system health
- **Storage**: 30-day retention with 1GB size limit

### Alert Rules (`alert_rules.yml`)

Pre-configured alerts for:

- **High error rate**: >10% 5xx errors
- **Service down**: Service unavailable for >1 minute
- **High memory usage**: >500MB memory consumption
- **High CPU usage**: >80% CPU utilization
- **Slow response time**: 95th percentile >1 second
- **Infrastructure alerts**: Disk usage, container restarts

## 🛠️ Management Script

The `prometheus-manager.sh` script provides comprehensive management:

### Available Commands

```bash
# Start Prometheus
./prometheus-manager.sh start

# Stop Prometheus
./prometheus-manager.sh stop

# Restart Prometheus
./prometheus-manager.sh restart

# Check status
./prometheus-manager.sh status

# View logs
./prometheus-manager.sh logs

# Reload configuration
./prometheus-manager.sh reload

# Backup data
./prometheus-manager.sh backup

# Clean up old data
./prometheus-manager.sh cleanup

# Validate configuration
./prometheus-manager.sh validate
```

### Features

- **Automatic health checks**: Verifies Prometheus is ready
- **Configuration validation**: Validates YAML files
- **Logging**: Comprehensive logging to `logs/prometheus.log`
- **Backup**: Creates timestamped backups
- **Cleanup**: Removes old logs and Docker images
- **Error handling**: Robust error handling and reporting

## 🧪 Testing

The `test-prometheus.sh` script provides comprehensive testing:

### Run All Tests

```bash
./test-prometheus.sh
```

### Test Categories

1. **Connectivity Tests**
   - Prometheus reachability
   - Health check endpoints
   - Status page accessibility

2. **API Tests**
   - Query API functionality
   - Targets API
   - Configuration API
   - Rules API

3. **Monitoring Tests**
   - Target status verification
   - Metrics collection
   - Self-monitoring

4. **Performance Tests**
   - Query response times
   - API performance

5. **Web UI Tests**
   - All web interface pages
   - Graph functionality
   - Alerts page

### Test Output

The script provides:
- Real-time test progress
- Detailed pass/fail results
- Performance metrics
- Comprehensive test report
- Logging to `logs/prometheus-test.log`

## 📊 Monitoring Targets

### Primary Targets

1. **Systematic PDCA Orchestrator** (`systematic-pdca-orchestrator:8080`)
   - Application metrics
   - Health status
   - Performance metrics

2. **Prometheus Self-Monitoring** (`localhost:9090`)
   - Prometheus internal metrics
   - Storage metrics
   - Query performance

### Optional Targets

3. **Node Exporter** (`node-exporter:9100`)
   - System metrics (CPU, memory, disk)
   - Network statistics
   - File system metrics

4. **Redis** (`redis:6379`)
   - Redis performance metrics
   - Memory usage
   - Connection statistics

## 🔍 Key Metrics

### Application Metrics

- `http_requests_total`: Total HTTP requests
- `http_request_duration_seconds`: Request duration histogram
- `process_resident_memory_bytes`: Memory usage
- `process_cpu_seconds_total`: CPU usage

### System Metrics

- `up`: Target availability (1 = up, 0 = down)
- `node_memory_MemAvailable_bytes`: Available memory
- `node_cpu_seconds_total`: CPU time
- `node_filesystem_free_bytes`: Free disk space

### Custom Metrics

- `kiro_ai_pdca_cycles_total`: PDCA cycle completions
- `kiro_ai_agent_interactions_total`: Agent interactions
- `kiro_ai_system_health_score`: Overall system health

## 🚨 Alerting

### Alert Severity Levels

- **Critical**: Service down, system failures
- **Warning**: High resource usage, performance issues

### Alert Channels

Currently configured for:
- Console logging
- Prometheus UI alerts page
- Grafana notifications (if configured)

### Customizing Alerts

Edit `alert_rules.yml` to:
- Modify threshold values
- Add new alert conditions
- Change severity levels
- Add custom annotations

## 📈 Grafana Integration

### Pre-configured Dashboards

1. **System Overview**: High-level system health
2. **Application Metrics**: PDCA orchestrator performance
3. **Infrastructure**: System resource utilization
4. **Alerts**: Active alerts and notifications

### Accessing Grafana

1. Navigate to http://localhost:3000
2. Login with admin/systematic
3. Import pre-configured dashboards
4. Customize as needed

## 🔧 Troubleshooting

### Common Issues

1. **Prometheus won't start**
   ```bash
   # Check Docker status
   docker ps
   
   # Check logs
   ./prometheus-manager.sh logs
   
   # Validate configuration
   ./prometheus-manager.sh validate
   ```

2. **Targets not showing up**
   ```bash
   # Check target status
   curl http://localhost:9090/api/v1/targets | jq
   
   # Verify network connectivity
   docker network ls
   ```

3. **High memory usage**
   ```bash
   # Check Prometheus memory
   docker stats prometheus
   
   # Adjust retention settings in prometheus.yml
   ```

4. **Slow queries**
   ```bash
   # Check query performance
   ./test-prometheus.sh
   
   # Review query patterns
   curl http://localhost:9090/api/v1/query?query=up
   ```

### Log Locations

- **Prometheus logs**: `logs/prometheus.log`
- **Test logs**: `logs/prometheus-test.log`
- **Docker logs**: `docker logs prometheus`

### Performance Tuning

1. **Adjust scrape intervals** in `prometheus.yml`
2. **Modify retention settings** for storage optimization
3. **Configure resource limits** in `docker-compose.yml`
4. **Optimize query patterns** for better performance

## 🔒 Security Considerations

### Current Security Measures

- **Network isolation**: Services run in isolated Docker network
- **Read-only volumes**: Configuration files mounted read-only
- **Resource limits**: Memory and CPU limits configured
- **Log rotation**: Automatic log file rotation

### Additional Security (Optional)

- **Authentication**: Enable basic auth in Prometheus
- **TLS**: Configure HTTPS for web interface
- **Firewall**: Restrict access to monitoring ports
- **Secrets management**: Use Docker secrets for sensitive data

## 📚 Additional Resources

### Documentation

- [Prometheus Documentation](https://prometheus.io/docs/)
- [Docker Compose Reference](https://docs.docker.com/compose/)
- [Grafana Documentation](https://grafana.com/docs/)

### Useful Commands

```bash
# View Prometheus configuration
curl http://localhost:9090/api/v1/status/config | jq

# List all metrics
curl http://localhost:9090/api/v1/label/__name__/values | jq

# Query specific metric
curl "http://localhost:9090/api/v1/query?query=up" | jq

# Check alert rules
curl http://localhost:9090/api/v1/rules | jq
```

### Monitoring Best Practices

1. **Regular testing**: Run tests frequently
2. **Alert tuning**: Adjust thresholds based on actual usage
3. **Dashboard maintenance**: Keep dashboards up to date
4. **Log monitoring**: Monitor logs for errors and warnings
5. **Performance monitoring**: Track query performance and resource usage

## 🤝 Contributing

To contribute to this monitoring setup:

1. **Test changes**: Always run `./test-prometheus.sh` after modifications
2. **Update documentation**: Keep this README current
3. **Follow conventions**: Use consistent naming and formatting
4. **Add tests**: Include tests for new functionality
5. **Document alerts**: Document any new alert rules

## 📝 License

This monitoring setup is part of the Kiro AI Development Hackathon project and follows the same licensing terms.

---

**Happy Monitoring! 🚀**

For questions or issues, please check the logs first and then refer to the troubleshooting section above.
