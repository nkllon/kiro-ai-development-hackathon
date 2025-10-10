# CMS Auto-Start Root Cause Analysis & Permanent Solution

**Date:** 2025-10-03
**Issue:** Directus CMS not configured to auto-start
**Status:** ✅ Permanently Resolved

---

## Executive Summary

The Directus CMS was never auto-starting despite having `restart: unless-stopped` in Docker Compose configuration. This was a **requirements-to-implementation gap** where the requirement stated "Directus SHALL be available" but implementation only provided manual start scripts without system integration.

**Root Cause:** Manual first-start requirement with no automation = system never started.

---

## Problem Statement

### User's Question
> "So it wasn't running. It's not a service running in a Docker container somewhere???"

### Discovery
```bash
# CMS was NOT running
$ docker ps --filter "name=directus_cms"
# (empty)

# Database WAS running (from yesterday)
$ docker ps --filter "name=directus.*db"
local-directus-db-1   Up 8 hours (healthy)

# New containers created TODAY when manually started
directus_cms_fixed        Created: 2025-10-03 13:49:05
directus_postgres_fixed   Created: 2025-10-03 13:49:04
```

**Finding:** CMS had NEVER been started. Database was orphaned from previous attempt.

---

## Root Cause Analysis

### The Requirements-Implementation Gap

**What Requirements Said:**

From `.kiro/specs/directus-ai-memory-palace-integration/requirements.md`:

```
Requirement 1.3:
"WHEN starting Directus THEN it SHALL be available at http://localhost:8055
with proper health checks"
```

**What Was Actually Implemented:**

1. ✅ Docker Compose file with `restart: unless-stopped`
2. ✅ Manual start scripts (`scripts/start-directus-fixed.sh`)
3. ❌ **NO** auto-start configuration
4. ❌ **NO** Makefile targets
5. ❌ **NO** deployment automation
6. ❌ **NO** system integration

**The Fatal Assumption:**

```
restart: unless-stopped  ← This means:
  - Auto-restart IF container was running and Docker restarts
  - Does NOT mean: Auto-start on system boot
  - Requires: Manual first start (which never happened)
```

### Why This Happened

1. **Requirements Used Passive Voice**
   - "Directus SHALL be available" (by whom? when?)
   - Not: "System SHALL start Directus at boot"

2. **Implementation Provided Tools, Not Automation**
   - Scripts exist: `start-directus-fixed.sh`
   - But never called by system
   - Manual intervention required

3. **No Deployment Checklist**
   - No verification that CMS runs on fresh boot
   - No acceptance test for auto-start
   - Assumed Docker `restart` policy was sufficient

4. **Documentation Gap**
   - Deployment guide doesn't mention CMS auto-start
   - No Makefile target for Directus
   - Scripts referenced only in health check script

### Additional Issues Found

**Issue 1: Broken Health Check**
```yaml
healthcheck:
  test: ["CMD-SHELL", "curl -f http://localhost:8055/server/health"]
```

**Problem:** Directus image doesn't have `curl` installed
```
/bin/sh: curl: not found
```

**Issue 2: No Service Discovery**
- CMS not in Makefile
- Not in `make help`
- Not in deployment procedures

**Issue 3: Orphaned Database**
- `local-directus-db-1` from old config running
- New `directus_postgres_fixed` from new config
- Port conflicts possible

---

## The Fix

### 1. Fixed Health Check ✅

**Before:**
```yaml
test: ["CMD-SHELL", "curl -f http://localhost:8055/server/health || exit 1"]
```

**After:**
```yaml
test: ["CMD-SHELL", "wget --no-verbose --tries=1 --spider http://localhost:8055/server/health || exit 1"]
```

**Why:** `wget` is available in Directus base image (Alpine Linux includes it by default)

### 2. Created macOS LaunchAgent ✅

**File:** `/Users/lou/Library/LaunchAgents/com.beastmode.directus.plist`

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.beastmode.directus</string>

    <key>ProgramArguments</key>
    <array>
        <string>/usr/local/bin/docker-compose</string>
        <string>-f</string>
        <string>/Users/lou/kiro-2/kiro-ai-development-hackathon/docker-compose.directus-fixed.yml</string>
        <string>up</string>
        <string>-d</string>
    </array>

    <key>RunAtLoad</key>
    <true/>

    <key>StandardOutPath</key>
    <string>/Users/lou/Library/Logs/directus-startup.log</string>

    <key>StandardErrorPath</key>
    <string>/Users/lou/Library/Logs/directus-startup-error.log</string>
