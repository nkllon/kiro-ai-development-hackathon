# Beast Mode Framework - Deployment Architecture Documentation

**Generated:** 2025-10-02
**Version:** 1.0.0
**Environment:** Local Development & Production-like Configuration

---

## Table of Contents

1. [Overview](#overview)
2. [Architecture Diagram](#architecture-diagram)
3. [Service Inventory](#service-inventory)
4. [Network Architecture](#network-architecture)
5. [Container Specifications](#container-specifications)
6. [Environment Configuration](#environment-configuration)
7. [Data Persistence](#data-persistence)
8. [Monitoring & Observability](#monitoring--observability)
9. [Security Configuration](#security-configuration)
10. [Health Checks & Restart Policies](#health-checks--restart-policies)
11. [Deployment Procedures](#deployment-procedures)
12. [Troubleshooting](#troubleshooting)

---

## Overview

The Beast Mode Framework deployment is a **microservices-based architecture** running on Docker containers. It provides:

- **Systematic PDCA (Plan-Do-Check-Act) orchestration** for AI-assisted development
- **Real-time monitoring and metrics** via Prometheus and Grafana
- **CMS capabilities** through Directus for content and data management
- **Reverse proxy and load balancing** via Nginx
- **Production-like local development environment**

### Key Architectural Principles

- **Container Isolation:** Each service runs in its own container
- **Service Discovery:** Docker DNS for inter-service communication
- **Systematic Monitoring:** Prometheus scraping + Grafana visualization
- **Health-First Design:** All services have health checks and auto-restart
- **Profile-Based Deployment:** Monitoring stack optional via `--profile monitoring`

---

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                         External Access                          │
│                  localhost:80 / localhost:443                    │
└────────────────────────────┬────────────────────────────────────┘
                             │
                    ┌────────▼────────┐
                    │     Nginx       │  Port 80/443
                    │ Reverse Proxy   │  (Entry Point)
                    └────────┬────────┘
                             │
         ┌───────────────────┼───────────────────┐
         │                   │                   │
    ┌────▼────┐      ┌──────▼──────┐    ┌──────▼──────┐
    │ PDCA    │      │  Directus   │    │  Grafana    │
    │ API     │      │  CMS        │    │  Dashboard  │
    │ :8080   │      │  :8055      │    │  :3000      │
    └────┬────┘      └──────┬──────┘    └──────┬──────┘
         │                  │                   │
         │           ┌──────▼──────┐            │
         │           │ Directus DB │            │
         │           │ PostgreSQL  │            │
         │           │  :5432      │            │
         │           └─────────────┘            │
         │                                      │
    ┌────▼────────┐                    ┌───────▼────────┐
    │  Beast Mode │                    │  Prometheus    │
    │  Metrics    │◄───────────────────┤  Scraper       │
    │  :8000      │    Scrapes         │  :9090         │
    └─────────────┘                    └────────────────┘
         │
         └─── Exports metrics for monitoring

┌──────────────────────────────────────────────────────────────────┐
│               Docker Network: systematic-pdca-local              │
│                     Bridge Network: 172.19.0.0/16                │
└──────────────────────────────────────────────────────────────────┘
```

---

## Service Inventory

### Core Services (Always Running)

| Service | Container Name | Port(s) | Purpose | Build Context |
|---------|---------------|---------|---------|---------------|
| **nginx** | local-nginx-1 | 80, 443 | Reverse proxy, load balancer, entry point | `deployment/local/nginx/` |
| **systematic-pdca-orchestrator** | local-systematic-pdca-orchestrator-1 | 8080 (internal) | Main FastAPI backend application | Root (`/`) |
| **directus** | local-directus-1 | 8055 | Headless CMS for data management | Official image |
| **directus-db** | local-directus-db-1 | 5432 (internal) | PostgreSQL database for Directus | Official postgres:15 |

### Monitoring Services (Profile: `monitoring`)

| Service | Container Name | Port(s) | Purpose | Build Context |
|---------|---------------|---------|---------|---------------|
| **beast-mode-metrics** | local-beast-mode-metrics-1 | 8000 (internal) | Prometheus metrics exporter | `deployment/beast-mode-metrics/` |
| **prometheus** | local-prometheus-1 | 9090 | Time-series metrics database | Official prom/prometheus |
| **grafana** | local-grafana-1 | 3000 | Metrics visualization dashboard | Official grafana/grafana |

---

## Network Architecture

### Docker Network Configuration

- **Network Name:** `local_systematic-pdca-local`
- **Driver:** bridge
- **Subnet:** 172.19.0.0/16
- **Gateway:** 172.19.0.1

### Current IP Allocations

```
172.19.0.2  - local-prometheus-1
172.19.0.3  - local-directus-db-1
172.19.0.4  - local-systematic-pdca-orchestrator-1
172.19.0.5  - local-directus-1
172.19.0.6  - local-beast-mode-metrics-1
```

### Service Communication

Services communicate via **Docker DNS** using container names:

- `nginx` → `systematic-pdca-orchestrator:8080`
- `nginx` → `local-grafana-1:3000`
- `nginx` → `host.docker.internal:8001` (Beast Mode metrics)
- `prometheus` → `beast-mode-metrics:8000`
- `prometheus` → `systematic-pdca-orchestrator:8080`
- `directus` → `directus-db:5432`

---

## Container Specifications

### 1. Nginx Reverse Proxy

**Image:** `nginx:1.25-alpine`
**Build:** Custom Dockerfile with curl and health check page

**Key Configuration:**
- Upstream backends defined for: PDCA API, Beast Mode metrics, Grafana
- Rate limiting: 10 req/s for API, 30 req/s for static
- Gzip compression enabled
- Security headers: X-Frame-Options, X-Content-Type-Options, X-XSS-Protection
- WebSocket support for Grafana

**Routes:**
- `/` → systematic-pdca-orchestrator (root endpoint)
- `/api/*` → systematic-pdca-orchestrator:8080
- `/health` → systematic-pdca-orchestrator:8080/health
- `/metrics` → beast-mode-metrics:8000/metrics
- `/grafana/*` → local-grafana-1:3000
- `/nginx-health` → Internal health check

**Health Check:**
```bash
curl -f http://localhost/nginx-health
# Interval: 30s, Timeout: 10s, Retries: 3
```

### 2. Systematic PDCA Orchestrator

**Image:** Custom Python 3.11-slim
**Build Context:** Root directory (`/`)
**Dockerfile:** `deployment/systematic-pdca/Dockerfile`

**Purpose:** Main FastAPI backend providing PDCA orchestration APIs

**Environment:**
- `ENVIRONMENT=development`
- `PYTHONPATH=/app`
- `LOG_LEVEL=DEBUG`
- `PORT=8080`

**Volumes:**
- `/app/src` → Read-only source code (hot reload)
- `/app/project_model_registry.json` → Registry file
- `/app/learning_patterns` → Learning patterns directory

**Entry Point:**
```bash
uvicorn src.beast_mode.api.main:app --host 0.0.0.0 --port 8080
```

**Health Check:**
```python
python -c "from src.beast_mode.core.model_registry import ModelRegistry; r = ModelRegistry(); print('Health:', r.get_health_status()['status'])"
# Interval: 30s, Timeout: 10s, Retries: 3
```

**API Endpoints:**
- `GET /` - HTML status page
- `GET /health` - Health check JSON
- `GET /api/status` - API status information
- `GET /api/metrics` - Application metrics (JSON)
- `GET /metrics` - Prometheus metrics (text)
- `GET /docs` - Swagger UI
- `GET /redoc` - ReDoc documentation

### 3. Beast Mode Metrics Exporter

**Image:** Custom Python 3.11-slim
**Build Context:** Root directory (`/`)
**Dockerfile:** `deployment/beast-mode-metrics/Dockerfile`

**Purpose:** Export Beast Mode framework metrics in Prometheus format

**Environment:**
- `PYTHONPATH=/app`
- `PROMETHEUS_PORT=8000`
- `BEAST_MODE_PROMETHEUS_ENABLED=true`

**Entry Point:**
```bash
python start_metrics.py
```

**Metrics Exposed:**
- System metrics: CPU, memory, disk, load average
- Application metrics: operations, duration, throughput, error rate
- Module metrics: health score, errors, warnings, uptime
- Cache metrics: hit rate, operations, size
- Health metrics: component status, health scores, alerts

**Health Check:**
```bash
curl -f http://localhost:8000/metrics
# Interval: 30s, Timeout: 10s, Retries: 3
```

### 4. Prometheus Server

**Image:** `prom/prometheus:latest`

**Purpose:** Time-series metrics database with scraping and alerting

**Configuration Files:**
- `/etc/prometheus/prometheus.yml` - Main configuration
- `/etc/prometheus/alert_rules.yml` - Alert rules

**Command-line Args:**
```bash
--config.file=/etc/prometheus/prometheus.yml
--storage.tsdb.path=/prometheus
--storage.tsdb.retention.time=30d
--storage.tsdb.retention.size=1GB
--storage.tsdb.wal-compression
--web.enable-lifecycle
--web.enable-admin-api
--log.level=info
--log.format=json
```

**Scrape Configuration:**
- `prometheus` (self): every 5s
- `beast-mode-metrics`: every 10s
- `systematic-pdca-app`: every 15s

**Alert Rules:**
- High error rate (>0.1/s for 2m)
- Service down (>1m)
- High memory usage (>500MB for 5m)
- High CPU usage (>0.8 cores for 5m)
- Slow response time (>1s p95 for 5m)

**Health Check:**
```bash
wget --no-verbose --tries=1 --spider http://localhost:9090/-/ready
# Interval: 30s, Timeout: 10s, Retries: 3
```

### 5. Grafana Dashboard

**Image:** `grafana/grafana:latest`

**Purpose:** Metrics visualization and dashboard platform

**Environment:**
- `GF_SECURITY_ADMIN_PASSWORD` - From `~/.env` (BeastMode2025!)

**Health Check:**
None configured (should be added)

**Access:**
- URL: http://localhost:3000
- Default username: `admin`
- Password: From `~/.env` → `GF_SECURITY_ADMIN_PASSWORD`

### 6. Directus CMS

**Image:** `directus/directus:latest`

**Purpose:** Headless CMS for content and data management

**Environment:**
- `KEY=255d861b-5ea1-5996-9aa3-922530ec40b1`
- `SECRET=6116487b-cda1-52c2-b5b5-c8022c45e263`
- `DB_CLIENT=pg`
- `DB_HOST=directus-db`
- `DB_PORT=5432`
- `DB_DATABASE=directus`
- `DB_USER=directus`
- `DB_PASSWORD=directus`
- `ADMIN_EMAIL=admin@example.com`
- `ADMIN_PASSWORD=d1r3ctu5`
- `CACHE_ENABLED=false`
- `RATE_LIMITER_ENABLED=false`

**SMTP Configuration (Gmail):**
- `MAIL_FROM=lou@louspringer.com`
- `MAIL_TRANSPORT=smtp`
- `MAIL_HOST=smtp.gmail.com`
- `MAIL_PORT=587`
- `MAIL_USER=lou@louspringer.com`
- `MAIL_PASSWORD=xjvk evlz qzsg qtfh`

**Health Check:**
```bash
wget --no-verbose --tries=1 --spider http://localhost:8055/server/health
# Interval: 30s, Timeout: 10s, Retries: 3, Start period: 30s
```

### 7. Directus PostgreSQL Database

**Image:** `postgres:15`

**Purpose:** Database backend for Directus CMS

**Environment:**
- `POSTGRES_USER=directus`
- `POSTGRES_PASSWORD=directus`
- `POSTGRES_DB=directus`

**Health Check:**
```bash
pg_isready -U directus
# Interval: 30s, Timeout: 10s, Retries: 3
```

---

## Environment Configuration

### Environment Variable Hierarchy

1. **~/.env** (Home directory) - Primary configuration source
2. **sample.env** (Project root) - Template and defaults
3. **.env.directus** (Project root) - Directus-specific settings
4. **docker-compose.yml** - Inline environment variables

### Primary Configuration (~/.env)

```bash
# Redis Configuration
REDIS_PASSWORD=beastmode2025
BEAST_MODE_REDIS_PASSWORD=beastmode2025
REDIS_HOST=192.168.1.119
REDIS_PORT=6379

# Environment
DEVELOPMENT=true
BEAST_MODE_ENV=development

# Grafana
GF_SECURITY_ADMIN_PASSWORD=BeastMode2025!
```

### Sample Configuration (sample.env)

```bash
# Redis
REDIS_PASSWORD=your_redis_password_here
BEAST_MODE_REDIS_PASSWORD=your_redis_password_here
REDIS_HOST=192.168.1.119
REDIS_PORT=6379

# Environment
DEVELOPMENT=true

# Directus
DIRECTUS_ADMIN_PASSWORD=your_directus_password_here
DIRECTUS_URL=http://localhost:8055
DIRECTUS_ADMIN_EMAIL=admin@example.com

# Grafana
GF_SECURITY_ADMIN_PASSWORD=systematic

# Beast Mode
BEAST_MODE_ENV=development
```

### Directus Configuration (.env.directus)

```bash
# Database
DIRECTUS_DB_PASSWORD=beast_mode_directus_secure_2024

# Security (CHANGE IN PRODUCTION!)
DIRECTUS_KEY=beast-mode-directus-key-change-in-production-$(date +%s)
DIRECTUS_SECRET=beast-mode-directus-secret-change-in-production-$(date +%s)

# Admin User
DIRECTUS_ADMIN_EMAIL=admin@beast-mode.local
DIRECTUS_ADMIN_PASSWORD=beast_mode_admin_secure_2024

# API
DIRECTUS_PUBLIC_URL=http://localhost:8055

# Integration
BEAST_MODE_INTEGRATION=true
AI_MEMORY_PALACE_ENABLED=true
```

---

## Data Persistence

### Docker Volumes

| Volume Name | Purpose | Service(s) | Size/Retention |
|-------------|---------|------------|----------------|
| `local_grafana-storage` | Grafana dashboards, datasources, user data | grafana | Persistent |
| `local_prometheus-data` | Time-series metrics data | prometheus | 30d / 1GB max |
| `local_nginx-logs` | Nginx access and error logs | nginx | Persistent |
| `local_directus-uploads` | Directus file uploads | directus | Persistent |
| `local_directus-extensions` | Directus extensions | directus | Persistent |
| `local_directus-db-data` | PostgreSQL database files | directus-db | Persistent |

### Volume Locations

All volumes are stored in Docker's default location:
- **Linux:** `/var/lib/docker/volumes/`
- **macOS:** Docker Desktop VM (not directly accessible)

### Backup Strategy

**Critical volumes requiring backup:**
1. `local_directus-db-data` - Database
2. `local_directus-uploads` - User content
3. `local_grafana-storage` - Dashboards

**Backup command:**
```bash
# Backup Directus database
docker exec local-directus-db-1 pg_dump -U directus directus > backup_directus_$(date +%Y%m%d).sql

# Backup volume
docker run --rm -v local_grafana-storage:/data -v $(pwd):/backup alpine tar czf /backup/grafana_backup_$(date +%Y%m%d).tar.gz /data
```

---

## Monitoring & Observability

### Prometheus Metrics Collection

**Scrape Targets:**
1. **Prometheus Self-Monitoring** (localhost:9090)
   - Interval: 5s
   - Metrics: prometheus_*

2. **Beast Mode Metrics** (beast-mode-metrics:8000)
   - Interval: 10s
   - Timeout: 5s
   - Metrics: beast_mode_*

3. **PDCA Application** (systematic-pdca-orchestrator:8080)
   - Interval: 15s
   - Timeout: 10s
   - Metrics: systematic_pdca_*

### Key Metrics Exported

**System Metrics:**
- `beast_mode_system_cpu_percent{host}` - CPU usage
- `beast_mode_system_memory_percent{host}` - Memory usage
- `beast_mode_system_memory_used_bytes{host}` - Memory bytes
- `beast_mode_system_disk_usage_percent{host,mountpoint}` - Disk usage
- `beast_mode_system_load_average{host,period}` - Load (1m, 5m, 15m)

**Application Metrics:**
- `beast_mode_app_operations_total{operation_type,status}` - Operation counter
- `beast_mode_app_operation_duration_seconds{operation_type}` - Duration histogram
- `beast_mode_app_throughput_ops_per_second{operation_type}` - Throughput
- `beast_mode_app_error_rate{component}` - Error rate
- `beast_mode_app_cache_hit_rate{cache_name}` - Cache hit rate
- `beast_mode_app_active_operations{operation_type}` - Active operations
- `beast_mode_app_queue_size{queue_name}` - Queue depth

**Health Metrics:**
- `beast_mode_component_health_status{component_name,component_type}` - 1=healthy, 0=unhealthy
- `beast_mode_component_health_score{component_name,component_type}` - Score 0-100
- `beast_mode_alerts_total{alert_level,alert_type}` - Alert counter

### Alert Rules

**Critical Alerts:**
- `ServiceDown` - Service unreachable for >1min
- `PrometheusTargetDown` - Scrape target down >1min

**Warning Alerts:**
- `HighErrorRate` - Error rate >0.1/s for 2min
- `HighMemoryUsage` - Memory >500MB for 5min
- `HighCPUUsage` - CPU >0.8 cores for 5min
- `SlowResponseTime` - p95 latency >1s for 5min
- `HighDiskUsage` - Disk >80% for 5min
- `ContainerRestart` - Container restarted in last 5min

### Grafana Integration

**Datasource Configuration:**
- Type: Prometheus
- URL: http://prometheus:9090
- Access: Server (proxy)

**Recommended Dashboards:**
- System Overview (CPU, Memory, Disk, Load)
- Application Performance (Throughput, Latency, Errors)
- Health Status (Component health, alerts)
- Cache Performance (Hit rate, operations)

---

## Security Configuration

### Network Security

- **Internal Network:** All services isolated in `systematic-pdca-local` bridge network
- **Exposed Ports:** Only nginx (80, 443), prometheus (9090), grafana (3000), directus (8055)
- **Service-to-Service:** Communication via internal Docker DNS (no external exposure)

### Nginx Security Headers

```nginx
X-Frame-Options: SAMEORIGIN
X-Content-Type-Options: nosniff
X-XSS-Protection: 1; mode=block
Referrer-Policy: strict-origin-when-cross-origin
```

### Rate Limiting (Nginx)

```nginx
API endpoints: 10 req/s, burst 20
Static files: 30 req/s, burst 50
```

### Authentication

| Service | Type | Credentials |
|---------|------|-------------|
| Grafana | Username/Password | admin / BeastMode2025! (from ~/.env) |
| Directus | Username/Password | admin@example.com / d1r3ctu5 |
| Prometheus | None (should be configured) | No authentication |

**Security Recommendations:**
1. Enable Prometheus authentication for production
2. Change default Directus credentials
3. Use environment-specific secrets management
4. Enable HTTPS/TLS with proper certificates
5. Implement API authentication/authorization

### Container User Permissions

- **nginx:** Runs as nginx user
- **systematic-pdca-orchestrator:** Runs as pdca user (UID 1000)
- **beast-mode-metrics:** Runs as metrics user (UID 1000)
- **prometheus:** Runs as nobody/prometheus
- **grafana:** Runs as grafana user
- **directus:** Runs as node user
- **directus-db:** Runs as postgres user

---

## Health Checks & Restart Policies

### Health Check Summary

| Service | Health Check Command | Interval | Timeout | Retries | Start Period |
|---------|---------------------|----------|---------|---------|--------------|
| nginx | curl http://localhost/nginx-health | 30s | 10s | 3 | 10s |
| systematic-pdca-orchestrator | Python health check | 30s | 10s | 3 | 10s |
| beast-mode-metrics | curl http://localhost:8000/metrics | 30s | 10s | 3 | 15s |
| prometheus | wget http://localhost:9090/-/ready | 30s | 10s | 3 | 10s |
| grafana | None | - | - | - | - |
| directus | wget http://localhost:8055/server/health | 30s | 10s | 3 | 30s |
| directus-db | pg_isready -U directus | 30s | 10s | 3 | 10s |

### Restart Policies

**All services:** `restart: unless-stopped`

This means:
- Containers auto-restart on failure
- Containers restart after Docker daemon restart
- Containers do NOT restart if manually stopped

### Dependency Chain

```
nginx
  └─ depends_on: systematic-pdca-orchestrator

directus
  └─ depends_on: directus-db

prometheus
  └─ depends_on: beast-mode-metrics
```

**Note:** `depends_on` only controls start order, not health-based readiness.

---

## Deployment Procedures

### Initial Deployment

```bash
# 1. Clone repository
cd /Users/lou/kiro-2/kiro-ai-development-hackathon

# 2. Configure environment
cp sample.env ~/.env
# Edit ~/.env with your configuration

# 3. Start core services
docker-compose -f deployment/local/docker-compose.yml up -d

# 4. Start monitoring stack (optional)
docker-compose -f deployment/local/docker-compose.yml --profile monitoring up -d

# 5. Verify all services
docker ps
docker-compose -f deployment/local/docker-compose.yml ps

# 6. Check logs
docker-compose -f deployment/local/docker-compose.yml logs -f
```

### Service-Specific Operations

**Start single service:**
```bash
docker-compose -f /Users/lou/kiro-2/kiro-ai-development-hackathon/deployment/local/docker-compose.yml up -d <service-name>
```

**Restart service:**
```bash
docker-compose -f /Users/lou/kiro-2/kiro-ai-development-hackathon/deployment/local/docker-compose.yml restart <service-name>
```

**Rebuild and restart:**
```bash
docker-compose -f /Users/lou/kiro-2/kiro-ai-development-hackathon/deployment/local/docker-compose.yml up -d --build <service-name>
```

**Stop all services:**
```bash
docker-compose -f /Users/lou/kiro-2/kiro-ai-development-hackathon/deployment/local/docker-compose.yml down
```

**Stop and remove volumes:**
```bash
docker-compose -f /Users/lou/kiro-2/kiro-ai-development-hackathon/deployment/local/docker-compose.yml down -v
```

### Grafana Password Reset Procedure

When Grafana password changes:

```bash
# 1. Update ~/.env with new password
echo "GF_SECURITY_ADMIN_PASSWORD=NewPassword123!" >> ~/.env

# 2. Force recreate Grafana container
docker-compose -f /Users/lou/kiro-2/kiro-ai-development-hackathon/deployment/local/docker-compose.yml \
  --profile monitoring \
  --env-file ~/.env \
  up -d --force-recreate --no-deps grafana

# 3. Verify
docker logs local-grafana-1 --tail 20
```

### Rolling Updates

```bash
# 1. Pull latest code
git pull

# 2. Rebuild affected services
docker-compose -f deployment/local/docker-compose.yml build <service-name>

# 3. Restart with zero downtime (for stateless services)
docker-compose -f deployment/local/docker-compose.yml up -d --no-deps --build <service-name>
```

### Monitoring Stack Deployment

```bash
# Start monitoring services
docker-compose -f deployment/local/docker-compose.yml --profile monitoring up -d

# Access monitoring tools
# Prometheus: http://localhost:9090
# Grafana: http://localhost:3000
# Metrics endpoint: http://localhost:8000/metrics
```

---

## Troubleshooting

### Common Issues

#### 1. Service Won't Start

**Symptoms:** Container exits immediately or restarts repeatedly

**Diagnosis:**
```bash
# Check container status
docker ps -a | grep <service-name>

# Check logs
docker logs <container-name>

# Inspect container
docker inspect <container-name>
```

**Common Causes:**
- Port already in use
- Volume mount permissions
- Missing environment variables
- Configuration file errors

#### 2. Health Check Failures

**Symptoms:** Container marked unhealthy

**Diagnosis:**
```bash
# Check health status
docker inspect <container-name> | grep -A 10 Health

# Test health check manually
docker exec <container-name> <health-check-command>
```

**Common Causes:**
- Service not fully started (wait for start_period)
- Incorrect health check endpoint
- Network connectivity issues

#### 3. Network Connectivity Issues

**Symptoms:** Services can't communicate

**Diagnosis:**
```bash
# Inspect network
docker network inspect local_systematic-pdca-local

# Test connectivity
docker exec <container-name> ping <other-service-name>
docker exec <container-name> curl http://<other-service>:<port>
```

**Common Causes:**
- Services on different networks
- Incorrect service name in configuration
- Firewall blocking internal traffic

#### 4. Grafana Login Issues

**Symptoms:** Cannot login with configured password

**Solution:**
```bash
# 1. Verify password in ~/.env
cat ~/.env | grep GF_SECURITY

# 2. Recreate container with correct env
docker-compose -f deployment/local/docker-compose.yml \
  --profile monitoring \
  --env-file ~/.env \
  up -d --force-recreate --no-deps grafana

# 3. Reset Grafana admin password (if needed)
docker exec -it local-grafana-1 grafana-cli admin reset-admin-password NewPassword
```

#### 5. Prometheus Not Scraping Metrics

**Symptoms:** Targets show as "Down" in Prometheus

**Diagnosis:**
```bash
# Check Prometheus targets
curl http://localhost:9090/api/v1/targets

# Test metric endpoint manually
curl http://beast-mode-metrics:8000/metrics
docker exec prometheus wget -qO- http://beast-mode-metrics:8000/metrics
```

**Common Causes:**
- Service not started
- Metrics exporter not running
- Incorrect scrape configuration
- Network connectivity

#### 6. Volume Data Loss

**Symptoms:** Data missing after container restart

**Diagnosis:**
```bash
# List volumes
docker volume ls | grep local_

# Inspect volume
docker volume inspect <volume-name>

# Check if volume is mounted
docker inspect <container-name> | grep -A 10 Mounts
```

**Prevention:**
- Always use named volumes for persistent data
- Regular backups of critical volumes
- Avoid `docker-compose down -v` unless intentional

### Debug Commands

```bash
# View all container logs
docker-compose -f deployment/local/docker-compose.yml logs -f

# View specific service logs
docker-compose -f deployment/local/docker-compose.yml logs -f <service-name>

# Enter container shell
docker exec -it <container-name> sh  # Alpine
docker exec -it <container-name> bash  # Debian/Ubuntu

# Check resource usage
docker stats

# List all resources
docker-compose -f deployment/local/docker-compose.yml ps -a
docker volume ls
docker network ls

# Prune unused resources (CAUTION!)
docker system prune -a --volumes
```

### Performance Tuning

**Prometheus Storage:**
- Adjust retention: `--storage.tsdb.retention.time=30d`
- Adjust size limit: `--storage.tsdb.retention.size=1GB`
- Enable WAL compression: `--storage.tsdb.wal-compression`

**Nginx Performance:**
- Increase worker_connections (default: 1024)
- Tune keepalive_timeout (default: 65s)
- Adjust rate limits per workload

**Container Resources:**
Add to docker-compose.yml:
```yaml
deploy:
  resources:
    limits:
      cpus: '2.0'
      memory: 2G
    reservations:
      cpus: '1.0'
      memory: 1G
```

---

## Additional Resources

### Configuration Files

- **docker-compose.yml:** `/Users/lou/kiro-2/kiro-ai-development-hackathon/deployment/local/docker-compose.yml`
- **Nginx config:** `/Users/lou/kiro-2/kiro-ai-development-hackathon/deployment/local/nginx/nginx.conf`
- **Prometheus config:** `/Users/lou/kiro-2/kiro-ai-development-hackathon/deployment/local/prometheus.yml`
- **Alert rules:** `/Users/lou/kiro-2/kiro-ai-development-hackathon/deployment/local/alert_rules.yml`

### Dockerfile Locations

- **PDCA Orchestrator:** `deployment/systematic-pdca/Dockerfile`
- **Beast Mode Metrics:** `deployment/beast-mode-metrics/Dockerfile`
- **Nginx:** `deployment/local/nginx/Dockerfile`

### Entry Point Scripts

- **Metrics Exporter:** `deployment/beast-mode-metrics/start_metrics.py`
- **PDCA API:** `src/beast_mode/api/main.py`

### Useful Links

- Prometheus: http://localhost:9090
- Prometheus Targets: http://localhost:9090/targets
- Prometheus Alerts: http://localhost:9090/alerts
- Grafana: http://localhost:3000
- Directus: http://localhost:8055
- API Docs: http://localhost/docs
- Health Check: http://localhost/health
- Metrics: http://localhost/metrics

---

**Document Version:** 1.0.0
**Last Updated:** 2025-10-02
**Maintained By:** Beast Mode Framework Team
