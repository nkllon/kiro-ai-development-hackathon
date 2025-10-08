# Dismiss Dependabot Security Alerts

## Purpose
Systematically dismiss Dependabot security alerts that have been analyzed and determined to pose no actual risk to the system.

## ✅ Current Status (Updated 2025-01-27)
- **Script Status**: ✅ Fully implemented and tested
- **Repository Status**: ✅ No open Dependabot alerts found
- **Configuration**: ✅ Pre-configured for common packages (python-jose, python-multipart, gunicorn, jinja2, requests, black)
- **Validation**: ✅ All tests passed, dry-run functionality confirmed

## When to Use This Process
- When new Dependabot alerts appear in the repository
- After analyzing alerts and determining they are false positives or acceptable risks
- When you need to clear security warnings that don't apply to your deployment architecture
- To document risk acceptance decisions with proper justification

## Prerequisites
- GitHub CLI (`gh`) installed and authenticated
- Python 3.9+
- Admin/write access to the repository

## Quick Start (Most Common Usage)

### Check Current Status
```bash
# Quick check for any open alerts
python3 scripts/dismiss_dependabot_alerts.py --dry-run
```

**Expected Output (Current State):**
```
✅ Configuration validation passed
📡 Fetching open Dependabot alerts...
✅ No open Dependabot alerts found
```

### If Alerts Are Found
```bash
# 1. See what would be dismissed
python3 scripts/dismiss_dependabot_alerts.py --dry-run

# 2. Execute dismissals (if satisfied with dry-run results)
python3 scripts/dismiss_dependabot_alerts.py

# 3. Target specific package if needed
python3 scripts/dismiss_dependabot_alerts.py --package python-jose
```

## Detailed Process

### Step 1: Review Open Alerts

**Using the Script (Recommended):**
```bash
# The script automatically fetches and displays alerts
python3 scripts/dismiss_dependabot_alerts.py --dry-run
```

**Manual GitHub API (Alternative):**
```bash
# List all open Dependabot alerts
gh api repos/nkllon/kiro-ai-development-hackathon/dependabot/alerts \
  --jq '.[] | select(.state == "open") | {number, package: .dependency.package.name, severity: .security_advisory.severity, vulnerability: .security_advisory.summary}'
```

### Step 2: Analyze Exposure

For each alert, determine:

1. **Is the package actually used?**
   ```bash
   # Check if package is in direct dependencies
   grep -r "package-name" pyproject.toml requirements*.txt

   # Check if package is used in code
   grep -r "import package" src/ --include="*.py"
   ```

2. **What's the attack surface?**
   - Behind Cloudflare WAF?
   - User-facing endpoints?
   - Actual usage patterns match vulnerability conditions?

3. **Risk classification:**
   - `not_used` - Package listed but never actually used
   - `inaccurate` - False positive (package not in dependencies)
   - `tolerable_risk` - Valid dependency, but attack vector doesn't exist
   - `no_bandwidth` - Need to fix later (deferred)
   - `fix_started` - Work in progress

### Step 3: Update Dismissal Configuration

**Current Pre-configured Packages:**
The script already includes dismissal configurations for:
- `python-jose` (CRITICAL - not used)
- `python-multipart` (HIGH - not used) 
- `gunicorn` (HIGH - false positive)
- `jinja2`/`Jinja2` (MEDIUM - tolerable risk)
- `requests` (MEDIUM - tolerable risk)
- `black` (MEDIUM - dev-only)

**To Add New Packages:**
Edit `scripts/dismiss_dependabot_alerts.py` and add/update the `DISMISSALS` dictionary:

```python
DISMISSALS = {
    "package-name": {
        "reason": "not_used",  # or "inaccurate", "tolerable_risk"
        "comment": (
            "Risk Accepted: [Concise explanation under 280 chars]. "
            "Attack surface: None."
        )
    },
}
```

**Comment Guidelines:**
- Must be under 280 characters (GitHub limit)
- Start with "Risk Accepted:" or "False Positive:"
- Explain why the vulnerability doesn't apply
- Mention architectural protections (Cloudflare, internal-only, etc.)
- End with "Attack surface: None" if applicable

### Step 4: Dry Run (Always Do This First)

```bash
# Preview what will be dismissed
python3 scripts/dismiss_dependabot_alerts.py --dry-run

# Preview specific package only
python3 scripts/dismiss_dependabot_alerts.py --dry-run --package python-jose
```

**Sample Output:**
```
✅ Configuration validation passed
📡 Fetching open Dependabot alerts...
Found 3 open alerts

📋 Alert #123: python-jose (CRITICAL)
   Vulnerability: JWT signature verification bypass
   Dismissal reason: not_used
   Comment: Risk Accepted: python-jose is listed in requirements-cms-search.txt...
   [DRY RUN] Would dismiss

Summary:
  Dismissed: 3
  Skipped: 0

💡 Run without --dry-run to actually dismiss alerts
```

### Step 5: Execute Dismissals

```bash
# Dismiss all configured alerts
python3 scripts/dismiss_dependabot_alerts.py

# Dismiss only specific package
python3 scripts/dismiss_dependabot_alerts.py --package python-jose
```

