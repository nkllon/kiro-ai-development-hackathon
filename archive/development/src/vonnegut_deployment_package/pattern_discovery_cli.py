#!/usr/bin/env python3
"""
Pattern Discovery CLI
====================

Simple command-line interface for discovering and managing atomic patterns.

Usage:
  python scripts/pattern_discovery_cli.py observe --name "My Pattern" --description "Does something useful"
  python scripts/pattern_discovery_cli.py status
  python scripts/pattern_discovery_cli.py report
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.spec_framework.knowledge.pattern_discovery_workflow import PatternDiscoveryWorkflow, PatternCategory

def main():
    """Main CLI entry point."""
    if len(sys.argv) < 2:
        print("Usage: python scripts/pattern_discovery_cli.py {observe|status|report}")
        print("\nCommands:")
        print("  observe  - Record a new pattern observation")
        print("  status   - Show workflow status")
        print("  report   - Generate discovery report")
        return
    
    command = sys.argv[1]
    workflow = PatternDiscoveryWorkflow()
    
    if command == "observe":
        print("🔍 Pattern Discovery - Observation Mode")
        print("=" * 50)
        
        # Interactive pattern observation
        observer = input("Observer name: ").strip()
        if not observer:
            observer = "anonymous"
        
        name = input("Pattern name: ").strip()
        if not name:
            print("❌ Pattern name is required")
            return
        
        description = input("Pattern description: ").strip()
        if not description:
            print("❌ Pattern description is required")
            return
        
        print("\nAvailable categories:")
        for i, category in enumerate(PatternCategory, 1):
            print(f"  {i}. {category.value}")
        
        try:
            cat_choice = int(input("Category (number): ").strip())
            category = list(PatternCategory)[cat_choice - 1]
        except (ValueError, IndexError):
            print("❌ Invalid category choice")
            return
        
        print("\nEnter command sequence (one per line, empty line to finish):")
        commands = []
        while True:
            cmd = input(f"Command {len(commands) + 1}: ").strip()
            if not cmd:
                break
            commands.append(cmd)
        
        if not commands:
            print("❌ At least one command is required")
            return
        
        context = input("Additional context (optional): ").strip()
        
        # Record observation
        discovery_id = workflow.observe_pattern(
            observer=observer,
            pattern_name=name,
            description=description,
            command_sequence=commands,
            category=category,
            context=context
        )
        
        print(f"\n🎉 Pattern observation recorded!")
        print(f"Discovery ID: {discovery_id}")
        print(f"\n📋 Next steps:")
        print(f"1. Test the pattern to validate it works")
        print(f"2. Document expected outputs and success criteria")
        print(f"3. Submit for review and approval")
        
    elif command == "status":
        print("📊 Pattern Discovery Workflow Status")
        print("=" * 50)
        
        health = workflow.get_health_status()
        print(f"Total discoveries: {health['total_discoveries']}")
        print("\nBy stage:")
        for stage, count in health['stage_distribution'].items():
            if count > 0:
                print(f"  {stage.title()}: {count}")
        
        # Show recent discoveries
        recent_discoveries = list(workflow.discoveries.values())[-5:]
        if recent_discoveries:
            print(f"\n📝 Recent discoveries:")
            for discovery in recent_discoveries:
                print(f"  • {discovery.pattern_candidate.name} ({discovery.stage.value})")
        
    elif command == "report":
        print("📄 Generating Pattern Discovery Report...")
        
        output_path = ".kiro/knowledge/pattern_discovery_report.md"
        report = workflow.export_discovery_report(output_path)
        
        print(f"✅ Report saved to: {output_path}")
        print(f"\nReport summary:")
        print(f"- Total discoveries: {len(workflow.discoveries)}")
        
        stage_counts = {}
        for discovery in workflow.discoveries.values():
            stage = discovery.stage.value
            stage_counts[stage] = stage_counts.get(stage, 0) + 1
        
        for stage, count in stage_counts.items():
            print(f"- {stage.title()}: {count}")
    
    else:
        print(f"❌ Unknown command: {command}")
        print("Available commands: observe, status, report")

if __name__ == "__main__":
    main()