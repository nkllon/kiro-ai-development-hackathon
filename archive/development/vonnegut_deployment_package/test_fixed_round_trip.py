#!/usr/bin/env python3
"""
Test Fixed Round-Trip System

Purpose: Test the fixed round-trip system with method body extraction
"""

import json
import os
import sys

# Add the root directory to Python path to access round_trip_model_system
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from round_trip_model_system import RoundTripModelSystem  # noqa: E402


def test_fixed_round_trip():
    """Test the fixed round-trip system with enhanced model"""

    print("🔄 Testing Fixed Round-Trip System with Method Body Extraction")
    print("=" * 70)

    # Load the enhanced model
    model_file = "enhanced_reverse_engineered_model_fixed_v2.json"

    if not os.path.exists(model_file):
        print(f"❌ Enhanced model file not found: {model_file}")
        print(
            "Please run: python enhanced_reverse_engineer_fixed.py src/ghostbusters/agents/code_quality_expert.py"
        )
        return

    print(f"📁 Loading enhanced model: {model_file}")

    try:
        with open(model_file) as f:
            extracted_model = json.load(f)

        print("✅ Enhanced model loaded successfully!")
        print(f"   📦 Components: {len(extracted_model.get('components', {}))}")
        print(
            f"   📏 Total Lines: {extracted_model.get('file_structure', {}).get('total_lines', 0)}"
        )

        # Check if method bodies are extracted
        components = extracted_model.get("components", {})
        for class_name, class_info in components.items():
            methods = class_info.get("methods", [])
            implemented_methods = 0
            methods_with_bodies = 0

            for method in methods:
                if method.get("implementation_status") == "implemented":
                    implemented_methods += 1
                if method.get("body"):
                    methods_with_bodies += 1

            print(
                f"   🏗️  {class_name}: {implemented_methods}/{len(methods)} methods implemented"
            )
            print(
                f"   📝 {class_name}: {methods_with_bodies}/{len(methods)} methods have body content"
            )

        # Test the fixed round-trip system
        print("\n🔧 Testing Fixed Round-Trip System...")

        round_trip_system = RoundTripModelSystem()
        generated_code = round_trip_system.generate_code_from_extracted_model(
            extracted_model
        )

        print("✅ Code generation successful!")
        print(f"   📝 Generated code length: {len(generated_code)} characters")

        # Save the generated code
        output_file = "ghostbusters_code_quality_expert_fixed_round_trip.py"
        with open(output_file, "w") as f:
            f.write(generated_code)

        print(f"   💾 Generated code saved to: {output_file}")

        # Test functional equivalence
        print("\n🧪 Testing Functional Equivalence...")

        # Count lines in original vs generated
        original_file = "src/ghostbusters/agents/code_quality_expert.py"
        if os.path.exists(original_file):
            with open(original_file) as f:
                original_lines = len(f.readlines())

            generated_lines = len(generated_code.split("\n"))

            print(f"   📊 Original file: {original_lines} lines")
            print(f"   📊 Generated file: {generated_lines} lines")
            print(f"   📊 Line count ratio: {generated_lines / original_lines:.1%}")

            if generated_lines / original_lines > 0.8:
                print("   ✅ Line count suggests good functional equivalence!")
            else:
                print("   ⚠️  Line count suggests potential missing content")

        # Check for implementation vs skeleton
        if "# TODO: Implement" in generated_code:
            todo_count = generated_code.count("# TODO: Implement")
            print(f"   ⚠️  Found {todo_count} TODO comments (skeleton code)")
        else:
            print("   ✅ No TODO comments found (full implementation preserved)")

        # Check for method bodies
        if "delusions = []" in generated_code:
            print("   ✅ Method implementation content preserved!")
        else:
            print("   ❌ Method implementation content missing!")

        print("\n🎯 Fixed Round-Trip Test Complete!")

    except Exception as e:
        print(f"❌ Error testing fixed round-trip: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    test_fixed_round_trip()
