#!/usr/bin/env python3
"""
Standalone script to analyze circular dependencies without importing broken modules.
"""

import ast
import sys
from pathlib import Path
from typing import Dict, List, Set


def analyze_circular_dependencies(codebase_path: str) -> List[List[str]]:
    """Analyze circular dependencies in the codebase"""
    import_graph = {}

    print(f"🔍 Scanning {codebase_path} for imports...")

    # Build import graph
    for py_file in Path(codebase_path).rglob("*.py"):
        try:
            with open(py_file, "r") as f:
                content = f.read()

            tree = ast.parse(content)
            imports = []

            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        imports.append(alias.name)
                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        imports.append(node.module)

            import_graph[str(py_file)] = imports

        except Exception as e:
            print(f"Warning: Could not parse {py_file}: {e}")

    print(f"📊 Found {len(import_graph)} files with imports")

    # Find cycles using DFS
    cycles = []
    visited = set()
    rec_stack = set()

    def find_cycle(node, path):
        if node in rec_stack:
            cycle_start = path.index(node)
            cycles.append(path[cycle_start:] + [node])
            return

        if node in visited:
            return

        visited.add(node)
        rec_stack.add(node)

        for neighbor in import_graph.get(node, []):
            find_cycle(neighbor, path + [node])

        rec_stack.remove(node)

    for node in import_graph:
        if node not in visited:
            find_cycle(node, [])

    return cycles


def analyze_specific_issue():
    """Analyze the specific Entity/AggregateRoot issue"""
    print("🎯 Analyzing Entity/AggregateRoot circular dependency...")

    # Check the specific files
    entities_file = Path("src/rm_ddd/domain/entities.py")
    entities_core_file = Path("src/rm_ddd/domain/entities_core.py")
    entities_core_core_file = Path("src/rm_ddd/domain/entities_core_core.py")
    entities_core_core_core_file = Path("src/rm_ddd/domain/entities_core_core_core.py")

    print(f"📁 Checking {entities_file}...")
    if entities_file.exists():
        with open(entities_file, "r") as f:
            content = f.read()
            if "from .entities_core import *" in content:
                print("  ❌ Found problematic import: from .entities_core import *")

    print(f"📁 Checking {entities_core_core_core_file}...")
    if entities_core_core_core_file.exists():
        with open(entities_core_core_core_file, "r") as f:
            content = f.read()
            if "class AggregateRoot(Entity[TAggregateId], ABC):" in content:
                print(
                    "  ❌ Found problematic class definition: AggregateRoot(Entity[TAggregateId])"
                )
                print(
                    "  💡 Issue: Entity is not defined but AggregateRoot tries to inherit from it"
                )

    print("\n🔧 Suggested fixes:")
    print("  1. Remove unused imports from entities_core_core_core.py")
    print("  2. Fix the Entity class definition in entities.py")
    print("  3. Remove the 'core_core_core' pattern - it's broken refactoring")


def main():
    """Main analysis function"""
    print("🚀 Circular Dependency Analysis")
    print("=" * 50)

    # Analyze specific issue first
    analyze_specific_issue()

    print("\n" + "=" * 50)
    print("🔍 Full circular dependency analysis...")

    # Analyze full codebase
    cycles = analyze_circular_dependencies("src")

    print(f"\n📊 Results:")
    print(f"  Found {len(cycles)} circular dependencies")

    if cycles:
        print("\n🚨 Circular dependencies found:")
        for i, cycle in enumerate(cycles[:10]):  # Show first 10
            print(f"  Cycle {i+1}: {' -> '.join(cycle)}")

        if len(cycles) > 10:
            print(f"  ... and {len(cycles) - 10} more cycles")
    else:
        print("  ✅ No circular dependencies found!")

    print("\n💡 Recommendations:")
    print("  1. Fix the 'core_core_core' broken refactoring files")
    print("  2. Remove unused imports")
    print("  3. Implement proper interface definitions")
    print("  4. Use dependency injection instead of direct imports")


if __name__ == "__main__":
    main()
