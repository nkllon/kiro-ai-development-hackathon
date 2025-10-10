# SonarCloud API-Based Setup Guide
## Automated Configuration for KIRO AI Development Hackathon

**Status:** API script ready, requires SONAR_TOKEN  
**Date:** 2025-10-10

---

## YES! SonarCloud Has a Web API

You're absolutely right - SonarCloud has a comprehensive Web API that can automate most of the setup process. I've created an automated setup script that uses it.

---

## Quick Start (API Method)

### Step 1: Get Your SonarCloud Token

You still need to do this manually once:

1. Log into https://sonarcloud.io (with GitHub)
2. Click profile → **My Account** → **Security** tab
3. Generate token: `kiro-hackathon-api-token`
4. Copy the token

### Step 2: Export the Token

```bash
export SONAR_TOKEN='your-token-here'
```

Or add to your `~/.env`:
```bash
echo "SONAR_TOKEN=your-token-here" >> ~/.env
```

### Step 3: Run the Automated Setup

```bash
cd /Users/lou/kiro-2/kiro-ai-development-hackathon

# Run the setup script
python3 scripts/setup_sonarcloud.py

# Or with custom options
python3 scripts/setup_sonarcloud.py \
  --project-key nkllon_kiro-ai-development-hackathon \
  --project-name "Kiro AI Development Hackathon" \
  --new-code-days 30
```

This will:
- ✅ Set organization-level new code definition (30 days)
- ✅ Create the project in SonarCloud
- ✅ Configure new code definition for the project
- ✅ Set visibility to public (free tier)

### Step 4: Add Token to GitHub

```bash
# Using GitHub CLI
gh secret set SONAR_TOKEN --body "$SONAR_TOKEN"

# Or manually in GitHub UI
# Settings → Secrets → Actions → New secret
# Name: SONAR_TOKEN
# Value: [your token]
```

### Step 5: Commit and Push

```bash
git add sonar-project.properties .github/workflows/sonarcloud.yml
git commit -m "ci: add SonarCloud configuration with automated setup"
git push origin rc1-patch
```

Done! The workflow will run automatically.

---

## API Reference

### Available Endpoints (from Web API exploration)

#### 1. Create Project
```bash
POST /api/projects/create
```

**Parameters:**
- `organization` (required): nkllon
- `project` (required): nkllon_kiro-ai-development-hackathon  
- `name` (required): Kiro AI Development Hackathon
- `newCodeDefinitionType` (optional): days, previous_version, date, version
- `newCodeDefinitionValue` (optional): e.g., "30" for 30 days
- `visibility` (optional): public, private

**Example:**
```bash
curl -u "$SONAR_TOKEN:" -X POST \
  "https://sonarcloud.io/api/projects/create" \
  -d "organization=nkllon" \
  -d "project=nkllon_kiro-ai-development-hackathon" \
  -d "name=Kiro AI Development Hackathon" \
  -d "newCodeDefinitionType=days" \
  -d "newCodeDefinitionValue=30" \
  -d "visibility=public"
```

#### 2. Set Organization New Code Definition
```bash
POST /api/new_code_periods/set
```

**Parameters:**
- `organization` (required): nkllon
- `type` (required): NUMBER_OF_DAYS, PREVIOUS_VERSION, SPECIFIC_ANALYSIS
- `value` (optional): e.g., "30" for 30 days

**Example:**
```bash
curl -u "$SONAR_TOKEN:" -X POST \
  "https://sonarcloud.io/api/new_code_periods/set" \
  -d "organization=nkllon" \
  -d "type=NUMBER_OF_DAYS" \
  -d "value=30"
```

#### 3. Check if Project Exists
```bash
GET /api/projects/search
```

**Example:**
```bash
curl -u "$SONAR_TOKEN:" \
  "https://sonarcloud.io/api/projects/search?projects=nkllon_kiro-ai-development-hackathon"
```

#### 4. Get Settings
```bash
GET /api/settings/values
```

