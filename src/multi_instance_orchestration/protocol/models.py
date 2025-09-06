"""Data models for text-based communication protocol."""

from datetime import datetime, timedelta
from typing import Any
from uuid import uuid4

from pydantic import BaseModel, Field, field_validator


class StructuredAction(BaseModel):
    """Structured action for text-based communication protocol.

    Follows verb-noun-modifier pattern for human-readable commands:
    - run task abc beast-mode
    - stop instance kiro-3 graceful
    - git sync branch feature/parallel-dev
    """

    verb: str = Field(
        ..., description="Action verb (run, stop, sync, status, scale, merge)"
    )
    noun: str = Field(
        ..., description="Target noun (task, instance, branch, swarm, instances)"
    )
    modifiers: list[str] = Field(default_factory=list, description="Action modifiers")
    parameters: dict[str, Any] = Field(
        default_factory=dict, description="Additional parameters"
    )
    timestamp: datetime = Field(default_factory=datetime.now)
    source_instance: str = Field(..., description="Source instance identifier")
    correlation_id: str = Field(default_factory=lambda: str(uuid4()))

    @field_validator("verb")
    @classmethod
    def validate_verb(cls, v: str) -> str:
        """Validate verb is in allowed set."""
        allowed_verbs = {
            "run",
            "stop",
            "sync",
            "status",
            "scale",
            "merge",
            "restart",
            "pause",
            "resume",
            "deploy",
            "rollback",
            "monitor",
            "alert",
            "configure",
            "validate",
        }
        if v.lower() not in allowed_verbs:
            raise ValueError(f"Verb '{v}' not in allowed verbs: {allowed_verbs}")
        return v.lower()

    @field_validator("noun")
    @classmethod
    def validate_noun(cls, v: str) -> str:
        """Validate noun is in allowed set."""
        allowed_nouns = {
            "task",
            "instance",
            "branch",
            "swarm",
            "instances",
            "branches",
            "service",
            "deployment",
            "configuration",
            "health",
            "metrics",
            "logs",
            "alerts",
            "resources",
            "workflow",
        }
        if v.lower() not in allowed_nouns:
            raise ValueError(f"Noun '{v}' not in allowed nouns: {allowed_nouns}")
        return v.lower()

    def to_command_string(self) -> str:
        """Convert to human-readable command string."""
        parts = [self.verb, self.noun]
        if self.modifiers:
            parts.extend(self.modifiers)

        # Add key parameters as inline arguments
        for key, value in self.parameters.items():
            if isinstance(value, (str, int, float, bool)):
                parts.append(f"{key}={value}")

        return " ".join(parts)

    @classmethod
    def from_command_string(
        cls, command: str, source_instance: str
    ) -> "StructuredAction":
        """Parse command string into StructuredAction."""
        parts = command.strip().split()
        if len(parts) < 2:
            raise ValueError("Command must have at least verb and noun")

        verb = parts[0]
        noun = parts[1]
        modifiers: list[str] = []
        parameters: dict[str, Any] = {}

        for part in parts[2:]:
            if "=" in part:
                key, value = part.split("=", 1)
                # Try to parse as number or boolean
                if value.lower() in ("true", "false"):
                    parameters[key] = value.lower() == "true"
                elif value.isdigit():
                    parameters[key] = int(value)
                elif value.replace(".", "").replace("-", "").isdigit():
                    parameters[key] = float(value)
                else:
                    parameters[key] = value
            else:
                modifiers.append(part)

        return cls(
            verb=verb,
            noun=noun,
            modifiers=modifiers,
            parameters=parameters,
            source_instance=source_instance,
        )


class ActionResult(BaseModel):
    """Result of executing a structured action."""

    success: bool
    message: str
    data: dict[str, Any] = Field(default_factory=dict)
    execution_time: timedelta
    side_effects: list[str] = Field(default_factory=list)
    correlation_id: str
    timestamp: datetime = Field(default_factory=datetime.now)

    def to_response_string(self) -> str:
        """Convert to human-readable response string."""
        status = "SUCCESS" if self.success else "FAILED"
        duration = f"{self.execution_time.total_seconds():.2f}s"

        response = f"[{status}] {self.message} (took {duration})"

        if self.data:
            response += f"\nData: {self.data}"

        if self.side_effects:
            response += f"\nSide effects: {', '.join(self.side_effects)}"

        return response


class ValidationResult(BaseModel):
    """Result of validating a structured action."""

    is_valid: bool
    errors: list[str] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)
    suggestions: list[str] = Field(default_factory=list)

    def to_string(self) -> str:
        """Convert to human-readable validation result."""
        if self.is_valid:
            result = "VALID"
            if self.warnings:
                result += f" (warnings: {', '.join(self.warnings)})"
        else:
            result = f"INVALID: {', '.join(self.errors)}"

        if self.suggestions:
            result += f"\nSuggestions: {', '.join(self.suggestions)}"

        return result


class CommandPattern(BaseModel):
    """Pattern definition for command validation and help."""

    verb: str
    noun: str
    allowed_modifiers: list[str] = Field(default_factory=list)
    required_parameters: list[str] = Field(default_factory=list)
    optional_parameters: list[str] = Field(default_factory=list)
    description: str
    examples: list[str] = Field(default_factory=list)

    def matches(self, action: StructuredAction) -> bool:
        """Check if action matches this pattern."""
        return action.verb == self.verb and action.noun == self.noun

    def validate_action(self, action: StructuredAction) -> ValidationResult:
        """Validate action against this pattern."""
        errors = []
        warnings = []
        suggestions = []

        # Check required parameters
        for param in self.required_parameters:
            if param not in action.parameters:
                errors.append(f"Missing required parameter: {param}")

        # Check modifiers
        for modifier in action.modifiers:
            if modifier not in self.allowed_modifiers:
                warnings.append(f"Unknown modifier: {modifier}")
                if self.allowed_modifiers:
                    suggestions.append(
                        f"Available modifiers: {', '.join(self.allowed_modifiers)}"
                    )

        return ValidationResult(
            is_valid=len(errors) == 0,
            errors=errors,
            warnings=warnings,
            suggestions=suggestions,
        )
