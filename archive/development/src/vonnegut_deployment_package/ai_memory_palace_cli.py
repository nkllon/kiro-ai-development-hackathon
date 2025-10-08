#!/usr/bin/env python3
"""
AI Memory Palace Comprehensive CLI.

Unified command-line interface for all AI Memory Palace operations including
context management, project operations, backups, analytics, and debugging.
"""

import sys
import argparse
import json
from pathlib import Path
from typing import Dict, Any, Optional, List

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from beast_mode.ai_memory_palace.api import ContextCLITools
from beast_mode.ai_memory_palace.context_manager import ContextManager
from beast_mode.ai_memory_palace.context_registry import ContextRegistry
from beast_mode.ai_memory_palace.storage import ContextStorage
from beast_mode.ai_memory_palace.multi_project_manager import MultiProjectContextManager
from beast_mode.ai_memory_palace.backup_recovery import ContextBackupManager
from beast_mode.ai_memory_palace.analytics import ContextAnalyzer, ContextOptimizer
from beast_mode.ai_memory_palace.spec_integration import SpecWorkflowIntegrator
from beast_mode.ai_memory_palace.developer_tools import ContextInspector
from beast_mode.ai_memory_palace.security import ContextSecurityManager
from beast_mode.ai_memory_palace.context_validator import ContextValidator


def create_cli_system() -> ContextCLITools:
    """Create complete CLI system with all dependencies"""
    # Initialize storage and core components
    storage_dir = Path.home() / ".kiro" / "context_storage"
    storage = ContextStorage(storage_dir)
    registry = ContextRegistry(storage)
    
    # Initialize managers
    context_manager = ContextManager(registry)
    security = ContextSecurityManager()
    multi_project_manager = MultiProjectContextManager(registry, security)
    
    # Initialize backup system
    validator = ContextValidator()
    backup_manager = ContextBackupManager(storage, validator)
    
    # Initialize analytics
    analyzer = ContextAnalyzer(registry)
    optimizer = ContextOptimizer(registry, analyzer)
    
    # Initialize integrations
    spec_integrator = SpecWorkflowIntegrator(context_manager, multi_project_manager)
    inspector = ContextInspector(context_manager, registry, validator)
    
    # Create CLI tools
    return ContextCLITools(
        context_manager, multi_project_manager, backup_manager,
        analyzer, optimizer, spec_integrator, inspector
    )


def format_size(bytes_value: float) -> str:
    """Format bytes as human-readable string"""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if bytes_value < 1024.0:
            return f"{bytes_value:.1f} {unit}"
        bytes_value /= 1024.0
    return f"{bytes_value:.1f} TB"


