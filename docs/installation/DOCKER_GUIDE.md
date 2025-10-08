# Docker Deployment Guide

This guide covers how to deploy and run the Beast Mode AI Development Framework using Docker containers.

## Quick Start

### Prerequisites

- Docker 20.10+ installed
- Docker Compose 2.0+ installed
- At least 4GB RAM available
- 10GB free disk space

### Production Deployment

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd beast-mode-ai-framework
   ```

2. **Start the production environment:**
   ```bash
   ./docker/manage.sh start production
   ```

3. **Access the services:**
   - Observatory: http://localhost:8080
   - Prometheus: http://localhost:9090
   - Grafana: http://localhost:3000 (admin/admin)

### Development Environment

1. **Start the development environment:**
   ```bash
   ./docker/manage.sh start development
   ```

2. **Access development services:**
   - Observatory: http://localhost:8080
   - Jupyter Notebook: http://localhost:8888
   - Mailhog: http://localhost:8025
   - PostgreSQL: localhost:5432

## Docker Images

### Production Image (`Dockerfile`)

- **Base:** Python 3.11-slim
- **Size:** ~500MB (optimized)
- **Features:**
  - Multi-stage build for smaller image
  - Non-root user for security
  - Health checks included
  - Production-ready configuration

### Development Image (`Dockerfile.dev`)

- **Base:** Python 3.11-slim
- **Size:** ~800MB (includes dev tools)
- **Features:**
  - Development tools (debugger, Jupyter)
  - Hot reloading support
  - Redis server included
  - Volume mounts for code changes

## Docker Compose Configurations

### Production (`docker-compose.yml`)

Services included:
- **beast-mode:** Main application
- **redis:** Data storage and caching
- **prometheus:** Metrics collection
- **grafana:** Monitoring dashboards

### Development (`docker-compose.dev.yml`)

Additional services:
- **jupyter:** Interactive development
- **postgres:** Development database
- **mailhog:** Email testing

## Management Script

The `docker/manage.sh` script provides convenient commands:

```bash
# Build images
./docker/manage.sh build [production|development]

# Start services
./docker/manage.sh start [production|development]

# Stop services
./docker/manage.sh stop [production|development]

# View logs
./docker/manage.sh logs [production|development] [service]

# Check health
./docker/manage.sh health [production|development]

# Execute commands
./docker/manage.sh exec [production|development] [service] [command]

# Clean up
./docker/manage.sh cleanup [production|development]
```

## Configuration

### Environment Variables

Create a `.env` file in the project root:

```bash
# Redis Configuration
REDIS_HOST=redis
REDIS_PORT=6379
REDIS_PASSWORD=your_secure_password

# API Keys
OPENAI_API_KEY=your_openai_key
ANTHROPIC_API_KEY=your_anthropic_key

# Environment
ENVIRONMENT=production
DEBUG=false

# Monitoring
PROMETHEUS_PORT=9090
GRAFANA_PORT=3000

# Observatory
OBSERVATORY_PORT=8080
OBSERVATORY_HOST=0.0.0.0
```

### Service Configuration

#### Redis (`config/redis.conf`)
- Persistence enabled
- Memory optimization
- Security settings

#### Prometheus (`config/prometheus.yml`)
- Application metrics scraping
- Service discovery
- Alerting rules

### Volume Mounts

#### Production
- `./data:/app/data` - Application data
- `./logs:/app/logs` - Application logs

#### Development
- `./src:/app/src` - Source code (hot reload)
- `./examples:/app/examples` - Examples
- `./docs:/app/docs` - Documentation
- `./tests:/app/tests` - Test files

## Security Considerations

### Production Security

1. **Non-root user:** Application runs as `appuser`
2. **Read-only filesystem:** Most directories are read-only
3. **Network isolation:** Services communicate via internal network
4. **Secret management:** Use environment variables for secrets
5. **Health checks:** Automatic service health monitoring

### Development Security

1. **Isolated environment:** Development containers are isolated
2. **Local-only access:** Services bound to localhost
3. **Test credentials:** Use test credentials only
4. **Volume permissions:** Proper file permissions maintained

## Performance Optimization

### Image Optimization

1. **Multi-stage builds:** Separate build and runtime stages
2. **Layer caching:** Optimized layer ordering
3. **Minimal base images:** Using slim Python images
4. **Dependency optimization:** Only necessary packages included

### Runtime Optimization

1. **Resource limits:** CPU and memory limits configured
2. **Health checks:** Proper health check intervals
3. **Restart policies:** Automatic restart on failure
4. **Log rotation:** Prevent log files from growing too large

## Monitoring and Logging

### Prometheus Metrics

Available at `http://localhost:9090`:
- Application performance metrics
- System resource usage
- Custom business metrics
- Service health status