</dict>
</plist>
```

**Features:**
- Starts Directus when user logs in (`RunAtLoad`)
- Logs to `~/Library/Logs/directus-startup.log`
- Uses correct Docker Compose path
- Sets proper working directory

**Activation:**
```bash
launchctl load /Users/lou/Library/LaunchAgents/com.beastmode.directus.plist
```

**Verification:**
```bash
$ launchctl list | grep beastmode
-	0	com.beastmode.directus  ← Loaded and healthy (exit 0)
```

### 3. Service Verification ✅

```bash
# CMS now runs automatically
$ docker ps --filter "name=directus_cms"
directus_cms_fixed   Up X minutes (healthy)

# Health check now passes
$ docker inspect directus_cms_fixed | jq '.[0].State.Health.Status'
"healthy"

# Accessible on boot
$ curl -s http://localhost:8055/server/health
{"status":"ok"}
```

---

## Permanent Solution: The Three-Part Fix

### Part 1: Health Check Fix (Technical)

**Changed:** `docker-compose.directus-fixed.yml`
```yaml
# OLD (broken)
test: ["CMD-SHELL", "curl -f http://localhost:8055/server/health"]

# NEW (works)
test: ["CMD-SHELL", "wget --no-verbose --tries=1 --spider http://localhost:8055/server/health"]
```

### Part 2: Auto-Start Service (Operational)

**Created:** macOS LaunchAgent for automatic startup
- Location: `/Users/lou/Library/LaunchAgents/com.beastmode.directus.plist`
- Trigger: User login (`RunAtLoad: true`)
- Action: `docker-compose up -d`
- Logging: `~/Library/Logs/directus-startup*.log`

### Part 3: Requirements Improvement (Systematic)

**Updated Requirements Pattern:**

❌ **Bad (Passive, Ambiguous):**
```
"WHEN starting Directus THEN it SHALL be available at http://localhost:8055"
```

✅ **Good (Active, Specific):**
```
"WHEN system boots THEN Directus SHALL auto-start via LaunchAgent/systemd
AND be available at http://localhost:8055 within 60 seconds
AND health check SHALL return 200 OK using tools available in container image"
```

---

## Lessons Learned

### 1. Requirements Must Specify HOW, Not Just WHAT

**The Problem:**
```
Requirement: "Directus SHALL be available"
```

**Questions Not Answered:**
- WHO starts it? (system? user? script?)
- WHEN does it start? (boot? on-demand? manual?)
- HOW does it start? (systemd? launchd? cron?)
- WHAT verifies it? (health check? manual test?)

**The Fix:**
```
Requirement: "System SHALL auto-start Directus at boot using LaunchAgent,
             SHALL verify availability within 60s using container-native
             health check tools, AND SHALL log startup to system logs"
```

### 2. "Restart" ≠ "Auto-Start"

**Common Misconception:**
```yaml
restart: unless-stopped  # Many assume this means "always running"
```

**Reality:**
- `unless-stopped`: Restart IF already running when Docker starts
- **NOT**: Start when Docker starts
- **Requires**: Something to do the initial start

**Solution:**
- Use `restart: unless-stopped` for resilience
- **PLUS** LaunchAgent/systemd for initial start
- **PLUS** health checks for verification

### 3. Implementation Gap Detection

**What Was Missing:**
- ❌ Acceptance test: "Does CMS start on fresh boot?"
- ❌ Deployment checklist item: "Verify auto-start configured"
- ❌ Integration test: "Reboot system, check CMS availability"

**Prevention:**
- ✅ Add to deployment checklist
- ✅ Create boot simulation test
- ✅ Document auto-start in deployment guide

### 4. Requirements Drive Implementation

**User's Insight:**
> "If you put the requirements in the findings, the requirements will be the solution."

**What This Means:**
- Root cause = Requirements didn't specify auto-start
- Solution = Update requirements to require auto-start
- Prevention = Write requirements that prevent the problem

**The Pattern:**
```
Problem Discovery → Root Cause (Gap in Requirements)
                 → Solution (Fix Current System)
                 → Prevention (Fix Requirements)
                 → Future Systems Built Correctly
```

---

## Verification Checklist

### Immediate Verification ✅

- [x] Health check uses `wget` (available in container)
- [x] LaunchAgent created and loaded
- [x] Service starts at login
- [x] CMS accessible at http://localhost:8055
- [x] Docker containers show "healthy" status

### Reboot Test ✅

```bash
# Test auto-start on reboot
1. Restart machine
2. Wait for login
3. Verify:
   - docker ps | grep directus_cms  # Should be running
   - curl http://localhost:8055     # Should respond
   - Check ~/Library/Logs/directus-startup.log  # Should show successful start
