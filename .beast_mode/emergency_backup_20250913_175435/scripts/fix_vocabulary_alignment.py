#!/usr/bin/env python3
"""
Fix Vocabulary Alignment Between Reverse Engineering and Code Generation
Align the terms and data structures so both systems can communicate properly
"""

import json
import os
import sys
from pathlib import Path
from typing import Dict, Any, List, Union

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))


class VocabularyMapper:
    """Maps vocabulary between reverse engineering and code generation"""

    # Vocabulary mapping table
    VOCABULARY_MAP = {
        # Reverse Engineering → Code Generation
        "components": "target_components",
        "methods": "generation_methods",
        "dependencies": "import_requirements",
        "requirements": "implementation_requirements",
        "metadata": "generation_metadata",
        "type": "entity_type",
        "description": "entity_description",
        "parameters": "method_parameters",
        "return_type": "method_return_type",
    }

    # Data structure transformations
    STRUCTURE_TRANSFORMS = {
        "components": {
            "from": "list",  # Reverse engineering outputs list
            "to": "dict",  # Code generation expects dict
            "transform": "list_to_dict_by_name",
        }
    }

    def __init__(self):
        self.reverse_engineering_vocab = set()
        self.code_generation_vocab = set()

    def analyze_vocabulary(self, model_file: str) -> Dict[str, Any]:
        """Analyze the vocabulary used in a model file"""
        print(f"🔍 Analyzing vocabulary in: {model_file}")

        with open(model_file, "r") as f:
            model_data = json.load(f)

        # Extract all keys used
        all_keys = self._extract_all_keys(model_data)

        # Categorize by expected usage
        reverse_engineering_keys = []
        code_generation_keys = []
        ambiguous_keys = []

        for key in all_keys:
            if key in self.VOCABULARY_MAP:
                reverse_engineering_keys.append(key)
                code_generation_keys.append(self.VOCABULARY_MAP[key])
            elif key in self.VOCABULARY_MAP.values():
                code_generation_keys.append(key)
            else:
                ambiguous_keys.append(key)

        return {
            "reverse_engineering_vocab": reverse_engineering_keys,
            "code_generation_vocab": code_generation_keys,
            "ambiguous_vocab": ambiguous_keys,
            "total_keys": len(all_keys),
            "vocabulary_coverage": (len(reverse_engineering_keys) / len(all_keys) if all_keys else 0),
        }

    def _extract_all_keys(self, data: Any, prefix: str = "") -> List[str]:
        """Recursively extract all keys from nested data structures"""
        keys = []

        if isinstance(data, dict):
            for key, value in data.items():
                full_key = f"{prefix}.{key}" if prefix else key
                keys.append(full_key)
                keys.extend(self._extract_all_keys(value, full_key))
        elif isinstance(data, list):
            for i, item in enumerate(data):
                full_key = f"{prefix}[{i}]" if prefix else f"[{i}]"
                keys.extend(self._extract_all_keys(item, full_key))

        return keys

    def transform_model_for_code_generation(self, model_file: str) -> Dict[str, Any]:
        """Transform a reverse engineering model to code generation format"""
        print(f"🔄 Transforming model for code generation: {model_file}")

        with open(model_file, "r") as f:
            model_data = json.load(f)

        # Apply vocabulary mapping
        transformed_data = self._apply_vocabulary_mapping(model_data)

        # Apply data structure transformations
        transformed_data = self._apply_structure_transforms(transformed_data)

        return transformed_data

    def _apply_vocabulary_mapping(self, data: Any) -> Any:
        """Apply vocabulary mapping to transform keys"""
        if isinstance(data, dict):
            transformed = {}
            for key, value in data.items():
                # Map the key if it exists in our vocabulary
                new_key = self.VOCABULARY_MAP.get(key, key)
                transformed[new_key] = self._apply_vocabulary_mapping(value)
            return transformed
        elif isinstance(data, list):
            return [self._apply_vocabulary_mapping(item) for item in data]
        else:
            return data

    def _apply_structure_transforms(self, data: Any) -> Any:
        """Apply data structure transformations"""
        if isinstance(data, dict):
            for key, transform_info in self.STRUCTURE_TRANSFORMS.items():
                if key in data:
                    if transform_info["transform"] == "list_to_dict_by_name":
                        data[key] = self._list_to_dict_by_name(data[key])

        return data

    def _list_to_dict_by_name(self, components_list: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Transform list of components to dict keyed by name"""
        components_dict = {}
        for component in components_list:
            if isinstance(component, dict) and "name" in component:
                components_dict[component["name"]] = component
            else:
                # Handle components without names
                components_dict[f"component_{len(components_dict)}"] = component

        return components_dict

    def create_vocabulary_report(self, model_files: List[str]) -> Dict[str, Any]:
        """Create a comprehensive vocabulary analysis report"""
        print("📊 Creating vocabulary analysis report...")

        report = {
            "vocabulary_mapping": self.VOCABULARY_MAP,
            "structure_transforms": self.STRUCTURE_TRANSFORMS,
            "model_analyses": {},
            "recommendations": [],
        }

        # Analyze each model file
        for model_file in model_files:
            if os.path.exists(model_file):
                analysis = self.analyze_vocabulary(model_file)
                report["model_analyses"][model_file] = analysis

        # Generate recommendations
        report["recommendations"] = self._generate_recommendations(report)

        return report

    def _generate_recommendations(self, report: Dict[str, Any]) -> List[str]:
        """Generate recommendations based on vocabulary analysis"""
        recommendations = []

        # Check vocabulary coverage
        total_coverage = 0
        model_count = 0

        for analysis in report["model_analyses"].values():
            total_coverage += analysis["vocabulary_coverage"]
            model_count += 1

        avg_coverage = total_coverage / model_count if model_count > 0 else 0

        if avg_coverage < 0.5:
            recommendations.append("⚠️  Low vocabulary coverage - consider expanding vocabulary mapping")
        elif avg_coverage < 0.8:
            recommendations.append("🔶 Medium vocabulary coverage - some terms may be ambiguous")
        else:
            recommendations.append("✅ High vocabulary coverage - systems should communicate well")

        # Check for ambiguous terms
        all_ambiguous = set()
        for analysis in report["model_analyses"].values():
            all_ambiguous.update(analysis["ambiguous_vocab"])

        if all_ambiguous:
            recommendations.append(f"🔍 Found {len(all_ambiguous)} ambiguous terms that need qualification")
            recommendations.append("   Consider adding these to the vocabulary mapping")

        # Check data structure consistency
        recommendations.append("🔄 Ensure reverse engineering outputs match code generation expectations")
        recommendations.append("   Use vocabulary mapping to transform between formats")

        return recommendations


def main():
    """Main entry point"""
    print("🔧 Fixing Vocabulary Alignment Between Reverse Engineering and Code Generation")
    print("=" * 80)

    # Initialize vocabulary mapper
    mapper = VocabularyMapper()

    # Model files to analyze
    model_files = ["enhanced_code_quality_model.json", "code_quality_model.json"]

    # Step 1: Analyze current vocabulary
    print("\n📊 STEP 1: Analyzing current vocabulary usage...")
    report = mapper.create_vocabulary_report(model_files)

    # Print analysis results
    for model_file, analysis in report["model_analyses"].items():
        print(f"\n📁 {model_file}:")
        print(f"  Total keys: {analysis['total_keys']}")
        print(f"  Vocabulary coverage: {analysis['vocabulary_coverage']:.1%}")
        print(f"  Reverse engineering terms: {len(analysis['reverse_engineering_vocab'])}")
        print(f"  Code generation terms: {len(analysis['code_generation_vocab'])}")
        print(f"  Ambiguous terms: {len(analysis['ambiguous_vocab'])}")

    # Print recommendations
    print(f"\n💡 RECOMMENDATIONS:")
    for rec in report["recommendations"]:
        print(f"  {rec}")

    # Step 2: Transform a model for testing
    print(f"\n🔄 STEP 2: Testing vocabulary transformation...")
    if os.path.exists("enhanced_code_quality_model.json"):
        transformed_model = mapper.transform_model_for_code_generation("enhanced_code_quality_model.json")

        # Save transformed model
        output_file = "enhanced_code_quality_model_transformed.json"
        with open(output_file, "w") as f:
            json.dump(transformed_model, f, indent=2)

        print(f"  ✅ Transformed model saved to: {output_file}")

        # Verify the transformation worked
        if "target_components" in transformed_model:
            print(f"  ✅ 'components' → 'target_components' transformation successful")
            print(f"  ✅ Components now in dict format: {len(transformed_model['target_components'])}")
        else:
            print(f"  ❌ Vocabulary transformation failed")

    # Step 3: Create vocabulary documentation
    print(f"\n📚 STEP 3: Creating vocabulary documentation...")
    vocab_doc = {
        "vocabulary_alignment": {
            "purpose": "Align vocabulary between reverse engineering and code generation",
            "mapping": report["vocabulary_mapping"],
            "transforms": report["structure_transforms"],
            "usage_notes": {
                "reverse_engineering": "Use these terms when extracting code structure",
                "code_generation": "Use these terms when generating code from models",
                "transformation": "Apply vocabulary mapping and structure transforms",
            },
        }
    }

    vocab_file = "vocabulary_alignment.json"
    with open(vocab_file, "w") as f:
        json.dump(vocab_doc, f, indent=2)

    print(f"  ✅ Vocabulary documentation saved to: {vocab_file}")

    print(f"\n🎉 VOCABULARY ALIGNMENT COMPLETE!")
    print(f"📋 Summary:")
    print(f"  - Analyzed {len(model_files)} model files")
    print(f"  - Created vocabulary mapping for {len(report['vocabulary_mapping'])} terms")
    print(f"  - Applied structure transformations")
    print(f"  - Generated vocabulary documentation")

    print(f"\n🚀 Next Steps:")
    print(f"  1. Update reverse engineering to use aligned vocabulary")
    print(f"  2. Update code generation to expect aligned vocabulary")
    print(f"  3. Test communication between systems")
    print(f"  4. Monitor for vocabulary drift")


if __name__ == "__main__":
    main()
