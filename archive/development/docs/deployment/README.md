# MSP SSL Chaos Tamer - Deployment Guide

## Overview

The MSP SSL Chaos Tamer provides multiple deployment options to match your MSP infrastructure requirements. This guide covers all deployment modes with step-by-step instructions, configuration options, and troubleshooting procedures.

## Quick Start

### Docker Deployment (Recommended)

```bash
# Clone the repository
git clone https://github.com/your-org/msp-ssl-chaos-tamer.git
cd msp-ssl-chaos-tamer

# Start with Docker Compose
docker-compose up -d

# Access the web interface
open http://localhost:8080
```

### System Requirements

**Minimum Requirements:**
- CPU: 2 cores
- RAM: 4GB
- Storage: 20GB
- OS: Linux, macOS, Windows (with Docker)

**Recommended for Production:**
- CPU: 4 cores
- RAM: 8GB
- Storage: 100GB SSD
- OS: Ubuntu 22.04 LTS or RHEL 8+

## Deployment Options

### 1. Docker Container Deployment

**Advantages:**
- Easy deployment and updates
- Consistent environment across systems
- Built-in monitoring and health checks
- Automatic SSL certificate management

**Prerequisites:**
- Docker 20.10+
- Docker Compose 2.0+

**Quick Deployment:**

```bash
# Create environment file
cat > .env << EOF
ENVIRONMENT=production
LOG_LEVEL=INFO
MSP_SSL_MASTER_KEY=$(openssl rand -base64 32)
GRAFANA_PASSWORD=$(openssl rand -base64 16)
REDIS_PASSWORD=$(openssl rand -base64 16)
EOF

# Deploy the stack
docker-compose up -d

# Check status
docker-compose ps
```

**Service Endpoints:**
- Web Interface: http://localhost:8080
- Secure Interface: https://localhost:8443
- Prometheus Metrics: http://localhost:9091
- Grafana Dashboard: http://localhost:3000

### 2. VM Appliance Deployment

**Download Pre-built Appliance:**

```bash
# Download VM appliance (Ubuntu 22.04 LTS)
wget https://releases.msp-ssl-chaos-tamer.com/v1.0.0/msp-ssl-appliance.ova

# Import into VMware/VirtualBox
# Configure network settings
# Start the appliance
```

**Manual VM Setup:**

```bash
# On Ubuntu 22.04 LTS
sudo apt update && sudo apt upgrade -y

# Install dependencies
sudo apt install -y python3.9 python3-pip sqlite3 nginx

# Create service user
sudo useradd -r -s /bin/bash -d /opt/msp-ssl mspssl

# Install application
sudo -u mspssl pip3 install msp-ssl-chaos-tamer

# Configure systemd service
sudo systemctl enable msp-ssl-chaos-tamer
sudo systemctl start msp-ssl-chaos-tamer
```

### 3. Cloud Deployment

#### AWS Deployment

**Using Terraform:**

```hcl
# main.tf
module "msp_ssl_chaos_tamer" {
  source = "./terraform/aws"
  
  instance_type = "t3.medium"
  key_name     = "your-key-pair"
  vpc_id       = "vpc-xxxxxxxx"
  subnet_id    = "subnet-xxxxxxxx"
  
  tags = {
    Environment = "production"
    Project     = "msp-ssl-chaos-tamer"
  }
}
```

```bash
# Deploy to AWS
terraform init
terraform plan
terraform apply
```

#### Azure Deployment

```bash
# Create resource group
az group create --name msp-ssl-rg --location eastus

# Deploy using ARM template
az deployment group create \
  --resource-group msp-ssl-rg \
  --template-file azure-template.json \
  --parameters @azure-parameters.json
```

#### Google Cloud Platform

```bash
# Create GCE instance
gcloud compute instances create msp-ssl-chaos-tamer \
  --image-family ubuntu-2204-lts \
  --image-project ubuntu-os-cloud \
  --machine-type e2-medium \
  --zone us-central1-a \
  --tags msp-ssl-server

# Configure firewall
gcloud compute firewall-rules create allow-msp-ssl \
  --allow tcp:8080,tcp:8443,tcp:9090 \
  --source-ranges 0.0.0.0/0 \
  --target-tags msp-ssl-server
```

### 4. Bare Metal Deployment

**System Preparation:**

```bash
# Install system dependencies (Ubuntu/Debian)
sudo apt update
sudo apt install -y python3.9 python3-pip python3-venv \
  sqlite3 nginx certbot redis-server prometheus grafana

# Create application user
sudo useradd -r -m -s /bin/bash mspssl
sudo mkdir -p /opt/msp-ssl-chaos-tamer
sudo chown mspssl:mspssl /opt/msp-ssl-chaos-tamer
```

**Application Installation:**

