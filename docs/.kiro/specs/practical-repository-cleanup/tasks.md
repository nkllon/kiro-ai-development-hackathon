# Practical Repository Cleanup - Tasks

## Overview

This task list provides actionable steps to execute the repository cleanup plan. Tasks are organized by phase with specific commands, validation steps, and rollback procedures.

**Total Estimated Time**: 2 days maximum
- Phase 1 (Assessment): 2 hours
- Phase 2 (Execution): 1 day
- Phase 3 (Cleanup): 2 hours

## Phase 1: Repository Assessment (2 hours)

### Task 1.1: Create Initial Backup and Assessment Setup
**Estimated Time**: 15 minutes

- [ ] Create full repository backup
  ```bash
  git bundle create ../kiro-repo-backup-$(date +%Y%m%d-%H%M%S).bundle --all
  ```
- [ ] Document current branch state
  ```bash
  git branch -a > branch-state-before-cleanup.txt
  git log --oneline --graph --all --decorate > git-graph-before-cleanup.txt
  ```
- [ ] Create cleanup workspace directory
  ```bash
  mkdir -p .cleanup-workspace
  cd .cleanup-workspace
  ```
- [ ] Record current repository statistics
  ```bash
  echo "Cleanup started: $(date)" > cleanup-log.txt
  echo "Current branch: $(git branch --show-current)" >> cleanup-log.txt
  echo "Total branches: $(git branch -a | wc -l)" >> cleanup-log.txt
  ```

### Task 1.2: Analyze Branch Relationships and Content
**Estimated Time**: 45 minutes

- [ ] Analyze rc1-project-cleanup-redo branch (45 commits ahead)
  ```bash
  git log master..origin/release/rc1-project-cleanup-redo --oneline > cleanup-redo-commits.txt
  git diff master...origin/release/rc1-project-cleanup-redo --name-only > cleanup-redo-files.txt
  git diff master...origin/release/rc1-project-cleanup-redo --stat > cleanup-redo-stats.txt
  ```
- [ ] Analyze rc1-final-integration branch (83 commits ahead)
  ```bash
  git log master..origin/release/rc1-final-integration --oneline > final-integration-commits.txt
  git diff master...origin/release/rc1-final-integration --name-only > final-integration-files.txt
  git diff master...origin/release/rc1-final-integration --stat > final-integration-stats.txt
  ```
- [ ] Compare branches for overlapping changes
  ```bash
  git log --oneline origin/release/rc1-project-cleanup-redo..origin/release/rc1-final-integration > integration-unique-commits.txt
  git log --oneline origin/release/rc1-final-integration..origin/release/rc1-project-cleanup-redo > cleanup-unique-commits.txt
  ```
- [ ] Identify common modified files
  ```bash
  comm -12 <(sort cleanup-redo-files.txt) <(sort final-integration-files.txt) > common-modified-files.txt
  ```

### Task 1.3: Conflict Prediction and Specification Validation
**Estimated Time**: 30 minutes

- [ ] Predict merge conflicts for cleanup-redo → master
  ```bash
  git merge-tree master origin/release/rc1-project-cleanup-redo > cleanup-merge-preview.txt
  ```
- [ ] Predict merge conflicts for final-integration → master (after cleanup-redo)
  ```bash
  # This requires temporary merge simulation
  git checkout master
  git checkout -b temp-merge-test
  git merge origin/release/rc1-project-cleanup-redo --no-commit --no-ff 2> temp-merge-conflicts.txt || true
  git merge-tree HEAD origin/release/rc1-final-integration > integration-merge-preview.txt
  git reset --hard master
  git branch -D temp-merge-test
  ```
- [ ] Check for conflict markers in current branches
  ```bash
  git grep -r "<<<<<<< " origin/release/rc1-project-cleanup-redo > cleanup-conflict-markers.txt || echo "No conflict markers found"
  git grep -r "<<<<<<< " origin/release/rc1-final-integration > integration-conflict-markers.txt || echo "No conflict markers found"
  ```
- [ ] Validate against specifications in .kiro/specs/
  ```bash
  find .kiro/specs -name "*.md" -exec grep -l "rc1\|cleanup\|integration" {} \; > relevant-specs.txt
  ```

### Task 1.4: Create Merge Plan and Risk Assessment
**Estimated Time**: 30 minutes

- [ ] Document merge order decision
  ```bash
  cat > merge-plan.txt << EOF
MERGE ORDER:
1. rc1-project-cleanup-redo → master (45 commits, foundational cleanup)
2. rc1-final-integration → master (83 commits, builds on cleanup)

RATIONALE:
- Cleanup branch likely contains foundational fixes
- Integration branch builds on cleanup work
- Lower risk to merge cleanup first

RISK ASSESSMENT:
- Common files: $(wc -l < common-modified-files.txt) files modified by both branches
- Predicted conflicts: See *-merge-preview.txt files
- Rollback plan: Bundle backup + git reset --hard
EOF
  ```