**Example:**
```bash
curl -u "$SONAR_TOKEN:" \
  "https://sonarcloud.io/api/settings/values?component=nkllon_kiro-ai-development-hackathon"
```

---

## Script Usage

### Basic Usage

```bash
# With token from environment
export SONAR_TOKEN='your-token'
python3 scripts/setup_sonarcloud.py
```

### Check if Project Exists

```bash
python3 scripts/setup_sonarcloud.py --check-only
```

### Custom Configuration

```bash
python3 scripts/setup_sonarcloud.py \
  --token "$SONAR_TOKEN" \
  --organization "nkllon" \
  --project-key "nkllon_kiro-ai-development-hackathon" \
  --project-name "Kiro AI Development Hackathon" \
  --new-code-days 30
```

---

## Important Notes

### What the API Can Do ✅

- ✅ Create projects programmatically
- ✅ Set new code definitions (org and project level)
- ✅ Configure project settings
- ✅ Update visibility
- ✅ Manage quality gates
- ✅ List existing projects

### What Still Requires UI 🔐

- 🔐 **Initial GitHub OAuth authorization** - Must be done once in UI
- 🔐 **GitHub App installation** - For automatic repository import

**Workaround:** 
1. First time: Log into SonarCloud UI and authorize GitHub (one-time)
2. After that: Use API for all project management
3. Or: Create projects via API manually (they work without GitHub integration)

### GitHub Integration (ALM)

For GitHub-integrated projects (with PR decoration, etc.):
1. You must first authorize GitHub in the SonarCloud UI
2. Install the SonarCloud GitHub App
3. Then you can import/create projects via API

**For now:** The API script creates a "manual" project that works with GitHub Actions but doesn't have PR decoration until GitHub is authorized in the UI.

---

## Complete Automation Approach

### One-Time Setup (Manual)

```bash
# 1. Log into SonarCloud and authorize GitHub (one-time)
open https://sonarcloud.io/login

# 2. After GitHub auth, get your token
open https://sonarcloud.io/account/security

# 3. Export the token
export SONAR_TOKEN='your-token-here'
```

### Automated Setup (API)

```bash
# 4. Run automated setup script
python3 scripts/setup_sonarcloud.py

# 5. Add token to GitHub secrets
gh secret set SONAR_TOKEN --body "$SONAR_TOKEN"

# 6. Commit and push configuration
git add sonar-project.properties .github/workflows/sonarcloud.yml scripts/setup_sonarcloud.py
git commit -m "ci: add SonarCloud with automated API setup"
git push origin rc1-patch
```

---

## Testing the Setup

```bash
# Check if project exists
python3 scripts/setup_sonarcloud.py --check-only

# List all projects
curl -u "$SONAR_TOKEN:" \
  "https://sonarcloud.io/api/components/search_projects?organization=nkllon"

# Get project details
curl -u "$SONAR_TOKEN:" \
  "https://sonarcloud.io/api/projects/search?projects=nkllon_kiro-ai-development-hackathon"
```

---

## API Documentation

- **Web API v1:** https://sonarcloud.io/web_api
- **Web API v2:** https://api-docs.sonarsource.com
- **New Code Periods:** https://sonarcloud.io/web_api/api/new_code_periods
- **Projects:** https://sonarcloud.io/web_api/api/projects
- **Settings:** https://sonarcloud.io/web_api/api/settings

---

## Troubleshooting

### Authentication Error

```
401 Unauthorized
```

**Solution:** Check your token is valid and not expired.

### Permission Error

```
403 Forbidden: Insufficient privileges
```

**Solution:** Ensure you have admin access to the organization.

### Project Already Exists

```
400 Bad Request: Project already exists
```

**Solution:** Use `--check-only` to verify, or skip creation.

---

## Summary

**Yes, you can use the API!** The setup script automates:
- Organization new code definition
- Project creation
- Project configuration

The only manual steps are:
1. Initial GitHub OAuth (one-time)
2. Token generation
3. Adding token to GitHub secrets

This is much faster than clicking through the UI for each project! 🚀

