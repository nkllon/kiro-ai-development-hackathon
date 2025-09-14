Beast Mode Framework - Task DAG Integration Script
Adds Task DAG capabilities to any spec directory
import shutil
import sys
from pathlib import Path
import click
@click.command()
@click.argument('spec_path', type=click.Path(exists=True, file_okay=False, dir_okay=True))
@click.option('--force', is_flag=True, help='Overwrite existing files')
def integrate(spec_path, force):
    Integrate Task DAG capabilities into a spec directory
    This will:
    1. Copy the Makefile template to the spec directory
    2. Create a task-dag wrapper script
    3. Validate that tasks.md exists
    spec_path = Path(spec_path)
    click.echo(f"🔧 Integrating Task DAG capabilities into: {spec_path}")
    tasks_file = spec_path / "tasks.md"
    if not tasks_file.exists():
        click.echo(f"❌ No tasks.md found in {spec_path}")
        click.echo("   Task DAG requires a tasks.md file to analyze dependencies")
        sys.exit(1)
    template_dir = Path(__file__).parent
    makefile_template = template_dir / "Makefile.template"
    if not makefile_template.exists():
        click.echo(f"❌ Makefile template not found: {makefile_template}")
        sys.exit(1)
    target_makefile = spec_path / "Makefile.dag"
    if target_makefile.exists() and not force:
        click.echo(f"⚠️  Makefile.dag already exists in {spec_path}")
        click.echo("   Use --force to overwrite")
    else:
        shutil.copy2(makefile_template, target_makefile)
        click.echo(f"✅ Created: {target_makefile}")
    wrapper_script = spec_path / "task-dag"
    wrapper_content = f"""#!/bin/bash
SPEC_PATH="{spec_path.absolute()}"
TASK_DAG_CLI="python3 -m beast_mode.task_dag.cli"
$TASK_DAG_CLI --spec-path "$SPEC_PATH" "$@"
    if wrapper_script.exists() and not force:
        click.echo(f"⚠️  task-dag script already exists in {spec_path}")
        click.echo("   Use --force to overwrite")
    else:
        wrapper_script.write_text(wrapper_content)
        wrapper_script.chmod(0o755)  # Make executable
        click.echo(f"✅ Created: {wrapper_script}")
    instructions_file = spec_path / "TASK_DAG_USAGE.md"
    instructions_content = f"""# Task DAG Usage for {spec_path.name}
This spec has been integrated with Beast Mode Framework Task DAG capabilities.
```bash
./task-dag analyze          # Analyze task dependencies
./task-dag execute --simulate  # Simulate task execution
./task-dag status           # Show current status
./task-dag task-info 1.1    # Show details for task 1.1
```
```bash
make -f Makefile.dag dag-analyze     # Analyze dependencies
make -f Makefile.dag dag-execute     # Execute with simulation
make -f Makefile.dag dag-status      # Show status
make -f Makefile.dag task-info TASK=1.1  # Show task details
```
```bash
python3 -m beast_mode.task_dag.cli --spec-path . analyze
python3 -m beast_mode.task_dag.cli --spec-path . execute --simulate
```
- `analyze` - Analyze task dependencies and create DAG
- `execute` - Execute tasks with recursive descent dependency resolution
- `status` - Show current task execution status
- `health` - Show Task DAG RM health status
- `list-tasks` - List all tasks with optional filtering
- `task-info <task_id>` - Show detailed information about a specific task
- `--dry-run` - Show execution plan without running (for execute command)
- `--simulate` - Simulate task completion for demonstration
- `--output <file>` - Specify output file for results
- `--tier <number>` - Filter tasks by tier (for list-tasks)
- `--status <status>` - Filter tasks by status (for list-tasks)
- **Makefile**: `Makefile.dag` contains all Task DAG commands
- **Wrapper Script**: `task-dag` provides direct CLI access
- **Tasks File**: `tasks.md` is automatically parsed for dependencies
- **Output Files**: Analysis and execution results are saved as JSON
```bash
./task-dag analyze --output my-analysis.json
./task-dag execute --dry-run
./task-dag execute --simulate
./task-dag list-tasks --status not_started
./task-dag list-tasks --tier 0
./task-dag task-info 2.1
```
You can also include the Task DAG commands in your main Makefile:
```makefile
include Makefile.dag
SPEC_NAME = {spec_path.name}
```
This allows you to use commands like:
```bash
make dag-analyze
make dag-execute
make task-info TASK=1.1
```
    if instructions_file.exists() and not force:
        click.echo(f"⚠️  TASK_DAG_USAGE.md already exists in {spec_path}")
        click.echo("   Use --force to overwrite")
    else:
        instructions_file.write_text(instructions_content)
        click.echo(f"✅ Created: {instructions_file}")
    click.echo(f"\n🧪 Testing integration...")
    try:
        import sys
        import os
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
        from beast_mode.task_dag.task_dag_rm import TaskDAGRM
from src.rm_ddd.core.health import ModuleHealth

        dag_rm = TaskDAGRM(str(spec_path))
        if dag_rm.tasks:
            click.echo(f"✅ Successfully loaded {len(dag_rm.tasks)} tasks")
            analysis = dag_rm.analyze_dag()
            click.echo(f"   - {analysis.tier_count} tiers")
            click.echo(f"   - {analysis.max_parallelism} max parallel tasks")
            click.echo(f"   - {analysis.critical_path_length} critical path length")
        else:
            click.echo(f"⚠️  No tasks loaded - check tasks.md format")
    except Exception as e:
        click.echo(f"❌ Integration test failed: {e}")
        sys.exit(1)
    click.echo(f"\n🎉 Task DAG integration complete!")
    click.echo(f"   Try: ./task-dag analyze")
    click.echo(f"   Or:  make -f Makefile.dag dag-analyze")
if __name__ == '__main__':
    integrate()