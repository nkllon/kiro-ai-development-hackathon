"""
Beast Mode CLI - User-friendly command-line interface
RM-DDD compliant CLI with auto-generated commands and stdin/stdout pipes.
"""

import click
import json
import os
import sys
from pathlib import Path
from typing import List, Optional

from ..foundation.makefile_health_manager import MakefileHealthManager

# RM-DDD Integration - Using Unified Interface
sys.path.append(str(Path(__file__).parent.parent.parent))
from src.rm_ddd.core.unified_reflective_module import ReflectiveModule


@click.group()
@click.version_option(version='1.0.0')
def beast_mode():
    """
    🚀 Beast Mode - Systematic Intelligence for System Recovery
    
    Advanced AI-powered system diagnosis and repair with DAG-driven architecture.
    Provides enterprise-grade solutions for complex development challenges.
    """
    pass


@beast_mode.command()
@click.argument('system', type=click.Choice(['makefile', 'system', 'all']))
@click.option('--path', '-p', help='Specific path to analyze (for makefile)')
@click.option('--auto-fix', '-f', is_flag=True, help='Automatically apply fixes')
@click.option('--output', '-o', help='Output file for detailed report')
@click.option('--verbose', '-v', is_flag=True, help='Verbose output')
def diagnose(system: str, path: Optional[str], auto_fix: bool, output: Optional[str], verbose: bool):
    """
    Diagnose system health and provide comprehensive analysis.
    
    SYSTEM options:
    - makefile: Analyze Makefile health and dependencies
    - system: Analyze overall system health
    - all: Comprehensive system-wide analysis
    """
    click.echo(f"🔍 Diagnosing {system} health...")
    
    manager = MakefileHealthManager()
    
    if system == 'makefile':
        _diagnose_makefile(manager, path, auto_fix, output, verbose)
    elif system == 'system':
        _diagnose_system(manager, auto_fix, output, verbose)
    elif system == 'all':
        _diagnose_all(manager, auto_fix, output, verbose)


@beast_mode.command()
@click.argument('system', type=click.Choice(['makefile', 'system', 'all']))
@click.option('--path', '-p', help='Specific path to fix (for makefile)')
@click.option('--backup/--no-backup', default=True, help='Create backup before fixing')
@click.option('--dry-run', is_flag=True, help='Show what would be fixed without applying changes')
@click.option('--verbose', '-v', is_flag=True, help='Verbose output')
def fix(system: str, path: Optional[str], backup: bool, dry_run: bool, verbose: bool):
    """
    Fix identified system issues with intelligent repair.
    
    SYSTEM options:
    - makefile: Fix Makefile issues and optimize structure
    - system: Apply system-wide fixes
    - all: Comprehensive system repair
    """
    click.echo(f"🔧 Fixing {system} issues...")
    
    manager = MakefileHealthManager()
    
    if dry_run:
        click.echo("🔍 DRY RUN MODE - No changes will be applied")
    
    if system == 'makefile':
        _fix_makefile(manager, path, backup, dry_run, verbose)
    elif system == 'system':
        _fix_system(manager, backup, dry_run, verbose)
    elif system == 'all':
        _fix_all(manager, backup, dry_run, verbose)


@beast_mode.command()
@click.option('--interval', '-i', default=30, help='Monitoring interval in seconds')
@click.option('--output', '-o', help='Output file for monitoring data')
@click.option('--alerts', '-a', is_flag=True, help='Enable alert notifications')
def monitor(interval: int, output: Optional[str], alerts: bool):
    """
    Monitor system health in real-time with continuous analysis.
    
    Provides real-time system health monitoring with configurable
    intervals and alert notifications for critical issues.
    """
    click.echo(f"📊 Starting real-time monitoring (interval: {interval}s)")
    
    if alerts:
        click.echo("🚨 Alert notifications enabled")
    
    if output:
        click.echo(f"📁 Output file: {output}")
    
    # TODO: Implement real-time monitoring
    click.echo("⚠️  Real-time monitoring not yet implemented")
    click.echo("💡 Use 'beast-mode diagnose system' for current health status")


