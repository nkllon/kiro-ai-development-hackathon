# Git Integration for Task Execution Engine

The Task Execution Engine now includes comprehensive Git branch management to ensure all changes are isolated, tracked, and safely managed.

## Features

### Automatic Session Branch Management
- **Session Branch Creation**: Automatically creates a unique session branch for each execution
- **Random Branch Names**: Generates names like `task-session-20241204-143022-a1b2c3d4`
- **Custom Branch Names**: Use `--branch my-branch-name` to specify a custom branch
- **Original Branch Preservation**: Safely returns to original branch after execution

### Change Tracking
- **Per-Task Commits**: Commits changes after each task completion
- **Progress Tracking**: Maintains detailed execution log with Git operations
- **Remote Backup**: Pushes session branch to remote for safety

### Automatic Resolution
- **Success Handling**: Auto-merges session branch on successful execution (≥80% completion)
- **Failure Handling**: Auto-reverts changes on failed execution
- **Manual Control**: Use `--no-merge` and `--no-revert` flags for manual control

## Usage Examples

### Basic Execution with Git Integration
```bash
# Execute with auto-generated session branch
python cli.py execute

# Execute with custom branch name
python cli.py execute --branch feature/my-enhancement

# Execute without auto-merge (preserve branch)
python cli.py execute --no-merge

# Execute without auto-revert (keep failed changes)
python cli.py execute --no-revert
```

### Testing and Development
```bash
# Dry run (no Git operations)
python cli.py execute --dry-run

# Simulate execution with Git operations
python cli.py execute --simulate --branch test-simulation

# Test Git integration
python test_git_integration.py
```

## Git Workflow

1. **Initialization**
   - Pulls latest changes from current branch
   - Creates new session branch
   - Switches to session branch

2. **During Execution**
   - Commits changes after each completed task
   - Commits failed task states for tracking
   - Pushes session branch to remote periodically

3. **Completion**
   - **Success (≥80% completion)**:
     - Commits final state
     - Switches back to original branch
     - Merges session branch
     - Pushes merged changes
     - Deletes session branch (local and remote)
   
   - **Failure (<80% completion)**:
     - Switches back to original branch
     - Deletes session branch (discards changes)
     - Cleans up remote branch

4. **Error Handling**
   - Reverts all changes on unexpected errors
   - Preserves original branch state
   - Logs all Git operations for debugging

## Configuration Options

### CLI Flags
- `--branch NAME`: Specify custom branch name
- `--no-merge`: Preserve session branch instead of merging
- `--no-revert`: Keep failed changes instead of reverting

### Engine Configuration
```python
engine = TaskExecutionEngine(branch_name="my-branch")
engine.auto_merge = False          # Disable auto-merge
engine.auto_revert_on_failure = False  # Disable auto-revert
```

## Safety Features

- **Isolation**: All changes happen in separate branches
- **Backup**: Session branches are pushed to remote
- **Rollback**: Failed executions are automatically reverted
- **Conflict Detection**: Merge conflicts are detected and reported
- **State Preservation**: Original branch is never modified directly

## Troubleshooting

### Common Issues

1. **Merge Conflicts**
   - Session branch is preserved for manual resolution
   - Check execution results for conflict details

2. **Permission Issues**
   - Ensure Git credentials are configured
   - Check remote repository access

3. **Branch Already Exists**
   - Engine will generate alternative branch name
   - Use `--branch` to specify different name

### Debug Information

Execution results include detailed Git session information:
```json
{
  "git_session": {
    "branch_name": "task-session-20241204-143022-a1b2c3d4",
    "original_branch": "main",
    "status": "merged_and_cleaned",
    "changes_made": true
  }
}
```

## Best Practices

1. **Always use Git integration** for production task execution
2. **Test with `--simulate`** before running actual tasks
3. **Use custom branch names** for feature development
4. **Review execution logs** for Git operation details
5. **Keep session branches** (`--no-merge`) for complex debugging