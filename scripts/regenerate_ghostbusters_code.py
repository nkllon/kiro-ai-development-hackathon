#!/usr/bin/env python3
"""
Regenerate Ghostbusters Code

Purpose: Use the round-trip system to regenerate clean code from extracted models
"""

import json
import os
import sys

# Add the root directory to Python path to access round_trip_model_system
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from round_trip_model_system import RoundTripModelSystem  # noqa: E402


def regenerate_ghostbusters_code():
    """Regenerate clean Ghostbusters code from extracted model"""

    print("🔄 Regenerating Ghostbusters Code from Extracted Model")
    print("=" * 60)

    # Load the extracted model
    model_path = "enhanced_reverse_engineered_model.json"

    if not os.path.exists(model_path):
        print(f"❌ Model file not found: {model_path}")
        return

    print(f"📂 Loading extracted model: {model_path}")

    try:
        with open(model_path) as f:
            extracted_model = json.load(f)
        print("✅ Model loaded successfully")
    except Exception as e:
        print(f"❌ Failed to load model: {e}")
        return

    # Initialize the round-trip system
    print("\n🔧 Initializing Round-Trip System")
    system = RoundTripModelSystem()

    # Generate clean code from the extracted model
    print("\n🎯 Generating Clean Code from Extracted Model")
    try:
        generated_code = system.generate_code_from_extracted_model(extracted_model)
        print("✅ Code generation successful!")

        # Save the regenerated code
        output_file = "regenerated_code_quality_expert.py"
        with open(output_file, "w") as f:
            f.write(generated_code)

        print(f"💾 Saved regenerated code to: {output_file}")

        # Verify the generated code parses
        print("\n🧪 Validating Generated Code")
        try:
            import ast

            ast.parse(generated_code)
            print("✅ Generated code parses successfully!")
        except SyntaxError as e:
            print(f"❌ Generated code has syntax errors: {e}")

        # Check for PEP 8 violations
        print("\n🔍 Checking for PEP 8 Violations")
        if "\\\n" in generated_code:
            print("❌ Generated code still contains backslash-newline patterns")
        else:
            print("✅ No backslash-newline patterns found")

        # Show a preview of the generated code
        print("\n📋 Generated Code Preview (first 500 chars):")
        print("-" * 50)
        print(generated_code[:500] + "..." if len(generated_code) > 500 else generated_code)
        print("-" * 50)

    except Exception as e:
        print(f"❌ Code generation failed: {e}")
        import traceback

        traceback.print_exc()


def main():
    """Main entry point"""
    regenerate_ghostbusters_code()


if __name__ == "__main__":
    main()