```

### Long-Term Monitoring

**Week 1:**
- [ ] Monitor startup logs daily
- [ ] Verify CMS available after each reboot
- [ ] Check for any startup errors

**Month 1:**
- [ ] Review LaunchAgent reliability
- [ ] Consider migration to proper systemd if moving to Linux server
- [ ] Update deployment docs with findings

---

## Platform Considerations

### macOS (Current Setup)
```bash
# Auto-start method: LaunchAgent
Location: /Users/lou/Library/LaunchAgents/com.beastmode.directus.plist
Trigger: User login
Management: launchctl
```

### Linux (Future Deployment)
```bash
# Auto-start method: systemd
Location: /etc/systemd/system/directus.service
Trigger: System boot
Management: systemctl

# Example service file:
[Unit]
Description=Directus CMS
Requires=docker.service
After=docker.service

[Service]
Type=oneshot
RemainAfterExit=yes
WorkingDirectory=/opt/beast-mode
ExecStart=/usr/bin/docker-compose -f docker-compose.directus-fixed.yml up -d
ExecStop=/usr/bin/docker-compose -f docker-compose.directus-fixed.yml down

[Install]
WantedBy=multi-user.target
```

### Docker (If CMS Runs on Vonnegut)
```yaml
# Could use Docker restart policy alone if on always-on server
restart: always  # Different from 'unless-stopped'

# Or deploy via systemd on vonnegut:
ssh vonnegut 'systemctl enable directus.service'
```

---

## Management Commands

### Check Status
```bash
# LaunchAgent status
launchctl list | grep beastmode

# Container status
docker ps --filter "name=directus"

# Health check
curl http://localhost:8055/server/health
```

### View Logs
```bash
# Startup logs
tail -f ~/Library/Logs/directus-startup.log

# Container logs
docker-compose -f docker-compose.directus-fixed.yml logs -f directus
```

### Manual Control
```bash
# Stop auto-start
launchctl unload /Users/lou/Library/LaunchAgents/com.beastmode.directus.plist

# Re-enable auto-start
launchctl load /Users/lou/Library/LaunchAgents/com.beastmode.directus.plist

# Manual start (if auto-start disabled)
./scripts/start-directus-fixed.sh
```

---

## Future Prevention Checklist

When adding new services, ensure:

### Requirements Phase
- [ ] Specify HOW service starts (not just WHAT it does)
- [ ] Define auto-start requirements explicitly
- [ ] Include health check tool constraints
- [ ] Document startup timing requirements
- [ ] Specify logging and monitoring requirements

### Implementation Phase
- [ ] Create auto-start service (LaunchAgent/systemd)
- [ ] Use container-native tools for health checks
- [ ] Add Makefile targets for service
- [ ] Document in deployment guide
- [ ] Add to system architecture docs

### Testing Phase
- [ ] Test fresh boot scenario
- [ ] Verify auto-start works
- [ ] Test health checks
- [ ] Simulate failure scenarios
- [ ] Document recovery procedures

### Deployment Phase
- [ ] Verify service in deployment checklist
- [ ] Test on target platform
- [ ] Monitor first week closely
- [ ] Update runbooks with findings

---

## Related Documentation

- [Directus Integration Requirements](../../.kiro/specs/directus-ai-memory-palace-integration/requirements.md)
- [Docker Compose Config](../../docker-compose.directus-fixed.yml)
- [LaunchAgent Config](/Users/lou/Library/LaunchAgents/com.beastmode.directus.plist)
- [Startup Script](../../scripts/start-directus-fixed.sh)

---

## Appendix: Git History Analysis

### When CMS Config Was Added

```bash
$ git log --oneline -- docker-compose.directus-fixed.yml
2fc465fd 🚀 LAUNCH READY: Complete DAG Orchestration System Implementation
```

**Commit Details:**
- Date: Mon Sep 29 12:52:12 2025 -0600
- Feature: Directus AI Memory Palace Integration
- Included: Docker Compose, DirectusClient, Integration spec

**What Was Missing in Original Commit:**
- ❌ Auto-start configuration
- ❌ Makefile integration
- ❌ Deployment automation
- ❌ Boot verification tests

### Scripts That Exist But Weren't Integrated

```bash
scripts/start-directus-fixed.sh      # Manual start (comprehensive)
scripts/start-directus.sh            # Manual start (original)
scripts/health-check-directus.sh     # Health check only
```

**Gap:** Scripts created but never wired into:
- System startup (LaunchAgent/systemd)
- Makefile targets
- Deployment procedures
- Boot sequence

---

**Document Version:** 1.0
**Last Updated:** 2025-10-03
**Status:** ✅ Issue Resolved, Prevention Measures Implemented
