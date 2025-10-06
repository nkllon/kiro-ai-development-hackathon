#!/usr/bin/env python3
"""
Analyze and Cleanup Disk Space
==============================

Comprehensive disk space analysis and cleanup for the workspace.
Identifies what's consuming disk space and provides safe cleanup options.

Author: Beast Mode Framework
Date: 2025-01-27
"""

import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.dag_orchestration.infrastructure.disk_space_manager import (
    DiskSpaceManager,
    analyze_workspace_disk_usage,
    execute_safe_workspace_cleanup
)


def main():
    """Analyze disk usage and perform safe cleanup."""
    
    print("💾 Workspace Disk Space Analysis and Cleanup")
    print("=" * 60)
    
    try:
        # Create disk space manager
        manager = DiskSpaceManager()
        
        # Show manager info
        module_info = manager.get_module_info()
        print(f"📊 Manager: {module_info['name']} v{module_info['version']}")
        print(f"📁 Workspace: {module_info['workspace_root']}")
        print(f"⚠️  Warning Threshold: {module_info['thresholds']['warning_percent']}%")
        print(f"🚨 Critical Threshold: {module_info['thresholds']['critical_percent']}%")
        
        # Check manager health
        health = manager.get_health_status()
        print(f"\n🏥 Manager Health: {health.status.value} (Score: {health.health_score})")
        if health.issues:
            for issue in health.issues:
                print(f"   ⚠️  {issue}")
        
        # Perform disk usage analysis
        print(f"\n🔍 ANALYZING DISK USAGE...")
        print("-" * 40)
        
        report = manager.analyze_disk_usage()
        
        # Display overall disk usage
        print(f"\n💾 OVERALL DISK USAGE")
        print("-" * 25)
        print(f"Total Space: {report.total_space_gb:.1f}GB")
        print(f"Used Space: {report.used_space_gb:.1f}GB")
        print(f"Free Space: {report.free_space_gb:.1f}GB")
        print(f"Usage: {report.usage_percent:.1f}%")
        
        # Status indicators
        if report.critical_threshold_reached:
            print("🚨 CRITICAL: Disk usage above critical threshold!")
        elif report.warning_threshold_reached:
            print("⚠️  WARNING: Disk usage above warning threshold")
        else:
            print("✅ OK: Disk usage within acceptable limits")
        
        # Display large consumers
        print(f"\n📊 LARGEST SPACE CONSUMERS")
        print("-" * 30)
        
        for i, consumer in enumerate(report.large_consumers[:10], 1):
            age_days = (report.generated_at - consumer.last_modified).days
            print(f"{i:2d}. {consumer.path:<25} {consumer.size_human:>8} ({consumer.file_count:,} files, {age_days}d old)")
        
        # Display cleanup recommendations
        print(f"\n🧹 CLEANUP RECOMMENDATIONS")
        print("-" * 30)
        
        if not report.cleanup_recommendations:
            print("No cleanup recommendations available.")
        else:
            total_potential_savings = sum(action.estimated_savings_bytes for action in report.cleanup_recommendations)
            print(f"Total Potential Savings: {manager._format_bytes(total_potential_savings)}")
            print()
            
            for i, action in enumerate(report.cleanup_recommendations, 1):
                risk_icon = {"low": "✅", "medium": "⚠️", "high": "🚨"}.get(action.risk_level, "❓")
                print(f"{i:2d}. {risk_icon} [{action.action_type.upper()}] {action.target_path}")
                print(f"    Savings: {action.estimated_savings_human}")
                print(f"    Risk: {action.risk_level.upper()}")
                print(f"    Description: {action.description}")
                print()
        
        # Offer to perform safe cleanup
        if report.cleanup_recommendations:
            safe_actions = [action for action in report.cleanup_recommendations if action.risk_level == 'low']
            
            if safe_actions:
                print(f"🔧 SAFE CLEANUP AVAILABLE")
                print("-" * 25)
                print(f"Found {len(safe_actions)} safe cleanup actions")
                
                safe_savings = sum(action.estimated_savings_bytes for action in safe_actions)
                print(f"Potential safe savings: {manager._format_bytes(safe_savings)}")
                
                # Perform dry run first
                print(f"\n🧪 PERFORMING DRY RUN...")
                dry_run_results = manager.execute_safe_cleanup(dry_run=True)
                
                print(f"Dry run results:")
                print(f"  Actions to execute: {dry_run_results['actions_executed']}")
                print(f"  Estimated bytes freed: {manager._format_bytes(dry_run_results['bytes_freed'])}")
                
                # Ask user if they want to proceed with actual cleanup
                print(f"\n❓ Would you like to execute safe cleanup? (y/N): ", end="")
                try:
                    response = input().strip().lower()
                    if response in ['y', 'yes']:
                        print(f"\n🧹 EXECUTING SAFE CLEANUP...")
                        cleanup_results = manager.execute_safe_cleanup(dry_run=False)
                        
                        print(f"Cleanup results:")
                        print(f"  Actions executed: {cleanup_results['actions_executed']}")
                        print(f"  Bytes freed: {manager._format_bytes(cleanup_results['bytes_freed'])}")
                        
                        # Show individual action results
                        for action_result in cleanup_results['actions']:
                            if action_result['success']:
                                print(f"  ✅ {action_result['action']}: {action_result['target']}")
                            else:
                                print(f"  ❌ {action_result['action']}: {action_result['target']} - {action_result.get('error', 'Unknown error')}")
                        
                        # Re-analyze after cleanup
                        print(f"\n🔍 RE-ANALYZING AFTER CLEANUP...")
                        new_report = manager.analyze_disk_usage()
                        print(f"New free space: {new_report.free_space_gb:.1f}GB ({new_report.usage_percent:.1f}% used)")
                        
                        freed_space = new_report.free_space_gb - report.free_space_gb
                        print(f"Space freed: {freed_space:.1f}GB")
                        
                    else:
                        print("Cleanup cancelled by user.")
                except KeyboardInterrupt:
                    print("\nCleanup cancelled by user.")
            else:
                print(f"\n⚠️  No safe cleanup actions available.")
                print("Manual intervention may be required for:")
                for action in report.cleanup_recommendations:
                    if action.risk_level != 'low':
                        print(f"  - {action.target_path} ({action.risk_level} risk)")
        
        # Final recommendations
        print(f"\n💡 RECOMMENDATIONS")
        print("-" * 20)
        
        if report.critical_threshold_reached:
            print("🚨 URGENT: Free up disk space immediately!")
            print("   - Consider removing unused virtual environment packages")
            print("   - Clean up large log files")
            print("   - Archive or compress old data")
        elif report.warning_threshold_reached:
            print("⚠️  Monitor disk usage closely")
            print("   - Plan for cleanup in the near future")
            print("   - Consider implementing automated cleanup")
        else:
            print("✅ Disk usage is healthy")
            print("   - Continue monitoring")
            print("   - Consider periodic cleanup maintenance")
        
        # Specific recommendations based on analysis
        venv_consumer = next((c for c in report.large_consumers if '.venv' in c.path), None)
        if venv_consumer and venv_consumer.size_bytes > 500 * 1024 * 1024:  # > 500MB
            print(f"\n🐍 PYTHON VIRTUAL ENVIRONMENT OPTIMIZATION")
            print("   Virtual environment is consuming significant space:")
            print(f"   - Size: {venv_consumer.size_human}")
            print("   - Consider: pip list | grep -E '(torch|tensorflow|scipy)' to identify large packages")
            print("   - Consider: pip uninstall <unused-large-packages>")
            print("   - Consider: pip cache purge")
        
        git_consumer = next((c for c in report.large_consumers if '.git' in c.path), None)
        if git_consumer and git_consumer.size_bytes > 100 * 1024 * 1024:  # > 100MB
            print(f"\n📦 GIT REPOSITORY OPTIMIZATION")
            print("   Git repository is consuming significant space:")
            print(f"   - Size: {git_consumer.size_human}")
            print("   - Consider: git gc --aggressive")
            print("   - Consider: git prune")
            print("   - Consider: git clean -fd")
        
        return True
        
    except Exception as e:
        print(f"\n❌ ANALYSIS FAILED:")
        print(f"Error: {e}")
        print(f"\n💡 Troubleshooting:")
        print("1. Verify disk space manager is working correctly")
        print("2. Check file system permissions")
        print("3. Ensure workspace path is accessible")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)