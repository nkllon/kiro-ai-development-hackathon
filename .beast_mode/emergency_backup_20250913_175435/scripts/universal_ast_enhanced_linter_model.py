#!/usr/bin/env python3
"""
Universal AST-Enhanced Linter Model - All File Types Support

This module extends the AST-enhanced linter to support ALL file types with
domain-specific parsers that provide semantic understanding equivalent to
Python AST parsing.

Supported File Types:
- Python: ast module
- JSON: json module with schema validation
- YAML: ruamel.yaml with structure analysis
- TOML: tomllib/tomli with semantic parsing
- INI: configparser with configuration analysis
- XML: xml.etree with DOM analysis
- Markdown: markdown parsing with structure analysis
- Shell: bash/sh/zsh with command analysis
- Dockerfile: Docker syntax analysis
- Makefile: Make syntax and dependency analysis
"""

import ast
import configparser
import io
import json
import xml.etree.ElementTree as ET
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Union


class FileType(Enum):
    """Supported file types for universal analysis"""

    PYTHON = "python"
    JSON = "json"
    YAML = "yaml"
    TOML = "toml"
    INI = "ini"
    XML = "xml"
    MARKDOWN = "markdown"
    SHELL = "shell"
    DOCKERFILE = "dockerfile"
    MAKEFILE = "makefile"
    GENERIC = "generic"


class AnalysisStrategy(Enum):
    """Different strategies for universal code analysis"""

    SYNTAX_VALIDATION = "syntax_validation"
    STRUCTURE_ANALYSIS = "structure_analysis"
    SEMANTIC_ANALYSIS = "semantic_analysis"
    PATTERN_ANALYSIS = "pattern_analysis"
    QUALITY_ANALYSIS = "quality_analysis"
    SECURITY_ANALYSIS = "security_analysis"
    CONFIGURATION_ANALYSIS = "configuration_analysis"


class IssueSeverity(Enum):
    """Severity levels for detected issues"""

    CRITICAL = "critical"
    WARNING = "warning"
    SUGGESTION = "suggestion"
    INFO = "info"


class IssueType(Enum):
    """Universal issue types across all file types"""

    # Syntax Issues
    SYNTAX_ERROR = "syntax_error"
    PARSE_ERROR = "parse_error"

    # Structure Issues
    INVALID_STRUCTURE = "invalid_structure"
    MISSING_REQUIRED_FIELD = "missing_required_field"
    UNEXPECTED_FIELD = "unexpected_field"
    DUPLICATE_KEY = "duplicate_key"

    # Quality Issues
    LINE_TOO_LONG = "line_too_long"
    MISSING_BLANK_LINES = "missing_blank_lines"
    INCONSISTENT_INDENTATION = "inconsistent_indentation"
    TRAILING_WHITESPACE = "trailing_whitespace"

    # Configuration Issues
    HARDCODED_VALUES = "hardcoded_values"
    MISSING_DEFAULTS = "missing_defaults"
    INVALID_VALUES = "invalid_values"
    SECURITY_ISSUES = "security_issues"

    # File Type Specific Issues
    PYTHON_SPECIFIC = "python_specific"
    JSON_SPECIFIC = "json_specific"
    YAML_SPECIFIC = "yaml_specific"
    TOML_SPECIFIC = "toml_specific"
    INI_SPECIFIC = "ini_specific"
    XML_SPECIFIC = "xml_specific"
    MARKDOWN_SPECIFIC = "markdown_specific"
    SHELL_SPECIFIC = "shell_specific"
    DOCKER_SPECIFIC = "docker_specific"
    MAKE_SPECIFIC = "make_specific"


class AutoFixCapability(Enum):
    """Capabilities for automatic issue fixing"""

    CAN_FIX = "can_fix"
    CAN_PARTIALLY_FIX = "can_partially_fix"
    CANNOT_FIX = "cannot_fix"
    REQUIRES_MANUAL_REVIEW = "requires_manual_review"


@dataclass
class UniversalAnalysisRule:
    """Defines a rule for universal code analysis"""

    name: str
    file_types: list[FileType]
    strategy: AnalysisStrategy
    issue_type: IssueType
    severity: IssueSeverity
    auto_fix: AutoFixCapability
    description: str
    suggestion: str
    conditions: list[Callable] = field(default_factory=list)
    fix_strategy: Optional[Callable] = None
    threshold: Optional[float] = None


