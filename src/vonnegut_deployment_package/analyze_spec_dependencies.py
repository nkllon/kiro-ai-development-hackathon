#!/usr/bin/env python3
"""
Spec Dependency Analysis - DAG Creation
======================================

Analyzes all specs to create a dependency DAG showing which specs need
to be implemented before others can be completed.

Author: Beast Mode Framework
Date: 2025-01-27
Purpose: Systematic dependency analysis before execution
"""

import sys
import os
from pathlib import Path
from typing import Dict, List, Set, Tuple
import re

# Add project root to path
sys.path.append('.')

from src.rm_ddd.core.dag_registry import DAGRegistry


class SpecDependencyAnalyzer:
    """Analyzes spec dependencies to create execution DAG."""
    
    def __init__(self):
        self.specs_dir = Path(".kiro/specs")
        self.dependencies = {}
        self.spec_status = {}
        self.dag_registry = DAGRegistry()
    
    def analyze_all_specs(self) -> Dict[str, any]:
        """Analyze all specs and create dependency DAG."""
        print("🔍 ANALYZING SPEC DEPENDENCIES")
        print("=" * 35)
        
        # Find all specs
        specs = self._find_all_specs()
        print(f"📊 Found {len(specs)} specs")
        
        # Analyze each spec
        for spec_name in specs:
            self._analyze_spec(spec_name)
        
        # Create dependency DAG
        dag_valid = self._create_dependency_dag()
        
        # Generate execution order
        execution_order = self._get_execution_order()
        
        return {
            'specs': specs,
            'dependencies': self.dependencies,
            'spec_status': self.spec_status,
            'dag_valid': dag_valid,
            'execution_order': execution_order
        }
    
    def _find_all_specs(self) -> List[str]:
        """Find all spec directories."""
        specs = []
        for item in self.specs_dir.iterdir():
            if item.is_dir() and not item.name.startswith('.'):
                specs.append(item.name)
        return sorted(specs)
    
    def _analyze_spec(self, spec_name: str):
        """Analyze a single spec for dependencies and status."""
        spec_path = self.specs_dir / spec_name
        
        # Check spec completeness
        has_requirements = (spec_path / "requirements.md").exists()
        has_design = (spec_path / "design.md").exists()
        has_tasks = (spec_path / "tasks.md").exists()
        
        # Analyze task completion if tasks exist
        completion_rate = 0.0
        if has_tasks:
            completion_rate = self._analyze_task_completion(spec_path / "tasks.md")
        
        # Find dependencies by analyzing content
        dependencies = self._find_spec_dependencies(spec_path)
        
        self.spec_status[spec_name] = {
            'has_requirements': has_requirements,
            'has_design': has_design,
            'has_tasks': has_tasks,
            'completion_rate': completion_rate,
            'is_complete': completion_rate >= 1.0,
            'is_ready': has_requirements and has_design and has_tasks
        }
        
        self.dependencies[spec_name] = dependencies
        
        print(f"📋 {spec_name}:")
        print(f"   Complete: {completion_rate:.1%}")
        print(f"   Dependencies: {dependencies}")
    
    def _analyze_task_completion(self, tasks_file: Path) -> float:
        """Analyze task completion rate."""
        if not tasks_file.exists():
            return 0.0
        
        try:
            content = tasks_file.read_text()
            completed = content.count('- [x]')
            total = completed + content.count('- [ ]')
            return completed / max(total, 1)
        except:
            return 0.0
    
    def _find_spec_dependencies(self, spec_path: Path) -> Set[str]:
        """Find dependencies by analyzing spec content."""
        dependencies = set()
        
        # Patterns to look for
        dependency_patterns = [
            r'llm-cli-discovery',
            r'prepare-spec-for-execution',
            r'beast-mode-.*',
            r'observatory-.*',
            r'dag-orchestrat.*',
            r'reflective-module',
            r'ai-memory-palace',
            r'ace-reporter'
        ]
        
        # Search in all spec files
        for file_path in spec_path.glob("*.md"):
            try:
                content = file_path.read_text().lower()
                
                for pattern in dependency_patterns:
                    matches = re.findall(pattern, content)
                    for match in matches:
                        # Convert to actual spec name
                        potential_spec = match.replace('_', '-')
                        if (self.specs_dir / potential_spec).exists():
                            dependencies.add(potential_spec)
            except:
                continue
        
        return dependencies
    
    def _create_dependency_dag(self) -> bool:
        """Create DAG registry with spec dependencies."""
        print(f"\n🏗️  CREATING DEPENDENCY DAG")
        print("=" * 30)
        
        # Register all specs with their dependencies
        for spec_name, deps in self.dependencies.items():
            success = self.dag_registry.register_module(spec_name, deps)
            if not success:
                print(f"❌ Circular dependency detected: {spec_name}")
                return False
        
        # Validate DAG
        is_valid = self.dag_registry.validate_dag()
        print(f"✅ DAG Valid: {is_valid}")
        
        return is_valid
    
    def _get_execution_order(self) -> List[str]:
        """Get topological execution order."""
        if not self.dag_registry.validate_dag():
            return []
        
        # Simple topological sort
        visited = set()
        result = []
        
        def dfs(spec):
            if spec in visited:
                return
            visited.add(spec)
            
            # Visit dependencies first
            for dep in self.dependencies.get(spec, set()):
                if dep in self.dependencies:  # Only if dep is a known spec
                    dfs(dep)
            
            result.append(spec)
        
        # Process all specs
        for spec in self.dependencies.keys():
            dfs(spec)
        
        return result
    
    def generate_execution_plan(self, analysis: Dict) -> Dict:
        """Generate execution plan based on analysis."""
        print(f"\n🎯 GENERATING EXECUTION PLAN")
        print("=" * 35)
        
        # Categorize specs by readiness
        ready_specs = []
        incomplete_specs = []
        missing_deps = []
        
        for spec_name in analysis['execution_order']:
            status = self.spec_status[spec_name]
            deps = self.dependencies[spec_name]
            
            # Check if dependencies are satisfied
            deps_satisfied = all(
                self.spec_status.get(dep, {}).get('is_complete', False) 
                for dep in deps
                if dep in self.spec_status
            )
            
            if status['is_complete']:
                ready_specs.append(spec_name)
            elif status['is_ready'] and deps_satisfied:
                incomplete_specs.append(spec_name)
            else:
                missing_deps.append(spec_name)
        
        print(f"✅ Complete specs: {len(ready_specs)}")
        print(f"🔄 Ready to execute: {len(incomplete_specs)}")
        print(f"⏳ Waiting on dependencies: {len(missing_deps)}")
        
        return {
            'ready_specs': ready_specs,
            'incomplete_specs': incomplete_specs,
            'missing_deps': missing_deps,
            'next_actions': self._determine_next_actions(incomplete_specs, missing_deps)
        }
    
    def _determine_next_actions(self, incomplete_specs: List[str], missing_deps: List[str]) -> List[Dict]:
        """Determine next actions to take."""
        actions = []
        
        # Priority 1: Complete specs that are ready to execute
        for spec in incomplete_specs:
            actions.append({
                'action': 'execute_spec',
                'spec': spec,
                'priority': 'high',
                'reason': 'All dependencies satisfied, ready to execute'
            })
        
        # Priority 2: Complete missing dependency specs
        for spec in missing_deps:
            status = self.spec_status[spec]
            if not status['is_ready']:
                if not status['has_tasks']:
                    actions.append({
                        'action': 'create_tasks',
                        'spec': spec,
                        'priority': 'medium',
                        'reason': 'Missing tasks.md file'
                    })
                elif not status['has_design']:
                    actions.append({
                        'action': 'create_design',
                        'spec': spec,
                        'priority': 'medium',
                        'reason': 'Missing design.md file'
                    })
        
        return actions


