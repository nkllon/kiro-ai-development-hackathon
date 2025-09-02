#!/usr/bin/env python3
"""
Round-Trip System Hairball Analysis
Profiles expected vs. actual behavior to understand the duplication bug
"""

import json
import os
import sys
from pathlib import Path
from typing import Dict, Any, List

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))


class RoundTripHairballAnalyzer:
    """Analyze the round-trip system hairball to understand duplication bugs"""

    def __init__(self):
        self.analysis_results = {}

    def analyze_expected_vs_actual(self):
        """Analyze expected vs. actual round-trip behavior"""
        print("🔍 Round-Trip System Hairball Analysis")
        print("=" * 60)

        # Step 1: Analyze source files
        print("\n📁 STEP 1: Source File Analysis")
        self._analyze_source_files()

        # Step 2: Analyze extracted models
        print("\n🔍 STEP 2: Extracted Model Analysis")
        self._analyze_extracted_models()

        # Step 3: Analyze generated files
        print("\n🏗️  STEP 3: Generated File Analysis")
        self._analyze_generated_files()

        # Step 4: Analyze the hairball
        print("\n🧶 STEP 4: Hairball Analysis")
        self._analyze_hairball_patterns()

        # Step 5: Generate recommendations
        print("\n💡 STEP 5: Recommendations")
        self._generate_recommendations()

    def _analyze_source_files(self):
        """Analyze the original source files"""
        source_files = [
            "src/round_trip_engineering/enhanced_reverse_engineer_v2.py",
            "src/round_trip_engineering/round_trip_model_system.py",
        ]

        for source_file in source_files:
            if os.path.exists(source_file):
                with open(source_file, "r") as f:
                    content = f.read()

                # Count method extraction calls
                method_extraction_calls = content.count("_extract_method_info_enhanced")
                method_generation_calls = content.count("_generate_method_from_extracted_model")

                print(f"  📄 {source_file}:")
                print(f"    - Method extraction calls: {method_extraction_calls}")
                print(f"    - Method generation calls: {method_generation_calls}")

                self.analysis_results[source_file] = {
                    "method_extraction_calls": method_extraction_calls,
                    "method_generation_calls": method_generation_calls,
                }

    def _analyze_extracted_models(self):
        """Analyze extracted models for duplication patterns"""
        model_files = [
            "enhanced_code_quality_model.json",
            "code_quality_model.json",
            "src/round_trip_generated/code_quality_model.json",
        ]

        for model_file in model_files:
            if os.path.exists(model_file):
                try:
                    with open(model_file, "r") as f:
                        model_data = json.load(f)

                    # Analyze components and methods
                    components = model_data.get("components", {})
                    total_methods = 0
                    methods_with_bodies = 0

                    for class_name, class_info in components.items():
                        methods = class_info.get("methods", [])
                        total_methods += len(methods)

                        for method in methods:
                            if method.get("body"):
                                methods_with_bodies += 1

                    print(f"  📊 {model_file}:")
                    print(f"    - Total components: {len(components)}")
                    print(f"    - Total methods: {total_methods}")
                    print(f"    - Methods with bodies: {methods_with_bodies}")

                    self.analysis_results[model_file] = {
                        "components": len(components),
                        "total_methods": total_methods,
                        "methods_with_bodies": methods_with_bodies,
                    }

                except Exception as e:
                    print(f"  ❌ Error analyzing {model_file}: {e}")

    def _analyze_generated_files(self):
        """Analyze generated files for duplication patterns"""
        generated_dir = "src/round_trip_generated"
        if os.path.exists(generated_dir):
            generated_files = list(Path(generated_dir).glob("*.py"))

            print(f"  🏗️  Generated Files ({len(generated_files)} total):")

            for gen_file in generated_files:
                try:
                    with open(gen_file, "r") as f:
                        content = f.read()

                    # Count duplication patterns
                    duplicate_returns = content.count('return ""')
                    duplicate_methods = content.count("def generate_fix")
                    unreachable_statements = content.count("# TODO: Implement")

                    print(f"    📄 {gen_file.name}:")
                    print(f"      - Duplicate return statements: {duplicate_returns}")
                    print(f"      - Duplicate method definitions: {duplicate_methods}")
                    print(f"      - TODO comments: {unreachable_statements}")

                    self.analysis_results[f"generated_{gen_file.name}"] = {
                        "duplicate_returns": duplicate_returns,
                        "duplicate_methods": duplicate_methods,
                        "todo_comments": unreachable_statements,
                    }

                except Exception as e:
                    print(f"    ❌ Error analyzing {gen_file.name}: {e}")

    def _analyze_hairball_patterns(self):
        """Analyze the hairball patterns to understand root cause"""
        print("  🧶 Hairball Pattern Analysis:")

        # Check for multiple round-trip runs
        root_files = [f for f in os.listdir(".") if f.endswith(".py") and "Quality" in f]
        generated_files = [f for f in os.listdir("src/round_trip_generated") if f.endswith(".py")]

        print(f"    - Root directory generated files: {len(root_files)}")
        print(f"    - Generated directory files: {len(generated_files)}")

        # Check for timestamp patterns
        if os.path.exists("src/round_trip_generated/proven_QualityRule.py"):
            stat = os.stat("src/round_trip_generated/proven_QualityRule.py")
            print(f"    - Last generated file modified: {stat.st_mtime}")

        # Check for cascading duplication
        total_duplicates = sum(result.get("duplicate_returns", 0) for key, result in self.analysis_results.items() if key.startswith("generated_"))

        print(f"    - Total duplicate return statements: {total_duplicates}")

        self.analysis_results["hairball_patterns"] = {
            "root_files": len(root_files),
            "generated_files": len(generated_files),
            "total_duplicates": total_duplicates,
        }

    def _generate_recommendations(self):
        """Generate recommendations based on analysis"""
        print("  💡 Recommendations:")

        # Check if we have a hairball
        total_duplicates = self.analysis_results.get("hairball_patterns", {}).get("total_duplicates", 0)

        if total_duplicates > 0:
            print("    🚨 CRITICAL: Duplication detected!")
            print("    📋 Action Plan:")
            print("      1. DELETE all broken generated files")
            print("      2. FIX the duplication bug in round-trip system")
            print("      3. REGENERATE clean code from models")
            print("      4. VALIDATE no duplications exist")

            # Specific recommendations
            if total_duplicates > 10:
                print("    ⚠️  HIGH duplication count - system may be fundamentally broken")
            elif total_duplicates > 5:
                print("    ⚠️  MEDIUM duplication count - bug in code generation")
            else:
                print("    ⚠️  LOW duplication count - minor issue")
        else:
            print("    ✅ No duplications detected - system appears clean")

        # Check for multiple round-trip runs
        root_files = self.analysis_results.get("hairball_patterns", {}).get("root_files", 0)
        if root_files > 0:
            print("    🔄 Multiple round-trip runs detected - clean up needed")

    def generate_report(self):
        """Generate a comprehensive analysis report"""
        report = {
            "summary": {
                "total_duplicates": self.analysis_results.get("hairball_patterns", {}).get("total_duplicates", 0),
                "has_hairball": self.analysis_results.get("hairball_patterns", {}).get("total_duplicates", 0) > 0,
                "multiple_runs": self.analysis_results.get("hairball_patterns", {}).get("root_files", 0) > 0,
            },
            "detailed_analysis": self.analysis_results,
            "recommendations": [
                "Delete broken generated files",
                "Fix duplication bug in round-trip system",
                "Regenerate clean code from models",
                "Validate no duplications exist",
            ],
        }

        # Save report
        with open("round_trip_hairball_analysis.json", "w") as f:
            json.dump(report, f, indent=2)

        print(f"\n📊 Analysis report saved to: round_trip_hairball_analysis.json")
        return report


def main():
    """Main entry point"""
    analyzer = RoundTripHairballAnalyzer()
    analyzer.analyze_expected_vs_actual()
    analyzer.generate_report()


if __name__ == "__main__":
    main()
