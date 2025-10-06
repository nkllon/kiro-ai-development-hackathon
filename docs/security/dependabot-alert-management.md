# Dependabot Alert Management

## Overview

This document describes the systematic approach to managing Dependabot security alerts in the Beast Mode AI Development Framework repository.

## Philosophy

We take a **risk-based approach** to security alerts:
- **Analyze before dismissing** - Never blindly dismiss alerts
- **Document reasoning** - All dismissals include clear risk acceptance rationale
- **Consider architecture** - Factor in Cloudflare WAF, internal-only services, etc.
- **Check actual usage** - Package in dependencies ≠ package used in code

## Tools

### 1. Check Current Alerts
```bash
# Quick status check
python3 scripts/check_dependabot_alerts.py

# Detailed view with dismissed alerts
python3 scripts/check_dependabot_alerts.py --verbose
```

### 2. Analyze Package Usage
```bash
# Analyze specific package
python3 scripts/analyze_dependency_usage.py python-jose

# Analyze all dependencies (comprehensive)
python3 scripts/analyze_dependency_usage.py --all
```

### 3. Dismiss Alerts Systematically
```bash
# Preview dismissals (safe)
python3 scripts/dismiss_dependabot_alerts.py --dry-run

# Dismiss all configured alerts
python3 scripts/dismiss_dependabot_alerts.py

# Dismiss specific package only
python3 scripts/dismiss_dependabot_alerts.py --package python-jose
```

## Risk Classification

### `not_used` - Unused Dependencies
Package is listed in requirements but never imported or used in code.

**Example:**
```python
"python-jose": {
    "reason": "not_used",
    "comment": (
        "Risk Accepted: Listed in requirements-cms-search.txt but no JWT/auth "
        "code exists. Unused dependency. Attack surface: None."
    )
}
```

### `inaccurate` - False Positives
Dependabot detects a package that isn't actually in dependencies.

**Example:**
```python
"gunicorn": {
    "reason": "inaccurate",
    "comment": (
        "False Positive: Not in any requirements files. System uses uvicorn. "
        "Dependabot scanning stale lock files."
    )
}
```

### `tolerable_risk` - Acceptable Risk
Vulnerability requires conditions that don't exist in our usage.

**Example:**
```python
"jinja2": {
    "reason": "tolerable_risk",
    "comment": (
        "Risk Accepted: No untrusted template rendering. Jinja2 only for "
        "internal FastAPI HTML. Behind Cloudflare WAF. Attack surface: None."
    )
}
```

### `fix_started` - Work in Progress
Fix is already being worked on.

### `no_bandwidth` - Deferred
Valid issue but no resources to fix immediately.

## Workflow

### 1. Regular Monitoring
```bash
# Weekly check for new alerts
python3 scripts/check_dependabot_alerts.py
```

### 2. New Alert Analysis
When new alerts appear:

1. **Analyze usage:**
   ```bash
   python3 scripts/analyze_dependency_usage.py <package-name>
   ```

2. **Research vulnerability:**
   - Read the CVE details
   - Understand attack vectors
   - Consider our usage patterns

3. **Assess risk:**
   - Is the package actually used?
   - Do we use the vulnerable functionality?
   - What protections are in place?

### 3. Configuration Update
Edit `scripts/dismiss_dependabot_alerts.py` and add to `DISMISSALS`:

```python
"package-name": {
    "reason": "not_used|inaccurate|tolerable_risk|fix_started|no_bandwidth",
    "comment": "Risk Accepted: [Explanation under 280 chars]. Attack surface: None."
}
```

### 4. Execute Dismissal
```bash
# Test first
python3 scripts/dismiss_dependabot_alerts.py --dry-run

# Execute
python3 scripts/dismiss_dependabot_alerts.py
```

## Architecture Considerations

### Cloudflare WAF Protection
Many vulnerabilities require direct HTTP access. Our services are protected by:
- Cloudflare Web Application Firewall
- Rate limiting and DDoS protection
- Geographic restrictions
- Bot protection

### Internal-Only Services
Some services are not exposed to the internet:
- Development tools
- Internal monitoring
- Build systems

### Usage Patterns
Consider how we actually use dependencies:
- Template rendering with trusted input only
- File processing of known-safe files
- API calls to trusted endpoints

## Comment Guidelines

All dismissal comments must:
- Be under 280 characters (GitHub limit)
- Start with "Risk Accepted:" or "False Positive:"
- Explain why the vulnerability doesn't apply
- Mention architectural protections if relevant
- End with "Attack surface: None" if applicable

## Monitoring and Review

### Automated Monitoring
- GitHub automatically creates alerts for new vulnerabilities
- CI/CD pipeline can be configured to check alert status
- Weekly automated reports can be generated

### Periodic Review
- Monthly review of dismissed alerts
- Quarterly review of risk classifications
- Annual review of overall security posture

### Metrics
Track:
- Time to alert resolution
- Percentage of alerts dismissed vs. fixed
- Recurring vulnerability patterns
- False positive rates

## Emergency Procedures

### Critical Vulnerability
If a critical vulnerability affects actively used code:

1. **Immediate assessment** - Understand impact and exploitability
2. **Temporary mitigation** - WAF rules, service isolation, etc.
3. **Rapid fix** - Update dependency or patch code
4. **Validation** - Ensure fix doesn't break functionality
5. **Documentation** - Update procedures based on lessons learned

### Mass Alert Event
If many alerts appear simultaneously:

1. **Triage by severity** - Critical and high first
2. **Batch analysis** - Use automated tools to assess usage
3. **Systematic dismissal** - Process in risk order
4. **Root cause analysis** - Why did this happen?

## Integration with Development

### Pre-commit Hooks
Consider adding dependency vulnerability checks to pre-commit hooks.

### CI/CD Integration
Alert status can be checked in CI/CD pipelines:
```bash
# Fail build if critical alerts exist
python3 scripts/check_dependabot_alerts.py --critical-only
```

### Developer Education
- Security awareness training
- Dependency selection guidelines
- Vulnerability assessment procedures

## Related Files

- `scripts/dismiss_dependabot_alerts.py` - Main dismissal script
- `scripts/analyze_dependency_usage.py` - Usage analysis tool
- `scripts/check_dependabot_alerts.py` - Status checking tool
- `pyproject.toml` - Main Python dependencies
- `requirements*.txt` - Service-specific dependencies

## References

- [GitHub Dependabot Documentation](https://docs.github.com/en/code-security/dependabot)
- [CVE Database](https://cve.mitre.org/)
- [NIST Vulnerability Database](https://nvd.nist.gov/)
- [OWASP Top 10](https://owasp.org/www-project-top-ten/)