#!/usr/bin/env python3
"""
Infrastructure Governance Task DAG Validator

This script validates the task dependency graph for the Observatory Cloudflare
Infrastructure Governance implementation, ensuring mathematical correctness
and preventing circular dependencies.
"""

import json
import sys
from typing import Dict, List, Set, Tuple, Optional
from dataclasses import dataclass
from enum import Enum
import networkx as nx
import matplotlib.pyplot as plt
from pathlib import Path

class ValidationResult(Enum):
    VALID = "valid"
    CIRCULAR_DEPENDENCY = "circular_dependency"
    MISSING_DEPENDENCY = "missing_dependency"
    ORPHANED_TASK = "orphaned_task"
    INVALID_PHASE_ORDER = "invalid_phase_order"

@dataclass
class TaskDefinition:
    id: str
    name: str
    dependencies: List[str]
    phase: int
    estimated_duration: int
    requirements: List[str]
    make_target: str

@dataclass
class ValidationIssue:
    issue_type: ValidationResult
    task_id: str
    description: str
    suggested_fix: str

class InfrastructureTaskDAGValidator:
    def __init__(self):
        self.tasks = self._load_task_definitions()
        self.graph = self._build_dependency_graph()
        
    def _load_task_definitions(self) -> Dict[str, TaskDefinition]:
        """Load task definitions from the orchestrator."""
        tasks = {
            # Phase 1: Service Management Foundation
            "1": TaskDefinition(
                id="1",
                name="Service Management Foundation",
                dependencies=[],
                phase=1,
                estimated_duration=30,
                requirements=["5.1", "5.2", "5.3"],
                make_target="infra-task-1"
            ),
            "2.1": TaskDefinition(
                id="2.1",
                name="UnifiedServiceManager Lifecycle",
                dependencies=["1"],
                phase=1,
                estimated_duration=45,
                requirements=["5.1", "5.2", "5.4"],
                make_target="infra-task-2.1"
            ),
            "2.2": TaskDefinition(
                id="2.2",
                name="Service Health Monitoring",
                dependencies=["2.1"],
                phase=1,
                estimated_duration=40,
                requirements=["5.7", "7.1", "7.2"],
                make_target="infra-task-2.2"
            ),
            "2.3": TaskDefinition(
                id="2.3",
                name="Configuration Management",
                dependencies=["2.2"],
                phase=1,
                estimated_duration=35,
                requirements=["6.1", "6.2", "6.5"],
                make_target="infra-task-2.3"
            ),
            
            # Phase 2: Tunnel Management
            "3.1": TaskDefinition(
                id="3.1",
                name="TunnelConfigurationManager",
                dependencies=["2.3"],
                phase=2,
                estimated_duration=50,
                requirements=["1.1", "1.2", "1.3", "1.4"],
                make_target="infra-task-3.1"
            ),
            "3.2": TaskDefinition(
                id="3.2",
                name="Tunnel Deployment",
                dependencies=["3.1"],
                phase=2,
                estimated_duration=40,
                requirements=["1.6", "1.7", "6.3", "6.4"],
                make_target="infra-task-3.2"
            ),
            "3.3": TaskDefinition(
                id="3.3",
                name="Tunnel Health Monitoring",
                dependencies=["3.2"],
                phase=2,
                estimated_duration=35,
                requirements=["7.1", "7.2", "7.3"],
                make_target="infra-task-3.3"
            ),
            
            # Phase 3: WebSocket Monitoring
            "4.1": TaskDefinition(
                id="4.1",
                name="WebSocketHealthMonitor",
                dependencies=["3.3"],
                phase=3,
                estimated_duration=45,
                requirements=["2.1", "2.2", "2.6"],
                make_target="infra-task-4.1"
            ),
            "4.2": TaskDefinition(
                id="4.2",
                name="HTTP Polling Fallback",
                dependencies=["4.1"],
                phase=3,
                estimated_duration=40,
                requirements=["2.3", "2.4", "2.5"],
                make_target="infra-task-4.2"
            ),
            "4.3": TaskDefinition(
                id="4.3",
                name="WebSocket Recovery",
                dependencies=["4.2"],
                phase=3,
                estimated_duration=35,
                requirements=["2.5", "2.6", "2.7"],
                make_target="infra-task-4.3"
            )
        }
        return tasks
    
    def _build_dependency_graph(self) -> nx.DiGraph:
        """Build NetworkX directed graph from task dependencies."""
        graph = nx.DiGraph()
        
        # Add all tasks as nodes
        for task_id, task in self.tasks.items():
            graph.add_node(task_id, **{
                'name': task.name,
                'phase': task.phase,
                'duration': task.estimated_duration,
                'requirements': task.requirements
            })
        
        # Add dependency edges
        for task_id, task in self.tasks.items():
            for dep_id in task.dependencies:
                graph.add_edge(dep_id, task_id)
        
        return graph
    
    def validate_dag(self) -> Tuple[bool, List[ValidationIssue]]:
        """Validate the task dependency graph for mathematical correctness."""
        issues = []
        
        # Check for circular dependencies
        if not nx.is_directed_acyclic_graph(self.graph):
            cycles = list(nx.simple_cycles(self.graph))
            for cycle in cycles:
                issues.append(ValidationIssue(
                    issue_type=ValidationResult.CIRCULAR_DEPENDENCY,
                    task_id=" -> ".join(cycle),
                    description=f"Circular dependency detected: {' -> '.join(cycle)}",
                    suggested_fix="Remove one of the dependencies to break the cycle"
                ))
        
        # Check for missing dependencies
        for task_id, task in self.tasks.items():
            for dep_id in task.dependencies:
                if dep_id not in self.tasks:
                    issues.append(ValidationIssue(
                        issue_type=ValidationResult.MISSING_DEPENDENCY,
                        task_id=task_id,
                        description=f"Task {task_id} depends on non-existent task {dep_id}",
                        suggested_fix=f"Either create task {dep_id} or remove the dependency"
                    ))
        
        # Check for orphaned tasks (no path from root)
        root_tasks = [task_id for task_id, task in self.tasks.items() if not task.dependencies]
        if root_tasks:
            reachable = set()
            for root in root_tasks:
                reachable.update(nx.descendants(self.graph, root))
                reachable.add(root)
            
            for task_id in self.tasks:
                if task_id not in reachable:
                    issues.append(ValidationIssue(
                        issue_type=ValidationResult.ORPHANED_TASK,
                        task_id=task_id,
                        description=f"Task {task_id} is not reachable from any root task",
                        suggested_fix="Add dependencies to connect this task to the main graph"
                    ))
        
        # Check phase ordering consistency
        for task_id, task in self.tasks.items():
            for dep_id in task.dependencies:
                if dep_id in self.tasks:
                    dep_task = self.tasks[dep_id]
                    if dep_task.phase > task.phase:
                        issues.append(ValidationIssue(
                            issue_type=ValidationResult.INVALID_PHASE_ORDER,
                            task_id=task_id,
                            description=f"Task {task_id} (phase {task.phase}) depends on task {dep_id} (phase {dep_task.phase})",
                            suggested_fix="Adjust phase assignments to maintain dependency order"
                        ))
        
        return len(issues) == 0, issues
    
    def get_topological_order(self) -> List[str]:
        """Get topological ordering of tasks (execution order)."""
        if nx.is_directed_acyclic_graph(self.graph):
            return list(nx.topological_sort(self.graph))
        else:
            return []
    
    def get_critical_path(self) -> Tuple[List[str], int]:
        """Calculate critical path (longest path) through the task graph."""
        if not nx.is_directed_acyclic_graph(self.graph):
            return [], 0
        
        # Create a copy with negative weights for longest path calculation
        weighted_graph = self.graph.copy()
        for node in weighted_graph.nodes():
            weighted_graph.nodes[node]['weight'] = -self.tasks[node].estimated_duration
        
        # Find longest path using shortest path with negative weights
        try:
            # Get all root nodes (no predecessors)
            root_nodes = [n for n in weighted_graph.nodes() if weighted_graph.in_degree(n) == 0]
            # Get all leaf nodes (no successors)
            leaf_nodes = [n for n in weighted_graph.nodes() if weighted_graph.out_degree(n) == 0]
            
            longest_path = []
            max_duration = 0
            
            for root in root_nodes:
                for leaf in leaf_nodes:
                    try:
                        path = nx.shortest_path(weighted_graph, root, leaf, weight='weight')
                        duration = sum(self.tasks[node].estimated_duration for node in path)
                        if duration > max_duration:
                            max_duration = duration
                            longest_path = path
                    except nx.NetworkXNoPath:
                        continue
            
            return longest_path, max_duration
        except Exception:
            return [], 0
    
    def get_parallel_execution_groups(self) -> List[List[str]]:
        """Get groups of tasks that can be executed in parallel."""
        if not nx.is_directed_acyclic_graph(self.graph):
            return []
        
        # Use topological generations to find parallel groups
        generations = list(nx.topological_generations(self.graph))
        return generations
    
    def analyze_resource_requirements(self) -> Dict[str, any]:
        """Analyze resource requirements and constraints."""
        total_duration = sum(task.estimated_duration for task in self.tasks.values())
        critical_path, critical_duration = self.get_critical_path()
        parallel_groups = self.get_parallel_execution_groups()
        
        # Calculate maximum parallelism
        max_parallel_tasks = max(len(group) for group in parallel_groups) if parallel_groups else 1
        
        # Calculate efficiency metrics
        efficiency = critical_duration / total_duration if total_duration > 0 else 0
        
        return {
            'total_tasks': len(self.tasks),
            'total_sequential_duration': total_duration,
            'critical_path_duration': critical_duration,
            'critical_path': critical_path,
            'max_parallel_tasks': max_parallel_tasks,
            'parallelization_efficiency': efficiency,
            'parallel_groups': parallel_groups,
            'phases': max(task.phase for task in self.tasks.values())
        }
    
    def generate_execution_plan(self) -> Dict[str, any]:
        """Generate optimized execution plan."""
        is_valid, issues = self.validate_dag()
        if not is_valid:
            return {
                'valid': False,
                'issues': [issue.__dict__ for issue in issues],
                'execution_plan': None
            }
        
        topological_order = self.get_topological_order()
        parallel_groups = self.get_parallel_execution_groups()
        resource_analysis = self.analyze_resource_requirements()
        
        execution_plan = {
            'sequential_order': topological_order,
            'parallel_groups': parallel_groups,
            'critical_path': resource_analysis['critical_path'],
            'estimated_duration': resource_analysis['critical_path_duration'],
            'phases': {}
        }
        
        # Group by phases
        for phase in range(1, resource_analysis['phases'] + 1):
            phase_tasks = [task_id for task_id, task in self.tasks.items() if task.phase == phase]
            phase_duration = sum(self.tasks[task_id].estimated_duration for task_id in phase_tasks)
            
            execution_plan['phases'][phase] = {
                'tasks': phase_tasks,
                'estimated_duration': phase_duration,
                'parallel_groups': [group for group in parallel_groups if any(task in phase_tasks for task in group)]
            }
        
        return {
            'valid': True,
            'issues': [],
            'execution_plan': execution_plan,
            'resource_analysis': resource_analysis
        }
    
    def visualize_dag(self, output_file: str = "infrastructure_task_dag.png"):
        """Generate visual representation of the task DAG."""
        plt.figure(figsize=(16, 12))
        
        # Create layout
        pos = nx.spring_layout(self.graph, k=3, iterations=50)
        
        # Color nodes by phase
        phase_colors = {1: 'lightblue', 2: 'lightgreen', 3: 'lightcoral'}
        node_colors = [phase_colors.get(self.tasks[node].phase, 'lightgray') for node in self.graph.nodes()]
        
        # Draw the graph
        nx.draw(self.graph, pos, 
                with_labels=True, 
                node_color=node_colors,
                node_size=3000,
                font_size=8,
                font_weight='bold',
                arrows=True,
                arrowsize=20,
                edge_color='gray',
                arrowstyle='->')
        
        # Add phase legend
        import matplotlib.patches as mpatches
        phase_patches = [mpatches.Patch(color=color, label=f'Phase {phase}') 
                        for phase, color in phase_colors.items()]
        plt.legend(handles=phase_patches, loc='upper right')
        
        plt.title("Observatory Infrastructure Governance Task Dependency Graph", 
                 fontsize=16, fontweight='bold')
        plt.tight_layout()
        plt.savefig(output_file, dpi=300, bbox_inches='tight')
        print(f"📊 Task DAG visualization saved to {output_file}")
    
    def export_dag_data(self, output_file: str = "infrastructure_task_dag.json"):
        """Export DAG data for external analysis."""
        execution_plan = self.generate_execution_plan()
        
        dag_data = {
            'tasks': {task_id: {
                'name': task.name,
                'dependencies': task.dependencies,
                'phase': task.phase,
                'estimated_duration': task.estimated_duration,
                'requirements': task.requirements,
                'make_target': task.make_target
            } for task_id, task in self.tasks.items()},
            'validation': execution_plan,
            'graph_properties': {
                'nodes': self.graph.number_of_nodes(),
                'edges': self.graph.number_of_edges(),
                'is_dag': nx.is_directed_acyclic_graph(self.graph),
                'density': nx.density(self.graph)
            }
        }
        
        with open(output_file, 'w') as f:
            json.dump(dag_data, f, indent=2)
        
        print(f"📄 DAG data exported to {output_file}")

