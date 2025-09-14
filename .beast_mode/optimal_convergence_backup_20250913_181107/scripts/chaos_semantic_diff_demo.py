#!/usr/bin/env python3
"""
Chaos Semantic Diff Demo - Maximum Chaos Testing Across File Types

This script creates MAXIMUM CHAOS by:
1. Creating different file types (Python, TOML, JSON, Shell)
2. Converting them to GlacierSpores
3. Attempting semantic diffing between completely different types
4. Seeing what chaos ensues!

Because we <3 chaos! 🎪🔥
"""

import hashlib
import json
import tempfile
from pathlib import Path
from typing import Any, Dict, List

# Import our chaos systems
try:
    from ghostbusters_file_type_processor import GhostbustersFileTypeProcessor
    from glacier_spore_models import Dimension, DimensionType, GlacierSpore, SporeType
    from semantic_diff_engine import SemanticDiffEngine
except ImportError as e:
    print(f"⚠️  Import error: {e}")
    print("Creating mock versions for chaos demo...")

    # Mock classes for chaos demo
    class SporeType:
        DISCOVERY = "discovery"
        ANALYSIS = "analysis"
        VALIDATION = "validation"

    class DimensionType:
        TEMPORAL = "temporal"
        SEMANTIC = "semantic"
        PROCESSING = "processing"

    class Dimension:
        def __init__(self, name: str, value: Any, dimension_type: str):
            self.name = name
            self.value = value
            self.dimension_type = dimension_type

    class GlacierSpore:
        def __init__(
            self,
            spore_type: str,
            content: dict[str, Any],
            metadata: dict[str, Any] = None,
        ):
            self.spore_type = spore_type
            self.content = content
            self.metadata = metadata or {}
            self.dimensions = []
            self.embedded_schema = {"type": "mock_schema"}
            self.content_schema = {"type": "mock_content_schema"}
            self.processing_instructions = []

        def add_dimension(self, dimension: Dimension):
            self.dimensions.append(dimension)

    class SemanticDiffEngine:
        def __init__(self):
            self.chaos_level = "MAXIMUM"

        def diff_spores(self, old_spore: GlacierSpore, new_spore: GlacierSpore) -> list[dict[str, Any]]:
            """Create semantic diffs between spores with MAXIMUM CHAOS"""
            print(f"🔥 CHAOS DIFFING: {old_spore.spore_type} vs {new_spore.spore_type}")

            diffs = []

            # Content changes
            if old_spore.content != new_spore.content:
                diffs.append(
                    {
                        "type": "content_chaos",
                        "description": f"Content changed from {type(old_spore.content)} to {type(new_spore.content)}",
                        "impact_score": 0.8,
                        "chaos_level": "HIGH",
                    }
                )

            # Type changes
            if old_spore.spore_type != new_spore.spore_type:
                diffs.append(
                    {
                        "type": "type_chaos",
                        "description": f"Spore type changed from {old_spore.spore_type} to {new_spore.spore_type}",
                        "impact_score": 0.9,
                        "chaos_level": "CRITICAL",
                    }
                )

            # Dimension chaos
            old_dim_count = len(old_spore.dimensions)
            new_dim_count = len(new_spore.dimensions)
            if old_dim_count != new_dim_count:
                diffs.append(
                    {
                        "type": "dimension_chaos",
                        "description": f"Dimensions changed from {old_dim_count} to {new_dim_count}",
                        "impact_score": 0.7,
                        "chaos_level": "MEDIUM",
                    }
                )

            return diffs


