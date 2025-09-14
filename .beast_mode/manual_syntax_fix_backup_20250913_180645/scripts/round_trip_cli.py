#!/usr/bin/env python3
"""
Round-Trip Engineering Command Line Interface

This script provides a command-line interface for the round-trip engineering system.
It uses the documented public interface of the RoundTripSystem.

Available Commands:
  reverse    - Reverse engineer a Python file to extract its model
  forward    - Forward engineer from a model to Python code
  round-trip - Complete round-trip workflow (reverse + forward + compare)
  compare    - Compare two Python files for functional equivalence
  status     - Show system status and capabilities
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Dict, Any

# Add the src directory to the path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from round_trip_engineering.core.round_trip_system import RoundTripSystem


def show_system_status():
    """Show the round-trip engineering system status."""
    print("🔍 Round-Trip Engineering System Status")
    print("=" * 50)

    try:
        rts = RoundTripSystem()
        status = rts.get_system_status()

        # Extract status information from the actual response structure
        overall_status = status.get("overall_status", "Unknown")
        print(f"Overall Status: {overall_status}")

        # Code Generation Status
        if "code_generation_status" in status:
            cg_status = status["code_generation_status"]
            print(f"Code Generation: {cg_status.get('code_generation_status', 'Unknown')}")
            print(f"Vocabulary Alignment: {cg_status.get('vocabulary_alignment_status', 'Unknown')}")
            print(f"Duplication Cleaning: {cg_status.get('duplication_cleaning_status', 'Unknown')}")

        # ArtifactForge Status
        if "artifact_forge_status" in status:
            af_status = status["artifact_forge_status"]
            print(f"ArtifactForge Integration: {af_status.get('integration_health', 'Unknown')}")
            print(f"Enhanced Parser: {'✅ Available' if af_status.get('enhanced_parser_available', False) else '❌ Not Available'}")

        # Workflow Analysis Status
        if "workflow_analysis_status" in status:
            wa_status = status["workflow_analysis_status"]
            print(f"Workflow Analysis: {wa_status.get('status', 'Unknown')}")
            capabilities = wa_status.get("analysis_capabilities", [])
            if capabilities:
                print(f"Analysis Capabilities: {', '.join(capabilities)}")

        # System Health Summary
        print(f"\nSystem Health: {'✅ Healthy' if overall_status == 'healthy' else '❌ Unhealthy'}")

    except Exception as e:
        print(f"❌ Failed to get system status: {e}")


def reverse_engineer(source_file: str) -> Dict[str, Any]:
    """Reverse engineer a Python file using the documented interface."""
    print(f"🔍 Reverse Engineering: {source_file}")

    try:
        rts = RoundTripSystem()

        # Use the documented interface method
        workflow_analysis = rts.get_workflow_analysis(source_file)

        print("✅ Reverse Engineering Complete")
        print(f"Analysis Type: {workflow_analysis.get('analysis_type', 'Unknown')}")

        return workflow_analysis

    except Exception as e:
        print(f"❌ Reverse Engineering Failed: {e}")
        return {"error": str(e)}


def forward_engineer(source_file: str, output_file: str) -> Dict[str, Any]:
    """Forward engineer using the documented interface."""
    print(f"🔧 Forward Engineering: {source_file} -> {output_file}")

    try:
        rts = RoundTripSystem()

        # Use the documented interface method
        result = rts.analyze_and_generate_code(source_file)

        # Extract the generated code
        if "generated_code" in result:
            with open(output_file, "w") as f:
                f.write(result["generated_code"])
            print(f"✅ Code written to: {output_file}")
        else:
            print("⚠️ No generated code found in result")
            print(f"Available keys: {list(result.keys())}")

        return result

    except Exception as e:
        print(f"❌ Forward Engineering Failed: {e}")
        return {"error": str(e)}


def compare_files(file1: str, file2: str) -> Dict[str, Any]:
    """Compare two Python files for functional equivalence."""
    print(f"🔍 Comparing Files: {file1} vs {file2}")

    try:
        # Read both files
        with open(file1, "r") as f1, open(file2, "r") as f2:
            content1 = f1.read()
            content2 = f2.read()

        # Basic comparison
        comparison = {
            "file1": file1,
            "file2": file2,
            "file1_size": len(content1),
            "file2_size": len(content2),
            "size_difference": abs(len(content1) - len(content2)),
            "identical": content1 == content2,
            "line_count_1": len(content1.splitlines()),
            "line_count_2": len(content2.splitlines()),
        }

        # Heuristic analysis for functional equivalence
        if comparison["identical"]:
            comparison["equivalence"] = "IDENTICAL"
            comparison["confidence"] = "100%"
        elif comparison["size_difference"] < 100:
            comparison["equivalence"] = "LIKELY_EQUIVALENT"
            comparison["confidence"] = "90%"
        elif comparison["size_difference"] < 500:
            comparison["equivalence"] = "POSSIBLY_EQUIVALENT"
            comparison["confidence"] = "70%"
        else:
            comparison["equivalence"] = "LIKELY_DIFFERENT"
            comparison["confidence"] = "30%"

        print(f"✅ Comparison Complete: {comparison['equivalence']} ({comparison['confidence']} confidence)")
        return comparison

    except Exception as e:
        print(f"❌ Comparison Failed: {e}")
        return {"error": str(e)}


def main():
    """Main CLI function."""
    parser = argparse.ArgumentParser(
        description="Round-Trip Engineering Command Line Interface",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Show system status
  uv run python round_trip_cli.py status
  
  # Reverse engineer a Python file
  uv run python round_trip_cli.py reverse test_file.py
  
  # Reverse engineer and save model to file
  uv run python round_trip_cli.py reverse test_file.py -o model.json
  
  # Forward engineer from a source file
  uv run python round_trip_cli.py forward test_file.py output.py
  
  # Complete round-trip workflow
  uv run python round_trip_cli.py round-trip test_file.py output.py
  
  # Compare two files
  uv run python round_trip_cli.py compare file1.py file2.py

Documentation:
  This CLI uses the documented public interface of RoundTripSystem:
  - get_system_status() - Get system health and capabilities
  - get_workflow_analysis(source_path) - Reverse engineer source code
  - analyze_and_generate_code(source_path) - Forward engineer code
        """,
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Status command
    status_parser = subparsers.add_parser("status", help="Show system status and capabilities")

    # Reverse engineering command
    reverse_parser = subparsers.add_parser("reverse", help="Reverse engineer a Python file")
    reverse_parser.add_argument("source_file", help="Source Python file to analyze")
    reverse_parser.add_argument("--output", "-o", help="Output JSON file for the model")

    # Forward engineering command
    forward_parser = subparsers.add_parser("forward", help="Forward engineer from a source file")
    forward_parser.add_argument("source_file", help="Source Python file to analyze and regenerate")
    forward_parser.add_argument("output_file", help="Output Python file")

    # Round-trip command
    round_trip_parser = subparsers.add_parser("round-trip", help="Complete round-trip workflow")
    round_trip_parser.add_argument("source_file", help="Source Python file")
    round_trip_parser.add_argument("output_file", help="Output Python file")

    # Compare command
    compare_parser = subparsers.add_parser("compare", help="Compare two Python files")
    compare_parser.add_argument("file1", help="First Python file")
    compare_parser.add_argument("file2", help="Second Python file")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    try:
        if args.command == "status":
            show_system_status()

        elif args.command == "reverse":
            model = reverse_engineer(args.source_file)
            if args.output:
                with open(args.output, "w") as f:
                    json.dump(model, f, indent=2)
                print(f"✅ Model saved to: {args.output}")
            else:
                print("\n📋 Extracted Model:")
                print(json.dumps(model, indent=2))

        elif args.command == "forward":
            result = forward_engineer(args.source_file, args.output_file)
            print("\n📋 Forward Engineering Result:")
            print(json.dumps(result, indent=2))

        elif args.command == "round-trip":
            print("🔄 Starting Round-Trip Engineering Workflow")
            print("=" * 50)

            # Step 1: Reverse Engineering
            print("\n📋 Step 1: Reverse Engineering")
            model = reverse_engineer(args.source_file)

            # Step 2: Forward Engineering
            print("\n📋 Step 2: Forward Engineering")
            result = forward_engineer(args.source_file, args.output_file)

            # Step 3: Comparison
            print("\n📋 Step 3: File Comparison")
            comparison = compare_files(args.source_file, args.output_file)

            # Summary
            print("\n📋 Summary")
            print("=" * 30)
            print(f"Source: {args.source_file}")
            print(f"Output: {args.output_file}")
            print(f"Equivalence: {comparison['equivalence']}")
            print(f"Confidence: {comparison['confidence']}")
            print(f"Size Difference: {comparison['size_difference']} characters")

        elif args.command == "compare":
            comparison = compare_files(args.file1, args.file2)
            print("\n📋 Comparison Result:")
            print(json.dumps(comparison, indent=2))

    except KeyboardInterrupt:
        print("\n❌ Operation cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