@dataclass
class FileTypeParser(ABC):
    """Abstract base class for file type parsers"""

    file_type: FileType
    supported_extensions: list[str]

    @abstractmethod
    def can_parse(self, file_path: Path) -> bool:
        """Check if this parser can handle the given file"""

    @abstractmethod
    def parse(self, file_path: Path) -> dict[str, Any]:
        """Parse the file and return structured data"""

    @abstractmethod
    def validate_syntax(self, content: str) -> tuple[bool, list[Any]]:
        """Validate syntax and return (is_valid, errors)"""

    @abstractmethod
    def analyze_structure(self, parsed_data: dict[str, Any]) -> list[Any]:
        """Analyze the structure of parsed data"""

    @abstractmethod
    def analyze_semantics(self, parsed_data: dict[str, Any]) -> list[Any]:
        """Analyze semantics of parsed data"""

    @abstractmethod
    def calculate_metrics(self, parsed_data: dict[str, Any], lines: list[str]) -> list[Any]:
        """Calculate quality metrics"""


class PythonParser(FileTypeParser):
    """Python file parser using AST"""

    def __init__(self):
        super().__init__(file_type=FileType.PYTHON, supported_extensions=[".py", ".pyi", ".pyx"])

    def can_parse(self, file_path: Path) -> bool:
        return file_path.suffix in self.supported_extensions

    def parse(self, file_path: Path) -> dict[str, Any]:
        with open(file_path, encoding="utf-8") as f:
            content = f.read()

        try:
            tree = ast.parse(content)
            return {
                "ast_tree": tree,
                "content": content,
                "syntax_valid": True,
                "errors": [],
            }
        except SyntaxError as e:
            return {
                "ast_tree": None,
                "content": content,
                "syntax_valid": False,
                "errors": [e],
            }

    def validate_syntax(self, content: str) -> tuple[bool, list[Any]]:
        try:
            ast.parse(content)
            return True, []
        except SyntaxError as e:
            return False, [e]

    def analyze_structure(self, parsed_data: dict[str, Any]) -> list[Any]:
        if not parsed_data["syntax_valid"]:
            return []

        tree = parsed_data["ast_tree"]
        structure_issues = []

        # Analyze imports
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                if len(node.names) > 1:
                    structure_issues.append(
                        {
                            "type": "multiple_imports",
                            "line": getattr(node, "lineno", 1),
                            "description": "Multiple imports on one line",
                        }
                    )

        return structure_issues

    def analyze_semantics(self, parsed_data: dict[str, Any]) -> list[Any]:
        if not parsed_data["syntax_valid"]:
            return []

        tree = parsed_data["ast_tree"]
        semantic_issues = []

        # Analyze functions
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                if not ast.get_docstring(node):
                    semantic_issues.append(
                        {
                            "type": "missing_docstring",
                            "line": getattr(node, "lineno", 1),
                            "description": f"Function {node.name} missing docstring",
                        }
                    )

                if len(node.body) > 20:
                    semantic_issues.append(
                        {
                            "type": "function_too_long",
                            "line": getattr(node, "lineno", 1),
                            "description": f"Function {node.name} is too long ({len(node.body)} lines)",
                        }
                    )

        return semantic_issues

    def calculate_metrics(self, parsed_data: dict[str, Any], lines: list[str]) -> list[Any]:
        if not parsed_data["syntax_valid"]:
            return []

        tree = parsed_data["ast_tree"]
        metrics = []

        # Function count
        function_count = len([node for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)])
        metrics.append({"name": "function_count", "value": function_count, "unit": "functions"})

        # Class count
        class_count = len([node for node in ast.walk(tree) if isinstance(node, ast.ClassDef)])
        metrics.append({"name": "class_count", "value": class_count, "unit": "classes"})

        # Import count
        import_count = len([node for node in ast.walk(tree) if isinstance(node, (ast.Import, ast.ImportFrom))])
        metrics.append({"name": "import_count", "value": import_count, "unit": "imports"})

        return metrics


