#!/usr/bin/env python3
"""
Specification Readiness Analysis
================================

Analyzes all specifications to determine which are ready for preparation
versus which ones need more work.

Author: Beast Mode Framework
Date: 2025-01-27
Version: 1.0
"""

import sys
from pathlib import Path
from typing import Dict, List, Tuple, Optional
import re

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

def analyze_spec_completeness(spec_path: Path) -> Dict[str, any]:
    """Analyze a single specification for completeness."""
    spec_name = spec_path.name
    
    # Check for required files
    requirements_file = spec_path / "requirements.md"
    design_file = spec_path / "design.md"
    tasks_file = spec_path / "tasks.md"
    
    analysis = {
        'name': spec_name,
        'path': str(spec_path),
        'has_requirements': requirements_file.exists(),
        'has_design': design_file.exists(),
        'has_tasks': tasks_file.exists(),
        'requirements_count': 0,
        'design_sections': 0,
        'task_count': 0,
        'completed_tasks': 0,
        'completeness_score': 0.0,
        'readiness_status': 'incomplete',
        'missing_components': [],
        'issues': []
    }
    
    # Analyze requirements
    if requirements_file.exists():
        try:
            content = requirements_file.read_text()
            # Count requirements (### Requirement patterns)
            req_matches = re.findall(r'^###\s+Requirement\s+\d+', content, re.MULTILINE)
            analysis['requirements_count'] = len(req_matches)
            
            # Check for user stories and acceptance criteria
            if 'User Story:' not in content:
                analysis['issues'].append('Missing user stories in requirements')
            if 'Acceptance Criteria' not in content:
                analysis['issues'].append('Missing acceptance criteria in requirements')
        except Exception as e:
            analysis['issues'].append(f'Error reading requirements: {e}')
    else:
        analysis['missing_components'].append('requirements.md')
    
    # Analyze design
    if design_file.exists():
        try:
            content = design_file.read_text()
            # Count design sections (## patterns)
            section_matches = re.findall(r'^##\s+[^#]', content, re.MULTILINE)
            analysis['design_sections'] = len(section_matches)
            
            # Check for key design sections
            key_sections = ['Overview', 'Architecture', 'Components', 'Implementation']
            missing_sections = [s for s in key_sections if s not in content]
            if missing_sections:
                analysis['issues'].append(f'Missing design sections: {", ".join(missing_sections)}')
        except Exception as e:
            analysis['issues'].append(f'Error reading design: {e}')
    else:
        analysis['missing_components'].append('design.md')
    
    # Analyze tasks
    if tasks_file.exists():
        try:
            content = tasks_file.read_text()
            # Count tasks (- [ ] or - [x] or - [-] patterns)
            task_matches = re.findall(r'^(\s*)-\s*\[([x\-\s])\]', content, re.MULTILINE)
            analysis['task_count'] = len(task_matches)
            
            # Count completed tasks
            completed = [m for m in task_matches if m[1].lower() == 'x']
            analysis['completed_tasks'] = len(completed)
            
            # Check for requirements references
            if '_Requirements:' not in content:
                analysis['issues'].append('Tasks missing requirements references')
        except Exception as e:
            analysis['issues'].append(f'Error reading tasks: {e}')
    else:
        analysis['missing_components'].append('tasks.md')
    
    # Calculate completeness score
    score = 0
    max_score = 100
    
    # File existence (30 points)
    if analysis['has_requirements']:
        score += 10
    if analysis['has_design']:
        score += 10
    if analysis['has_tasks']:
        score += 10
    
    # Content quality (70 points)
    if analysis['requirements_count'] > 0:
        score += min(20, analysis['requirements_count'] * 4)  # Up to 20 points
    
    if analysis['design_sections'] > 0:
        score += min(25, analysis['design_sections'] * 5)  # Up to 25 points
    
    if analysis['task_count'] > 0:
        score += min(25, analysis['task_count'] * 2)  # Up to 25 points
    
    analysis['completeness_score'] = min(score / max_score, 1.0)
    
    # Determine readiness status
    if analysis['completeness_score'] >= 0.8 and len(analysis['missing_components']) == 0:
        analysis['readiness_status'] = 'ready'
    elif analysis['completeness_score'] >= 0.6:
        analysis['readiness_status'] = 'needs_work'
    else:
        analysis['readiness_status'] = 'incomplete'
    
    return analysis


def categorize_specs_by_priority() -> Dict[str, List[str]]:
    """Categorize specs by implementation priority."""
    return {
        'critical_infrastructure': [
            'beast-mode-rebuild',
            'beast-mode-reliability-requirements',
            'reflective-module-architecture-consolidation',
            'unified-dag-registry',
            'dag-orchestrated-parallel-execution'
        ],
        'core_functionality': [
            'atomic-spec-execution-pattern',
            'spec-framework',
            'prepare-spec-for-execution',
            'observatory-deployment-procedures',
            'repository-setup-and-installation'
        ],
        'integration_systems': [
            'directus-cms-systematic-implementation',
            'mcp-development-framework',
            'observatory-cloudflare-infrastructure-governance',
            'websocket-implementation-validation'
        ],
        'monitoring_observability': [
            'beast-mode-coordination-observatory',
            'observatory-editorial-intelligence',
            'prometheus-monitoring-system-repair',
            'observatory-performance-chart'
        ],
        'productivity_tools': [
            'comprehensive-makefile-system',
            'multi-dimensional-vocabulary-projector',
            'documentation-index-generator',
            'practical-repository-cleanup'
        ],
        'examples_training': [
            'example-simple-api',
            'example-complex-system'
        ]
    }


