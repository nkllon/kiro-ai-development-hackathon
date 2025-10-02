---
inclusion: always
---

# Security Credentials Governance - Zero Tolerance for Hardcoded Secrets

## Core Principle

**"NEVER hardcode passwords, API keys, tokens, or any credentials in source code, configuration files, or documentation. This is a critical security violation with zero tolerance."**

## Critical Security Violations Observed

### **The Redis Password Incident**
- **What Happened**: Redis password `"beastmode2025"` was hardcoded in multiple source files
- **Files Affected**: 
  - `src/execution_tracking/redis_execution_tracker.py`
  - `scripts/configure_dag_coordination_mode.py` 
  - `scripts/validate_redis_execution_tracking.py`
- **Security Impact**: Production credentials exposed in version control
- **Compliance Impact**: Violates security best practices and regulatory requirements

## Mandatory Security Requirements

### **NEVER Hardcode These:**
- ❌ Passwords (database, Redis, service accounts)
- ❌ API keys (OpenAI, Anthropic, cloud services)
- ❌ Authentication tokens (JWT, OAuth, session tokens)
- ❌ Private keys (SSH, TLS, signing keys)
- ❌ Connection strings with embedded credentials
- ❌ Service account credentials
- ❌ Encryption keys or salts
- ❌ Third-party service secrets

### **ALWAYS Use Environment Variables:**
- ✅ `os.getenv('REDIS_PASSWORD')`
- ✅ `os.getenv('OPENAI_API_KEY')`
- ✅ `os.getenv('DATABASE_PASSWORD')`
- ✅ Load from `~/.env` or system environment
- ✅ Use configuration management systems
- ✅ Use secret management services (AWS Secrets Manager, etc.)

## Mandatory Implementation Patterns

### **Environment Variable Loading Pattern**
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

# CORRECT: Use environment variables
redis_password = os.getenv('REDIS_PASSWORD', os.getenv('BEAST_MODE_REDIS_PASSWORD', ''))
if not redis_password:
    raise ValueError("Redis password must be set in environment variables")
```

### **Configuration Class Pattern**
```python
@dataclass
class SecureConfig:
    """Secure configuration using environment variables only."""
    redis_host: str = field(default_factory=lambda: os.getenv('REDIS_HOST', 'localhost'))
    redis_port: int = field(default_factory=lambda: int(os.getenv('REDIS_PORT', '6379')))
    redis_password: str = field(default_factory=lambda: os.getenv('REDIS_PASSWORD', ''))
    
    def __post_init__(self):
        if not self.redis_password:
            raise ValueError("REDIS_PASSWORD environment variable is required")
```

### **Graceful Error Handling Pattern**
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
```

## Anti-Patterns - STRICTLY FORBIDDEN

### ❌ **Hardcoded Credentials**
```python
# NEVER DO THIS
redis_password = "beastmode2025"
api_key = "sk-1234567890abcdef"
database_url = "postgresql://user:password@host:5432/db"
```

### ❌ **Default Credential Values**
```python
# NEVER DO THIS
password = os.getenv('PASSWORD', 'default_password')
api_key = os.getenv('API_KEY', 'fallback_key')
```

### ❌ **Credentials in Configuration Files**
```json
// NEVER DO THIS
{
  "redis_password": "beastmode2025",
  "api_key": "secret_key_here"
}
```

### ❌ **Credentials in Documentation**
```markdown
<!-- NEVER DO THIS -->
Connect to Redis with password: beastmode2025
Use API key: sk-1234567890abcdef
```

### ❌ **Credentials in Comments**
```python
# NEVER DO THIS
# Default password is: beastmode2025
# API key for testing: sk-1234567890abcdef
```

## Mandatory Security Practices

### **For All Developers**
1. **NEVER commit credentials** to version control
2. **ALWAYS use environment variables** for sensitive data
3. **VALIDATE environment variables** are set before using
4. **PROVIDE helpful error messages** when credentials are missing
5. **USE ~/.env files** for local development (add to .gitignore)

