---
inclusion: always
---

# ⚠️ CORRECTED: Python Package Release Procedure

**Last Updated:** 2025-10-10  
**Status:** MANDATORY - This procedure must be followed without exception  
**Supersedes:** Any previous informal or incorrect release procedures

## Incident Report

**Date:** 2025-10-10  
**Package:** beast-mailbox-core  
**Severity:** Critical  
**Agent:** Claude Sonnet 4.5

### What Happened
Version 0.2.0 was published to PyPI from a development directory (`/Users/lou/kiro-2/kiro-ai-development-hackathon/packages/beast-mailbox-core`) without committing changes to the canonical repository (`/Users/lou/Documents/cursor/beast-mailbox-core`), creating a complete break in version control integrity and violating supply chain security.

### Lesson Learned
**NEVER publish a package without committing, tagging, and pushing to the repository first.**

Working in multiple directories of the same project is dangerous. Always verify you're in the canonical repository before any release operations.

---

## The ONLY Correct Release Procedure

### Pre-Release Requirements

Before you even THINK about publishing:

1. ✅ Verify you're in the CANONICAL repository (not a development copy)
2. ✅ All code changes are committed and pushed to GitHub
3. ✅ All changes have gone through pull request review
4. ✅ All tests pass
5. ✅ No linter errors

### Release Steps (Must Follow in Order)

#### Step 0: Verify Location (CRITICAL)
```bash
# Verify you're in the correct repository
pwd
git remote -v  # Must point to the canonical GitHub repo
git status     # Must be clean or only have intended changes

# If working in multiple clones, STOP and consolidate
find ~ -name "beast-mailbox-core" -type d 2>/dev/null
```

#### Step 1: Prepare Release Branch
```bash
# Ensure you're in the correct repository
git checkout main
git pull origin main

# Create release branch
git checkout -b release/vX.Y.Z
```

#### Step 2: Update Version and Changelog
```bash
# Edit pyproject.toml - update version line
# Edit CHANGELOG.md - add release notes

git add pyproject.toml CHANGELOG.md
git commit -m "Bump version to X.Y.Z"
git push origin release/vX.Y.Z
```

#### Step 3: Create Pull Request
- Create PR from release/vX.Y.Z to main
- Title: "Release vX.Y.Z"
- Wait for review and approval
- Merge PR

#### Step 4: Tag the Release
```bash
# Pull the merged changes
git checkout main
git pull origin main

# Verify version in pyproject.toml matches intended release
grep "^version" pyproject.toml

# Create annotated tag
git tag -a vX.Y.Z -m "Release version X.Y.Z"

# Push tag
git push origin vX.Y.Z

# VERIFY tag is on GitHub
git ls-remote --tags origin | grep vX.Y.Z
```

#### Step 5: Build Package
```bash
# Clean previous builds
rm -rf dist/ build/ *.egg-info

# Install build tools
pip install --upgrade build twine

# Build
python -m build

# Verify built package
tar -tzf dist/beast-mailbox-core-X.Y.Z.tar.gz | head -20
```

#### Step 6: Test Publication (REQUIRED)
```bash
# Upload to Test PyPI first
twine upload --repository testpypi dist/*

# Install from Test PyPI and verify
pip install --index-url https://test.pypi.org/simple/ beast-mailbox-core==X.Y.Z

# Test basic functionality
beast-mailbox-service --help
beast-mailbox-send --help
```

#### Step 7: Publish to PyPI
```bash
# Only proceed if Test PyPI worked
twine upload dist/*

# Verify on PyPI
pip install beast-mailbox-core==X.Y.Z
pip show beast-mailbox-core
```

#### Step 8: Create GitHub Release
1. Go to https://github.com/nkllon/beast-mailbox-core/releases/new
2. Select tag: vX.Y.Z
3. Release title: vX.Y.Z
4. Description: Copy from CHANGELOG.md
5. Publish release

#### Step 9: Verify Everything
```bash
# Repository check
git log --oneline -5
git tag | grep vX.Y.Z

# PyPI check
pip index versions beast-mailbox-core

# GitHub check - verify release exists
# GitHub check - verify tag exists
```

---

## Critical Rules

### ❌ NEVER DO THESE:

1. **NEVER** publish without pushing commits first
2. **NEVER** publish without creating a git tag
3. **NEVER** publish from a directory that isn't the main repository
4. **NEVER** work in multiple clones without extreme care
5. **NEVER** skip the Test PyPI step
6. **NEVER** skip code review (even for version bumps)
7. **NEVER** rush a release
8. **NEVER** assume you remember the correct procedure

### ✅ ALWAYS DO THESE:

1. **ALWAYS** verify you're in the correct repository directory first
2. **ALWAYS** run `pwd` and `git remote -v` before any release operation
3. **ALWAYS** check that git status is clean before tagging
4. **ALWAYS** use Test PyPI first
5. **ALWAYS** verify the tag is pushed before publishing
6. **ALWAYS** create a GitHub Release after publishing
7. **ALWAYS** follow the checklist completely
8. **ALWAYS** update CHANGELOG.md

---

## Verification Questions

Before publishing, answer YES to all:

- [ ] Are all my changes committed?
- [ ] Are all my changes pushed to GitHub?
- [ ] Have my changes been reviewed in a PR?
- [ ] Is the PR merged to main?
- [ ] Am I working in the canonical repository? (`pwd` and check)
- [ ] Have I created and pushed the git tag?
- [ ] Does the tag match the version in pyproject.toml?
- [ ] Have I tested on Test PyPI?
- [ ] Have I verified the package contents?

**If ANY answer is NO, STOP and complete that step first.**

---

## Multiple Directory Problem

The v0.2.0 incident occurred because work was done in:
- `/Users/lou/kiro-2/kiro-ai-development-hackathon/packages/beast-mailbox-core` (dev)

But the canonical repository was at:
- `/Users/lou/Documents/cursor/beast-mailbox-core` (canonical)

**Solution:** Work in ONE place only. If you must have multiple checkouts:
1. Designate ONE as canonical
2. NEVER publish from non-canonical locations
3. Always verify with `pwd` before operations

---

## Emergency Contact

If confused or uncertain at ANY point:
1. STOP immediately
2. Do NOT publish
3. Ask for help
4. Review this document again
5. Check which directory you're in

---

## Post-Mortem: v0.2.0 Incident

**What Went Wrong:**
1. Agent worked in development directory
2. Published to PyPI from development directory
3. Canonical repository was not updated
4. No git tag created
5. No verification that repo matched package

**Impact:**
- PyPI had v0.2.0 with no corresponding source in repo
- Users couldn't audit code
- MIT license violation (source unavailable)
- Supply chain security broken
- Reproducibility impossible

**Resolution:**
1. Created branch `fix/sync-repo-with-v0.2.0`
2. Copied all changes from dev to canonical repo
3. Created comprehensive CHANGELOG.md
4. Committed with detailed incident report
5. Pushed branch and created PR

**Prevention:**
- This document created
- Always verify location before operations
- Updated testing-patterns.md
- Encoded location verification as first step

---

**This procedure was created in response to a critical incident. Following it is not optional.**