```bash
# Switch to application user
sudo -u mspssl -i

# Create virtual environment
python3 -m venv /opt/msp-ssl-chaos-tamer/venv
source /opt/msp-ssl-chaos-tamer/venv/bin/activate

# Install application
pip install msp-ssl-chaos-tamer

# Create configuration
mkdir -p /opt/msp-ssl-chaos-tamer/{config,data,logs,backups}
```

## Configuration

### Environment Variables

```bash
# Core Configuration
MSP_SSL_ENVIRONMENT=production
MSP_SSL_LOG_LEVEL=INFO
MSP_SSL_DATA_DIR=/app/data
MSP_SSL_CONFIG_DIR=/app/config

# Security
MSP_SSL_MASTER_KEY=your-encryption-key
MSP_SSL_SECRET_KEY=your-session-key

# Database
MSP_SSL_DATABASE_URL=sqlite:///app/data/certificates.db

# Monitoring
MSP_SSL_PROMETHEUS_PORT=9090
MSP_SSL_METRICS_ENABLED=true

# Web Interface
MSP_SSL_WEB_PORT=8080
MSP_SSL_SECURE_PORT=8443
MSP_SSL_SSL_CERT_PATH=/app/ssl/cert.pem
MSP_SSL_SSL_KEY_PATH=/app/ssl/key.pem
```

### MSP-Specific Configuration

**Client Configuration:**

```yaml
# config/clients.yml
clients:
  - id: client-001
    name: "Acme Corporation"
    domains:
      - "acme.com"
      - "*.acme.com"
    preferred_ca: "letsencrypt"
    emergency_contact: "admin@acme.com"
    
  - id: client-002
    name: "Beta Industries"
    domains:
      - "betaindustries.com"
    preferred_ca: "godaddy"
    certificate_policies:
      - renewal_days_before_expiry: 30
      - emergency_renewal_enabled: true
```

**CA Configuration:**

```yaml
# config/certificate_authorities.yml
certificate_authorities:
  letsencrypt:
    enabled: true
    directory_url: "https://acme-v02.api.letsencrypt.org/directory"
    email: "certificates@yourmsp.com"
    challenge_type: "http-01"
    
  godaddy:
    enabled: true
    api_key: "${GODADDY_API_KEY}"
    api_secret: "${GODADDY_API_SECRET}"
    
  namecheap:
    enabled: false
    api_key: "${NAMECHEAP_API_KEY}"
    username: "${NAMECHEAP_USERNAME}"
```

## Security Configuration

### SSL/TLS Setup

```bash
# Generate self-signed certificate for development
openssl req -x509 -newkey rsa:4096 -keyout ssl/key.pem \
  -out ssl/cert.pem -days 365 -nodes \
  -subj "/C=US/ST=State/L=City/O=MSP/CN=localhost"

# For production, use Let's Encrypt
certbot certonly --standalone -d your-domain.com
```

### Firewall Configuration

```bash
# UFW (Ubuntu)
sudo ufw allow 22/tcp    # SSH
sudo ufw allow 80/tcp    # HTTP
sudo ufw allow 443/tcp   # HTTPS
sudo ufw allow 8080/tcp  # MSP SSL Web
sudo ufw allow 8443/tcp  # MSP SSL Secure
sudo ufw allow 9090/tcp  # Prometheus (restrict to monitoring network)
sudo ufw enable

# iptables
sudo iptables -A INPUT -p tcp --dport 8080 -j ACCEPT
sudo iptables -A INPUT -p tcp --dport 8443 -j ACCEPT
sudo iptables -A INPUT -p tcp --dport 9090 -s 10.0.0.0/8 -j ACCEPT
```

### Access Control

```yaml
# config/access_control.yml
rbac:
  roles:
    - name: "msp_admin"
      permissions:
        - "certificates:*"
        - "clients:*"
        - "system:*"
        
    - name: "client_viewer"
      permissions:
        - "certificates:read"
        - "clients:read_own"
        
  users:
    - username: "admin@yourmsp.com"
      roles: ["msp_admin"]
      
    - username: "client@acme.com"
      roles: ["client_viewer"]
      client_id: "client-001"
```

## Monitoring and Observability

### Prometheus Configuration

```yaml
# monitoring/prometheus.yml
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'msp-ssl-chaos-tamer'
    static_configs:
      - targets: ['msp-ssl-chaos-tamer:9090']
    scrape_interval: 30s
    metrics_path: '/metrics'
```

### Grafana Dashboards

The deployment includes pre-configured Grafana dashboards:

- **Certificate Overview**: Certificate inventory and health
- **MSP Operations**: Client metrics and operational status
- **System Health**: Application performance and resource usage
- **Security Monitoring**: Authentication and access patterns

### Log Management