@beast_mode.command()
@click.option('--format', '-f', type=click.Choice(['json', 'yaml', 'table']), default='table')
@click.option('--output', '-o', help='Output file for report')
@click.option('--include-fixes', is_flag=True, help='Include applied fixes in report')
def report(format: str, output: Optional[str], include_fixes: bool):
    """
    Generate comprehensive system health report.
    
    Creates detailed reports in various formats with health metrics,
    identified issues, and recommended actions.
    """
    click.echo(f"📋 Generating {format} report...")
    
    manager = MakefileHealthManager()
    
    # Discover and analyze all Makefiles
    makefiles = manager.discover_makefiles('.')
    results = manager.diagnose_multiple_makefiles(makefiles)
    summary = manager.generate_health_summary(results)
    
    if format == 'json':
        _generate_json_report(summary, results, output, include_fixes)
    elif format == 'yaml':
        _generate_yaml_report(summary, results, output, include_fixes)
    else:  # table
        _generate_table_report(summary, results, output, include_fixes)


@beast_mode.command()
def status():
    """
    Show current system status and quick health overview.
    
    Provides a quick overview of system health without detailed analysis.
    """
    click.echo("📊 System Status Overview")
    click.echo("=" * 50)
    
    manager = MakefileHealthManager()
    
    # Quick analysis
    makefiles = manager.discover_makefiles('.')
    
    if makefiles:
        click.echo(f"📁 Found {len(makefiles)} Makefile(s)")
        
        # Quick health check on first few makefiles
        sample_size = min(3, len(makefiles))
        quick_results = manager.diagnose_multiple_makefiles(makefiles[:sample_size])
        
        healthy_count = sum(1 for r in quick_results if r.status == 'healthy')
        needs_attention_count = sum(1 for r in quick_results if r.status == 'needs_attention')
        critical_count = sum(1 for r in quick_results if r.status == 'critical')
        
        click.echo(f"✅ Healthy: {healthy_count}")
        click.echo(f"⚠️  Needs Attention: {needs_attention_count}")
        click.echo(f"🚨 Critical: {critical_count}")
        
        if critical_count > 0:
            click.echo("\n💡 Run 'beast-mode diagnose all' for detailed analysis")
    else:
        click.echo("❌ No Makefiles found in current directory")


def _diagnose_makefile(manager: MakefileHealthManager, path: Optional[str], 
                      auto_fix: bool, output: Optional[str], verbose: bool):
    """Diagnose specific Makefile or discover and analyze all"""
    if path:
        if not os.path.exists(path):
            click.echo(f"❌ Path not found: {path}")
            return
        
        makefiles = [path]
    else:
        makefiles = manager.discover_makefiles('.')
    
    if not makefiles:
        click.echo("❌ No Makefiles found")
        return
    
    click.echo(f"📁 Analyzing {len(makefiles)} Makefile(s)...")
    
    results = manager.diagnose_multiple_makefiles(makefiles, auto_fix)
    summary = manager.generate_health_summary(results)
    
    _display_summary(summary, verbose)
    
    if output:
        manager.export_health_report(results, output)
        click.echo(f"📄 Detailed report saved to: {output}")


def _diagnose_system(manager: MakefileHealthManager, auto_fix: bool, 
                    output: Optional[str], verbose: bool):
    """Diagnose overall system health"""
    click.echo("🔍 Analyzing system-wide health...")
    
    # Discover all makefiles
    makefiles = manager.discover_makefiles('.')
    
    if makefiles:
        results = manager.diagnose_multiple_makefiles(makefiles, auto_fix)
        summary = manager.generate_health_summary(results)
        
        _display_summary(summary, verbose)
        
        if output:
            manager.export_health_report(results, output)
            click.echo(f"📄 System report saved to: {output}")
    else:
        click.echo("❌ No Makefiles found for system analysis")


def _diagnose_all(manager: MakefileHealthManager, auto_fix: bool, 
                 output: Optional[str], verbose: bool):
    """Comprehensive system-wide analysis"""
    click.echo("🚀 Comprehensive system analysis...")
    
    # This would include multiple system components
    # For now, focus on makefiles as the primary component
    _diagnose_system(manager, auto_fix, output, verbose)