- [ ] Create detailed backup strategy
  ```bash
  cat > backup-strategy.txt << EOF
BACKUP STRATEGY:
1. Initial full backup: ../kiro-repo-backup-*.bundle
2. Pre-merge backup points: git tag before each merge
3. Rollback commands: git reset --hard <tag>
4. Emergency restore: git clone ../kiro-repo-backup-*.bundle

BACKUP POINTS:
- before-cleanup-merge
- before-integration-merge
- cleanup-complete
EOF
  ```
- [ ] Identify high-risk areas requiring Ghostbusters consultation
  ```bash
  cat > ghostbusters-consultation-needed.txt << EOF
GHOSTBUSTERS CONSULTATION NEEDED FOR:
1. Complex conflicts in common files (see common-modified-files.txt)
2. Specification compliance decisions
3. Architecture decisions in conflicting implementations
4. Unknown/undocumented code conflicts

ESCALATION CRITERIA:
- More than 10 files with merge conflicts
- Conflicts in core Beast Mode components
- Specification ambiguity or conflicts
- Uncertain architectural decisions
EOF
  ```

## Phase 2: Merge Execution (1 day)

### Task 2.1: Pre-Merge Setup and Safety Checks
**Estimated Time**: 30 minutes

- [ ] Ensure clean working directory
  ```bash
  git status
  # If uncommitted changes exist:
  git stash push -m "Pre-cleanup stash $(date)"
  ```
- [ ] Switch to master and update
  ```bash
  git checkout master
  git pull origin master
  ```
- [ ] Create pre-merge backup tag
  ```bash
  git tag before-cleanup-merge
  echo "Created backup tag: before-cleanup-merge" >> cleanup-log.txt
  ```
- [ ] Verify repository integrity
  ```bash
  git fsck --full > pre-merge-fsck.txt
  ```

### Task 2.2: Merge rc1-project-cleanup-redo → master
**Estimated Time**: 2-4 hours (depending on conflicts)

- [ ] Create merge branch for safety
  ```bash
  git checkout -b merge-cleanup-redo
  ```
- [ ] Attempt merge
  ```bash
  git merge origin/release/rc1-project-cleanup-redo --no-ff -m "Merge rc1-project-cleanup-redo: foundational cleanup work"
  ```
- [ ] **IF CONFLICTS OCCUR**:
  - [ ] List conflict files
    ```bash
    git status --porcelain | grep "^UU" > current-conflicts.txt
    ```
  - [ ] For each conflict file:
    - [ ] Examine conflict using spec-driven approach
    - [ ] Check for relevant specifications in .kiro/specs/
    - [ ] **IF LOW CONFIDENCE**: Call Ghostbusters for advisory
    - [ ] Resolve using hierarchy: Requirements > Design > Ghostbusters > Implementation
    - [ ] Document resolution rationale
      ```bash
      echo "File: [filename] - Resolution: [rationale]" >> conflict-resolutions.txt
      ```
  - [ ] Mark conflicts resolved
    ```bash
    git add [resolved-files]
    git commit -m "Resolve merge conflicts: [brief description]"
    ```
- [ ] **IF NO CONFLICTS**: Continue to validation

### Task 2.3: Validate Cleanup Merge
**Estimated Time**: 1 hour

- [ ] Basic syntax validation
  ```bash
  find . -name "*.py" -exec python -m py_compile {} \; > syntax-check.txt 2>&1
  ```
- [ ] Check for import errors in key modules
  ```bash
  python -c "import src.beast_mode; print('Beast Mode imports OK')" >> validation-log.txt 2>&1
  python -c "import src.beast_mode.api.main; print('API imports OK')" >> validation-log.txt 2>&1
  ```
- [ ] Run basic smoke tests if available
  ```bash
  # Check if tests exist and were passing
  if [ -f "pytest.ini" ] || [ -f "pyproject.toml" ]; then
    python -m pytest tests/ -x --tb=short > smoke-test-results.txt 2>&1
  fi
  ```
- [ ] Verify key functionality manually
  ```bash
  # Check if key commands work
  make help > make-help-test.txt 2>&1
  python -c "from src.beast_mode.cli import main; print('CLI module loads')" >> validation-log.txt 2>&1
  ```
- [ ] **IF VALIDATION FAILS**:
  - [ ] Document failure
    ```bash
    echo "Validation failed at $(date)" >> cleanup-log.txt
    cat validation-log.txt >> cleanup-log.txt
    ```
  - [ ] Rollback to backup
    ```bash
    git reset --hard before-cleanup-merge
    git branch -D merge-cleanup-redo
    ```
  - [ ] **STOP** and consult Ghostbusters
