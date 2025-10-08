# Nginx Docker Implementation

This directory contains the nginx Docker configuration for the Kiro AI Development Hackathon project.

## Overview

The nginx service acts as a reverse proxy, load balancer, and web server for the systematic-pdca-orchestrator backend service.

## Files

- `Dockerfile` - Nginx Docker image configuration
- `nginx.conf` - Nginx configuration file
- `README.md` - This documentation

## Features

- **Reverse Proxy**: Routes requests to the backend FastAPI application
- **Load Balancing**: Ready for multiple backend instances
- **Health Checks**: Built-in health monitoring
- **Security Headers**: Basic security headers for web requests
- **Rate Limiting**: API rate limiting to prevent abuse
- **Gzip Compression**: Automatic compression for better performance
- **Static File Serving**: Ready for static content delivery
- **Logging**: Comprehensive access and error logging

## Configuration

### Nginx Configuration (`nginx.conf`)

The nginx configuration includes:

- **Upstream Backend**: Points to `systematic-pdca-orchestrator:8080`
- **API Routes**: `/api/` routes are proxied to the backend
- **Health Endpoints**: `/health` and `/nginx-health` for monitoring
- **Static Files**: `/static/` for serving static content
- **Rate Limiting**: 10 req/s for API, 30 req/s for static content
- **Security Headers**: X-Frame-Options, X-Content-Type-Options, etc.

### Docker Configuration

- **Base Image**: nginx:1.25-alpine (lightweight and secure)
- **Additional Tools**: curl for health checks
- **Ports**: 80 (HTTP) and 443 (HTTPS, ready for SSL)
- **Volumes**: Logs and configuration mounted

## Usage

### Using the nginx-manager.sh script

```bash
# Build nginx service
./nginx-manager.sh build

# Start all services
./nginx-manager.sh start

# Start only nginx
./nginx-manager.sh start-nginx

# Stop all services
./nginx-manager.sh stop

# Restart nginx
./nginx-manager.sh restart

# Check status
./nginx-manager.sh status

# View logs
./nginx-manager.sh logs

# Test functionality
./nginx-manager.sh test

# Clean up
./nginx-manager.sh cleanup
```

### Using docker-compose directly

```bash
# Start all services
docker compose up -d

# Start only nginx
docker compose up -d nginx

# View logs
docker compose logs nginx

# Stop services
docker compose down
```

## Endpoints

Once running, the following endpoints are available:

- `http://localhost/` - Main application page
- `http://localhost/health` - Backend health check
- `http://localhost/nginx-health` - Nginx health check
- `http://localhost/api/status` - API status information
- `http://localhost/api/metrics` - System metrics
- `http://localhost/api/test` - Test endpoint for nginx routing
- `http://localhost/docs` - FastAPI documentation (Swagger UI)
- `http://localhost/redoc` - FastAPI documentation (ReDoc)

## Monitoring

### Health Checks

- **Nginx Health**: `curl http://localhost/nginx-health`
- **Backend Health**: `curl http://localhost/health`
- **API Status**: `curl http://localhost/api/status`

### Logs

- **Nginx Access Logs**: Available in the `nginx-logs` Docker volume
- **Nginx Error Logs**: Available in the `nginx-logs` Docker volume
- **Backend Logs**: Available via `docker compose logs systematic-pdca-orchestrator`

## Development

### Modifying Configuration

1. Edit `nginx.conf` for nginx configuration changes
2. Edit `Dockerfile` for Docker image changes
3. Rebuild the service: `./nginx-manager.sh build`
4. Restart the service: `./nginx-manager.sh restart`

### Adding SSL/HTTPS

To enable HTTPS:

1. Add SSL certificates to the nginx container
2. Uncomment the HTTPS server block in `nginx.conf`
3. Update the Dockerfile to copy certificates
4. Rebuild and restart the service

### Load Balancing

To add more backend instances:

1. Add more servers to the `upstream systematic_pdca_backend` block in `nginx.conf`
2. Update the docker-compose.yml to include additional backend services
3. Rebuild and restart

## Troubleshooting

### Common Issues

1. **Backend not responding**: Check if the backend service is running and healthy
2. **502 Bad Gateway**: Backend service is not accessible from nginx
3. **Connection refused**: Check network configuration and service dependencies
4. **Permission denied**: Check file permissions and Docker volume mounts

### Debug Commands

```bash
# Check service status
docker compose ps

# View nginx logs
docker compose logs nginx

# View backend logs
docker compose logs systematic-pdca-orchestrator

# Test nginx configuration
docker compose exec nginx nginx -t

# Access nginx container shell
docker compose exec nginx sh

# Test connectivity from nginx to backend
docker compose exec nginx curl http://systematic-pdca-orchestrator:8080/health
```

## Security Considerations

- The current configuration is for development use
- For production, consider:
  - SSL/TLS certificates
  - More restrictive CORS settings
  - Additional security headers
  - Rate limiting adjustments
  - Firewall configuration
  - Regular security updates
