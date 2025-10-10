# Credential Management Security Guide

## Overview

This document establishes the **zero-tolerance policy** for hardcoded credentials in the Beast Mode AI Development Framework. All credentials, API keys, passwords, and sensitive configuration must use environment variables or secure credential management systems.

## Zero Tolerance Policy

**NEVER hardcode passwords, API keys, tokens, or any credentials in source code, configuration files, or documentation.**

This is a critical security violation with zero tolerance. Any hardcoded credentials will result in:
- Immediate build failure
- Security incident response
- Mandatory credential rotation
- Code review rejection

## Critical Security Requirements

### Prohibited Practices ❌

```python
# NEVER DO THIS - Hardcoded credentials
redis_password = "beastmode2025"
api_key = "sk-1234567890abcdef"
database_url = "postgresql://user:password@host:5432/db"

# NEVER DO THIS - Default credential values
password = os.getenv('PASSWORD', 'default_password')
api_key = os.getenv('API_KEY', 'fallback_key')
```

### Required Practices ✅

```python
# ALWAYS DO THIS - Environment variables with validation
import os

def load_secure_config():
    redis_password = os.getenv('REDIS_PASSWORD')
    if not redis_password:
        raise ValueError("REDIS_PASSWORD environment variable is required")
    return redis_password

# ALWAYS DO THIS - Secure configuration class
@dataclass
class SecureConfig:
    redis_password: str = field(default_factory=lambda: os.getenv('REDIS_PASSWORD', ''))
    
    def __post_init__(self):
        if not self.redis_password:
            raise ValueError("REDIS_PASSWORD must be set in environment")
```

## Environment Variable Management

### Setting Environment Variables

Create a `~/.env` file for local development:

```bash
# ~/.env - NEVER commit this file
REDIS_PASSWORD=your_actual_password_here
OPENAI_API_KEY=sk-your_openai_key_here
ANTHROPIC_API_KEY=your_anthropic_key_here
DATABASE_PASSWORD=your_db_password_here
```

### Loading Environment Variables

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
```## Sec
ure Configuration Patterns

### Pattern 1: Validated Environment Variables

```python
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
```

### Pattern 2: Configuration Classes

```python
@dataclass
class DatabaseConfig:
    """Secure database configuration."""
    host: str = field(default_factory=lambda: os.getenv('DB_HOST', 'localhost'))
    port: int = field(default_factory=lambda: int(os.getenv('DB_PORT', '5432')))
    password: str = field(default_factory=lambda: os.getenv('DB_PASSWORD', ''))
    
    def __post_init__(self):
        if not self.password:
            raise ValueError("DB_PASSWORD environment variable is required")
```

### Pattern 3: Graceful Error Handling

```python
def connect_to_redis():
    """Connect to Redis with secure credential handling."""
    try:
        password = get_secure_credential('REDIS_PASSWORD', 'Redis password')
        return redis.Redis(host='localhost', port=6379, password=password)
    except ValueError as e:
        logger.error(f"Redis connection failed: {e}")
        logger.info("Please set REDIS_PASSWORD in ~/.env file")
        raise
```

## Security Validation

### Automated Scanning

The repository includes automated security scanning:

```bash
# Run comprehensive security validation
python scripts/comprehensive_security_validator.py

# Run configuration compliance validation
python scripts/configuration_compliance_validator.py
```

### Pre-commit Hooks

Security validation is enforced through pre-commit hooks:

```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/Yelp/detect-secrets
    rev: v1.4.0
    hooks:
      - id: detect-secrets
        args: ['--baseline', '.secrets.baseline']
```

### CI/CD Integration

All builds include mandatory security scanning:

```yaml
# .github/workflows/security.yml
- name: Security Scan
  run: |
    python scripts/comprehensive_security_validator.py
    if [ $? -ne 0 ]; then
      echo "Security scan failed - hardcoded credentials detected"
      exit 1
    fi
```

## Credential Types and Handling

### Database Credentials

```python
# Environment variables
DB_HOST=localhost
DB_PORT=5432
DB_NAME=beastmode
DB_USER=beastmode_user
DB_PASSWORD=secure_password_here

# Usage
database_config = {
    'host': os.getenv('DB_HOST'),
    'port': int(os.getenv('DB_PORT', '5432')),
    'database': os.getenv('DB_NAME'),
    'user': os.getenv('DB_USER'),
    'password': get_secure_credential('DB_PASSWORD', 'Database password')
}
```### API 
Keys

```python
# Environment variables
OPENAI_API_KEY=sk-your_openai_key_here
ANTHROPIC_API_KEY=your_anthropic_key_here
GITHUB_TOKEN=ghp_your_github_token_here

# Usage
openai_client = OpenAI(
    api_key=get_secure_credential('OPENAI_API_KEY', 'OpenAI API key')
)
```

### Redis Credentials

```python
# Environment variables
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_PASSWORD=your_redis_password_here

# Usage
redis_client = redis.Redis(
    host=os.getenv('REDIS_HOST', 'localhost'),
    port=int(os.getenv('REDIS_PORT', '6379')),
    password=get_secure_credential('REDIS_PASSWORD', 'Redis password')
)
```

### Cloud Service Credentials

```python
# Environment variables
AWS_ACCESS_KEY_ID=your_access_key
AWS_SECRET_ACCESS_KEY=your_secret_key
GCP_SERVICE_ACCOUNT_KEY=path/to/service-account.json

