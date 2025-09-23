#!/usr/bin/env python3
"""
Enhanced Interface Registry Scanner
Extracts comprehensive metadata from ReflectiveModule implementations including:
- Actual method signatures
- Precise file location tracking
- Domain vocabulary (ubiquitous language) indexing
- Interface compliance validation
"""

import ast
import os
import re
from typing import Dict, List, Set, Tuple, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime
import json

from src.beast_mode.interface_governance.interface_registry import (
    BeastModeInterfaceRegistry,
    InterfaceMetadata,
    InterfaceType,
    InterfaceStatus,
)


@dataclass
class MethodSignature:
    """Represents a method signature with full metadata."""

    name: str
    parameters: List[
        Dict[str, str]
    ]  # [{"name": "param", "type": "str", "default": None}]
    return_type: Optional[str] = None
    docstring: Optional[str] = None
    is_abstract: bool = False
    decorators: List[str] = field(default_factory=list)


@dataclass
class EnhancedInterfaceMetadata:
    """Enhanced interface metadata with comprehensive information."""

    interface_name: str
    interface_type: InterfaceType
    file_path: str
    line_number: int
    end_line_number: int
    methods: List[MethodSignature] = field(default_factory=list)
    domain_terms: Set[str] = field(default_factory=set)
    ubiquitous_language: Set[str] = field(default_factory=set)
    imports: List[str] = field(default_factory=list)
    dependencies: Set[str] = field(default_factory=set)
    compliance_score: float = 0.0
    status: InterfaceStatus = InterfaceStatus.ACTIVE
    registered_at: datetime = field(default_factory=datetime.now)
    conflicts: List[str] = field(default_factory=list)


