#!/usr/bin/env python3
"""
RMDDD Interface Standards
========================

Every RMDDD-conforming LangGraph node must have:
1. Self-documenting interface
2. Safe command line interface
3. Component map (knowledge graph)
4. Babble fish (Q&A interface)
"""

from typing import Dict, Any, List, Optional, Callable
from dataclasses import dataclass, asdict
from abc import ABC, abstractmethod
import json
import argparse
from datetime import datetime


@dataclass
class ComponentMap:
    """Knowledge graph/map of what the component knows and doesn't know"""

    component_name: str
    capabilities: List[str]
    limitations: List[str]
    dependencies: List[str]
    inputs_accepted: List[str]
    outputs_produced: List[str]
    knowledge_domains: List[str]
    unknown_areas: List[str]
    confidence_levels: Dict[str, float]
    last_updated: datetime


@dataclass
class BabbleFishResponse:
    """Response from the component's Q&A interface"""

    question: str
    answer: str
    confidence: float
    knowledge_source: str
    limitations: List[str]
    follow_up_suggestions: List[str]
    related_capabilities: List[str]


class RMDDDInterface(ABC):
    """Base interface that every RMDDD-conforming LangGraph node must implement"""

    def __init__(self, name: str):
        self.name = name
        self.component_map: Optional[ComponentMap] = None
        self.babble_fish_questions: List[str] = []
        self.command_line_args: Dict[str, Any] = {}

    @abstractmethod
    def get_self_documentation(self) -> Dict[str, Any]:
        """Return comprehensive self-documentation"""
        pass

    @abstractmethod
    def create_safe_command_line(self) -> argparse.ArgumentParser:
        """Create safe command line interface"""
        pass

    @abstractmethod
    def build_component_map(self) -> ComponentMap:
        """Build knowledge graph/map of component capabilities"""
        pass

    @abstractmethod
    def babble_fish_ask(self, question: str) -> BabbleFishResponse:
        """Answer questions about what the component knows and doesn't know"""
        pass

    def get_interface_summary(self) -> Dict[str, Any]:
        """Get summary of all interfaces"""
        return {
            "name": self.name,
            "documentation": self.get_self_documentation(),
            "component_map": (
                asdict(self.build_component_map()) if self.component_map else None
            ),
            "command_line_help": self.create_safe_command_line().format_help(),
            "babble_fish_questions": self.babble_fish_questions,
        }