def print_table(headers: List[str], rows: List[List[str]], max_width: int = 80):
    """Print formatted table"""
    if not rows:
        return
    
    # Calculate column widths
    col_widths = [len(header) for header in headers]
    for row in rows:
        for i, cell in enumerate(row):
            if i < len(col_widths):
                col_widths[i] = max(col_widths[i], len(str(cell)))
    
    # Adjust for max width
    total_width = sum(col_widths) + len(headers) * 3 - 1
    if total_width > max_width:
        # Reduce widths proportionally
        reduction = (total_width - max_width) / len(col_widths)
        col_widths = [max(10, int(w - reduction)) for w in col_widths]
    
    # Print header
    header_row = " | ".join(h.ljust(w) for h, w in zip(headers, col_widths))
    print(header_row)
    print("-" * len(header_row))
    
    # Print rows
    for row in rows:
        formatted_row = " | ".join(
            str(cell)[:w].ljust(w) for cell, w in zip(row, col_widths)
        )
        print(formatted_row)


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description="AI Memory Palace Comprehensive CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Session management
  python ai_memory_palace_cli.py session start my-project
  python ai_memory_palace_cli.py session info
  python ai_memory_palace_cli.py session end
  
  # Context operations
  python ai_memory_palace_cli.py context add-event user "Working on new feature"
  python ai_memory_palace_cli.py context search my-project "implementation"
  python ai_memory_palace_cli.py context inspect my-project
  
  # Project management
  python ai_memory_palace_cli.py project list
  python ai_memory_palace_cli.py project switch my-project
  python ai_memory_palace_cli.py project stats
  
  # Backup operations
  python ai_memory_palace_cli.py backup create my-project
  python ai_memory_palace_cli.py backup list my-project
  python ai_memory_palace_cli.py backup restore backup-id-123
  
  # Analytics
  python ai_memory_palace_cli.py analytics usage --project my-project
  python ai_memory_palace_cli.py analytics dashboard --days 30
  python ai_memory_palace_cli.py analytics optimize
  
  # System operations
  python ai_memory_palace_cli.py system health
  python ai_memory_palace_cli.py system export my-project output.json
        """
    )
    
    subparsers = parser.add_subparsers(dest='category', help='Command categories')
    
    # Session management commands
    session_parser = subparsers.add_parser('session', help='Session management')
    session_subparsers = session_parser.add_subparsers(dest='session_action')
    
    start_parser = session_subparsers.add_parser('start', help='Start new session')
    start_parser.add_argument('project_id', help='Project identifier')
    
    session_subparsers.add_parser('end', help='End current session')
    session_subparsers.add_parser('info', help='Show session information')
    
    # Context operations commands
    context_parser = subparsers.add_parser('context', help='Context operations')
    context_subparsers = context_parser.add_subparsers(dest='context_action')
    
    add_event_parser = context_subparsers.add_parser('add-event', help='Add context event')
    add_event_parser.add_argument('event_type', choices=['user', 'ai', 'system'], help='Event type')
    add_event_parser.add_argument('content', help='Event content')
    add_event_parser.add_argument('--metadata', type=str, help='JSON metadata')
    
    search_parser = context_subparsers.add_parser('search', help='Search context')
    search_parser.add_argument('project_id', help='Project identifier')
    search_parser.add_argument('query', help='Search query')
    search_parser.add_argument('--types', help='Content types (comma-separated)')
    
    inspect_parser = context_subparsers.add_parser('inspect', help='Inspect context')
    inspect_parser.add_argument('project_id', help='Project identifier')
    
    validate_parser = context_subparsers.add_parser('validate', help='Validate context')
    validate_parser.add_argument('project_id', help='Project identifier')
    
    clear_parser = context_subparsers.add_parser('clear', help='Clear context')
    clear_parser.add_argument('--confirm', required=True, help='Confirmation code')
    
    # Project management commands
    project_parser = subparsers.add_parser('project', help='Project management')
    project_subparsers = project_parser.add_subparsers(dest='project_action')
    
    project_subparsers.add_parser('list', help='List projects')
    project_subparsers.add_parser('stats', help='Project statistics')
    
    switch_parser = project_subparsers.add_parser('switch', help='Switch project')
    switch_parser.add_argument('project_id', help='Project identifier')
    
    # Backup operations commands
    backup_parser = subparsers.add_parser('backup', help='Backup operations')
    backup_subparsers = backup_parser.add_subparsers(dest='backup_action')
    
    create_backup_parser = backup_subparsers.add_parser('create', help='Create backup')
    create_backup_parser.add_argument('project_id', help='Project identifier')
    create_backup_parser.add_argument('--type', default='manual', help='Backup type')
    
    list_backup_parser = backup_subparsers.add_parser('list', help='List backups')
    list_backup_parser.add_argument('project_id', help='Project identifier')
    list_backup_parser.add_argument('--limit', type=int, default=10, help='Maximum results')
    
    restore_parser = backup_subparsers.add_parser('restore', help='Restore backup')
    restore_parser.add_argument('backup_id', help='Backup identifier')
    
    backup_subparsers.add_parser('stats', help='Backup statistics')
    
    # Analytics commands
    analytics_parser = subparsers.add_parser('analytics', help='Analytics operations')
    analytics_subparsers = analytics_parser.add_subparsers(dest='analytics_action')
    
    usage_parser = analytics_subparsers.add_parser('usage', help='Usage analysis')
    usage_parser.add_argument('--project', help='Project identifier')
    
    dashboard_parser = analytics_subparsers.add_parser('dashboard', help='Analytics dashboard')
    dashboard_parser.add_argument('--project', help='Project identifier')
    dashboard_parser.add_argument('--days', type=int, default=7, help='Days to analyze')
    
    optimize_parser = analytics_subparsers.add_parser('optimize', help='Optimization recommendations')
    optimize_parser.add_argument('--project', help='Project identifier')
    
    analytics_subparsers.add_parser('stats', help='Analytics statistics')
    
    # System operations commands
    system_parser = subparsers.add_parser('system', help='System operations')
    system_subparsers = system_parser.add_subparsers(dest='system_action')
    
    system_subparsers.add_parser('health', help='System health check')
    
    export_parser = system_subparsers.add_parser('export', help='Export context')
    export_parser.add_argument('project_id', help='Project identifier')
    export_parser.add_argument('output_file', help='Output file path')
    export_parser.add_argument('--format', default='json', help='Export format')
    export_parser.add_argument('--include-sensitive', action='store_true', help='Include sensitive data')
    
    import_parser = system_subparsers.add_parser('import', help='Import context')
    import_parser.add_argument('input_file', help='Input file path')
    import_parser.add_argument('project_id', help='Project identifier')
    import_parser.add_argument('--strategy', default='replace', help='Merge strategy')
    
    args = parser.parse_args()
    
    if not args.category:
        parser.print_help()
        return 1
    
    try:
        cli = create_cli_system()
        
        # Session management
        if args.category == 'session':
            if args.session_action == 'start':
                result = cli.start_session(args.project_id)
                if result['success']:
                    print(f"✅ Session started: {result['session_id']}")
                    print(f"Project: {result['project_id']}")
                else:
                    print("❌ Failed to start session")
                    return 1
            
            elif args.session_action == 'end':
                result = cli.end_session()
                if result['success']:
                    print("✅ Session ended")
                else:
                    print("❌ Failed to end session")
                    return 1
            
            elif args.session_action == 'info':
                info = cli.get_session_info()
                if info['active']:
                    print("📊 Current Session:")
                    print(f"  Project: {info['project_id']}")
                    print(f"  Session ID: {info['session_id']}")
                    print(f"  Size: {format_size(info['size_mb'] * 1024 * 1024)}")
                    print(f"  Events: {info['events']}")
                else:
                    print("No active session")
        
        # Context operations
        elif args.category == 'context':
            if args.context_action == 'add-event':
                event_type_map = {'user': 'USER_MESSAGE', 'ai': 'AI_RESPONSE', 'system': 'SYSTEM_EVENT'}
                event_type = event_type_map.get(args.event_type, 'USER_MESSAGE')
                
                metadata = None
                if args.metadata:
                    try:
                        metadata = json.loads(args.metadata)
                    except json.JSONDecodeError:
                        print("❌ Invalid JSON metadata")
                        return 1
                
                result = cli.add_event(event_type, args.content, metadata)
                if result['success']:
                    print(f"✅ Event added: {result['event_id']}")
                else:
                    print(f"❌ Failed to add event: {result.get('error', 'Unknown error')}")
                    return 1
            
            elif args.context_action == 'search':
                content_types = args.types.split(',') if args.types else None
                results = cli.search_context(args.project_id, args.query, content_types)
                
                if 'error' in results:
                    print(f"❌ Search error: {results['error']}")
                    return 1
                
                print(f"🔍 Search Results for '{args.query}':")
                print(f"Found {results['total_results']} results")
                
                if results['results']:
                    for i, result in enumerate(results['results'][:10], 1):
                        print(f"\n{i}. {result['type'].title()}")
                        if 'timestamp' in result:
                            print(f"   Time: {result['timestamp']}")
                        if 'content_preview' in result:
                            print(f"   Content: {result['content_preview']}")
                        elif 'description' in result:
                            print(f"   Description: {result['description']}")
            
            elif args.context_action == 'inspect':
                inspection = cli.inspect_context(args.project_id)
                
                if 'error' in inspection:
                    print(f"❌ Inspection error: {inspection['error']}")
                    return 1
                
                print(f"🔍 Context Inspection: {args.project_id}")
                
                basic_info = inspection.get('basic_info', {})
                print(f"Size: {format_size(basic_info.get('size_bytes', 0))}")
                print(f"Created: {basic_info.get('created', 'Unknown')}")
                
                content_analysis = inspection.get('content_analysis', {})
                print(f"Events: {content_analysis.get('conversation_events', 0)}")
                print(f"Decisions: {content_analysis.get('decisions_made', 0)}")
                print(f"Work Items: {content_analysis.get('work_items', 0)}")
                
                validation_status = inspection.get('validation_status', {})
                is_valid = validation_status.get('is_valid', False)
                print(f"Valid: {'✅' if is_valid else '❌'}")
                
                if not is_valid:
                    error_count = validation_status.get('error_count', 0)
                    warning_count = validation_status.get('warning_count', 0)
                    print(f"Errors: {error_count}, Warnings: {warning_count}")
            
            elif args.context_action == 'validate':
                validation = cli.validate_context(args.project_id)
                
                if 'error' in validation:
                    print(f"❌ Validation error: {validation['error']}")
                    return 1
                
                is_valid = validation.get('is_valid', False)
                print(f"Context Validation: {'✅ Valid' if is_valid else '❌ Invalid'}")
                
                summary = validation.get('summary', {})
                if summary.get('total_issues', 0) > 0:
                    print(f"Issues found: {summary['total_issues']}")
                    print(f"  Errors: {summary['error_count']}")
                    print(f"  Warnings: {summary['warning_count']}")
                    
                    # Show first few errors
                    errors = validation.get('errors', [])[:3]
                    for error in errors:
                        print(f"  ❌ {error['message']}")
            
            elif args.context_action == 'clear':
                result = cli.clear_context(args.confirm)
                if result['success']:
                    print("✅ Context cleared")
                else:
                    print("❌ Failed to clear context (check confirmation code)")
                    return 1
        
        # Project management
        elif args.category == 'project':
            if args.project_action == 'list':
                projects = cli.list_projects()
                
                if not projects:
                    print("No projects found")
                else:
                    print(f"📋 Projects ({len(projects)}):")
                    
                    headers = ['Name', 'Type', 'Last Accessed', 'Size']
                    rows = []
                    
                    for project in projects:
                        size_mb = project.get('context_size_bytes', 0) / 1024 / 1024
                        rows.append([
                            project.get('project_name', 'Unknown'),
                            project.get('project_type', 'Unknown'),
                            project.get('last_accessed', 'Unknown')[:19],  # Truncate timestamp
                            format_size(size_mb * 1024 * 1024)
                        ])
                    
                    print_table(headers, rows)
            
            elif args.project_action == 'switch':
                result = cli.switch_project(args.project_id)
                if result['success']:
                    print(f"✅ Switched to project: {args.project_id}")
                else:
                    print(f"❌ Failed to switch to project: {args.project_id}")
                    return 1
            
            elif args.project_action == 'stats':
                stats = cli.get_project_stats()
                
                print("📊 Multi-Project Statistics:")
                print(f"Total Projects: {stats.get('total_projects', 0)}")
                print(f"Current Project: {stats.get('current_project_name', 'None')}")
                print(f"Total Size: {format_size(stats.get('total_context_size_mb', 0) * 1024 * 1024)}")
                print(f"Project Switches: {stats.get('project_switches', 0)}")
                print(f"Shared Contexts: {stats.get('shared_contexts', 0)}")
        
        # Backup operations
        elif args.category == 'backup':
            if args.backup_action == 'create':
                result = cli.create_backup(args.project_id, args.type)
                if result['success']:
                    print(f"✅ Backup created: {result['backup_id']}")
                    print(f"Size: {format_size(result['size_mb'] * 1024 * 1024)}")
                else:
                    print(f"❌ Backup failed: {result.get('error', 'Unknown error')}")
                    return 1
            
            elif args.backup_action == 'list':
                backups = cli.list_backups(args.project_id, args.limit)
                
                if not backups:
                    print("No backups found")
                else:
                    print(f"💾 Backups for {args.project_id} ({len(backups)}):")
                    
                    headers = ['ID', 'Type', 'Created', 'Size', 'Status']
                    rows = []
                    
                    for backup in backups:
                        rows.append([
                            backup['backup_id'][:8] + '...',
                            backup['backup_type'],
                            backup['timestamp'][:19],
                            format_size(backup['size_bytes']),
                            backup['validation_status']
                        ])
                    
                    print_table(headers, rows)
            
            elif args.backup_action == 'restore':
                result = cli.restore_backup(args.backup_id)
                if result['success']:
                    print(f"✅ Backup restored: {args.backup_id}")
                else:
                    print(f"❌ Restore failed: {args.backup_id}")
                    return 1
            
            elif args.backup_action == 'stats':
                stats = cli.get_backup_stats()
                
                print("💾 Backup Statistics:")
                print(f"Total Backups: {stats.get('total_backups', 0)}")
                print(f"Recent Backups (24h): {stats.get('recent_backups_24h', 0)}")
                print(f"Total Storage: {format_size(stats.get('total_storage_mb', 0) * 1024 * 1024)}")
                print(f"Auto Backup: {'✅ Enabled' if stats.get('auto_backup_enabled') else '❌ Disabled'}")
        
        # Analytics operations
        elif args.category == 'analytics':
            if args.analytics_action == 'usage':
                analysis = cli.analyze_usage(args.project)
                
                if 'error' in analysis:
                    print(f"❌ Analysis error: {analysis['error']}")
                    return 1
                
                print("📊 Usage Analysis:")
                
                usage_stats = analysis.get('usage_statistics', {})
                if usage_stats:
                    print(f"Total Contexts: {usage_stats.get('total_contexts', 0)}")
                    print(f"Total Size: {format_size(usage_stats.get('total_size_mb', 0) * 1024 * 1024)}")
                    print(f"Average Size: {format_size(usage_stats.get('average_size_mb', 0) * 1024 * 1024)}")
                
                quality_metrics = analysis.get('quality_metrics', {})
                if quality_metrics:
                    print(f"Quality Score: {quality_metrics.get('overall_quality_score', 0):.1f}%")
                
                patterns = analysis.get('patterns_detected', [])
                if patterns:
                    print(f"Patterns Detected: {len(patterns)}")
                    for pattern in patterns[:3]:
                        print(f"  • {pattern['description']}")
            
            elif args.analytics_action == 'dashboard':
                dashboard = cli.get_dashboard(args.project, args.days)
                
                if 'error' in dashboard:
                    print(f"❌ Dashboard error: {dashboard['error']}")
                    return 1
                
                print(f"📈 Analytics Dashboard ({args.days} days):")
                print(f"Metrics Collected: {dashboard.get('metrics_count', 0)}")
                
                summary = dashboard.get('summary', {})
                for metric_type, stats in summary.items():
                    print(f"{metric_type.title()}: {stats.get('count', 0)} samples, avg: {stats.get('average', 0):.2f}")
                
                insights = dashboard.get('performance_insights', []) + dashboard.get('usage_insights', [])
                if insights:
                    print("💡 Insights:")
                    for insight in insights[:3]:
                        print(f"  • {insight}")
            
            elif args.analytics_action == 'optimize':
                recommendations = cli.get_optimization_recommendations(args.project)
                
                if not recommendations:
                    print("✅ No optimization recommendations")
                else:
                    print(f"⚡ Optimization Recommendations ({len(recommendations)}):")
                    
                    for i, rec in enumerate(recommendations[:5], 1):
                        priority_icon = "🔴" if rec['priority'] == 'high' else "🟡" if rec['priority'] == 'medium' else "🟢"
                        print(f"{i}. {priority_icon} {rec['title']}")
                        print(f"   Strategy: {rec['strategy']}")
                        print(f"   Savings: {format_size(rec['estimated_savings_mb'] * 1024 * 1024)}")
                        print(f"   Performance: +{rec['estimated_performance_gain']:.1f}%")
            
            elif args.analytics_action == 'stats':
                stats = cli.get_analytics_stats()
                
                print("📊 Analytics Statistics:")
                print(f"Analyses Performed: {stats.get('analyses_performed', 0)}")
                print(f"Patterns Detected: {stats.get('patterns_detected', 0)}")
                print(f"Metrics Collected: {stats.get('metrics_collected', 0)}")
                print(f"Optimizations Applied: {stats.get('optimizations_performed', 0)}")
                print(f"Space Saved: {format_size(stats.get('space_saved_mb', 0) * 1024 * 1024)}")
        
        # System operations
        elif args.category == 'system':
            if args.system_action == 'health':
                health = cli.get_system_health()
                
                print("🏥 System Health:")
                
                for component, status in health.items():
                    if isinstance(status, dict) and 'status' in status:
                        component_status = status['status']
                        icon = "✅" if component_status == 'healthy' else "⚠️" if component_status == 'degraded' else "❌"
                        print(f"  {icon} {component}: {component_status}")
                    elif component != 'timestamp':
                        print(f"  • {component}: {status}")
            
            elif args.system_action == 'export':
                result = cli.export_context(args.project_id, args.format, args.include_sensitive)
                
                if result.get('success'):
                    # Move file to specified location
                    import shutil
                    shutil.move(result['path'], args.output_file)
                    
                    print(f"✅ Context exported: {args.output_file}")
                    print(f"Format: {result['format']}")
                    print(f"Size: {format_size(result['size_bytes'])}")
                else:
                    print(f"❌ Export failed: {result.get('error', 'Unknown error')}")
                    return 1
            
            elif args.system_action == 'import':
                result = cli.import_context(args.input_file, args.project_id, args.strategy)
                
                if result.get('success'):
                    print(f"✅ Context imported: {args.input_file}")
                    print(f"Project: {args.project_id}")
                    print(f"Strategy: {args.strategy}")
                    print(f"Session ID: {result.get('imported_session_id', 'Unknown')}")
                else:
                    print(f"❌ Import failed: {result.get('error', 'Unknown error')}")
                    return 1
        
        return 0
    
    except KeyboardInterrupt:
        print("\n⏹️ Operation cancelled by user")
        return 1
    
    except Exception as e:
        print(f"💥 Error: {e}")
        return 1


if __name__ == '__main__':
    sys.exit(main())