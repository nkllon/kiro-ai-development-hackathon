#!/usr/bin/env python3
"""
Execution Tracker CLI
====================
Command-line interface for monitoring specification executions.

Author: Beast Mode Framework
Date: 2025-10-01
Purpose: Monitor launched specifications and their status
"""

import asyncio
import sys
import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Optional
import argparse

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

try:
    from src.execution_tracking.redis_execution_tracker import (
        RedisExecutionTracker, ExecutionStatus, ExecutionRecord, CheckinRecord
    )
    TRACKER_AVAILABLE = True
except ImportError as e:
    print(f"❌ Execution tracker not available: {e}")
    TRACKER_AVAILABLE = False
    sys.exit(1)


class ExecutionTrackerCLI:
    """CLI for execution tracking system."""
    
    def __init__(self):
        self.tracker = RedisExecutionTracker()
    
    async def initialize(self) -> bool:
        """Initialize the tracker."""
        return await self.tracker.initialize()
    
    async def list_active(self) -> None:
        """List all active executions."""
        print("🔍 Active Executions")
        print("=" * 60)
        
        active_executions = await self.tracker.get_active_executions()
        
        if not active_executions:
            print("No active executions found.")
            return
        
        for execution in active_executions:
            self._print_execution_summary(execution)
            print("-" * 60)
    
    async def list_history(self, spec_name: Optional[str] = None, limit: int = 10) -> None:
        """List execution history."""
        print(f"📋 Execution History{f' for {spec_name}' if spec_name else ''}")
        print("=" * 60)
        
        history = await self.tracker.get_execution_history(spec_name, limit)
        
        if not history:
            print("No execution history found.")
            return
        
        for execution in history:
            self._print_execution_summary(execution)
            print("-" * 60)
    
    async def show_execution(self, execution_id: str) -> None:
        """Show detailed execution information."""
        print(f"🔍 Execution Details: {execution_id}")
        print("=" * 80)
        
        execution = await self.tracker.get_execution_record(execution_id)
        if not execution:
            print(f"❌ Execution not found: {execution_id}")
            return
        
        self._print_execution_details(execution)
        
        # Show check-in history
        print("\n📊 Check-in History:")
        print("-" * 40)
        
        checkins = await self.tracker.get_execution_checkins(execution_id)
        if checkins:
            for checkin in checkins[-10:]:  # Show last 10 check-ins
                self._print_checkin(checkin)
        else:
            print("No check-ins recorded.")
    
    async def detect_stuck(self, timeout_minutes: int = 60) -> None:
        """Detect stuck executions."""
        print(f"🚨 Detecting Stuck Executions (timeout: {timeout_minutes} minutes)")
        print("=" * 70)
        
        stuck_executions = await self.tracker.detect_stuck_executions(timeout_minutes)
        
        if not stuck_executions:
            print("✅ No stuck executions detected.")
            return
        
        print(f"❌ Found {len(stuck_executions)} stuck execution(s):")
        for execution in stuck_executions:
            self._print_execution_summary(execution)
            print("-" * 60)
    
    async def cleanup_old(self, days: int = 30) -> None:
        """Clean up old execution records."""
        print(f"🧹 Cleaning up execution records older than {days} days")
        print("=" * 60)
        
        cleaned_count = await self.tracker.cleanup_old_records(days)
        print(f"✅ Cleaned up {cleaned_count} old execution records.")
    
    async def status_dashboard(self) -> None:
        """Show execution status dashboard."""
        print("📊 Execution Status Dashboard")
        print("=" * 50)
        
        # Get active executions
        active_executions = await self.tracker.get_active_executions()
        
        # Get recent history
        recent_history = await self.tracker.get_execution_history(limit=20)
        
        # Calculate statistics
        status_counts = {}
        spec_counts = {}
        
        for execution in recent_history:
            status_counts[execution.status.value] = status_counts.get(execution.status.value, 0) + 1
            spec_counts[execution.spec_name] = spec_counts.get(execution.spec_name, 0) + 1
        
        print(f"🔄 Active Executions: {len(active_executions)}")
        print(f"📈 Recent Executions (last 20): {len(recent_history)}")
        
        print("\n📊 Status Distribution:")
        for status, count in sorted(status_counts.items()):
            print(f"  {status}: {count}")
        
        print("\n📋 Specification Distribution:")
        for spec, count in sorted(spec_counts.items()):
            print(f"  {spec}: {count}")
        
        if active_executions:
            print("\n🔄 Currently Active:")
            for execution in active_executions:
                duration = datetime.now() - execution.started_at
                print(f"  {execution.spec_name} ({execution.execution_id})")
                print(f"    Status: {execution.status.value}")
                print(f"    Duration: {self._format_duration(duration)}")
                print(f"    Last Check-in: {self._format_time_ago(execution.last_checkin)}")
    
    def _print_execution_summary(self, execution: ExecutionRecord) -> None:
        """Print execution summary."""
        duration = (execution.completed_at or datetime.now()) - execution.started_at
        status_emoji = {
            ExecutionStatus.PENDING: "⏳",
            ExecutionStatus.RUNNING: "🔄",
            ExecutionStatus.COMPLETED: "✅",
            ExecutionStatus.FAILED: "❌",
            ExecutionStatus.CANCELLED: "🚫",
            ExecutionStatus.STUCK: "🚨",
            ExecutionStatus.UNKNOWN: "❓"
        }
        
        print(f"{status_emoji.get(execution.status, '❓')} {execution.spec_name}")
        print(f"   ID: {execution.execution_id}")
        print(f"   Status: {execution.status.value}")
        print(f"   Started: {execution.started_at.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"   Duration: {self._format_duration(duration)}")
        print(f"   Last Check-in: {self._format_time_ago(execution.last_checkin)}")
        
        if execution.efficiency_gain:
            print(f"   Efficiency Gain: {execution.efficiency_gain:.1f}%")
        
        if execution.total_tasks:
            completed = execution.completed_tasks or 0
            print(f"   Progress: {completed}/{execution.total_tasks} tasks")
        
        if execution.error_message:
            print(f"   Error: {execution.error_message}")
    
    def _print_execution_details(self, execution: ExecutionRecord) -> None:
        """Print detailed execution information."""
        print(f"Execution ID: {execution.execution_id}")
        print(f"Specification: {execution.spec_name}")
        print(f"Status: {execution.status.value}")
        print(f"Workflow Version: {execution.workflow_version}")
        print(f"Started: {execution.started_at.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Last Check-in: {execution.last_checkin.strftime('%Y-%m-%d %H:%M:%S')}")
        
        if execution.completed_at:
            print(f"Completed: {execution.completed_at.strftime('%Y-%m-%d %H:%M:%S')}")
            duration = execution.completed_at - execution.started_at
        else:
            duration = datetime.now() - execution.started_at
        
        print(f"Duration: {self._format_duration(duration)}")
        
        if execution.pid:
            print(f"Process ID: {execution.pid}")
        
        if execution.log_file:
            print(f"Log File: {execution.log_file}")
        
        if execution.progress_file:
            print(f"Progress File: {execution.progress_file}")
        
        if execution.efficiency_gain:
            print(f"Efficiency Gain: {execution.efficiency_gain:.1f}%")
        
        if execution.total_tasks:
            completed = execution.completed_tasks or 0
            progress = (completed / execution.total_tasks) * 100
            print(f"Task Progress: {completed}/{execution.total_tasks} ({progress:.1f}%)")
        
        if execution.error_message:
            print(f"Error Message: {execution.error_message}")
        
        if execution.metadata:
            print(f"Metadata: {json.dumps(execution.metadata, indent=2)}")
    
    def _print_checkin(self, checkin: CheckinRecord) -> None:
        """Print check-in information."""
        print(f"  {checkin.timestamp.strftime('%H:%M:%S')} - {checkin.status.value}")
        
        if checkin.phase:
            print(f"    Phase: {checkin.phase}")
        
        if checkin.progress_percentage is not None:
            print(f"    Progress: {checkin.progress_percentage:.1f}%")
        
        if checkin.message:
            print(f"    Message: {checkin.message}")
        
        if checkin.resource_usage:
            print(f"    Resources: {checkin.resource_usage}")
    
    def _format_duration(self, duration: timedelta) -> str:
        """Format duration for display."""
        total_seconds = int(duration.total_seconds())
        hours, remainder = divmod(total_seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        
        if hours > 0:
            return f"{hours}h {minutes}m {seconds}s"
        elif minutes > 0:
            return f"{minutes}m {seconds}s"
        else:
            return f"{seconds}s"
    
    def _format_time_ago(self, timestamp: datetime) -> str:
        """Format time ago for display."""
        now = datetime.now()
        diff = now - timestamp
        
        if diff.days > 0:
            return f"{diff.days} day(s) ago"
        elif diff.seconds > 3600:
            hours = diff.seconds // 3600
            return f"{hours} hour(s) ago"
        elif diff.seconds > 60:
            minutes = diff.seconds // 60
            return f"{minutes} minute(s) ago"
        else:
            return f"{diff.seconds} second(s) ago"


async def main():
    """Main CLI function."""
    parser = argparse.ArgumentParser(description="Execution Tracker CLI")
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # List active executions
    subparsers.add_parser('active', help='List active executions')
    
    # List execution history
    history_parser = subparsers.add_parser('history', help='List execution history')
    history_parser.add_argument('--spec', help='Filter by specification name')
    history_parser.add_argument('--limit', type=int, default=10, help='Limit number of results')
    
    # Show execution details
    show_parser = subparsers.add_parser('show', help='Show execution details')
    show_parser.add_argument('execution_id', help='Execution ID to show')
    
    # Detect stuck executions
    stuck_parser = subparsers.add_parser('stuck', help='Detect stuck executions')
    stuck_parser.add_argument('--timeout', type=int, default=60, help='Timeout in minutes')
    
    # Cleanup old records
    cleanup_parser = subparsers.add_parser('cleanup', help='Clean up old execution records')
    cleanup_parser.add_argument('--days', type=int, default=30, help='Days to keep')
    
    # Status dashboard
    subparsers.add_parser('dashboard', help='Show execution status dashboard')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    cli = ExecutionTrackerCLI()
    
    # Initialize tracker
    if not await cli.initialize():
        print("❌ Failed to initialize execution tracker")
        sys.exit(1)
    
    try:
        if args.command == 'active':
            await cli.list_active()
        elif args.command == 'history':
            await cli.list_history(args.spec, args.limit)
        elif args.command == 'show':
            await cli.show_execution(args.execution_id)
        elif args.command == 'stuck':
            await cli.detect_stuck(args.timeout)
        elif args.command == 'cleanup':
            await cli.cleanup_old(args.days)
        elif args.command == 'dashboard':
            await cli.status_dashboard()
    
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())