class JSONParser(FileTypeParser):
    """JSON file parser with schema validation"""

    def __init__(self):
        super().__init__(file_type=FileType.JSON, supported_extensions=[".json", ".jsonc", ".json5"])

    def can_parse(self, file_path: Path) -> bool:
        return file_path.suffix in self.supported_extensions

    def parse(self, file_path: Path) -> dict[str, Any]:
        with open(file_path, encoding="utf-8") as f:
            content = f.read()

        try:
            data = json.loads(content)
            return {
                "data": data,
                "content": content,
                "syntax_valid": True,
                "errors": [],
            }
        except json.JSONDecodeError as e:
            return {
                "data": None,
                "content": content,
                "syntax_valid": False,
                "errors": [e],
            }

    def validate_syntax(self, content: str) -> tuple[bool, list[Any]]:
        try:
            json.loads(content)
            return True, []
        except json.JSONDecodeError as e:
            return False, [e]

    def analyze_structure(self, parsed_data: dict[str, Any]) -> list[Any]:
        if not parsed_data["syntax_valid"]:
            return []

        data = parsed_data["data"]
        structure_issues = []

        # Check for duplicate keys (JSON doesn't allow this, but some parsers might)
        if isinstance(data, dict):
            keys = list(data.keys())
            if len(keys) != len(set(keys)):
                structure_issues.append(
                    {
                        "type": "duplicate_key",
                        "line": 1,
                        "description": "Duplicate keys detected in JSON",
                    }
                )

        return structure_issues

    def analyze_semantics(self, parsed_data: dict[str, Any]) -> list[Any]:
        if not parsed_data["syntax_valid"]:
            return []

        data = parsed_data["data"]
        semantic_issues = []

        # Check for hardcoded values
        if isinstance(data, dict):
            for key, value in data.items():
                if isinstance(value, str) and len(value) > 50:
                    semantic_issues.append(
                        {
                            "type": "hardcoded_values",
                            "line": 1,
                            "description": f'Long hardcoded string in key "{key}"',
                        }
                    )

        return semantic_issues

    def calculate_metrics(self, parsed_data: dict[str, Any], lines: list[str]) -> list[Any]:
        if not parsed_data["syntax_valid"]:
            return []

        data = parsed_data["data"]
        metrics = []

        # Key count
        if isinstance(data, dict):
            key_count = len(data.keys())
            metrics.append({"name": "key_count", "value": key_count, "unit": "keys"})

        # Nesting depth
        max_depth = self._calculate_nesting_depth(data)
        metrics.append({"name": "nesting_depth", "value": max_depth, "unit": "levels"})

        return metrics

    def _calculate_nesting_depth(self, obj, current_depth=0):
        if isinstance(obj, dict):
            if not obj:
                return current_depth
            return max(self._calculate_nesting_depth(v, current_depth + 1) for v in obj.values())
        if isinstance(obj, list):
            if not obj:
                return current_depth
            return max(self._calculate_nesting_depth(item, current_depth + 1) for item in obj)
        return current_depth


