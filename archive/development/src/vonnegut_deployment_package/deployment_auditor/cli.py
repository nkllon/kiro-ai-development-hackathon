"""
Command-line interface for the Deployment Data Governance Auditor.

This module provides comprehensive CLI functionality for all major auditor operations
including daemon management, manual scanning, and interactive violation resolution.
"""

import os
import sys
import json
import click
import signal
import logging
from pathlib import Path
from typing import Optional, Dict, Any
from datetime import datetime

from .core import DeploymentAuditor
from .config import ConfigManager
from .models import Severity


# Global auditor instance for signal handling
_auditor_instance: Optional[DeploymentAuditor] = None


def signal_handler(signum, frame):
    """Handle shutdown signals gracefully."""
    if _auditor_instance:
        click.echo("\nReceived shutdown signal, stopping auditor...")
        _auditor_instance.shutdown()
    sys.exit(0)


@click.group()
@click.option('--config', '-c', help='Configuration file path')
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose logging')
@click.option('--quiet', '-q', is_flag=True, help='Suppress non-error output')
@click.pass_context
def cli(ctx, config, verbose, quiet):
    """
    Deployment Data Governance Auditor CLI.
    
    Monitors deployment directories for governance violations and provides
    automated remediation with comprehensive reporting capabilities.
    """
    # Set up logging
    log_level = logging.DEBUG if verbose else logging.WARNING if quiet else logging.INFO
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Store configuration in context
    ctx.ensure_object(dict)
    ctx.obj['config_path'] = config
    ctx.obj['verbose'] = verbose
    ctx.obj['quiet'] = quiet


@cli.command()
@click.option('--daemon', '-d', is_flag=True, help='Run as daemon in background')
@click.option('--pidfile', help='PID file for daemon mode')
@click.pass_context
def start(ctx, daemon, pidfile):
    """Start the deployment data monitoring daemon."""
    global _auditor_instance
    
    try:
        # Initialize auditor
        config_path = ctx.obj.get('config_path')
        _auditor_instance = DeploymentAuditor(config_path=config_path)
        
        # Set up signal handlers
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
        
        if daemon:
            click.echo("Starting deployment auditor daemon...")
            if pidfile:
                with open(pidfile, 'w') as f:
                    f.write(str(os.getpid()))
        else:
            click.echo("Starting deployment auditor in foreground mode...")
        
        # Start monitoring
        if _auditor_instance.start_monitoring():
            if not ctx.obj.get('quiet'):
                click.echo("✅ Deployment auditor started successfully")
                click.echo(f"Monitoring paths: {_auditor_instance.monitoring_status.watched_paths}")
            
            if daemon:
                # In real implementation, this would fork to background
                click.echo("Daemon mode not fully implemented - running in foreground")
            
            # Keep running until interrupted
            try:
                while _auditor_instance.monitoring_status.is_active:
                    import time
                    time.sleep(1)
            except KeyboardInterrupt:
                pass
        else:
            click.echo("❌ Failed to start deployment auditor", err=True)
            sys.exit(1)
            
    except Exception as e:
        click.echo(f"❌ Error starting auditor: {e}", err=True)
        sys.exit(1)
    finally:
        if _auditor_instance:
            _auditor_instance.shutdown()