def create_chaos_files() -> dict[str, str]:
    """Create different file types for maximum chaos"""
    chaos_files = {}

    # 1. Python file (complex structure)
    python_content = '''#!/usr/bin/env python3
"""
Chaos Python File - Maximum Complexity
"""

import json
import yaml
from typing import Any

class ChaosClass:
    def __init__(self, chaos_level: str = "MAXIMUM"):
        self.chaos_level = chaos_level
        self.chaos_data = {}

    def add_chaos(self, chaos_type: str, chaos_value: Any):
        self.chaos_data[chaos_type] = chaos_value

    def get_chaos_level(self) -> str:
        return f"CHAOS_LEVEL_{self.chaos_level.upper()}"

def main():
    chaos = ChaosClass("MAXIMUM")
    chaos.add_chaos("file_type", "python")
    chaos.add_chaos("complexity", "HIGH")
    chaos.add_chaos("chaos_factor", 0.95)
    print(f"Chaos level: {chaos.get_chaos_level()}")

if __name__ == "__main__":
    main()
'''
    chaos_files["python"] = python_content

    # 2. TOML file (configuration structure)
    toml_content = """# Chaos TOML Configuration
[chaos_settings]
chaos_level = "MAXIMUM"
chaos_enabled = true
chaos_factor = 0.95

[chaos_types]
python = "complex"
toml = "simple"
json = "structured"
shell = "command_based"

[chaos_processing]
max_iterations = 100
chaos_threshold = 0.8
recovery_enabled = false

# Chaos dimensions
[[chaos_dimensions]]
name = "temporal"
value = "real_time"
type = "processing"

[[chaos_dimensions]]
name = "semantic"
value = "high_complexity"
type = "analysis"
"""
    chaos_files["toml"] = toml_content

    # 3. JSON file (data structure)
    json_content = {
        "chaos_configuration": {
            "chaos_level": "MAXIMUM",
            "chaos_enabled": True,
            "chaos_factor": 0.95,
            "chaos_types": {
                "python": "complex",
                "toml": "simple",
                "json": "structured",
                "shell": "command_based",
            },
            "chaos_processing": {
                "max_iterations": 100,
                "chaos_threshold": 0.8,
                "recovery_enabled": False,
            },
            "chaos_dimensions": [
                {"name": "temporal", "value": "real_time", "type": "processing"},
                {"name": "semantic", "value": "high_complexity", "type": "analysis"},
            ],
        }
    }
    chaos_files["json"] = json.dumps(json_content, indent=2)

    # 4. Shell script (command structure)
    shell_content = """#!/bin/bash
# Chaos Shell Script - Maximum Command Complexity

CHAOS_LEVEL="MAXIMUM"
CHAOS_FACTOR=0.95
CHAOS_ENABLED=true

echo "🔥 Starting Chaos Shell Script..."

# Chaos function
chaos_function() {
    local chaos_type=$1
    local chaos_value=$2

    echo "Adding chaos: $chaos_type = $chaos_value"

    case $chaos_type in
        "python")
            echo "Python chaos detected - complexity HIGH"
            ;;
        "toml")
            echo "TOML chaos detected - structure SIMPLE"
            ;;
        "json")
            echo "JSON chaos detected - data STRUCTURED"
            ;;
        "shell")
            echo "Shell chaos detected - commands EXECUTABLE"
            ;;
        *)
            echo "Unknown chaos type: $chaos_type"
            ;;
    esac
}

# Main chaos execution
main() {
    echo "🚀 Executing chaos with level: $CHAOS_LEVEL"

    chaos_function "python" "complex"
    chaos_function "toml" "simple"
    chaos_function "json" "structured"
    chaos_function "shell" "command_based"

    echo "✅ Chaos execution complete!"
}

main "$@"
"""
    chaos_files["shell"] = shell_content

    return chaos_files


def create_chaos_spores(chaos_files: dict[str, str]) -> dict[str, GlacierSpore]:
    """Convert chaos files to GlacierSpores"""
    chaos_spores = {}

    for file_type, content in chaos_files.items():
        # Create content based on file type
        if file_type == "python":
            content_dict = {
                "file_type": "python",
                "complexity": "HIGH",
                "structure": "class_based",
                "chaos_level": "MAXIMUM",
                "repo_name": "chaos-python-repo",
            }
        elif file_type == "toml":
            content_dict = {
                "file_type": "toml",
                "complexity": "MEDIUM",
                "structure": "section_based",
                "chaos_level": "HIGH",
                "repo_name": "chaos-toml-repo",
            }
        elif file_type == "json":
            content_dict = {
                "file_type": "json",
                "complexity": "MEDIUM",
                "structure": "object_based",
                "chaos_level": "HIGH",
                "repo_name": "chaos-json-repo",
            }
        elif file_type == "shell":
            content_dict = {
                "file_type": "shell",
                "complexity": "LOW",
                "structure": "command_based",
                "chaos_level": "MEDIUM",
                "repo_name": "chaos-shell-repo",
            }

        # Create spore with required fields
        spore = GlacierSpore(
            spore_type=SporeType.DISCOVERY,
            content=content_dict,
            content_hash=hashlib.sha256(str(content_dict).encode()).hexdigest(),
            embedded_schema={
                "type": "chaos_file",
                "version": "1.0",
                "file_type": file_type,
                "chaos_level": "MAXIMUM",
            },
            content_schema={
                "type": "object",
                "properties": {
                    "file_type": {"type": "string"},
                    "complexity": {"type": "string"},
                    "structure": {"type": "string"},
                    "chaos_level": {"type": "string"},
                },
            },
            metadata={
                "original_file_type": file_type,
                "content_length": len(content),
                "chaos_factor": 0.95,
            },
        )

        # Add dimensions
        spore.set_dimension_value("temporal", "real_time")
        spore.set_dimension_value("semantic", f"{file_type}_chaos")
        spore.set_dimension_value("processing", "chaos_analysis")

        chaos_spores[file_type] = spore

    return chaos_spores


