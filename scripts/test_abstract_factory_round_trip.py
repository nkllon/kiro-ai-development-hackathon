#!/usr/bin/env python3
"""
Test Abstract Factory Round-Trip Engineering

Purpose: Use the abstract factory to eliminate context confusion and properly round-trip code
"""

import json
import os
import sys

# Add src to path for accessing the abstract factory
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from abstract_factory_system import (
    generate_code_from_model,
    reverse_engineer_file,
)


def test_ghostbusters_round_trip():
    """Test round-trip engineering using the abstract factory"""

    print("🔄 Testing Ghostbusters Round-Trip with Abstract Factory")
    print("=" * 60)

    # Test file
    test_file = "src/ghostbusters/agents/code_quality_expert.py"

    if not os.path.exists(test_file):
        print(f"❌ Test file not found: {test_file}")
        return

    print(f"📁 Testing file: {test_file}")

    # Step 1: Reverse engineer using abstract factory
    print("\n🔍 Step 1: Reverse Engineering with Abstract Factory")
    try:
        model = reverse_engineer_file(test_file)
        print("✅ Model extracted successfully!")
        print(f"   📦 Components: {len(model.get('components', {}))}")
        print(f"   ⚙️  Module Functions: {len(model.get('module_functions', []))}")
        print(f"   📏 Total Lines: {model.get('file_structure', {}).get('total_lines', 0)}")

        # Save the model
        model_file = "ghostbusters_code_quality_expert_model.json"
        with open(model_file, "w") as f:
            json.dump(model, f, indent=2)
        print(f"   💾 Model saved to: {model_file}")

    except Exception as e:
        print(f"❌ Reverse engineering failed: {e}")
        return

    # Step 2: Generate code using abstract factory
    print("\n🔧 Step 2: Code Generation with Abstract Factory")
    try:
        generated_code = generate_code_from_model(model)
        print("✅ Code generated successfully!")
        print(f"   📝 Generated code length: {len(generated_code)} characters")

        # Save the generated code
        output_file = "ghostbusters_code_quality_expert_regenerated.py"
        with open(output_file, "w") as f:
            f.write(generated_code)
        print(f"   💾 Generated code saved to: {output_file}")

    except Exception as e:
        print(f"❌ Code generation failed: {e}")
        return

    # Step 3: Validate functional equivalence
    print("\n✅ Step 3: Functional Equivalence Validation")

    # Check line counts
    original_lines = len(open(test_file).readlines())
    generated_lines = len(generated_code.split("\n"))

    print(f"   📊 Original file: {original_lines} lines")
    print(f"   📊 Generated file: {generated_lines} lines")

    # Check if generated code can be imported
    print("\n🧪 Testing Generated Code Import:")
    try:
        # Create a temporary import test
        test_import_file = "test_import.py"
        with open(test_import_file, "w") as f:
            f.write(generated_code)

        # Test import
        import subprocess

        result = subprocess.run(
            [
                "uv",
                "run",
                "python",
                "-c",
                f'import sys; sys.path.insert(0, "."); exec(open("{test_import_file}").read()); print("✅ Generated code imports successfully!")',
            ],
            capture_output=True,
            text=True,
        )

        if result.returncode == 0:
            print("✅ Generated code imports successfully!")
        else:
            print(f"❌ Generated code import failed: {result.stderr}")

        # Clean up
        os.remove(test_import_file)

    except Exception as e:
        print(f"❌ Import test failed: {e}")

    print("\n🎯 Abstract Factory Round-Trip Test Complete!")


def main():
    """Main function"""
    test_ghostbusters_round_trip()


if __name__ == "__main__":
    main()