- [ ] **IF VALIDATION SUCCEEDS**:
  - [ ] Merge to master
    ```bash
    git checkout master
    git merge merge-cleanup-redo --no-ff
    git branch -D merge-cleanup-redo
    ```
  - [ ] Create post-merge backup
    ```bash
    git tag after-cleanup-merge
    ```

### Task 2.4: Merge rc1-final-integration → master
**Estimated Time**: 3-6 hours (depending on conflicts)

- [ ] Create pre-integration backup
  ```bash
  git tag before-integration-merge
  echo "Created backup tag: before-integration-merge" >> cleanup-log.txt
  ```
- [ ] Create merge branch
  ```bash
  git checkout -b merge-final-integration
  ```
- [ ] Attempt merge
  ```bash
  git merge origin/release/rc1-final-integration --no-ff -m "Merge rc1-final-integration: comprehensive integration work"
  ```
- [ ] **IF CONFLICTS OCCUR**:
  - [ ] List conflict files
    ```bash
    git status --porcelain | grep "^UU" > integration-conflicts.txt
    ```
  - [ ] For each conflict file:
    - [ ] Examine conflict using spec-driven approach
    - [ ] Prioritize: Requirements > Design > Ghostbusters > Implementation
    - [ ] **IF COMPLEX OR LOW CONFIDENCE**: Call Ghostbusters
    - [ ] Document resolution rationale
      ```bash
      echo "File: [filename] - Resolution: [rationale]" >> integration-conflict-resolutions.txt
      ```
  - [ ] Mark conflicts resolved and commit
    ```bash
    git add [resolved-files]
    git commit -m "Resolve integration merge conflicts: [brief description]"
    ```

### Task 2.5: Validate Integration Merge
**Estimated Time**: 1.5 hours

- [ ] Comprehensive syntax validation
  ```bash
  find . -name "*.py" -exec python -m py_compile {} \; > integration-syntax-check.txt 2>&1
  ```
- [ ] Import validation for all major modules
  ```bash
  python -c "import src.beast_mode" >> integration-validation.txt 2>&1
  python -c "import src.beast_mode.mcp_integrations.google_calendar" >> integration-validation.txt 2>&1
  python -c "import src.beast_mode.api.main" >> integration-validation.txt 2>&1
  ```
- [ ] Docker infrastructure validation
  ```bash
  cd docker/google-calendar-mcp && docker-compose config > docker-config-check.txt 2>&1
  ```
- [ ] MCP integration smoke test
  ```bash
  # Basic MCP server validation if possible
  python -c "from src.beast_mode.mcp_integrations.google_calendar.auth_manager import AuthManager; print('MCP auth loads')" >> integration-validation.txt 2>&1
  ```
- [ ] Run available test suite
  ```bash
  if [ -f "pytest.ini" ] || [ -f "pyproject.toml" ]; then
    python -m pytest tests/ --tb=short -x > integration-test-results.txt 2>&1
  fi
  ```
- [ ] **IF VALIDATION FAILS**:
  - [ ] Document failure details
  - [ ] Rollback to before-integration-merge
  - [ ] Consult Ghostbusters for resolution strategy
- [ ] **IF VALIDATION SUCCEEDS**:
  - [ ] Merge to master
    ```bash
    git checkout master
    git merge merge-final-integration --no-ff
    git branch -D merge-final-integration
    ```
  - [ ] Create final backup
    ```bash
    git tag integration-complete
    ```

## Phase 3: Cleanup and Documentation (2 hours)

### Task 3.1: Repository Cleanup
**Estimated Time**: 45 minutes

- [ ] Identify obsolete branches
  ```bash
  cat > branch-cleanup-plan.txt << EOF
BRANCHES TO CLEAN UP:
- release/rc1-project-cleanup-redo (merged)
- release/rc1-final-integration (merged)

BRANCHES TO KEEP:
- master (updated)
- develop branches (if active)
- feature branches (if needed)
EOF
  ```
