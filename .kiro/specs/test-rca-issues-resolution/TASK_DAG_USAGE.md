# Task DAG Usage for test-rca-issues-resolution

This spec has been integrated with Beast Mode Framework Task DAG capabilities.

## Quick Start

### Using the wrapper script:
```bash
./task-dag analyze          # Analyze task dependencies
./task-dag execute --simulate  # Simulate task execution
./task-dag status           # Show current status
./task-dag task-info 1.1    # Show details for task 1.1
```

### Using the Makefile:
```bash
make -f Makefile.dag dag-analyze     # Analyze dependencies
make -f Makefile.dag dag-execute     # Execute with simulation
make -f Makefile.dag dag-status      # Show status
make -f Makefile.dag task-info TASK=1.1  # Show task details
```

### Using the CLI directly:
```bash
python3 -m beast_mode.task_dag.cli --spec-path . analyze
python3 -m beast_mode.task_dag.cli --spec-path . execute --simulate
```

## Available Commands

- `analyze` - Analyze task dependencies and create DAG
- `execute` - Execute tasks with recursive descent dependency resolution
- `status` - Show current task execution status
- `health` - Show Task DAG RM health status
- `list-tasks` - List all tasks with optional filtering
- `task-info <task_id>` - Show detailed information about a specific task

## Command Options

- `--dry-run` - Show execution plan without running (for execute command)
- `--simulate` - Simulate task completion for demonstration
- `--output <file>` - Specify output file for results
- `--tier <number>` - Filter tasks by tier (for list-tasks)
- `--status <status>` - Filter tasks by status (for list-tasks)

## Integration Details

- **Makefile**: `Makefile.dag` contains all Task DAG commands
- **Wrapper Script**: `task-dag` provides direct CLI access
- **Tasks File**: `tasks.md` is automatically parsed for dependencies
- **Output Files**: Analysis and execution results are saved as JSON

## Examples

```bash
# Analyze dependencies and export to custom file
./task-dag analyze --output my-analysis.json

# Execute with dry run first
./task-dag execute --dry-run
./task-dag execute --simulate

# List only ready tasks
./task-dag list-tasks --status not_started

# Show tasks in tier 0 (no dependencies)
./task-dag list-tasks --tier 0

# Get detailed info about a specific task
./task-dag task-info 2.1
```

## Makefile Integration

You can also include the Task DAG commands in your main Makefile:

```makefile
# Include Task DAG capabilities
include Makefile.dag

# Override spec name if needed
SPEC_NAME = test-rca-issues-resolution
```

This allows you to use commands like:
```bash
make dag-analyze
make dag-execute
make task-info TASK=1.1
```
