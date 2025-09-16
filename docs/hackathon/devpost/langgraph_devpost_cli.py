#!/usr/bin/env python3
"""
LangGraph DevPost CLI
=====================

Command-line interface for the LangGraph-based DevPost automation workflow.
"""

import argparse
import sys
import json
from typing import Optional
from datetime import datetime

from langgraph_devpost_workflow import DevPostWorkflow, create_devpost_workflow


def main():
    """Main CLI entry point"""

    parser = argparse.ArgumentParser(
        description="DevPost Automation Workflow with LangGraph",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run interactive workflow
  python langgraph_devpost_cli.py run --mode interactive
  
  # Run automatic workflow with custom data directory
  python langgraph_devpost_cli.py run --mode automatic --data-dir /custom/path
  
  # Resume existing workflow
  python langgraph_devpost_cli.py resume --workflow-id devpost_workflow_20241201_143022
  
  # Check workflow status
  python langgraph_devpost_cli.py status --workflow-id devpost_workflow_20241201_143022
  
  # Provide input for interactive recovery
  python langgraph_devpost_cli.py input --workflow-id devpost_workflow_20241201_143022 "1"
  
  # List all workflows
  python langgraph_devpost_cli.py list
        """,
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Run command
    run_parser = subparsers.add_parser("run", help="Run DevPost automation workflow")
    run_parser.add_argument(
        "--mode",
        choices=["interactive", "automatic", "guided"],
        default="interactive",
        help="Automation mode (default: interactive)",
    )
    run_parser.add_argument(
        "--data-dir",
        default="/tmp/devpost-browser",
        help="Browser data directory (default: /tmp/devpost-browser)",
    )
    run_parser.add_argument(
        "--workflow-id", help="Custom workflow ID (default: auto-generated)"
    )
    run_parser.add_argument("--output", help="Output file for workflow results")

    # Resume command
    resume_parser = subparsers.add_parser("resume", help="Resume existing workflow")
    resume_parser.add_argument("workflow_id", help="Workflow ID to resume")
    resume_parser.add_argument("--output", help="Output file for workflow results")

    # Status command
    status_parser = subparsers.add_parser("status", help="Check workflow status")
    status_parser.add_argument("workflow_id", help="Workflow ID to check")
    status_parser.add_argument(
        "--json", action="store_true", help="Output status as JSON"
    )

    # Input command (for interactive recovery)
    input_parser = subparsers.add_parser(
        "input", help="Provide input for interactive recovery"
    )
    input_parser.add_argument("workflow_id", help="Workflow ID to provide input for")
    input_parser.add_argument(
        "user_input", help="User input/choice for recovery or memory qualification"
    )
    input_parser.add_argument(
        "--output", help="Output file for workflow results after input"
    )

    # List command
    list_parser = subparsers.add_parser("list", help="List available workflows")
    list_parser.add_argument("--json", action="store_true", help="Output as JSON")

    # Version command
    subparsers.add_parser("version", help="Show version information")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    try:
        if args.command == "run":
            run_workflow(args)
        elif args.command == "resume":
            resume_workflow(args)
        elif args.command == "status":
            check_status(args)
        elif args.command == "input":
            handle_input(args)
        elif args.command == "list":
            list_workflows(args)
        elif args.command == "version":
            show_version()
        else:
            parser.print_help()
            sys.exit(1)

    except KeyboardInterrupt:
        print("\n⚠️ Workflow interrupted by user")
        sys.exit(130)
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        sys.exit(1)


def run_workflow(args):
    """Run the DevPost automation workflow"""

    print("🚀 DevPost Automation Workflow")
    print("=" * 50)

    # Create workflow
    workflow = create_devpost_workflow(args.workflow_id)

    # Run workflow
    result = workflow.run_workflow(
        user_data_dir=args.data_dir, automation_mode=args.mode
    )

    # Handle results
    if result["success"]:
        print("\n✅ Workflow completed successfully!")

        # Save results if requested
        if args.output:
            save_results(result, args.output)

        # Show summary
        summary = result.get("summary", {})
        print("\n📊 Workflow Summary:")
        for key, value in summary.items():
            print(f"   {key}: {value}")

    else:
        print(f"\n❌ Workflow failed: {result['error']}")
        sys.exit(1)


def resume_workflow(args):
    """Resume an existing workflow"""

    print(f"🔄 Resuming workflow: {args.workflow_id}")
    print("=" * 50)

    # Create workflow
    workflow = create_devpost_workflow()

    # Resume workflow
    result = workflow.resume_workflow(args.workflow_id)

    # Handle results
    if result["success"]:
        print("\n✅ Workflow resumed and completed!")

        # Save results if requested
        if args.output:
            save_results(result, args.output)

        # Show summary
        summary = result.get("summary", {})
        print("\n📊 Workflow Summary:")
        for key, value in summary.items():
            print(f"   {key}: {value}")

    else:
        print(f"\n❌ Resume failed: {result['error']}")
        sys.exit(1)


def check_status(args):
    """Check workflow status"""

    # Create workflow
    workflow = create_devpost_workflow()

    # Get status
    status = workflow.get_workflow_status(args.workflow_id)

    if args.json:
        print(json.dumps(status, indent=2, default=str))
    else:
        print(f"📋 Workflow Status: {args.workflow_id}")
        print("=" * 50)

        if status["status"] == "not_found":
            print("❌ Workflow not found")
        elif status["status"] == "error":
            print(f"❌ Error: {status['error']}")
        else:
            print(f"Phase: {status.get('current_phase', 'Unknown')}")
            print(f"Status: {status['status']}")
            print(f"User Input Required: {status.get('user_input_required', False)}")

            # Show interactive recovery status
            if status.get("ghostbusters_mode", False):
                print("🚨 GHOSTBUSTERS MODE: Completely confused - needs help!")
            if status.get("awaiting_recovery_choice", False):
                print("🤔 Awaiting recovery choice (1-5)")
            if status.get("awaiting_memory_qualification", False):
                print("🧠 Awaiting memory qualification")

            errors = status.get("errors", [])
            if errors:
                print(f"Errors: {len(errors)}")
                for error in errors[-3:]:  # Show last 3 errors
                    print(f"   • {error}")

            summary = status.get("summary", {})
            if summary:
                print("\n📊 Summary:")
                for key, value in summary.items():
                    print(f"   {key}: {value}")


def handle_input(args):
    """Handle user input for interactive recovery"""

    print(f"🔄 Handling input for workflow: {args.workflow_id}")
    print(f"📝 User input: {args.user_input}")
    print("=" * 50)

    # Create workflow
    workflow = create_devpost_workflow()

    # Handle the input
    result = workflow.handle_user_input(args.workflow_id, args.user_input)

    if result["success"]:
        print(f"✅ {result['message']}")

        # Check if workflow should continue
        if result.get("next_action") == "continue_workflow":
            print("🔄 Workflow continuing...")

            # Get updated status
            status = workflow.get_workflow_status(args.workflow_id)

            if status["status"] == "completed":
                print("✅ Workflow completed!")

                # Save results if requested
                if args.output:
                    workflow_result = {
                        "success": True,
                        "final_state": status,
                        "summary": status.get("summary", {}),
                        "workflow_id": args.workflow_id,
                    }
                    save_results(workflow_result, args.output)
            else:
                print(f"📍 Current phase: {status.get('current_phase', 'Unknown')}")

                # Check if more input is needed
                if status.get("awaiting_recovery_choice", False):
                    print("🤔 Still awaiting recovery choice")
                elif status.get("awaiting_memory_qualification", False):
                    print("🧠 Still awaiting memory qualification")
                elif status.get("user_input_required", False):
                    print("👤 User input still required")
                else:
                    print("🔄 Workflow running autonomously")
        else:
            print("⏸️ Workflow paused - check status for next steps")

    else:
        print(f"❌ Failed to handle input: {result['error']}")
        sys.exit(1)


def list_workflows(args):
    """List available workflows"""

    # For now, this is a placeholder since we don't have persistent storage
    # In a real implementation, you'd query the checkpointer for available workflows

    print("📋 Available Workflows")
    print("=" * 50)
    print("⚠️ Workflow listing not yet implemented")
    print("💡 Use 'status' command with a specific workflow ID")


def save_results(result: dict, output_file: str):
    """Save workflow results to file"""

    try:
        # Prepare results for JSON serialization
        serializable_result = {}
        for key, value in result.items():
            if key == "final_state" and value:
                # Convert final state to serializable format
                serializable_result[key] = {}
                for state_key, state_value in value.items():
                    if hasattr(state_value, "value"):  # Enum
                        serializable_result[key][state_key] = state_value.value
                    elif hasattr(state_value, "isoformat"):  # datetime
                        serializable_result[key][state_key] = state_value.isoformat()
                    else:
                        serializable_result[key][state_key] = state_value
            else:
                serializable_result[key] = value

        with open(output_file, "w") as f:
            json.dump(serializable_result, f, indent=2, default=str)

        print(f"💾 Results saved to: {output_file}")

    except Exception as e:
        print(f"⚠️ Failed to save results: {str(e)}")


def show_version():
    """Show version information"""

    print("DevPost Automation Workflow")
    print("Version: 1.0.0")
    print("Framework: LangGraph + Playwright")
    print("Python: 3.9+")


if __name__ == "__main__":
    main()
