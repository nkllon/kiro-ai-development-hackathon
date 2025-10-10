# Configuration Management API

## Overview

The Beast Mode AI Development Framework uses environment-based configuration management to ensure secure credential handling and flexible deployment options. All sensitive data is managed through environment variables, never hardcoded in source code.

## Security Principles

⚠️ **CRITICAL SECURITY REQUIREMENT**: Never hardcode passwords, API keys, tokens, or any credentials in source code. This is a zero-tolerance security violation.

## Location

```python
from src.security.secure_credentials import get_secure_credentials
```

## Core Functions

### `get_secure_credentials(strict_mode: bool = True) -> SecureCredentials`

Returns a secure credentials manager that loads configuration from environment variables.

```python
from src.security.secure_credentials import get_secure_credentials

# Get credentials manager
creds = get_secure_credentials(strict_mode=False)

# Get Redis configuration
redis_config = creds.get_redis_config()
print(f"Redis host: {redis_config['host']}")
print(f"Redis port: {redis_config['port']}")
# Password is securely loaded from environment
```

**Parameters:**
- `strict_mode` (bool): If True, raises exceptions for missing credentials. If False, provides defaults where safe.

**Returns:** `SecureCredentials` instance with methods for accessing configuration.

## SecureCredentials Class

### Methods

#### `get_redis_config() -> Dict[str, Any]`

Returns Redis connection configuration.

```python
redis_config = creds.get_redis_config()
# Returns:
# {
#     'host': 'localhost',  # from REDIS_HOST or default
#     'port': 6379,         # from REDIS_PORT or default
#     'password': '...',    # from REDIS_PASSWORD (required)
#     'db': 0
# }
```

**Environment Variables:**
- `REDIS_HOST` (optional): Redis server hostname (default: localhost)
- `REDIS_PORT` (optional): Redis server port (default: 6379)
- `REDIS_PASSWORD` (required): Redis authentication password

#### `get_api_keys() -> Dict[str, str]`

Returns API keys for external services.

```python
api_keys = creds.get_api_keys()
# Returns:
# {
#     'openai': '...',      # from OPENAI_API_KEY
#     'anthropic': '...',   # from ANTHROPIC_API_KEY
#     'google': '...'       # from GOOGLE_API_KEY
# }
```

**Environment Variables:**
- `OPENAI_API_KEY`: OpenAI API key
- `ANTHROPIC_API_KEY`: Anthropic API key
- `GOOGLE_API_KEY`: Google API key

#### `get_database_config() -> Dict[str, Any]`

Returns database connection configuration.

```python
db_config = creds.get_database_config()
# Returns:
# {
#     'url': 'postgresql://...',  # from DATABASE_URL
#     'password': '...',          # from DATABASE_PASSWORD
#     'host': 'localhost',        # from DATABASE_HOST
#     'port': 5432,              # from DATABASE_PORT
#     'name': 'mydb'             # from DATABASE_NAME
# }
```

**Environment Variables:**
- `DATABASE_URL`: Complete database connection URL
- `DATABASE_PASSWORD`: Database password
- `DATABASE_HOST`: Database hostname
- `DATABASE_PORT`: Database port
- `DATABASE_NAME`: Database name

## Environment Variable Patterns

### Required Pattern

All components must use environment variables for sensitive configuration:

```python
import os

# ✅ CORRECT: Use environment variables
def get_secure_credential(env_var_name: str, description: str) -> str:
    """Get credential from environment with helpful error messages."""
    credential = os.getenv(env_var_name)
    if not credential:
        raise ValueError(
            f"{description} not found. "
            f"Please set {env_var_name} in ~/.env or environment variables"
        )
    return credential

# Usage
redis_password = get_secure_credential('REDIS_PASSWORD', 'Redis password')
api_key = get_secure_credential('OPENAI_API_KEY', 'OpenAI API key')
```

### Environment Variable Loading

Components should load environment variables from `~/.env` file:

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

# Load environment variables at module initialization
load_env_vars()
```

### Configuration Class Pattern

Use dataclasses for structured configuration:

```python
import os
from dataclasses import dataclass, field
from typing import Optional

