#!/usr/bin/env python3
"""
Heuristic File Type Processor - Dynamic Discovery and Exception Mapping

This module implements a heuristic approach to file type discovery that can:
1. Handle parsing exceptions gracefully
2. Heuristically classify unknown file types
3. Map exceptions to recovery strategies
4. Learn from failures to improve future classification
5. Support TOML and other artifact types with semantic diffing
"""

import ast
import configparser
import hashlib
import json
import os
import re
import xml.etree.ElementTree as ET
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Callable, Optional

import tomllib
import yaml


class FileTypeConfidence(Enum):
    """Confidence levels for heuristic file type detection"""

    CERTAIN = "certain"  # 100% confidence (known extension + successful parse)
    HIGH = "high"  # 80-99% confidence (strong heuristics)
    MEDIUM = "medium"  # 60-79% confidence (moderate heuristics)
    LOW = "low"  # 40-59% confidence (weak heuristics)
    UNKNOWN = "unknown"  # <40% confidence (cannot determine)


class DiscoveryStrategy(Enum):
    """Strategies for discovering file types"""

    EXTENSION_BASED = "extension_based"
    CONTENT_PATTERN = "content_pattern"
    STRUCTURE_ANALYSIS = "structure_analysis"
    MIME_TYPE = "mime_type"
    MAGIC_BYTES = "magic_bytes"
    HEURISTIC_FALLBACK = "heuristic_fallback"


@dataclass
class HeuristicPattern:
    """A pattern used for heuristic file type detection"""

    pattern: str
    confidence: float
    file_type: str
    description: str
    regex: Optional[re.Pattern] = None

    def __post_init__(self):
        if self.regex is None:
            self.regex = re.compile(self.pattern, re.MULTILINE | re.IGNORECASE)


@dataclass
class FileTypeDiscovery:
    """Result of file type discovery"""

    file_path: Path
    detected_type: str
    confidence: FileTypeConfidence
    confidence_score: float
    discovery_strategy: DiscoveryStrategy
    parsing_success: bool
    parsing_errors: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)
    heuristic_patterns: list[HeuristicPattern] = field(default_factory=list)


@dataclass
class ExceptionMapping:
    """Mapping of parsing exceptions to recovery strategies"""

    exception_type: str
    exception_message: str
    file_type: str
    recovery_strategy: str
    success_rate: float
    usage_count: int = 0