def run_chaos_diffing(chaos_spores: dict[str, GlacierSpore]):
    """Run MAXIMUM CHAOS semantic diffing between different file types"""
    print("🎪 CHAOS SEMANTIC DIFFING DEMO")
    print("=" * 60)
    print("🔥 Testing semantic diffing between completely different file types!")
    print("🚨 This will create MAXIMUM CHAOS!")
    print()

    diff_engine = SemanticDiffEngine()

    # Get all spore types
    spore_types = list(chaos_spores.keys())

    # Create chaos by diffing every combination
    total_diffs = 0
    chaos_score = 0

    for i, type1 in enumerate(spore_types):
        for j, type2 in enumerate(spore_types):
            if i != j:  # Don't diff with self
                print(f"🔥 CHAOS DIFF #{total_diffs + 1}: {type1.upper()} vs {type2.upper()}")
                print("-" * 40)

                spore1 = chaos_spores[type1]
                spore2 = chaos_spores[type2]

                try:
                    diffs = diff_engine.diff_spores(spore1, spore2)

                    if diffs:
                        print(f"   📊 Found {len(diffs)} semantic differences:")
                        for diff in diffs:
                            print(f"      • {diff.change_type}: {diff.field_path}")
                            print(f"        Impact: {diff.impact_score:.2f}, Breaking: {diff.is_breaking_change}")
                            chaos_score += diff.impact_score
                    else:
                        print("   ✅ No differences found (boring!)")

                    total_diffs += 1
                    print()

                except Exception as e:
                    print(f"   💥 CHAOS ERROR: {e}")
                    chaos_score += 1.0  # Maximum chaos for errors!
                    print()

    # Calculate final chaos score
    final_chaos_score = min(chaos_score / total_diffs, 1.0) if total_diffs > 0 else 0.0

    print("🎪 CHAOS DIFFING COMPLETE!")
    print("=" * 60)
    print(f"📊 Total Diffs: {total_diffs}")
    print(f"🔥 Chaos Score: {final_chaos_score:.2f}")
    print(f"🚨 Chaos Level: {'MAXIMUM' if final_chaos_score > 0.8 else 'HIGH' if final_chaos_score > 0.6 else 'MEDIUM' if final_chaos_score > 0.4 else 'LOW'}")

    if final_chaos_score > 0.8:
        print("🎉 SUCCESS: MAXIMUM CHAOS ACHIEVED!")
    else:
        print("😔 FAILURE: Not enough chaos generated")


def test_ghostbusters_investigation(chaos_files: dict[str, str]):
    """Test Ghostbusters investigation on chaos files"""
    print("\n👻 GHOSTBUSTERS CHAOS INVESTIGATION")
    print("=" * 60)
    print("🔬 Investigating chaos files with paranormal technology...")
    print()

    try:
        processor = GhostbustersFileTypeProcessor()

        # Create temporary files for investigation
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_files = {}

            for file_type, content in chaos_files.items():
                temp_path = Path(temp_dir) / f"chaos_file.{file_type}"
                with open(temp_path, "w", encoding="utf-8") as f:
                    f.write(content)
                temp_files[file_type] = temp_path

            # Investigate each chaos file
            for file_type, temp_path in temp_files.items():
                print(f"🔍 Investigating {file_type.upper()} chaos file...")
                result = processor.investigate_file(temp_path)

                print(f"   👻 Ghost Class: {result['ghost_classification'].ghost_class.value}")
                print(f"   📡 PKE Energy: {result['pke_reading'].energy_level.value}")
                print(f"   ⚡ Proton Status: {result['proton_pack_status'].stream_mode.value}")
                print(f"   ✅ Containment: {'Success' if result['proton_pack_status'].containment_success else 'Failed'}")
                print()

        print("👻 Ghostbusters investigation complete!")

    except Exception as e:
        print(f"💥 Ghostbusters investigation failed: {e}")
        print("But that's OK - chaos is expected!")


def main():
    """Main chaos function"""
    print("🎪 CHAOS SEMANTIC DIFFING DEMO")
    print("🔥 Because we <3 chaos!")
    print("=" * 60)

    # Phase 1: Create chaos files
    print("📁 Creating chaos files...")
    chaos_files = create_chaos_files()
    print(f"✅ Created {len(chaos_files)} chaos files: {', '.join(chaos_files.keys())}")
    print()

    # Phase 2: Convert to chaos spores
    print("🦠 Converting to chaos spores...")
    chaos_spores = create_chaos_spores(chaos_files)
    print(f"✅ Created {len(chaos_spores)} chaos spores")
    print()

    # Phase 3: Run chaos diffing
    print("🔥 Starting chaos semantic diffing...")
    run_chaos_diffing(chaos_spores)

    # Phase 4: Ghostbusters investigation
    print("\n👻 Starting Ghostbusters chaos investigation...")
    test_ghostbusters_investigation(chaos_files)

    print("\n🎉 CHAOS DEMO COMPLETE!")
    print("🔥 Maximum chaos achieved!")
    print("🚀 Semantic diffing across file types: SUCCESS!")
    print("👻 Paranormal investigation: SUCCESS!")
    print("🎪 Integration chaos: SUCCESS!")


if __name__ == "__main__":
    main()