class LangGraphNodeRMDDDInterface(RMDDDInterface):
    """RMDDD interface for LangGraph nodes"""

    def __init__(self, node_function: Callable, node_name: str):
        super().__init__(node_name)
        self.node_function = node_function
        self.node_name = node_name
        self.component_map = self.build_component_map()

    def get_self_documentation(self) -> Dict[str, Any]:
        """Return comprehensive self-documentation for the LangGraph node"""
        doc = {
            "node_name": self.node_name,
            "node_type": "LangGraph Node",
            "function_name": self.node_function.__name__,
            "docstring": self.node_function.__doc__ or "No docstring available",
            "module": self.node_function.__module__,
            "file": self.node_function.__code__.co_filename,
            "line_number": self.node_function.__code__.co_firstlineno,
            "parameters": self._get_function_parameters(),
            "purpose": self._infer_purpose(),
            "usage": self._get_usage_examples(),
            "integration": self._get_integration_info(),
            "testing": self._get_testing_info(),
            "rmddd_compliance": {
                "modular": True,
                "testable": True,
                "documented": True,
                "single_responsibility": True,
            },
            "last_updated": datetime.now().isoformat(),
        }
        return doc

    def create_safe_command_line(self) -> argparse.ArgumentParser:
        """Create safe command line interface for testing/debugging the node"""
        parser = argparse.ArgumentParser(
            description=f"Safe command line interface for {self.node_name}",
            formatter_class=argparse.RawDescriptionHelpFormatter,
            epilog=f"""
Examples:
  # Test with default state
  python {self.node_name}.py --test
  
  # Test with custom state
  python {self.node_name}.py --test --state-file custom_state.json
  
  # Interactive mode
  python {self.node_name}.py --interactive
  
  # Documentation mode
  python {self.node_name}.py --docs
  
  # Babble fish mode
  python {self.node_name}.py --babble-fish "What does this node do?"
            """,
        )

        # Safe testing options
        parser.add_argument(
            "--test", action="store_true", help="Test the node with safe default inputs"
        )
        parser.add_argument(
            "--interactive",
            action="store_true",
            help="Run in interactive mode for exploration",
        )
        parser.add_argument(
            "--state-file", type=str, help="Load state from JSON file for testing"
        )
        parser.add_argument("--output-file", type=str, help="Save results to JSON file")

        # Documentation options
        parser.add_argument(
            "--docs", action="store_true", help="Show comprehensive documentation"
        )
        parser.add_argument(
            "--component-map", action="store_true", help="Show component knowledge map"
        )
        parser.add_argument(
            "--interface", action="store_true", help="Show interface summary"
        )

        # Babble fish options
        parser.add_argument(
            "--babble-fish",
            type=str,
            help="Ask a question to the component's babble fish",
        )
        parser.add_argument(
            "--list-questions",
            action="store_true",
            help="List common questions for babble fish",
        )

        # Safety options
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Show what would be done without executing",
        )
        parser.add_argument(
            "--validate-only",
            action="store_true",
            help="Only validate inputs, don't execute",
        )

        return parser

    def build_component_map(self) -> ComponentMap:
        """Build knowledge graph/map of component capabilities"""
        # Analyze the node function to determine capabilities
        capabilities = self._analyze_capabilities()
        limitations = self._analyze_limitations()
        dependencies = self._analyze_dependencies()

        return ComponentMap(
            component_name=self.node_name,
            capabilities=capabilities,
            limitations=limitations,
            dependencies=dependencies,
            inputs_accepted=self._get_accepted_inputs(),
            outputs_produced=self._get_produced_outputs(),
            knowledge_domains=self._get_knowledge_domains(),
            unknown_areas=self._get_unknown_areas(),
            confidence_levels=self._get_confidence_levels(),
            last_updated=datetime.now(),
        )

    def babble_fish_ask(self, question: str) -> BabbleFishResponse:
        """Answer questions about what the component knows and doesn't know"""
        question_lower = question.lower()

        # Route questions to appropriate handlers
        if "what" in question_lower and "do" in question_lower:
            return self._handle_capability_question(question)
        elif "how" in question_lower:
            return self._handle_how_question(question)
        elif "what" in question_lower and (
            "input" in question_lower or "accept" in question_lower
        ):
            return self._handle_input_question(question)
        elif "what" in question_lower and (
            "output" in question_lower or "produce" in question_lower
        ):
            return self._handle_output_question(question)
        elif "what" in question_lower and (
            "depend" in question_lower or "require" in question_lower
        ):
            return self._handle_dependency_question(question)
        elif "what" in question_lower and (
            "limitation" in question_lower or "can't" in question_lower
        ):
            return self._handle_limitation_question(question)
        elif "what" in question_lower and (
            "know" in question_lower or "understand" in question_lower
        ):
            return self._handle_knowledge_question(question)
        elif "what" in question_lower and (
            "don't" in question_lower or "unknown" in question_lower
        ):
            return self._handle_unknown_question(question)
        else:
            return self._handle_general_question(question)

    def _get_function_parameters(self) -> Dict[str, Any]:
        """Extract function parameters and their types"""
        import inspect

        sig = inspect.signature(self.node_function)
        params = {}
        for name, param in sig.parameters.items():
            params[name] = {
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
            }
        return params

    def _infer_purpose(self) -> str:
        """Infer the purpose of the node from its name and docstring"""
        name_lower = self.node_name.lower()
        if "ghostbusters" in name_lower:
            return "Ghostbusters consultation and investigation for low-confidence scenarios"
        elif "session_recovery" in name_lower:
            return "Session recovery and state analysis for navigation scenarios"
        elif "interactive_recovery" in name_lower:
            return "Interactive recovery and user guidance for confused states"
        elif "prompt_mode" in name_lower:
            return "Prompt mode for conversational decision-making"
        elif "browser_connection" in name_lower:
            return "Browser connection and session management"
        elif "page_detection" in name_lower:
            return "Page type detection and analysis"
        elif "form_analysis" in name_lower:
            return "Form structure analysis and field identification"
        elif "navigation" in name_lower:
            return "Navigation strategy selection and execution"
        elif "verification" in name_lower:
            return "System verification and integration testing"
        else:
            return f"LangGraph node for {self.node_name} functionality"

    def _get_usage_examples(self) -> List[str]:
        """Get usage examples for the node"""
        return [
            f"# Basic usage in LangGraph workflow",
            f"workflow.add_node('{self.node_name}', {self.node_function.__name__})",
            f"",
            f"# Direct invocation with state",
            f"result = {self.node_function.__name__}(state)",
            f"",
            f"# Testing with command line",
            f"python {self.node_name}.py --test",
            f"python {self.node_name}.py --interactive",
        ]

    def _get_integration_info(self) -> Dict[str, Any]:
        """Get integration information"""
        return {
            "langgraph_compatible": True,
            "state_management": "TypedDict state",
            "error_handling": "Graceful error handling with recovery",
            "logging": "Comprehensive logging and telemetry",
            "testing": "Unit and integration test support",
        }

    def _get_testing_info(self) -> Dict[str, Any]:
        """Get testing information"""
        return {
            "unit_tests": f"test_{self.node_name}.py",
            "integration_tests": f"test_{self.node_name}_integration.py",
            "command_line_tests": f"python {self.node_name}.py --test",
            "interactive_tests": f"python {self.node_name}.py --interactive",
            "validation_tests": f"python {self.node_name}.py --validate-only",
        }

    def _analyze_capabilities(self) -> List[str]:
        """Analyze what the component can do"""
        capabilities = []
        name_lower = self.node_name.lower()

        if "ghostbusters" in name_lower:
            capabilities.extend(
                [
                    "Investigate low-confidence scenarios",
                    "Analyze page structure and navigation",
                    "Perform diagnostic testing",
                    "Generate investigation reports",
                    "Handle completely confused states",
                ]
            )
        elif "session_recovery" in name_lower:
            capabilities.extend(
                [
                    "Analyze page similarity",
                    "Calculate confidence scores",
                    "Route to appropriate navigation strategies",
                    "Handle multi-dimensional context analysis",
                ]
            )
        elif "verification" in name_lower:
            capabilities.extend(
                [
                    "Analyze execution characteristics",
                    "Analyze state mutations",
                    "Analyze performance metrics",
                    "Combine verification results",
                    "Generate verification reports",
                ]
            )

        return capabilities

    def _analyze_limitations(self) -> List[str]:
        """Analyze what the component cannot do"""
        limitations = []
        name_lower = self.node_name.lower()

        if "ghostbusters" in name_lower:
            limitations.extend(
                [
                    "Cannot make decisions without human input in critical scenarios",
                    "Cannot navigate without confidence thresholds",
                    "Cannot operate without proper state context",
                ]
            )
        elif "verification" in name_lower:
            limitations.extend(
                [
                    "Cannot verify components without execution data",
                    "Cannot provide 100% confidence in all scenarios",
                    "Cannot analyze components without proper interfaces",
                ]
            )

        return limitations

    def _analyze_dependencies(self) -> List[str]:
        """Analyze component dependencies"""
        dependencies = []
        name_lower = self.node_name.lower()

        if "ghostbusters" in name_lower:
            dependencies.extend(
                [
                    "investigation_modules.PageStructureAnalyzer",
                    "investigation_modules.NavigationAnalyzer",
                    "investigation_modules.ContentAnalyzer",
                    "investigation_modules.DiagnosticTester",
                    "investigation_modules.InvestigationOrchestrator",
                ]
            )
        elif "verification" in name_lower:
            dependencies.extend(
                [
                    "verification_modules.ExecutionAnalyzer",
                    "verification_modules.StateMutationAnalyzer",
                    "verification_modules.PerformanceAnalyzer",
                    "verification_modules.ResultCombiner",
                    "verification_modules.VerificationReporter",
                ]
            )

        return dependencies

    def _get_accepted_inputs(self) -> List[str]:
        """Get accepted input types"""
        return ["TypedDict state", "Context data", "Configuration parameters"]

    def _get_produced_outputs(self) -> List[str]:
        """Get produced output types"""
        return ["Updated state", "Messages", "Logs", "Telemetry data"]

    def _get_knowledge_domains(self) -> List[str]:
        """Get knowledge domains"""
        name_lower = self.node_name.lower()
        domains = []

        if "ghostbusters" in name_lower:
            domains.extend(
                ["Page analysis", "Navigation strategies", "Confidence assessment"]
            )
        elif "verification" in name_lower:
            domains.extend(
                ["System verification", "Performance analysis", "Integration testing"]
            )
        elif "recovery" in name_lower:
            domains.extend(["Session recovery", "State analysis", "Context evaluation"])

        return domains

    def _get_unknown_areas(self) -> List[str]:
        """Get areas where the component has limited knowledge"""
        return [
            "Future state changes",
            "External system behavior",
            "User-specific preferences",
            "Dynamic content variations",
        ]

    def _get_confidence_levels(self) -> Dict[str, float]:
        """Get confidence levels for different capabilities"""
        return {
            "core_functionality": 0.9,
            "error_handling": 0.8,
            "integration": 0.7,
            "edge_cases": 0.6,
        }

    def _handle_capability_question(self, question: str) -> BabbleFishResponse:
        """Handle questions about what the component can do"""
        return BabbleFishResponse(
            question=question,
            answer=f"The {self.node_name} can: "
            + "; ".join(self.component_map.capabilities),
            confidence=0.9,
            knowledge_source="Component analysis",
            limitations=self.component_map.limitations,
            follow_up_suggestions=[
                "What are the limitations?",
                "What inputs does it accept?",
                "What outputs does it produce?",
            ],
            related_capabilities=self.component_map.capabilities,
        )

    def _handle_how_question(self, question: str) -> BabbleFishResponse:
        """Handle 'how' questions"""
        return BabbleFishResponse(
            question=question,
            answer=f"The {self.node_name} operates by analyzing state and applying specialized logic for its domain.",
            confidence=0.8,
            knowledge_source="Component design",
            limitations=["Cannot explain implementation details without code analysis"],
            follow_up_suggestions=[
                "What are the key steps?",
                "What inputs are required?",
                "What are the dependencies?",
            ],
            related_capabilities=["Process execution", "State management"],
        )

    def _handle_input_question(self, question: str) -> BabbleFishResponse:
        """Handle questions about inputs"""
        return BabbleFishResponse(
            question=question,
            answer=f"The {self.node_name} accepts: "
            + "; ".join(self.component_map.inputs_accepted),
            confidence=0.9,
            knowledge_source="Interface analysis",
            limitations=[],
            follow_up_suggestions=[
                "What outputs does it produce?",
                "What are the dependencies?",
                "How do I provide the inputs?",
            ],
            related_capabilities=["Input validation", "Data processing"],
        )

    def _handle_output_question(self, question: str) -> BabbleFishResponse:
        """Handle questions about outputs"""
        return BabbleFishResponse(
            question=question,
            answer=f"The {self.node_name} produces: "
            + "; ".join(self.component_map.outputs_produced),
            confidence=0.9,
            knowledge_source="Interface analysis",
            limitations=[],
            follow_up_suggestions=[
                "What inputs does it accept?",
                "What are the dependencies?",
                "How do I use the outputs?",
            ],
            related_capabilities=["Output generation", "State updates"],
        )

    def _handle_dependency_question(self, question: str) -> BabbleFishResponse:
        """Handle questions about dependencies"""
        return BabbleFishResponse(
            question=question,
            answer=f"The {self.node_name} depends on: "
            + "; ".join(self.component_map.dependencies),
            confidence=0.9,
            knowledge_source="Dependency analysis",
            limitations=[],
            follow_up_suggestions=[
                "What are the capabilities?",
                "What are the limitations?",
                "How do I install dependencies?",
            ],
            related_capabilities=["Dependency management", "Integration"],
        )

    def _handle_limitation_question(self, question: str) -> BabbleFishResponse:
        """Handle questions about limitations"""
        return BabbleFishResponse(
            question=question,
            answer=f"The {self.node_name} cannot: "
            + "; ".join(self.component_map.limitations),
            confidence=0.9,
            knowledge_source="Capability analysis",
            limitations=[],
            follow_up_suggestions=[
                "What can it do?",
                "What are the alternatives?",
                "How do I work around limitations?",
            ],
            related_capabilities=["Capability assessment", "Workaround suggestions"],
        )

    def _handle_knowledge_question(self, question: str) -> BabbleFishResponse:
        """Handle questions about knowledge"""
        return BabbleFishResponse(
            question=question,
            answer=f"The {self.node_name} knows about: "
            + "; ".join(self.component_map.knowledge_domains),
            confidence=0.8,
            knowledge_source="Knowledge domain analysis",
            limitations=self.component_map.unknown_areas,
            follow_up_suggestions=[
                "What doesn't it know?",
                "What are the limitations?",
                "How confident is it?",
            ],
            related_capabilities=["Knowledge assessment", "Domain expertise"],
        )

    def _handle_unknown_question(self, question: str) -> BabbleFishResponse:
        """Handle questions about unknowns"""
        return BabbleFishResponse(
            question=question,
            answer=f"The {self.node_name} doesn't know about: "
            + "; ".join(self.component_map.unknown_areas),
            confidence=0.9,
            knowledge_source="Unknown area analysis",
            limitations=[],
            follow_up_suggestions=[
                "What does it know?",
                "How can I help it learn?",
                "What are the alternatives?",
            ],
            related_capabilities=[
                "Knowledge gap identification",
                "Learning opportunities",
            ],
        )

    def _handle_general_question(self, question: str) -> BabbleFishResponse:
        """Handle general questions"""
        return BabbleFishResponse(
            question=question,
            answer=f"I'm the {self.node_name} component. I can help you understand my capabilities, limitations, inputs, outputs, and dependencies. Try asking more specific questions!",
            confidence=0.7,
            knowledge_source="General knowledge",
            limitations=["Cannot answer questions outside my domain"],
            follow_up_suggestions=[
                "What can you do?",
                "What are your limitations?",
                "How do I use you?",
                "What do you depend on?",
            ],
            related_capabilities=["General assistance", "Question routing"],
        )


def create_rmddd_interface_for_node(
    node_function: Callable, node_name: str
) -> LangGraphNodeRMDDDInterface:
    """Factory function to create RMDDD interface for a LangGraph node"""
    return LangGraphNodeRMDDDInterface(node_function, node_name)
