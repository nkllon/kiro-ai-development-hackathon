"""
Project generator for RM-DDD projects.

Provides systematic project scaffolding with configurable templates,
domain context setup, and best practice enforcement.
"""

import logging
import os
import shutil
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Set
from uuid import uuid4

from ..core.base import DomainReflectiveModule
from ..core.compliance import ValidationResult
from ..models import DomainException, ModuleStatus, ModuleCapability


logger = logging.getLogger(__name__)


class ProjectType(Enum):
    """Types of RM-DDD projects that can be generated."""

    MICROSERVICE = "microservice"
    MODULAR_MONOLITH = "modular_monolith"
    LIBRARY = "library"
    CLI_TOOL = "cli_tool"
    WEB_API = "web_api"
    EVENT_DRIVEN = "event_driven"


class TemplateType(Enum):
    """Types of project templates."""

    MINIMAL = "minimal"
    STANDARD = "standard"
    ENTERPRISE = "enterprise"
    CUSTOM = "custom"


@dataclass
class ProjectConfig:
    """Configuration for project generation."""

    project_name: str
    project_type: ProjectType
    template_type: TemplateType = TemplateType.STANDARD
    domain_contexts: List[str] = field(default_factory=list)
    author_name: str = ""
    author_email: str = ""
    description: str = ""
    python_version: str = "3.9"
    include_tests: bool = True
    include_docs: bool = True
    include_ci_cd: bool = True
    include_docker: bool = True
    license_type: str = "MIT"
    metadata: Dict[str, Any] = field(default_factory=dict)

    def validate_config(self) -> ValidationResult:
        """Validate project configuration."""
        result = ValidationResult(is_valid=True)

        if not self.project_name:
            result.add_error("Project name is required")
        elif not self.project_name.replace("_", "").replace("-", "").isalnum():
            result.add_error(
                "Project name must be alphanumeric with underscores or hyphens"
            )

        if not self.domain_contexts:
            result.add_warning(
                "No domain contexts specified - will create default context"
            )

        if self.python_version and not self.python_version.replace(".", "").isdigit():
            result.add_error("Invalid Python version format")

        return result


@dataclass
class ScaffoldingResult:
    """Result of project scaffolding operation."""

    project_path: Path
    generated_files: List[Path] = field(default_factory=list)
    created_directories: List[Path] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)
    generation_time: datetime = field(default_factory=datetime.now)

    @property
    def success(self) -> bool:
        """Check if scaffolding was successful."""
        return len(self.errors) == 0

    def to_dict(self) -> Dict[str, Any]:
        """Convert result to dictionary."""
        return {
            "project_path": str(self.project_path),
            "generated_files": [str(f) for f in self.generated_files],
            "created_directories": [str(d) for d in self.created_directories],
            "warnings": self.warnings,
            "errors": self.errors,
            "success": self.success,
            "generation_time": self.generation_time.isoformat(),
        }


class ProjectTemplate:
    """Template for generating RM-DDD projects."""

    def __init__(
        self,
        name: str,
        template_type: TemplateType,
        supported_project_types: List[ProjectType],
    ):
        self.name = name
        self.template_type = template_type
        self.supported_project_types = supported_project_types
        self._file_templates: Dict[str, str] = {}
        self._directory_structure: List[str] = []
        self._dependencies: Dict[str, str] = {}
        self._dev_dependencies: Dict[str, str] = {}

    def add_file_template(self, relative_path: str, content: str):
        """Add a file template to the project template."""
        self._file_templates[relative_path] = content

    def add_directory(self, relative_path: str):
        """Add a directory to the project structure."""
        self._directory_structure.append(relative_path)

    def add_dependency(self, package: str, version: str):
        """Add a runtime dependency."""
        self._dependencies[package] = version

    def add_dev_dependency(self, package: str, version: str):
        """Add a development dependency."""
        self._dev_dependencies[package] = version

    def supports_project_type(self, project_type: ProjectType) -> bool:
        """Check if template supports a project type."""
        return project_type in self.supported_project_types

    def get_file_templates(self) -> Dict[str, str]:
        """Get all file templates."""
        return self._file_templates.copy()

    def get_directory_structure(self) -> List[str]:
        """Get directory structure."""
        return self._directory_structure.copy()

    def get_dependencies(self) -> Dict[str, str]:
        """Get runtime dependencies."""
        return self._dependencies.copy()

    def get_dev_dependencies(self) -> Dict[str, str]:
        """Get development dependencies."""
        return self._dev_dependencies.copy()