- [ ] Archive merged branches (don't delete immediately)
  ```bash
  git tag archive/rc1-project-cleanup-redo origin/release/rc1-project-cleanup-redo
  git tag archive/rc1-final-integration origin/release/rc1-final-integration
  ```
- [ ] Clean up local branches
  ```bash
  git branch -d merge-cleanup-redo 2>/dev/null || true
  git branch -d merge-final-integration 2>/dev/null || true
  ```
- [ ] Document final repository state
  ```bash
  git branch -a > branch-state-after-cleanup.txt
  git log --oneline --graph --decorate -10 > final-git-graph.txt
  ```

### Task 3.2: Documentation and Handoff
**Estimated Time**: 45 minutes

- [ ] Create cleanup summary report
  ```bash
  cat > cleanup-summary.md << EOF
# Repository Cleanup Summary

## Completed Actions
- Merged rc1-project-cleanup-redo (45 commits) → master
- Merged rc1-final-integration (83 commits) → master
- Total commits integrated: 128 commits

## Conflicts Resolved
[Document any conflicts and their resolutions]

## Validation Results
[Summary of validation results]

## Backup Points Created
- before-cleanup-merge
- after-cleanup-merge
- before-integration-merge
- integration-complete

## Archived Branches
- archive/rc1-project-cleanup-redo
- archive/rc1-final-integration

## Next Steps
1. Team can resume development from clean master
2. Use simple feature branch workflow
3. Regular integration to prevent branch divergence
EOF
  ```
- [ ] Document resolution decisions with spec references
  ```bash
  cat conflict-resolutions.txt integration-conflict-resolutions.txt > all-conflict-resolutions.txt
  ```
- [ ] Create simple ongoing workflow documentation
  ```bash
  cat > ongoing-workflow.md << EOF
# Ongoing Development Workflow

## Branching Strategy
1. Create feature branches from master: git checkout -b feature/name
2. Regular commits with clear messages
3. Merge back to master when complete: git merge --no-ff feature/name
4. Delete feature branch: git branch -d feature/name

## Conflict Prevention
1. Sync with master regularly: git pull origin master
2. Keep feature branches short-lived (< 1 week)
3. Communicate major changes to team
4. Follow specification-driven development

## When Conflicts Occur
1. Check for relevant specifications in .kiro/specs/
2. Follow hierarchy: Requirements > Design > Implementation
3. Consult Ghostbusters for complex decisions
4. Document resolution rationale
EOF
  ```

### Task 3.3: Final Validation and Cleanup
**Estimated Time**: 30 minutes

- [ ] Run final comprehensive validation
  ```bash
  make help > final-make-test.txt 2>&1
  python -c "import src.beast_mode; print('Final import test: OK')" > final-import-test.txt 2>&1
  ```
- [ ] Verify no conflict markers remain
  ```bash
  git grep -r "<<<<<<< \|>>>>>>> \|=======" > remaining-conflicts.txt || echo "No conflict markers found" > remaining-conflicts.txt
  ```
- [ ] Clean up workspace
  ```bash
  # Archive all cleanup files
  tar -czf cleanup-workspace-$(date +%Y%m%d-%H%M%S).tar.gz .cleanup-workspace/
  ```
- [ ] Push clean master to origin
  ```bash
  git push origin master
  git push origin --tags
  ```
- [ ] Create final completion log
  ```bash
  echo "Repository cleanup completed successfully at $(date)" >> cleanup-log.txt
  echo "Master branch now contains integrated work from:" >> cleanup-log.txt
  echo "- rc1-project-cleanup-redo (45 commits)" >> cleanup-log.txt
  echo "- rc1-final-integration (83 commits)" >> cleanup-log.txt
  echo "Total effort: [actual time spent]" >> cleanup-log.txt
  ```

## Emergency Procedures

### If Major Issues Occur
1. **STOP** all merge operations
2. **DO NOT PUSH** to origin
3. **Rollback** to nearest backup tag:
   ```bash
   git reset --hard [backup-tag]
   ```
4. **Document** the issue thoroughly
5. **Consult Ghostbusters** before proceeding

### If Complete Restore Needed
1. **Clone from bundle backup**:
   ```bash
   git clone ../kiro-repo-backup-*.bundle restored-repo
   ```
2. **Verify backup integrity**
3. **Document what went wrong**
4. **Plan alternative approach with Ghostbusters**

### Rollback Commands Reference
```bash
# Rollback to before cleanup merge
git reset --hard before-cleanup-merge

# Rollback to before integration merge
git reset --hard before-integration-merge

# Complete rollback to start
git reset --hard [initial-commit-hash]

# Emergency restore from bundle
git clone ../kiro-repo-backup-*.bundle emergency-restore
```

## Success Criteria Checklist

- [ ] rc1-project-cleanup-redo successfully merged to master
- [ ] rc1-final-integration successfully merged to master
- [ ] No conflict markers remain in repository
- [ ] Basic functionality validated (imports, syntax, key commands)
- [ ] All merge conflicts documented with resolution rationale
- [ ] Backup tags created and verified
- [ ] Obsolete branches archived
- [ ] Team handoff documentation complete
- [ ] Repository ready for normal development workflow

**Estimated Total Time**: 2 days maximum
**Actual Time Spent**: [To be filled during execution]