class EnhancedInterfaceScanner:
    """Enhanced scanner for ReflectiveModule implementations."""

    def __init__(self):
        self.domain_vocabulary = self._load_domain_vocabulary()
        self.ubiquitous_language = self._load_ubiquitous_language()

    def _load_domain_vocabulary(self) -> Set[str]:
        """Load domain vocabulary from various sources."""
        vocabulary = set(
            [
                # Beast Mode Core
                "beast_mode",
                "systematic",
                "superiority",
                "pdca",
                "orchestration",
                "reflective",
                "module",
                "governance",
                "compliance",
                "validation",
                # Development Terms
                "development",
                "engineering",
                "architecture",
                "design",
                "implementation",
                "testing",
                "quality",
                "metrics",
                "monitoring",
                "observability",
                # Domain-Driven Design
                "domain",
                "service",
                "repository",
                "entity",
                "value_object",
                "aggregate",
                "bounded_context",
                "anti_corruption_layer",
                "shared_kernel",
                "event",
                "command",
                "query",
                "handler",
                "factory",
                "specification",
                # Integration Terms
                "integration",
                "adapter",
                "transformer",
                "mapper",
                "converter",
                "api",
                "client",
                "server",
                "protocol",
                "transport",
                "serialization",
                # Quality & Testing
                "test",
                "specification",
                "assertion",
                "mock",
                "stub",
                "fixture",
                "coverage",
                "performance",
                "benchmark",
                "profiling",
                "debugging",
                # Infrastructure
                "infrastructure",
                "deployment",
                "configuration",
                "environment",
                "container",
                "docker",
                "kubernetes",
                "cloud",
                "aws",
                "gcp",
                "azure",
                # Security & Compliance
                "security",
                "authentication",
                "authorization",
                "encryption",
                "audit",
                "compliance",
                "governance",
                "policy",
                "rule",
                "validation",
                # AI & ML
                "ai",
                "machine_learning",
                "neural_network",
                "model",
                "training",
                "inference",
                "prediction",
                "classification",
                "regression",
                "clustering",
                # Project Management
                "project",
                "task",
                "sprint",
                "backlog",
                "milestone",
                "deadline",
                "resource",
                "timeline",
                "budget",
                "risk",
                "issue",
                "dependency",
            ]
        )
        return vocabulary

    def _load_ubiquitous_language(self) -> Set[str]:
        """Load ubiquitous language terms specific to the project."""
        ubiquitous = set(
            [
                # Project-specific terms
                "kiro",
                "simone",
                "claude",
                "devpost",
                "hackathon",
                "competitive",
                "launch",
                "rc0",
                "beast_mode",
                "systematic_approach",
                "zero_tech_debt",
                # Interface-specific terms
                "reflective_module",
                "interface_registry",
                "governance",
                "compliance",
                "duplicate_prevention",
                "rm_ddd",
                "rdi",
                "domain_driven_design",
                # Integration-specific terms
                "mcp_server",
                "github_integration",
                "claude_simone",
                "ai_assisted",
                "project_management",
                "task_orchestration",
                "sprint_management",
                # Quality-specific terms
                "quality_gates",
                "automated_validation",
                "systematic_testing",
                "performance_monitoring",
                "error_handling",
                "graceful_degradation",
                # Architecture-specific terms
                "microservices",
                "event_sourcing",
                "cqrs",
                "hexagonal_architecture",
                "clean_architecture",
                "onion_architecture",
                "layered_architecture",
            ]
        )
        return ubiquitous

    def scan_file(self, file_path: str) -> List[EnhancedInterfaceMetadata]:
        """Scan a single file for ReflectiveModule implementations."""
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            tree = ast.parse(content)
            interfaces = []

            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    if self._is_reflective_module(node, content):
                        interface = self._extract_interface_metadata(
                            node, file_path, content
                        )
                        if interface:
                            interfaces.append(interface)

            return interfaces

        except Exception as e:
            print(f"Error scanning {file_path}: {e}")
            return []

    def _is_reflective_module(self, class_node: ast.ClassDef, content: str) -> bool:
        """Check if a class is a ReflectiveModule implementation."""
        # Check base classes
        for base in class_node.bases:
            if isinstance(base, ast.Name) and base.id == "ReflectiveModule":
                return True

        # Check class docstring or comments for ReflectiveModule
        if "ReflectiveModule" in content[class_node.lineno - 1 : class_node.end_lineno]:
            return True

        return False

    def _extract_interface_metadata(
        self, class_node: ast.ClassDef, file_path: str, content: str
    ) -> Optional[EnhancedInterfaceMetadata]:
        """Extract comprehensive metadata from a ReflectiveModule class."""
        interface_name = class_node.name

        # Extract methods with signatures
        methods = []
        for node in class_node.body:
            if isinstance(node, ast.FunctionDef):
                method = self._extract_method_signature(node, content)
                methods.append(method)

        # Extract domain terms and ubiquitous language
        class_text = content[class_node.lineno - 1 : class_node.end_lineno].lower()
        domain_terms = self._extract_domain_terms(class_text)
        ubiquitous_terms = self._extract_ubiquitous_language(class_text)

        # Extract imports and dependencies
        imports = self._extract_imports(content)
        dependencies = self._extract_dependencies(class_node, content)

        # Calculate compliance score
        compliance_score = self._calculate_compliance_score(class_node, methods)

        # Determine interface type
        interface_type = self._determine_interface_type(
            interface_name, class_text, methods
        )

        return EnhancedInterfaceMetadata(
            interface_name=interface_name,
            interface_type=interface_type,
            file_path=file_path,
            line_number=class_node.lineno,
            end_line_number=class_node.end_lineno,
            methods=methods,
            domain_terms=domain_terms,
            ubiquitous_language=ubiquitous_terms,
            imports=imports,
            dependencies=dependencies,
            compliance_score=compliance_score,
        )

    def _extract_method_signature(
        self, method_node: ast.FunctionDef, content: str
    ) -> MethodSignature:
        """Extract detailed method signature information."""
        parameters = []
        for arg in method_node.args.args:
            param_info = {"name": arg.arg}

            # Extract type annotation
            if arg.annotation:
                param_info["type"] = (
                    ast.unparse(arg.annotation)
                    if hasattr(ast, "unparse")
                    else str(arg.annotation)
                )

            parameters.append(param_info)

        # Extract return type
        return_type = None
        if method_node.returns:
            return_type = (
                ast.unparse(method_node.returns)
                if hasattr(ast, "unparse")
                else str(method_node.returns)
            )

        # Extract docstring
        docstring = ast.get_docstring(method_node)

        # Extract decorators
        decorators = []
        for decorator in method_node.decorator_list:
            if isinstance(decorator, ast.Name):
                decorators.append(decorator.id)
            elif isinstance(decorator, ast.Attribute):
                decorators.append(f"{decorator.attr}")

        # Check if abstract
        is_abstract = any("abstract" in dec.lower() for dec in decorators)

        return MethodSignature(
            name=method_node.name,
            parameters=parameters,
            return_type=return_type,
            docstring=docstring,
            is_abstract=is_abstract,
            decorators=decorators,
        )

    def _extract_domain_terms(self, text: str) -> Set[str]:
        """Extract domain-specific terms from text."""
        terms = set()
        words = re.findall(r"\b[a-z_]+\b", text)

        for word in words:
            if word in self.domain_vocabulary:
                terms.add(word)

        return terms

    def _extract_ubiquitous_language(self, text: str) -> Set[str]:
        """Extract ubiquitous language terms from text."""
        terms = set()
        words = re.findall(r"\b[a-z_]+\b", text)

        for word in words:
            if word in self.ubiquitous_language:
                terms.add(word)

        return terms

    def _extract_imports(self, content: str) -> List[str]:
        """Extract import statements from content."""
        imports = []
        lines = content.split("\n")

        for line in lines:
            line = line.strip()
            if line.startswith(("import ", "from ")):
                imports.append(line)

        return imports

    def _extract_dependencies(self, class_node: ast.ClassDef, content: str) -> Set[str]:
        """Extract dependencies from class usage."""
        dependencies = set()

        # Look for attribute access patterns
        for node in ast.walk(class_node):
            if isinstance(node, ast.Attribute):
                if isinstance(node.value, ast.Name):
                    dependencies.add(node.value.id)

        return dependencies

    def _calculate_compliance_score(
        self, class_node: ast.ClassDef, methods: List[MethodSignature]
    ) -> float:
        """Calculate compliance score for ReflectiveModule interface."""
        score = 0.0
        max_score = 100.0

        # Required methods for ReflectiveModule
        required_methods = ["get_health_status", "get_metrics", "is_healthy"]
        method_names = [method.name for method in methods]

        # Check for required methods (40 points)
        for req_method in required_methods:
            if req_method in method_names:
                score += 40.0 / len(required_methods)

        # Check for proper documentation (20 points)
        documented_methods = sum(1 for method in methods if method.docstring)
        if methods:
            score += 20.0 * (documented_methods / len(methods))

        # Check for type annotations (20 points)
        typed_methods = sum(1 for method in methods if method.return_type)
        if methods:
            score += 20.0 * (typed_methods / len(methods))

        # Check for abstract methods (10 points)
        abstract_methods = sum(1 for method in methods if method.is_abstract)
        if methods:
            score += 10.0 * min(abstract_methods / len(methods), 0.5)  # Max 10 points

        # Check for decorators (10 points)
        decorated_methods = sum(1 for method in methods if method.decorators)
        if methods:
            score += 10.0 * (decorated_methods / len(methods))

        return min(score, max_score)

    def _determine_interface_type(
        self, name: str, text: str, methods: List[MethodSignature]
    ) -> InterfaceType:
        """Determine the interface type based on name and content."""
        name_lower = name.lower()
        text_lower = text.lower()

        # Check for specific patterns
        if any(term in name_lower for term in ["service", "manager", "handler"]):
            return InterfaceType.DOMAIN_SERVICE
        elif any(term in name_lower for term in ["api", "client", "server"]):
            return InterfaceType.API_INTERFACE
        elif any(term in name_lower for term in ["model", "entity", "data"]):
            return InterfaceType.DATA_MODEL
        elif any(term in name_lower for term in ["rule", "validator", "validation"]):
            return InterfaceType.VALIDATION_RULE
        elif any(
            term in name_lower for term in ["config", "settings", "configuration"]
        ):
            return InterfaceType.CONFIGURATION
        else:
            return InterfaceType.REFLECTIVE_MODULE


