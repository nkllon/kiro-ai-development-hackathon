# Monitoring Daemon Deployment Summary

## What Was Fixed

The warning `"Monitoring daemon not running on port 8000, falling back to legacy mode"` occurred because:
1. The monitoring daemon is a standalone service that should run centrally
2. It was not running anywhere (not on localhost, not on vonnegut, not in Docker)
3. Applications were trying to connect to it and falling back to legacy monitoring

## Solution

Created a Docker deployment for the monitoring daemon to run on **vonnegut** (central metrics server).

## Architecture

```
┌─────────────────────────────────────────┐
│           Vonnegut Server               │
│                                         │
│  ┌─────────────────────────────────┐   │
│  │  Monitoring Daemon              │   │
│  │  Port: 8000                     │   │
│  │  Endpoint: /metrics             │   │
│  └─────────────────────────────────┘   │
│              ▲                          │
│              │ Collects metrics         │
│              │                          │
│  ┌─────────────────────────────────┐   │
│  │  Central Prometheus             │   │
│  │  Port: 9090                     │   │
│  │  Scrapes: localhost:8000        │   │
│  └─────────────────────────────────┘   │
└─────────────────────────────────────────┘
                ▲
                │
                │ Send metrics
                │
┌───────────────┴─────────────────────────┐
│     Beast Mode Applications              │
│     (Local, Docker, Observatory, etc)    │
│                                          │
│     Config: MONITORING_DAEMON_HOST=      │
│             vonnegut                     │
└──────────────────────────────────────────┘
```

## Deployment Steps

### 1. Deploy to Vonnegut

```bash
cd /Users/lou/kiro-2/kiro-ai-development-hackathon
./deployment/monitoring-daemon/deploy-to-vonnegut.sh
```

This will:
- Build the Docker image
- Start the monitoring daemon container on vonnegut:8000
- Make metrics available at http://vonnegut:8000/metrics

### 2. Configure Applications

Applications now default to looking for the daemon on **vonnegut** instead of localhost.

To override (e.g., for local development):
```bash
export MONITORING_DAEMON_HOST=localhost  # or any other host
```

To explicitly disable daemon mode:
```bash
export BEAST_MODE_DISABLE_DAEMON=1
```

### 3. Configure Central Prometheus

Add to `/etc/prometheus/prometheus.yml` on vonnegut:

```yaml
scrape_configs:
  - job_name: 'beast-mode-daemon'
    static_configs:
      - targets: ['localhost:8000']
        labels:
          service: 'beast-mode-monitoring'
          environment: 'production'
```

Reload Prometheus:
```bash
curl -X POST http://localhost:9090/-/reload
```

## Files Created

1. `deployment/monitoring-daemon/Dockerfile` - Container image for daemon
2. `deployment/monitoring-daemon/docker-compose.yml` - Docker Compose config
3. `deployment/monitoring-daemon/deploy-to-vonnegut.sh` - Deployment script
4. `deployment/monitoring-daemon/README.md` - Usage documentation

## Files Modified

1. `src/beast_mode/monitoring/prometheus_exporter.py` - Updated to use vonnegut as default host

## Verification

After deployment, verify:

```bash
# Check daemon is running
ssh vonnegut 'docker ps | grep monitoring-daemon'

# Check metrics endpoint
curl http://vonnegut:8000/metrics

# Check logs
ssh vonnegut 'cd /opt/beast-mode/monitoring-daemon/monitoring-daemon && docker-compose logs -f'
```

## Next Steps

1. Deploy to vonnegut: `./deployment/monitoring-daemon/deploy-to-vonnegut.sh`
2. Update Prometheus config to scrape the daemon
3. Restart any applications to pick up the new daemon connection
4. Stop the temporary local daemon: `ps aux | grep monitoring.daemon` and kill the process

## Environment Variables

- `MONITORING_DAEMON_HOST` - Daemon hostname (default: vonnegut)
- `MONITORING_DAEMON_PORT` - Daemon port (default: 8000)
- `BEAST_MODE_DISABLE_DAEMON` - Set to "1" to disable daemon mode entirely