### **For Code Reviews**
1. **SCAN for hardcoded credentials** in every PR
2. **REJECT any PR** with hardcoded secrets
3. **REQUIRE environment variable usage** for all credentials
4. **VALIDATE error handling** for missing credentials
5. **CHECK .gitignore** includes credential files

### **For AI Assistants**
1. **NEVER generate code** with hardcoded credentials
2. **ALWAYS use environment variable patterns** for sensitive data
3. **PROVIDE secure configuration examples** in all code
4. **FLAG any existing hardcoded credentials** for immediate remediation
5. **EDUCATE users** about security best practices

## Remediation Protocol

### **When Hardcoded Credentials Are Found**
1. **IMMEDIATE ACTION**: Remove credentials from code
2. **ENVIRONMENT VARIABLES**: Convert to environment variable usage
3. **CREDENTIAL ROTATION**: Rotate any exposed credentials
4. **GIT HISTORY**: Consider rewriting git history if credentials were committed
5. **SECURITY REVIEW**: Assess potential exposure and impact

### **Emergency Response**
1. **STOP**: Halt deployment if hardcoded credentials are discovered
2. **ASSESS**: Determine scope of credential exposure
3. **ROTATE**: Change all potentially exposed credentials
4. **REMEDIATE**: Fix all code to use environment variables
5. **VALIDATE**: Ensure no other hardcoded credentials exist

## Automated Detection

### **Pre-commit Hooks**
```bash
# Add to .pre-commit-config.yaml
- repo: https://github.com/Yelp/detect-secrets
  rev: v1.4.0
  hooks:
    - id: detect-secrets
      args: ['--baseline', '.secrets.baseline']
```

### **Code Scanning Patterns**
```bash
# Scan for common credential patterns
grep -r "password.*=" --include="*.py" .
grep -r "api_key.*=" --include="*.py" .
grep -r "secret.*=" --include="*.py" .
grep -r "token.*=" --include="*.py" .
```

### **CI/CD Integration**
- **MANDATORY**: Scan all code for hardcoded credentials
- **FAIL BUILD**: If any credentials are detected
- **REQUIRE**: Environment variable usage validation
- **AUDIT**: Regular security scans of entire codebase

## Sample ~/.env File Structure

```bash
# ~/.env - NEVER commit this file
# Redis Configuration
REDIS_PASSWORD=your_actual_password_here
REDIS_HOST=192.168.1.119
REDIS_PORT=6379

# API Keys
OPENAI_API_KEY=sk-your_openai_key_here
ANTHROPIC_API_KEY=your_anthropic_key_here

# Database
DATABASE_PASSWORD=your_db_password_here
DATABASE_URL=postgresql://user:${DATABASE_PASSWORD}@host:5432/db

# Environment
ENVIRONMENT=development
DEBUG=true
```

## Compliance and Regulatory Impact

### **Regulatory Violations**
- **GDPR**: Inadequate security measures for personal data
- **SOC 2**: Failure to protect system credentials
- **PCI DSS**: Insecure credential storage
- **HIPAA**: Inadequate safeguards for system access

### **Business Impact**
- **Security Breach**: Exposed credentials enable unauthorized access
- **Compliance Failure**: Regulatory fines and penalties
- **Reputation Damage**: Loss of customer trust
- **Operational Risk**: System compromise and data loss

## Success Metrics

### **Security Compliance**
- **Zero hardcoded credentials** in entire codebase
- **100% environment variable usage** for sensitive data
- **Automated scanning** catches all credential patterns
- **Regular security audits** validate compliance

### **Developer Education**
- **All developers trained** on secure credential practices
- **Code review process** includes security validation
- **Documentation updated** with security requirements
- **Incident response plan** for credential exposure

## The Meta-Principle

**"Security is not optional. Credentials are never hardcoded. Environment variables are mandatory. This is non-negotiable."**

Every line of code that handles credentials must follow secure practices. Every developer must understand that hardcoded credentials are a critical security violation. Every system must be designed with security-first principles.

---

**This steering rule ensures that the Redis password incident never happens again and establishes zero tolerance for hardcoded credentials in any form.**