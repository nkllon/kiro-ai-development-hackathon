# Topological Branch Sync Procedure

## Overview
The Topological Branch Sync is a systematic procedure for synchronizing complex Git branching structures that follow a Directed Acyclic Graph (DAG) dependency model. This ensures all branches are synchronized at the same point in time while respecting their hierarchical relationships.

## When to Use
- Multi-agent development with parallel feature branches
- Complex task decomposition with dependency hierarchies
- Ensuring consistent state across all development branches
- Before major development phases or releases

## Prerequisites
- All branches must be pushed to remote
- DAG structure must be well-defined
- No circular dependencies between branches

## Procedure Steps

### Phase 1: Prepare Master Branch
```bash
# Commit any pending changes
git add .
git commit -m "Sync preparation: [description]"
git push
```

### Phase 2: Sync Feature Branches (Level 1 Dependencies)
```bash
# Sync all feature branches from master
for branch in feature/branch-1 feature/branch-2 feature/branch-N; do
    git checkout $branch
    git pull origin master
    git push
done
```

### Phase 3: Sync Task Branches (Level 2 Dependencies)
```bash
# Sync task branches from their respective feature branches
git checkout task/feature-1-task-1
git pull origin feature/branch-1
git push

git checkout task/feature-1-task-2
git pull origin feature/branch-1
git push
# Repeat for all feature-dependent tasks
```

### Phase 4: Sync Remaining Branches (Level 3+ Dependencies)
```bash
# Sync all remaining branches from master (cross-feature dependencies)
for branch in task/integration-task-1 task/integration-task-2; do
    git checkout $branch
    git pull origin master
    git push
done
```

### Phase 5: Verification
```bash
# Verify all branches are at the same commit
echo "Master: $(git rev-parse HEAD)"
for branch in $(git branch -r | grep -v HEAD); do
    echo "$branch: $(git rev-parse $branch)"
done
```

## DAG Structure Example
```
master
├── feature/domain-registry-manager
│   ├── task/2.2-domain-indexing-caching
│   └── task/2.3-domain-validation-consistency
├── feature/query-engine
│   ├── task/3.2-advanced-query-capabilities
│   └── task/3.3-natural-language-query
└── task/5.1-filesystem-synchronization (depends on Phase 2 completion)
```

## Benefits
- **Consistency**: All branches synchronized to same point in time
- **Dependency Respect**: Maintains hierarchical relationships
- **Conflict Prevention**: Eliminates merge conflicts from timing issues
- **Parallel Safety**: Enables safe parallel development
- **Audit Trail**: Clear synchronization points for tracking

## Automation Script
```bash
#!/bin/bash
# topological-sync.sh

set -e

echo "=== Topological Branch Sync ==="

# Phase 1: Master
git checkout master
git add .
git commit -m "Topological sync preparation - $(date)"
git push

# Phase 2: Feature branches
FEATURE_BRANCHES=("feature/domain-registry-manager" "feature/query-engine" "feature/health-monitoring")
for branch in "${FEATURE_BRANCHES[@]}"; do
    echo "Syncing $branch from master..."
    git checkout $branch
    git pull origin master
    git push
done

# Phase 3: Feature-dependent tasks
declare -A TASK_DEPENDENCIES=(
    ["task/2.2-domain-indexing-caching"]="feature/domain-registry-manager"
    ["task/2.3-domain-validation-consistency"]="feature/domain-registry-manager"
    ["task/3.2-advanced-query-capabilities"]="feature/query-engine"
)

for task in "${!TASK_DEPENDENCIES[@]}"; do
    parent="${TASK_DEPENDENCIES[$task]}"
    echo "Syncing $task from $parent..."
    git checkout $task
    git pull origin $parent
    git push
done

# Phase 4: Master-dependent tasks
MASTER_TASKS=("task/5.1-filesystem-synchronization" "task/6.1-domain-metrics-calculation")
for task in "${MASTER_TASKS[@]}"; do
    echo "Syncing $task from master..."
    git checkout $task
    git pull origin master
    git push
done

git checkout master
echo "✅ Topological sync complete"
```

## Best Practices
1. **Document Dependencies**: Maintain clear DAG documentation
2. **Regular Syncing**: Perform before major development phases
3. **Verification**: Always verify synchronization success
4. **Communication**: Notify team before/after sync operations
5. **Backup**: Ensure all work is committed before sync

## Troubleshooting
- **Merge Conflicts**: Resolve at the dependency source level first
- **Missing Branches**: Ensure all branches exist remotely
- **Circular Dependencies**: Redesign branch structure to eliminate cycles
- **Failed Pushes**: Check permissions and network connectivity

---
*This procedure ensures consistent, dependency-aware branch synchronization for complex multi-agent development workflows.*