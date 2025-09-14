#!/usr/bin/env python3
"""
Ghostbusters CLI - Clean interface for multi-agent delusion detection
Suppresses debug output and provides clean, formatted results
"""

import asyncio
import logging
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

# Suppress all debug logging
logging.getLogger().setLevel(logging.WARNING)
for logger_name in ["ghostbusters", "langgraph", "asyncio"]:
    logging.getLogger(logger_name).setLevel(logging.ERROR)

try:
    from ghostbusters import run_ghostbusters
except ImportError:
    # Fallback for when running from different directory
    sys.path.insert(0, "src")
    from ghostbusters import run_ghostbusters


def print_header(title: str):
    """Print a formatted header"""
    print(f"\n{'=' * 60}")
    print(f"👻 {title}")
    print(f"{'=' * 60}")


def print_section(title: str):
    """Print a formatted section"""
    print(f"\n🔒 {title}")
    print("-" * 40)


def print_finding(finding_type: str, description: str, priority: str = "medium"):
    """Print a formatted finding"""
    priority_emoji = {"critical": "🚨", "high": "⚠️", "medium": "🔍", "low": "ℹ️"}
    emoji = priority_emoji.get(priority, "🔍")
    print(f"  {emoji} {finding_type}: {description}")


async def run_ghostbusters_analysis(project_path: str = ".") -> dict:
    """Run Ghostbusters analysis with proper output display"""
    try:
        # Don't suppress output - let us see what's happening
        return await run_ghostbusters(project_path)
    except Exception as e:
        print(f"❌ Ghostbusters analysis failed: {e}")
        return {}


def display_quick_results(result: dict):
    """Display quick results summary"""
    confidence = result.get("confidence_score", "unknown")
    delusions = result.get("delusions_detected", [])
    errors = len(result.get("errors", []))

    # Count total delusions across all agents
    total_delusions = 0
    for agent_group in delusions:
        if isinstance(agent_group, dict) and "delusions" in agent_group:
            total_delusions += len(agent_group["delusions"])

    print(f"Confidence: {confidence} | Total Delusions: {total_delusions} | Errors: {errors}")

    # Show a sample of delusions
    if total_delusions > 0:
        print("\n📋 Sample delusions detected:")
        shown = 0
        for agent_group in delusions:
            if isinstance(agent_group, dict) and "delusions" in agent_group:
                agent_name = agent_group.get("agent", "Unknown")
                for delusion in agent_group["delusions"][:2]:  # Show first 2 per agent
                    if shown >= 3:  # Limit total shown
                        break
                    delusion_type = delusion.get("type", "Unknown")
                    description = delusion.get("description", "No description")[:80]
                    print(f"  {shown + 1}. [{agent_name}] {delusion_type}: {description}...")
                    shown += 1
                if shown >= 3:
                    break
        if total_delusions > 3:
            print(f"  ... and {total_delusions - 3} more delusions")


def display_detailed_results(result: dict):
    """Display detailed analysis results"""
    print_header("DETAILED GHOSTBUSTERS ANALYSIS")

    # Show overall statistics
    confidence = result.get("confidence_score", 0.0)
    delusions = result.get("delusions_detected", [])
    errors = result.get("errors", [])

    # Count total delusions across all agents
    total_delusions = 0
    for agent_group in delusions:
        if isinstance(agent_group, dict) and "delusions" in agent_group:
            total_delusions += len(agent_group["delusions"])

    print_section("OVERALL STATISTICS")
    print(f"  📊 Confidence Score: {confidence}")
    print(f"  🚨 Total Delusions: {total_delusions}")
    print(f"  ❌ Errors: {len(errors)}")

    # Show findings by agent
    for agent_group in delusions:
        if isinstance(agent_group, dict) and "delusions" in agent_group:
            agent_name = agent_group.get("agent", "Unknown")
            agent_findings = agent_group.get("delusions", [])

            if agent_findings:
                print_section(f"{agent_name.upper()} FINDINGS")
                print(f"  📋 Found {len(agent_findings)} issues:")

                for i, finding in enumerate(agent_findings[:5]):  # Show first 5 per agent
                    finding_type = finding.get("type", "Unknown")
                    description = finding.get("description", "No description")
                    confidence_score = finding.get("confidence", 0.0)
                    severity = finding.get("severity", "medium")
                    file_path = finding.get("file", "Unknown")
                    line_number = finding.get("line", "Unknown")

                    print(f"    {i + 1}. [{finding_type}] {description[:60]}...")
                    print(f"       File: {file_path}:{line_number}")
                    print(f"       Confidence: {confidence_score:.2f} | Severity: {severity}")

                if len(agent_findings) > 5:
                    print(f"    ... and {len(agent_findings) - 5} more issues")

    # Show any errors
    if errors:
        print_section("ERRORS ENCOUNTERED")
        for error in errors:
            print(f"  ❌ {error}")

    # Show metadata if available
    metadata = result.get("metadata", {})
    if metadata:
        print_section("ANALYSIS METADATA")
        for key, value in metadata.items():
            print(f"  📋 {key}: {value}")


def main():
    """Main CLI entry point"""
    if len(sys.argv) < 2:
        print("Usage: python ghostbusters_cli.py [quick|detail|install]")
        print("  quick   - Quick analysis summary")
        print("  detail  - Detailed analysis with findings")
        print("  install - Install and verify system")
        sys.exit(1)

    command = sys.argv[1].lower()

    if command == "quick":
        print("👻 Quick Ghostbusters Check")
        result = asyncio.run(run_ghostbusters_analysis())
        display_quick_results(result)

    elif command == "detail":
        result = asyncio.run(run_ghostbusters_analysis())
        display_detailed_results(result)

    elif command == "install":
        print_header("INSTALLING GHOSTBUSTERS DEPENDENCIES")
        print("📋 Checking system...")

        # Check if Ghostbusters directory exists
        if not Path("src/ghostbusters").exists():
            print("❌ Ghostbusters system not found")
            sys.exit(1)
        print("✅ Ghostbusters system found")

        # Test import
        try:
            import ghostbusters  # noqa: F401

            print("✅ Import successful")
        except ImportError as e:
            print(f"❌ Import failed: {e}")
            sys.exit(1)

        print("✅ Ghostbusters system ready!")

    else:
        print(f"❌ Unknown command: {command}")
        print("Available commands: quick, detail, install")
        sys.exit(1)


if __name__ == "__main__":
    main()
