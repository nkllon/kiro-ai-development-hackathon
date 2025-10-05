# Beast Mode Monitoring Daemon

Standalone Prometheus monitoring daemon that provides centralized metrics collection for Beast Mode applications.

## Overview

The monitoring daemon:
- Runs on port 8000
- Exposes `/metrics` endpoint for Prometheus scraping
- Accepts metric registration and updates from Beast Mode applications
- Forwards metrics to central Prometheus (optional)

## Deployment on Vonnegut

### Build and Deploy

```bash
# From the monitoring-daemon directory
cd deployment/monitoring-daemon

# Build the image
docker-compose build

# Start the daemon
docker-compose up -d

# Check status
docker-compose ps
docker-compose logs -f monitoring-daemon
```

### Access Metrics

Once running, metrics are available at:
```
http://vonnegut:8000/metrics
```

### Configure Applications

Applications need to point to the daemon host. Set environment variable:
```bash
export MONITORING_DAEMON_HOST=vonnegut
export MONITORING_DAEMON_PORT=8000
```

Or update client configuration in code:
```python
from src.beast_mode.monitoring.client import MonitoringClient

client = MonitoringClient(
    client_id="my_app",
    daemon_host="vonnegut",  # Point to vonnegut instead of localhost
    daemon_port=8000
)
```

### Stop/Restart

```bash
# Stop
docker-compose down

# Restart
docker-compose restart

# View logs
docker-compose logs -f
```

## Integration with Central Prometheus

To have vonnegut's central Prometheus scrape this daemon, add to `/etc/prometheus/prometheus.yml`:

```yaml
scrape_configs:
  - job_name: 'beast-mode-daemon'
    static_configs:
      - targets: ['localhost:8000']
        labels:
          service: 'beast-mode-monitoring'
```

Then reload Prometheus:
```bash
curl -X POST http://localhost:9090/-/reload
```
