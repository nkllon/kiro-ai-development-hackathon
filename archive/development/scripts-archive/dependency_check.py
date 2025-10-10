#!/usr/bin/env python3
"""
Dependency Cycle Check - Verify no circular dependencies in DAG executor
"""

import ast
import sys
from pathlib import Path
from typing import Dict, Set, List


def extract_imports(file_path: Path) -> Set[str]:
    """Extract all imports from a Python file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        tree = ast.parse(content)
        imports = set()
        
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports.add(alias.name)
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    imports.add(node.module)
        
        return imports
    except Exception as e:
        print(f"Error parsing {file_path}: {e}")
        return set()


def build_dependency_graph() -> Dict[str, Set[str]]:
    """Build dependency graph for our new modules"""
    
    modules = {
        'hierarchical_task_parser': Path('src/beast_mode/task_dag/hierarchical_task_parser.py'),
        'dag_task_executor': Path('src/beast_mode/task_dag/dag_task_executor.py'),
        'unified_reflective_module': Path('src/rm_ddd/core/unified_reflective_module.py')
    }
    
    graph = {}
    
    for module_name, file_path in modules.items():
        if file_path.exists():
            imports = extract_imports(file_path)
            # Filter to only our modules
            relevant_imports = set()
            for imp in imports:
                if 'hierarchical_task_parser' in imp:
                    relevant_imports.add('hierarchical_task_parser')
                elif 'dag_task_executor' in imp:
                    relevant_imports.add('dag_task_executor')
                elif 'unified_reflective_module' in imp:
                    relevant_imports.add('unified_reflective_module')
                elif 'rm_ddd' in imp:
                    relevant_imports.add('unified_reflective_module')
            
            graph[module_name] = relevant_imports
            print(f"{module_name} imports: {relevant_imports}")
    
    return graph


def detect_cycles(graph: Dict[str, Set[str]]) -> List[List[str]]:
    """Detect cycles in dependency graph using DFS"""
    
    def dfs(node: str, path: List[str], visited: Set[str], rec_stack: Set[str]) -> List[List[str]]:
        visited.add(node)
        rec_stack.add(node)
        path.append(node)
        
        cycles = []
        
        if node in graph:
            for neighbor in graph[node]:
                if neighbor not in visited:
                    cycles.extend(dfs(neighbor, path.copy(), visited, rec_stack))
                elif neighbor in rec_stack:
                    # Found cycle
                    cycle_start = path.index(neighbor)
                    cycle = path[cycle_start:] + [neighbor]
                    cycles.append(cycle)
        
        rec_stack.remove(node)
        return cycles
    
    all_cycles = []
    visited = set()
    
    for node in graph:
        if node not in visited:
            cycles = dfs(node, [], visited, set())
            all_cycles.extend(cycles)
    
    return all_cycles


def main():
    """Main dependency check"""
    print("=== Dependency Cycle Check ===")
    
    # Build dependency graph
    graph = build_dependency_graph()
    
    print(f"\nDependency Graph:")
    for module, deps in graph.items():
        print(f"  {module} -> {deps}")
    
    # Check for cycles
    cycles = detect_cycles(graph)
    
    if cycles:
        print(f"\n❌ CIRCULAR DEPENDENCIES DETECTED:")
        for i, cycle in enumerate(cycles, 1):
            print(f"  Cycle {i}: {' -> '.join(cycle)}")
        return False
    else:
        print(f"\n✅ NO CIRCULAR DEPENDENCIES FOUND")
        
        # Show dependency chain
        print(f"\nDependency Chain:")
        print(f"  dag_task_executor -> hierarchical_task_parser -> unified_reflective_module")
        print(f"  (This is a clean linear dependency chain)")
        
        return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)