### Step 6: Verify

```bash
# Check remaining open alerts
gh api repos/nkllon/kiro-ai-development-hackathon/dependabot/alerts \
  --jq '[.[] | select(.state == "open")] | length'
```

## Pre-configured Risk Classifications

### `not_used` - Unused Dependencies
Use when the package is listed in requirements but never actually imported or used:

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
Use when Dependabot detects a package that isn't actually in your dependencies:

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
Use when the vulnerability requires conditions that don't exist in your usage:

```python
"jinja2": {
    "reason": "tolerable_risk",
    "comment": (
        "Risk Accepted: No untrusted template rendering. Jinja2 only for "
        "internal FastAPI HTML. Behind Cloudflare WAF. Attack surface: None."
    )
}
```

## Example: Full Workflow

```bash
# 1. Check what alerts exist
gh api repos/nkllon/kiro-ai-development-hackathon/dependabot/alerts \
  --jq 'map({number, package: .dependency.package.name, severity: .security_advisory.severity}) | unique_by(.package)'

# 2. Analyze a specific package
grep -r "python-multipart" pyproject.toml requirements*.txt
grep -r "UploadFile\|File(" src/ --include="*.py"

# 3. Update dismissal config in scripts/dismiss_dependabot_alerts.py

# 4. Test with dry run
python3 scripts/dismiss_dependabot_alerts.py --dry-run

# 5. Execute
python3 scripts/dismiss_dependabot_alerts.py

# 6. Verify all cleared
gh api repos/nkllon/kiro-ai-development-hackathon/dependabot/alerts \
  --jq '[.[] | select(.state == "open")] | length'
```

## Script Features & Capabilities

### Built-in Validation
- ✅ **Configuration validation** - Checks DISMISSALS dictionary format
- ✅ **GitHub API connectivity** - Validates authentication and access
- ✅ **Comment length validation** - Ensures 280-character GitHub limit compliance
- ✅ **Dry-run mode** - Preview changes before execution

### Error Handling
- ✅ **API rate limiting** - Handles GitHub API limits gracefully
- ✅ **Network failures** - Robust error handling for connectivity issues
- ✅ **Permission errors** - Clear messages for access issues
- ✅ **Invalid alerts** - Handles alerts that may have been auto-closed

### Reporting
- ✅ **Detailed output** - Shows alert numbers, packages, severities
- ✅ **Summary statistics** - Counts dismissed vs skipped alerts
- ✅ **Progress tracking** - Real-time feedback during execution

## Security Best Practices

1. **Always analyze before dismissing** - Don't blindly dismiss alerts
2. **Document reasoning** - Future you needs to understand why
3. **Consider architecture** - WAF, internal-only, etc. affect risk
4. **Check actual usage** - Package in deps ≠ package used in code
5. **Review periodically** - Usage patterns change over time
6. **Use dry-run first** - Always preview changes before execution

## Maintenance & Updates

### When New Alerts Appear
1. Run `python3 scripts/dismiss_dependabot_alerts.py --dry-run`
2. If new packages appear, analyze their usage
3. Add appropriate dismissal configuration
4. Test with dry-run, then execute

### Periodic Review (Quarterly)
1. Review dismissed alerts in GitHub
2. Check if usage patterns have changed
3. Update dismissal configurations as needed
4. Re-open alerts if circumstances have changed

## Notes

- Dismissed alerts remain visible in GitHub with the dismissal reason
- You can re-open dismissed alerts if circumstances change
- Comments are visible to all repo collaborators
- GitHub API rate limits apply (typically 5000/hour for authenticated users)
- The script includes automatic retry logic for transient failures

## Related Files

- `/scripts/dismiss_dependabot_alerts.py` - The main dismissal script
- `/scripts/check_dependabot_alerts.py` - Helper script for checking alerts
- `/scripts/analyze_dependency_usage.py` - Helper script for usage analysis
- `/pyproject.toml` - Main Python dependencies
- `/requirements*.txt` - Service-specific dependencies
- `/.github/dependabot.yml` - Dependabot configuration (if exists)

## Troubleshooting

**"Invalid property /dismissed_comment: Only 280 characters allowed"**
- Shorten the comment in the DISMISSALS dictionary
- Focus on key facts: why it's not a risk, what protections exist

**"Alert not found"**
- Alert may have been auto-closed by dependency update
- Run dry-run first to see current state

**"Permission denied"**
- Ensure `gh` is authenticated: `gh auth status`
- Requires write access to repository security alerts

**"Configuration validation failed"**
- Check DISMISSALS dictionary syntax in the script
- Ensure all required fields (reason, comment) are present

**"No open alerts found" but you expect some**
- Alerts may have been auto-resolved by dependency updates
- Check GitHub web interface to confirm
- Verify repository name in script matches actual repo

## Implementation History

**2025-01-27**: Script fully implemented and tested
- ✅ Complete dismissal automation
- ✅ Pre-configured for 6 common packages
- ✅ Comprehensive error handling and validation
- ✅ Dry-run functionality confirmed working
- ✅ No open alerts found in current repository state