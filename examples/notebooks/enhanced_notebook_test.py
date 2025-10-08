#!/usr/bin/env python3
"""
Enhanced notebook testing with execution validation.
Tests that code cells can actually run.
"""

import json
import sys
from pathlib import Path
from typing import Dict, List, Any
import warnings

# Suppress warnings for cleaner output
warnings.filterwarnings('ignore')


def test_notebook_execution(notebook_path: Path) -> Dict[str, Any]:
    """Test notebook by executing its code cells."""

    print(f"\n{'='*70}")
    print(f"Testing: {notebook_path.stem}")
    print(f"{'='*70}")

    with open(notebook_path, 'r') as f:
        nb = json.load(f)

    results = {
        'notebook': notebook_path.stem,
        'total_cells': len(nb['cells']),
        'code_cells': 0,
        'passed': 0,
        'failed': 0,
        'skipped': 0,
        'errors': []
    }

    # Create execution namespace
    exec_globals = {'__name__': '__notebook__'}

    # Execute each code cell
    for i, cell in enumerate(nb['cells']):
        if cell['cell_type'] != 'code':
            continue

        results['code_cells'] += 1
        code = ''.join(cell['source']).strip()

        if not code:
            results['skipped'] += 1
            print(f"  Cell {i}: ⏭️  SKIP (empty)")
            continue

        # Skip cells with interactive displays or plots
        if any(keyword in code for keyword in ['plt.show()', 'display(', 'IPython', 'get_ipython']):
            results['skipped'] += 1
            print(f"  Cell {i}: ⏭️  SKIP (interactive)")
            continue

        try:
            print(f"  Cell {i}: ", end="")
            exec(code, exec_globals)
            results['passed'] += 1
            print("✅ PASS")
        except Exception as e:
            results['failed'] += 1
            error_type = type(e).__name__
            error_msg = str(e)[:80]
            results['errors'].append(f"Cell {i}: {error_type}: {error_msg}")
            print(f"❌ FAIL ({error_type})")

    return results


def test_notebook_structure(notebook_path: Path) -> Dict[str, Any]:
    """Test notebook structure and metadata."""

    with open(notebook_path, 'r') as f:
        nb = json.load(f)

    checks = {
        'has_cells': len(nb.get('cells', [])) > 0,
        'has_markdown': any(c['cell_type'] == 'markdown' for c in nb.get('cells', [])),
        'has_code': any(c['cell_type'] == 'code' for c in nb.get('cells', [])),
        'has_title': False,
        'has_content': len(nb.get('cells', [])) >= 3
    }

    # Check for title in first cell
    if nb.get('cells') and nb['cells'][0]['cell_type'] == 'markdown':
        first_cell = ''.join(nb['cells'][0]['source'])
        checks['has_title'] = first_cell.startswith('#')

    return checks


def main():
    """Test all demonstration notebooks."""

    print("\n🧪 Beast Mode Notebook Test Suite")
    print("="*70)

    # Find our main demo notebooks
    notebook_dir = Path(__file__).parent
    demo_notebooks = [
        'constellation_orchestrator_demo.ipynb',
        'ai_memory_palace_demo.ipynb',
        'reflective_module_demo.ipynb',
        'langgraph_workflows_demo.ipynb'
    ]

    all_results = []

    for notebook_name in demo_notebooks:
        notebook_path = notebook_dir / notebook_name

        if not notebook_path.exists():
            print(f"\n❌ {notebook_name} not found!")
            continue

        # Test structure
        structure = test_notebook_structure(notebook_path)

        # Test execution
        execution = test_notebook_execution(notebook_path)

        all_results.append({
            'name': notebook_name,
            'structure': structure,
            'execution': execution
        })

    # Summary
    print(f"\n{'='*70}")
    print("TEST SUMMARY")
    print(f"{'='*70}\n")

    for result in all_results:
        name = result['name']
        struct = result['structure']
        exec_res = result['execution']

        # Overall status
        struct_ok = all(struct.values())
        exec_ok = exec_res['failed'] == 0
        overall_ok = struct_ok and exec_ok

        status = "✅" if overall_ok else "❌"
        print(f"{status} {name}")

        # Structure checks
        if not struct_ok:
            print(f"     Structure issues:")
            for check, passed in struct.items():
                if not passed:
                    print(f"       ❌ {check}")

        # Execution stats
        total_exec = exec_res['passed'] + exec_res['failed']
        if total_exec > 0:
            success_rate = (exec_res['passed'] / total_exec) * 100
            print(f"     Execution: {exec_res['passed']}/{total_exec} passed ({success_rate:.0f}%)")

            if exec_res['skipped'] > 0:
                print(f"     Skipped: {exec_res['skipped']} cells")

            if exec_res['failed'] > 0:
                print(f"     Failed cells: {exec_res['failed']}")
                # Show first few errors
                for error in exec_res['errors'][:2]:
                    print(f"       • {error}")
                if len(exec_res['errors']) > 2:
                    print(f"       ... and {len(exec_res['errors']) - 2} more")

        print()

    # Overall statistics
    total_passed = sum(r['execution']['passed'] for r in all_results)
    total_failed = sum(r['execution']['failed'] for r in all_results)
    total_tests = total_passed + total_failed

    print(f"{'='*70}")
    if total_tests > 0:
        success_rate = (total_passed / total_tests) * 100
        print(f"Overall: {total_passed}/{total_tests} tests passed ({success_rate:.1f}%)")
    else:
        print(f"No executable tests found")
    print(f"{'='*70}\n")

    return 0 if total_failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
