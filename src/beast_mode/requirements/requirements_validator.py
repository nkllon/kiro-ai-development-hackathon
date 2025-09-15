#!/usr/bin/env python3
"""
Requirements Validator
=====================

Comprehensive requirements validation framework to prevent missing requirements
failures. Provides systematic validation of requirements completeness, consistency,
and traceability throughout the development lifecycle.

Author: Beast Mode Framework
Date: 2025-09-14
Purpose: Prevent requirements missing failures
"""

import sys
import os
import json
import logging
import re
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple, Union, Set
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
import yaml


class RequirementType(Enum):
    """Types of requirements."""

    FUNCTIONAL = "functional"
    NON_FUNCTIONAL = "non_functional"
    TECHNICAL = "technical"
    BUSINESS = "business"
    COMPLIANCE = "compliance"
    SECURITY = "security"
    PERFORMANCE = "performance"
    USABILITY = "usability"


class RequirementStatus(Enum):
    """Requirement status."""

    DRAFT = "draft"
    REVIEW = "review"
    APPROVED = "approved"
    IMPLEMENTED = "implemented"
    TESTED = "tested"
    DEPRECATED = "deprecated"


class ValidationSeverity(Enum):
    """Validation severity levels."""

    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


@dataclass
class Requirement:
    """Individual requirement definition."""

    id: str
    title: str
    description: str
    type: RequirementType
    status: RequirementStatus = RequirementStatus.DRAFT
    priority: int = 1  # 1=highest, 5=lowest
    dependencies: List[str] = field(default_factory=list)
    acceptance_criteria: List[str] = field(default_factory=list)
    traceability: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ValidationResult:
    """Result of requirements validation."""

    requirement_id: str
    severity: ValidationSeverity
    message: str
    category: str
    suggestions: List[str] = field(default_factory=list)


@dataclass
class RequirementsSet:
    """Complete set of requirements."""

    name: str
    description: str
    version: str
    requirements: List[Requirement] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)


