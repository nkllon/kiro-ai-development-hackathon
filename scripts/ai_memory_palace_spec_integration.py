#!/usr/bin/env python3
"""
AI Memory Palace Spec Integration CLI.

Command-line interface for managing spec workflow integration with
the AI Memory Palace context system.
"""

import sys
import argparse
import json
from pathlib import Path
from typing import Dict, Any

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from beast_mode.ai_memory_palace.spec_integration import (
    SpecWorkflowIntegrator, SpecWorkflowCLI, TaskStatus
)
from beast_mode.ai_memory_palace.context_manager import ContextManager
from beast_mode.ai_memory_palace.context_registry import ContextRegistry
from beast_mode.ai_memory_palace.storage import ContextStorage
from beast_mode.ai_memory_palace.multi_project_manager import MultiProjectContextManager
from beast_mode.ai_memory_palace.security import ContextSecurityManager


def create_integrator() -> SpecWorkflowIntegrator:
    """Create spec workflow integrator with dependencies"""
    # Initialize storage and registry
    storage_dir = Path.home() / ".kiro" / "context_storage"
    storage = ContextStorage(storage_dir)
    registry = ContextRegistry(storage)
    
    # Initialize context manager
    context_manager = ContextManager(registry)
    
    # Initialize multi-project manager
    security = ContextSecurityManager()
    multi_project_manager = MultiProjectContextManager(registry, security)
    
    # Create integrator
    return SpecWorkflowIntegrator(context_manager, multi_project_manager)


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description="AI Memory Palace Spec Integration CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Initialize spec integration for current workspace
  python ai_memory_palace_spec_integration.py init

  # Register a new spec
  python ai_memory_palace_spec_integration.py register my-feature .kiro/specs/my-feature

  # Update task status
  python ai_memory_palace_spec_integration.py task my-feature 1.1 completed

  # Get spec recommendations
  python ai_memory_palace_spec_integration.py recommendations

  # Show spec navigation info
  python ai_memory_palace_spec_integration.py navigation

  # Show integration statistics
  python ai_memory_palace_spec_integration.py stats

  # Watch specs for changes (daemon mode)
  python ai_memory_palace_spec_integration.py watch --daemon
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Init command
    init_parser = subparsers.add_parser('init', help='Initialize spec integration')
    init_parser.add_argument('--workspace', type=str, default='.',
                            help='Workspace directory (default: current directory)')
    
    # Register command
    register_parser = subparsers.add_parser('register', help='Register a spec for tracking')
    register_parser.add_argument('spec_name', help='Name of the spec')
    register_parser.add_argument('spec_path', help='Path to spec directory')
    register_parser.add_argument('--project-id', type=str,
                                help='Project ID (default: derived from spec name)')
    
    # Task command
    task_parser = subparsers.add_parser('task', help='Update task status')
    task_parser.add_argument('spec_name', help='Name of the spec')
    task_parser.add_argument('task_number', help='Task number (e.g., 1.1, 2.3)')
    task_parser.add_argument('status', choices=['not_started', 'in_progress', 'completed', 'blocked', 'cancelled'],
                            help='New task status')
    task_parser.add_argument('--project-id', type=str,
                            help='Project ID (default: derived from spec name)')
    
    # Recommendations command
    rec_parser = subparsers.add_parser('recommendations', help='Get spec recommendations')
    rec_parser.add_argument('--project-id', type=str, default='current',
                           help='Project ID (default: current)')
    rec_parser.add_argument('--format', choices=['json', 'text'], default='text',
                           help='Output format')
    
    # Navigation command
    nav_parser = subparsers.add_parser('navigation', help='Show spec navigation info')
    nav_parser.add_argument('--project-id', type=str, default='current',
                           help='Project ID (default: current)')
    nav_parser.add_argument('--format', choices=['json', 'text'], default='text',
                           help='Output format')
    
    # Stats command
    stats_parser = subparsers.add_parser('stats', help='Show integration statistics')
    stats_parser.add_argument('--format', choices=['json', 'text'], default='text',
                             help='Output format')
    
    # Watch command
    watch_parser = subparsers.add_parser('watch', help='Watch specs for changes')
    watch_parser.add_argument('--workspace', type=str, default='.',
                             help='Workspace directory (default: current directory)')
    watch_parser.add_argument('--daemon', action='store_true',
                             help='Run as daemon process')
    watch_parser.add_argument('--interval', type=int, default=5,
                             help='Watch interval in seconds (default: 5)')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 1
    
    try:
        integrator = create_integrator()
        cli = SpecWorkflowCLI(integrator)
        
        if args.command == 'init':
            workspace_path = Path(args.workspace).resolve()
            print(f"🔗 Initializing spec integration for {workspace_path}")
            
            integrator.initialize_spec_integration(workspace_path)
            
            print("✅ Spec integration initialized")
            print(f"Workspace: {workspace_path}")
            
            # Show discovered specs
            stats = cli.get_stats()
            if stats['specs_tracked'] > 0:
                print(f"Discovered {stats['specs_tracked']} existing specs")
            else:
                print("No existing specs found")
        
        elif args.command == 'register':
            spec_name = args.spec_name
            spec_path = args.spec_path
            project_id = args.project_id or f"spec_{spec_name}"
            
            print(f"📋 Registering spec: {spec_name}")
            
            result = cli.register_spec(spec_name, spec_path, project_id)
            
            if result['success']:
                print(f"✅ Spec registered successfully")
                print(f"Name: {spec_name}")
                print(f"Path: {spec_path}")
                print(f"Project ID: {project_id}")
            else:
                print(f"❌ Failed to register spec: {spec_name}")
                return 1
        
        elif args.command == 'task':
            spec_name = args.spec_name
            task_number = args.task_number
            status = args.status
            project_id = args.project_id or f"spec_{spec_name}"
            
            print(f"📝 Updating task {task_number} in {spec_name} to {status}")
            
            result = cli.update_task(spec_name, task_number, status, project_id)
            
            if result['success']:
                print(f"✅ Task updated successfully")
                print(f"Spec: {spec_name}")
                print(f"Task: {task_number}")
                print(f"Status: {status}")
            else:
                print(f"❌ Failed to update task")
                if 'error' in result:
                    print(f"Error: {result['error']}")
                return 1
        
        elif args.command == 'recommendations':
            project_id = args.project_id
            
            print("💡 Getting spec recommendations...")
            recommendations = cli.get_recommendations(project_id)
            
            if args.format == 'json':
                print(json.dumps(recommendations, indent=2))
            else:
                if not recommendations:
                    print("No recommendations available")
                else:
                    print(f"Found {len(recommendations)} recommendations:")
                    print()
                    
                    for i, rec in enumerate(recommendations, 1):
                        priority_icon = "🔴" if rec['priority'] == 'high' else "🟡" if rec['priority'] == 'medium' else "🟢"
                        print(f"{i}. {priority_icon} {rec['message']}")
                        
                        if 'spec_name' in rec:
                            print(f"   Spec: {rec['spec_name']}")
                        
                        if 'progress' in rec:
                            print(f"   Progress: {rec['progress']:.1f}%")
                        
                        if 'suggested_actions' in rec:
                            print("   Suggested actions:")
                            for action in rec['suggested_actions']:
                                print(f"   - {action}")
                        
                        print()
        
        elif args.command == 'navigation':
            project_id = args.project_id
            
            print("🧭 Getting spec navigation info...")
            nav_info = cli.get_navigation(project_id)
            
            if args.format == 'json':
                print(json.dumps(nav_info, indent=2))
            else:
                if 'error' in nav_info:
                    print(f"❌ Error: {nav_info['error']}")
                    return 1
                
                # Active specs
                active_specs = nav_info.get('active_specs', [])
                if active_specs:
                    print("📋 Active Specs:")
                    for spec in active_specs:
                        print(f"  - {spec['name']} ({spec['phase']}) - {spec['progress']:.1f}%")
                else:
                    print("📋 No active specs")
                
                print()
                
                # Completion status
                completion = nav_info.get('completion_status', {})
                total = completion.get('total_specs', 0)
                completed = completion.get('completed_specs', 0)
                percentage = completion.get('completion_percentage', 0)
                
                print(f"📊 Completion Status: {completed}/{total} specs ({percentage:.1f}%)")
                print()
                
                # Next actions
                next_actions = nav_info.get('next_actions', [])
                if next_actions:
                    print("🎯 Next Actions:")
                    for action in next_actions:
                        priority_icon = "🔴" if action['priority'] == 'high' else "🟡" if action['priority'] == 'medium' else "🟢"
                        print(f"  {priority_icon} {action['action']}")
                else:
                    print("🎯 No pending actions")
        
        elif args.command == 'stats':
            print("📊 Getting integration statistics...")
            stats = cli.get_stats()
            
            if args.format == 'json':
                print(json.dumps(stats, indent=2))
            else:
                print("AI Memory Palace Spec Integration Statistics:")
                print(f"  Specs tracked: {stats['specs_tracked']}")
                print(f"  Tasks completed: {stats['tasks_completed']}")
                print(f"  Context syncs: {stats['context_syncs']}")
                print(f"  File changes detected: {stats['file_changes_detected']}")
                print(f"  Context updates triggered: {stats['context_updates_triggered']}")
                print(f"  Active specs: {stats['active_specs']}")
                print(f"  Completed specs: {stats['completed_specs']}")
        
        elif args.command == 'watch':
            workspace_path = Path(args.workspace).resolve()
            
            print(f"👁️ Starting spec file watcher for {workspace_path}")
            print(f"Watch interval: {args.interval} seconds")
            
            if args.daemon:
                print("Running in daemon mode (Ctrl+C to stop)")
            
            # Initialize and start watching
            integrator.initialize_spec_integration(workspace_path)
            
            try:
                if args.daemon:
                    # Keep running until interrupted
                    import time
                    while True:
                        time.sleep(1)
                else:
                    # Run for a short time and show status
                    import time
                    time.sleep(10)
                    
                    stats = cli.get_stats()
                    print(f"✅ Watched for 10 seconds")
                    print(f"File changes detected: {stats['file_changes_detected']}")
                    print(f"Context updates triggered: {stats['context_updates_triggered']}")
            
            except KeyboardInterrupt:
                print("\n⏹️ Stopping spec watcher...")
                integrator.file_watcher.stop_watching()
                print("✅ Spec watcher stopped")
        
        return 0
    
    except KeyboardInterrupt:
        print("\n⏹️ Operation cancelled by user")
        return 1
    
    except Exception as e:
        print(f"💥 Error: {e}")
        return 1


if __name__ == '__main__':
    sys.exit(main())