class HeuristicFileTypeProcessor:
    """
    Heuristic processor for dynamic file type discovery and exception handling
    """

    def __init__(self):
        self.known_extensions = {
            ".py": "python",
            ".json": "json",
            ".yaml": "yaml",
            ".yml": "yaml",
            ".toml": "toml",
            ".ini": "ini",
            ".cfg": "ini",
            ".xml": "xml",
            ".md": "markdown",
            ".sh": "shell",
            ".bash": "shell",
            ".zsh": "shell",
            ".dockerfile": "dockerfile",
            ".makefile": "makefile",
            ".mk": "makefile",
        }

        self.heuristic_patterns = self._initialize_heuristic_patterns()
        self.exception_mappings = self._initialize_exception_mappings()
        self.learning_history = []

    def _initialize_heuristic_patterns(self) -> list[HeuristicPattern]:
        """Initialize heuristic patterns for file type detection"""
        return [
            # Python patterns
            HeuristicPattern(r"^#!/usr/bin/env python", 0.95, "python", "Python shebang"),
            HeuristicPattern(r"^import\s+\w+", 0.90, "python", "Python import statement"),
            HeuristicPattern(r"^from\s+\w+\s+import", 0.90, "python", "Python from import"),
            HeuristicPattern(r"^def\s+\w+\s*\(", 0.85, "python", "Python function definition"),
            HeuristicPattern(r"^class\s+\w+", 0.85, "python", "Python class definition"),
            # JSON patterns
            HeuristicPattern(r"^\s*\{", 0.80, "json", "JSON object start"),
            HeuristicPattern(r"^\s*\[", 0.80, "json", "JSON array start"),
            HeuristicPattern(r'"[^"]*"\s*:', 0.85, "json", "JSON key-value pattern"),
            # YAML patterns
            HeuristicPattern(r"^\s*[\w-]+\s*:", 0.75, "yaml", "YAML key-value pattern"),
            HeuristicPattern(r"^\s*-\s+", 0.80, "yaml", "YAML list item"),
            HeuristicPattern(r"^\s*#", 0.60, "yaml", "YAML comment"),
            # TOML patterns
            HeuristicPattern(r"^\s*\[[\w.]+\]", 0.90, "toml", "TOML section header"),
            HeuristicPattern(r'^\s*[\w-]+\s*=\s*["\']?[^"\']*["\']?', 0.85, "toml", "TOML key-value"),
            HeuristicPattern(r"^\s*#.*$", 0.70, "toml", "TOML comment"),
            # INI patterns
            HeuristicPattern(r"^\s*\[[\w\s]+\]", 0.85, "ini", "INI section header"),
            HeuristicPattern(r"^\s*\w+\s*=", 0.80, "ini", "INI key-value"),
            HeuristicPattern(r"^\s*;.*$", 0.70, "ini", "INI comment"),
            # XML patterns
            HeuristicPattern(r"^\s*<\?xml", 0.95, "xml", "XML declaration"),
            HeuristicPattern(r"^\s*<[\w-]+", 0.85, "xml", "XML tag start"),
            HeuristicPattern(r"</[\w-]+>", 0.85, "xml", "XML tag end"),
            # Markdown patterns
            HeuristicPattern(r"^#\s+", 0.90, "markdown", "Markdown heading"),
            HeuristicPattern(r"^\*\s+", 0.80, "markdown", "Markdown list"),
            HeuristicPattern(r"^\s*```", 0.85, "markdown", "Markdown code block"),
            # Shell patterns
            HeuristicPattern(r"^#!/bin/(bash|sh|zsh)", 0.95, "shell", "Shell shebang"),
            HeuristicPattern(r"^\w+\(\)\s*\{", 0.85, "shell", "Shell function"),
            HeuristicPattern(r"^\w+=\$\(", 0.80, "shell", "Shell command substitution"),
            # Dockerfile patterns
            HeuristicPattern(r"^FROM\s+", 0.95, "dockerfile", "Docker FROM instruction"),
            HeuristicPattern(r"^RUN\s+", 0.90, "dockerfile", "Docker RUN instruction"),
            HeuristicPattern(r"^COPY\s+", 0.90, "dockerfile", "Docker COPY instruction"),
            # Makefile patterns
            HeuristicPattern(r"^\w+:", 0.80, "makefile", "Makefile target"),
            HeuristicPattern(r"^\t", 0.75, "makefile", "Makefile tab indentation"),
            HeuristicPattern(r"^\s*\.PHONY:", 0.90, "makefile", "Makefile .PHONY declaration"),
        ]

    def _initialize_exception_mappings(self) -> list[ExceptionMapping]:
        """Initialize exception mappings for recovery strategies"""
        return [
            # JSON exceptions
            ExceptionMapping(
                "json.JSONDecodeError",
                "Expecting property name enclosed in double quotes",
                "json",
                "fix_quotes_and_validate",
                0.85,
            ),
            ExceptionMapping(
                "json.JSONDecodeError",
                "Expecting value",
                "json",
                "fix_syntax_and_validate",
                0.80,
            ),
            # YAML exceptions
            ExceptionMapping(
                "yaml.YAMLError",
                "mapping values are not allowed here",
                "yaml",
                "fix_indentation_and_validate",
                0.90,
            ),
            ExceptionMapping(
                "yaml.YAMLError",
                "expected <block end>",
                "yaml",
                "fix_structure_and_validate",
                0.85,
            ),
            # TOML exceptions
            ExceptionMapping(
                "tomllib.TOMLDecodeError",
                "Invalid TOML",
                "toml",
                "fix_syntax_and_validate",
                0.80,
            ),
            # XML exceptions
            ExceptionMapping(
                "xml.etree.ElementTree.ParseError",
                "syntax error",
                "xml",
                "fix_xml_syntax_and_validate",
                0.85,
            ),
        ]

    def discover_file_type(self, file_path: Path) -> FileTypeDiscovery:
        """
        Discover file type using multiple strategies with fallback to heuristics
        """
        # Strategy 1: Extension-based detection
        if file_path.suffix in self.known_extensions:
            discovery = self._extension_based_discovery(file_path)
            if discovery.parsing_success:
                return discovery

        # Strategy 2: Content pattern analysis
        discovery = self._content_pattern_discovery(file_path)
        if discovery.confidence in [
            FileTypeConfidence.HIGH,
            FileTypeConfidence.CERTAIN,
        ]:
            return discovery

        # Strategy 3: Structure analysis
        discovery = self._structure_analysis_discovery(file_path)
        if discovery.confidence in [FileTypeConfidence.MEDIUM, FileTypeConfidence.HIGH]:
            return discovery

        # Strategy 4: Heuristic fallback
        return self._heuristic_fallback_discovery(file_path)

    def _extension_based_discovery(self, file_path: Path) -> FileTypeDiscovery:
        """Discover file type based on extension and attempt parsing"""
        file_type = self.known_extensions[file_path.suffix]
        parsing_success, errors = self._attempt_parsing(file_path, file_type)

        return FileTypeDiscovery(
            file_path=file_path,
            detected_type=file_type,
            confidence=(FileTypeConfidence.CERTAIN if parsing_success else FileTypeConfidence.HIGH),
            confidence_score=1.0 if parsing_success else 0.8,
            discovery_strategy=DiscoveryStrategy.EXTENSION_BASED,
            parsing_success=parsing_success,
            parsing_errors=errors,
        )

    def _content_pattern_discovery(self, file_path: Path) -> FileTypeDiscovery:
        """Discover file type based on content patterns"""
        try:
            with open(file_path, encoding="utf-8") as f:
                content = f.read()
        except Exception:
            return self._create_unknown_discovery(file_path)

        # Score each pattern
        pattern_scores = {}
        for pattern in self.heuristic_patterns:
            matches = pattern.regex.findall(content)
            if matches:
                score = min(len(matches) * pattern.confidence, 1.0)
                if pattern.file_type not in pattern_scores:
                    pattern_scores[pattern.file_type] = []
                pattern_scores[pattern.file_type].append((pattern, score))

        if not pattern_scores:
            return self._create_unknown_discovery(file_path)

        # Find the best match
        best_type = max(pattern_scores.keys(), key=lambda t: max(s[1] for s in pattern_scores[t]))
        best_score = max(s[1] for s in pattern_scores[best_type])

        # Attempt parsing with discovered type
        parsing_success, errors = self._attempt_parsing(file_path, best_type)

        # Determine confidence
        if best_score >= 0.9:
            confidence = FileTypeConfidence.HIGH
        elif best_score >= 0.7:
            confidence = FileTypeConfidence.MEDIUM
        else:
            confidence = FileTypeConfidence.LOW

        return FileTypeDiscovery(
            file_path=file_path,
            detected_type=best_type,
            confidence=confidence,
            confidence_score=best_score,
            discovery_strategy=DiscoveryStrategy.CONTENT_PATTERN,
            parsing_success=parsing_success,
            parsing_errors=errors,
            heuristic_patterns=[p for p, _ in pattern_scores[best_type]],
        )

    def _structure_analysis_discovery(self, file_path: Path) -> FileTypeDiscovery:
        """Discover file type based on structural analysis"""
        try:
            with open(file_path, encoding="utf-8") as f:
                lines = f.readlines()
        except Exception:
            return self._create_unknown_discovery(file_path)

        # Analyze line structure patterns
        structure_scores = {}

        # Check for consistent indentation patterns
        indent_patterns = self._analyze_indentation_patterns(lines)
        if indent_patterns:
            structure_scores["yaml"] = indent_patterns.get("yaml", 0)
            structure_scores["python"] = indent_patterns.get("python", 0)

        # Check for bracket patterns
        bracket_patterns = self._analyze_bracket_patterns(lines)
        if bracket_patterns:
            structure_scores["json"] = bracket_patterns.get("json", 0)
            structure_scores["xml"] = bracket_patterns.get("xml", 0)

        if not structure_scores:
            return self._create_unknown_discovery(file_path)

        best_type = max(structure_scores.keys(), key=structure_scores.get)
        best_score = structure_scores[best_type]

        # Attempt parsing
        parsing_success, errors = self._attempt_parsing(file_path, best_type)

        confidence = FileTypeConfidence.MEDIUM if best_score >= 0.6 else FileTypeConfidence.LOW

        return FileTypeDiscovery(
            file_path=file_path,
            detected_type=best_type,
            confidence=confidence,
            confidence_score=best_score,
            discovery_strategy=DiscoveryStrategy.STRUCTURE_ANALYSIS,
            parsing_success=parsing_success,
            parsing_errors=errors,
        )

    def _heuristic_fallback_discovery(self, file_path: Path) -> FileTypeDiscovery:
        """Final fallback using general heuristics"""
        try:
            with open(file_path, encoding="utf-8") as f:
                content = f.read()
        except Exception:
            return self._create_unknown_discovery(file_path)

        # General heuristics
        if content.strip().startswith("{") or content.strip().startswith("["):
            detected_type = "json"
            confidence_score = 0.5
        elif "=" in content and "[" in content:
            detected_type = "ini"
            confidence_score = 0.4
        elif content.count("#") > content.count("//") * 2:
            detected_type = "shell"
            confidence_score = 0.3
        else:
            detected_type = "generic"
            confidence_score = 0.1

        return FileTypeDiscovery(
            file_path=file_path,
            detected_type=detected_type,
            confidence=FileTypeConfidence.LOW,
            confidence_score=confidence_score,
            discovery_strategy=DiscoveryStrategy.HEURISTIC_FALLBACK,
            parsing_success=False,
            parsing_errors=["Heuristic fallback - no parsing attempted"],
        )

    def _create_unknown_discovery(self, file_path: Path) -> FileTypeDiscovery:
        """Create a discovery result for unknown file types"""
        return FileTypeDiscovery(
            file_path=file_path,
            detected_type="unknown",
            confidence=FileTypeConfidence.UNKNOWN,
            confidence_score=0.0,
            discovery_strategy=DiscoveryStrategy.HEURISTIC_FALLBACK,
            parsing_success=False,
            parsing_errors=["File type could not be determined"],
        )

    def _attempt_parsing(self, file_path: Path, file_type: str) -> tuple[bool, list[str]]:
        """Attempt to parse a file with the given type"""
        try:
            if file_type == "python":
                with open(file_path, encoding="utf-8") as f:
                    ast.parse(f.read())
                return True, []

            if file_type == "json":
                with open(file_path, encoding="utf-8") as f:
                    json.load(f)
                return True, []

            if file_type == "yaml":
                with open(file_path, encoding="utf-8") as f:
                    yaml.safe_load(f)
                return True, []

            if file_type == "toml":
                with open(file_path, "rb") as f:
                    tomllib.load(f)
                return True, []

            if file_type == "ini":
                config = configparser.ConfigParser()
                config.read(file_path)
                return True, []

            if file_type == "xml":
                ET.parse(file_path)
                return True, []

            return False, [f"No parser available for {file_type}"]

        except Exception as e:
            # Map exception to recovery strategy
            recovery_strategy = self._map_exception_to_recovery(str(type(e)), str(e), file_type)
            return False, [
                f"Parse error: {e}",
                f"Recovery strategy: {recovery_strategy}",
            ]

    def _map_exception_to_recovery(self, exception_type: str, exception_message: str, file_type: str) -> str:
        """Map parsing exceptions to recovery strategies"""
        for mapping in self.exception_mappings:
            if mapping.exception_type in exception_type and mapping.file_type == file_type:
                # Update usage count and success rate
                mapping.usage_count += 1
                return mapping.recovery_strategy

        return "manual_inspection_required"

    def _analyze_indentation_patterns(self, lines: list[str]) -> dict[str, float]:
        """Analyze indentation patterns to infer file type"""
        patterns = {"yaml": 0, "python": 0}

        yaml_score = 0
        python_score = 0
        total_lines = len(lines)

        for line in lines:
            stripped = line.strip()
            if not stripped or stripped.startswith("#"):
                continue

            indent = len(line) - len(line.lstrip())

            # YAML patterns: consistent 2-space indentation, key-value pairs
            if indent % 2 == 0 and ":" in stripped and not stripped.endswith(":"):
                yaml_score += 1

            # Python patterns: 4-space indentation, function/class definitions
            if indent % 4 == 0 and (stripped.startswith(("def ", "class "))):
                python_score += 1

        if total_lines > 0:
            patterns["yaml"] = yaml_score / total_lines
            patterns["python"] = python_score / total_lines

        return patterns

    def _analyze_bracket_patterns(self, lines: list[str]) -> dict[str, float]:
        """Analyze bracket patterns to infer file type"""
        patterns = {"json": 0, "xml": 0}

        json_score = 0
        xml_score = 0
        total_lines = len(lines)

        for line in lines:
            stripped = line.strip()
            if not stripped:
                continue

            # JSON patterns: curly braces, square brackets
            if "{" in stripped or "}" in stripped or "[" in stripped or "]" in stripped:
                json_score += 1

            # XML patterns: angle brackets, tags
            if "<" in stripped and ">" in stripped:
                xml_score += 1

        if total_lines > 0:
            patterns["json"] = json_score / total_lines
            patterns["xml"] = xml_score / total_lines

        return patterns

    def learn_from_discovery(self, discovery: FileTypeDiscovery, actual_type: str):
        """Learn from discovery results to improve future classifications"""
        learning_entry = {
            "file_path": str(discovery.file_path),
            "detected_type": discovery.detected_type,
            "actual_type": actual_type,
            "confidence": discovery.confidence.value,
            "confidence_score": discovery.confidence_score,
            "strategy": discovery.discovery_strategy.value,
            "success": discovery.detected_type == actual_type,
        }

        self.learning_history.append(learning_entry)

        # Update pattern confidence based on success
        if discovery.heuristic_patterns:
            for pattern in discovery.heuristic_patterns:
                if discovery.detected_type == actual_type:
                    pattern.confidence = min(pattern.confidence + 0.05, 1.0)
                else:
                    pattern.confidence = max(pattern.confidence - 0.1, 0.1)

    def get_discovery_statistics(self) -> dict[str, Any]:
        """Get statistics about discovery performance"""
        if not self.learning_history:
            return {"total_discoveries": 0, "success_rate": 0.0}

        total = len(self.learning_history)
        successful = sum(1 for entry in self.learning_history if entry["success"])
        success_rate = successful / total

        # Strategy performance
        strategy_performance = {}
        for entry in self.learning_history:
            strategy = entry["strategy"]
            if strategy not in strategy_performance:
                strategy_performance[strategy] = {"total": 0, "successful": 0}

            strategy_performance[strategy]["total"] += 1
            if entry["success"]:
                strategy_performance[strategy]["successful"] += 1

        # Calculate success rates for each strategy
        for strategy in strategy_performance:
            total_strategy = strategy_performance[strategy]["total"]
            successful_strategy = strategy_performance[strategy]["successful"]
            strategy_performance[strategy]["success_rate"] = successful_strategy / total_strategy

        return {
            "total_discoveries": total,
            "success_rate": success_rate,
            "strategy_performance": strategy_performance,
            "pattern_confidence": {p.file_type: p.confidence for p in self.heuristic_patterns},
        }


def main():
    """Demo the heuristic file type processor"""
    processor = HeuristicFileTypeProcessor()

    # Test with various file types
    test_files = [
        "scripts/one_liner_linter.py",
        "project_model_registry.json",
        "scripts/universal_ast_enhanced_linter_model.py",
        "pyproject.toml",
        "README.md",
    ]

    print("🔍 Heuristic File Type Discovery Demo")
    print("=" * 50)

    for test_file in test_files:
        if os.path.exists(test_file):
            discovery = processor.discover_file_type(Path(test_file))
            print(f"\n📁 {test_file}")
            print(f"   Type: {discovery.detected_type}")
            print(f"   Confidence: {discovery.confidence.value} ({discovery.confidence_score:.2f})")
            print(f"   Strategy: {discovery.discovery_strategy.value}")
            print(f"   Parsing: {'✅' if discovery.parsing_success else '❌'}")

            if discovery.parsing_errors:
                print(f"   Errors: {discovery.parsing_errors[0]}")

    # Show statistics
    stats = processor.get_discovery_statistics()
    print(f"\n📊 Discovery Statistics")
    print(f"   Total: {stats['total_discoveries']}")
    print(f"   Success Rate: {stats['success_rate']:.2%}")


if __name__ == "__main__":
    main()
