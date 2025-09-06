# Branch Protection Configuration

## GitHub Settings to Apply

### Master Branch Protection
**Path**: Settings → Branches → Add rule

**Branch name pattern**: `master`

**Protection Rules**:
- ✅ **Require a pull request before merging**
  - ✅ Require approvals: 1
  - ✅ Dismiss stale PR approvals when new commits are pushed
  - ✅ Require review from code owners
- ✅ **Require status checks to pass before merging**
  - ✅ Require branches to be up to date before merging
  - Status checks: (will be added when CI is configured)
- ✅ **Require conversation resolution before merging**
- ✅ **Restrict pushes that create files larger than 100MB**
- ✅ **Allow force pushes** (for maintainers only)
- ✅ **Allow deletions** (for maintainers only)

**Restrictions**:
- ✅ **Restrict pushes**
  - Add maintainers/admins who can bypass (you)
  - Everyone else must use PRs

### Develop Branch Protection  
**Branch name pattern**: `develop`

**Protection Rules**:
- ✅ **Require a pull request before merging**
  - ✅ Require approvals: 1
  - ✅ Dismiss stale PR approvals when new commits are pushed
- ✅ **Require status checks to pass before merging**
  - ✅ Require branches to be up to date before merging
- ✅ **Require conversation resolution before merging**
- ✅ **Allow force pushes** (for maintainers only)
- ✅ **Allow deletions** (for maintainers only)

**Restrictions**:
- ✅ **Restrict pushes**
  - Add maintainers/admins who can bypass (you)

## Systematic Safety Enforcement

### What This Protects
- **Steering files** from ad-hoc pollution
- **Implementation quality** through required reviews
- **Systematic approach** by forcing PR workflow
- **Beast Mode principles** through conversation resolution

### Emergency Override
- Maintainers can force push with "whimper of a warning"
- Use only for critical fixes or systematic improvements
- Document reason in commit message

### Workflow
1. **Feature branches** → **develop** (via PR)
2. **develop** → **master** (via PR, for releases)
3. **Hotfixes** → **master** (via PR, emergency only)

## Implementation Commands

```bash
# Create develop branch if it doesn't exist
git checkout -b develop
git push -u origin develop

# Return to master
git checkout master
```

**Note**: Apply these settings in GitHub web interface at:
`https://github.com/nkllon/kiro-ai-development-hackathon/settings/branches`