class YAMLParser(FileTypeParser):
    """YAML file parser with structure analysis"""

    def __init__(self):
        super().__init__(file_type=FileType.YAML, supported_extensions=[".yaml", ".yml"])

    def can_parse(self, file_path: Path) -> bool:
        return file_path.suffix in self.supported_extensions

    def parse(self, file_path: Path) -> dict[str, Any]:
        try:
            import ruamel.yaml

            yaml = ruamel.yaml.YAML()

            with open(file_path, encoding="utf-8") as f:
                data = yaml.load(f)
                content = f.read()

            return {
                "data": data,
                "content": content,
                "syntax_valid": True,
                "errors": [],
            }
        except Exception as e:
            with open(file_path, encoding="utf-8") as f:
                content = f.read()

            return {
                "data": None,
                "content": content,
                "syntax_valid": False,
                "errors": [e],
            }

    def validate_syntax(self, content: str) -> tuple[bool, list[Any]]:
        try:
            import ruamel.yaml

            yaml = ruamel.yaml.YAML()
            yaml.load(content)
            return True, []
        except Exception as e:
            return False, [e]

    def analyze_structure(self, parsed_data: dict[str, Any]) -> list[Any]:
        if not parsed_data["syntax_valid"]:
            return []

        parsed_data["data"]
        structure_issues = []

        # Check for inconsistent indentation
        lines = parsed_data["content"].splitlines()
        indent_sizes = set()

        for line in lines:
            if line.strip() and not line.startswith("#"):
                indent = len(line) - len(line.lstrip())
                if indent > 0:
                    indent_sizes.add(indent)

        if len(indent_sizes) > 1:
            structure_issues.append(
                {
                    "type": "inconsistent_indentation",
                    "line": 1,
                    "description": "Inconsistent indentation detected",
                }
            )

        return structure_issues

    def analyze_semantics(self, parsed_data: dict[str, Any]) -> list[Any]:
        if not parsed_data["syntax_valid"]:
            return []

        data = parsed_data["data"]
        semantic_issues = []

        # Check for hardcoded values
        if isinstance(data, dict):
            for key, value in data.items():
                if isinstance(value, str) and len(value) > 50:
                    semantic_issues.append(
                        {
                            "type": "hardcoded_values",
                            "line": 1,
                            "description": f'Long hardcoded string in key "{key}"',
                        }
                    )

        return semantic_issues

    def calculate_metrics(self, parsed_data: dict[str, Any], lines: list[str]) -> list[Any]:
        if not parsed_data["syntax_valid"]:
            return []

        data = parsed_data["data"]
        metrics = []

        # Key count
        if isinstance(data, dict):
            key_count = len(data.keys())
            metrics.append({"name": "key_count", "value": key_count, "unit": "keys"})

        # Line count
        metrics.append({"name": "line_count", "value": len(lines), "unit": "lines"})

        return metrics


class INIParser(FileTypeParser):
    """INI file parser with configuration analysis"""

    def __init__(self):
        super().__init__(file_type=FileType.INI, supported_extensions=[".ini", ".cfg", ".conf"])

    def can_parse(self, file_path: Path) -> bool:
        return file_path.suffix in self.supported_extensions

    def parse(self, file_path: Path) -> dict[str, Any]:
        config = configparser.ConfigParser()

        try:
            config.read(file_path)
            with open(file_path, encoding="utf-8") as f:
                content = f.read()

            return {
                "config": config,
                "content": content,
                "syntax_valid": True,
                "errors": [],
            }
        except Exception as e:
            with open(file_path, encoding="utf-8") as f:
                content = f.read()

            return {
                "config": None,
                "content": content,
                "syntax_valid": False,
                "errors": [e],
            }

    def validate_syntax(self, content: str) -> tuple[bool, list[Any]]:
        try:
            config = configparser.ConfigParser()
            config.read_string(content)
            return True, []
        except Exception as e:
            return False, [e]

    def analyze_structure(self, parsed_data: dict[str, Any]) -> list[Any]:
        if not parsed_data["syntax_valid"]:
            return []

        config = parsed_data["config"]
        structure_issues = []

        # Check for empty sections
        for section in config.sections():
            if not config[section]:
                structure_issues.append(
                    {
                        "type": "empty_section",
                        "line": 1,
                        "description": f'Empty section "{section}"',
                    }
                )

        return structure_issues

    def analyze_semantics(self, parsed_data: dict[str, Any]) -> list[Any]:
        if not parsed_data["syntax_valid"]:
            return []

        config = parsed_data["config"]
        semantic_issues = []

        # Check for hardcoded values
        for section in config.sections():
            for key, value in config[section].items():
                if len(value) > 100:
                    semantic_issues.append(
                        {
                            "type": "hardcoded_values",
                            "line": 1,
                            "description": f"Long hardcoded value in [{section}] {key}",
                        }
                    )

        return semantic_issues

    def calculate_metrics(self, parsed_data: dict[str, Any], lines: list[str]) -> list[Any]:
        if not parsed_data["syntax_valid"]:
            return []

        config = parsed_data["config"]
        metrics = []

        # Section count
        section_count = len(config.sections())
        metrics.append({"name": "section_count", "value": section_count, "unit": "sections"})

        # Total key count
        total_keys = sum(len(config[section]) for section in config.sections())
        metrics.append({"name": "total_keys", "value": total_keys, "unit": "keys"})

        return metrics