def main():
    """Main execution function."""
    print("🎯 SPEC DEPENDENCY ANALYSIS")
    print("=" * 30)
    
    analyzer = SpecDependencyAnalyzer()
    analysis = analyzer.analyze_all_specs()
    
    if not analysis['dag_valid']:
        print("❌ CIRCULAR DEPENDENCIES DETECTED")
        print("Cannot proceed with execution")
        return 1
    
    # Generate execution plan
    plan = analyzer.generate_execution_plan(analysis)
    
    # Show execution order
    print(f"\n📋 EXECUTION ORDER:")
    for i, spec in enumerate(analysis['execution_order'], 1):
        status = analyzer.spec_status[spec]
        completion = status['completion_rate']
        ready = "✅" if status['is_complete'] else "🔄" if status['is_ready'] else "⏳"
        print(f"   {i:2d}. {ready} {spec} ({completion:.1%})")
    
    # Show next actions
    print(f"\n🚀 NEXT ACTIONS:")
    for action in plan['next_actions'][:5]:  # Show top 5
        print(f"   • {action['action']}: {action['spec']} - {action['reason']}")
    
    # Focus on DAG orchestration dependencies
    dag_spec = 'dag-orchestrated-parallel-execution'
    if dag_spec in analysis['dependencies']:
        print(f"\n🎯 DAG ORCHESTRATION DEPENDENCIES:")
        deps = analysis['dependencies'][dag_spec]
        for dep in deps:
            if dep in analyzer.spec_status:
                status = analyzer.spec_status[dep]
                ready = "✅" if status['is_complete'] else "❌"
                print(f"   {ready} {dep} ({status['completion_rate']:.1%})")
    
    return 0


if __name__ == "__main__":
    exit(main())