# Environment Variables Configuration

## Overview

The Beast Mode AI Development Framework uses environment-based configuration for all sensitive data and system settings. This ensures secure credential management and flexible deployment across different environments.

## Security Requirements

⚠️ **CRITICAL**: All sensitive configuration must use environment variables. Never hardcode credentials in source code.

## Required Environment Variables

### Redis Configuration

Redis is used for execution tracking and state management.

```bash
# Required: Redis authentication password
REDIS_PASSWORD=your_secure_redis_password

# Optional: Redis connection details (defaults provided)
REDIS_HOST=localhost          # Default: localhost
REDIS_PORT=6379              # Default: 6379
REDIS_DB=0                   # Default: 0
```

**Security Notes:**
- `REDIS_PASSWORD` is required for all Redis connections
- Use a strong, unique password for Redis authentication
- Never commit Redis passwords to version control

### AI API Keys

At least one AI API key is required for the framework to function.

```bash
# OpenAI API Key
OPENAI_API_KEY=sk-your_openai_api_key_here

# Anthropic API Key
ANTHROPIC_API_KEY=your_anthropic_api_key_here

# Google AI API Key (optional)
GOOGLE_API_KEY=your_google_api_key_here
```

**API Key Requirements:**
- At least one of `OPENAI_API_KEY` or `ANTHROPIC_API_KEY` must be set
- API keys must be valid and have sufficient quota
- Keys should have appropriate permissions for your use case

### Database Configuration

For components that require database access.

```bash
# Database password (required if using database features)
DATABASE_PASSWORD=your_secure_database_password

# Complete database URL (alternative to individual settings)
DATABASE_URL=postgresql://user:password@host:5432/dbname

# Individual database settings
DATABASE_HOST=localhost       # Default: localhost
DATABASE_PORT=5432           # Default: 5432
DATABASE_NAME=beast_mode     # Default: beast_mode
DATABASE_USER=postgres       # Default: postgres
```

## Optional Environment Variables

### Application Settings

```bash
# Environment designation
ENVIRONMENT=development      # Options: development, staging, production

# Debug mode
DEBUG=false                 # Options: true, false

# Logging level
LOG_LEVEL=INFO             # Options: DEBUG, INFO, WARNING, ERROR, CRITICAL
```

### Performance Configuration

```bash
# Maximum concurrent tasks in orchestrator
MAX_CONCURRENT_TASKS=10     # Default: 10

# Context cache size limit in MB
CONTEXT_CACHE_SIZE_MB=100   # Default: 100

# Default execution timeout in seconds
EXECUTION_TIMEOUT_SECONDS=3600  # Default: 3600 (1 hour)

# Agent pool size
AGENT_POOL_SIZE=5          # Default: 5

# Agent timeout in seconds
AGENT_TIMEOUT_SECONDS=300   # Default: 300 (5 minutes)
```

### Health Check Configuration

```bash
# Health check interval in seconds
HEALTH_CHECK_INTERVAL_SECONDS=30    # Default: 30

# Status update interval in seconds
STATUS_UPDATE_INTERVAL_SECONDS=10   # Default: 10

# Stuck execution timeout in minutes
STUCK_EXECUTION_TIMEOUT_MINUTES=60  # Default: 60
```

### CMS Configuration

For Directus CMS integration (if used).

```bash
# Directus admin credentials
DIRECTUS_ADMIN_EMAIL=admin@example.com
DIRECTUS_ADMIN_PASSWORD=your_directus_admin_password

# Directus database password
DIRECTUS_DB_PASSWORD=your_directus_db_password

# Directus URL
DIRECTUS_URL=http://localhost:8055
```

## Environment File Setup

### Creating Your .env File

1. Copy the example file:
   ```bash
   cp .env.example .env
   ```

2. Edit the `.env` file with your actual values:
   ```bash
   nano .env  # or your preferred editor
   ```

3. Set appropriate file permissions:
   ```bash
   chmod 600 .env  # Read/write for owner only
   ```

### .env File Template

