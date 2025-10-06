# MSP SSL Chaos Tamer - Deployment Guide

## 🚀 Complete Deployment Guide for MSPs

This guide provides comprehensive instructions for deploying the MSP SSL Chaos Tamer in various environments, from Docker containers to bare metal installations.

---

## 📋 Table of Contents

1. [Quick Start (Docker)](#quick-start-docker)
2. [Production Deployment](#production-deployment)
3. [Environment-Specific Deployments](#environment-specific-deployments)
4. [Configuration Guide](#configuration-guide)
5. [Security Hardening](#security-hardening)
6. [Monitoring Setup](#monitoring-setup)
7. [Troubleshooting](#troubleshooting)
8. [Maintenance & Updates](#maintenance--updates)

---

## 🐳 Quick Start (Docker)

### Prerequisites
- Docker 20.10+ and Docker Compose 2.0+
- 2GB RAM minimum, 4GB recommended
- 10GB disk space for data and logs
- Network access to certificate authorities

### 1. Clone and Setup
```bash
# Clone the repository
git clone https://github.com/your-org/msp-ssl-chaos-tamer.git
cd msp-ssl-chaos-tamer

# Create environment file
cp .env.example .env
```

### 2. Configure Environment
Edit `.env` file:
```bash
# Master encryption key (CRITICAL - SAVE THIS KEY!)
MSP_SSL_MASTER_KEY=your-secure-master-key-here

# Grafana admin password
GRAFANA_ADMIN_PASSWORD=your-secure-password

# Log level
LOG_LEVEL=INFO

# Data directories
DATA_DIR=./data
LOG_DIR=./logs
CERT_DIR=./certs
BACKUP_DIR=./backups
```

### 3. Deploy Stack
```bash
# Create directories
mkdir -p data logs certs backups config

# Start the complete stack
docker-compose up -d

# Check status
docker-compose ps
```

### 4. Access Services
- **MSP SSL Tamer:** http://localhost:8080
- **Grafana Dashboard:** http://localhost:3000 (admin/your-password)
- **Prometheus Metrics:** http://localhost:9091

---

## 🏭 Production Deployment

### Architecture Overview
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Load Balancer │    │  MSP SSL Tamer  │    │   Monitoring    │
│    (Nginx)      │────│   Application   │────│  (Prometheus)   │
│                 │    │                 │    │   & Grafana     │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Certificate   │    │   Credential    │    │   Monitoring    │
│   Storage       │    │   Storage       │    │   Storage       │
│   (Encrypted)   │    │   (Encrypted)   │    │   (Time Series) │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

### Hardware Requirements

**Minimum Production Setup:**
- **CPU:** 4 cores (2.4GHz+)
- **RAM:** 8GB (16GB recommended)
- **Storage:** 100GB SSD (500GB recommended)
- **Network:** 100Mbps+ with low latency to CAs

**High-Availability Setup:**
- **Load Balancer:** 2x 2 cores, 4GB RAM
- **Application Servers:** 3x 4 cores, 8GB RAM
- **Database:** 2x 4 cores, 16GB RAM, SSD storage
- **Monitoring:** 2x 2 cores, 8GB RAM

---

## 🌐 Environment-Specific Deployments

### AWS Deployment

#### 1. ECS Fargate Deployment
```bash
# Install AWS CLI and ECS CLI
pip install awscli
curl -Lo ecs-cli https://amazon-ecs-cli.s3.amazonaws.com/ecs-cli-linux-amd64-latest
chmod +x ecs-cli && sudo mv ecs-cli /usr/local/bin/

# Configure ECS cluster
ecs-cli configure --cluster msp-ssl-cluster --region us-west-2 --default-launch-type FARGATE
ecs-cli up --cluster-config msp-ssl-cluster --ecs-profile default

# Deploy using ECS task definition
aws ecs register-task-definition --cli-input-json file://aws/task-definition.json
aws ecs create-service --cluster msp-ssl-cluster --service-name msp-ssl-service --task-definition msp-ssl-tamer:1 --desired-count 2
```

### Azure Deployment

#### 1. Container Instances
```bash
# Install Azure CLI
curl -sL https://aka.ms/InstallAzureCLIDeb | sudo bash

# Create resource group and container instance
az group create --name msp-ssl-rg --location eastus
az container create --resource-group msp-ssl-rg --name msp-ssl-tamer \
    --image msp-ssl-chaos-tamer:latest --cpu 2 --memory 4 \
    --ports 80 443 --dns-name-label msp-ssl-tamer \
    --environment-variables MSP_SSL_ENV=production
```

### Bare Metal / VM Deployment

#### 1. Ubuntu/Debian Installation
```bash
#!/bin/bash
# MSP SSL Chaos Tamer - Bare Metal Installation Script

# Update system
sudo apt update && sudo apt upgrade -y

# Install Python 3.9+
sudo apt install -y python3.9 python3.9-venv python3.9-dev python3-pip

# Install system dependencies
sudo apt install -y nginx postgresql redis-server supervisor

# Create application user
sudo useradd -m -s /bin/bash mspssl
sudo usermod -aG sudo mspssl

# Create application directory
sudo mkdir -p /opt/msp-ssl-tamer
sudo chown mspssl:mspssl /opt/msp-ssl-tamer

# Switch to application user
sudo -u mspssl bash << 'EOF'
cd /opt/msp-ssl-tamer

# Create virtual environment
python3.9 -m venv venv
source venv/bin/activate

# Clone and install application
git clone https://github.com/your-org/msp-ssl-chaos-tamer.git .
pip install -r requirements.txt
pip install -e .

# Create configuration
cp config/production.example.yml config/production.yml
# Edit configuration as needed

# Initialize database
python -m msp_ssl_chaos_tamer.cli init-db
EOF

# Configure systemd service
sudo cp scripts/systemd/msp-ssl-tamer.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable msp-ssl-tamer
sudo systemctl start msp-ssl-tamer

# Configure nginx
sudo cp config/nginx/msp-ssl-tamer.conf /etc/nginx/sites-available/
sudo ln -s /etc/nginx/sites-available/msp-ssl-tamer.conf /etc/nginx/sites-enabled/
sudo systemctl reload nginx

echo "MSP SSL Chaos Tamer installed successfully!"
echo "Access the web interface at: https://your-domain.com"
```

---

## ⚙️ Configuration Guide

### Core Configuration Files

#### 1. Application Configuration (`config/production.yml`)
```yaml
# MSP SSL Chaos Tamer - Production Configuration

# Application Settings
app:
  name: "MSP SSL Chaos Tamer"
  version: "1.0.0"
  environment: "production"
  debug: false
  log_level: "INFO"
  
# Server Configuration
server:
  host: "0.0.0.0"
  port: 8080
  ssl_port: 8443
  ssl_cert: "/app/config/ssl.crt"
  ssl_key: "/app/config/ssl.key"
  workers: 4
  
# Database Configuration
database:
  url: "${MSP_SSL_DATABASE_URL}"
  pool_size: 20
  max_overflow: 30
  pool_timeout: 30
  pool_recycle: 3600
  
# Security Configuration
security:
  master_key: "${MSP_SSL_MASTER_KEY}"
  jwt_secret: "${MSP_SSL_JWT_SECRET}"
  jwt_expiry: 3600
  session_timeout: 1800
  max_login_attempts: 5
  lockout_duration: 900
  
# Certificate Authority Plugins
ca_plugins:
  letsencrypt:
    enabled: true
    staging: false
    email: "${LETSENCRYPT_EMAIL}"
    key_size: 2048
    challenge_type: "http-01"
    
  godaddy:
    enabled: true
    sandbox: false
    api_key: "${GODADDY_API_KEY}"
    api_secret: "${GODADDY_API_SECRET}"
    
# Monitoring Configuration
monitoring:
  prometheus:
    enabled: true
    port: 9090
    path: "/metrics"
    
  health_checks:
    enabled: true
    interval: 30
    timeout: 10
    
# Alert Configuration
alerts:
  email:
    enabled: true
    smtp_host: "${MSP_SSL_SMTP_HOST}"
    smtp_port: 587
    smtp_user: "${MSP_SSL_SMTP_USER}"
    smtp_password: "${MSP_SSL_SMTP_PASSWORD}"
    from_address: "${MSP_SSL_ALERT_EMAIL}"
    
# Backup Configuration
backup:
  enabled: true
  schedule: "0 2 * * *"  # Daily at 2 AM
  retention_days: 30
  storage_path: "/app/backups"
  encrypt: true
```

---

## 🔒 Security Hardening

### 1. System Security

#### Firewall Configuration
```bash
# Configure UFW firewall
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow ssh
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw allow from 10.0.0.0/8 to any port 9090  # Prometheus (internal only)
sudo ufw enable
```

#### SSH Hardening
```bash
# Edit /etc/ssh/sshd_config
sudo sed -i 's/#PermitRootLogin yes/PermitRootLogin no/' /etc/ssh/sshd_config
sudo sed -i 's/#PasswordAuthentication yes/PasswordAuthentication no/' /etc/ssh/sshd_config
sudo sed -i 's/#PubkeyAuthentication yes/PubkeyAuthentication yes/' /etc/ssh/sshd_config
echo "AllowUsers mspssl" | sudo tee -a /etc/ssh/sshd_config
sudo systemctl restart sshd
```

### 2. Application Security

#### Environment Variables Security
```bash
# Create secure environment file
sudo touch /opt/msp-ssl-tamer/.env
sudo chmod 600 /opt/msp-ssl-tamer/.env
sudo chown mspssl:mspssl /opt/msp-ssl-tamer/.env

# Generate secure keys
python3 -c "import secrets; print('MSP_SSL_MASTER_KEY=' + secrets.token_urlsafe(32))" | sudo tee -a /opt/msp-ssl-tamer/.env
python3 -c "import secrets; print('MSP_SSL_JWT_SECRET=' + secrets.token_urlsafe(32))" | sudo tee -a /opt/msp-ssl-tamer/.env
```

---

## 📊 Monitoring Setup

### 1. Grafana Dashboard Configuration

The application provides comprehensive monitoring through Prometheus metrics and Grafana dashboards.

### 2. Alert Rules

Configure alerts for:
- Certificate expiration warnings
- Renewal failures
- System health issues
- Performance degradation

---

## 🔧 Troubleshooting

### Common Issues and Solutions

#### 1. Application Won't Start
```bash
# Check logs
docker-compose logs msp-ssl-tamer

# Verify configuration
docker-compose config

# Test database connection
docker-compose exec msp-ssl-tamer python -c "
from msp_ssl_chaos_tamer.storage.database import DatabaseManager
db = DatabaseManager()
print('Database connection:', db.test_connection())
"
```

#### 2. Certificate Renewal Failures
```bash
# Check CA plugin status
docker-compose exec msp-ssl-tamer python -c "
from msp_ssl_chaos_tamer.plugins import get_plugin
le = get_plugin('letsencrypt')
print('Let\'s Encrypt status:', le.is_healthy())
"

# Manual renewal test
docker-compose exec msp-ssl-tamer python -m msp_ssl_chaos_tamer.cli renew-certificate --domain example.com --dry-run
```

---

## 🔄 Maintenance & Updates

### Regular Maintenance Tasks

#### 1. Daily Tasks (Automated)
```bash
#!/bin/bash
# Daily maintenance script

# Backup database
docker-compose exec postgres pg_dump -U msp_ssl_user msp_ssl_db | gzip > /opt/msp-ssl-tamer/backups/db-$(date +%Y%m%d).sql.gz

# Check certificate expiry
docker-compose exec msp-ssl-tamer python -m msp_ssl_chaos_tamer.cli check-expiry --days 30

# Health check
curl -f http://localhost:8080/health || echo "Health check failed" | mail -s "MSP SSL Tamer Alert" admin@your-msp.com
```

### Update Procedures

#### 1. Application Updates
```bash
# Backup current version
docker-compose exec postgres pg_dump -U msp_ssl_user msp_ssl_db > backup-pre-update.sql

# Pull new version
docker-compose pull msp-ssl-tamer

# Update with zero downtime
docker-compose up -d --no-deps msp-ssl-tamer

# Verify update
curl -f http://localhost:8080/health
```

---

## 📞 Support and Resources

### Getting Help

1. **Documentation:** Check the official documentation
2. **Community Forum:** Join our community discussions
3. **GitHub Issues:** Report bugs at GitHub Issues
4. **Professional Support:** Contact support team

---

## 🎯 Next Steps

After successful deployment:

1. **Configure CA Plugins:** Set up Let's Encrypt and GoDaddy integrations
2. **Import Existing Certificates:** Use the bulk import feature
3. **Set Up Monitoring:** Configure alerts and dashboards
4. **Train Your Team:** Conduct training sessions for MSP staff
5. **Plan Automation:** Implement automated renewal workflows

**Congratulations! Your MSP SSL Chaos Tamer is now deployed and ready to bring order to certificate chaos! 🎉**