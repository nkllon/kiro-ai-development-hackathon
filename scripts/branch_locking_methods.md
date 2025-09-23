# Branch Locking Methods

## 🔒 GitHub Branch Protection Rules (ACTIVE)

### Protected Branches:
- ✅ `master` - Main production branch
- ✅ `release/rc0-competitive-launch` - Release candidate

### Protection Features:
- **Pull Request Reviews**: Require 1 approval minimum
- **Status Checks**: Require CI to pass
- **Restrictions**: Prevent direct pushes
- **Force Push Protection**: Disabled
- **Deletion Protection**: Enabled
- **Stale Review Dismissal**: Enabled

## 🛡️ Local Protection Methods

### 1. Git Hooks (Available)
```bash
# Use the protection script
./scripts/protect_branches.sh protect master
./scripts/protect_branches.sh status
```

### 2. Git Aliases (Recommended)
```bash
# Add to .gitconfig
[alias]
    protect = "!f() { git config branch.$1.protected true; }; f"
    unprotect = "!f() { git config --unset branch.$1.protected; }; f"
    safe-commit = "!f() { if git config --get branch.$(git branch --show-current).protected; then echo 'Protected branch - use PR'; else git commit \"$@\"; fi; }; f"
```

### 3. Environment Variables
```bash
# Prevent accidental pushes to protected branches
export GIT_PROTECTED_BRANCHES="master,release/rc0-competitive-launch"
```

### 4. IDE/Editor Integration
- **VS Code**: Use GitLens extension with branch protection
- **IntelliJ**: Configure branch protection in VCS settings
- **Sublime**: Use GitSavvy plugin with branch protection

## 🚨 Emergency Override Methods

### GitHub Override (Admin Only)
```bash
# Temporarily disable protection (use with extreme caution)
gh api repos/nkllon/kiro-ai-development-hackathon/branches/master/protection --method DELETE
```

### Local Override
```bash
# Bypass local hooks (use with caution)
git commit --no-verify
git push --force-with-lease
```

## 📋 Protection Checklist

### Before Merging to Protected Branches:
- [ ] All tests pass
- [ ] Code review completed
- [ ] Documentation updated
- [ ] Security scan passed
- [ ] Performance tests passed
- [ ] Branch is up to date with target

### Emergency Procedures:
- [ ] Document reason for override
- [ ] Notify team of changes
- [ ] Re-enable protection immediately
- [ ] Review changes in next team meeting

## 🔧 Configuration Commands

### Check Current Protection:
```bash
gh api repos/nkllon/kiro-ai-development-hackathon/branches/master/protection
```

### Update Protection Rules:
```bash
gh api repos/nkllon/kiro-ai-development-hackathon/branches/master/protection \
  --method PUT \
  --input protection_rules.json
```

### List All Protected Branches:
```bash
gh api repos/nkllon/kiro-ai-development-hackathon/branches --jq '.[] | select(.protected == true) | .name'
```
