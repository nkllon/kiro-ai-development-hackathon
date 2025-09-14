# 🔍 Proper Git Workflow Research: Beast Mode DNA Spawning

## The Problem We Discovered

**Current Broken Approach:**
- Using `git worktree` to create "spawned" repositories
- Worktrees become detached from upstream
- Fresh Kiro instances can't push changes back
- Submodules in worktrees lose their connection

**What We Actually Need:**
- Independent repositories that can evolve separately
- Ability to push changes back to their own remotes
- Proper upstream tracking for continuous integration
- Beast Mode DNA seeding that maintains git connectivity

## Research: Proper Approaches

### Option 1: Template Repository + Fork Pattern
```bash
# Create template repository with Beast Mode DNA
# Users fork the template
# Fresh Kiro instances work in forked repos
# Can submit PRs back to template for improvements
```

### Option 2: Git Submodule with Proper Remote Setup
```bash
# Add submodule pointing to separate repository
git submodule add https://github.com/user/spawn-repo.git spawns/project-name
cd spawns/project-name
# Submodule has its own remote, can push independently
git push origin main
```

### Option 3: Monorepo with Independent Directories
```bash
# Each spawn is a directory in main repo
# Uses sparse-checkout for Kiro instances
# All changes tracked in main repository
# Simpler but less distributed
```

### Option 4: Git Subtree (Better than Submodules)
```bash
# Add external repo as subtree
git subtree add --prefix=spawns/project-name https://github.com/user/spawn-repo.git main
# Can push changes back to original repo
git subtree push --prefix=spawns/project-name origin main
```

## Recommended Solution: Template + Independent Repos

### Step 1: Create Template Repository
- Beast Mode DNA template repository
- Contains `.kiro/` structure with spores
- Users can fork or use as template

### Step 2: Spawn Independent Repositories  
- Each spawn is its own repository
- Seeded from template
- Has its own remote origin
- Can evolve independently

### Step 3: Fresh Kiro Workflow
- Clone spawned repository directly
- Work in independent repo
- Push changes to spawn's origin
- Submit improvements back to template via PR

## Implementation Plan

1. **Fix Current Worktree Approach** - Stop using worktrees for spawning
2. **Create Template Repos** - Proper template repositories for each spore type
3. **Update Spawning Scripts** - Use proper git clone/fork workflow
4. **Test with TIDB** - Validate new approach works correctly