@dataclass
class SecureConfig:
    """Secure configuration using environment variables only."""
    
    # Redis Configuration
    redis_host: str = field(default_factory=lambda: os.getenv('REDIS_HOST', 'localhost'))
    redis_port: int = field(default_factory=lambda: int(os.getenv('REDIS_PORT', '6379')))
    redis_password: str = field(default_factory=lambda: os.getenv('REDIS_PASSWORD', ''))
    
    # API Keys
    openai_api_key: str = field(default_factory=lambda: os.getenv('OPENAI_API_KEY', ''))
    anthropic_api_key: str = field(default_factory=lambda: os.getenv('ANTHROPIC_API_KEY', ''))
    
    # Application Settings
    debug: bool = field(default_factory=lambda: os.getenv('DEBUG', 'false').lower() == 'true')
    environment: str = field(default_factory=lambda: os.getenv('ENVIRONMENT', 'development'))
    log_level: str = field(default_factory=lambda: os.getenv('LOG_LEVEL', 'INFO'))
    
    def __post_init__(self):
        """Validate required configuration."""
        if not self.redis_password:
            raise ValueError("REDIS_PASSWORD environment variable is required")
        
        if not self.openai_api_key and not self.anthropic_api_key:
            raise ValueError("At least one AI API key (OPENAI_API_KEY or ANTHROPIC_API_KEY) is required")

# Usage
config = SecureConfig()
```

## Environment File Structure

### `.env` File Template

```bash
# ~/.env - NEVER commit this file to version control

# Redis Configuration
REDIS_PASSWORD=your_actual_redis_password_here
REDIS_HOST=192.168.1.119
REDIS_PORT=6379

# API Keys
OPENAI_API_KEY=sk-your_actual_openai_key_here
ANTHROPIC_API_KEY=your_actual_anthropic_key_here

# Database Configuration
DATABASE_PASSWORD=your_actual_database_password
DATABASE_URL=postgresql://user:${DATABASE_PASSWORD}@localhost:5432/dbname

# Application Configuration
DEBUG=false
ENVIRONMENT=production
LOG_LEVEL=INFO

# Directus CMS Configuration
DIRECTUS_ADMIN_PASSWORD=your_directus_admin_password
DIRECTUS_DB_PASSWORD=your_directus_db_password
DIRECTUS_URL=http://localhost:8055
DIRECTUS_ADMIN_EMAIL=admin@example.com

# Performance Configuration
MAX_CONCURRENT_TASKS=10
CONTEXT_CACHE_SIZE_MB=100
EXECUTION_TIMEOUT_SECONDS=3600
```

### `.env.example` File

```bash
# Environment Variables Template
# Copy this file to .env and fill in your actual values

# Redis Configuration
REDIS_PASSWORD=your_redis_password_here
REDIS_HOST=localhost
REDIS_PORT=6379

# API Keys (replace with your actual keys)
OPENAI_API_KEY=your_openai_api_key_here
ANTHROPIC_API_KEY=your_anthropic_api_key_here

# Database Configuration
DATABASE_PASSWORD=your_database_password_here
DATABASE_URL=postgresql://user:password@localhost:5432/dbname

# Application Configuration
DEBUG=false
ENVIRONMENT=development

# Security Note: Never commit the actual .env file to version control
# Add .env to your .gitignore file
```

## Component Integration Examples

### Redis Connection

```python
from src.security.secure_credentials import get_secure_credentials
import redis.asyncio as redis

class RedisComponent:
    def __init__(self):
        # ✅ SECURE: Use secure credentials helper
        creds = get_secure_credentials(strict_mode=False)
        redis_config = creds.get_redis_config()
        
        self.redis_host = redis_config['host']
        self.redis_port = redis_config['port']
        self.redis_password = redis_config['password']
        
        if not self.redis_password:
            raise ValueError("Redis password must be set in environment variables")
    
    async def connect(self):
        self.redis_client = redis.Redis(
            host=self.redis_host,
            port=self.redis_port,
            password=self.redis_password,
            decode_responses=True
        )
```

### API Client Configuration

```python
from src.security.secure_credentials import get_secure_credentials
import openai

class AIClient:
    def __init__(self):
        # ✅ SECURE: Use secure credentials helper
        creds = get_secure_credentials()
        api_keys = creds.get_api_keys()
        
        self.openai_key = api_keys.get('openai')
        self.anthropic_key = api_keys.get('anthropic')
        
        if not self.openai_key and not self.anthropic_key:
            raise ValueError("At least one AI API key must be configured")
    
    def get_openai_client(self):
        if not self.openai_key:
            raise ValueError("OpenAI API key not configured")
        
        return openai.OpenAI(api_key=self.openai_key)
```

### Database Configuration

```python
from src.security.secure_credentials import get_secure_credentials
import asyncpg

class DatabaseManager:
    def __init__(self):
        # ✅ SECURE: Use secure credentials helper
        creds = get_secure_credentials()
        db_config = creds.get_database_config()
        
        self.database_url = db_config['url']
        
        if not self.database_url:
            raise ValueError("Database URL must be configured")
    
    async def connect(self):
        self.connection = await asyncpg.connect(self.database_url)
