# Security Guidelines

## Overview

This document outlines security best practices for the Beast Mode AI Development Framework. Following these guidelines ensures secure deployment and operation of the system.

## Credential Management

### Environment Variables

**NEVER** hardcode credentials in source code. Always use environment variables:

```python
import os

# ✅ CORRECT - Use environment variables
redis_password = os.getenv('REDIS_PASSWORD')
api_key = os.getenv('OPENAI_API_KEY')
database_url = os.getenv('DATABASE_URL')

# ❌ WRONG - Never hardcode credentials
redis_password = "my_secret_password"
api_key = "sk-1234567890abcdef"
```

### Environment File Setup

1. Copy the example environment file:
   ```bash
   cp .env.example .env
   ```

2. Edit `.env` with your actual credentials:
   ```bash
   # Redis Configuration
   REDIS_PASSWORD=your_actual_redis_password
   REDIS_HOST=localhost
   REDIS_PORT=6379
   
   # API Keys
   OPENAI_API_KEY=your_actual_openai_key
   ANTHROPIC_API_KEY=your_actual_anthropic_key
   
   # Database Configuration
   DATABASE_URL=postgresql://user:password@localhost:5432/dbname
   ```

3. **IMPORTANT**: Never commit `.env` to version control. It's already in `.gitignore`.

## Required Environment Variables

### Core System
- `REDIS_PASSWORD` - Redis authentication password
- `REDIS_HOST` - Redis server hostname (default: localhost)
- `REDIS_PORT` - Redis server port (default: 6379)

### AI Services
- `OPENAI_API_KEY` - OpenAI API key for GPT models
- `ANTHROPIC_API_KEY` - Anthropic API key for Claude models

### Database
- `DATABASE_URL` - PostgreSQL connection string
- `DATABASE_PASSWORD` - Database password (if not in URL)

### Optional Configuration
- `DEBUG` - Enable debug mode (default: false)
- `ENVIRONMENT` - Deployment environment (development/production)

## Security Validation

### Automated Scanning

Run security scans before deployment:

```bash
# Scan for hardcoded credentials
python scripts/security_credential_scanner.py

# Run security cleanup if issues found
python scripts/security_cleanup_executor.py
```

### Manual Review Checklist

Before deploying or sharing code:

- [ ] No hardcoded passwords, API keys, or tokens
- [ ] All credentials use environment variables
- [ ] `.env` file is not committed to git
- [ ] `.env.example` is updated with new variables
- [ ] Security scan passes with no HIGH severity issues

## Production Deployment

### Secure Configuration

1. **Use strong passwords**: Generate random passwords for all services
2. **Rotate credentials**: Regularly update API keys and passwords
3. **Limit access**: Use principle of least privilege
4. **Monitor usage**: Track API usage and access patterns

### Environment-Specific Settings

```bash
# Production
ENVIRONMENT=production
DEBUG=false
REDIS_PASSWORD=<strong-random-password>

# Development
ENVIRONMENT=development
DEBUG=true
REDIS_PASSWORD=<development-password>
```

## Common Security Issues

### Hardcoded Credentials
```python
# ❌ WRONG
password = "secret123"

# ✅ CORRECT
password = os.getenv('PASSWORD')
if not password:
    raise ValueError("PASSWORD environment variable is required")
```

### Database Connection Strings
```python
# ❌ WRONG
db_url = "postgresql://user:password@localhost:5432/db"

# ✅ CORRECT
db_url = os.getenv('DATABASE_URL')
if not db_url:
    raise ValueError("DATABASE_URL environment variable is required")
```

### API Keys in Configuration
```python
# ❌ WRONG
config = {
    "api_key": "sk-1234567890abcdef"
}

# ✅ CORRECT
config = {
    "api_key": os.getenv('OPENAI_API_KEY')
}
```

## Incident Response

If credentials are accidentally committed:

1. **Immediately rotate** all exposed credentials
2. **Remove from git history** if possible
3. **Update environment variables** with new credentials
4. **Run security scan** to ensure no other exposures
5. **Review access logs** for unauthorized usage

## Security Tools

### Available Scripts

- `scripts/security_credential_scanner.py` - Scan for hardcoded credentials
- `scripts/security_cleanup_executor.py` - Automated security fixes
- `scripts/emergency_security_cleanup.py` - Emergency credential removal

### Integration

Add security scanning to your development workflow:

```bash
# Pre-commit hook
python scripts/security_credential_scanner.py --quick

# CI/CD pipeline
python scripts/security_credential_scanner.py --strict
```

## Contact

For security issues or questions:
- Review this documentation
- Check existing security tools and scripts
- Follow environment variable patterns consistently

Remember: **Security is everyone's responsibility**. When in doubt, use environment variables and never commit credentials.