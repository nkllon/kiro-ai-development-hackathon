#!/usr/bin/env python3
"""
CLI to run hybrid code generator on Kiro spec tasks
"""

import sys
import argparse
from hybrid_code_generator import run_code_generation


def extract_task_from_spec(spec_path: str, task_index: int = 0) -> tuple:
    """Extract a specific task from a Kiro spec tasks.md file"""
    with open(spec_path, 'r') as f:
        content = f.read()

    # Simple parser - extract task items
    # In real implementation, would parse markdown structure properly
    lines = content.split('\n')
    tasks = []
    current_task = []

    for line in lines:
        if line.strip().startswith('- ['):
            if current_task:
                tasks.append('\n'.join(current_task))
            current_task = [line]
        elif current_task and line.strip():
            current_task.append(line)

    if current_task:
        tasks.append('\n'.join(current_task))

    if task_index >= len(tasks):
        print(f"Error: Task index {task_index} not found (only {len(tasks)} tasks)")
        sys.exit(1)

    # Extract task description
    task_text = tasks[task_index]
    requirements = "Follow Python best practices. Include type hints and docstrings."

    return task_text, requirements


def main():
    parser = argparse.ArgumentParser(description="Hybrid Code Generator - DeepSeek + Claude")
    parser.add_argument('--spec', type=str, help='Path to Kiro spec tasks.md file')
    parser.add_argument('--task-index', type=int, default=0, help='Task index to generate (default: 0)')
    parser.add_argument('--task', type=str, help='Direct task description (alternative to --spec)')
    parser.add_argument('--output', type=str, help='Output file for generated code')

    args = parser.parse_args()

    if args.spec:
        print(f"📖 Loading task from spec: {args.spec}")
        task_description, requirements = extract_task_from_spec(args.spec, args.task_index)
    elif args.task:
        task_description = args.task
        requirements = "Follow Python best practices."
    else:
        parser.print_help()
        sys.exit(1)

    # Run the workflow
    result = run_code_generation(task_description, requirements)

    # Save output if requested
    if args.output:
        final_code = result.get('final_code', result.get('generated_code', ''))
        with open(args.output, 'w') as f:
            f.write(final_code)
        print(f"\n💾 Code saved to: {args.output}")

    return result


if __name__ == "__main__":
    main()