class EnhancedInterfaceRegistry:
    """Enhanced interface registry with comprehensive metadata."""

    def __init__(
        self, registry_file: str = ".beast_mode/enhanced_interface_registry.json"
    ):
        self.registry_file = registry_file
        self.scanner = EnhancedInterfaceScanner()
        self.interfaces: Dict[str, EnhancedInterfaceMetadata] = {}
        self.domain_index: Dict[str, Set[str]] = {}
        self.ubiquitous_language_index: Dict[str, Set[str]] = {}

        # Ensure directory exists
        os.makedirs(os.path.dirname(registry_file), exist_ok=True)

        self.load_registry()

    def scan_codebase(self, root_path: str = "src") -> None:
        """Scan the entire codebase for ReflectiveModule implementations."""
        print("🔍 Enhanced Interface Registry Scanner")
        print("=" * 50)

        total_files = 0
        total_interfaces = 0

        for root, dirs, files in os.walk(root_path):
            for file in files:
                if file.endswith(".py"):
                    file_path = os.path.join(root, file)
                    total_files += 1

                    interfaces = self.scanner.scan_file(file_path)
                    for interface in interfaces:
                        interface_id = f"{interface.interface_name}_{interface.interface_type.value}"
                        self.interfaces[interface_id] = interface
                        total_interfaces += 1

                        # Update domain index
                        for term in interface.domain_terms:
                            if term not in self.domain_index:
                                self.domain_index[term] = set()
                            self.domain_index[term].add(interface_id)

                        # Update ubiquitous language index
                        for term in interface.ubiquitous_language:
                            if term not in self.ubiquitous_language_index:
                                self.ubiquitous_language_index[term] = set()
                            self.ubiquitous_language_index[term].add(interface_id)

        print(f"📁 Files scanned: {total_files}")
        print(f"🔧 Interfaces found: {total_interfaces}")
        print(f"📚 Domain terms indexed: {len(self.domain_index)}")
        print(f"🗣️  Ubiquitous language terms: {len(self.ubiquitous_language_index)}")

        self.save_registry()

    def save_registry(self) -> None:
        """Save enhanced registry to file."""
        try:
            data = {
                "interfaces": {
                    interface_id: {
                        "interface_name": interface.interface_name,
                        "interface_type": interface.interface_type.value,
                        "file_path": interface.file_path,
                        "line_number": interface.line_number,
                        "end_line_number": interface.end_line_number,
                        "methods": [
                            {
                                "name": method.name,
                                "parameters": method.parameters,
                                "return_type": method.return_type,
                                "docstring": method.docstring,
                                "is_abstract": method.is_abstract,
                                "decorators": method.decorators,
                            }
                            for method in interface.methods
                        ],
                        "domain_terms": list(interface.domain_terms),
                        "ubiquitous_language": list(interface.ubiquitous_language),
                        "imports": interface.imports,
                        "dependencies": list(interface.dependencies),
                        "compliance_score": interface.compliance_score,
                        "status": interface.status.value,
                        "registered_at": interface.registered_at.isoformat(),
                        "conflicts": interface.conflicts,
                    }
                    for interface_id, interface in self.interfaces.items()
                },
                "domain_index": {
                    term: list(interface_ids)
                    for term, interface_ids in self.domain_index.items()
                },
                "ubiquitous_language_index": {
                    term: list(interface_ids)
                    for term, interface_ids in self.ubiquitous_language_index.items()
                },
                "metadata": {
                    "total_interfaces": len(self.interfaces),
                    "total_domain_terms": len(self.domain_index),
                    "total_ubiquitous_terms": len(self.ubiquitous_language_index),
                    "last_updated": datetime.now().isoformat(),
                },
            }

            with open(self.registry_file, "w") as f:
                json.dump(data, f, indent=2)

            print(f"✅ Enhanced registry saved to {self.registry_file}")

        except Exception as e:
            print(f"❌ Error saving enhanced registry: {e}")

    def load_registry(self) -> None:
        """Load enhanced registry from file."""
        if os.path.exists(self.registry_file):
            try:
                with open(self.registry_file, "r") as f:
                    data = json.load(f)

                # Load interfaces
                for interface_id, interface_data in data.get("interfaces", {}).items():
                    # Convert methods back to MethodSignature objects
                    methods = [
                        MethodSignature(
                            name=method_data["name"],
                            parameters=method_data["parameters"],
                            return_type=method_data["return_type"],
                            docstring=method_data["docstring"],
                            is_abstract=method_data["is_abstract"],
                            decorators=method_data["decorators"],
                        )
                        for method_data in interface_data["methods"]
                    ]

                    interface = EnhancedInterfaceMetadata(
                        interface_name=interface_data["interface_name"],
                        interface_type=InterfaceType(interface_data["interface_type"]),
                        file_path=interface_data["file_path"],
                        line_number=interface_data["line_number"],
                        end_line_number=interface_data["end_line_number"],
                        methods=methods,
                        domain_terms=set(interface_data["domain_terms"]),
                        ubiquitous_language=set(interface_data["ubiquitous_language"]),
                        imports=interface_data["imports"],
                        dependencies=set(interface_data["dependencies"]),
                        compliance_score=interface_data["compliance_score"],
                        status=InterfaceStatus(interface_data["status"]),
                        registered_at=datetime.fromisoformat(
                            interface_data["registered_at"]
                        ),
                        conflicts=interface_data["conflicts"],
                    )

                    self.interfaces[interface_id] = interface

                # Load indices
                self.domain_index = {
                    term: set(interface_ids)
                    for term, interface_ids in data.get("domain_index", {}).items()
                }

                self.ubiquitous_language_index = {
                    term: set(interface_ids)
                    for term, interface_ids in data.get(
                        "ubiquitous_language_index", {}
                    ).items()
                }

            except Exception as e:
                print(f"Warning: Could not load enhanced registry: {e}")

    def get_registry_report(self) -> Dict[str, Any]:
        """Generate comprehensive registry report."""
        total_interfaces = len(self.interfaces)
        avg_compliance = (
            sum(interface.compliance_score for interface in self.interfaces.values())
            / total_interfaces
            if total_interfaces > 0
            else 0
        )

        # Method statistics
        total_methods = sum(
            len(interface.methods) for interface in self.interfaces.values()
        )
        documented_methods = sum(
            sum(1 for method in interface.methods if method.docstring)
            for interface in self.interfaces.values()
        )
        typed_methods = sum(
            sum(1 for method in interface.methods if method.return_type)
            for interface in self.interfaces.values()
        )

        return {
            "total_interfaces": total_interfaces,
            "average_compliance_score": round(avg_compliance, 2),
            "total_methods": total_methods,
            "documented_methods": documented_methods,
            "documentation_coverage": (
                round(documented_methods / total_methods * 100, 1)
                if total_methods > 0
                else 0
            ),
            "typed_methods": typed_methods,
            "type_coverage": (
                round(typed_methods / total_methods * 100, 1)
                if total_methods > 0
                else 0
            ),
            "domain_terms_indexed": len(self.domain_index),
            "ubiquitous_language_terms": len(self.ubiquitous_language_index),
            "interface_types": {
                interface_type.value: len(
                    [
                        i
                        for i in self.interfaces.values()
                        if i.interface_type == interface_type
                    ]
                )
                for interface_type in InterfaceType
            },
        }


def main():
    """Main execution function."""
    registry = EnhancedInterfaceRegistry()
    registry.scan_codebase()

    # Generate and display report
    report = registry.get_registry_report()

    print("\n📊 Enhanced Registry Report")
    print("=" * 50)
    print(f"Total interfaces: {report['total_interfaces']}")
    print(f"Average compliance score: {report['average_compliance_score']}%")
    print(f"Total methods: {report['total_methods']}")
    print(f"Documentation coverage: {report['documentation_coverage']}%")
    print(f"Type annotation coverage: {report['type_coverage']}%")
    print(f"Domain terms indexed: {report['domain_terms_indexed']}")
    print(f"Ubiquitous language terms: {report['ubiquitous_language_terms']}")

    print("\n📋 Interface Types:")
    for interface_type, count in report["interface_types"].items():
        print(f"  {interface_type}: {count}")


if __name__ == "__main__":
    main()