# Usage
aws_session = boto3.Session(
    aws_access_key_id=get_secure_credential('AWS_ACCESS_KEY_ID', 'AWS Access Key'),
    aws_secret_access_key=get_secure_credential('AWS_SECRET_ACCESS_KEY', 'AWS Secret Key')
)
```

## Example Configuration Files

### .env.example Template

```bash
# Beast Mode AI Development Framework - Environment Variables Template
# Copy this file to ~/.env and fill in your actual values

# Redis Configuration
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_PASSWORD=your_redis_password_here

# API Keys
OPENAI_API_KEY=sk-your_openai_key_here
ANTHROPIC_API_KEY=your_anthropic_key_here

# Database Configuration
DB_HOST=localhost
DB_PORT=5432
DB_NAME=beastmode
DB_USER=beastmode_user
DB_PASSWORD=your_database_password_here

# Cloud Services
AWS_ACCESS_KEY_ID=your_aws_access_key
AWS_SECRET_ACCESS_KEY=your_aws_secret_key
GCP_PROJECT_ID=your_gcp_project_id

# Application Configuration
ENVIRONMENT=development
DEBUG=true
LOG_LEVEL=INFO
```

### Docker Environment File

```bash
# docker.env.example - For Docker deployments
# Copy to docker.env and customize

REDIS_PASSWORD=secure_redis_password
OPENAI_API_KEY=sk-your_key_here
DB_PASSWORD=secure_db_password
```

## Security Incident Response

### When Hardcoded Credentials Are Found

1. **IMMEDIATE ACTION**: Remove credentials from code
2. **CREDENTIAL ROTATION**: Change all potentially exposed credentials
3. **ENVIRONMENT VARIABLES**: Convert to secure environment variable usage
4. **GIT HISTORY**: Consider rewriting git history if credentials were committed
5. **SECURITY REVIEW**: Assess potential exposure and impact

### Emergency Response Protocol

```bash
# 1. Stop all services immediately
docker-compose down

# 2. Rotate all credentials
# - Change Redis password
# - Regenerate API keys
# - Update database passwords

# 3. Update environment variables
# Edit ~/.env with new credentials

# 4. Restart services with new credentials
docker-compose up -d
```## D
evelopment Workflow

### Setting Up Development Environment

1. **Clone Repository**
   ```bash
   git clone <repository-url>
   cd beast-mode-framework
   ```

2. **Create Environment File**
   ```bash
   cp .env.example ~/.env
   # Edit ~/.env with your actual credentials
   ```

3. **Validate Security**
   ```bash
   python scripts/comprehensive_security_validator.py
   ```

4. **Install and Run**
   ```bash
   ./install.sh
   python examples/quick_start/basic_example.py
   ```

### Code Review Checklist

- [ ] No hardcoded credentials in any files
- [ ] All sensitive configuration uses environment variables
- [ ] Environment variables are validated before use
- [ ] Helpful error messages for missing credentials
- [ ] .env.example updated with new variables
- [ ] Security scan passes

### Testing with Credentials

```python
# Use mock credentials for testing
import unittest.mock

class TestSecureFeature(unittest.TestCase):
    @unittest.mock.patch.dict(os.environ, {
        'REDIS_PASSWORD': 'test_password',
        'OPENAI_API_KEY': 'test_key'
    })
    def test_secure_connection(self):
        # Test code here
        pass
```

## Compliance and Regulatory Requirements

### Regulatory Standards

- **GDPR**: Adequate security measures for personal data
- **SOC 2**: Proper credential protection and access controls
- **PCI DSS**: Secure credential storage and transmission
- **HIPAA**: Safeguards for system access credentials

### Audit Requirements

- All credentials must use environment variables
- No hardcoded secrets in version control
- Automated security scanning in CI/CD
- Regular credential rotation procedures
- Incident response documentation

## Tools and Automation

### Security Scanning Tools

```bash
# Comprehensive security validator
python scripts/comprehensive_security_validator.py

# Configuration compliance validator
python scripts/configuration_compliance_validator.py

# Detect secrets (pre-commit hook)
detect-secrets scan --baseline .secrets.baseline
```

### Automated Remediation

```bash
# Emergency credential cleanup
python scripts/emergency_security_cleanup.py

# Validate all examples work with environment variables
python scripts/example_validator.py --security-check
```

## Success Metrics

### Security Compliance Targets

- **Zero hardcoded credentials** in entire codebase
- **100% environment variable usage** for sensitive data
- **Automated scanning** catches all credential patterns
- **Regular security audits** validate compliance
- **Developer training** on secure practices

### Monitoring and Alerting

- Pre-commit hooks prevent credential commits
- CI/CD builds fail on security violations
- Regular automated security scans
- Incident response procedures documented
- Security metrics tracked and reported

## Conclusion

The Beast Mode AI Development Framework maintains a **zero-tolerance policy** for hardcoded credentials. This comprehensive credential management system ensures:

- **Security**: All credentials are properly protected
- **Compliance**: Meets regulatory and industry standards
- **Usability**: Clear patterns and helpful error messages
- **Automation**: Automated validation and enforcement
- **Documentation**: Complete guidance for developers

Remember: **Security is not optional. Credentials are never hardcoded. Environment variables are mandatory.**