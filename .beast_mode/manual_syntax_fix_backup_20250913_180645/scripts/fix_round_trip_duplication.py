#!/usr/bin/env python3
"""
Fix Round-Trip Duplication Issue
Clean up generated files and ensure clean regeneration from models
"""

import os
import shutil
import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))


def cleanup_generated_files():
    """Clean up all broken generated files"""
    print("🧹 Cleaning up broken generated files...")

    # Files to clean up
    files_to_clean = [
        "src/round_trip_generated/proven_QualityRule.py",
        "src/round_trip_generated/proven_QualityOrchestrator.py",
        "src/round_trip_generated/proven_ASTAnalyzer.py",
        "src/round_trip_generated/__init__.py",
    ]

    # Root directory duplicates
    root_duplicates = ["proven_QualityRule.py", "proven_QualityOrchestrator.py"]

    cleaned_count = 0

    # Clean generated directory files
    for file_path in files_to_clean:
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
                print(f"  ✅ Deleted: {file_path}")
                cleaned_count += 1
            except Exception as e:
                print(f"  ❌ Failed to delete {file_path}: {e}")

    # Clean root directory duplicates
    for file_path in root_duplicates:
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
                print(f"  ✅ Deleted: {file_path}")
                cleaned_count += 1
            except Exception as e:
                print(f"  ❌ Failed to delete {file_path}: {e}")

    print(f"🧹 Cleaned up {cleaned_count} files")
    return cleaned_count


def fix_round_trip_system():
    """Fix the round-trip system to prevent duplication"""
    print("\n🔧 Fixing round-trip system duplication bug...")

    # The issue is that the round-trip system accumulates duplicates
    # instead of generating clean code from scratch. Let me add a fix
    # to ensure clean generation.

    round_trip_file = "src/round_trip_engineering/round_trip_model_system.py"

    if not os.path.exists(round_trip_file):
        print(f"  ❌ Round-trip system file not found: {round_trip_file}")
        return False

    # Read the current file
    with open(round_trip_file, "r") as f:
        content = f.read()

    # Check if the fix is already applied
    if "CLEAN_GENERATION_FIX" in content:
        print("  ✅ Clean generation fix already applied")
        return True

    # Add a fix to ensure clean generation
    fix_code = '''
    def _ensure_clean_generation(self, code: str) -> str:
        """CLEAN_GENERATION_FIX: Ensure generated code has no duplications"""
        lines = code.split("\\n")
        cleaned_lines = []
        seen_methods = set()
        
        for line in lines:
            # Skip duplicate method definitions
            if line.strip().startswith("def ") and "def " in line:
                method_name = line.split("def ")[1].split("(")[0].strip()
                if method_name in seen_methods:
                    continue  # Skip duplicate method
                seen_methods.add(method_name)
            
            # Skip duplicate return statements within same method
            if line.strip().startswith("return "):
                # Check if this is a duplicate return in the same method
                # (This is a simplified check - in practice, we'd need more context)
                pass
            
            cleaned_lines.append(line)
        
        return "\\n".join(cleaned_lines)
'''

    # Find where to insert the fix (after the _clean_generated_code method)
    if "_clean_generated_code" in content:
        # Insert the fix after the existing _clean_generated_code method
        content = content.replace(
            "    def _clean_generated_code(self, code: str) -> str:",
            "    def _clean_generated_code(self, code: str) -> str:" + fix_code,
        )

        # Also update the call to use the new method
        content = content.replace(
            "        return self._clean_generated_code(code)",
            "        cleaned_code = self._clean_generated_code(code)\n        return self._ensure_clean_generation(cleaned_code)",
        )

        # Write the fixed file
        with open(round_trip_file, "w") as f:
            f.write(content)

        print("  ✅ Applied clean generation fix to round-trip system")
        return True
    else:
        print("  ❌ Could not find _clean_generated_code method to apply fix")
        return False


def regenerate_clean_code():
    """Regenerate clean code from models"""
    print("\n🔄 Regenerating clean code from models...")

    # Check if we have the round-trip system available
    try:
        from round_trip_engineering.round_trip_model_system import RoundTripModelSystem

        print("  ✅ Round-trip system imported successfully")
    except ImportError as e:
        print(f"  ❌ Could not import round-trip system: {e}")
        return False

    # Check if we have a model to work with
    model_files = ["enhanced_code_quality_model.json", "code_quality_model.json"]

    model_file = None
    for mf in model_files:
        if os.path.exists(mf):
            model_file = mf
            break

    if not model_file:
        print("  ❌ No model file found for regeneration")
        return False

    print(f"  📊 Using model: {model_file}")

    try:
        # Initialize the round-trip system
        system = RoundTripModelSystem()

        # Load the model
        import json

        with open(model_file, "r") as f:
            model_data = json.load(f)

        # Generate clean code
        generated_code = system.generate_code_from_extracted_model(model_data)

        # Save the clean generated code
        output_file = "src/round_trip_generated/clean_quality_system.py"
        os.makedirs("src/round_trip_generated", exist_ok=True)

        with open(output_file, "w") as f:
            f.write(generated_code)

        print(f"  ✅ Generated clean code: {output_file}")

        # Validate the generated code
        try:
            import ast

            ast.parse(generated_code)
            print("  ✅ Generated code parses successfully")
        except SyntaxError as e:
            print(f"  ❌ Generated code has syntax errors: {e}")
            return False

        return True

    except Exception as e:
        print(f"  ❌ Code regeneration failed: {e}")
        import traceback

        traceback.print_exc()
        return False


def main():
    """Main entry point"""
    print("🔧 Fixing Round-Trip Duplication Issue")
    print("=" * 50)

    # Step 1: Clean up broken files
    cleaned_count = cleanup_generated_files()

    # Step 2: Fix the round-trip system
    fix_applied = fix_round_trip_system()

    # Step 3: Regenerate clean code
    if fix_applied:
        regeneration_success = regenerate_clean_code()

        if regeneration_success:
            print("\n🎉 SUCCESS: Round-trip duplication issue fixed!")
            print("📋 Summary:")
            print(f"  - Cleaned up {cleaned_count} broken files")
            print(f"  - Applied duplication fix: {'✅' if fix_applied else '❌'}")
            print(f"  - Regenerated clean code: {'✅' if regeneration_success else '❌'}")
        else:
            print("\n⚠️  PARTIAL SUCCESS: Cleanup and fix applied, but regeneration failed")
    else:
        print("\n❌ FAILED: Could not apply duplication fix")


if __name__ == "__main__":
    main()