```bash
# Beast Mode AI Development Framework Configuration
# Copy this file to .env and fill in your actual values

# ============================================================================
# REQUIRED CONFIGURATION
# ============================================================================

# Redis Configuration (Required)
REDIS_PASSWORD=your_secure_redis_password_here
REDIS_HOST=localhost
REDIS_PORT=6379

# AI API Keys (At least one required)
OPENAI_API_KEY=sk-your_openai_api_key_here
ANTHROPIC_API_KEY=your_anthropic_api_key_here

# ============================================================================
# OPTIONAL CONFIGURATION
# ============================================================================

# Application Settings
DEBUG=false
ENVIRONMENT=development
LOG_LEVEL=INFO

# Database Configuration (if using database features)
DATABASE_PASSWORD=your_database_password_here
DATABASE_URL=postgresql://user:password@localhost:5432/beast_mode

# Performance Settings
MAX_CONCURRENT_TASKS=10
CONTEXT_CACHE_SIZE_MB=100
EXECUTION_TIMEOUT_SECONDS=3600

# Health Check Settings
HEALTH_CHECK_INTERVAL_SECONDS=30
STATUS_UPDATE_INTERVAL_SECONDS=10

# CMS Configuration (if using Directus)
DIRECTUS_ADMIN_EMAIL=admin@example.com
DIRECTUS_ADMIN_PASSWORD=your_directus_admin_password
DIRECTUS_DB_PASSWORD=your_directus_db_password
DIRECTUS_URL=http://localhost:8055

# ============================================================================
# SECURITY NOTES
# ============================================================================
# - Never commit this file to version control
# - Use strong, unique passwords for all services
# - Rotate credentials regularly
# - Use different credentials for different environments
```

## Environment-Specific Configuration

### Development Environment

```bash
# Development settings
ENVIRONMENT=development
DEBUG=true
LOG_LEVEL=DEBUG

# Local services
REDIS_HOST=localhost
DATABASE_HOST=localhost
DIRECTUS_URL=http://localhost:8055

# Relaxed timeouts for debugging
EXECUTION_TIMEOUT_SECONDS=7200
AGENT_TIMEOUT_SECONDS=600
```

### Staging Environment

```bash
# Staging settings
ENVIRONMENT=staging
DEBUG=false
LOG_LEVEL=INFO

# Staging services
REDIS_HOST=staging-redis.example.com
DATABASE_HOST=staging-db.example.com
DIRECTUS_URL=https://staging-cms.example.com

# Production-like timeouts
EXECUTION_TIMEOUT_SECONDS=3600
AGENT_TIMEOUT_SECONDS=300
```

### Production Environment

```bash
# Production settings
ENVIRONMENT=production
DEBUG=false
LOG_LEVEL=WARNING

# Production services
REDIS_HOST=prod-redis.example.com
DATABASE_HOST=prod-db.example.com
DIRECTUS_URL=https://cms.example.com

# Optimized performance settings
MAX_CONCURRENT_TASKS=20
CONTEXT_CACHE_SIZE_MB=500
EXECUTION_TIMEOUT_SECONDS=3600

# Frequent health checks
HEALTH_CHECK_INTERVAL_SECONDS=15
STATUS_UPDATE_INTERVAL_SECONDS=5
```

## Loading Environment Variables

### Automatic Loading

The framework automatically loads environment variables from:

1. System environment variables
2. `~/.env` file (user-specific)
3. `.env` file in project root

### Manual Loading

```python
import os
from pathlib import Path

def load_env_vars():
    """Load environment variables from ~/.env if it exists."""
    home_env = Path.home() / ".env"
    if home_env.exists():
        with open(home_env, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    os.environ[key.strip()] = value.strip().strip('"').strip("'")

# Load at application startup
load_env_vars()
```

### Validation

```python
def validate_required_env_vars():
    """Validate all required environment variables are set."""
    required_vars = [
        'REDIS_PASSWORD',
        ('OPENAI_API_KEY', 'ANTHROPIC_API_KEY'),  # At least one required
    ]
    
    missing_vars = []
    
    for var in required_vars:
        if isinstance(var, tuple):
            # At least one of these must be set
            if not any(os.getenv(v) for v in var):
                missing_vars.append(f"One of: {', '.join(var)}")
        else:
            # This specific variable must be set
            if not os.getenv(var):
                missing_vars.append(var)
    
    if missing_vars:
        raise ValueError(
            f"Missing required environment variables:\n"
            f"{chr(10).join(f'  - {var}' for var in missing_vars)}\n"
            f"Please set these in your .env file or environment"
        )

# Validate at startup
validate_required_env_vars()
```