class TOMLParser(FileTypeParser):
    """TOML file parser with semantic analysis"""

    def __init__(self):
        super().__init__(file_type=FileType.TOML, supported_extensions=[".toml"])

    def can_parse(self, file_path: Path) -> bool:
        return file_path.suffix in self.supported_extensions

    def parse(self, file_path: Path) -> dict[str, Any]:
        try:
            import tomllib

            with open(file_path, "rb") as f:
                data = tomllib.load(f)

            with open(file_path, encoding="utf-8") as f:
                content = f.read()

            return {
                "data": data,
                "content": content,
                "syntax_valid": True,
                "errors": [],
            }
        except ImportError:
            try:
                import tomli

                with open(file_path, "rb") as f:
                    data = tomli.load(f)

                with open(file_path, encoding="utf-8") as f:
                    content = f.read()

                return {
                    "data": data,
                    "content": content,
                    "syntax_valid": True,
                    "errors": [],
                }
            except Exception as e:
                with open(file_path, encoding="utf-8") as f:
                    content = f.read()

                return {
                    "data": None,
                    "content": content,
                    "syntax_valid": False,
                    "errors": [e],
                }
        except Exception as e:
            with open(file_path, encoding="utf-8") as f:
                content = f.read()

            return {
                "data": None,
                "content": content,
                "syntax_valid": False,
                "errors": [e],
            }

    def validate_syntax(self, content: str) -> tuple[bool, list[Any]]:
        try:
            import tomllib

            tomllib.load(io.BytesIO(content.encode()))
            return True, []
        except ImportError:
            try:
                import tomli

                tomli.load(io.BytesIO(content.encode()))
                return True, []
            except Exception as e:
                return False, [e]
        except Exception as e:
            return False, [e]

    def analyze_structure(self, parsed_data: dict[str, Any]) -> list[Any]:
        if not parsed_data["syntax_valid"]:
            return []

        data = parsed_data["data"]
        structure_issues = []

        # Check for deeply nested structures
        max_depth = self._calculate_nesting_depth(data)
        if max_depth > 5:
            structure_issues.append(
                {
                    "type": "deep_nesting",
                    "line": 1,
                    "description": f"Deeply nested structure ({max_depth} levels)",
                }
            )

        return structure_issues

    def analyze_semantics(self, parsed_data: dict[str, Any]) -> list[Any]:
        if not parsed_data["syntax_valid"]:
            return []

        data = parsed_data["data"]
        semantic_issues = []

        # Check for hardcoded values
        if isinstance(data, dict):
            for key, value in data.items():
                if isinstance(value, str) and len(value) > 100:
                    semantic_issues.append(
                        {
                            "type": "hardcoded_values",
                            "line": 1,
                            "description": f'Long hardcoded string in key "{key}"',
                        }
                    )

        return semantic_issues

    def calculate_metrics(self, parsed_data: dict[str, Any], lines: list[str]) -> list[Any]:
        if not parsed_data["syntax_valid"]:
            return []

        data = parsed_data["data"]
        metrics = []

        # Key count
        if isinstance(data, dict):
            key_count = len(data.keys())
            metrics.append({"name": "key_count", "value": key_count, "unit": "keys"})

        # Nesting depth
        max_depth = self._calculate_nesting_depth(data)
        metrics.append({"name": "nesting_depth", "value": max_depth, "unit": "levels"})

        return metrics

    def _calculate_nesting_depth(self, obj, current_depth=0):
        if isinstance(obj, dict):
            if not obj:
                return current_depth
            return max(self._calculate_nesting_depth(v, current_depth + 1) for v in obj.values())
        if isinstance(obj, list):
            if not obj:
                return current_depth
            return max(self._calculate_nesting_depth(item, current_depth + 1) for item in obj)
        return current_depth


