#!/usr/bin/env python3
"""
Devpost Integration CLI

The Requirements ARE the Solution - Command Line Interface
"""

import click
import sys
from pathlib import Path
from typing import Optional

from .project_manager import DevpostProjectManager
from .sync_manager import DevpostSyncManager
from .preview_generator import DevpostPreviewGenerator
from .models import DevpostConfig


@click.group()
@click.version_option()
def cli():
    """
    Devpost Integration CLI - Where Requirements ARE the Solution
    
    Systematic project management for hackathon submissions.
    No ad-hoc approaches, no surprises, just systematic success.
    """
    pass


@cli.command()
@click.option('--project-id', required=True, help='Devpost project ID')
@click.option('--local-path', default='.', help='Local project directory')
@click.option('--config-file', help='Custom configuration file path')
def connect(project_id: str, local_path: str, config_file: Optional[str]):
    """Connect local project to Devpost submission."""
    try:
        click.echo("🔗 Connecting to Devpost project...")
        
        manager = DevpostProjectManager()
        success = manager.connect_project(
            project_id=project_id,
            local_path=Path(local_path),
            config_file=config_file
        )
        
        if success:
            click.echo(f"✅ Successfully connected to project {project_id}")
            click.echo(f"📁 Local path: {local_path}")
            click.echo("\n💡 Next steps:")
            click.echo("  • Run 'devpost status' to check project status")
            click.echo("  • Run 'devpost sync' to synchronize with Devpost")
            click.echo("  • Run 'devpost preview' to generate local preview")
        else:
            click.echo("❌ Failed to connect project", err=True)
            sys.exit(1)
            
    except Exception as e:
        click.echo(f"❌ Connection failed: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.option('--force', is_flag=True, help='Force sync even if no changes detected')
@click.option('--dry-run', is_flag=True, help='Show what would be synced without making changes')
def sync(force: bool, dry_run: bool):
    """Synchronize local project with Devpost submission."""
    try:
        click.echo("🔄 Synchronizing with Devpost...")
        
        sync_manager = DevpostSyncManager()
        
        if dry_run:
            changes = sync_manager.get_pending_changes()
            if changes:
                click.echo("📋 Changes that would be synced:")
                for change in changes:
                    click.echo(f"  • {change}")
            else:
                click.echo("✨ No changes to sync")
            return
        
        result = sync_manager.sync_project(force=force)
        
        if result.success:
            click.echo(f"✅ Sync completed successfully")
            if result.changes_made:
                click.echo(f"📝 {len(result.changes_made)} changes synchronized")
            else:
                click.echo("✨ Project already up to date")
        else:
            click.echo(f"❌ Sync failed: {result.error}", err=True)
            sys.exit(1)
            
    except Exception as e:
        click.echo(f"❌ Sync failed: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.option('--verbose', is_flag=True, help='Show detailed status information')
def status(verbose: bool):
    """Show project connection and sync status."""
    try:
        manager = DevpostProjectManager()
        project_status = manager.get_project_status()
        
        if not project_status.connected:
            click.echo("❌ No project connected")
            click.echo("💡 Run 'devpost connect' to connect a project")
            return
        
        click.echo(f"🎯 Project: {project_status.project_name}")
        click.echo(f"🔗 Devpost ID: {project_status.project_id}")
        click.echo(f"📁 Local path: {project_status.local_path}")
        
        # Sync status
        if project_status.last_sync:
            click.echo(f"🔄 Last sync: {project_status.last_sync}")
        else:
            click.echo("🔄 Never synced")
        
        if project_status.pending_changes:
            click.echo(f"⚠️  {len(project_status.pending_changes)} pending changes")
            if verbose:
                for change in project_status.pending_changes:
                    click.echo(f"  • {change}")
        else:
            click.echo("✅ Up to date")
        
        # Requirements validation
        if project_status.validation_errors:
            click.echo(f"❌ {len(project_status.validation_errors)} validation errors")
            if verbose:
                for error in project_status.validation_errors:
                    click.echo(f"  • {error}")
        else:
            click.echo("✅ All requirements met")
            
    except Exception as e:
        click.echo(f"❌ Status check failed: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.option('--output', default='preview.html', help='Output file for preview')
@click.option('--open-browser', is_flag=True, help='Open preview in browser')
def preview(output: str, open_browser: bool):
    """Generate local preview of Devpost submission."""
    try:
        click.echo("🎨 Generating Devpost preview...")
        
        generator = DevpostPreviewGenerator()
        preview_path = generator.generate_preview(output_file=output)
        
        click.echo(f"✅ Preview generated: {preview_path}")
        
        if open_browser:
            import webbrowser
            webbrowser.open(f"file://{preview_path.absolute()}")
            click.echo("🌐 Opened in browser")
        
        click.echo("\n💡 Preview includes:")
        click.echo("  • Project description and media")
        click.echo("  • Team information")
        click.echo("  • Technical details")
        click.echo("  • Submission requirements validation")
        
    except Exception as e:
        click.echo(f"❌ Preview generation failed: {e}", err=True)
        sys.exit(1)


if __name__ == '__main__':
    cli()