## Security Best Practices

### 1. Strong Passwords

```bash
# Generate secure passwords
openssl rand -base64 32  # For Redis password
openssl rand -base64 32  # For database password
```

### 2. File Permissions

```bash
# Secure .env file permissions
chmod 600 .env           # Read/write for owner only
chown $USER:$USER .env   # Ensure correct ownership
```

### 3. Git Configuration

Ensure `.env` files are never committed:

```bash
# Add to .gitignore
echo ".env" >> .gitignore
echo "*.env" >> .gitignore
echo ".env.*" >> .gitignore

# Remove if accidentally committed
git rm --cached .env
git commit -m "Remove .env file from tracking"
```

### 4. Environment Separation

Use different credentials for each environment:

```bash
# Development
REDIS_PASSWORD=dev_redis_password_123

# Staging  
REDIS_PASSWORD=staging_redis_password_456

# Production
REDIS_PASSWORD=prod_redis_password_789
```

### 5. Credential Rotation

Regularly rotate sensitive credentials:

```bash
# Generate new password
NEW_PASSWORD=$(openssl rand -base64 32)

# Update Redis password
redis-cli CONFIG SET requirepass $NEW_PASSWORD

# Update environment variable
sed -i "s/REDIS_PASSWORD=.*/REDIS_PASSWORD=$NEW_PASSWORD/" .env
```

## Docker Configuration

### Docker Compose

```yaml
# docker-compose.yml
version: '3.8'

services:
  beast-mode:
    build: .
    environment:
      # Load from .env file
      - REDIS_PASSWORD=${REDIS_PASSWORD}
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - ANTHROPIC_API_KEY=${ANTHROPIC_API_KEY}
      - DATABASE_PASSWORD=${DATABASE_PASSWORD}
      - ENVIRONMENT=${ENVIRONMENT:-production}
      - DEBUG=${DEBUG:-false}
    env_file:
      - .env  # Load additional variables from .env
    depends_on:
      - redis
      - postgres

  redis:
    image: redis:7-alpine
    command: redis-server --requirepass ${REDIS_PASSWORD}
    environment:
      - REDIS_PASSWORD=${REDIS_PASSWORD}

  postgres:
    image: postgres:15-alpine
    environment:
      - POSTGRES_PASSWORD=${DATABASE_PASSWORD}
      - POSTGRES_DB=beast_mode
```

### Dockerfile

```dockerfile
FROM python:3.11-slim

# Install dependencies
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copy application code
COPY src/ /app/src/
WORKDIR /app

# Environment variables will be provided at runtime
# NEVER include credentials in Docker images

# Run application
CMD ["python", "-m", "src.main"]
```

## Kubernetes Configuration

### Secret Management

```yaml
# kubernetes-secrets.yaml
apiVersion: v1
kind: Secret
metadata:
  name: beast-mode-secrets
type: Opaque
data:
  redis-password: <base64-encoded-redis-password>
  openai-api-key: <base64-encoded-openai-key>
  anthropic-api-key: <base64-encoded-anthropic-key>
  database-password: <base64-encoded-db-password>
```

### ConfigMap for Non-Sensitive Config

```yaml
# kubernetes-config.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: beast-mode-config
data:
  ENVIRONMENT: "production"
  DEBUG: "false"
  LOG_LEVEL: "INFO"
  MAX_CONCURRENT_TASKS: "20"
  CONTEXT_CACHE_SIZE_MB: "500"
  REDIS_HOST: "redis-service"
  DATABASE_HOST: "postgres-service"
```

### Deployment Configuration