class UniversalASTEnhancedLinterModel:
    """
    Universal AST-Enhanced Linter Model

    This model provides semantic analysis capabilities for ALL file types,
    not just Python. Each file type gets its own specialized parser that
    provides AST-equivalent semantic understanding.
    """

    def __init__(self):
        self.parsers: dict[FileType, FileTypeParser] = {}
        self.analysis_rules: list[UniversalAnalysisRule] = []

        self._initialize_parsers()
        self._initialize_analysis_rules()

    def _initialize_parsers(self):
        """Initialize parsers for all supported file types"""
        self.parsers[FileType.PYTHON] = PythonParser()
        self.parsers[FileType.JSON] = JSONParser()
        self.parsers[FileType.YAML] = YAMLParser()
        self.parsers[FileType.INI] = INIParser()
        self.parsers[FileType.TOML] = TOMLParser()

        # TODO: Add more parsers for XML, Markdown, Shell, Dockerfile, Makefile

    def _initialize_analysis_rules(self):
        """Initialize universal analysis rules"""

        # Universal quality rules
        self.analysis_rules.append(
            UniversalAnalysisRule(
                name="Line Too Long",
                file_types=[FileType.PYTHON, FileType.MARKDOWN, FileType.SHELL],
                strategy=AnalysisStrategy.QUALITY_ANALYSIS,
                issue_type=IssueType.LINE_TOO_LONG,
                severity=IssueSeverity.WARNING,
                auto_fix=AutoFixCapability.CAN_FIX,
                description="Line exceeds recommended length",
                suggestion="Break line into multiple lines",
                threshold=88.0,
            )
        )

        # File type specific rules
        self.analysis_rules.append(
            UniversalAnalysisRule(
                name="Missing Docstrings",
                file_types=[FileType.PYTHON],
                strategy=AnalysisStrategy.SEMANTIC_ANALYSIS,
                issue_type=IssueType.PYTHON_SPECIFIC,
                severity=IssueSeverity.SUGGESTION,
                auto_fix=AutoFixCapability.CANNOT_FIX,
                description="Function or class missing docstring",
                suggestion="Add docstring to document purpose",
            )
        )

        self.analysis_rules.append(
            UniversalAnalysisRule(
                name="Hardcoded Values",
                file_types=[FileType.JSON, FileType.YAML, FileType.TOML, FileType.INI],
                strategy=AnalysisStrategy.SEMANTIC_ANALYSIS,
                issue_type=IssueType.HARDCODED_VALUES,
                severity=IssueSeverity.SUGGESTION,
                auto_fix=AutoFixCapability.CANNOT_FIX,
                description="Hardcoded values that should be configurable",
                suggestion="Extract to configuration or environment variables",
            )
        )

    def get_parser_for_file(self, file_path: Path) -> Optional[FileTypeParser]:
        """Get the appropriate parser for a file"""
        for parser in self.parsers.values():
            if parser.can_parse(file_path):
                return parser
        return None

    def get_rules_for_file_type(self, file_type: FileType) -> list[UniversalAnalysisRule]:
        """Get analysis rules for a specific file type"""
        return [rule for rule in self.analysis_rules if file_type in rule.file_types]

    def get_rules_for_strategy(self, strategy: AnalysisStrategy) -> list[UniversalAnalysisRule]:
        """Get analysis rules for a specific strategy"""
        return [rule for rule in self.analysis_rules if rule.strategy == strategy]


# Factory function
def create_universal_ast_enhanced_linter_model() -> UniversalASTEnhancedLinterModel:
    """Create and return a configured universal AST-enhanced linter model"""
    return UniversalASTEnhancedLinterModel()


if __name__ == "__main__":
    # Test the universal model
    model = create_universal_ast_enhanced_linter_model()
    print(f"✅ Universal AST-Enhanced Linter Model created successfully!")
    print(f"   Parsers: {len(model.parsers)}")
    print(f"   Analysis Rules: {len(model.analysis_rules)}")

    # Test parser detection
    test_files = [
        Path("test.py"),
        Path("config.json"),
        Path("settings.yaml"),
        Path("config.ini"),
        Path("pyproject.toml"),
    ]

    print(f"\n🔍 Parser Detection Test:")
    for test_file in test_files:
        parser = model.get_parser_for_file(test_file)
        if parser:
            print(f"   ✅ {test_file.name} → {parser.file_type.value}")
        else:
            print(f"   ❌ {test_file.name} → No parser found")

    print(f"\n📋 Analysis Rules by File Type:")
    for file_type in FileType:
        rules = model.get_rules_for_file_type(file_type)
        if rules:
            print(f"   {file_type.value}: {len(rules)} rules")