```

## Anti-Patterns (FORBIDDEN)

### ❌ Hardcoded Credentials

```python
# NEVER DO THIS - SECURITY VIOLATION
redis_password = "beastmode2025"
api_key = "sk-1234567890abcdef"
database_url = "postgresql://user:password@host:5432/db"
```

### ❌ Default Credential Values

```python
# NEVER DO THIS - SECURITY RISK
password = os.getenv('PASSWORD', 'default_password')
api_key = os.getenv('API_KEY', 'fallback_key')
```

### ❌ Credentials in Configuration Files

```json
// NEVER DO THIS
{
  "redis_password": "beastmode2025",
  "api_key": "secret_key_here"
}
```

### ❌ Credentials in Comments or Documentation

```python
# NEVER DO THIS
# Default password is: beastmode2025
# API key for testing: sk-1234567890abcdef
```

## Validation and Error Handling

### Environment Variable Validation

```python
def validate_environment():
    """Validate all required environment variables are set."""
    required_vars = [
        'REDIS_PASSWORD',
        'OPENAI_API_KEY',
        'DATABASE_PASSWORD'
    ]
    
    missing_vars = []
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        raise ValueError(
            f"Missing required environment variables: {', '.join(missing_vars)}\n"
            f"Please set these in your ~/.env file or environment"
        )

# Validate at application startup
validate_environment()
```

### Graceful Error Messages

```python
def get_credential_with_help(env_var: str, service_name: str) -> str:
    """Get credential with helpful error message."""
    credential = os.getenv(env_var)
    if not credential:
        raise ValueError(
            f"{service_name} credential not found.\n"
            f"Please set {env_var} in your ~/.env file:\n"
            f"echo '{env_var}=your_actual_key_here' >> ~/.env"
        )
    return credential
```

## Testing Configuration

### Test Environment Setup

```python
import os
import pytest
from unittest.mock import patch

@pytest.fixture
def test_env():
    """Set up test environment variables."""
    test_vars = {
        'REDIS_PASSWORD': 'test_redis_password',
        'OPENAI_API_KEY': 'test_openai_key',
        'DATABASE_PASSWORD': 'test_db_password',
        'ENVIRONMENT': 'test'
    }
    
    with patch.dict(os.environ, test_vars):
        yield test_vars

def test_secure_credentials(test_env):
    """Test secure credentials loading."""
    creds = get_secure_credentials(strict_mode=False)
    redis_config = creds.get_redis_config()
    
    assert redis_config['password'] == 'test_redis_password'
    assert redis_config['host'] == 'localhost'  # default
    assert redis_config['port'] == 6379  # default
```

## Deployment Considerations

### Production Environment

```bash
# Production environment variables
export REDIS_PASSWORD="$(openssl rand -base64 32)"
export OPENAI_API_KEY="sk-prod-key-here"
export DATABASE_PASSWORD="$(openssl rand -base64 32)"
export ENVIRONMENT="production"
export DEBUG="false"
export LOG_LEVEL="WARNING"
```

### Docker Configuration

```dockerfile
# Dockerfile
FROM python:3.11-slim

# Install dependencies
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copy application
COPY src/ /app/src/
WORKDIR /app

# Environment variables will be provided at runtime
# NEVER include credentials in Docker images
CMD ["python", "-m", "src.main"]
```

```yaml
# docker-compose.yml
version: '3.8'
services:
  app:
    build: .
    environment:
      - REDIS_PASSWORD=${REDIS_PASSWORD}
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - DATABASE_PASSWORD=${DATABASE_PASSWORD}
    env_file:
      - .env  # Load from .env file (not committed to git)
```

### Kubernetes Configuration

```yaml
# kubernetes-secret.yaml
apiVersion: v1
kind: Secret
metadata:
  name: app-secrets
type: Opaque
data:
  redis-password: <base64-encoded-password>
  openai-api-key: <base64-encoded-key>
  database-password: <base64-encoded-password>
```

```yaml
# kubernetes-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: beast-mode-app
spec:
  template:
    spec:
      containers:
      - name: app
        image: beast-mode:latest
        env:
        - name: REDIS_PASSWORD
          valueFrom:
            secretKeyRef:
              name: app-secrets
              key: redis-password
        - name: OPENAI_API_KEY
          valueFrom:
            secretKeyRef:
              name: app-secrets
              key: openai-api-key
```

## Best Practices Summary

1. **Never hardcode credentials** - Always use environment variables
2. **Validate early** - Check required environment variables at startup
3. **Provide helpful errors** - Guide users on how to set missing variables
4. **Use structured configuration** - Implement configuration classes with validation
5. **Load from ~/.env** - Support local development with environment files
6. **Secure defaults** - Never provide default values for sensitive credentials
7. **Document requirements** - Clearly document all required environment variables
8. **Test configuration** - Include configuration testing in your test suite

---

**Next**: [Error Handling](./error-handling.md) | **Up**: [Core APIs](../core/)