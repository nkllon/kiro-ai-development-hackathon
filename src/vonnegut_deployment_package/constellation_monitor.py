#!/usr/bin/env python3
"""
Real-time Progress Monitor for Constellation Execution

Displays a live dashboard showing execution progress, running tasks,
and estimated completion time.

Usage:
    python scripts/constellation_monitor.py
    python scripts/constellation_monitor.py --refresh 5
    python scripts/constellation_monitor.py --status .kiro/execution-status.json
"""

import json
import time
import sys
import argparse
from pathlib import Path
from datetime import datetime, timedelta


def clear_screen():
    """Clear terminal screen"""
    print("\033[2J\033[H", end="")


def format_duration(seconds):
    """Format duration in human-readable format"""
    if seconds is None:
        return "N/A"
    return str(timedelta(seconds=int(seconds)))


def get_status_emoji(status):
    """Get emoji for status"""
    return {
        "pending": "⏳",
        "running": "🔄",
        "completed": "✅",
        "failed": "❌",
    }.get(status, "❓")


def draw_progress_bar(progress, width=50):
    """Draw a progress bar"""
    filled = int(width * progress / 100)
    bar = "█" * filled + "░" * (width - filled)
    return f"[{bar}] {progress:.1f}%"


def monitor_execution(status_file: str, refresh_interval: int = 2):
    """Monitor execution with live dashboard"""
    status_path = Path(status_file)

    if not status_path.exists():
        print(f"❌ Status file not found: {status_file}")
        print("\n🚀 Start execution first with:")
        print("   python scripts/constellation_orchestrator.py")
        return

    print("📊 Starting monitor... (Press Ctrl+C to exit)\n")
    time.sleep(1)

    try:
        while True:
            clear_screen()

            # Load current status
            try:
                with open(status_path) as f:
                    status = json.load(f)
            except json.JSONDecodeError:
                print("⚠️  Error reading status file, retrying...")
                time.sleep(refresh_interval)
                continue

            # Header
            print("=" * 100)
            print("CONSTELLATION ELABORATION - EXECUTION DASHBOARD")
            print("=" * 100)
            print(f"🆔 Execution ID: {status['execution_id']}")
            print(
                f"📊 Status: {status.get('status', 'unknown').upper()} | Agents: {status.get('max_agents', 'N/A')}"
            )
            print(f"🕐 Started: {status.get('started_at', 'N/A')}")

            # Calculate stats
            prompts = status["prompts"]
            total = len(prompts)
            pending = sum(1 for p in prompts.values() if p["status"] == "pending")
            running = sum(1 for p in prompts.values() if p["status"] == "running")
            completed = sum(1 for p in prompts.values() if p["status"] == "completed")
            failed = sum(1 for p in prompts.values() if p["status"] == "failed")

            progress = (completed + failed) / total * 100 if total > 0 else 0

            # Progress bar
            print("\n" + "=" * 100)
            print(f"Progress: {draw_progress_bar(progress)}")
            print(
                f"Total: {total} | ⏳ Pending: {pending} | 🔄 Running: {running} | ✅ Completed: {completed} | ❌ Failed: {failed}"
            )
            print("=" * 100)

            # Currently running prompts
            if running > 0:
                print("\n🔄 CURRENTLY RUNNING:")
                running_prompts = [
                    (name, info)
                    for name, info in prompts.items()
                    if info["status"] == "running"
                ]
                running_prompts.sort(key=lambda x: x[1]["started_at"] or "")

                for name, info in running_prompts:
                    if info["started_at"]:
                        started = datetime.fromisoformat(info["started_at"])
                        elapsed = (datetime.now() - started).total_seconds() / 60
                        est = info.get("estimated_min", "?")
                        progress_pct = (
                            min(elapsed / est * 100, 99) if est != "?" else 0
                        )
                        bar = draw_progress_bar(progress_pct, width=20)
                        print(
                            f"  [{info['agent_id']}] {name[:50]:50s} {bar} {elapsed:.0f}/{est} min"
                        )

            # Recently completed
            recently_completed = [
                (name, info)
                for name, info in prompts.items()
                if info["status"] == "completed" and info["completed_at"]
            ]
            recently_completed.sort(key=lambda x: x[1]["completed_at"], reverse=True)

            if recently_completed:
                print("\n✅ RECENTLY COMPLETED (last 5):")
                for name, info in recently_completed[:5]:
                    est = info.get("estimated_min", "?")
                    actual = info.get("duration_min", "?")
                    variance = ""
                    if est != "?" and actual != "?":
                        pct = ((actual - est) / est) * 100
                        if abs(pct) < 10:
                            variance = "≈"
                        elif pct > 0:
                            variance = f"+{pct:.0f}%"
                        else:
                            variance = f"{pct:.0f}%"
                    print(
                        f"  [{info['agent_id']}] {name[:50]:50s} {actual:.1f} min {variance}"
                    )

            # Failed prompts
            if failed > 0:
                print("\n❌ FAILED:")
                failed_prompts = [
                    (name, info)
                    for name, info in prompts.items()
                    if info["status"] == "failed"
                ]
                for name, info in failed_prompts:
                    error = info.get("error", "Unknown error")[:60]
                    print(f"  {name[:50]:50s} {error}")

            # Next up
            ready = []
            for name, info in prompts.items():
                if info["status"] == "pending":
                    deps_satisfied = all(
                        prompts.get(dep, {}).get("status") == "completed"
                        for dep in info["dependencies"]
                    )
                    if deps_satisfied:
                        ready.append((name, info))

            max_agents = status.get("max_agents", 10)
            if ready and running < max_agents:
                slots_available = max_agents - running
                print(f"\n⏳ READY TO START (next {min(5, len(ready))}):")
                ready.sort(key=lambda x: x[1].get("estimated_min", 999))
                for name, info in ready[:5]:
                    est = info.get("estimated_min", "?")
                    print(f"  {name[:50]:50s} est. {est} min")

            # ETA calculation
            if completed > 0 and running > 0:
                # Calculate average duration for completed prompts
                completed_prompts = [
                    p for p in prompts.values() if p["duration_min"] is not None
                ]
                if completed_prompts:
                    avg_duration = sum(p["duration_min"] for p in completed_prompts) / len(
                        completed_prompts
                    )

                    # Estimate remaining time
                    # For running prompts, estimate time left based on average
                    running_time_left = (
                        sum(
                            max(0, info.get("estimated_min", avg_duration) - (
                                (datetime.now() - datetime.fromisoformat(info["started_at"])).total_seconds() / 60
                                if info.get("started_at") else 0
                            ))
                            for info in prompts.values()
                            if info["status"] == "running"
                        )
                        / max(running, 1)
                    )

                    # For pending prompts, use average duration
                    pending_time = (pending * avg_duration) / max_agents

                    eta_min = running_time_left + pending_time
                    eta = datetime.now() + timedelta(minutes=eta_min)

                    print(
                        f"\n⏰ ESTIMATED COMPLETION: {eta.strftime('%Y-%m-%d %H:%M:%S')} ({eta_min:.0f} min remaining)"
                    )

            # Phase summary
            phase_stats = {}
            for name, info in prompts.items():
                phase = name.split("-")[1]  # Extract phase number
                if phase not in phase_stats:
                    phase_stats[phase] = {"total": 0, "completed": 0}
                phase_stats[phase]["total"] += 1
                if info["status"] == "completed":
                    phase_stats[phase]["completed"] += 1

            if phase_stats:
                print("\n📈 PHASE PROGRESS:")
                for phase in sorted(phase_stats.keys()):
                    stats = phase_stats[phase]
                    pct = stats["completed"] / stats["total"] * 100
                    print(f"  Phase {phase}: {draw_progress_bar(pct, width=30)} {stats['completed']}/{stats['total']}")

            print("\n" + "=" * 100)
            print(f"Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | Refresh: {refresh_interval}s")
            print("Press Ctrl+C to exit")

            # Check if execution is complete
            if status.get("status") == "completed":
                print("\n✅ EXECUTION COMPLETE!")
                print(f"\n📊 View full results in: {status_file}")
                break

            time.sleep(refresh_interval)

    except KeyboardInterrupt:
        print("\n\n⚠️  Monitoring stopped.")
        sys.exit(0)


def main():
    parser = argparse.ArgumentParser(description="Monitor constellation execution progress")
    parser.add_argument(
        "--status",
        default=".kiro/execution-status.json",
        help="Status file path (default: .kiro/execution-status.json)",
    )
    parser.add_argument(
        "--refresh",
        type=int,
        default=2,
        help="Refresh interval in seconds (default: 2)",
    )

    args = parser.parse_args()

    monitor_execution(args.status, args.refresh)


if __name__ == "__main__":
    main()
