#!/usr/bin/env python3
"""
RMDDD Base Interface
===================

Dynamic base class implementation that automatically handles most RMDDD interface
functionality through introspection, analysis, and code generation.
"""

from typing import (
    Dict,
    Any,
    List,
    Optional,
    Callable,
    get_type_hints,
    get_origin,
    get_args,
)
from dataclasses import dataclass, asdict
from abc import ABC, abstractmethod
import inspect
import json
import argparse
import ast
import sys
from datetime import datetime
from pathlib import Path


@dataclass
class DynamicComponentMap:
    """Dynamically generated component map"""

    component_name: str
    capabilities: List[str]
    limitations: List[str]
    dependencies: List[str]
    inputs_accepted: List[str]
    outputs_produced: List[str]
    knowledge_domains: List[str]
    unknown_areas: List[str]
    confidence_levels: Dict[str, float]
    code_complexity: Dict[str, Any]
    analysis_timestamp: datetime


@dataclass
class DynamicBabbleFishResponse:
    """Dynamically generated babble fish response"""

    question: str
    answer: str
    confidence: float
    knowledge_source: str
    limitations: List[str]
    follow_up_suggestions: List[str]
    related_capabilities: List[str]
    code_references: List[str]


class RMDDDBaseInterface(ABC):
    """
    Dynamic base class that automatically handles most RMDDD interface functionality
    through introspection, AST analysis, and intelligent code generation.
    """

    def __init__(self, target_function: Callable, component_name: str):
        self.target_function = target_function
        self.component_name = component_name
        self.function_source = self._get_function_source()
        self.ast_tree = self._parse_ast()
        self.type_hints = self._get_type_hints()
        self.component_map = None
        self._initialize_dynamic_analysis()

    def _get_function_source(self) -> str:
        """Get the source code of the target function"""
        try:
            return inspect.getsource(self.target_function)
        except (OSError, TypeError):
            return f"# Source code not available for {self.target_function.__name__}"

    def _parse_ast(self) -> Optional[ast.AST]:
        """Parse the function source code into an AST"""
        try:
            return ast.parse(self.function_source)
        except SyntaxError:
            return None

    def _get_type_hints(self) -> Dict[str, Any]:
        """Get type hints from the function"""
        try:
            return get_type_hints(self.target_function)
        except (TypeError, NameError):
            return {}

    def _initialize_dynamic_analysis(self):
        """Initialize dynamic analysis of the component"""
        self.component_map = self._build_dynamic_component_map()

    def _build_dynamic_component_map(self) -> DynamicComponentMap:
        """Dynamically build component map through code analysis"""

        # Analyze function signature
        sig = inspect.signature(self.target_function)
        parameters = dict(sig.parameters)

        # Analyze source code patterns
        capabilities = self._analyze_capabilities_from_code()
        limitations = self._analyze_limitations_from_code()
        dependencies = self._analyze_dependencies_from_code()

        # Analyze type hints and parameters
        inputs_accepted = self._analyze_inputs_from_signature(parameters)
        outputs_produced = self._analyze_outputs_from_code()

        # Analyze knowledge domains from code content
        knowledge_domains = self._analyze_knowledge_domains_from_code()
        unknown_areas = self._analyze_unknown_areas_from_code()

        # Calculate confidence levels based on code analysis
        confidence_levels = self._calculate_confidence_levels_from_code()

        # Analyze code complexity
        code_complexity = self._analyze_code_complexity()

        return DynamicComponentMap(
            component_name=self.component_name,
            capabilities=capabilities,
            limitations=limitations,
            dependencies=dependencies,
            inputs_accepted=inputs_accepted,
            outputs_produced=outputs_produced,
            knowledge_domains=knowledge_domains,
            unknown_areas=unknown_areas,
            confidence_levels=confidence_levels,
            code_complexity=code_complexity,
            analysis_timestamp=datetime.now(),
        )

    def _analyze_capabilities_from_code(self) -> List[str]:
        """Analyze source code to determine capabilities"""
        capabilities = []
        source_lower = self.function_source.lower()

        # Pattern-based capability detection
        capability_patterns = {
            "investigate": ["investigate", "investigation", "analyze", "analysis"],
            "navigate": ["navigate", "navigation", "route", "routing"],
            "verify": ["verify", "verification", "validate", "validation"],
            "recover": ["recover", "recovery", "restore", "restoration"],
            "consult": ["consult", "consultation", "advise", "advice"],
            "test": ["test", "testing", "diagnose", "diagnostic"],
            "generate": ["generate", "create", "produce", "build"],
            "handle": ["handle", "manage", "process", "execute"],
            "analyze": ["analyze", "examine", "inspect", "evaluate"],
            "communicate": ["communicate", "message", "report", "respond"],
        }

        for capability, patterns in capability_patterns.items():
            if any(pattern in source_lower for pattern in patterns):
                capabilities.append(f"Can {capability} based on code analysis")

        # AST-based capability detection
        if self.ast_tree:
            ast_capabilities = self._analyze_capabilities_from_ast()
            capabilities.extend(ast_capabilities)

        return list(set(capabilities))  # Remove duplicates

    def _analyze_capabilities_from_ast(self) -> List[str]:
        """Analyze AST to determine capabilities"""
        capabilities = []

        class CapabilityVisitor(ast.NodeVisitor):
            def __init__(self):
                self.capabilities = []

            def visit_Call(self, node):
                if isinstance(node.func, ast.Name):
                    func_name = node.func.id.lower()
                    if "analyze" in func_name:
                        self.capabilities.append("Can analyze data structures")
                    elif "process" in func_name:
                        self.capabilities.append("Can process information")
                    elif "handle" in func_name:
                        self.capabilities.append("Can handle events")
                    elif "generate" in func_name:
                        self.capabilities.append("Can generate outputs")
                self.generic_visit(node)

            def visit_If(self, node):
                self.capabilities.append("Can make conditional decisions")
                self.generic_visit(node)

            def visit_For(self, node):
                self.capabilities.append("Can iterate over collections")
                self.generic_visit(node)

            def visit_While(self, node):
                self.capabilities.append("Can perform iterative operations")
                self.generic_visit(node)

        visitor = CapabilityVisitor()
        visitor.visit(self.ast_tree)
        return visitor.capabilities

    def _analyze_limitations_from_code(self) -> List[str]:
        """Analyze source code to determine limitations"""
        limitations = []
        source_lower = self.function_source.lower()

        # Pattern-based limitation detection
        limitation_patterns = {
            "requires_input": ["requires", "needs", "expects", "depends on"],
            "cannot_operate_alone": ["cannot", "unable", "requires", "needs"],
            "limited_by_context": ["context", "environment", "state", "condition"],
            "error_handling": ["try", "except", "error", "exception"],
            "validation_required": ["validate", "check", "verify", "confirm"],
        }

        for limitation, patterns in limitation_patterns.items():
            if any(pattern in source_lower for pattern in patterns):
                limitations.append(f"Limited by {limitation.replace('_', ' ')}")

        # Error handling analysis
        if "try:" in source_lower and "except" in source_lower:
            limitations.append(
                "Requires error handling and may fail under certain conditions"
            )

        # Dependency analysis
        if "import" in source_lower:
            limitations.append(
                "Depends on external modules and may fail if dependencies are missing"
            )

        return list(set(limitations))

    def _analyze_dependencies_from_code(self) -> List[str]:
        """Analyze source code to determine dependencies"""
        dependencies = []
        source_lines = self.function_source.split("\n")

        for line in source_lines:
            line = line.strip()
            if line.startswith("from ") and " import " in line:
                module = line.split(" import ")[0].replace("from ", "")
                dependencies.append(module)
            elif line.startswith("import "):
                module = line.replace("import ", "").split()[0]
                dependencies.append(module)

        return list(set(dependencies))

    def _analyze_inputs_from_signature(
        self, parameters: Dict[str, inspect.Parameter]
    ) -> List[str]:
        """Analyze function signature to determine accepted inputs"""
        inputs = []

        for param_name, param in parameters.items():
            param_type = (
                param.annotation
                if param.annotation != inspect.Parameter.empty
                else "Any"
            )
            param_type_str = str(param_type)

            # Simplify type annotations
            if hasattr(param_type, "__name__"):
                param_type_str = param_type.__name__
            elif hasattr(param_type, "__origin__"):
                origin = get_origin(param_type)
                if origin:
                    param_type_str = str(origin)

            inputs.append(f"{param_name}: {param_type_str}")

        return inputs

    def _analyze_outputs_from_code(self) -> List[str]:
        """Analyze source code to determine produced outputs"""
        outputs = []
        source_lower = self.function_source.lower()

        # Pattern-based output detection
        output_patterns = {
            "state_updates": ["state", "update", "modify", "change"],
            "messages": ["message", "msg", "response", "reply"],
            "logs": ["log", "logging", "debug", "info"],
            "data": ["data", "result", "output", "return"],
            "telemetry": ["telemetry", "metrics", "stats", "analytics"],
        }

        for output_type, patterns in output_patterns.items():
            if any(pattern in source_lower for pattern in patterns):
                outputs.append(f"Produces {output_type.replace('_', ' ')}")

        # Return statement analysis
        if "return" in source_lower:
            outputs.append("Returns computed results")

        return list(set(outputs))

    def _analyze_knowledge_domains_from_code(self) -> List[str]:
        """Analyze source code to determine knowledge domains"""
        domains = []
        source_lower = self.function_source.lower()

        # Domain-specific pattern detection
        domain_patterns = {
            "browser_automation": ["browser", "page", "element", "click", "navigate"],
            "web_scraping": ["scrape", "parse", "html", "dom", "element"],
            "form_handling": ["form", "input", "submit", "field", "validation"],
            "state_management": ["state", "context", "session", "persist"],
            "error_recovery": ["error", "exception", "recover", "retry", "fallback"],
            "navigation": ["navigate", "route", "path", "step", "flow"],
            "verification": ["verify", "validate", "check", "test", "confirm"],
            "investigation": ["investigate", "analyze", "examine", "diagnose"],
            "communication": ["message", "communicate", "report", "respond"],
        }

        for domain, patterns in domain_patterns.items():
            if any(pattern in source_lower for pattern in patterns):
                domains.append(domain.replace("_", " ").title())

        return list(set(domains))

    def _analyze_unknown_areas_from_code(self) -> List[str]:
        """Analyze source code to determine unknown areas"""
        unknowns = []
        source_lower = self.function_source.lower()

        # Pattern-based unknown detection
        unknown_patterns = {
            "external_systems": ["external", "api", "service", "remote"],
            "user_input": ["user", "input", "interactive", "prompt"],
            "dynamic_content": ["dynamic", "variable", "unknown", "unpredictable"],
            "network_issues": ["network", "connection", "timeout", "retry"],
            "environment_dependencies": [
                "environment",
                "config",
                "setting",
                "variable",
            ],
        }

        for unknown_area, patterns in unknown_patterns.items():
            if any(pattern in source_lower for pattern in patterns):
                unknowns.append(f"Unknown behavior in {unknown_area.replace('_', ' ')}")

        return list(set(unknowns))

    def _calculate_confidence_levels_from_code(self) -> Dict[str, float]:
        """Calculate confidence levels based on code analysis"""
        confidence = {}

        # Analyze code quality indicators
        source_lines = self.function_source.split("\n")
        total_lines = len([line for line in source_lines if line.strip()])

        # Error handling confidence
        error_handling_score = 0.0
        if "try:" in self.function_source and "except" in self.function_source:
            error_handling_score += 0.3
        if "if" in self.function_source:
            error_handling_score += 0.2
        if "return" in self.function_source:
            error_handling_score += 0.2
        if "log" in self.function_source.lower():
            error_handling_score += 0.3

        confidence["error_handling"] = min(error_handling_score, 1.0)

        # Type safety confidence
        type_safety_score = 0.5  # Base score
        if self.type_hints:
            type_safety_score += 0.3
        if "typing" in str(self.type_hints):
            type_safety_score += 0.2

        confidence["type_safety"] = min(type_safety_score, 1.0)

        # Documentation confidence
        doc_confidence = 0.3  # Base score
        if self.target_function.__doc__:
            doc_confidence += 0.4
        if "TODO" not in self.function_source and "FIXME" not in self.function_source:
            doc_confidence += 0.3

        confidence["documentation"] = min(doc_confidence, 1.0)

        # Overall confidence
        confidence["overall"] = sum(confidence.values()) / len(confidence)

        return confidence

    def _analyze_code_complexity(self) -> Dict[str, Any]:
        """Analyze code complexity metrics"""
        complexity = {}

        if not self.ast_tree:
            return {"error": "Cannot analyze complexity - AST parsing failed"}

        class ComplexityVisitor(ast.NodeVisitor):
            def __init__(self):
                self.cyclomatic_complexity = 1  # Base complexity
                self.line_count = 0
                self.function_calls = 0
                self.conditionals = 0
                self.loops = 0

            def visit_Call(self, node):
                self.function_calls += 1
                self.generic_visit(node)

            def visit_If(self, node):
                self.cyclomatic_complexity += 1
                self.conditionals += 1
                self.generic_visit(node)

            def visit_For(self, node):
                self.cyclomatic_complexity += 1
                self.loops += 1
                self.generic_visit(node)

            def visit_While(self, node):
                self.cyclomatic_complexity += 1
                self.loops += 1
                self.generic_visit(node)

            def visit_ExceptHandler(self, node):
                self.cyclomatic_complexity += 1
                self.generic_visit(node)

        visitor = ComplexityVisitor()
        visitor.visit(self.ast_tree)

        complexity["cyclomatic_complexity"] = visitor.cyclomatic_complexity
        complexity["function_calls"] = visitor.function_calls
        complexity["conditionals"] = visitor.conditionals
        complexity["loops"] = visitor.loops
        complexity["complexity_rating"] = self._rate_complexity(
            visitor.cyclomatic_complexity
        )

        return complexity

    def _rate_complexity(self, complexity: int) -> str:
        """Rate complexity level"""
        if complexity <= 5:
            return "Low"
        elif complexity <= 10:
            return "Medium"
        elif complexity <= 20:
            return "High"
        else:
            return "Very High"

    def get_self_documentation(self) -> Dict[str, Any]:
        """Dynamically generate comprehensive self-documentation"""
        return {
            "component_name": self.component_name,
            "function_name": self.target_function.__name__,
            "module": self.target_function.__module__,
            "docstring": self.target_function.__doc__ or "No docstring available",
            "source_file": self.target_function.__code__.co_filename,
            "line_number": self.target_function.__code__.co_firstlineno,
            "parameters": self._get_dynamic_parameters(),
            "capabilities": self.component_map.capabilities,
            "limitations": self.component_map.limitations,
            "dependencies": self.component_map.dependencies,
            "knowledge_domains": self.component_map.knowledge_domains,
            "code_complexity": self.component_map.code_complexity,
            "confidence_levels": self.component_map.confidence_levels,
            "rmddd_compliance": self._assess_rmddd_compliance(),
            "analysis_timestamp": self.component_map.analysis_timestamp.isoformat(),
            "dynamic_analysis": True,
        }

    def _get_dynamic_parameters(self) -> Dict[str, Any]:
        """Dynamically extract function parameters"""
        sig = inspect.signature(self.target_function)
        parameters = {}

        for name, param in sig.parameters.items():
            parameters[name] = {
                "name": name,
                "type": (
                    param.annotation
                    if param.annotation != inspect.Parameter.empty
                    else "Any"
                ),
                "default": (
                    param.default if param.default != inspect.Parameter.empty else None
                ),
                "required": param.default == inspect.Parameter.empty,
                "kind": str(param.kind),
            }

        return parameters

    def _assess_rmddd_compliance(self) -> Dict[str, bool]:
        """Dynamically assess RMDDD compliance"""
        compliance = {}

        # Modularity assessment
        compliance["modular"] = len(self.component_map.dependencies) > 0

        # Testability assessment
        compliance["testable"] = "return" in self.function_source.lower()

        # Documentation assessment
        compliance["documented"] = bool(self.target_function.__doc__)

        # Single responsibility assessment
        complexity = self.component_map.code_complexity.get("cyclomatic_complexity", 0)
        compliance["single_responsibility"] = complexity <= 10

        # Overall compliance
        compliance["overall_compliant"] = all(compliance.values())

        return compliance

    def create_safe_command_line(self) -> argparse.ArgumentParser:
        """Dynamically create safe command line interface"""
        parser = argparse.ArgumentParser(
            description=f"Dynamic command line interface for {self.component_name}",
            formatter_class=argparse.RawDescriptionHelpFormatter,
            epilog=self._generate_command_line_epilog(),
        )

        # Dynamic argument generation based on function parameters
        sig = inspect.signature(self.target_function)
        for name, param in sig.parameters.items():
            if name == "state":  # Skip LangGraph state parameter
                continue

            if param.annotation != inspect.Parameter.empty:
                arg_type = self._convert_type_to_argparse_type(param.annotation)
                parser.add_argument(
                    f"--{name}",
                    type=arg_type,
                    help=f"Parameter: {name} ({param.annotation})",
                )
            else:
                parser.add_argument(f"--{name}", help=f"Parameter: {name}")

        # Standard RMDDD interface arguments
        parser.add_argument(
            "--test",
            action="store_true",
            help="Test the component with safe default inputs",
        )
        parser.add_argument(
            "--interactive",
            action="store_true",
            help="Run in interactive mode for exploration",
        )
        parser.add_argument(
            "--docs", action="store_true", help="Show dynamic documentation"
        )
        parser.add_argument(
            "--component-map", action="store_true", help="Show dynamic component map"
        )
        parser.add_argument(
            "--babble-fish",
            type=str,
            help="Ask a question to the component's babble fish",
        )
        parser.add_argument(
            "--analyze", action="store_true", help="Show dynamic code analysis"
        )

        return parser

    def _convert_type_to_argparse_type(self, type_annotation) -> type:
        """Convert type annotation to argparse type"""
        if type_annotation == str:
            return str
        elif type_annotation == int:
            return int
        elif type_annotation == float:
            return float
        elif type_annotation == bool:
            return bool
        else:
            return str  # Default to string

    def _generate_command_line_epilog(self) -> str:
        """Generate command line epilog with examples"""
        return f"""
Examples:
  # Test with dynamic analysis
  python {self.component_name}.py --test --analyze
  
  # Interactive exploration
  python {self.component_name}.py --interactive
  
  # Show dynamic documentation
  python {self.component_name}.py --docs
  
  # Show component map
  python {self.component_name}.py --component-map
  
  # Ask babble fish
  python {self.component_name}.py --babble-fish "What can you do?"
        """

    def babble_fish_ask(self, question: str) -> DynamicBabbleFishResponse:
        """Dynamically answer questions using code analysis"""
        question_lower = question.lower()

        # Route to appropriate dynamic handler
        if "what" in question_lower and "do" in question_lower:
            return self._handle_dynamic_capability_question(question)
        elif "what" in question_lower and (
            "can't" in question_lower or "cannot" in question_lower
        ):
            return self._handle_dynamic_limitation_question(question)
        elif "what" in question_lower and "depend" in question_lower:
            return self._handle_dynamic_dependency_question(question)
        elif "how" in question_lower and "complex" in question_lower:
            return self._handle_dynamic_complexity_question(question)
        elif "what" in question_lower and "know" in question_lower:
            return self._handle_dynamic_knowledge_question(question)
        else:
            return self._handle_dynamic_general_question(question)

    def _handle_dynamic_capability_question(
        self, question: str
    ) -> DynamicBabbleFishResponse:
        """Handle capability questions with dynamic analysis"""
        capabilities = self.component_map.capabilities
        confidence = self.component_map.confidence_levels.get("overall", 0.7)

        return DynamicBabbleFishResponse(
            question=question,
            answer=f"Based on dynamic code analysis, {self.component_name} can: "
            + "; ".join(capabilities[:3])
            + (
                f" and {len(capabilities)-3} more capabilities"
                if len(capabilities) > 3
                else ""
            ),
            confidence=confidence,
            knowledge_source="Dynamic code analysis and AST parsing",
            limitations=self.component_map.limitations,
            follow_up_suggestions=[
                "What are the limitations?",
                "How complex is the code?",
                "What does it depend on?",
            ],
            related_capabilities=capabilities,
            code_references=[
                f"Analyzed {self.target_function.__name__} in {self.target_function.__module__}"
            ],
        )

    def _handle_dynamic_limitation_question(
        self, question: str
    ) -> DynamicBabbleFishResponse:
        """Handle limitation questions with dynamic analysis"""
        limitations = self.component_map.limitations
        unknowns = self.component_map.unknown_areas

        return DynamicBabbleFishResponse(
            question=question,
            answer=f"Based on dynamic code analysis, {self.component_name} has limitations: "
            + "; ".join(limitations[:2])
            + f". Also has unknown areas: "
            + "; ".join(unknowns[:2]),
            confidence=0.8,
            knowledge_source="Dynamic limitation and unknown area analysis",
            limitations=limitations,
            follow_up_suggestions=[
                "What can it do?",
                "How confident is it?",
                "What are the dependencies?",
            ],
            related_capabilities=self.component_map.capabilities,
            code_references=["Code pattern analysis", "Error handling analysis"],
        )

    def _handle_dynamic_dependency_question(
        self, question: str
    ) -> DynamicBabbleFishResponse:
        """Handle dependency questions with dynamic analysis"""
        dependencies = self.component_map.dependencies

        return DynamicBabbleFishResponse(
            question=question,
            answer=(
                f"Based on dynamic import analysis, {self.component_name} depends on: "
                + "; ".join(dependencies)
                if dependencies
                else "No external dependencies detected"
            ),
            confidence=0.9,
            knowledge_source="Dynamic import statement analysis",
            limitations=[],
            follow_up_suggestions=[
                "What are the capabilities?",
                "What are the limitations?",
                "How complex is the code?",
            ],
            related_capabilities=["Dependency management", "Module integration"],
            code_references=["Import statement analysis", "Module dependency tracking"],
        )

    def _handle_dynamic_complexity_question(
        self, question: str
    ) -> DynamicBabbleFishResponse:
        """Handle complexity questions with dynamic analysis"""
        complexity = self.component_map.code_complexity
        rating = complexity.get("complexity_rating", "Unknown")
        cyclomatic = complexity.get("cyclomatic_complexity", 0)

        return DynamicBabbleFishResponse(
            question=question,
            answer=f"Based on dynamic AST analysis, {self.component_name} has {rating} complexity "
            + f"(cyclomatic complexity: {cyclomatic}). "
            + f"Contains {complexity.get('function_calls', 0)} function calls, "
            + f"{complexity.get('conditionals', 0)} conditionals, and {complexity.get('loops', 0)} loops.",
            confidence=0.9,
            knowledge_source="Dynamic AST complexity analysis",
            limitations=[],
            follow_up_suggestions=[
                "What are the capabilities?",
                "Is it RMDDD compliant?",
                "What are the confidence levels?",
            ],
            related_capabilities=["Code analysis", "Complexity assessment"],
            code_references=["AST parsing", "Cyclomatic complexity calculation"],
        )

    def _handle_dynamic_knowledge_question(
        self, question: str
    ) -> DynamicBabbleFishResponse:
        """Handle knowledge questions with dynamic analysis"""
        domains = self.component_map.knowledge_domains
        unknowns = self.component_map.unknown_areas

        return DynamicBabbleFishResponse(
            question=question,
            answer=(
                f"Based on dynamic code analysis, {self.component_name} knows about: "
                + "; ".join(domains)
                if domains
                else (
                    "No specific domains detected. "
                    + f"Unknown areas: "
                    + "; ".join(unknowns[:2])
                    if unknowns
                    else "No unknown areas detected"
                )
            ),
            confidence=0.8,
            knowledge_source="Dynamic knowledge domain analysis",
            limitations=unknowns,
            follow_up_suggestions=[
                "What are the limitations?",
                "What can it do?",
                "How confident is it?",
            ],
            related_capabilities=self.component_map.capabilities,
            code_references=["Pattern matching", "Domain keyword analysis"],
        )

    def _handle_dynamic_general_question(
        self, question: str
    ) -> DynamicBabbleFishResponse:
        """Handle general questions with dynamic analysis"""
        return DynamicBabbleFishResponse(
            question=question,
            answer=f"I'm {self.component_name}, dynamically analyzed from code. "
            + f"I have {len(self.component_map.capabilities)} capabilities, "
            + f"{len(self.component_map.limitations)} limitations, and "
            + f"{len(self.component_map.dependencies)} dependencies. "
            + f"My RMDDD compliance is {self._assess_rmddd_compliance()['overall_compliant']}.",
            confidence=0.7,
            knowledge_source="Dynamic general analysis",
            limitations=self.component_map.limitations,
            follow_up_suggestions=[
                "What can you do?",
                "What are your limitations?",
                "How complex is your code?",
                "What do you depend on?",
            ],
            related_capabilities=self.component_map.capabilities,
            code_references=["General code analysis", "RMDDD compliance assessment"],
        )


def create_dynamic_rmddd_interface(
    target_function: Callable, component_name: str
) -> RMDDDBaseInterface:
    """Factory function to create dynamic RMDDD interface for any function"""
    return RMDDDBaseInterface(target_function, component_name)
