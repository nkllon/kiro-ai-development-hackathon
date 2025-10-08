#!/usr/bin/env python3
"""
Simple Hybrid Task Executor - DeepSeek + Claude

Usage:
    python scripts/hybrid_task_executor.py .kiro/specs/test-hybrid-executor
"""

import sys
import re
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.hybrid_code_generator import run_code_generation


def parse_tasks_from_md(tasks_file: Path):
    """Simple parser for tasks.md files"""
    tasks = []
    content = tasks_file.read_text()

    # Find all task lines: - [ ] 1. Task description
    task_pattern = re.compile(r'^- \[([ x])\] (\d+|[\*\d]+)\.\s+(.+)$', re.MULTILINE)

    for match in task_pattern.finditer(content):
        completed = match.group(1) == 'x'
        task_id = match.group(2)
        description = match.group(3)

        if not completed:  # Only return uncompleted tasks
            tasks.append({
                'id': task_id,
                'description': description,
                'completed': completed
            })

    return tasks


def load_spec_context(spec_dir: Path) -> str:
    """Load requirements and design context"""
    context_parts = []

    requirements_file = spec_dir / "requirements.md"
    design_file = spec_dir / "design.md"

    if requirements_file.exists():
        context_parts.append(f"## Requirements\n{requirements_file.read_text()}")

    if design_file.exists():
        context_parts.append(f"## Design\n{design_file.read_text()}")

    return "\n\n".join(context_parts) if context_parts else "Follow Python best practices"


def mark_task_completed(tasks_file: Path, task_id: str):
    """Mark task as completed in tasks.md"""
    content = tasks_file.read_text()

    # Replace - [ ] with - [x] for this task ID
    pattern = rf'^- \[ \] {re.escape(task_id)}\.'
    replacement = f'- [x] {task_id}.'

    updated_content = re.sub(pattern, replacement, content, flags=re.MULTILINE)
    tasks_file.write_text(updated_content)


def main():
    if len(sys.argv) < 2:
        print("Usage: python scripts/hybrid_task_executor.py <spec_directory>")
        print("Example: python scripts/hybrid_task_executor.py .kiro/specs/test-hybrid-executor")
        sys.exit(1)

    spec_dir = Path(sys.argv[1])

    if not spec_dir.exists():
        print(f"Error: Spec directory not found: {spec_dir}")
        sys.exit(1)

    tasks_file = spec_dir / "tasks.md"
    if not tasks_file.exists():
        print(f"Error: tasks.md not found in {spec_dir}")
        sys.exit(1)

    print(f"🐺⚡ HYBRID TASK EXECUTOR")
    print(f"Spec: {spec_dir.name}")
    print("=" * 80)

    # Load tasks
    tasks = parse_tasks_from_md(tasks_file)
    print(f"\n📋 Found {len(tasks)} uncompleted tasks\n")

    if not tasks:
        print("✅ All tasks completed!")
        return

    # Load spec context
    spec_context = load_spec_context(spec_dir)

    # Execute each task
    for i, task in enumerate(tasks, 1):
        print(f"\n{'='*80}")
        print(f"🤖 TASK {i}/{len(tasks)}: {task['description'][:60]}...")
        print(f"{'='*80}\n")

        try:
            # Run hybrid workflow
            result = run_code_generation(
                task_description=task['description'],
                spec_requirements=spec_context
            )

            # Save generated code
            if result.get('final_code') or result.get('generated_code'):
                code = result.get('final_code', result.get('generated_code'))

                # Save to file
                safe_task_id = task['id'].replace('.', '_').replace('*', '').replace(' ', '_')
                output_file = spec_dir / f"generated_task_{safe_task_id}.py"
                output_file.write_text(code)

                print(f"\n✅ COMPLETED!")
                print(f"   Iterations: {result.get('iteration_count', 0)}")
                print(f"   Status: {result.get('approval_status', 'unknown')}")
                print(f"   Code saved to: {output_file}")

                # Mark as completed
                mark_task_completed(tasks_file, task['id'])

            else:
                print(f"\n⚠️  No code generated")

        except KeyboardInterrupt:
            print(f"\n\n⚠️  Interrupted by user")
            break
        except Exception as e:
            print(f"\n❌ ERROR: {e}")
            import traceback
            traceback.print_exc()
            continue

    print(f"\n{'='*80}")
    print("🎯 EXECUTION COMPLETE")
    print(f"{'='*80}\n")


if __name__ == "__main__":
    main()
