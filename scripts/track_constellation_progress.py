#!/usr/bin/env python3
"""
Constellation Elaboration Progress Tracker

Tracks progress of the constellation elaboration process across all phases.
"""

import json
from pathlib import Path
from datetime import datetime

def check_constellation_progress():
    """Check and display constellation elaboration progress."""
    base_dir = Path.cwd()
    status_file = base_dir / ".kiro" / "reports" / "constellation-elaboration-status.json"
    
    if not status_file.exists():
        print("❌ Constellation elaboration not started")
        return
    
    status = json.loads(status_file.read_text())
    
    print("🌟 Constellation Elaboration Progress")
    print("=" * 50)
    print(f"Agent ID: {status['agent_id']}")
    print(f"Started: {status['start_time']}")
    print(f"Status: {status['status']}")
    print()
    
    # Phase progress
    for phase_name, phase_data in status['phases'].items():
        phase_display = phase_name.replace('_', ' ').title()
        print(f"{phase_display}: {phase_data['status']}")
    
    print()
    print(f"Specs Completed: {status['completed_specs']}/{status['total_specs']}")
    
    # Success criteria
    criteria = status['success_criteria']
    print("\nSuccess Criteria:")
    print(f"  Requirements.md files: {criteria['requirements_md_count']}")
    print(f"  Design.md files: {criteria['design_md_count']}")
    print(f"  Tasks.md files: {criteria['tasks_md_count']}")
    print(f"  Dimension coverage: {criteria['dimension_coverage']}%")
    print(f"  Stakeholder types: {criteria['stakeholder_types_addressed']}")
    print(f"  CMS dependencies: {'✅' if criteria['cms_dependencies_identified'] else '❌'}")
    print(f"  CMS architecture updated: {'✅' if criteria['cms_architecture_updated'] else '❌'}")

if __name__ == "__main__":
    check_constellation_progress()
