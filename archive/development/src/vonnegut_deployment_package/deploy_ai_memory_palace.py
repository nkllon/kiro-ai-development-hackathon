#!/usr/bin/env python3
"""
AI Memory Palace Deployment Script.

Provides command-line interface for deploying, configuring, and managing
the AI Memory Palace system.
"""

import sys
import argparse
import json
import yaml
from pathlib import Path
from typing import Dict, Any

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from beast_mode.ai_memory_palace.deployment import DeploymentCLI


def main():
    """Main deployment script entry point"""
    parser = argparse.ArgumentParser(
        description="AI Memory Palace Deployment Tool",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Deploy the system
  python deploy_ai_memory_palace.py deploy

  # Deploy with force (redeploy existing)
  python deploy_ai_memory_palace.py deploy --force

  # Check deployment status
  python deploy_ai_memory_palace.py status

  # Show current configuration
  python deploy_ai_memory_palace.py config show

  # Update configuration
  python deploy_ai_memory_palace.py config update --storage-size 200

  # Run database migrations
  python deploy_ai_memory_palace.py migrate

  # Check migration status
  python deploy_ai_memory_palace.py migrate --status

  # Perform health check
  python deploy_ai_memory_palace.py health

  # Undeploy the system
  python deploy_ai_memory_palace.py undeploy
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Deploy command
    deploy_parser = subparsers.add_parser('deploy', help='Deploy AI Memory Palace system')
    deploy_parser.add_argument('--force', action='store_true', 
                              help='Force redeployment of existing system')
    deploy_parser.add_argument('--config', type=str, 
                              help='Path to configuration file')
    
    # Undeploy command
    undeploy_parser = subparsers.add_parser('undeploy', help='Undeploy AI Memory Palace system')
    
    # Status command
    status_parser = subparsers.add_parser('status', help='Show deployment status')
    
    # Config command
    config_parser = subparsers.add_parser('config', help='Configuration management')
    config_subparsers = config_parser.add_subparsers(dest='config_action')
    
    config_show_parser = config_subparsers.add_parser('show', help='Show current configuration')
    config_show_parser.add_argument('--format', choices=['json', 'yaml'], default='yaml',
                                   help='Output format')
    
    config_update_parser = config_subparsers.add_parser('update', help='Update configuration')
    config_update_parser.add_argument('--storage-size', type=int, 
                                     help='Max context size in MB')
    config_update_parser.add_argument('--session-timeout', type=int,
                                     help='Session timeout in minutes')
    config_update_parser.add_argument('--backup-interval', type=int,
                                     help='Auto backup interval in seconds')
    config_update_parser.add_argument('--enable-encryption', action='store_true',
                                     help='Enable encryption')
    config_update_parser.add_argument('--disable-encryption', action='store_true',
                                     help='Disable encryption')
    
    # Migrate command
    migrate_parser = subparsers.add_parser('migrate', help='Database migration management')
    migrate_parser.add_argument('--dry-run', action='store_true',
                               help='Show what migrations would be applied')
    migrate_parser.add_argument('--status', action='store_true',
                               help='Show migration status')
    
    # Health command
    health_parser = subparsers.add_parser('health', help='Perform system health check')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 1
    
    try:
        cli = DeploymentCLI()
        
        if args.command == 'deploy':
            print("🚀 Deploying AI Memory Palace system...")
            result = cli.deploy(force=args.force)
            
            if result['success']:
                print(f"✅ Deployment successful (ID: {result['deployment_id']})")
                print(f"Environment: {result['environment']}")
                print(f"Steps completed: {', '.join(result['steps_completed'])}")
                
                if result['components_deployed']:
                    print("Components deployed:")
                    for component, status in result['components_deployed'].items():
                        status_icon = "✅" if status else "❌"
                        print(f"  {status_icon} {component}")
            else:
                print("❌ Deployment failed")
                if result.get('errors'):
                    print("Errors:")
                    for error in result['errors']:
                        print(f"  - {error}")
                return 1
        
        elif args.command == 'undeploy':
            print("🛑 Undeploying AI Memory Palace system...")
            result = cli.undeploy()
            
            if result['success']:
                print("✅ Undeployment successful")
                print(f"Steps completed: {', '.join(result['steps_completed'])}")
            else:
                print("❌ Undeployment failed")
                if result.get('errors'):
                    print("Errors:")
                    for error in result['errors']:
                        print(f"  - {error}")
                return 1
        
        elif args.command == 'status':
            print("📊 AI Memory Palace Status:")
            status = cli.status()
            
            print(f"Status: {status['status']}")
            print(f"Environment: {status['environment']}")
            print(f"Config loaded: {status['config_loaded']}")
            print(f"Config valid: {status['config_valid']}")
            print(f"Health monitoring: {status['health_monitoring_active']}")
            
            if status['components_initialized']:
                print("Components:")
                for component, initialized in status['components_initialized'].items():
                    status_icon = "✅" if initialized else "❌"
                    print(f"  {status_icon} {component}")
        
        elif args.command == 'config':
            if args.config_action == 'show':
                config = cli.config_show()
                
                if args.format == 'json':
                    print(json.dumps(config, indent=2))
                else:
                    print(yaml.dump(config, default_flow_style=False, indent=2))
            
            elif args.config_action == 'update':
                updates = {}
                
                if args.storage_size:
                    updates.setdefault('storage', {})['max_context_size_mb'] = args.storage_size
                
                if args.session_timeout:
                    updates.setdefault('performance', {})['session_timeout_minutes'] = args.session_timeout
                
                if args.backup_interval:
                    updates.setdefault('performance', {})['auto_backup_interval_seconds'] = args.backup_interval
                
                if args.enable_encryption:
                    updates.setdefault('security', {})['encryption_enabled'] = True
                
                if args.disable_encryption:
                    updates.setdefault('security', {})['encryption_enabled'] = False
                
                if updates:
                    success = cli.config_update(updates)
                    if success:
                        print("✅ Configuration updated successfully")
                    else:
                        print("❌ Configuration update failed")
                        return 1
                else:
                    print("No configuration updates specified")
            
            else:
                config_parser.print_help()
        
        elif args.command == 'migrate':
            if args.status:
                print("📊 Migration Status:")
                status = cli.migration_status()
                
                if 'error' in status:
                    print(f"❌ Error: {status['error']}")
                    return 1
                
                print(f"Total migrations: {status['total_migrations']}")
                print(f"Applied: {status['applied_migrations']}")
                print(f"Pending: {status['pending_migrations']}")
                
                if status['last_applied']:
                    print(f"Last applied: {status['last_applied']}")
                
                if status['next_pending']:
                    print(f"Next pending: {status['next_pending']}")
            
            else:
                print("🗄️ Running database migrations...")
                result = cli.migrate(dry_run=args.dry_run)
                
                if result['success']:
                    if args.dry_run:
                        print("✅ Dry run completed")
                        if result['applied_migrations']:
                            print("Would apply migrations:")
                            for migration in result['applied_migrations']:
                                print(f"  - {migration}")
                        else:
                            print("No pending migrations")
                    else:
                        print(f"✅ Applied {result['migrations_applied']} migrations")
                        if result['applied_migrations']:
                            print("Applied migrations:")
                            for migration in result['applied_migrations']:
                                print(f"  - {migration}")
                else:
                    print("❌ Migration failed")
                    if result.get('error'):
                        print(f"Error: {result['error']}")
                    return 1
        
        elif args.command == 'health':
            print("🏥 Performing health check...")
            health = cli.health_check()
            
            print(f"Overall status: {health['overall_status']}")
            print(f"Timestamp: {health['timestamp']}")
            
            if 'components' in health:
                print("Component health:")
                for component, status in health['components'].items():
                    status_icon = "✅" if status == "healthy" else "❌"
                    print(f"  {status_icon} {component}: {status}")
            
            if health['overall_status'] != 'healthy':
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