# Deployment Data Governance - Zero Tolerance for Volatile Data in Version Control

## Core Principle

**"Deployment directories must contain ONLY configuration and infrastructure code. Runtime data, databases, logs, and volatile files are STRICTLY FORBIDDEN in version control."**

## Critical Incident Reference

**Date**: January 27, 2025  
**Issue**: 342 volatile files (Prometheus TSDB, Grafana databases, plugin binaries) were tracked in version control  
**Impact**: Repository pollution, security risks, performance degradation  
**Resolution**: Complete cleanup and governance implementation  

## Mandatory Deployment Data Classification

### ✅ ALLOWED in Version Control (Configuration)
- **Docker Compose files**: `docker-compose.yml`, `docker-compose.override.yml`
- **Container definitions**: `Dockerfile`, `.dockerignore`
- **Infrastructure as Code**: Kubernetes manifests, Helm charts, Terraform
- **Configuration templates**: Nginx configs, application configs (without secrets)
- **Build and deployment scripts**: Shell scripts, Makefiles, CI/CD pipelines
- **Documentation**: README files, deployment guides, troubleshooting docs

### ❌ STRICTLY FORBIDDEN in Version Control (Volatile Data)
- **Database files**: `*.db`, `*.sqlite`, `*.sqlite3`, database dumps
- **Time-series data**: Prometheus TSDB blocks, InfluxDB data, metrics storage
- **Application logs**: `*.log`, log directories, rotated logs
- **Cache files**: Redis dumps, application caches, temporary files
- **Plugin/extension data**: Downloaded plugins, compiled extensions
- **Runtime state**: PID files, socket files, lock files
- **Binary executables**: Downloaded binaries, compiled artifacts
- **Secrets and credentials**: API keys, certificates, password files
- **User-generated content**: Uploaded files, user data, session data

## Mandatory .gitignore Patterns

### Universal Deployment Patterns
```gitignore
# Deployment volatile data - NEVER commit these
deployment/*/data/
deployment/*-data/
deployment/*/logs/
deployment/*/cache/
deployment/*/tmp/
deployment/*/temp/

# Database files
*.db
*.sqlite
*.sqlite3
**/database/
**/db-data/

# Monitoring and metrics data
**/prometheus-data/
**/grafana-data/
**/grafana.db
**/alertmanager-data/
**/influxdb-data/

# Application logs
*.log
**/logs/
**/log/

# Cache and temporary files
**/cache/
**/tmp/
**/temp/
**/pid/
*.pid

# Plugin and extension directories
**/plugins/
**/extensions/
**/node_modules/
**/vendor/

# Runtime state
*.sock
*.lock
**/run/
**/var/

# Backup files
*.bak
*.backup
**/backups/
```

### Service-Specific Patterns
```gitignore
# Prometheus
**/prometheus-data/
**/tsdb/
**/wal/
**/chunks_head/

# Grafana
**/grafana-data/
**/grafana.db
**/grafana/plugins/
**/grafana/provisioning/dashboards/*.json

# Redis
**/redis-data/
*.rdb
*.aof

# PostgreSQL
**/postgres-data/
**/postgresql-data/
**/pgdata/

# Nginx
**/nginx-logs/
**/access.log
**/error.log

# Docker
**/docker-data/
**/volumes/
```

## Docker Volume Strategy (MANDATORY)

### ✅ CORRECT: Named Volumes
```yaml
# docker-compose.yml
services:
  prometheus:
    image: prom/prometheus
    volumes:
      - prometheus-data:/prometheus  # Named volume - not tracked
      - ./prometheus.yml:/etc/prometheus/prometheus.yml:ro  # Config only

  grafana:
    image: grafana/grafana
    volumes:
      - grafana-storage:/var/lib/grafana  # Named volume - not tracked
      - ./grafana/provisioning:/etc/grafana/provisioning:ro  # Config only

volumes:
  prometheus-data:    # Managed by Docker, not in git
  grafana-storage:    # Persistent but not tracked
```