def main():
    """Analyze all specifications and generate readiness report."""
    print("🔍 Specification Readiness Analysis")
    print("=" * 60)
    
    specs_dir = Path(".kiro/specs")
    if not specs_dir.exists():
        print("❌ .kiro/specs directory not found")
        return 1
    
    # Get all spec directories
    spec_dirs = [d for d in specs_dir.iterdir() if d.is_dir() and not d.name.startswith('.')]
    spec_dirs.sort()
    
    print(f"Found {len(spec_dirs)} specifications")
    print()
    
    # Analyze each spec
    analyses = []
    for spec_dir in spec_dirs:
        analysis = analyze_spec_completeness(spec_dir)
        analyses.append(analysis)
    
    # Categorize by readiness
    ready_specs = [a for a in analyses if a['readiness_status'] == 'ready']
    needs_work_specs = [a for a in analyses if a['readiness_status'] == 'needs_work']
    incomplete_specs = [a for a in analyses if a['readiness_status'] == 'incomplete']
    
    # Get priority categories
    priority_categories = categorize_specs_by_priority()
    
    print("📊 READINESS SUMMARY")
    print("=" * 60)
    print(f"✅ Ready for Preparation: {len(ready_specs)}")
    print(f"⚠️ Needs Work: {len(needs_work_specs)}")
    print(f"❌ Incomplete: {len(incomplete_specs)}")
    print()
    
    # Show ready specs
    if ready_specs:
        print("🚀 READY FOR PREPARATION")
        print("=" * 40)
        for spec in sorted(ready_specs, key=lambda x: x['completeness_score'], reverse=True):
            priority = "Unknown"
            for cat, specs in priority_categories.items():
                if spec['name'] in specs:
                    priority = cat.replace('_', ' ').title()
                    break
            
            print(f"✅ {spec['name']}")
            print(f"   Score: {spec['completeness_score']:.1%}")
            print(f"   Priority: {priority}")
            print(f"   Components: {spec['requirements_count']} req, {spec['design_sections']} design, {spec['task_count']} tasks")
            if spec['completed_tasks'] > 0:
                completion_rate = spec['completed_tasks'] / spec['task_count'] * 100
                print(f"   Progress: {spec['completed_tasks']}/{spec['task_count']} tasks ({completion_rate:.1f}%)")
            print()
    
    # Show specs that need work
    if needs_work_specs:
        print("⚠️ NEEDS WORK (60-80% complete)")
        print("=" * 40)
        for spec in sorted(needs_work_specs, key=lambda x: x['completeness_score'], reverse=True):
            print(f"⚠️ {spec['name']}")
            print(f"   Score: {spec['completeness_score']:.1%}")
            print(f"   Missing: {', '.join(spec['missing_components']) if spec['missing_components'] else 'None'}")
            if spec['issues']:
                print(f"   Issues: {spec['issues'][0]}")  # Show first issue
            print()
    
    # Show incomplete specs (summary only)
    if incomplete_specs:
        print("❌ INCOMPLETE (<60% complete)")
        print("=" * 40)
        print(f"Found {len(incomplete_specs)} incomplete specifications")
        
        # Group by missing components
        missing_all = [s for s in incomplete_specs if len(s['missing_components']) == 3]
        missing_some = [s for s in incomplete_specs if 0 < len(s['missing_components']) < 3]
        
        if missing_all:
            print(f"   {len(missing_all)} specs missing all components")
        if missing_some:
            print(f"   {len(missing_some)} specs missing some components")
        print()
    
    # Priority recommendations
    print("🎯 PRIORITY RECOMMENDATIONS")
    print("=" * 40)
    
    for category, spec_names in priority_categories.items():
        category_ready = [a for a in ready_specs if a['name'] in spec_names]
        category_needs_work = [a for a in needs_work_specs if a['name'] in spec_names]
        
        if category_ready or category_needs_work:
            print(f"{category.replace('_', ' ').title()}:")
            for spec in category_ready:
                print(f"   ✅ {spec['name']} (ready)")
            for spec in category_needs_work:
                print(f"   ⚠️ {spec['name']} (needs work)")
            print()
    
    # Immediate action items
    print("🚀 IMMEDIATE ACTION ITEMS")
    print("=" * 40)
    
    # High-priority ready specs
    high_priority_ready = []
    for category in ['critical_infrastructure', 'core_functionality']:
        for spec_name in priority_categories[category]:
            spec_analysis = next((a for a in ready_specs if a['name'] == spec_name), None)
            if spec_analysis:
                high_priority_ready.append(spec_analysis)
    
    if high_priority_ready:
        print("Ready for immediate preparation:")
        for spec in high_priority_ready:
            print(f"   🚀 {spec['name']}")
        print()
    
    # High-priority specs needing work
    high_priority_needs_work = []
    for category in ['critical_infrastructure', 'core_functionality']:
        for spec_name in priority_categories[category]:
            spec_analysis = next((a for a in needs_work_specs if a['name'] == spec_name), None)
            if spec_analysis:
                high_priority_needs_work.append(spec_analysis)
    
    if high_priority_needs_work:
        print("High-priority specs needing completion:")
        for spec in high_priority_needs_work:
            print(f"   ⚠️ {spec['name']} - {', '.join(spec['missing_components']) if spec['missing_components'] else 'Quality issues'}")
        print()
    
    print("=" * 60)
    print(f"📈 Overall Readiness: {len(ready_specs)}/{len(analyses)} ({len(ready_specs)/len(analyses)*100:.1f}%)")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())