#!/usr/bin/env python3
"""
Module Detection System - Phase 2 of Mass Reverse Engineering

Purpose: Group related Python files into logical modules and create aggregated models
Graph API Level: 2
Projection System: module_detection
"""

import json
import re
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Set


@dataclass
class ModuleInfo:
    """Information about a detected module"""

    name: str
    files: list[Path]
    dependencies: set[str]
    total_lines: int
    total_classes: int
    total_functions: int
    total_imports: int
    module_type: str  # 'single_file', 'multi_file', 'package'
    confidence_score: float  # 0.0 to 1.0


class ModuleDetector:
    """Detect logical modules from Python files"""

    def __init__(self, workspace_path: str = "."):
        self.workspace_path = Path(workspace_path)
        self.python_files: list[Path] = []
        self.modules: dict[str, ModuleInfo] = {}

        # Module detection patterns
        self.module_patterns = {
            "test": r"(test_|_test\.py|tests?/)",
            "script": r"(script|tool|utility|cli)",
            "core": r"(core|main|app|application)",
            "model": r"(model|data|schema|entity)",
            "service": r"(service|api|client|handler)",
            "config": r"(config|settings|conf)",
            "utils": r"(util|helper|common|shared)",
        }

        # Import-based dependency patterns
        self.dependency_patterns = {
            "relative_import": r"^from \.(\w+)",
            "absolute_import": r"^from (\w+)",
            "import_statement": r"^import (\w+)",
        }

    def discover_python_files(self) -> list[Path]:
        """Discover all Python files in the workspace"""
        print("🔍 Discovering Python files...")

        python_files: list[Path] = []
        for pattern in ["**/*.py", "**/*.pyi"]:
            python_files.extend(self.workspace_path.glob(pattern))

        # Filter out common exclusions
        exclusions = {
            "__pycache__",
            ".git",
            ".venv",
            "venv",
            "env",
            "node_modules",
            "build",
            "dist",
            ".pytest_cache",
        }

        filtered_files = []
        for file_path in python_files:
            if not any(exclusion in str(file_path) for exclusion in exclusions):
                filtered_files.append(file_path)

        self.python_files = sorted(filtered_files)
        print(f"✅ Found {len(self.python_files)} Python files")
        return self.python_files

    def analyze_file_relationships(self) -> dict[str, set[str]]:
        """Analyze relationships between files based on imports and naming"""
        print("🔗 Analyzing file relationships...")

        relationships = defaultdict(set)

        for file_path in self.python_files:
            try:
                content = file_path.read_text(encoding="utf-8")
                file_name = file_path.stem

                # Find imports in this file
                imports = self._extract_imports(content)

                # Find files that this file imports
                for imp in imports:
                    for other_file in self.python_files:
                        if other_file.stem == imp or other_file.name == f"{imp}.py":
                            relationships[file_name].add(other_file.stem)

                # Find files with similar names (potential module grouping)
                for other_file in self.python_files:
                    if other_file != file_path:
                        similarity = self._calculate_name_similarity(file_name, other_file.stem)
                        if similarity > 0.7:  # High similarity threshold
                            relationships[file_name].add(other_file.stem)

            except Exception as e:
                print(f"⚠️ Error analyzing {file_path}: {e}")
                continue

        print(f"✅ Analyzed relationships for {len(relationships)} files")
        return dict(relationships)

    def _extract_imports(self, content: str) -> set[str]:
        """Extract import statements from file content"""
        imports = set()

        for line in content.split("\n"):
            line = line.strip()

            # Skip comments and empty lines
            if not line or line.startswith("#"):
                continue

            # Check for import patterns
            for pattern_name, pattern in self.dependency_patterns.items():
                match = re.match(pattern, line)
                if match:
                    module_name = match.group(1)
                    if module_name and not module_name.startswith("."):
                        imports.add(module_name)

        return imports

    def _calculate_name_similarity(self, name1: str, name2: str) -> float:
        """Calculate similarity between two file names"""
        # Simple similarity based on common prefixes/suffixes
        if name1 == name2:
            return 1.0

        # Check for common prefixes
        min_len = min(len(name1), len(name2))
        common_prefix = 0
        for i in range(min_len):
            if name1[i] == name2[i]:
                common_prefix += 1
            else:
                break

        # Check for common suffixes
        common_suffix = 0
        for i in range(1, min_len + 1):
            if name1[-i] == name2[-i]:
                common_suffix += 1
            else:
                break

        # Calculate similarity score
        total_similarity = common_prefix + common_suffix
        max_length = max(len(name1), len(name2))

        return total_similarity / max_length if max_length > 0 else 0.0

    def detect_modules(self) -> dict[str, ModuleInfo]:
        """Detect logical modules from Python files"""
        print("🧩 Detecting logical modules...")

        # First analyze relationships
        relationships = self.analyze_file_relationships()

        # Group files into modules
        module_groups = self._group_files_into_modules(relationships)

        # Create ModuleInfo objects
        for module_name, files in module_groups.items():
            module_info = self._create_module_info(module_name, files)
            self.modules[module_name] = module_info

        print(f"✅ Detected {len(self.modules)} logical modules")
        return self.modules

    def _group_files_into_modules(self, relationships: dict[str, set[str]]) -> dict[str, list[Path]]:
        """Group files into logical modules based on relationships"""
        module_groups = defaultdict(list)
        processed_files = set()

        # Start with single files that have no strong relationships
        for file_path in self.python_files:
            file_name = file_path.stem

            if file_name in processed_files:
                continue

            # Check if this file has strong relationships
            related_files = relationships.get(file_name, set())

            if not related_files:
                # Single file module
                module_name = self._generate_module_name(file_path)
                module_groups[module_name].append(file_path)
                processed_files.add(file_name)
            else:
                # Multi-file module
                module_name = self._generate_module_name(file_path)
                module_files = [file_path]

                # Add related files
                for related_name in related_files:
                    related_file = next((f for f in self.python_files if f.stem == related_name), None)
                    if related_file and related_file.stem not in processed_files:
                        module_files.append(related_file)
                        processed_files.add(related_file.stem)

                module_groups[module_name] = module_files
                processed_files.add(file_name)

        return dict(module_groups)

    def _generate_module_name(self, file_path: Path) -> str:
        """Generate a logical module name from file path"""
        file_name = file_path.stem

        # Check for common module patterns
        for pattern_name, pattern in self.module_patterns.items():
            if re.search(pattern, file_name, re.IGNORECASE):
                return f"{pattern_name}_{file_name}"

        # Check directory structure for clues
        parent_dir = file_path.parent.name
        if parent_dir and parent_dir not in ["scripts", "src", "tests"]:
            return f"{parent_dir}_{file_name}"

        # Default to file name
        return file_name

    def _create_module_info(self, module_name: str, files: list[Path]) -> ModuleInfo:
        """Create ModuleInfo object for a module"""
        total_lines = 0
        total_classes = 0
        total_functions = 0
        total_imports = 0
        dependencies = set()

        # Analyze each file in the module
        for file_path in files:
            try:
                content = file_path.read_text(encoding="utf-8")
                lines = content.split("\n")

                total_lines += len(lines)
                total_classes += len(re.findall(r"^class\s+\w+", content, re.MULTILINE))
                total_functions += len(re.findall(r"^def\s+\w+", content, re.MULTILINE))
                total_imports += len(re.findall(r"^(?:from|import)\s+\w+", content, re.MULTILINE))

                # Extract dependencies
                file_deps = self._extract_imports(content)
                dependencies.update(file_deps)

            except Exception as e:
                print(f"⚠️ Error analyzing {file_path}: {e}")
                continue

        # Determine module type
        if len(files) == 1:
            module_type = "single_file"
            confidence_score = 0.9
        elif len(files) <= 3:
            module_type = "multi_file"
            confidence_score = 0.8
        else:
            module_type = "package"
            confidence_score = 0.7

        return ModuleInfo(
            name=module_name,
            files=files,
            dependencies=dependencies,
            total_lines=total_lines,
            total_classes=total_classes,
            total_functions=total_functions,
            total_imports=total_imports,
            module_type=module_type,
            confidence_score=confidence_score,
        )

    def generate_module_summary(self) -> dict[str, Any]:
        """Generate summary of all detected modules"""
        summary: dict[str, Any] = {
            "workspace_path": str(self.workspace_path),
            "total_files": len(self.python_files),
            "total_modules": len(self.modules),
            "modules": {},
            "statistics": {
                "total_lines": sum(m.total_lines for m in self.modules.values()),
                "total_classes": sum(m.total_classes for m in self.modules.values()),
                "total_functions": sum(m.total_functions for m in self.modules.values()),
                "total_imports": sum(m.total_imports for m in self.modules.values()),
            },
        }

        # Add module details
        for module_name, module_info in self.modules.items():
            summary["modules"][module_name] = {
                "name": module_info.name,
                "files": [str(f) for f in module_info.files],
                "dependencies": list(module_info.dependencies),
                "total_lines": module_info.total_lines,
                "total_classes": module_info.total_classes,
                "total_functions": module_info.total_functions,
                "total_imports": module_info.total_imports,
                "module_type": module_info.module_type,
                "confidence_score": module_info.confidence_score,
                "file_count": len(module_info.files),
            }

        return summary

    def save_module_summary(self, output_path: str = "module_detection_summary.json") -> str:
        """Save module detection summary to JSON file"""
        summary = self.generate_module_summary()

        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(summary, f, indent=2, ensure_ascii=False)

        print(f"💾 Module summary saved to {output_path}")
        return output_path


def main() -> None:
    """Main entry point for module detection"""
    print("🚀 Module Detection System - Phase 2")
    print("=" * 50)

    # Initialize detector
    detector = ModuleDetector(".")

    # Discover Python files
    detector.discover_python_files()

    # Detect modules
    modules = detector.detect_modules()

    # Generate and save summary
    summary_path = detector.save_module_summary()

    # Display results
    print("\n📊 Module Detection Results:")
    print("-" * 30)

    for module_name, module_info in modules.items():
        print(f"📦 {module_name}")
        print(f"   Type: {module_info.module_type}")
        print(f"   Files: {len(module_info.files)}")
        print(f"   Lines: {module_info.total_lines}")
        print(f"   Classes: {module_info.total_classes}")
        print(f"   Functions: {module_info.total_functions}")
        print(f"   Confidence: {module_info.confidence_score:.2f}")
        print()

    print(f"🎯 Phase 2 Complete! Detected {len(modules)} logical modules")
    print(f"📁 Summary saved to: {summary_path}")


if __name__ == "__main__":
    main()