### ❌ FORBIDDEN: Host Directory Mounts for Data
```yaml
# NEVER DO THIS - Creates tracked directories
services:
  prometheus:
    volumes:
      - ./prometheus-data:/prometheus  # Creates tracked directory
  
  grafana:
    volumes:
      - ./grafana-data:/var/lib/grafana  # Creates tracked directory
```

### ✅ ACCEPTABLE: Host Mounts for Configuration Only
```yaml
# OK for read-only configuration
services:
  nginx:
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro  # Config file only
      - nginx-logs:/var/log/nginx  # Logs to named volume
```

## Enforcement Mechanisms

### Pre-Commit Validation
```bash
#!/bin/bash
# .git/hooks/pre-commit
# Prevent volatile data commits

FORBIDDEN_PATTERNS=(
    "*.db"
    "*.sqlite"
    "*.log"
    "*/prometheus-data/*"
    "*/grafana-data/*"
    "*/logs/*"
    "*/cache/*"
    "*/tmp/*"
)

for pattern in "${FORBIDDEN_PATTERNS[@]}"; do
    if git diff --cached --name-only | grep -E "$pattern"; then
        echo "ERROR: Attempting to commit volatile data: $pattern"
        echo "This violates deployment data governance."
        exit 1
    fi
done
```

### CI/CD Pipeline Checks
```yaml
# .github/workflows/deployment-hygiene.yml
name: Deployment Data Governance
on: [push, pull_request]

jobs:
  check-volatile-data:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Scan for volatile data
        run: |
          # Check for database files
          if find deployment/ -name "*.db" -o -name "*.sqlite*" | grep -q .; then
            echo "ERROR: Database files found in deployment directory"
            exit 1
          fi
          
          # Check for data directories
          if find deployment/ -type d -name "*-data" | grep -q .; then
            echo "ERROR: Data directories found in deployment directory"
            exit 1
          fi
          
          # Check for log files
          if find deployment/ -name "*.log" | grep -q .; then
            echo "ERROR: Log files found in deployment directory"
            exit 1
          fi
```

### Repository Audit Script
```python
#!/usr/bin/env python3
"""
Deployment Data Governance Audit Script
Scans repository for volatile data violations
"""

import os
import glob
from pathlib import Path

FORBIDDEN_PATTERNS = [
    "**/*.db",
    "**/*.sqlite*",
    "**/*.log",
    "**/prometheus-data/**",
    "**/grafana-data/**",
    "**/logs/**",
    "**/cache/**",
    "**/tmp/**",
    "**/data/**",
]

def audit_deployment_directory():
    """Audit deployment directory for volatile data."""
    violations = []
    
    for pattern in FORBIDDEN_PATTERNS:
        matches = glob.glob(f"deployment/{pattern}", recursive=True)
        for match in matches:
            if os.path.exists(match):
                violations.append(match)
    
    return violations

if __name__ == "__main__":
    violations = audit_deployment_directory()
    if violations:
        print("DEPLOYMENT DATA GOVERNANCE VIOLATIONS:")
        for violation in violations:
            print(f"  ❌ {violation}")
        print("\nThese files must be removed from version control.")
        exit(1)
    else:
        print("✅ No deployment data governance violations found.")
```

## Emergency Cleanup Procedures

### When Volatile Data is Discovered
```bash
#!/bin/bash
# Emergency cleanup script

echo "🚨 DEPLOYMENT DATA GOVERNANCE VIOLATION DETECTED"
echo "Initiating emergency cleanup..."

# 1. Stop all running services
docker-compose down
pkill -f "prometheus|grafana"

# 2. Remove volatile data from git tracking
git rm -r --cached deployment/*/prometheus-data/ 2>/dev/null || true
git rm -r --cached deployment/*/grafana-data/ 2>/dev/null || true
git rm -r --cached deployment/*/*.db 2>/dev/null || true
git rm -r --cached deployment/*/*.log 2>/dev/null || true

# 3. Update .gitignore if needed
echo "# Emergency governance patterns" >> .gitignore
echo "deployment/*/prometheus-data/" >> .gitignore
echo "deployment/*/grafana-data/" >> .gitignore
echo "deployment/*/*.db" >> .gitignore
echo "deployment/*/*.log" >> .gitignore

# 4. Commit cleanup
git add .gitignore
git commit -m "🚨 EMERGENCY: Remove volatile deployment data from version control

- Remove database files, logs, and runtime data
- Update .gitignore to prevent future violations
- Enforce deployment data governance"

echo "✅ Emergency cleanup completed"
echo "⚠️  Update docker-compose.yml to use named volumes"
```