class RequirementsValidator:
    """
    Comprehensive requirements validation framework.

    Provides systematic validation of requirements completeness, consistency,
    and traceability to prevent missing requirements failures.
    """

    def __init__(self):
        """Initialize the requirements validator."""
        self.logger = self._setup_logging()
        self.validation_rules: Dict[str, List[callable]] = (
            self._initialize_validation_rules()
        )
        self.requirements_cache: Dict[str, RequirementsSet] = {}

    def _setup_logging(self) -> logging.Logger:
        """Setup logging for requirements validation."""
        logger = logging.getLogger("requirements_validator")
        logger.setLevel(logging.INFO)

        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)

        return logger

    def _initialize_validation_rules(self) -> Dict[str, List[callable]]:
        """Initialize validation rules for requirements."""
        return {
            "completeness": [
                self._validate_requirement_id,
                self._validate_requirement_title,
                self._validate_requirement_description,
                self._validate_acceptance_criteria,
            ],
            "consistency": [
                self._validate_dependency_consistency,
                self._validate_priority_consistency,
                self._validate_type_consistency,
            ],
            "traceability": [
                self._validate_traceability_links,
                self._validate_implementation_tracking,
                self._validate_test_coverage,
            ],
            "quality": [
                self._validate_description_quality,
                self._validate_acceptance_criteria_quality,
                self._validate_requirement_clarity,
            ],
        }

    def load_requirements_from_file(self, file_path: str) -> RequirementsSet:
        """Load requirements from various file formats."""
        file_path = Path(file_path)

        if not file_path.exists():
            raise FileNotFoundError(f"Requirements file not found: {file_path}")

        if file_path.suffix.lower() == ".json":
            return self._load_from_json(file_path)
        elif file_path.suffix.lower() in [".yml", ".yaml"]:
            return self._load_from_yaml(file_path)
        elif file_path.suffix.lower() == ".md":
            return self._load_from_markdown(file_path)
        else:
            raise ValueError(f"Unsupported file format: {file_path.suffix}")

    def _load_from_json(self, file_path: Path) -> RequirementsSet:
        """Load requirements from JSON file."""
        with open(file_path, "r") as f:
            data = json.load(f)

        requirements = []
        for req_data in data.get("requirements", []):
            requirement = Requirement(
                id=req_data["id"],
                title=req_data["title"],
                description=req_data["description"],
                type=RequirementType(req_data["type"]),
                status=RequirementStatus(req_data.get("status", "draft")),
                priority=req_data.get("priority", 1),
                dependencies=req_data.get("dependencies", []),
                acceptance_criteria=req_data.get("acceptance_criteria", []),
                traceability=req_data.get("traceability", {}),
                metadata=req_data.get("metadata", {}),
            )
            requirements.append(requirement)

        return RequirementsSet(
            name=data.get("name", file_path.stem),
            description=data.get("description", ""),
            version=data.get("version", "1.0.0"),
            requirements=requirements,
            metadata=data.get("metadata", {}),
        )

    def _load_from_yaml(self, file_path: Path) -> RequirementsSet:
        """Load requirements from YAML file."""
        with open(file_path, "r") as f:
            data = yaml.safe_load(f)

        requirements = []
        for req_data in data.get("requirements", []):
            requirement = Requirement(
                id=req_data["id"],
                title=req_data["title"],
                description=req_data["description"],
                type=RequirementType(req_data["type"]),
                status=RequirementStatus(req_data.get("status", "draft")),
                priority=req_data.get("priority", 1),
                dependencies=req_data.get("dependencies", []),
                acceptance_criteria=req_data.get("acceptance_criteria", []),
                traceability=req_data.get("traceability", {}),
                metadata=req_data.get("metadata", {}),
            )
            requirements.append(requirement)

        return RequirementsSet(
            name=data.get("name", file_path.stem),
            description=data.get("description", ""),
            version=data.get("version", "1.0.0"),
            requirements=requirements,
            metadata=data.get("metadata", {}),
        )

    def _load_from_markdown(self, file_path: Path) -> RequirementsSet:
        """Load requirements from Markdown file."""
        with open(file_path, "r") as f:
            content = f.read()

        # Parse markdown requirements
        requirements = []
        lines = content.split("\n")
        current_requirement = None

        for line in lines:
            line = line.strip()

            # Match requirement headers
            if re.match(r"^#+\s*REQ-\d+", line, re.IGNORECASE):
                if current_requirement:
                    requirements.append(current_requirement)

                # Extract requirement ID and title
                match = re.match(r"^#+\s*(REQ-\d+):\s*(.+)", line, re.IGNORECASE)
                if match:
                    req_id = match.group(1)
                    title = match.group(2)

                    current_requirement = Requirement(
                        id=req_id,
                        title=title,
                        description="",
                        type=RequirementType.FUNCTIONAL,
                    )

            # Match description
            elif current_requirement and line and not line.startswith("#"):
                if current_requirement.description:
                    current_requirement.description += " " + line
                else:
                    current_requirement.description = line

        # Add last requirement
        if current_requirement:
            requirements.append(current_requirement)

        return RequirementsSet(
            name=file_path.stem,
            description=f"Requirements loaded from {file_path.name}",
            version="1.0.0",
            requirements=requirements,
        )

    def validate_requirements(
        self, requirements_set: RequirementsSet
    ) -> List[ValidationResult]:
        """Validate a complete set of requirements."""
        validation_results = []

        self.logger.info(f"Validating requirements set: {requirements_set.name}")

        # Validate individual requirements
        for requirement in requirements_set.requirements:
            individual_results = self._validate_individual_requirement(requirement)
            validation_results.extend(individual_results)

        # Validate requirements set as a whole
        set_results = self._validate_requirements_set(requirements_set)
        validation_results.extend(set_results)

        self.logger.info(f"Validation complete: {len(validation_results)} issues found")
        return validation_results

    def _validate_individual_requirement(
        self, requirement: Requirement
    ) -> List[ValidationResult]:
        """Validate an individual requirement."""
        results = []

        for category, rules in self.validation_rules.items():
            for rule in rules:
                try:
                    rule_result = rule(requirement)
                    if rule_result:
                        results.append(rule_result)
                except Exception as e:
                    self.logger.error(
                        f"Validation rule failed for {requirement.id}: {e}"
                    )
                    results.append(
                        ValidationResult(
                            requirement_id=requirement.id,
                            severity=ValidationSeverity.ERROR,
                            message=f"Validation rule failed: {e}",
                            category=category,
                        )
                    )

        return results

    def _validate_requirements_set(
        self, requirements_set: RequirementsSet
    ) -> List[ValidationResult]:
        """Validate the requirements set as a whole."""
        results = []

        # Check for duplicate requirement IDs
        ids = [req.id for req in requirements_set.requirements]
        duplicates = [id for id in set(ids) if ids.count(id) > 1]
        if duplicates:
            results.append(
                ValidationResult(
                    requirement_id="SET",
                    severity=ValidationSeverity.ERROR,
                    message=f"Duplicate requirement IDs found: {duplicates}",
                    category="consistency",
                    suggestions=["Ensure all requirement IDs are unique"],
                )
            )

        # Check for missing dependencies
        all_ids = set(ids)
        missing_deps = []
        for req in requirements_set.requirements:
            for dep in req.dependencies:
                if dep not in all_ids:
                    missing_deps.append(f"{req.id} -> {dep}")

        if missing_deps:
            results.append(
                ValidationResult(
                    requirement_id="SET",
                    severity=ValidationSeverity.WARNING,
                    message=f"Missing dependencies: {missing_deps}",
                    category="consistency",
                    suggestions=[
                        "Verify all dependency IDs exist in the requirements set"
                    ],
                )
            )

        # Check for circular dependencies
        circular_deps = self._detect_circular_dependencies(
            requirements_set.requirements
        )
        if circular_deps:
            results.append(
                ValidationResult(
                    requirement_id="SET",
                    severity=ValidationSeverity.ERROR,
                    message=f"Circular dependencies detected: {circular_deps}",
                    category="consistency",
                    suggestions=[
                        "Remove circular dependencies to prevent infinite loops"
                    ],
                )
            )

        return results

    def _detect_circular_dependencies(
        self, requirements: List[Requirement]
    ) -> List[List[str]]:
        """Detect circular dependencies in requirements."""
        # Build dependency graph
        graph = {req.id: req.dependencies for req in requirements}

        def has_cycle(node, visited, rec_stack):
            visited.add(node)
            rec_stack.add(node)

            for neighbor in graph.get(node, []):
                if neighbor not in visited:
                    if has_cycle(neighbor, visited, rec_stack):
                        return True
                elif neighbor in rec_stack:
                    return True

            rec_stack.remove(node)
            return False

        visited = set()
        cycles = []

        for node in graph:
            if node not in visited:
                rec_stack = set()
                if has_cycle(node, visited, rec_stack):
                    cycles.append(list(rec_stack))

        return cycles

    # Individual validation rules
    def _validate_requirement_id(
        self, requirement: Requirement
    ) -> Optional[ValidationResult]:
        """Validate requirement ID format."""
        if not requirement.id or not requirement.id.strip():
            return ValidationResult(
                requirement_id=requirement.id or "UNKNOWN",
                severity=ValidationSeverity.CRITICAL,
                message="Requirement ID is empty or missing",
                category="completeness",
                suggestions=["Provide a unique identifier for the requirement"],
            )

        # Check ID format (should be alphanumeric with hyphens/underscores)
        if not re.match(r"^[A-Za-z0-9_-]+$", requirement.id):
            return ValidationResult(
                requirement_id=requirement.id,
                severity=ValidationSeverity.WARNING,
                message="Requirement ID contains invalid characters",
                category="completeness",
                suggestions=[
                    "Use only alphanumeric characters, hyphens, and underscores"
                ],
            )

        return None

    def _validate_requirement_title(
        self, requirement: Requirement
    ) -> Optional[ValidationResult]:
        """Validate requirement title."""
        if not requirement.title or len(requirement.title.strip()) < 5:
            return ValidationResult(
                requirement_id=requirement.id,
                severity=ValidationSeverity.ERROR,
                message="Requirement title is too short or missing",
                category="completeness",
                suggestions=[
                    "Provide a clear, descriptive title (minimum 5 characters)"
                ],
            )

        return None

    def _validate_requirement_description(
        self, requirement: Requirement
    ) -> Optional[ValidationResult]:
        """Validate requirement description."""
        if not requirement.description or len(requirement.description.strip()) < 20:
            return ValidationResult(
                requirement_id=requirement.id,
                severity=ValidationSeverity.ERROR,
                message="Requirement description is too short or missing",
                category="completeness",
                suggestions=["Provide a detailed description (minimum 20 characters)"],
            )

        return None

    def _validate_acceptance_criteria(
        self, requirement: Requirement
    ) -> Optional[ValidationResult]:
        """Validate acceptance criteria."""
        if not requirement.acceptance_criteria:
            return ValidationResult(
                requirement_id=requirement.id,
                severity=ValidationSeverity.WARNING,
                message="No acceptance criteria defined",
                category="completeness",
                suggestions=["Define clear acceptance criteria for the requirement"],
            )

        # Check quality of acceptance criteria
        poor_criteria = []
        for criteria in requirement.acceptance_criteria:
            if len(criteria.strip()) < 10:
                poor_criteria.append(criteria)

        if poor_criteria:
            return ValidationResult(
                requirement_id=requirement.id,
                severity=ValidationSeverity.WARNING,
                message=f"Some acceptance criteria are too brief: {poor_criteria}",
                category="quality",
                suggestions=["Make acceptance criteria more specific and measurable"],
            )

        return None

    def _validate_dependency_consistency(
        self, requirement: Requirement
    ) -> Optional[ValidationResult]:
        """Validate dependency consistency."""
        # This would check if dependencies exist and are valid
        # Implementation depends on having access to the full requirements set
        return None

    def _validate_priority_consistency(
        self, requirement: Requirement
    ) -> Optional[ValidationResult]:
        """Validate priority consistency."""
        if requirement.priority < 1 or requirement.priority > 5:
            return ValidationResult(
                requirement_id=requirement.id,
                severity=ValidationSeverity.WARNING,
                message=f"Priority {requirement.priority} is outside valid range (1-5)",
                category="consistency",
                suggestions=["Use priority values between 1 (highest) and 5 (lowest)"],
            )

        return None

    def _validate_type_consistency(
        self, requirement: Requirement
    ) -> Optional[ValidationResult]:
        """Validate requirement type consistency."""
        # Check if type is valid
        try:
            RequirementType(
                requirement.type.value
                if hasattr(requirement.type, "value")
                else requirement.type
            )
        except (ValueError, AttributeError):
            return ValidationResult(
                requirement_id=requirement.id,
                severity=ValidationSeverity.ERROR,
                message=f"Invalid requirement type: {requirement.type}",
                category="consistency",
                suggestions=[
                    "Use valid requirement types: functional, non_functional, technical, business, compliance, security, performance, usability"
                ],
            )

        return None

    def _validate_traceability_links(
        self, requirement: Requirement
    ) -> Optional[ValidationResult]:
        """Validate traceability links."""
        if not requirement.traceability:
            return ValidationResult(
                requirement_id=requirement.id,
                severity=ValidationSeverity.INFO,
                message="No traceability information provided",
                category="traceability",
                suggestions=[
                    "Add traceability links to related documents, code, or tests"
                ],
            )

        return None

    def _validate_implementation_tracking(
        self, requirement: Requirement
    ) -> Optional[ValidationResult]:
        """Validate implementation tracking."""
        # Check if requirement has implementation tracking
        if requirement.status in [RequirementStatus.DRAFT, RequirementStatus.REVIEW]:
            return None  # Not yet implemented

        if not requirement.traceability.get("implementation"):
            return ValidationResult(
                requirement_id=requirement.id,
                severity=ValidationSeverity.WARNING,
                message="No implementation tracking for implemented requirement",
                category="traceability",
                suggestions=["Add links to implementation code or documentation"],
            )

        return None

    def _validate_test_coverage(
        self, requirement: Requirement
    ) -> Optional[ValidationResult]:
        """Validate test coverage."""
        if requirement.status == RequirementStatus.IMPLEMENTED:
            if not requirement.traceability.get("tests"):
                return ValidationResult(
                    requirement_id=requirement.id,
                    severity=ValidationSeverity.WARNING,
                    message="No test coverage information for implemented requirement",
                    category="traceability",
                    suggestions=["Add links to test cases or test coverage reports"],
                )

        return None

    def _validate_description_quality(
        self, requirement: Requirement
    ) -> Optional[ValidationResult]:
        """Validate description quality."""
        if not requirement.description:
            return None

        # Check for common quality issues
        issues = []

        if requirement.description.isupper():
            issues.append("Description is in all caps")

        if len(requirement.description.split()) < 5:
            issues.append("Description is too brief")

        if not requirement.description.endswith("."):
            issues.append("Description should end with a period")

        if issues:
            return ValidationResult(
                requirement_id=requirement.id,
                severity=ValidationSeverity.WARNING,
                message=f"Description quality issues: {', '.join(issues)}",
                category="quality",
                suggestions=["Improve description clarity and formatting"],
            )

        return None

    def _validate_acceptance_criteria_quality(
        self, requirement: Requirement
    ) -> Optional[ValidationResult]:
        """Validate acceptance criteria quality."""
        if not requirement.acceptance_criteria:
            return None

        issues = []
        for criteria in requirement.acceptance_criteria:
            if not criteria.strip():
                issues.append("Empty acceptance criteria")
            elif not criteria.strip().endswith("."):
                issues.append("Acceptance criteria should end with a period")

        if issues:
            return ValidationResult(
                requirement_id=requirement.id,
                severity=ValidationSeverity.WARNING,
                message=f"Acceptance criteria quality issues: {', '.join(issues)}",
                category="quality",
                suggestions=["Improve acceptance criteria clarity and formatting"],
            )

        return None

    def _validate_requirement_clarity(
        self, requirement: Requirement
    ) -> Optional[ValidationResult]:
        """Validate overall requirement clarity."""
        # Check for ambiguous language
        ambiguous_terms = ["should", "might", "could", "possibly", "maybe"]
        description_lower = requirement.description.lower()

        found_ambiguous = [
            term for term in ambiguous_terms if term in description_lower
        ]

        if found_ambiguous:
            return ValidationResult(
                requirement_id=requirement.id,
                severity=ValidationSeverity.WARNING,
                message=f"Ambiguous language found: {found_ambiguous}",
                category="quality",
                suggestions=["Use clear, unambiguous language in requirements"],
            )

        return None

    def generate_validation_report(
        self, validation_results: List[ValidationResult]
    ) -> str:
        """Generate a comprehensive validation report."""
        if not validation_results:
            return "No validation issues found - requirements are valid"

        report = []
        report.append("=" * 80)
        report.append("REQUIREMENTS VALIDATION REPORT")
        report.append("=" * 80)
        report.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append("")

        # Group by severity
        severity_counts = {}
        for result in validation_results:
            severity = result.severity.value
            severity_counts[severity] = severity_counts.get(severity, 0) + 1

        report.append("VALIDATION SUMMARY:")
        report.append(f"  Total Issues: {len(validation_results)}")
        for severity, count in severity_counts.items():
            report.append(f"  {severity.title()}: {count}")
        report.append("")

        # Group by category
        category_counts = {}
        for result in validation_results:
            category = result.category
            category_counts[category] = category_counts.get(category, 0) + 1

        report.append("ISSUES BY CATEGORY:")
        for category, count in category_counts.items():
            report.append(f"  {category.title()}: {count}")
        report.append("")

        # Detailed issues
        report.append("DETAILED ISSUES:")
        for result in validation_results:
            report.append(
                f"  [{result.severity.value.upper()}] {result.requirement_id}"
            )
            report.append(f"    Category: {result.category}")
            report.append(f"    Message: {result.message}")
            if result.suggestions:
                report.append(f"    Suggestions: {'; '.join(result.suggestions)}")
            report.append("")

        return "\n".join(report)


def main():
    """Main function for testing the requirements validator."""
    validator = RequirementsValidator()

    print("Testing Requirements Validator...")

    # Create sample requirements for testing
    sample_requirements = RequirementsSet(
        name="Test Requirements",
        description="Sample requirements for testing validation",
        version="1.0.0",
        requirements=[
            Requirement(
                id="REQ-001",
                title="User Authentication",
                description="The system shall provide user authentication functionality.",
                type=RequirementType.FUNCTIONAL,
                acceptance_criteria=[
                    "User can login with valid credentials",
                    "User cannot login with invalid credentials",
                ],
            ),
            Requirement(
                id="REQ-002",
                title="",
                description="Invalid requirement with missing title",
                type=RequirementType.FUNCTIONAL,
            ),
        ],
    )

    # Validate requirements
    results = validator.validate_requirements(sample_requirements)

    # Generate report
    report = validator.generate_validation_report(results)
    print(report)


if __name__ == "__main__":
    main()