class ProjectGenerator(DomainReflectiveModule):
    """
    Systematic project generator for RM-DDD projects.

    Provides comprehensive project scaffolding with configurable templates,
    domain context initialization, and systematic best practices.
    """

    def __init__(self, domain_context: str = "project_generation"):
        super().__init__(domain_context)
        self._templates: Dict[str, ProjectTemplate] = {}
        self._generated_projects: List[ScaffoldingResult] = []
        self._initialize_default_templates()

    def _initialize_default_templates(self):
        """Initialize default project templates."""
        self._create_minimal_template()
        self._create_standard_template()
        self._create_enterprise_template()

        logger.debug("Initialized default project templates")

    def _create_minimal_template(self):
        """Create minimal project template."""
        template = ProjectTemplate(
            "minimal",
            TemplateType.MINIMAL,
            list(ProjectType),  # Supports all project types
        )

        # Basic directory structure
        template.add_directory("src")
        template.add_directory("tests")
        template.add_directory("docs")

        # Basic files
        template.add_file_template("README.md", self._get_readme_template())
        template.add_file_template("pyproject.toml", self._get_pyproject_template())
        template.add_file_template("src/__init__.py", "")
        template.add_file_template("tests/__init__.py", "")
        template.add_file_template(".gitignore", self._get_gitignore_template())

        # Basic dependencies
        template.add_dependency("rm-ddd", ">=0.1.0")
        template.add_dev_dependency("pytest", ">=7.0.0")
        template.add_dev_dependency("black", ">=22.0.0")
        template.add_dev_dependency("mypy", ">=0.991")

        self._templates["minimal"] = template

    def _create_standard_template(self):
        """Create standard project template."""
        template = ProjectTemplate("standard", TemplateType.STANDARD, list(ProjectType))

        # Enhanced directory structure
        directories = [
            "src",
            "tests",
            "docs",
            "scripts",
            "config",
            "src/domain",
            "src/infrastructure",
            "src/application",
            "tests/unit",
            "tests/integration",
            "tests/fixtures",
        ]

        for directory in directories:
            template.add_directory(directory)

        # Standard files
        template.add_file_template("README.md", self._get_readme_template())
        template.add_file_template("pyproject.toml", self._get_pyproject_template())
        template.add_file_template("Makefile", self._get_makefile_template())
        template.add_file_template(
            "docker-compose.yml", self._get_docker_compose_template()
        )
        template.add_file_template("Dockerfile", self._get_dockerfile_template())
        template.add_file_template(".github/workflows/ci.yml", self._get_ci_template())

        # Domain layer files
        template.add_file_template("src/domain/__init__.py", "")
        template.add_file_template(
            "src/domain/entities.py", self._get_entities_template()
        )
        template.add_file_template(
            "src/domain/value_objects.py", self._get_value_objects_template()
        )
        template.add_file_template(
            "src/domain/services.py", self._get_domain_services_template()
        )
        template.add_file_template(
            "src/domain/repositories.py", self._get_repositories_template()
        )

        # Infrastructure layer files
        template.add_file_template("src/infrastructure/__init__.py", "")
        template.add_file_template(
            "src/infrastructure/persistence.py", self._get_persistence_template()
        )
        template.add_file_template(
            "src/infrastructure/external_services.py",
            self._get_external_services_template(),
        )

        # Application layer files
        template.add_file_template("src/application/__init__.py", "")
        template.add_file_template(
            "src/application/services.py", self._get_application_services_template()
        )
        template.add_file_template(
            "src/application/handlers.py", self._get_handlers_template()
        )

        # Test files
        template.add_file_template("tests/conftest.py", self._get_conftest_template())
        template.add_file_template(
            "tests/unit/test_entities.py", self._get_test_entities_template()
        )
        template.add_file_template(
            "tests/integration/test_repositories.py",
            self._get_test_repositories_template(),
        )

        # Configuration files
        template.add_file_template("config/settings.py", self._get_settings_template())
        template.add_file_template(".env.example", self._get_env_template())

        # Enhanced dependencies
        template.add_dependency("rm-ddd", ">=0.1.0")
        template.add_dependency("pydantic", ">=1.10.0")
        template.add_dependency("click", ">=8.0.0")

        template.add_dev_dependency("pytest", ">=7.0.0")
        template.add_dev_dependency("pytest-cov", ">=4.0.0")
        template.add_dev_dependency("black", ">=22.0.0")
        template.add_dev_dependency("mypy", ">=0.991")
        template.add_dev_dependency("flake8", ">=5.0.0")
        template.add_dev_dependency("pre-commit", ">=2.20.0")

        self._templates["standard"] = template

    def _create_enterprise_template(self):
        """Create enterprise project template."""
        template = ProjectTemplate(
            "enterprise",
            TemplateType.ENTERPRISE,
            [
                ProjectType.MICROSERVICE,
                ProjectType.MODULAR_MONOLITH,
                ProjectType.WEB_API,
            ],
        )

        # Enterprise directory structure
        directories = [
            "src",
            "tests",
            "docs",
            "scripts",
            "config",
            "deployment",
            "src/domain",
            "src/infrastructure",
            "src/application",
            "src/presentation",
            "src/domain/entities",
            "src/domain/value_objects",
            "src/domain/services",
            "src/domain/events",
            "src/domain/repositories",
            "src/infrastructure/persistence",
            "src/infrastructure/messaging",
            "src/infrastructure/external",
            "src/infrastructure/monitoring",
            "src/application/commands",
            "src/application/queries",
            "src/application/handlers",
            "src/presentation/api",
            "src/presentation/cli",
            "src/presentation/web",
            "tests/unit",
            "tests/integration",
            "tests/e2e",
            "tests/performance",
            "tests/fixtures",
            "tests/mocks",
            "docs/architecture",
            "docs/api",
            "docs/deployment",
            "deployment/docker",
            "deployment/k8s",
            "deployment/terraform",
        ]

        for directory in directories:
            template.add_directory(directory)

        # Enterprise files (would include many more files)
        template.add_file_template("README.md", self._get_enterprise_readme_template())
        template.add_file_template(
            "pyproject.toml", self._get_enterprise_pyproject_template()
        )
        template.add_file_template("Makefile", self._get_enterprise_makefile_template())

        # Enterprise dependencies
        template.add_dependency("rm-ddd", ">=0.1.0")
        template.add_dependency("fastapi", ">=0.95.0")
        template.add_dependency("sqlalchemy", ">=2.0.0")
        template.add_dependency("alembic", ">=1.10.0")
        template.add_dependency("redis", ">=4.5.0")
        template.add_dependency("celery", ">=5.2.0")
        template.add_dependency("prometheus-client", ">=0.16.0")

        self._templates["enterprise"] = template

    def register_template(self, template: ProjectTemplate):
        """Register a custom project template."""
        self._templates[template.name] = template
        logger.info(f"Registered project template: {template.name}")

    def generate_project(
        self,
        config: ProjectConfig,
        output_path: Path,
        template_name: Optional[str] = None,
    ) -> ScaffoldingResult:
        """
        Generate a new RM-DDD project.

        Args:
            config: Project configuration
            output_path: Directory where project will be created
            template_name: Optional specific template to use

        Returns:
            ScaffoldingResult: Generation results
        """
        # Validate configuration
        validation_result = config.validate_config()
        if not validation_result.is_valid:
            result = ScaffoldingResult(project_path=output_path)
            result.errors.extend(validation_result.errors)
            return result

        # Determine template
        if template_name:
            template = self._templates.get(template_name)
        else:
            template = self._templates.get(config.template_type.value)

        if not template:
            result = ScaffoldingResult(project_path=output_path)
            result.errors.append(
                f"Template not found: {template_name or config.template_type.value}"
            )
            return result

        # Check template compatibility
        if not template.supports_project_type(config.project_type):
            result = ScaffoldingResult(project_path=output_path)
            result.errors.append(
                f"Template {template.name} does not support project type {config.project_type.value}"
            )
            return result

        # Generate project
        try:
            result = self._generate_project_from_template(config, output_path, template)
            self._generated_projects.append(result)
            return result

        except Exception as e:
            logger.error(f"Project generation failed: {e}")
            result = ScaffoldingResult(project_path=output_path)
            result.errors.append(f"Generation failed: {str(e)}")
            return result

    def _generate_project_from_template(
        self, config: ProjectConfig, output_path: Path, template: ProjectTemplate
    ) -> ScaffoldingResult:
        """Generate project from template."""
        project_path = output_path / config.project_name
        result = ScaffoldingResult(project_path=project_path)

        # Create project directory
        project_path.mkdir(parents=True, exist_ok=True)
        result.created_directories.append(project_path)

        # Create directory structure
        for directory in template.get_directory_structure():
            dir_path = project_path / directory
            dir_path.mkdir(parents=True, exist_ok=True)
            result.created_directories.append(dir_path)

        # Generate files from templates
        template_context = self._create_template_context(config, template)

        for relative_path, content_template in template.get_file_templates().items():
            try:
                # Render template content
                if JINJA2_AVAILABLE:
                    from jinja2 import Template

                    jinja_template = Template(content_template)
                    content = jinja_template.render(**template_context)
                else:
                    # Simple string substitution fallback
                    content = self._simple_template_substitution(
                        content_template, template_context
                    )

                # Write file
                file_path = project_path / relative_path
                file_path.parent.mkdir(parents=True, exist_ok=True)

                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(content)

                result.generated_files.append(file_path)

            except Exception as e:
                result.errors.append(f"Failed to generate {relative_path}: {str(e)}")

        logger.info(f"Generated project {config.project_name} at {project_path}")
        return result

    def _create_template_context(
        self, config: ProjectConfig, template: ProjectTemplate
    ) -> Dict[str, Any]:
        """Create template rendering context."""
        return {
            "project_name": config.project_name,
            "project_type": config.project_type.value,
            "author_name": config.author_name,
            "author_email": config.author_email,
            "description": config.description,
            "python_version": config.python_version,
            "license_type": config.license_type,
            "domain_contexts": config.domain_contexts,
            "dependencies": template.get_dependencies(),
            "dev_dependencies": template.get_dev_dependencies(),
            "include_tests": config.include_tests,
            "include_docs": config.include_docs,
            "include_ci_cd": config.include_ci_cd,
            "include_docker": config.include_docker,
            "generation_date": datetime.now().strftime("%Y-%m-%d"),
            "generation_time": datetime.now().isoformat(),
            **config.metadata,
        }

    def _simple_template_substitution(
        self, template: str, context: Dict[str, Any]
    ) -> str:
        """Simple template substitution when Jinja2 is not available."""
        result = template
        for key, value in context.items():
            placeholder = f"{{{{{key}}}}}"
            result = result.replace(placeholder, str(value))
        return result

    def list_templates(self) -> List[Dict[str, Any]]:
        """List all available project templates."""
        return [
            {
                "name": template.name,
                "type": template.template_type.value,
                "supported_project_types": [
                    pt.value for pt in template.supported_project_types
                ],
                "file_count": len(template.get_file_templates()),
                "directory_count": len(template.get_directory_structure()),
            }
            for template in self._templates.values()
        ]

    def get_generation_summary(self) -> Dict[str, Any]:
        """Get summary of project generation activity."""
        successful_projects = [p for p in self._generated_projects if p.success]
        failed_projects = [p for p in self._generated_projects if not p.success]

        return {
            "total_projects": len(self._generated_projects),
            "successful_projects": len(successful_projects),
            "failed_projects": len(failed_projects),
            "success_rate": len(successful_projects)
            / max(len(self._generated_projects), 1),
            "available_templates": len(self._templates),
            "template_names": list(self._templates.keys()),
        }

    # Template content methods (simplified versions for brevity)

    def _get_readme_template(self) -> str:
        """Get README.md template."""
        return """# {{project_name}}

{{description}}

## Overview

This is an RM-DDD (Reflective Module Domain-Driven Design) project that demonstrates systematic domain modeling with Beast Mode framework integration.

## Features

- Systematic domain modeling with RM-DDD patterns
- Domain-driven design tactical patterns (Entities, Value Objects, Aggregates)
- Event sourcing and CQRS capabilities
- Bounded context management
- Anti-corruption layers for external integration
- Comprehensive testing framework
- Beast Mode PDCA integration

## Getting Started

### Prerequisites

- Python {{python_version}}+
- pip or poetry for dependency management

### Installation

```bash
pip install -e .
```

### Usage

```python
from {{project_name}} import YourDomainService

# Your systematic domain implementation here
```

## Architecture

This project follows RM-DDD architecture principles:

- **Domain Layer**: Core business logic and domain models
- **Application Layer**: Use cases and application services  
- **Infrastructure Layer**: External concerns and persistence
- **Presentation Layer**: APIs and user interfaces

## Domain Contexts

{% for context in domain_contexts -%}
- **{{context}}**: [Add description]
{% endfor %}

## Development

### Running Tests

```bash
make test
```

### Code Quality

```bash
make lint
make format
```

## Contributing

This project follows systematic development principles. Please ensure:

1. All domain logic follows DDD tactical patterns
2. Components inherit from ReflectiveModule base classes
3. Test coverage remains above 90%
4. Domain invariants are properly validated

## License

{{license_type}} License - see LICENSE file for details.

## Author

{{author_name}} <{{author_email}}>

Generated with RM-DDD SDK on {{generation_date}}
"""

    def _get_pyproject_template(self) -> str:
        """Get pyproject.toml template."""
        return """[build-system]
requires = ["setuptools>=61.0", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "{{project_name}}"
version = "0.1.0"
description = "{{description}}"
authors = [
    {name = "{{author_name}}", email = "{{author_email}}"}
]
readme = "README.md"
license = {text = "{{license_type}}"}
requires-python = ">={{python_version}}"
classifiers = [
    "Development Status :: 3 - Alpha",
    "Intended Audience :: Developers",
    "License :: OSI Approved :: {{license_type}} License",
    "Programming Language :: Python :: {{python_version}}",
    "Topic :: Software Development :: Libraries :: Python Modules",
]

dependencies = [
{% for dep, version in dependencies.items() -%}
    "{{dep}}{{version}}",
{% endfor %}
]

[project.optional-dependencies]
dev = [
{% for dep, version in dev_dependencies.items() -%}
    "{{dep}}{{version}}",
{% endfor %}
]

[project.urls]
Homepage = "https://github.com/{{author_name}}/{{project_name}}"
Repository = "https://github.com/{{author_name}}/{{project_name}}"
Documentation = "https://{{project_name}}.readthedocs.io/"

[tool.setuptools.packages.find]
where = ["src"]

[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = ["test_*.py"]
python_classes = ["Test*"]
python_functions = ["test_*"]
addopts = "--cov=src --cov-report=html --cov-report=term-missing --cov-fail-under=90"

[tool.black]
line-length = 88
target-version = ['py{{python_version.replace(".", "")}}']
include = '\\.pyi?$'

[tool.mypy]
python_version = "{{python_version}}"
warn_return_any = true
warn_unused_configs = true
disallow_untyped_defs = true
"""

    def _get_makefile_template(self) -> str:
        """Get Makefile template."""
        return """# {{project_name}} Makefile
# Systematic development automation

.PHONY: help install test lint format clean build docs

help:  ## Show this help message
\t@echo "Available commands:"
\t@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\\033[36m%-20s\\033[0m %s\\n", $$1, $$2}'

install:  ## Install dependencies
\tpip install -e ".[dev]"

test:  ## Run tests with coverage
\tpytest tests/ --cov=src --cov-report=html --cov-report=term-missing

test-unit:  ## Run unit tests only
\tpytest tests/unit/ -v

test-integration:  ## Run integration tests only
\tpytest tests/integration/ -v

lint:  ## Run linting checks
\tflake8 src tests
\tmypy src

format:  ## Format code
\tblack src tests
\tisort src tests

format-check:  ## Check code formatting
\tblack --check src tests
\tisort --check-only src tests

clean:  ## Clean build artifacts
\trm -rf build/
\trm -rf dist/
\trm -rf *.egg-info/
\trm -rf .coverage
\trm -rf htmlcov/
\tfind . -type d -name __pycache__ -delete
\tfind . -type f -name "*.pyc" -delete

build:  ## Build package
\tpython -m build

docs:  ## Generate documentation
\tcd docs && make html

docs-serve:  ## Serve documentation locally
\tcd docs/_build/html && python -m http.server 8000

# Beast Mode systematic development targets
systematic-check:  ## Run systematic compliance checks
\t@echo "Running systematic compliance validation..."
\t@python -c "from rm_ddd import validate_systematic_compliance; validate_systematic_compliance('src')"

pdca-cycle:  ## Execute PDCA development cycle
\t@echo "Executing PDCA cycle..."
\tmake test
\tmake lint
\tmake systematic-check
\t@echo "PDCA cycle complete - systematic superiority maintained"
"""

    def _get_entities_template(self) -> str:
        """Get domain entities template."""
        return '''"""
Domain entities for {{project_name}}.

This module contains the core domain entities that represent
the main business concepts with identity and lifecycle.
"""

from typing import Any, Dict, List, Optional
from uuid import UUID, uuid4
from datetime import datetime

from rm_ddd import Entity, AggregateRoot, ValidationResult, DomainBoundaries
from rm_ddd.decorators import domain_entity, aggregate_root


@domain_entity("{{domain_contexts[0] if domain_contexts else 'default'}}")
class ExampleEntity(Entity[UUID]):
    """Example domain entity demonstrating RM-DDD patterns."""
    
    def __init__(self, entity_id: Optional[UUID] = None, name: str = ""):
        super().__init__(entity_id or uuid4(), "{{domain_contexts[0] if domain_contexts else 'default'}}")
        self.name = name
        self.created_at = datetime.now()
        self.updated_at = datetime.now()
    
    def update_name(self, new_name: str):
        """Update entity name with business validation."""
        if not new_name or len(new_name.strip()) == 0:
            raise ValueError("Name cannot be empty")
        
        self.name = new_name.strip()
        self.updated_at = datetime.now()
    
    def get_domain_boundaries(self) -> DomainBoundaries:
        """Define domain boundaries for this entity."""
        return DomainBoundaries(
            context="{{domain_contexts[0] if domain_contexts else 'default'}}",
            invariants=[
                "Name must not be empty",
                "Created date must be before updated date"
            ]
        )
    
    def validate_domain_invariants(self) -> ValidationResult:
        """Validate domain invariants."""
        result = ValidationResult(is_valid=True)
        
        if not self.name or len(self.name.strip()) == 0:
            result.add_error("Entity name cannot be empty")
        
        if self.updated_at < self.created_at:
            result.add_error("Updated date cannot be before created date")
        
        return result


@aggregate_root("{{domain_contexts[0] if domain_contexts else 'default'}}", max_size=50)
class ExampleAggregate(AggregateRoot[UUID]):
    """Example aggregate root demonstrating RM-DDD patterns."""
    
    def __init__(self, aggregate_id: Optional[UUID] = None):
        super().__init__(aggregate_id or uuid4(), "{{domain_contexts[0] if domain_contexts else 'default'}}")
        self.items: List[ExampleEntity] = []
        self.status = "active"
    
    def add_item(self, item: ExampleEntity):
        """Add item to aggregate with business rules."""
        if len(self.items) >= 50:
            raise ValueError("Aggregate cannot contain more than 50 items")
        
        if item in self.items:
            raise ValueError("Item already exists in aggregate")
        
        self.items.append(item)
        
        # Emit domain event (would be implemented with actual event)
        # self.add_domain_event(ItemAddedEvent(self.id, item.id))
    
    def remove_item(self, item_id: UUID):
        """Remove item from aggregate."""
        self.items = [item for item in self.items if item.id != item_id]
        
        # Emit domain event
        # self.add_domain_event(ItemRemovedEvent(self.id, item_id))
    
    def get_domain_boundaries(self) -> DomainBoundaries:
        """Define aggregate boundaries."""
        return DomainBoundaries(
            context="{{domain_contexts[0] if domain_contexts else 'default'}}",
            invariants=[
                "Aggregate cannot contain more than 50 items",
                "All items must have unique identities",
                "Status must be valid"
            ]
        )
    
    def validate_domain_invariants(self) -> ValidationResult:
        """Validate aggregate invariants."""
        result = ValidationResult(is_valid=True)
        
        if len(self.items) > 50:
            result.add_error("Aggregate contains too many items")
        
        # Check for duplicate items
        item_ids = [item.id for item in self.items]
        if len(item_ids) != len(set(item_ids)):
            result.add_error("Aggregate contains duplicate items")
        
        if self.status not in ["active", "inactive", "archived"]:
            result.add_error("Invalid aggregate status")
        
        return result
'''

    def _get_value_objects_template(self) -> str:
        """Get value objects template."""
        return '''"""
Domain value objects for {{project_name}}.

This module contains immutable value objects that represent
domain concepts without identity.
"""

from dataclasses import dataclass
from decimal import Decimal
from typing import Any

from rm_ddd import ValueObject, ImmutableValueObject, ValidationResult
from rm_ddd.decorators import value_object


@value_object(immutable=True)
@dataclass(frozen=True)
class Money(ImmutableValueObject):
    """Money value object with currency."""
    
    amount: Decimal
    currency: str
    
    def __post_init__(self):
        super().__post_init__()
        
        if self.amount < 0:
            raise ValueError("Money amount cannot be negative")
        
        if not self.currency or len(self.currency) != 3:
            raise ValueError("Currency must be a 3-letter ISO code")
    
    def add(self, other: 'Money') -> 'Money':
        """Add two money amounts."""
        if self.currency != other.currency:
            raise ValueError(f"Cannot add {self.currency} and {other.currency}")
        
        return Money(self.amount + other.amount, self.currency)
    
    def subtract(self, other: 'Money') -> 'Money':
        """Subtract two money amounts."""
        if self.currency != other.currency:
            raise ValueError(f"Cannot subtract {other.currency} from {self.currency}")
        
        result_amount = self.amount - other.amount
        if result_amount < 0:
            raise ValueError("Result cannot be negative")
        
        return Money(result_amount, self.currency)
    
    def validate(self) -> ValidationResult:
        """Validate money value object."""
        result = ValidationResult(is_valid=True)
        
        if self.amount < 0:
            result.add_error("Money amount cannot be negative")
        
        if not self.currency or len(self.currency) != 3:
            result.add_error("Currency must be a 3-letter ISO code")
        
        return result


@value_object(immutable=True)
@dataclass(frozen=True)
class EmailAddress(ImmutableValueObject):
    """Email address value object with validation."""
    
    address: str
    
    def __post_init__(self):
        super().__post_init__()
        
        if not self._is_valid_email(self.address):
            raise ValueError(f"Invalid email address: {self.address}")
    
    def _is_valid_email(self, email: str) -> bool:
        """Simple email validation."""
        import re
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None
    
    @property
    def domain(self) -> str:
        """Get email domain."""
        return self.address.split('@')[1]
    
    @property
    def local_part(self) -> str:
        """Get email local part."""
        return self.address.split('@')[0]
    
    def validate(self) -> ValidationResult:
        """Validate email address."""
        result = ValidationResult(is_valid=True)
        
        if not self._is_valid_email(self.address):
            result.add_error("Invalid email address format")
        
        return result
'''

    # Additional template methods would be implemented here...
    # For brevity, showing key templates only

    def _get_domain_services_template(self) -> str:
        return '''"""Domain services for {{project_name}}."""

from rm_ddd import DomainService
from rm_ddd.decorators import domain_service

@domain_service("{{domain_contexts[0] if domain_contexts else 'default'}}")
class ExampleDomainService(DomainService):
    """Example domain service."""
    
    def __init__(self):
        super().__init__("{{domain_contexts[0] if domain_contexts else 'default'}}", "ExampleDomainService")
    
    def perform_business_operation(self, data: str) -> str:
        """Perform domain-specific business operation."""
        # Domain logic here
        return f"Processed: {data}"
'''

    def _get_repositories_template(self) -> str:
        return '''"""Repository interfaces for {{project_name}}."""

from abc import ABC, abstractmethod
from typing import List, Optional
from uuid import UUID

from rm_ddd import Repository

class ExampleRepository(Repository[ExampleEntity, UUID], ABC):
    """Repository interface for ExampleEntity."""
    
    @abstractmethod
    async def find_by_name(self, name: str) -> List[ExampleEntity]:
        """Find entities by name."""
        pass
'''

    # Simplified template methods for other files
    def _get_gitignore_template(self) -> str:
        return """# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Testing
.coverage
.pytest_cache/
htmlcov/

# IDEs
.vscode/
.idea/
*.swp
*.swo

# Environment
.env
.venv
env/
venv/

# OS
.DS_Store
Thumbs.db
"""

    def _get_dockerfile_template(self) -> str:
        return """FROM python:{{python_version}}-slim

WORKDIR /app

COPY pyproject.toml .
RUN pip install -e .

COPY src/ src/

EXPOSE 8000

CMD ["python", "-m", "{{project_name}}"]
"""

    def _get_docker_compose_template(self) -> str:
        return """version: '3.8'

services:
  {{project_name}}:
    build: .
    ports:
      - "8000:8000"
    environment:
      - ENV=development
"""

    def _get_ci_template(self) -> str:
        return """name: CI

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: [{{python_version}}]
    
    steps:
    - uses: actions/checkout@v3
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: ${{ matrix.python-version }}
    - name: Install dependencies
      run: |
        pip install -e ".[dev]"
    - name: Run tests
      run: |
        make test
    - name: Run linting
      run: |
        make lint
"""

    # Additional simplified templates...
    def _get_persistence_template(self) -> str:
        return '''"""Infrastructure persistence layer."""
pass  # Implementation here
'''

    def _get_external_services_template(self) -> str:
        return '''"""External service integrations."""
pass  # Implementation here
'''

    def _get_application_services_template(self) -> str:
        return '''"""Application services."""
pass  # Implementation here
'''

    def _get_handlers_template(self) -> str:
        return '''"""Application handlers."""
pass  # Implementation here
'''

    def _get_conftest_template(self) -> str:
        return '''"""Pytest configuration."""
import pytest
'''

    def _get_test_entities_template(self) -> str:
        return '''"""Tests for domain entities."""
import pytest
from src.domain.entities import ExampleEntity

def test_example_entity_creation():
    entity = ExampleEntity(name="Test")
    assert entity.name == "Test"
'''

    def _get_test_repositories_template(self) -> str:
        return '''"""Integration tests for repositories."""
pass  # Implementation here
'''

    def _get_settings_template(self) -> str:
        return '''"""Application settings."""
import os

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///{{project_name}}.db")
'''

    def _get_env_template(self) -> str:
        return """# Environment variables
DATABASE_URL=sqlite:///{{project_name}}.db
DEBUG=true
"""

    def _get_enterprise_readme_template(self) -> str:
        return self._get_readme_template()  # Would be more comprehensive

    def _get_enterprise_pyproject_template(self) -> str:
        return self._get_pyproject_template()  # Would include more dependencies

    def _get_enterprise_makefile_template(self) -> str:
        return self._get_makefile_template()  # Would include more targets

    # RM Interface Implementation
    async def get_module_status(self):
        """Get module status."""
        from ..core.health import ModuleHealth

        summary = self.get_generation_summary()

        return ModuleHealth(
            status=ModuleStatus.AVAILABLE,
            message=f"Project generator with {summary['available_templates']} templates",
            capabilities=await self.get_module_capabilities(),
            health_indicators={
                "available_templates": summary["available_templates"],
                "generated_projects": summary["total_projects"],
                "success_rate": summary["success_rate"],
            },
        )

    async def get_module_capabilities(self):
        """Get module capabilities."""
        return [
            ModuleCapability(
                name="rm_ddd_project_generation",
                description="Generates RM-DDD compliant projects from templates",
                available=True,
                version="1.0.0",
            )
        ]

    async def is_healthy(self) -> bool:
        """Check if project generator is healthy."""
        return len(self._templates) > 0

    async def get_health_indicators(self):
        """Get health indicators."""
        return {
            "generation_summary": self.get_generation_summary(),
            "domain_context": self.domain_context,
        }

    def get_domain_boundaries(self):
        """Get domain boundaries."""
        from ..models import DomainBoundaries

        return DomainBoundaries(
            context=self.domain_context,
            invariants=[
                "Generated projects must be syntactically valid",
                "All templates must support their declared project types",
                "Project configuration must be validated before generation",
            ],
        )

    def validate_domain_invariants(self):
        """Validate domain invariants."""
        result = ValidationResult(is_valid=True)

        if not self._templates:
            result.add_error("No project templates available")

        # Validate each template
        for name, template in self._templates.items():
            if not template.get_file_templates():
                result.add_warning(f"Template {name} has no file templates")

        return result


# Global JINJA2_AVAILABLE check
try:
    import jinja2

    JINJA2_AVAILABLE = True
except ImportError:
    JINJA2_AVAILABLE = False