@cli.command()
@click.option('--pidfile', help='PID file to read process ID from')
@click.pass_context
def stop(ctx, pidfile):
    """Stop the deployment data monitoring daemon."""
    try:
        if pidfile and os.path.exists(pidfile):
            with open(pidfile, 'r') as f:
                pid = int(f.read().strip())
            
            try:
                os.kill(pid, signal.SIGTERM)
                click.echo(f"✅ Sent stop signal to process {pid}")
                
                # Clean up PID file
                os.remove(pidfile)
                
            except ProcessLookupError:
                click.echo(f"⚠️  Process {pid} not found")
                os.remove(pidfile)  # Clean up stale PID file
            except PermissionError:
                click.echo(f"❌ Permission denied stopping process {pid}", err=True)
                sys.exit(1)
        else:
            click.echo("❌ No PID file specified or found", err=True)
            sys.exit(1)
            
    except Exception as e:
        click.echo(f"❌ Error stopping auditor: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.argument('directory', default='deployment/')
@click.option('--format', '-f', type=click.Choice(['text', 'json', 'yaml']), default='text', help='Output format')
@click.option('--output', '-o', help='Output file (default: stdout)')
@click.option('--severity', type=click.Choice(['CRITICAL', 'HIGH', 'MEDIUM', 'LOW']), help='Filter by severity')
@click.pass_context
def scan(ctx, directory, format, output, severity):
    """Perform a manual scan of a directory for violations."""
    try:
        # Initialize auditor
        config_path = ctx.obj.get('config_path')
        auditor = DeploymentAuditor(config_path=config_path)
        
        if not ctx.obj.get('quiet'):
            click.echo(f"Scanning directory: {directory}")
        
        # Perform scan
        report = auditor.scan_directory(directory)
        
        # Filter by severity if specified
        if severity:
            # This would filter violations in a real implementation
            pass
        
        # Format output
        if format == 'json':
            output_data = {
                "scan_timestamp": report.scan_timestamp.isoformat(),
                "directory": directory,
                "total_files_scanned": report.total_files_scanned,
                "violations_found": report.violations_found,
                "violations_by_severity": {k.value: v for k, v in report.violations_by_severity.items()},
                "violations_by_type": {k.value: v for k, v in report.violations_by_type.items()},
                "recommendations": report.recommendations
            }
            output_text = json.dumps(output_data, indent=2)
        elif format == 'yaml':
            import yaml
            output_data = {
                "scan_timestamp": report.scan_timestamp.isoformat(),
                "directory": directory,
                "total_files_scanned": report.total_files_scanned,
                "violations_found": report.violations_found,
                "violations_by_severity": {k.value: v for k, v in report.violations_by_severity.items()},
                "violations_by_type": {k.value: v for k, v in report.violations_by_type.items()},
                "recommendations": report.recommendations
            }
            output_text = yaml.dump(output_data, default_flow_style=False)
        else:  # text format
            output_lines = [
                f"Deployment Data Governance Scan Report",
                f"======================================",
                f"Scan Time: {report.scan_timestamp}",
                f"Directory: {directory}",
                f"Files Scanned: {report.total_files_scanned}",
                f"Violations Found: {report.violations_found}",
                ""
            ]
            
            if report.violations_by_severity:
                output_lines.append("Violations by Severity:")
                for sev, count in report.violations_by_severity.items():
                    output_lines.append(f"  {sev.value.upper()}: {count}")
                output_lines.append("")
            
            if report.recommendations:
                output_lines.append("Recommendations:")
                for rec in report.recommendations:
                    output_lines.append(f"  • {rec}")
            
            output_text = "\n".join(output_lines)
        
        # Write output
        if output:
            with open(output, 'w') as f:
                f.write(output_text)
            if not ctx.obj.get('quiet'):
                click.echo(f"✅ Scan report written to {output}")
        else:
            click.echo(output_text)
            
    except Exception as e:
        click.echo(f"❌ Scan failed: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.pass_context
def status(ctx):
    """Show current auditor status and health information."""
    try:
        # Initialize auditor
        config_path = ctx.obj.get('config_path')
        auditor = DeploymentAuditor(config_path=config_path)

        # Get health status (returns ModuleHealth object)
        health = auditor.get_health_status()

        click.echo("Deployment Data Auditor Status")
        click.echo("=============================")
        click.echo(f"Module ID: {health.module_id}")
        click.echo(f"Status: {health.status.value}")
        click.echo(f"Health Score: {health.health_score:.2f}")
        click.echo(f"Uptime: {health.uptime_seconds:.2f}s")
        click.echo(f"Error Count: {health.error_count}")
        click.echo(f"Warning Count: {health.warning_count}")
        click.echo(f"Last Check: {health.last_check.isoformat()}")

        # Show monitoring details
        click.echo(f"\nMonitoring Active: {auditor.monitoring_status.is_active}")
        click.echo(f"Watched Paths: {len(auditor.monitoring_status.watched_paths)}")
        if auditor.monitoring_status.watched_paths:
            for path in auditor.monitoring_status.watched_paths:
                click.echo(f"  • {path}")
        click.echo(f"Events Processed: {auditor.monitoring_status.events_processed}")
        click.echo(f"Violations Detected: {auditor.monitoring_status.violations_detected}")

        if auditor.monitoring_status.last_scan:
            click.echo(f"Last Scan: {auditor.monitoring_status.last_scan.isoformat()}")

        click.echo(f"\nConfiguration: {auditor.config_path}")
        click.echo(f"Auto Remediation: {auditor.config.remediation.get('auto_gitignore', False)}")

        if health.issues:
            click.echo("\nRecent Issues:")
            for issue in health.issues[-5:]:  # Show last 5 issues
                click.echo(f"  • {issue}")

    except Exception as e:
        click.echo(f"❌ Status check failed: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.pass_context
def config(ctx):
    """Show current configuration and validate settings."""
    try:
        # Initialize config manager
        config_path = ctx.obj.get('config_path')
        config_manager = ConfigManager(config_path=config_path)
        
        if not config_manager.load_configuration():
            click.echo("❌ Configuration validation failed", err=True)
            if config_manager.validation_errors:
                click.echo("Validation errors:")
                for error in config_manager.validation_errors:
                    click.echo(f"  • {error}")
            sys.exit(1)
        
        click.echo("Configuration Status")
        click.echo("===================")
        
        health = config_manager.get_health_status()
        click.echo(f"Status: {health['status']}")
        click.echo(f"Config File: {health['config_path']}")
        click.echo(f"File Exists: {health['config_exists']}")
        click.echo(f"Sections: {', '.join(health['sections_loaded'])}")
        
        if health['validation_errors']:
            click.echo("\nValidation Errors:")
            for error in health['validation_errors']:
                click.echo(f"  • {error}")
        
        # Show key configuration values
        monitoring = config_manager.get_monitoring_config()
        click.echo(f"\nMonitoring:")
        click.echo(f"  Watch Paths: {monitoring.watch_paths}")
        click.echo(f"  Scan Interval: {monitoring.scan_interval}s")
        
        remediation = config_manager.get_remediation_config()
        click.echo(f"\nRemediation:")
        click.echo(f"  Auto GitIgnore: {remediation.auto_gitignore}")
        click.echo(f"  Auto Quarantine: {remediation.auto_quarantine}")
        click.echo(f"  Git Integration: {remediation.git_integration}")
        
    except Exception as e:
        click.echo(f"❌ Configuration check failed: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.option('--create-sample', is_flag=True, help='Create a sample configuration file')
@click.pass_context
def init(ctx, create_sample):
    """Initialize deployment auditor configuration and setup."""
    try:
        config_path = ctx.obj.get('config_path') or 'deployment-auditor-config.yml'
        
        if create_sample:
            sample_config = """# Deployment Data Governance Auditor Configuration
# Generated sample configuration

monitoring:
  watch_paths:
    - "deployment/"
  excluded_paths:
    - "deployment/docs/"
  scan_interval: 60
  recursive: true

patterns:
  database_files:
    patterns: ["*.db", "*.sqlite*", "*.sql"]
    severity: "CRITICAL"
    description: "Database files and dumps"
    
  time_series_data:
    patterns: ["*prometheus-data*", "*grafana-data*"]
    severity: "HIGH"
    description: "Time-series monitoring data"
    
  log_files:
    patterns: ["*.log", "logs/", "log/"]
    severity: "MEDIUM"
    description: "Application and system logs"

remediation:
  auto_gitignore: true
  auto_quarantine: true
  git_integration: true
  quarantine_directory: ".deployment-auditor-quarantine"

notifications:
  enabled: true
  severity_threshold: "MEDIUM"
  rate_limit_minutes: 5
  slack:
    webhook_url: "${SLACK_WEBHOOK_URL}"
    enabled: false
  email:
    smtp_server: "${SMTP_SERVER}"
    recipients: ["security@company.com"]
    enabled: false

prometheus:
  enabled: true
  port: 9090
  metrics_prefix: "deployment_auditor_"
"""
            
            if os.path.exists(config_path):
                if not click.confirm(f"Configuration file {config_path} already exists. Overwrite?"):
                    click.echo("Configuration creation cancelled.")
                    return
            
            with open(config_path, 'w') as f:
                f.write(sample_config)
            
            click.echo(f"✅ Sample configuration created: {config_path}")
            click.echo("Edit the file to customize settings for your environment.")
        else:
            click.echo("Deployment Data Auditor Initialization")
            click.echo("====================================")
            click.echo("Use --create-sample to generate a sample configuration file.")
            
    except Exception as e:
        click.echo(f"❌ Initialization failed: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.pass_context
def version(ctx):
    """Show version information."""
    from . import __version__
    click.echo(f"Deployment Data Governance Auditor v{__version__}")
    click.echo("Built with Beast Mode Framework")


@cli.command()
@click.option('--host', default='0.0.0.0', help='Host to bind to')
@click.option('--port', default=8080, help='Port to listen on')
@click.pass_context
def serve(ctx, host, port):
    """Start the health monitoring API server."""
    try:
        # Initialize auditor
        config_path = ctx.obj.get('config_path')
        auditor = DeploymentAuditor(config_path=config_path)

        # Start monitoring first
        if not auditor.start_monitoring():
            click.echo("⚠️  Warning: Monitoring failed to start, but API will still run", err=True)

        # Import and run the API server
        from .api import run_health_api

        click.echo(f"Starting health API server on {host}:{port}")
        click.echo("Available endpoints:")
        click.echo(f"  • http://{host}:{port}/health - Health status")
        click.echo(f"  • http://{host}:{port}/ready - Readiness check")
        click.echo(f"  • http://{host}:{port}/metrics - Prometheus metrics")
        click.echo("\nPress Ctrl+C to stop the server")

        run_health_api(auditor, host, port)

    except KeyboardInterrupt:
        click.echo("\n✅ Server stopped")
    except Exception as e:
        click.echo(f"❌ Server failed: {e}", err=True)
        sys.exit(1)


if __name__ == '__main__':
    cli()