```yaml
# config/logging.yml
version: 1
formatters:
  standard:
    format: '%(asctime)s [%(levelname)s] %(name)s: %(message)s'
    
handlers:
  file:
    class: logging.handlers.RotatingFileHandler
    filename: /app/logs/msp-ssl.log
    maxBytes: 10485760  # 10MB
    backupCount: 5
    formatter: standard
    
  console:
    class: logging.StreamHandler
    formatter: standard
    
loggers:
  msp_ssl:
    level: INFO
    handlers: [file, console]
    propagate: false
```

## Backup and Recovery

### Automated Backups

```bash
#!/bin/bash
# backup.sh - Automated backup script

BACKUP_DIR="/app/backups"
DATE=$(date +%Y%m%d_%H%M%S)

# Backup database
sqlite3 /app/data/certificates.db ".backup $BACKUP_DIR/certificates_$DATE.db"

# Backup credentials
cp /app/data/credentials.enc "$BACKUP_DIR/credentials_$DATE.enc"

# Backup configuration
tar -czf "$BACKUP_DIR/config_$DATE.tar.gz" /app/config/

# Cleanup old backups (keep 30 days)
find "$BACKUP_DIR" -name "*.db" -mtime +30 -delete
find "$BACKUP_DIR" -name "*.enc" -mtime +30 -delete
find "$BACKUP_DIR" -name "*.tar.gz" -mtime +30 -delete

echo "Backup completed: $DATE"
```

### Disaster Recovery

```bash
# Restore from backup
RESTORE_DATE="20241001_120000"

# Stop services
docker-compose down

# Restore database
cp "/app/backups/certificates_$RESTORE_DATE.db" /app/data/certificates.db

# Restore credentials
cp "/app/backups/credentials_$RESTORE_DATE.enc" /app/data/credentials.enc

# Restore configuration
tar -xzf "/app/backups/config_$RESTORE_DATE.tar.gz" -C /

# Start services
docker-compose up -d
```

## Troubleshooting

### Common Issues

**1. Database Connection Errors**

```bash
# Check database file permissions
ls -la /app/data/certificates.db

# Test database connectivity
sqlite3 /app/data/certificates.db "SELECT COUNT(*) FROM certificates;"

# Recreate database if corrupted
python -c "
from msp_ssl_chaos_tamer.storage.database import CertificateDatabase
db = CertificateDatabase('/app/data/certificates.db')
print('Database recreated')
"
```

**2. Certificate Authority Authentication Failures**

```bash
# Check CA credentials
python -c "
from msp_ssl_chaos_tamer.storage.credentials import EncryptedCredentialStore
store = EncryptedCredentialStore('/app/data/credentials.enc')
print('Stored CAs:', store.list_credentials())
"

# Test CA connectivity
curl -I https://acme-v02.api.letsencrypt.org/directory
```

**3. Port Binding Issues**

```bash
# Check port usage
netstat -tlnp | grep :8080

# Kill conflicting processes
sudo fuser -k 8080/tcp

# Restart with different ports
MSP_SSL_WEB_PORT=8081 docker-compose up -d
```

### Log Analysis

```bash
# View application logs
docker-compose logs -f msp-ssl-chaos-tamer

# Check specific error patterns
grep -i "error\|exception\|failed" /app/logs/msp-ssl.log

# Monitor certificate operations
tail -f /app/logs/msp-ssl.log | grep "certificate"
```

### Performance Tuning

```yaml
# config/performance.yml
database:
  connection_pool_size: 20
  query_timeout: 30
  
cache:
  enabled: true
  ttl: 3600
  max_size: 1000
  
rate_limiting:
  enabled: true
  requests_per_minute: 100
  burst_size: 20
```

## Maintenance

### Updates

```bash
# Docker deployment update
docker-compose pull
docker-compose up -d

# Bare metal update
pip install --upgrade msp-ssl-chaos-tamer
sudo systemctl restart msp-ssl-chaos-tamer
```

### Health Monitoring

```bash
# Check system health
curl http://localhost:8080/health

# Check component status
curl http://localhost:8080/status

# View metrics
curl http://localhost:9090/metrics
```

### Certificate Renewal Monitoring

```bash
# List expiring certificates
curl http://localhost:8080/api/certificates/expiring

# Force certificate renewal
curl -X POST http://localhost:8080/api/certificates/{id}/renew
```

## Support

### Documentation
- [API Reference](../api/README.md)
- [Configuration Guide](../configuration/README.md)
- [Security Best Practices](../security/README.md)

### Community
- GitHub Issues: https://github.com/your-org/msp-ssl-chaos-tamer/issues
- Documentation: https://docs.msp-ssl-chaos-tamer.com
- Community Forum: https://community.msp-ssl-chaos-tamer.com

### Professional Support
For MSPs requiring professional support, training, or custom integrations, contact our team at support@msp-ssl-chaos-tamer.com.