### Grafana Dashboards

Available at `http://localhost:3000`:
- System overview dashboard
- Application performance dashboard
- Error tracking dashboard
- Custom metric visualizations

### Log Management

```bash
# View all logs
./docker/manage.sh logs production

# View specific service logs
./docker/manage.sh logs production beast-mode

# Follow logs in real-time
./docker/manage.sh logs production beast-mode -f
```

## Troubleshooting

### Common Issues

#### Port Conflicts
```bash
# Check which ports are in use
netstat -tulpn | grep :8080

# Stop conflicting services
sudo systemctl stop apache2  # Example
```

#### Memory Issues
```bash
# Check Docker memory usage
docker stats

# Increase Docker memory limit in Docker Desktop
# Settings > Resources > Memory
```

#### Permission Issues
```bash
# Fix volume permissions
sudo chown -R $USER:$USER ./data ./logs

# Reset Docker permissions
docker-compose down -v
./docker/manage.sh cleanup production
```

### Health Check Failures

```bash
# Check service health
./docker/manage.sh health production

# View detailed health check logs
docker inspect beast-mode-app | grep -A 10 Health

# Manual health check
curl http://localhost:8080/health
```

### Database Connection Issues

```bash
# Check Redis connection
docker exec beast-mode-redis redis-cli ping

# Check PostgreSQL connection (development)
docker exec beast-mode-postgres-dev psql -U beast_mode -d beast_mode_dev -c "SELECT 1;"
```

## Backup and Recovery

### Data Backup

```bash
# Backup Redis data
docker exec beast-mode-redis redis-cli BGSAVE
docker cp beast-mode-redis:/data/dump.rdb ./backup/

# Backup application data
tar -czf backup/app-data-$(date +%Y%m%d).tar.gz ./data/
```

### Data Recovery

```bash
# Restore Redis data
docker cp ./backup/dump.rdb beast-mode-redis:/data/
docker restart beast-mode-redis

# Restore application data
tar -xzf backup/app-data-20231201.tar.gz
```

## Scaling and Production Deployment

### Horizontal Scaling

```yaml
# docker-compose.prod.yml
services:
  beast-mode:
    deploy:
      replicas: 3
      resources:
        limits:
          cpus: '1.0'
          memory: 1G
        reservations:
          cpus: '0.5'
          memory: 512M
```

### Load Balancing

```yaml
# Add nginx load balancer
nginx:
  image: nginx:alpine
  ports:
    - "80:80"
  volumes:
    - ./config/nginx.conf:/etc/nginx/nginx.conf
  depends_on:
    - beast-mode
```

### Production Checklist

- [ ] Environment variables configured
- [ ] Secrets properly managed
- [ ] SSL/TLS certificates configured
- [ ] Monitoring and alerting set up
- [ ] Backup strategy implemented
- [ ] Log aggregation configured
- [ ] Resource limits set
- [ ] Health checks validated
- [ ] Security scan completed
- [ ] Performance testing done

## Support

For Docker-related issues:

1. Check the [troubleshooting section](#troubleshooting)
2. Review Docker logs: `./docker/manage.sh logs production`
3. Validate configuration: `./docker/manage.sh health production`
4. Check system resources: `docker stats`
5. Consult the [main documentation](../README.md)

## Advanced Configuration

### Custom Networks

```yaml
networks:
  frontend:
    driver: bridge
  backend:
    driver: bridge
    internal: true
```

### External Services

```yaml
services:
  beast-mode:
    external_links:
      - external-redis:redis
      - external-postgres:postgres
```

### Resource Constraints

```yaml
services:
  beast-mode:
    deploy:
      resources:
        limits:
          cpus: '2.0'
          memory: 2G
        reservations:
          cpus: '1.0'
          memory: 1G
```