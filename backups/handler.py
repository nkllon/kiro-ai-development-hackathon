"""Text protocol handler for human-readable structured actions."""

import re
from datetime import datetime
from typing import Callable, Optional

from ..core.reflective_module import HealthIndicator, ModuleStatus, ReflectiveModule
from .models import ActionResult, CommandPattern, StructuredAction, ValidationResult


class TextProtocolHandler(ReflectiveModule):
    """Handler for text-based communication protocol.

    Processes human-readable structured action commands following
    verb-noun-modifier pattern with instant extensibility.
    """

    def __init__(self, instance_id: str):
        super().__init__("TextProtocolHandler", "1.0.0")
        self.instance_id = instance_id
        self.command_patterns: dict[str, CommandPattern] = {}
        self.action_handlers: dict[str, Callable[[StructuredAction], ActionResult]] = {}
        self.command_history: list[StructuredAction] = []
        self.execution_stats = {
            "total_commands": 0,
            "successful_commands": 0,
            "failed_commands": 0,
            "average_execution_time": 0.0,
        }

        # Register default command patterns
        self._register_default_patterns()

    def _register_default_patterns(self) -> None:
        """Register default command patterns."""
        patterns = [
            CommandPattern(
                verb="run",
                noun="task",
                allowed_modifiers=["beast-mode", "parallel", "sequential", "debug"],
                required_parameters=["task_id"],
                optional_parameters=["timeout", "priority", "workspace"],
                description="Execute a task with specified mode",
                examples=[
                    "run task abc beast-mode",
                    "run task xyz parallel timeout=300",
                ],
            ),
            CommandPattern(
                verb="stop",
                noun="instance",
                allowed_modifiers=["graceful", "immediate", "force"],
                required_parameters=["instance_id"],
                optional_parameters=["timeout", "preserve_state"],
                description="Stop a running instance",
                examples=[
                    "stop instance kiro-3 graceful",
                    "stop instance kiro-1 immediate",
                ],
            ),
            CommandPattern(
                verb="sync",
                noun="branch",
                allowed_modifiers=["upstream", "downstream", "bidirectional"],
                required_parameters=["branch_name"],
                optional_parameters=["conflict_strategy", "merge_strategy"],
                description="Synchronize git branch",
                examples=[
                    "sync branch feature/task-1 upstream",
                    "sync branch main bidirectional",
                ],
            ),
            CommandPattern(
                verb="status",
                noun="swarm",
                allowed_modifiers=["detailed", "summary", "health", "performance"],
                required_parameters=[],
                optional_parameters=["format", "filter"],
                description="Get swarm status information",
                examples=["status swarm detailed", "status swarm health"],
            ),
            CommandPattern(
                verb="scale",
                noun="instances",
                allowed_modifiers=["up", "down", "auto"],
                required_parameters=["count"],
                optional_parameters=["resource_type", "deployment_target"],
                description="Scale instance count",
                examples=["scale instances up count=5", "scale instances auto count=3"],
            ),
        ]

        for pattern in patterns:
            self.register_pattern(pattern)

    def register_pattern(self, pattern: CommandPattern) -> None:
        """Register a command pattern for validation."""
        key = f"{pattern.verb}_{pattern.noun}"
        self.command_patterns[key] = pattern
        self.update_activity()

    def register_handler(
        self, verb: str, noun: str, handler: Callable[[StructuredAction], ActionResult]
    ) -> None:
        """Register an action handler."""
        key = f"{verb}_{noun}"
        self.action_handlers[key] = handler
        self.update_activity()

    def parse_command(self, text: str) -> StructuredAction:
        """Parse human-readable text into structured action.

        Supports natural language variations:
        - 'run task abc beast mode' -> verb=run, noun=task, modifiers=[beast-mode]
        - 'execute task xyz in parallel' -> verb=run, noun=task, modifiers=[parallel]
        - 'stop all running threads' -> verb=stop, noun=instances, modifiers=[all]
        """
        try:
            # Normalize text
            normalized = self._normalize_command_text(text)

            # Try direct parsing first
            try:
                action = StructuredAction.from_command_string(
                    normalized, self.instance_id
                )
                self.command_history.append(action)
                return action
            except ValueError:
                # Try natural language parsing
                action = self._parse_natural_language(text)
                self.command_history.append(action)
                return action

        except Exception as e:
            # Create error indicator
            self.add_health_indicator(
                self.create_health_indicator(
                    "command_parsing",
                    "warning",
                    f"Failed to parse command: {text}",
                    {"error": str(e)},
                )
            )
            raise ValueError(f"Failed to parse command '{text}': {e}") from e

    def _normalize_command_text(self, text: str) -> str:
        """Normalize command text for parsing."""
        # Convert common natural language patterns
        replacements = {
            r"\bexecute\b": "run",
            r"\bhalt\b": "stop",
            r"\bin beast mode\b": "beast-mode",
            r"\bin parallel\b": "parallel",
            r"\ball running threads\b": "instances all",
            r"\bactive processes\b": "instances active",
            r"\bgracefully\b": "graceful",  # Convert gracefully to graceful
        }

        normalized = text.lower().strip()
        for pattern, replacement in replacements.items():
            normalized = re.sub(pattern, replacement, normalized)

        return normalized

    def _parse_natural_language(self, text: str) -> StructuredAction:
        """Parse natural language command into structured action."""
        # This is a simplified natural language parser
        # In production, this could use more sophisticated NLP

        words = text.lower().split()

        # Extract verb
        verb_mapping = {
            "execute": "run",
            "start": "run",
            "launch": "run",
            "halt": "stop",
            "kill": "stop",
            "terminate": "stop",
            "synchronize": "sync",
            "update": "sync",
            "check": "status",
            "show": "status",
            "get": "status",
            "increase": "scale",
            "decrease": "scale",
            "resize": "scale",
        }

        verb = None
        for word in words:
            if word in verb_mapping:
                verb = verb_mapping[word]
                break
            elif word in ["run", "stop", "sync", "status", "scale", "merge"]:
                verb = word
                break

        if not verb:
            raise ValueError("Could not identify verb in command")

        # Extract noun
        noun_mapping = {
            "job": "task",
            "jobs": "tasks",
            "agent": "instance",
            "agents": "instances",
            "worker": "instance",
            "workers": "instances",
            "process": "instance",
            "processes": "instances",
            "thread": "instance",
            "threads": "instances",
            "repo": "branch",
            "repository": "branch",
            "cluster": "swarm",
            "group": "swarm",
        }

        noun = None
        for word in words:
            if word in noun_mapping:
                noun = noun_mapping[word]
                break
            elif word in [
                "task",
                "instance",
                "branch",
                "swarm",
                "instances",
                "branches",
            ]:
                noun = word
                break

        if not noun:
            # Default noun based on verb
            default_nouns = {
                "run": "task",
                "stop": "instance",
                "sync": "branch",
                "status": "swarm",
                "scale": "instances",
            }
            noun = default_nouns.get(verb, "task")

        # Extract modifiers and parameters
        modifiers = []
        parameters = {}

        # Check for modifiers in the text
        if "beast" in text.lower() and "mode" in text.lower():
            modifiers.append("beast-mode")
        if "parallel" in text.lower():
            modifiers.append("parallel")
        if "graceful" in text.lower() or "gracefully" in text.lower():
            modifiers.append("graceful")
        if "all" in text.lower():
            modifiers.append("all")
        if "upstream" in text.lower():
            modifiers.append("upstream")

        # Extract identifiers but don't add them as modifiers
        for word in words:
            if word.startswith(("task-", "kiro-", "instance-")):
                if "task" in noun:
                    parameters["task_id"] = word
                else:
                    parameters["instance_id"] = word
            elif word in ["abc", "main"] and len(word) <= 4:  # Simple identifiers
                if "task" in noun:
                    parameters["task_id"] = word
                elif "branch" in noun:
                    parameters["branch_name"] = word

        return StructuredAction(
            verb=verb,
            noun=noun,
            modifiers=modifiers,
            parameters=parameters,
            source_instance=self.instance_id,
        )

    def validate_command(self, action: StructuredAction) -> ValidationResult:
        """Validate command syntax and permissions."""
        key = f"{action.verb}_{action.noun}"

        if key in self.command_patterns:
            pattern = self.command_patterns[key]
            return pattern.validate_action(action)
        else:
            # Unknown command pattern
            return ValidationResult(
                is_valid=False,
                errors=[f"Unknown command pattern: {action.verb} {action.noun}"],
                suggestions=[
                    f"Available patterns: {', '.join(self.command_patterns.keys())}"
                ],
            )

    def execute_action(self, action: StructuredAction) -> ActionResult:
        """Execute structured action and return result."""
        start_time = datetime.now()

        try:
            # Validate action first
            validation = self.validate_command(action)
            if not validation.is_valid:
                return ActionResult(
                    success=False,
                    message=f"Invalid command: {', '.join(validation.errors)}",
                    execution_time=datetime.now() - start_time,
                    correlation_id=action.correlation_id,
                )

            # Find and execute handler
            key = f"{action.verb}_{action.noun}"
            if key in self.action_handlers:
                handler = self.action_handlers[key]
                result = handler(action)

                # Update statistics
                self.execution_stats["total_commands"] += 1
                if result.success:
                    self.execution_stats["successful_commands"] += 1
                else:
                    self.execution_stats["failed_commands"] += 1

                # Update average execution time
                total_time = (
                    self.execution_stats["average_execution_time"]
                    * (self.execution_stats["total_commands"] - 1)
                    + result.execution_time.total_seconds()
                ) / self.execution_stats["total_commands"]
                self.execution_stats["average_execution_time"] = total_time

                self.update_activity()
                return result
            else:
                return ActionResult(
                    success=False,
                    message=f"No handler registered for: {action.verb} {action.noun}",
                    execution_time=datetime.now() - start_time,
                    correlation_id=action.correlation_id,
                )

        except Exception as e:
            self.add_health_indicator(
                self.create_health_indicator(
                    "action_execution",
                    "critical",
                    f"Failed to execute action: {action.to_command_string()}",
                    {"error": str(e), "action": action.model_dump()},
                )
            )

            return ActionResult(
                success=False,
                message=f"Execution failed: {str(e)}",
                execution_time=datetime.now() - start_time,
                correlation_id=action.correlation_id,
            )

    def format_response(self, result: ActionResult) -> str:
        """Format result as human-readable text."""
        return result.to_response_string()

    def get_command_help(
        self, verb: Optional[str] = None, noun: Optional[str] = None
    ) -> str:
        """Get help text for commands."""
        if verb and noun:
            key = f"{verb}_{noun}"
            if key in self.command_patterns:
                pattern = self.command_patterns[key]
                help_text = f"{pattern.verb} {pattern.noun} - {pattern.description}\n"
                if pattern.allowed_modifiers:
                    help_text += f"Modifiers: {', '.join(pattern.allowed_modifiers)}\n"
                if pattern.required_parameters:
                    help_text += f"Required: {', '.join(pattern.required_parameters)}\n"
                if pattern.optional_parameters:
                    help_text += f"Optional: {', '.join(pattern.optional_parameters)}\n"
                if pattern.examples:
                    help_text += "Examples:\n"
                    for example in pattern.examples:
                        help_text += f"  {example}\n"
                return help_text
            else:
                return f"No help available for: {verb} {noun}"
        else:
            # List all available commands
            help_text = "Available commands:\n"
            for _key, pattern in self.command_patterns.items():
                help_text += (
                    f"  {pattern.verb} {pattern.noun} - {pattern.description}\n"
                )
            return help_text

    # ReflectiveModule implementation

    def get_module_status(self) -> ModuleStatus:
        """Get current module status with health indicators."""
        return ModuleStatus(
            module_name=self.name,
            version=self.version,
            status="active" if self.is_healthy() else "error",
            uptime=self.get_uptime(),
            last_activity=self.last_activity,
            health_indicators=self.get_health_indicators(),
            performance_metrics={
                "execution_stats": self.execution_stats,
                "command_history_size": len(self.command_history),
                "registered_patterns": len(self.command_patterns),
                "registered_handlers": len(self.action_handlers),
            },
        )

    def is_healthy(self) -> bool:
        """Check if module is in healthy state."""
        # Check for recent critical health indicators
        recent_indicators = [
            indicator
            for indicator in self._health_indicators
            if (datetime.now() - indicator.timestamp).total_seconds() < 300  # 5 minutes
        ]

        critical_count = sum(
            1 for indicator in recent_indicators if indicator.status == "critical"
        )

        return critical_count == 0

    def get_health_indicators(self) -> list[HealthIndicator]:
        """Get current health indicators."""
        # Add current performance indicator
        success_rate = 0.0
        if self.execution_stats["total_commands"] > 0:
            success_rate = (
                self.execution_stats["successful_commands"]
                / self.execution_stats["total_commands"]
            )

        performance_indicator = self.create_health_indicator(
            "performance",
            (
                "healthy"
                if success_rate >= 0.9
                else "warning" if success_rate >= 0.7 else "critical"
            ),
            f"Command success rate: {success_rate:.2%}",
            {
                "success_rate": success_rate,
                "total_commands": self.execution_stats["total_commands"],
                "average_execution_time": self.execution_stats[
                    "average_execution_time"
                ],
            },
        )

        return self._health_indicators + [performance_indicator]
