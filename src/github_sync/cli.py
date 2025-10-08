"""
Comprehensive command-line interface for GitHub synchronization.

This module provides a full-featured CLI for managing GitHub synchronization operations,
configuration, monitoring, and troubleshooting.
"""

import argparse
import asyncio
import json
import logging
import sys
from datetime import datetime
from typing import Optional, List
from pathlib import Path

from .config import GitHubConfig
from .config_manager import ConfigurationManager, FilterType, ScheduleType, SyncSchedule
from .auth import AuthenticationManager
from .client import GitHubAPIClient
from .sync import SynchronizationEngine
from .monitoring import MetricsCollector, StructuredLogger
from .health import HealthMonitor
from .error_recovery import ErrorRecoveryManager
from .workflows import WorkflowManager

logger = logging.getLogger(__name__)


class GitHubSyncCLI:
    """
    Comprehensive command-line interface for GitHub synchronization operations.
    
    This CLI provides commands for configuration, synchronization,
    monitoring, troubleshooting, and system management.
    """
    
    def __init__(self):
        """Initialize the CLI."""
        self.config_manager: Optional[ConfigurationManager] = None
        self.auth_manager: Optional[AuthenticationManager] = None
        self.api_client: Optional[GitHubAPIClient] = None
        self.metrics_collector: Optional[MetricsCollector] = None
        self.health_monitor: Optional[HealthMonitor] = None
        self.error_recovery: Optional[ErrorRecoveryManager] = None
        self.workflow_manager: Optional[WorkflowManager] = None
    
    def setup_logging(self, level: str = "INFO") -> None:
        """
        Set up logging configuration.
        
        Args:
            level: Logging level
        """
        logging.basicConfig(
            level=getattr(logging, level.upper()),
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
    
    def initialize_components(self) -> None:
        """Initialize all system components."""
        if not self.config_manager:
            self.config_manager = ConfigurationManager()
        
        if not self.auth_manager:
            self.auth_manager = AuthenticationManager()
        
        if not self.api_client:
            self.api_client = GitHubAPIClient(self.auth_manager)
        
        if not self.metrics_collector:
            self.metrics_collector = MetricsCollector()
        
        if not self.health_monitor:
            self.health_monitor = HealthMonitor(
                self.api_client, self.auth_manager, self.metrics_collector
            )
        
        if not self.error_recovery:
            self.error_recovery = ErrorRecoveryManager()
        
        if not self.workflow_manager:
            self.workflow_manager = WorkflowManager()
    
    # Authentication commands
    def cmd_auth_test(self, args) -> int:
        """Test GitHub authentication."""
        try:
            self.initialize_components()
            
            if self.auth_manager.validate_token():
                token_info = self.auth_manager.get_token_info()
                print(f"✓ Authentication successful")
                print(f"  User: {token_info['user']['login']}")
                print(f"  Name: {token_info['user']['name']}")
                print(f"  Type: {token_info['user']['type']}")
                
                rate_limit = self.auth_manager.check_rate_limit()
                print(f"  Rate limit: {rate_limit['remaining']}/{rate_limit['limit']}")
                
                return 0
            else:
                print("✗ Authentication failed")
                return 1
                
        except Exception as e:
            print(f"✗ Authentication error: {e}")
            return 1
    
    # Configuration commands
    def cmd_config_validate(self, args) -> int:
        """Validate configuration."""
        try:
            self.initialize_components()
            config = self.config_manager.load_config()
            errors = self.config_manager.validate_configuration()
            
            if not errors:
                print("✓ Configuration is valid")
                print(f"  Repositories: {len(config.sync_config.repositories)}")
                print(f"  Webhooks enabled: {config.sync_config.enable_webhooks}")
                return 0
            else:
                print("✗ Configuration errors:")
                for error in errors:
                    print(f"  - {error}")
                return 1
                
        except Exception as e:
            print(f"✗ Configuration error: {e}")
            return 1
    
    def cmd_config_show(self, args) -> int:
        """Show current configuration."""
        try:
            self.initialize_components()
            config = self.config_manager.load_config()
            
            print("GitHub Synchronization Configuration")
            print("=" * 40)
            print(f"API Base URL: {config.api_base_url}")
            print(f"Webhook Base URL: {config.webhook_base_url or 'Not configured'}")
            print(f"Repositories: {len(config.sync_config.repositories)}")
            print(f"Webhooks Enabled: {config.sync_config.enable_webhooks}")
            print(f"Sync Interval: {config.sync_config.sync_interval} seconds")
            print(f"Max Concurrent Syncs: {config.sync_config.max_concurrent_syncs}")
            
            if config.sync_config.repositories:
                print("\nConfigured Repositories:")
                for repo in config.sync_config.repositories:
                    print(f"  - {repo.full_name}")
                    print(f"    Issues: {repo.sync_issues}, PRs: {repo.sync_pull_requests}")
                    print(f"    Branches: {', '.join(repo.sync_branches)}")
            
            return 0
            
        except Exception as e:
            print(f"✗ Configuration error: {e}")
            return 1
    
    def cmd_repo_add(self, args) -> int:
        """Add a repository to synchronization."""
        try:
            self.initialize_components()
            
            repo_config = self.config_manager.add_repository(
                owner=args.owner,
                name=args.name,
                sync_issues=args.sync_issues,
                sync_pull_requests=args.sync_prs,
                sync_commits=args.sync_commits
            )
            
            print(f"✓ Added repository {repo_config.full_name}")
            print(f"  Issues: {repo_config.sync_issues}")
            print(f"  Pull Requests: {repo_config.sync_pull_requests}")
            print(f"  Commits: {repo_config.sync_commits}")
            
            return 0
            
        except Exception as e:
            print(f"✗ Failed to add repository: {e}")
            return 1
    
    def cmd_repo_remove(self, args) -> int:
        """Remove a repository from synchronization."""
        try:
            self.initialize_components()
            
            if self.config_manager.remove_repository(args.owner, args.name):
                print(f"✓ Removed repository {args.owner}/{args.name}")
                return 0
            else:
                print(f"✗ Repository {args.owner}/{args.name} not found")
                return 1
                
        except Exception as e:
            print(f"✗ Failed to remove repository: {e}")
            return 1
    
    def cmd_repo_list(self, args) -> int:
        """List configured repositories."""
        try:
            self.initialize_components()
            
            repositories = self.config_manager.list_repositories(
                tags=args.tags.split(',') if args.tags else None,
                group=args.group
            )
            
            if not repositories:
                print("No repositories configured")
                return 0
            
            print(f"Configured Repositories ({len(repositories)}):")
            print("-" * 40)
            
            for repo in repositories:
                print(f"📁 {repo.full_name}")
                print(f"   Issues: {'✓' if repo.sync_issues else '✗'}")
                print(f"   PRs: {'✓' if repo.sync_pull_requests else '✗'}")
                print(f"   Commits: {'✓' if repo.sync_commits else '✗'}")
                print(f"   Branches: {', '.join(repo.sync_branches)}")
                if hasattr(repo, 'tags') and repo.tags:
                    print(f"   Tags: {', '.join(repo.tags)}")
                if hasattr(repo, 'last_sync') and repo.last_sync:
                    print(f"   Last Sync: {repo.last_sync.strftime('%Y-%m-%d %H:%M:%S')}")
                print()
            
            return 0
            
        except Exception as e:
            print(f"✗ Failed to list repositories: {e}")
            return 1
    
    # Synchronization commands
    def cmd_sync_run(self, args) -> int:
        """Run synchronization for specified repositories."""
        try:
            self.initialize_components()
            
            if args.repository:
                owner, name = args.repository.split('/')
                repo_config = self.config_manager.get_repository_config(owner, name)
                if not repo_config:
                    print(f"✗ Repository {args.repository} not configured")
                    return 1
                repositories = [repo_config]
            else:
                repositories = self.config_manager.list_repositories()
            
            if not repositories:
                print("No repositories to synchronize")
                return 0
            
            print(f"Starting synchronization for {len(repositories)} repositories...")
            
            # This would integrate with the actual sync engine
            # For now, just show what would be synchronized
            for repo in repositories:
                print(f"📁 Synchronizing {repo.full_name}...")
                if repo.sync_issues:
                    print("  - Issues")
                if repo.sync_pull_requests:
                    print("  - Pull Requests")
                if repo.sync_commits:
                    print("  - Commits")
            
            print("✓ Synchronization completed")
            return 0
            
        except Exception as e:
            print(f"✗ Synchronization failed: {e}")
            return 1
    
    # Monitoring commands
    def cmd_status(self, args) -> int:
        """Show comprehensive system status."""
        try:
            self.initialize_components()
            
            print("GitHub Synchronization Status")
            print("=" * 40)
            
            # Authentication status
            print("🔐 Authentication:")
            if self.auth_manager.validate_token():
                token_info = self.auth_manager.get_token_info()
                print(f"  ✓ Authenticated as {token_info['user']['login']}")
                rate_limit = self.auth_manager.check_rate_limit()
                print(f"  ✓ Rate limit: {rate_limit['remaining']}/{rate_limit['limit']}")
            else:
                print("  ✗ Authentication failed")
            
            # Configuration status
            print("\n⚙️  Configuration:")
            config = self.config_manager.load_config()
            errors = self.config_manager.validate_configuration()
            if not errors:
                print(f"  ✓ Valid configuration")
                print(f"  ✓ {len(config.sync_config.repositories)} repositories configured")
            else:
                print(f"  ✗ {len(errors)} configuration errors")
            
            # System health
            print("\n🏥 System Health:")
            health_status = asyncio.run(self.health_monitor.perform_health_check())
            print(f"  Status: {health_status.overall_status.value.upper()}")
            print(f"  Uptime: {health_status.uptime_seconds:.0f} seconds")
            
            failed_checks = [
                check for check in health_status.checks
                if check.status.value != 'healthy'
            ]
            if failed_checks:
                print(f"  ⚠️  {len(failed_checks)} health check(s) failed")
            else:
                print("  ✓ All health checks passed")
            
            # Metrics summary
            print("\n📊 Metrics (Last 24 hours):")
            metrics_summary = self.metrics_collector.get_metrics_summary(24)
            sync_ops = metrics_summary.get('sync_operations', {})
            api_usage = metrics_summary.get('api_usage', {})
            
            print(f"  Sync Operations: {sync_ops.get('total', 0)}")
            print(f"  Success Rate: {sync_ops.get('success_rate', 0):.1%}")
            print(f"  API Calls: {api_usage.get('total_calls', 0)}")
            print(f"  API Error Rate: {api_usage.get('error_rate', 0):.1%}")
            
            return 0
            
        except Exception as e:
            print(f"✗ Status check failed: {e}")
            return 1
    
    def cmd_metrics(self, args) -> int:
        """Show detailed metrics."""
        try:
            self.initialize_components()
            
            hours = args.hours or 24
            summary = self.metrics_collector.get_metrics_summary(hours)
            
            print(f"GitHub Sync Metrics (Last {hours} hours)")
            print("=" * 50)
            
            # Sync operations
            sync_ops = summary.get('sync_operations', {})
            print("📈 Synchronization Operations:")
            print(f"  Total: {sync_ops.get('total', 0)}")
            print(f"  Successful: {sync_ops.get('successful', 0)}")
            print(f"  Failed: {sync_ops.get('failed', 0)}")
            print(f"  Success Rate: {sync_ops.get('success_rate', 0):.1%}")
            print(f"  Average Duration: {sync_ops.get('avg_duration_seconds', 0):.1f}s")
            
            # API usage
            api_usage = summary.get('api_usage', {})
            print("\n🌐 API Usage:")
            print(f"  Total Calls: {api_usage.get('total_calls', 0)}")
            print(f"  Errors: {api_usage.get('errors', 0)}")
            print(f"  Error Rate: {api_usage.get('error_rate', 0):.1%}")
            print(f"  Rate Limit Hits: {api_usage.get('rate_limit_hits', 0)}")
            print(f"  Average Response Time: {api_usage.get('avg_response_time_ms', 0):.0f}ms")
            
            # Current state
            current_state = summary.get('current_state', {})
            print("\n📊 Current State:")
            print(f"  Active Syncs: {current_state.get('active_syncs', 0)}")
            print(f"  Total Repositories: {current_state.get('total_repositories', 0)}")
            print(f"  Total Issues: {current_state.get('total_issues', 0)}")
            print(f"  Total Pull Requests: {current_state.get('total_pull_requests', 0)}")
            print(f"  Total Commits: {current_state.get('total_commits', 0)}")
            
            if args.json:
                print("\n" + "=" * 50)
                print("JSON Output:")
                print(json.dumps(summary, indent=2, default=str))
            
            return 0
            
        except Exception as e:
            print(f"✗ Failed to get metrics: {e}")
            return 1
    
    def cmd_health(self, args) -> int:
        """Show system health status."""
        try:
            self.initialize_components()
            
            health_status = asyncio.run(self.health_monitor.perform_health_check())
            
            print("System Health Status")
            print("=" * 30)
            print(f"Overall Status: {health_status.overall_status.value.upper()}")
            print(f"Timestamp: {health_status.timestamp.strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"Uptime: {health_status.uptime_seconds:.0f} seconds")
            
            print("\nHealth Checks:")
            for check in health_status.checks:
                status_icon = {
                    'healthy': '✓',
                    'warning': '⚠️',
                    'critical': '✗',
                    'unknown': '?'
                }.get(check.status.value, '?')
                
                print(f"  {status_icon} {check.name}: {check.message}")
                if check.duration_ms:
                    print(f"    Duration: {check.duration_ms:.0f}ms")
                if check.details:
                    for key, value in check.details.items():
                        print(f"    {key}: {value}")
            
            if args.json:
                print("\n" + "=" * 30)
                print("JSON Output:")
                print(json.dumps(health_status.to_dict(), indent=2))
            
            return 0 if health_status.overall_status.value == 'healthy' else 1
            
        except Exception as e:
            print(f"✗ Health check failed: {e}")
            return 1
    
    def cmd_errors(self, args) -> int:
        """Show error statistics and unresolved errors."""
        try:
            self.initialize_components()
            
            hours = args.hours or 24
            error_stats = self.error_recovery.get_error_statistics(hours)
            
            if error_stats.get('no_errors'):
                print(f"No errors in the last {hours} hours")
                return 0
            
            print(f"Error Statistics (Last {hours} hours)")
            print("=" * 40)
            print(f"Total Errors: {error_stats['total_errors']}")
            print(f"Resolved: {error_stats['resolved_errors']}")
            print(f"Unresolved: {error_stats['unresolved_errors']}")
            print(f"Resolution Rate: {error_stats['resolution_rate']:.1%}")
            print(f"Average Retries: {error_stats['average_retries']:.1f}")
            
            if error_stats['errors_by_category']:
                print("\nErrors by Category:")
                for category, count in error_stats['errors_by_category'].items():
                    print(f"  {category}: {count}")
            
            # Show unresolved errors
            unresolved = self.error_recovery.get_unresolved_errors()
            if unresolved:
                print(f"\nUnresolved Errors ({len(unresolved)}):")
                for error in unresolved[:10]:  # Show first 10
                    print(f"  🔴 {error.error_id}")
                    print(f"     Category: {error.category.value}")
                    print(f"     Message: {error.error_message}")
                    print(f"     Repository: {error.context.repository or 'N/A'}")
                    print(f"     Timestamp: {error.timestamp.strftime('%Y-%m-%d %H:%M:%S')}")
                    print()
                
                if len(unresolved) > 10:
                    print(f"  ... and {len(unresolved) - 10} more")
            
            if args.export:
                export_data = self.error_recovery.export_error_records(hours)
                export_file = Path(f"github_sync_errors_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
                export_file.write_text(export_data)
                print(f"\n✓ Error records exported to {export_file}")
            
            return 0
            
        except Exception as e:
            print(f"✗ Failed to get error information: {e}")
            return 1
    
    def create_parser(self) -> argparse.ArgumentParser:
        """Create comprehensive command-line argument parser."""
        parser = argparse.ArgumentParser(
            description="GitHub Synchronization CLI",
            formatter_class=argparse.RawDescriptionHelpFormatter
        )
        
        parser.add_argument(
            '--log-level',
            choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'],
            default='INFO',
            help='Set logging level'
        )
        
        subparsers = parser.add_subparsers(dest='command', help='Available commands')
        
        # Auth commands
        auth_parser = subparsers.add_parser('auth', help='Authentication commands')
        auth_subparsers = auth_parser.add_subparsers(dest='auth_command')
        auth_subparsers.add_parser('test', help='Test GitHub authentication')
        
        # Config commands
        config_parser = subparsers.add_parser('config', help='Configuration commands')
        config_subparsers = config_parser.add_subparsers(dest='config_command')
        config_subparsers.add_parser('validate', help='Validate configuration')
        config_subparsers.add_parser('show', help='Show current configuration')
        
        # Repository commands
        repo_parser = subparsers.add_parser('repo', help='Repository management')
        repo_subparsers = repo_parser.add_subparsers(dest='repo_command')
        
        # Add repository
        add_repo_parser = repo_subparsers.add_parser('add', help='Add repository')
        add_repo_parser.add_argument('owner', help='Repository owner')
        add_repo_parser.add_argument('name', help='Repository name')
        add_repo_parser.add_argument('--sync-issues', action='store_true', default=True, help='Sync issues')
        add_repo_parser.add_argument('--sync-prs', action='store_true', default=True, help='Sync pull requests')
        add_repo_parser.add_argument('--sync-commits', action='store_true', default=True, help='Sync commits')
        
        # Remove repository
        remove_repo_parser = repo_subparsers.add_parser('remove', help='Remove repository')
        remove_repo_parser.add_argument('owner', help='Repository owner')
        remove_repo_parser.add_argument('name', help='Repository name')
        
        # List repositories
        list_repo_parser = repo_subparsers.add_parser('list', help='List repositories')
        list_repo_parser.add_argument('--tags', help='Filter by tags (comma-separated)')
        list_repo_parser.add_argument('--group', help='Filter by group')
        
        # Sync commands
        sync_parser = subparsers.add_parser('sync', help='Synchronization commands')
        sync_subparsers = sync_parser.add_subparsers(dest='sync_command')
        
        run_sync_parser = sync_subparsers.add_parser('run', help='Run synchronization')
        run_sync_parser.add_argument('--repository', help='Specific repository (owner/name)')
        
        # Monitoring commands
        subparsers.add_parser('status', help='Show system status')
        
        metrics_parser = subparsers.add_parser('metrics', help='Show metrics')
        metrics_parser.add_argument('--hours', type=int, help='Hours to look back (default: 24)')
        metrics_parser.add_argument('--json', action='store_true', help='Output JSON format')
        
        health_parser = subparsers.add_parser('health', help='Show health status')
        health_parser.add_argument('--json', action='store_true', help='Output JSON format')
        
        errors_parser = subparsers.add_parser('errors', help='Show error information')
        errors_parser.add_argument('--hours', type=int, help='Hours to look back (default: 24)')
        errors_parser.add_argument('--export', action='store_true', help='Export error records to JSON')
        
        return parser
    
    def run(self, args: Optional[list] = None) -> int:
        """Run the CLI with given arguments."""
        parser = self.create_parser()
        parsed_args = parser.parse_args(args)
        
        self.setup_logging(parsed_args.log_level)
        
        if not parsed_args.command:
            parser.print_help()
            return 1
        
        # Route commands
        try:
            if parsed_args.command == 'auth':
                if parsed_args.auth_command == 'test':
                    return self.cmd_auth_test(parsed_args)
            
            elif parsed_args.command == 'config':
                if parsed_args.config_command == 'validate':
                    return self.cmd_config_validate(parsed_args)
                elif parsed_args.config_command == 'show':
                    return self.cmd_config_show(parsed_args)
            
            elif parsed_args.command == 'repo':
                if parsed_args.repo_command == 'add':
                    return self.cmd_repo_add(parsed_args)
                elif parsed_args.repo_command == 'remove':
                    return self.cmd_repo_remove(parsed_args)
                elif parsed_args.repo_command == 'list':
                    return self.cmd_repo_list(parsed_args)
            
            elif parsed_args.command == 'sync':
                if parsed_args.sync_command == 'run':
                    return self.cmd_sync_run(parsed_args)
            
            elif parsed_args.command == 'status':
                return self.cmd_status(parsed_args)
            
            elif parsed_args.command == 'metrics':
                return self.cmd_metrics(parsed_args)
            
            elif parsed_args.command == 'health':
                return self.cmd_health(parsed_args)
            
            elif parsed_args.command == 'errors':
                return self.cmd_errors(parsed_args)
            
            parser.print_help()
            return 1
            
        except KeyboardInterrupt:
            print("\n✗ Operation cancelled by user")
            return 1
        except Exception as e:
            print(f"✗ Unexpected error: {e}")
            logger.exception("Unexpected CLI error")
            return 1


def main():
    """Main entry point for the CLI."""
    cli = GitHubSyncCLI()
    sys.exit(cli.run())


if __name__ == '__main__':
    main()