### Data Recovery Procedures
```bash
#!/bin/bash
# Recover data after cleanup (if needed)

echo "🔄 Recovering deployment data from Docker volumes..."

# List existing volumes
docker volume ls

# Backup existing volumes before cleanup
docker run --rm -v prometheus-data:/data -v $(pwd):/backup alpine tar czf /backup/prometheus-backup.tar.gz -C /data .
docker run --rm -v grafana-storage:/data -v $(pwd):/backup alpine tar czf /backup/grafana-backup.tar.gz -C /data .

echo "✅ Data backed up to prometheus-backup.tar.gz and grafana-backup.tar.gz"
```

## Monitoring and Compliance

### Regular Audit Schedule
- **Daily**: Automated CI/CD checks on all commits
- **Weekly**: Repository scan for volatile data accumulation
- **Monthly**: Full deployment directory audit and cleanup
- **Quarterly**: Review and update governance patterns

### Compliance Metrics
- **Zero volatile files**: No database, log, or runtime files in version control
- **Clean .gitignore**: All necessary patterns present and effective
- **Proper volumes**: All persistent data uses Docker named volumes
- **Team compliance**: 100% adherence to governance rules

### Violation Response
1. **Immediate**: Block deployment until violation resolved
2. **Emergency cleanup**: Remove volatile data from version control
3. **Root cause analysis**: Determine how violation occurred
4. **Process improvement**: Update governance to prevent recurrence
5. **Team education**: Ensure all developers understand rules

## Success Metrics

### Repository Health
- **Repository size**: Stable or decreasing (no binary bloat)
- **Clone performance**: Fast clone times for new developers
- **Merge conflicts**: Zero conflicts on volatile data files
- **Security posture**: No credentials or sensitive data in version control

### Deployment Reliability
- **Consistent deployments**: Same configuration produces same results
- **Environment isolation**: Development data doesn't affect production
- **Backup integrity**: All persistent data properly backed up
- **Recovery capability**: Fast recovery from data loss

## The Meta-Principle

**"Configuration belongs in git. Data belongs in volumes. Never mix the two."**

This governance ensures that:
- **Version control** contains only what should be versioned
- **Persistent data** is properly managed outside version control
- **Security** is maintained by keeping sensitive data out of git
- **Performance** is optimized by avoiding binary file bloat
- **Collaboration** is improved by eliminating meaningless data commits

## Training and Education

### For Developers
- **Understand the difference** between configuration and data
- **Use named volumes** for all persistent data
- **Never commit** database files, logs, or runtime state
- **Check .gitignore** before adding new deployment components

### For DevOps Engineers
- **Design volume strategies** that separate concerns properly
- **Implement monitoring** for governance compliance
- **Create backup procedures** for Docker volumes
- **Maintain .gitignore patterns** for new services

### For Security Teams
- **Audit repositories** regularly for sensitive data exposure
- **Validate backup procedures** don't expose credentials
- **Monitor access** to persistent data volumes
- **Ensure compliance** with data protection regulations

---

**This steering rule is derived from the critical incident of January 27, 2025, where 342 volatile files were discovered in version control. It establishes permanent governance to prevent recurrence and maintain deployment hygiene.**

**ZERO TOLERANCE POLICY**: Any violation of this governance must be immediately remediated with emergency cleanup procedures.