# Dismiss Dependabot Security Alerts

## Purpose
Systematically dismiss Dependabot security alerts that have been analyzed and determined to pose no actual risk to the system.

## When to Use This Prompt
- After analyzing Dependabot alerts and determining they are false positives or acceptable risks
- When you need to clear security warnings that don't apply to your deployment architecture
- To document risk acceptance decisions with proper justification

## Prerequisites
- GitHub CLI (`gh`) installed and authenticated
- Python 3.9+
- Admin/write access to the repository

## Step 1: Review Open Alerts

```bash
# List all open Dependabot alerts
gh api repos/nkllon/kiro-ai-development-hackathon/dependabot/alerts \
  --jq '.[] | select(.state == "open") | {number, package: .dependency.package.name, severity: .security_advisory.severity, vulnerability: .security_advisory.summary}'
```

## Step 2: Analyze Exposure

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

## Step 3: Update Dismissal Configuration

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

## Step 4: Dry Run

```bash
# Preview what will be dismissed
python3 scripts/dismiss_dependabot_alerts.py --dry-run

# Preview specific package only
python3 scripts/dismiss_dependabot_alerts.py --dry-run --package python-jose
```

## Step 5: Execute Dismissals

```bash
# Dismiss all configured alerts
python3 scripts/dismiss_dependabot_alerts.py

# Dismiss only specific package
python3 scripts/dismiss_dependabot_alerts.py --package python-jose
```

## Step 6: Verify

```bash
# Check remaining open alerts
gh api repos/nkllon/kiro-ai-development-hackathon/dependabot/alerts \
  --jq '[.[] | select(.state == "open")] | length'
```

## Common Risk Classifications

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

## Security Best Practices

1. **Always analyze before dismissing** - Don't blindly dismiss alerts
2. **Document reasoning** - Future you needs to understand why
3. **Consider architecture** - WAF, internal-only, etc. affect risk
4. **Check actual usage** - Package in deps ≠ package used in code
5. **Review periodically** - Usage patterns change over time

## Notes

- Dismissed alerts remain visible in GitHub with the dismissal reason
- You can re-open dismissed alerts if circumstances change
- Comments are visible to all repo collaborators
- GitHub API rate limits apply (typically 5000/hour for authenticated users)

## Related Files

- `/scripts/dismiss_dependabot_alerts.py` - The dismissal script
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
