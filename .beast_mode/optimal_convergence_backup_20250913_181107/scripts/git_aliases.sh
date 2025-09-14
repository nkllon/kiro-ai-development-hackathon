#!/bin/bash
# Systematic Git Workflow Aliases
# Source this file to add convenient aliases

# Snapshot management
alias git-snap='python3 scripts/git_workflow.py snapshot'
alias git-snap-create='python3 scripts/git_workflow.py snapshot create'
alias git-snap-list='python3 scripts/git_workflow.py snapshot list'
alias git-snap-restore='python3 scripts/git_workflow.py snapshot restore'
alias git-snap-delete='python3 scripts/git_workflow.py snapshot delete'

# Feature management
alias git-feat='python3 scripts/git_workflow.py feature'
alias git-feat-create='python3 scripts/git_workflow.py feature create'
alias git-feat-list='python3 scripts/git_workflow.py feature list'

# Systematic commits
alias git-commit-sys='python3 scripts/git_workflow.py commit'

# Quick shortcuts
alias gsnap='git-snap-create'
alias glist='git-snap-list'
alias grestore='git-snap-restore'

echo "🚀 Systematic Git Workflow aliases loaded!"
echo ""
echo "Available commands:"
echo "  git-snap-create <name> [--description 'desc']  - Create snapshot"
echo "  git-snap-list                                   - List snapshots"
echo "  git-snap-restore <name>                         - Restore snapshot"
echo "  git-feat-create <name>                          - Create feature branch"
echo "  git-feat-list                                   - List feature branches"
echo "  git-commit-sys 'message' [--spec 'spec-ref']    - Systematic commit"
echo ""
echo "Quick shortcuts:"
echo "  gsnap <name>     - Quick snapshot"
echo "  glist            - List snapshots"
echo "  grestore <name>  - Quick restore"