#!/usr/bin/env python3
"""
Dashboard & Observatory Specification Analysis
==============================================

Analyzes dashboard, chart, and observatory-related specifications
to determine which ones can help fix the sad board.

Author: Beast Mode Framework
Date: 2025-01-27
Version: 1.0
"""

import sys
from pathlib import Path
import re

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

def analyze_dashboard_spec(spec_path: Path) -> dict:
    """Analyze a dashboard-related specification."""
    spec_name = spec_path.name
    
    # Check for required files
    requirements_file = spec_path / "requirements.md"
    design_file = spec_path / "design.md"
    tasks_file = spec_path / "tasks.md"
    
    analysis = {
        'name': spec_name,
        'path': str(spec_path),
        'has_all_files': all([requirements_file.exists(), design_file.exists(), tasks_file.exists()]),
        'task_count': 0,
        'completed_tasks': 0,
        'completion_percentage': 0.0,
        'dashboard_features': [],
        'chart_types': [],
        'readiness_status': 'unknown',
        'priority_score': 0
    }
    
    # Analyze tasks if file exists
    if tasks_file.exists():
        try:
            content = tasks_file.read_text()
            # Count tasks
            task_matches = re.findall(r'^(\s*)-\s*\[([x\-\s])\]', content, re.MULTILINE)
            analysis['task_count'] = len(task_matches)
            
            # Count completed tasks
            completed = [m for m in task_matches if m[1].lower() == 'x']
            analysis['completed_tasks'] = len(completed)
            
            if analysis['task_count'] > 0:
                analysis['completion_percentage'] = (analysis['completed_tasks'] / analysis['task_count']) * 100
        except Exception as e:
            pass
    
    # Analyze design for dashboard features
    if design_file.exists():
        try:
            content = design_file.read_text().lower()
            
            # Look for dashboard features
            dashboard_keywords = [
                'real-time', 'live feed', 'dashboard', 'chart', 'graph', 'visualization',
                'metrics', 'monitoring', 'status', 'health', 'performance', 'analytics'
            ]
            
            for keyword in dashboard_keywords:
                if keyword in content:
                    analysis['dashboard_features'].append(keyword)
            
            # Look for specific chart types
            chart_types = [
                'line chart', 'bar chart', 'pie chart', 'scatter plot', 'heatmap',
                'gauge', 'progress bar', 'timeline', 'network graph', 'tree map'
            ]
            
            for chart_type in chart_types:
                if chart_type in content:
                    analysis['chart_types'].append(chart_type)
                    
        except Exception as e:
            pass
    
    # Analyze requirements for dashboard priority
    if requirements_file.exists():
        try:
            content = requirements_file.read_text().lower()
            
            # Priority indicators
            high_priority_terms = [
                'critical', 'urgent', 'immediate', 'essential', 'core',
                'user interface', 'visualization', 'real-time', 'monitoring'
            ]
            
            for term in high_priority_terms:
                if term in content:
                    analysis['priority_score'] += 1
                    
        except Exception as e:
            pass
    
    # Determine readiness status
    if analysis['has_all_files']:
        if analysis['completion_percentage'] >= 80:
            analysis['readiness_status'] = 'ready_to_deploy'
        elif analysis['completion_percentage'] >= 50:
            analysis['readiness_status'] = 'in_progress'
        elif analysis['task_count'] > 0:
            analysis['readiness_status'] = 'ready_to_start'
        else:
            analysis['readiness_status'] = 'needs_tasks'
    else:
        analysis['readiness_status'] = 'incomplete'
    
    return analysis