def main():
    """Main validation function."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Infrastructure Task DAG Validator")
    parser.add_argument("--validate", action="store_true", help="Validate task DAG")
    parser.add_argument("--visualize", action="store_true", help="Generate DAG visualization")
    parser.add_argument("--export", action="store_true", help="Export DAG data")
    parser.add_argument("--execution-plan", action="store_true", help="Generate execution plan")
    parser.add_argument("--all", action="store_true", help="Run all analyses")
    
    args = parser.parse_args()
    
    validator = InfrastructureTaskDAGValidator()
    
    if args.validate or args.all:
        print("🔍 Validating Infrastructure Task DAG...")
        is_valid, issues = validator.validate_dag()
        
        if is_valid:
            print("✅ Task DAG is mathematically valid!")
            print(f"📊 Total tasks: {len(validator.tasks)}")
            print(f"🔗 Total dependencies: {validator.graph.number_of_edges()}")
        else:
            print("❌ Task DAG validation failed!")
            for issue in issues:
                print(f"  • {issue.issue_type.value}: {issue.description}")
                print(f"    Fix: {issue.suggested_fix}")
            sys.exit(1)
    
    if args.execution_plan or args.all:
        print("\n📋 Generating Execution Plan...")
        plan = validator.generate_execution_plan()
        
        if plan['valid']:
            print("✅ Execution plan generated successfully!")
            print(f"⏱️  Estimated total duration: {plan['resource_analysis']['critical_path_duration']} minutes")
            print(f"🎯 Critical path: {' → '.join(plan['execution_plan']['critical_path'])}")
            print(f"⚡ Maximum parallel tasks: {plan['resource_analysis']['max_parallel_tasks']}")
            
            print(f"\n📊 Phase Breakdown:")
            for phase, phase_data in plan['execution_plan']['phases'].items():
                print(f"  Phase {phase}: {len(phase_data['tasks'])} tasks, {phase_data['estimated_duration']} minutes")
        else:
            print("❌ Cannot generate execution plan due to validation issues")
    
    if args.visualize or args.all:
        print("\n🎨 Generating DAG visualization...")
        validator.visualize_dag()
    
    if args.export or args.all:
        print("\n💾 Exporting DAG data...")
        validator.export_dag_data()
    
    if not any([args.validate, args.visualize, args.export, args.execution_plan, args.all]):
        # Default: just validate
        is_valid, issues = validator.validate_dag()
        if is_valid:
            print("✅ Infrastructure Task DAG is valid!")
        else:
            print("❌ Infrastructure Task DAG has issues:")
            for issue in issues:
                print(f"  • {issue.description}")

if __name__ == "__main__":
    main()