```yaml
# kubernetes-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: beast-mode-app
spec:
  replicas: 3
  selector:
    matchLabels:
      app: beast-mode
  template:
    metadata:
      labels:
        app: beast-mode
    spec:
      containers:
      - name: beast-mode
        image: beast-mode:latest
        env:
        # Load from ConfigMap
        - name: ENVIRONMENT
          valueFrom:
            configMapKeyRef:
              name: beast-mode-config
              key: ENVIRONMENT
        - name: DEBUG
          valueFrom:
            configMapKeyRef:
              name: beast-mode-config
              key: DEBUG
        # Load from Secret
        - name: REDIS_PASSWORD
          valueFrom:
            secretKeyRef:
              name: beast-mode-secrets
              key: redis-password
        - name: OPENAI_API_KEY
          valueFrom:
            secretKeyRef:
              name: beast-mode-secrets
              key: openai-api-key
        - name: ANTHROPIC_API_KEY
          valueFrom:
            secretKeyRef:
              name: beast-mode-secrets
              key: anthropic-api-key
        - name: DATABASE_PASSWORD
          valueFrom:
            secretKeyRef:
              name: beast-mode-secrets
              key: database-password
```

## Troubleshooting

### Common Issues

1. **Missing Environment Variables**
   ```bash
   # Check if variable is set
   echo $REDIS_PASSWORD
   
   # List all environment variables
   env | grep -E "(REDIS|OPENAI|ANTHROPIC)"
   ```

2. **Permission Denied on .env File**
   ```bash
   # Fix file permissions
   chmod 600 .env
   chown $USER:$USER .env
   ```

3. **Environment Variables Not Loading**
   ```python
   # Debug environment loading
   import os
   print("REDIS_PASSWORD set:", bool(os.getenv('REDIS_PASSWORD')))
   print("OPENAI_API_KEY set:", bool(os.getenv('OPENAI_API_KEY')))
   ```

4. **Invalid Credentials**
   ```bash
   # Test Redis connection
   redis-cli -h $REDIS_HOST -p $REDIS_PORT -a $REDIS_PASSWORD ping
   
   # Test API key (OpenAI example)
   curl -H "Authorization: Bearer $OPENAI_API_KEY" \
        https://api.openai.com/v1/models
   ```

### Validation Script

```python
#!/usr/bin/env python3
"""Environment validation script."""

import os
import sys
from pathlib import Path

def validate_environment():
    """Validate environment configuration."""
    errors = []
    warnings = []
    
    # Check required variables
    required_vars = {
        'REDIS_PASSWORD': 'Redis authentication password',
    }
    
    for var, description in required_vars.items():
        if not os.getenv(var):
            errors.append(f"Missing {var}: {description}")
    
    # Check at least one AI API key
    ai_keys = ['OPENAI_API_KEY', 'ANTHROPIC_API_KEY']
    if not any(os.getenv(key) for key in ai_keys):
        errors.append(f"Missing AI API key: At least one of {', '.join(ai_keys)} required")
    
    # Check optional but recommended variables
    recommended_vars = {
        'ENVIRONMENT': 'Environment designation (development/staging/production)',
        'LOG_LEVEL': 'Logging level (DEBUG/INFO/WARNING/ERROR)',
    }
    
    for var, description in recommended_vars.items():
        if not os.getenv(var):
            warnings.append(f"Missing {var}: {description}")
    
    # Check .env file exists
    env_file = Path('.env')
    if not env_file.exists():
        warnings.append("No .env file found - using system environment variables only")
    else:
        # Check .env file permissions
        stat = env_file.stat()
        if stat.st_mode & 0o077:  # Check if group/other have any permissions
            warnings.append(".env file has overly permissive permissions - run: chmod 600 .env")
    
    # Report results
    if errors:
        print("❌ Environment validation failed:")
        for error in errors:
            print(f"  - {error}")
        print("\nPlease fix these issues and try again.")
        return False
    
    if warnings:
        print("⚠️  Environment validation warnings:")
        for warning in warnings:
            print(f"  - {warning}")
    
    print("✅ Environment validation passed")
    return True

if __name__ == '__main__':
    if not validate_environment():
        sys.exit(1)
```

Run the validation script:

```bash
python validate_env.py
```

---

**Next**: [Deployment Configuration](./deployment.md) | **Up**: [Configuration Guide](./)