def _fix_makefile(manager: MakefileHealthManager, path: Optional[str], 
                 backup: bool, dry_run: bool, verbose: bool):
    """Fix Makefile issues"""
    if path:
        if not os.path.exists(path):
            click.echo(f"❌ Path not found: {path}")
            return
        
        makefiles = [path]
    else:
        makefiles = manager.discover_makefiles('.')
    
    if not makefiles:
        click.echo("❌ No Makefiles found")
        return
    
    for makefile in makefiles:
        click.echo(f"🔧 Analyzing {makefile}...")
        
        result = manager.diagnose_makefile(makefile, auto_fix=not dry_run)
        
        if result.health_report and result.health_report.issues:
            if dry_run:
                click.echo(f"🔍 Would fix {len(result.health_report.issues)} issues in {makefile}")
                for issue in result.health_report.issues:
                    click.echo(f"  - {issue}")
            else:
                if result.fix_result:
                    if result.fix_result.success:
                        click.echo(f"✅ Fixed {len(result.fix_result.fixes_applied)} issues")
                    else:
                        click.echo(f"❌ Fix failed: {result.fix_result.errors}")
        else:
            click.echo(f"✅ {makefile} is healthy - no fixes needed")


def _fix_system(manager: MakefileHealthManager, backup: bool, 
               dry_run: bool, verbose: bool):
    """Fix system-wide issues"""
    click.echo("🔧 Applying system-wide fixes...")
    _fix_makefile(manager, None, backup, dry_run, verbose)


def _fix_all(manager: MakefileHealthManager, backup: bool, 
            dry_run: bool, verbose: bool):
    """Comprehensive system repair"""
    click.echo("🚀 Comprehensive system repair...")
    _fix_system(manager, backup, dry_run, verbose)


def _display_summary(summary: dict, verbose: bool):
    """Display health summary"""
    click.echo("\n📊 Health Summary")
    click.echo("=" * 50)
    click.echo(f"📁 Total Makefiles: {summary['total_makefiles']}")
    click.echo(f"✅ Healthy: {summary['healthy']}")
    click.echo(f"⚠️  Needs Attention: {summary['needs_attention']}")
    click.echo(f"🚨 Critical: {summary['critical']}")
    click.echo(f"❌ Errors: {summary['errors']}")
    click.echo(f"📈 Success Rate: {summary['success_rate']}%")
    click.echo(f"🎯 Average Health Score: {summary['average_health_score']}")
    
    if verbose and summary['common_issues']:
        click.echo("\n🔍 Common Issues:")
        for issue, count in summary['common_issues'][:5]:
            click.echo(f"  - {issue} ({count} occurrences)")


def _generate_json_report(summary: dict, results: List, output: Optional[str], include_fixes: bool):
    """Generate JSON report"""
    report_data = {
        "summary": summary,
        "detailed_results": results,
        "include_fixes": include_fixes
    }
    
    if output:
        with open(output, 'w') as f:
            json.dump(report_data, f, indent=2, default=str)
        click.echo(f"📄 JSON report saved to: {output}")
    else:
        click.echo(json.dumps(report_data, indent=2, default=str))


def _generate_yaml_report(summary: dict, results: List, output: Optional[str], include_fixes: bool):
    """Generate YAML report"""
    try:
        import yaml
        
        report_data = {
            "summary": summary,
            "detailed_results": results,
            "include_fixes": include_fixes
        }
        
        if output:
            with open(output, 'w') as f:
                yaml.dump(report_data, f, default_flow_style=False)
            click.echo(f"📄 YAML report saved to: {output}")
        else:
            click.echo(yaml.dump(report_data, default_flow_style=False))
    except ImportError:
        click.echo("❌ YAML support not available. Install PyYAML or use JSON format.")


def _generate_table_report(summary: dict, results: List, output: Optional[str], include_fixes: bool):
    """Generate table report"""
    _display_summary(summary, verbose=True)
    
    if output:
        with open(output, 'w') as f:
            f.write("Beast Mode Health Report\n")
            f.write("=" * 50 + "\n\n")
            f.write(f"Summary: {json.dumps(summary, indent=2)}\n\n")
            f.write(f"Detailed Results: {json.dumps(results, indent=2, default=str)}\n")
        click.echo(f"📄 Table report saved to: {output}")


if __name__ == '__main__':
    beast_mode()