def main():
    """Analyze dashboard-related specifications."""
    print("📊 Dashboard & Observatory Specification Analysis")
    print("=" * 60)
    print("🎯 Finding specs to fix that sad board!")
    print()
    
    specs_dir = Path(".kiro/specs")
    
    # Find dashboard/observatory related specs
    dashboard_keywords = [
        'dashboard', 'chart', 'observatory', 'monitoring', 'visualization',
        'health', 'performance', 'metrics', 'analytics', 'feed'
    ]
    
    dashboard_specs = []
    for spec_dir in specs_dir.iterdir():
        if spec_dir.is_dir() and not spec_dir.name.startswith('.'):
            spec_name_lower = spec_dir.name.lower()
            if any(keyword in spec_name_lower for keyword in dashboard_keywords):
                dashboard_specs.append(spec_dir)
    
    print(f"Found {len(dashboard_specs)} dashboard-related specifications")
    print()
    
    # Analyze each dashboard spec
    analyses = []
    for spec_dir in dashboard_specs:
        analysis = analyze_dashboard_spec(spec_dir)
        analyses.append(analysis)
    
    # Sort by readiness and priority
    analyses.sort(key=lambda x: (
        x['readiness_status'] == 'ready_to_deploy',
        x['readiness_status'] == 'in_progress', 
        x['completion_percentage'],
        x['priority_score']
    ), reverse=True)
    
    # Categorize by readiness
    ready_to_deploy = [a for a in analyses if a['readiness_status'] == 'ready_to_deploy']
    in_progress = [a for a in analyses if a['readiness_status'] == 'in_progress']
    ready_to_start = [a for a in analyses if a['readiness_status'] == 'ready_to_start']
    needs_work = [a for a in analyses if a['readiness_status'] in ['needs_tasks', 'incomplete']]
    
    print("🚀 READY TO DEPLOY (80%+ complete)")
    print("=" * 40)
    if ready_to_deploy:
        for spec in ready_to_deploy:
            print(f"✅ {spec['name']}")
            print(f"   Progress: {spec['completed_tasks']}/{spec['task_count']} tasks ({spec['completion_percentage']:.1f}%)")
            print(f"   Features: {', '.join(spec['dashboard_features'][:3])}")
            if spec['chart_types']:
                print(f"   Charts: {', '.join(spec['chart_types'])}")
            print(f"   🚀 READY FOR IMMEDIATE DEPLOYMENT!")
            print()
    else:
        print("   No specs ready for immediate deployment")
        print()
    
    print("🔄 IN PROGRESS (50-79% complete)")
    print("=" * 40)
    if in_progress:
        for spec in in_progress:
            print(f"⚡ {spec['name']}")
            print(f"   Progress: {spec['completed_tasks']}/{spec['task_count']} tasks ({spec['completion_percentage']:.1f}%)")
            print(f"   Features: {', '.join(spec['dashboard_features'][:3])}")
            remaining = spec['task_count'] - spec['completed_tasks']
            print(f"   📋 {remaining} tasks remaining to complete")
            print()
    else:
        print("   No specs currently in progress")
        print()
    
    print("🎯 READY TO START (0-49% complete)")
    print("=" * 40)
    if ready_to_start:
        for spec in ready_to_start:
            print(f"🚀 {spec['name']}")
            print(f"   Progress: {spec['completed_tasks']}/{spec['task_count']} tasks ({spec['completion_percentage']:.1f}%)")
            print(f"   Features: {', '.join(spec['dashboard_features'][:3])}")
            print(f"   Priority Score: {spec['priority_score']}")
            print()
    else:
        print("   No specs ready to start")
        print()
    
    print("⚠️ NEEDS WORK")
    print("=" * 40)
    if needs_work:
        for spec in needs_work:
            print(f"⚠️ {spec['name']}")
            print(f"   Status: {spec['readiness_status']}")
            if not spec['has_all_files']:
                print(f"   Issue: Missing required files")
            else:
                print(f"   Issue: Needs task definition")
            print()
    else:
        print("   All dashboard specs have proper structure!")
        print()
    
    # Quick wins for the board
    print("🎯 IMMEDIATE ACTION PLAN FOR THE BOARD")
    print("=" * 50)
    
    if ready_to_deploy:
        print("🚀 DEPLOY IMMEDIATELY (Will fix board now!):")
        for spec in ready_to_deploy[:3]:  # Top 3
            print(f"   python src/spec_framework/cli/prepare_spec_cli.py prepare .kiro/specs/{spec['name']}")
        print()
    
    if in_progress:
        print("⚡ COMPLETE THESE NEXT (Quick wins):")
        for spec in in_progress[:3]:  # Top 3
            remaining = spec['task_count'] - spec['completed_tasks']
            print(f"   {spec['name']} - Only {remaining} tasks left!")
        print()
    
    # High-impact recommendations
    high_impact_specs = [
        'observatory-performance-chart',
        'observatory-health-chart-implementation', 
        'observatory-token-tracking-chart',
        'beast-mode-coordination-observatory',
        'observatory-live-coordination-feed'
    ]
    
    print("🎯 HIGH-IMPACT DASHBOARD SPECS:")
    for spec_name in high_impact_specs:
        spec_analysis = next((a for a in analyses if a['name'] == spec_name), None)
        if spec_analysis:
            status_emoji = {
                'ready_to_deploy': '🚀',
                'in_progress': '⚡', 
                'ready_to_start': '🎯',
                'needs_tasks': '⚠️',
                'incomplete': '❌'
            }.get(spec_analysis['readiness_status'], '❓')
            
            print(f"   {status_emoji} {spec_name} - {spec_analysis['completion_percentage']:.1f}% complete")
    
    print()
    print("=" * 60)
    print("💡 RECOMMENDATION: Start with the ready-to-deploy specs!")
    print("   These will immediately improve the board's appearance.")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())