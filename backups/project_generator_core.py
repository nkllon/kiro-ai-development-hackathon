"""
Project Generator Core

This module was extracted from project_generator.py
as part of RM-DDD compliance refactoring.
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
import jinja2
from ..core.health import ModuleHealth
from ..models import DomainBoundaries
from jinja2 import Template


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
        if self.python_version and (not self.python_version.replace(".", "").isdigit()):
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
        template = ProjectTemplate("minimal", TemplateType.MINIMAL, list(ProjectType))
        template.add_directory("src")
        template.add_directory("tests")
        template.add_directory("docs")
        template.add_file_template("README.md", self._get_readme_template())
        template.add_file_template("pyproject.toml", self._get_pyproject_template())
        template.add_file_template("src/__init__.py", "")
        template.add_file_template("tests/__init__.py", "")
        template.add_file_template(".gitignore", self._get_gitignore_template())
        template.add_dependency("rm-ddd", ">=0.1.0")
        template.add_dev_dependency("pytest", ">=7.0.0")
        template.add_dev_dependency("black", ">=22.0.0")
        template.add_dev_dependency("mypy", ">=0.991")
        self._templates["minimal"] = template

    def _create_standard_template(self):
        """Create standard project template."""
        template = ProjectTemplate("standard", TemplateType.STANDARD, list(ProjectType))
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
        template.add_file_template("README.md", self._get_readme_template())
        template.add_file_template("pyproject.toml", self._get_pyproject_template())
        template.add_file_template("Makefile", self._get_makefile_template())
        template.add_file_template(
            "docker-compose.yml", self._get_docker_compose_template()
        )
        template.add_file_template("Dockerfile", self._get_dockerfile_template())
        template.add_file_template(".github/workflows/ci.yml", self._get_ci_template())
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
        template.add_file_template("src/infrastructure/__init__.py", "")
        template.add_file_template(
            "src/infrastructure/persistence.py", self._get_persistence_template()
        )
        template.add_file_template(
            "src/infrastructure/external_services.py",
            self._get_external_services_template(),
        )
        template.add_file_template("src/application/__init__.py", "")
        template.add_file_template(
            "src/application/services.py", self._get_application_services_template()
        )
        template.add_file_template(
            "src/application/handlers.py", self._get_handlers_template()
        )
        template.add_file_template("tests/conftest.py", self._get_conftest_template())
        template.add_file_template(
            "tests/unit/test_entities.py", self._get_test_entities_template()
        )
        template.add_file_template(
            "tests/integration/test_repositories.py",
            self._get_test_repositories_template(),
        )
        template.add_file_template("config/settings.py", self._get_settings_template())
        template.add_file_template(".env.example", self._get_env_template())
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
        template.add_file_template("README.md", self._get_enterprise_readme_template())
        template.add_file_template(
            "pyproject.toml", self._get_enterprise_pyproject_template()
        )
        template.add_file_template("Makefile", self._get_enterprise_makefile_template())
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
        validation_result = config.validate_config()
        if not validation_result.is_valid:
            result = ScaffoldingResult(project_path=output_path)
            result.errors.extend(validation_result.errors)
            return result
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
        if not template.supports_project_type(config.project_type):
            result = ScaffoldingResult(project_path=output_path)
            result.errors.append(
                f"Template {template.name} does not support project type {config.project_type.value}"
            )
            return result
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
        project_path.mkdir(parents=True, exist_ok=True)
        result.created_directories.append(project_path)
        for directory in template.get_directory_structure():
            dir_path = project_path / directory
            dir_path.mkdir(parents=True, exist_ok=True)
            result.created_directories.append(dir_path)
        template_context = self._create_template_context(config, template)
        for relative_path, content_template in template.get_file_templates().items():
            try:
                if JINJA2_AVAILABLE:
                    from jinja2 import Template

                    jinja_template = Template(content_template)
                    content = jinja_template.render(**template_context)
                else:
                    content = self._simple_template_substitution(
                        content_template, template_context
                    )
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

    def _get_readme_template(self) -> str:
        """Get README.md template."""
        return "# {{project_name}}\n\n{{description}}\n\n## Overview\n\nThis is an RM-DDD (Reflective Module Domain-Driven Design) project that demonstrates systematic domain modeling with Beast Mode framework integration.\n\n## Features\n\n- Systematic domain modeling with RM-DDD patterns\n- Domain-driven design tactical patterns (Entities, Value Objects, Aggregates)\n- Event sourcing and CQRS capabilities\n- Bounded context management\n- Anti-corruption layers for external integration\n- Comprehensive testing framework\n- Beast Mode PDCA integration\n\n## Getting Started\n\n### Prerequisites\n\n- Python {{python_version}}+\n- pip or poetry for dependency management\n\n### Installation\n\n```bash\npip install -e .\n```\n\n### Usage\n\n```python\nfrom {{project_name}} import YourDomainService\n\n# Your systematic domain implementation here\n```\n\n## Architecture\n\nThis project follows RM-DDD architecture principles:\n\n- **Domain Layer**: Core business logic and domain models\n- **Application Layer**: Use cases and application services  \n- **Infrastructure Layer**: External concerns and persistence\n- **Presentation Layer**: APIs and user interfaces\n\n## Domain Contexts\n\n{% for context in domain_contexts -%}\n- **{{context}}**: [Add description]\n{% endfor %}\n\n## Development\n\n### Running Tests\n\n```bash\nmake test\n```\n\n### Code Quality\n\n```bash\nmake lint\nmake format\n```\n\n## Contributing\n\nThis project follows systematic development principles. Please ensure:\n\n1. All domain logic follows DDD tactical patterns\n2. Components inherit from ReflectiveModule base classes\n3. Test coverage remains above 90%\n4. Domain invariants are properly validated\n\n## License\n\n{{license_type}} License - see LICENSE file for details.\n\n## Author\n\n{{author_name}} <{{author_email}}>\n\nGenerated with RM-DDD SDK on {{generation_date}}\n"

    def _get_pyproject_template(self) -> str:
        """Get pyproject.toml template."""
        return '[build-system]\nrequires = ["setuptools>=61.0", "wheel"]\nbuild-backend = "setuptools.build_meta"\n\n[project]\nname = "{{project_name}}"\nversion = "0.1.0"\ndescription = "{{description}}"\nauthors = [\n    {name = "{{author_name}}", email = "{{author_email}}"}\n]\nreadme = "README.md"\nlicense = {text = "{{license_type}}"}\nrequires-python = ">={{python_version}}"\nclassifiers = [\n    "Development Status :: 3 - Alpha",\n    "Intended Audience :: Developers",\n    "License :: OSI Approved :: {{license_type}} License",\n    "Programming Language :: Python :: {{python_version}}",\n    "Topic :: Software Development :: Libraries :: Python Modules",\n]\n\ndependencies = [\n{% for dep, version in dependencies.items() -%}\n    "{{dep}}{{version}}",\n{% endfor %}\n]\n\n[project.optional-dependencies]\ndev = [\n{% for dep, version in dev_dependencies.items() -%}\n    "{{dep}}{{version}}",\n{% endfor %}\n]\n\n[project.urls]\nHomepage = "https://github.com/{{author_name}}/{{project_name}}"\nRepository = "https://github.com/{{author_name}}/{{project_name}}"\nDocumentation = "https://{{project_name}}.readthedocs.io/"\n\n[tool.setuptools.packages.find]\nwhere = ["src"]\n\n[tool.pytest.ini_options]\ntestpaths = ["tests"]\npython_files = ["test_*.py"]\npython_classes = ["Test*"]\npython_functions = ["test_*"]\naddopts = "--cov=src --cov-report=html --cov-report=term-missing --cov-fail-under=90"\n\n[tool.black]\nline-length = 88\ntarget-version = [\'py{{python_version.replace(".", "")}}\']\ninclude = \'\\.pyi?$\'\n\n[tool.mypy]\npython_version = "{{python_version}}"\nwarn_return_any = true\nwarn_unused_configs = true\ndisallow_untyped_defs = true\n'

    def _get_makefile_template(self) -> str:
        """Get Makefile template."""
        return '# {{project_name}} Makefile\n# Systematic development automation\n\n.PHONY: help install test lint format clean build docs\n\nhelp:  ## Show this help message\n\t@echo "Available commands:"\n\t@grep -E \'^[a-zA-Z_-]+:.*?## .*$$\' $(MAKEFILE_LIST) | sort | awk \'BEGIN {FS = ":.*?## "}; {printf "\\033[36m%-20s\\033[0m %s\\n", $$1, $$2}\'\n\ninstall:  ## Install dependencies\n\tpip install -e ".[dev]"\n\ntest:  ## Run tests with coverage\n\tpytest tests/ --cov=src --cov-report=html --cov-report=term-missing\n\ntest-unit:  ## Run unit tests only\n\tpytest tests/unit/ -v\n\ntest-integration:  ## Run integration tests only\n\tpytest tests/integration/ -v\n\nlint:  ## Run linting checks\n\tflake8 src tests\n\tmypy src\n\nformat:  ## Format code\n\tblack src tests\n\tisort src tests\n\nformat-check:  ## Check code formatting\n\tblack --check src tests\n\tisort --check-only src tests\n\nclean:  ## Clean build artifacts\n\trm -rf build/\n\trm -rf dist/\n\trm -rf *.egg-info/\n\trm -rf .coverage\n\trm -rf htmlcov/\n\tfind . -type d -name __pycache__ -delete\n\tfind . -type f -name "*.pyc" -delete\n\nbuild:  ## Build package\n\tpython -m build\n\ndocs:  ## Generate documentation\n\tcd docs && make html\n\ndocs-serve:  ## Serve documentation locally\n\tcd docs/_build/html && python -m http.server 8000\n\n# Beast Mode systematic development targets\nsystematic-check:  ## Run systematic compliance checks\n\t@echo "Running systematic compliance validation..."\n\t@python -c "from rm_ddd import validate_systematic_compliance; validate_systematic_compliance(\'src\')"\n\npdca-cycle:  ## Execute PDCA development cycle\n\t@echo "Executing PDCA cycle..."\n\tmake test\n\tmake lint\n\tmake systematic-check\n\t@echo "PDCA cycle complete - systematic superiority maintained"\n'

    def _get_entities_template(self) -> str:
        """Get domain entities template."""
        return '"""\nDomain entities for {{project_name}}.\n\nThis module contains the core domain entities that represent\nthe main business concepts with identity and lifecycle.\n"""\n\nfrom typing import Any, Dict, List, Optional\nfrom uuid import UUID, uuid4\nfrom datetime import datetime\n\nfrom rm_ddd import Entity, AggregateRoot, ValidationResult, DomainBoundaries\nfrom rm_ddd.decorators import domain_entity, aggregate_root\n\n\n@domain_entity("{{domain_contexts[0] if domain_contexts else \'default\'}}")\nclass ExampleEntity(Entity[UUID]):\n    """Example domain entity demonstrating RM-DDD patterns."""\n    \n    def __init__(self, entity_id: Optional[UUID] = None, name: str = ""):\n        super().__init__(entity_id or uuid4(), "{{domain_contexts[0] if domain_contexts else \'default\'}}")\n        self.name = name\n        self.created_at = datetime.now()\n        self.updated_at = datetime.now()\n    \n    def update_name(self, new_name: str):\n        """Update entity name with business validation."""\n        if not new_name or len(new_name.strip()) == 0:\n            raise ValueError("Name cannot be empty")\n        \n        self.name = new_name.strip()\n        self.updated_at = datetime.now()\n    \n    def get_domain_boundaries(self) -> DomainBoundaries:\n        """Define domain boundaries for this entity."""\n        return DomainBoundaries(\n            context="{{domain_contexts[0] if domain_contexts else \'default\'}}",\n            invariants=[\n                "Name must not be empty",\n                "Created date must be before updated date"\n            ]\n        )\n    \n    def validate_domain_invariants(self) -> ValidationResult:\n        """Validate domain invariants."""\n        result = ValidationResult(is_valid=True)\n        \n        if not self.name or len(self.name.strip()) == 0:\n            result.add_error("Entity name cannot be empty")\n        \n        if self.updated_at < self.created_at:\n            result.add_error("Updated date cannot be before created date")\n        \n        return result\n\n\n@aggregate_root("{{domain_contexts[0] if domain_contexts else \'default\'}}", max_size=50)\nclass ExampleAggregate(AggregateRoot[UUID]):\n    """Example aggregate root demonstrating RM-DDD patterns."""\n    \n    def __init__(self, aggregate_id: Optional[UUID] = None):\n        super().__init__(aggregate_id or uuid4(), "{{domain_contexts[0] if domain_contexts else \'default\'}}")\n        self.items: List[ExampleEntity] = []\n        self.status = "active"\n    \n    def add_item(self, item: ExampleEntity):\n        """Add item to aggregate with business rules."""\n        if len(self.items) >= 50:\n            raise ValueError("Aggregate cannot contain more than 50 items")\n        \n        if item in self.items:\n            raise ValueError("Item already exists in aggregate")\n        \n        self.items.append(item)\n        \n        # Emit domain event (would be implemented with actual event)\n        # self.add_domain_event(ItemAddedEvent(self.id, item.id))\n    \n    def remove_item(self, item_id: UUID):\n        """Remove item from aggregate."""\n        self.items = [item for item in self.items if item.id != item_id]\n        \n        # Emit domain event\n        # self.add_domain_event(ItemRemovedEvent(self.id, item_id))\n    \n    def get_domain_boundaries(self) -> DomainBoundaries:\n        """Define aggregate boundaries."""\n        return DomainBoundaries(\n            context="{{domain_contexts[0] if domain_contexts else \'default\'}}",\n            invariants=[\n                "Aggregate cannot contain more than 50 items",\n                "All items must have unique identities",\n                "Status must be valid"\n            ]\n        )\n    \n    def validate_domain_invariants(self) -> ValidationResult:\n        """Validate aggregate invariants."""\n        result = ValidationResult(is_valid=True)\n        \n        if len(self.items) > 50:\n            result.add_error("Aggregate contains too many items")\n        \n        # Check for duplicate items\n        item_ids = [item.id for item in self.items]\n        if len(item_ids) != len(set(item_ids)):\n            result.add_error("Aggregate contains duplicate items")\n        \n        if self.status not in ["active", "inactive", "archived"]:\n            result.add_error("Invalid aggregate status")\n        \n        return result\n'

    def _get_value_objects_template(self) -> str:
        """Get value objects template."""
        return '"""\nDomain value objects for {{project_name}}.\n\nThis module contains immutable value objects that represent\ndomain concepts without identity.\n"""\n\nfrom dataclasses import dataclass\nfrom decimal import Decimal\nfrom typing import Any\n\nfrom rm_ddd import ValueObject, ImmutableValueObject, ValidationResult\nfrom rm_ddd.decorators import value_object\n\n\n@value_object(immutable=True)\n@dataclass(frozen=True)\nclass Money(ImmutableValueObject):\n    """Money value object with currency."""\n    \n    amount: Decimal\n    currency: str\n    \n    def __post_init__(self):\n        super().__post_init__()\n        \n        if self.amount < 0:\n            raise ValueError("Money amount cannot be negative")\n        \n        if not self.currency or len(self.currency) != 3:\n            raise ValueError("Currency must be a 3-letter ISO code")\n    \n    def add(self, other: \'Money\') -> \'Money\':\n        """Add two money amounts."""\n        if self.currency != other.currency:\n            raise ValueError(f"Cannot add {self.currency} and {other.currency}")\n        \n        return Money(self.amount + other.amount, self.currency)\n    \n    def subtract(self, other: \'Money\') -> \'Money\':\n        """Subtract two money amounts."""\n        if self.currency != other.currency:\n            raise ValueError(f"Cannot subtract {other.currency} from {self.currency}")\n        \n        result_amount = self.amount - other.amount\n        if result_amount < 0:\n            raise ValueError("Result cannot be negative")\n        \n        return Money(result_amount, self.currency)\n    \n    def validate(self) -> ValidationResult:\n        """Validate money value object."""\n        result = ValidationResult(is_valid=True)\n        \n        if self.amount < 0:\n            result.add_error("Money amount cannot be negative")\n        \n        if not self.currency or len(self.currency) != 3:\n            result.add_error("Currency must be a 3-letter ISO code")\n        \n        return result\n\n\n@value_object(immutable=True)\n@dataclass(frozen=True)\nclass EmailAddress(ImmutableValueObject):\n    """Email address value object with validation."""\n    \n    address: str\n    \n    def __post_init__(self):\n        super().__post_init__()\n        \n        if not self._is_valid_email(self.address):\n            raise ValueError(f"Invalid email address: {self.address}")\n    \n    def _is_valid_email(self, email: str) -> bool:\n        """Simple email validation."""\n        import re\n        pattern = r\'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}$\'\n        return re.match(pattern, email) is not None\n    \n    @property\n    def domain(self) -> str:\n        """Get email domain."""\n        return self.address.split(\'@\')[1]\n    \n    @property\n    def local_part(self) -> str:\n        """Get email local part."""\n        return self.address.split(\'@\')[0]\n    \n    def validate(self) -> ValidationResult:\n        """Validate email address."""\n        result = ValidationResult(is_valid=True)\n        \n        if not self._is_valid_email(self.address):\n            result.add_error("Invalid email address format")\n        \n        return result\n'

    def _get_domain_services_template(self) -> str:
        return '"""Domain services for {{project_name}}."""\n\nfrom rm_ddd import DomainService\nfrom rm_ddd.decorators import domain_service\n\n@domain_service("{{domain_contexts[0] if domain_contexts else \'default\'}}")\nclass ExampleDomainService(DomainService):\n    """Example domain service."""\n    \n    def __init__(self):\n        super().__init__("{{domain_contexts[0] if domain_contexts else \'default\'}}", "ExampleDomainService")\n    \n    def perform_business_operation(self, data: str) -> str:\n        """Perform domain-specific business operation."""\n        # Domain logic here\n        return f"Processed: {data}"\n'

    def _get_repositories_template(self) -> str:
        return '"""Repository interfaces for {{project_name}}."""\n\nfrom abc import ABC, abstractmethod\nfrom typing import List, Optional\nfrom uuid import UUID\n\nfrom rm_ddd import Repository\n\nclass ExampleRepository(Repository[ExampleEntity, UUID], ABC):\n    """Repository interface for ExampleEntity."""\n    \n    @abstractmethod\n    async def find_by_name(self, name: str) -> List[ExampleEntity]:\n        """Find entities by name."""\n        pass\n'

    def _get_gitignore_template(self) -> str:
        return "# Python\n__pycache__/\n*.py[cod]\n*$py.class\n*.so\n.Python\nbuild/\ndevelop-eggs/\ndist/\ndownloads/\neggs/\n.eggs/\nlib/\nlib64/\nparts/\nsdist/\nvar/\nwheels/\n*.egg-info/\n.installed.cfg\n*.egg\n\n# Testing\n.coverage\n.pytest_cache/\nhtmlcov/\n\n# IDEs\n.vscode/\n.idea/\n*.swp\n*.swo\n\n# Environment\n.env\n.venv\nenv/\nvenv/\n\n# OS\n.DS_Store\nThumbs.db\n"

    def _get_dockerfile_template(self) -> str:
        return 'FROM python:{{python_version}}-slim\n\nWORKDIR /app\n\nCOPY pyproject.toml .\nRUN pip install -e .\n\nCOPY src/ src/\n\nEXPOSE 8000\n\nCMD ["python", "-m", "{{project_name}}"]\n'

    def _get_docker_compose_template(self) -> str:
        return "version: '3.8'\n\nservices:\n  {{project_name}}:\n    build: .\n    ports:\n      - \"8000:8000\"\n    environment:\n      - ENV=development\n"

    def _get_ci_template(self) -> str:
        return 'name: CI\n\non: [push, pull_request]\n\njobs:\n  test:\n    runs-on: ubuntu-latest\n    strategy:\n      matrix:\n        python-version: [{{python_version}}]\n    \n    steps:\n    - uses: actions/checkout@v3\n    - name: Set up Python\n      uses: actions/setup-python@v4\n      with:\n        python-version: ${{ matrix.python-version }}\n    - name: Install dependencies\n      run: |\n        pip install -e ".[dev]"\n    - name: Run tests\n      run: |\n        make test\n    - name: Run linting\n      run: |\n        make lint\n'

    def _get_persistence_template(self) -> str:
        return '"""Infrastructure persistence layer."""\npass  # Implementation here\n'

    def _get_external_services_template(self) -> str:
        return '"""External service integrations."""\npass  # Implementation here\n'

    def _get_application_services_template(self) -> str:
        return '"""Application services."""\npass  # Implementation here\n'

    def _get_handlers_template(self) -> str:
        return '"""Application handlers."""\npass  # Implementation here\n'

    def _get_conftest_template(self) -> str:
        return '"""Pytest configuration."""\nimport pytest\n'

    def _get_test_entities_template(self) -> str:
        return '"""Tests for domain entities."""\nimport pytest\nfrom src.domain.entities import ExampleEntity\n\ndef test_example_entity_creation():\n    entity = ExampleEntity(name="Test")\n    assert entity.name == "Test"\n'

    def _get_test_repositories_template(self) -> str:
        return (
            '"""Integration tests for repositories."""\npass  # Implementation here\n'
        )

    def _get_settings_template(self) -> str:
        return '"""Application settings."""\nimport os\n\nDATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///{{project_name}}.db")\n'

    def _get_env_template(self) -> str:
        return "# Environment variables\nDATABASE_URL=sqlite:///{{project_name}}.db\nDEBUG=true\n"

    def _get_enterprise_readme_template(self) -> str:
        return self._get_readme_template()

    def _get_enterprise_pyproject_template(self) -> str:
        return self._get_pyproject_template()

    def _get_enterprise_makefile_template(self) -> str:
        return self._get_makefile_template()

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
        for name, template in self._templates.items():
            if not template.get_file_templates():
                result.add_warning(f"Template {name} has no file templates")
        return result


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
    template = ProjectTemplate("minimal", TemplateType.MINIMAL, list(ProjectType))
    template.add_directory("src")
    template.add_directory("tests")
    template.add_directory("docs")
    template.add_file_template("README.md", self._get_readme_template())
    template.add_file_template("pyproject.toml", self._get_pyproject_template())
    template.add_file_template("src/__init__.py", "")
    template.add_file_template("tests/__init__.py", "")
    template.add_file_template(".gitignore", self._get_gitignore_template())
    template.add_dependency("rm-ddd", ">=0.1.0")
    template.add_dev_dependency("pytest", ">=7.0.0")
    template.add_dev_dependency("black", ">=22.0.0")
    template.add_dev_dependency("mypy", ">=0.991")
    self._templates["minimal"] = template


def _create_standard_template(self):
    """Create standard project template."""
    template = ProjectTemplate("standard", TemplateType.STANDARD, list(ProjectType))
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
    template.add_file_template("README.md", self._get_readme_template())
    template.add_file_template("pyproject.toml", self._get_pyproject_template())
    template.add_file_template("Makefile", self._get_makefile_template())
    template.add_file_template(
        "docker-compose.yml", self._get_docker_compose_template()
    )
    template.add_file_template("Dockerfile", self._get_dockerfile_template())
    template.add_file_template(".github/workflows/ci.yml", self._get_ci_template())
    template.add_file_template("src/domain/__init__.py", "")
    template.add_file_template("src/domain/entities.py", self._get_entities_template())
    template.add_file_template(
        "src/domain/value_objects.py", self._get_value_objects_template()
    )
    template.add_file_template(
        "src/domain/services.py", self._get_domain_services_template()
    )
    template.add_file_template(
        "src/domain/repositories.py", self._get_repositories_template()
    )
    template.add_file_template("src/infrastructure/__init__.py", "")
    template.add_file_template(
        "src/infrastructure/persistence.py", self._get_persistence_template()
    )
    template.add_file_template(
        "src/infrastructure/external_services.py",
        self._get_external_services_template(),
    )
    template.add_file_template("src/application/__init__.py", "")
    template.add_file_template(
        "src/application/services.py", self._get_application_services_template()
    )
    template.add_file_template(
        "src/application/handlers.py", self._get_handlers_template()
    )
    template.add_file_template("tests/conftest.py", self._get_conftest_template())
    template.add_file_template(
        "tests/unit/test_entities.py", self._get_test_entities_template()
    )
    template.add_file_template(
        "tests/integration/test_repositories.py", self._get_test_repositories_template()
    )
    template.add_file_template("config/settings.py", self._get_settings_template())
    template.add_file_template(".env.example", self._get_env_template())
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
        [ProjectType.MICROSERVICE, ProjectType.MODULAR_MONOLITH, ProjectType.WEB_API],
    )
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
    template.add_file_template("README.md", self._get_enterprise_readme_template())
    template.add_file_template(
        "pyproject.toml", self._get_enterprise_pyproject_template()
    )
    template.add_file_template("Makefile", self._get_enterprise_makefile_template())
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
    self, config: ProjectConfig, output_path: Path, template_name: Optional[str] = None
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
    validation_result = config.validate_config()
    if not validation_result.is_valid:
        result = ScaffoldingResult(project_path=output_path)
        result.errors.extend(validation_result.errors)
        return result
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
    if not template.supports_project_type(config.project_type):
        result = ScaffoldingResult(project_path=output_path)
        result.errors.append(
            f"Template {template.name} does not support project type {config.project_type.value}"
        )
        return result
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
    project_path.mkdir(parents=True, exist_ok=True)
    result.created_directories.append(project_path)
    for directory in template.get_directory_structure():
        dir_path = project_path / directory
        dir_path.mkdir(parents=True, exist_ok=True)
        result.created_directories.append(dir_path)
    template_context = self._create_template_context(config, template)
    for relative_path, content_template in template.get_file_templates().items():
        try:
            if JINJA2_AVAILABLE:
                from jinja2 import Template

                jinja_template = Template(content_template)
                content = jinja_template.render(**template_context)
            else:
                content = self._simple_template_substitution(
                    content_template, template_context
                )
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


def _simple_template_substitution(self, template: str, context: Dict[str, Any]) -> str:
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


def _get_readme_template(self) -> str:
    """Get README.md template."""
    return "# {{project_name}}\n\n{{description}}\n\n## Overview\n\nThis is an RM-DDD (Reflective Module Domain-Driven Design) project that demonstrates systematic domain modeling with Beast Mode framework integration.\n\n## Features\n\n- Systematic domain modeling with RM-DDD patterns\n- Domain-driven design tactical patterns (Entities, Value Objects, Aggregates)\n- Event sourcing and CQRS capabilities\n- Bounded context management\n- Anti-corruption layers for external integration\n- Comprehensive testing framework\n- Beast Mode PDCA integration\n\n## Getting Started\n\n### Prerequisites\n\n- Python {{python_version}}+\n- pip or poetry for dependency management\n\n### Installation\n\n```bash\npip install -e .\n```\n\n### Usage\n\n```python\nfrom {{project_name}} import YourDomainService\n\n# Your systematic domain implementation here\n```\n\n## Architecture\n\nThis project follows RM-DDD architecture principles:\n\n- **Domain Layer**: Core business logic and domain models\n- **Application Layer**: Use cases and application services  \n- **Infrastructure Layer**: External concerns and persistence\n- **Presentation Layer**: APIs and user interfaces\n\n## Domain Contexts\n\n{% for context in domain_contexts -%}\n- **{{context}}**: [Add description]\n{% endfor %}\n\n## Development\n\n### Running Tests\n\n```bash\nmake test\n```\n\n### Code Quality\n\n```bash\nmake lint\nmake format\n```\n\n## Contributing\n\nThis project follows systematic development principles. Please ensure:\n\n1. All domain logic follows DDD tactical patterns\n2. Components inherit from ReflectiveModule base classes\n3. Test coverage remains above 90%\n4. Domain invariants are properly validated\n\n## License\n\n{{license_type}} License - see LICENSE file for details.\n\n## Author\n\n{{author_name}} <{{author_email}}>\n\nGenerated with RM-DDD SDK on {{generation_date}}\n"


def _get_pyproject_template(self) -> str:
    """Get pyproject.toml template."""
    return '[build-system]\nrequires = ["setuptools>=61.0", "wheel"]\nbuild-backend = "setuptools.build_meta"\n\n[project]\nname = "{{project_name}}"\nversion = "0.1.0"\ndescription = "{{description}}"\nauthors = [\n    {name = "{{author_name}}", email = "{{author_email}}"}\n]\nreadme = "README.md"\nlicense = {text = "{{license_type}}"}\nrequires-python = ">={{python_version}}"\nclassifiers = [\n    "Development Status :: 3 - Alpha",\n    "Intended Audience :: Developers",\n    "License :: OSI Approved :: {{license_type}} License",\n    "Programming Language :: Python :: {{python_version}}",\n    "Topic :: Software Development :: Libraries :: Python Modules",\n]\n\ndependencies = [\n{% for dep, version in dependencies.items() -%}\n    "{{dep}}{{version}}",\n{% endfor %}\n]\n\n[project.optional-dependencies]\ndev = [\n{% for dep, version in dev_dependencies.items() -%}\n    "{{dep}}{{version}}",\n{% endfor %}\n]\n\n[project.urls]\nHomepage = "https://github.com/{{author_name}}/{{project_name}}"\nRepository = "https://github.com/{{author_name}}/{{project_name}}"\nDocumentation = "https://{{project_name}}.readthedocs.io/"\n\n[tool.setuptools.packages.find]\nwhere = ["src"]\n\n[tool.pytest.ini_options]\ntestpaths = ["tests"]\npython_files = ["test_*.py"]\npython_classes = ["Test*"]\npython_functions = ["test_*"]\naddopts = "--cov=src --cov-report=html --cov-report=term-missing --cov-fail-under=90"\n\n[tool.black]\nline-length = 88\ntarget-version = [\'py{{python_version.replace(".", "")}}\']\ninclude = \'\\.pyi?$\'\n\n[tool.mypy]\npython_version = "{{python_version}}"\nwarn_return_any = true\nwarn_unused_configs = true\ndisallow_untyped_defs = true\n'


def _get_makefile_template(self) -> str:
    """Get Makefile template."""
    return '# {{project_name}} Makefile\n# Systematic development automation\n\n.PHONY: help install test lint format clean build docs\n\nhelp:  ## Show this help message\n\t@echo "Available commands:"\n\t@grep -E \'^[a-zA-Z_-]+:.*?## .*$$\' $(MAKEFILE_LIST) | sort | awk \'BEGIN {FS = ":.*?## "}; {printf "\\033[36m%-20s\\033[0m %s\\n", $$1, $$2}\'\n\ninstall:  ## Install dependencies\n\tpip install -e ".[dev]"\n\ntest:  ## Run tests with coverage\n\tpytest tests/ --cov=src --cov-report=html --cov-report=term-missing\n\ntest-unit:  ## Run unit tests only\n\tpytest tests/unit/ -v\n\ntest-integration:  ## Run integration tests only\n\tpytest tests/integration/ -v\n\nlint:  ## Run linting checks\n\tflake8 src tests\n\tmypy src\n\nformat:  ## Format code\n\tblack src tests\n\tisort src tests\n\nformat-check:  ## Check code formatting\n\tblack --check src tests\n\tisort --check-only src tests\n\nclean:  ## Clean build artifacts\n\trm -rf build/\n\trm -rf dist/\n\trm -rf *.egg-info/\n\trm -rf .coverage\n\trm -rf htmlcov/\n\tfind . -type d -name __pycache__ -delete\n\tfind . -type f -name "*.pyc" -delete\n\nbuild:  ## Build package\n\tpython -m build\n\ndocs:  ## Generate documentation\n\tcd docs && make html\n\ndocs-serve:  ## Serve documentation locally\n\tcd docs/_build/html && python -m http.server 8000\n\n# Beast Mode systematic development targets\nsystematic-check:  ## Run systematic compliance checks\n\t@echo "Running systematic compliance validation..."\n\t@python -c "from rm_ddd import validate_systematic_compliance; validate_systematic_compliance(\'src\')"\n\npdca-cycle:  ## Execute PDCA development cycle\n\t@echo "Executing PDCA cycle..."\n\tmake test\n\tmake lint\n\tmake systematic-check\n\t@echo "PDCA cycle complete - systematic superiority maintained"\n'


def _get_entities_template(self) -> str:
    """Get domain entities template."""
    return '"""\nDomain entities for {{project_name}}.\n\nThis module contains the core domain entities that represent\nthe main business concepts with identity and lifecycle.\n"""\n\nfrom typing import Any, Dict, List, Optional\nfrom uuid import UUID, uuid4\nfrom datetime import datetime\n\nfrom rm_ddd import Entity, AggregateRoot, ValidationResult, DomainBoundaries\nfrom rm_ddd.decorators import domain_entity, aggregate_root\n\n\n@domain_entity("{{domain_contexts[0] if domain_contexts else \'default\'}}")\nclass ExampleEntity(Entity[UUID]):\n    """Example domain entity demonstrating RM-DDD patterns."""\n    \n    def __init__(self, entity_id: Optional[UUID] = None, name: str = ""):\n        super().__init__(entity_id or uuid4(), "{{domain_contexts[0] if domain_contexts else \'default\'}}")\n        self.name = name\n        self.created_at = datetime.now()\n        self.updated_at = datetime.now()\n    \n    def update_name(self, new_name: str):\n        """Update entity name with business validation."""\n        if not new_name or len(new_name.strip()) == 0:\n            raise ValueError("Name cannot be empty")\n        \n        self.name = new_name.strip()\n        self.updated_at = datetime.now()\n    \n    def get_domain_boundaries(self) -> DomainBoundaries:\n        """Define domain boundaries for this entity."""\n        return DomainBoundaries(\n            context="{{domain_contexts[0] if domain_contexts else \'default\'}}",\n            invariants=[\n                "Name must not be empty",\n                "Created date must be before updated date"\n            ]\n        )\n    \n    def validate_domain_invariants(self) -> ValidationResult:\n        """Validate domain invariants."""\n        result = ValidationResult(is_valid=True)\n        \n        if not self.name or len(self.name.strip()) == 0:\n            result.add_error("Entity name cannot be empty")\n        \n        if self.updated_at < self.created_at:\n            result.add_error("Updated date cannot be before created date")\n        \n        return result\n\n\n@aggregate_root("{{domain_contexts[0] if domain_contexts else \'default\'}}", max_size=50)\nclass ExampleAggregate(AggregateRoot[UUID]):\n    """Example aggregate root demonstrating RM-DDD patterns."""\n    \n    def __init__(self, aggregate_id: Optional[UUID] = None):\n        super().__init__(aggregate_id or uuid4(), "{{domain_contexts[0] if domain_contexts else \'default\'}}")\n        self.items: List[ExampleEntity] = []\n        self.status = "active"\n    \n    def add_item(self, item: ExampleEntity):\n        """Add item to aggregate with business rules."""\n        if len(self.items) >= 50:\n            raise ValueError("Aggregate cannot contain more than 50 items")\n        \n        if item in self.items:\n            raise ValueError("Item already exists in aggregate")\n        \n        self.items.append(item)\n        \n        # Emit domain event (would be implemented with actual event)\n        # self.add_domain_event(ItemAddedEvent(self.id, item.id))\n    \n    def remove_item(self, item_id: UUID):\n        """Remove item from aggregate."""\n        self.items = [item for item in self.items if item.id != item_id]\n        \n        # Emit domain event\n        # self.add_domain_event(ItemRemovedEvent(self.id, item_id))\n    \n    def get_domain_boundaries(self) -> DomainBoundaries:\n        """Define aggregate boundaries."""\n        return DomainBoundaries(\n            context="{{domain_contexts[0] if domain_contexts else \'default\'}}",\n            invariants=[\n                "Aggregate cannot contain more than 50 items",\n                "All items must have unique identities",\n                "Status must be valid"\n            ]\n        )\n    \n    def validate_domain_invariants(self) -> ValidationResult:\n        """Validate aggregate invariants."""\n        result = ValidationResult(is_valid=True)\n        \n        if len(self.items) > 50:\n            result.add_error("Aggregate contains too many items")\n        \n        # Check for duplicate items\n        item_ids = [item.id for item in self.items]\n        if len(item_ids) != len(set(item_ids)):\n            result.add_error("Aggregate contains duplicate items")\n        \n        if self.status not in ["active", "inactive", "archived"]:\n            result.add_error("Invalid aggregate status")\n        \n        return result\n'


def _get_value_objects_template(self) -> str:
    """Get value objects template."""
    return '"""\nDomain value objects for {{project_name}}.\n\nThis module contains immutable value objects that represent\ndomain concepts without identity.\n"""\n\nfrom dataclasses import dataclass\nfrom decimal import Decimal\nfrom typing import Any\n\nfrom rm_ddd import ValueObject, ImmutableValueObject, ValidationResult\nfrom rm_ddd.decorators import value_object\n\n\n@value_object(immutable=True)\n@dataclass(frozen=True)\nclass Money(ImmutableValueObject):\n    """Money value object with currency."""\n    \n    amount: Decimal\n    currency: str\n    \n    def __post_init__(self):\n        super().__post_init__()\n        \n        if self.amount < 0:\n            raise ValueError("Money amount cannot be negative")\n        \n        if not self.currency or len(self.currency) != 3:\n            raise ValueError("Currency must be a 3-letter ISO code")\n    \n    def add(self, other: \'Money\') -> \'Money\':\n        """Add two money amounts."""\n        if self.currency != other.currency:\n            raise ValueError(f"Cannot add {self.currency} and {other.currency}")\n        \n        return Money(self.amount + other.amount, self.currency)\n    \n    def subtract(self, other: \'Money\') -> \'Money\':\n        """Subtract two money amounts."""\n        if self.currency != other.currency:\n            raise ValueError(f"Cannot subtract {other.currency} from {self.currency}")\n        \n        result_amount = self.amount - other.amount\n        if result_amount < 0:\n            raise ValueError("Result cannot be negative")\n        \n        return Money(result_amount, self.currency)\n    \n    def validate(self) -> ValidationResult:\n        """Validate money value object."""\n        result = ValidationResult(is_valid=True)\n        \n        if self.amount < 0:\n            result.add_error("Money amount cannot be negative")\n        \n        if not self.currency or len(self.currency) != 3:\n            result.add_error("Currency must be a 3-letter ISO code")\n        \n        return result\n\n\n@value_object(immutable=True)\n@dataclass(frozen=True)\nclass EmailAddress(ImmutableValueObject):\n    """Email address value object with validation."""\n    \n    address: str\n    \n    def __post_init__(self):\n        super().__post_init__()\n        \n        if not self._is_valid_email(self.address):\n            raise ValueError(f"Invalid email address: {self.address}")\n    \n    def _is_valid_email(self, email: str) -> bool:\n        """Simple email validation."""\n        import re\n        pattern = r\'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}$\'\n        return re.match(pattern, email) is not None\n    \n    @property\n    def domain(self) -> str:\n        """Get email domain."""\n        return self.address.split(\'@\')[1]\n    \n    @property\n    def local_part(self) -> str:\n        """Get email local part."""\n        return self.address.split(\'@\')[0]\n    \n    def validate(self) -> ValidationResult:\n        """Validate email address."""\n        result = ValidationResult(is_valid=True)\n        \n        if not self._is_valid_email(self.address):\n            result.add_error("Invalid email address format")\n        \n        return result\n'


def _get_domain_services_template(self) -> str:
    return '"""Domain services for {{project_name}}."""\n\nfrom rm_ddd import DomainService\nfrom rm_ddd.decorators import domain_service\n\n@domain_service("{{domain_contexts[0] if domain_contexts else \'default\'}}")\nclass ExampleDomainService(DomainService):\n    """Example domain service."""\n    \n    def __init__(self):\n        super().__init__("{{domain_contexts[0] if domain_contexts else \'default\'}}", "ExampleDomainService")\n    \n    def perform_business_operation(self, data: str) -> str:\n        """Perform domain-specific business operation."""\n        # Domain logic here\n        return f"Processed: {data}"\n'


def _get_repositories_template(self) -> str:
    return '"""Repository interfaces for {{project_name}}."""\n\nfrom abc import ABC, abstractmethod\nfrom typing import List, Optional\nfrom uuid import UUID\n\nfrom rm_ddd import Repository\n\nclass ExampleRepository(Repository[ExampleEntity, UUID], ABC):\n    """Repository interface for ExampleEntity."""\n    \n    @abstractmethod\n    async def find_by_name(self, name: str) -> List[ExampleEntity]:\n        """Find entities by name."""\n        pass\n'


def _get_gitignore_template(self) -> str:
    return "# Python\n__pycache__/\n*.py[cod]\n*$py.class\n*.so\n.Python\nbuild/\ndevelop-eggs/\ndist/\ndownloads/\neggs/\n.eggs/\nlib/\nlib64/\nparts/\nsdist/\nvar/\nwheels/\n*.egg-info/\n.installed.cfg\n*.egg\n\n# Testing\n.coverage\n.pytest_cache/\nhtmlcov/\n\n# IDEs\n.vscode/\n.idea/\n*.swp\n*.swo\n\n# Environment\n.env\n.venv\nenv/\nvenv/\n\n# OS\n.DS_Store\nThumbs.db\n"


def _get_dockerfile_template(self) -> str:
    return 'FROM python:{{python_version}}-slim\n\nWORKDIR /app\n\nCOPY pyproject.toml .\nRUN pip install -e .\n\nCOPY src/ src/\n\nEXPOSE 8000\n\nCMD ["python", "-m", "{{project_name}}"]\n'


def _get_docker_compose_template(self) -> str:
    return "version: '3.8'\n\nservices:\n  {{project_name}}:\n    build: .\n    ports:\n      - \"8000:8000\"\n    environment:\n      - ENV=development\n"


def _get_ci_template(self) -> str:
    return 'name: CI\n\non: [push, pull_request]\n\njobs:\n  test:\n    runs-on: ubuntu-latest\n    strategy:\n      matrix:\n        python-version: [{{python_version}}]\n    \n    steps:\n    - uses: actions/checkout@v3\n    - name: Set up Python\n      uses: actions/setup-python@v4\n      with:\n        python-version: ${{ matrix.python-version }}\n    - name: Install dependencies\n      run: |\n        pip install -e ".[dev]"\n    - name: Run tests\n      run: |\n        make test\n    - name: Run linting\n      run: |\n        make lint\n'


def _get_persistence_template(self) -> str:
    return '"""Infrastructure persistence layer."""\npass  # Implementation here\n'


def _get_external_services_template(self) -> str:
    return '"""External service integrations."""\npass  # Implementation here\n'


def _get_application_services_template(self) -> str:
    return '"""Application services."""\npass  # Implementation here\n'


def _get_handlers_template(self) -> str:
    return '"""Application handlers."""\npass  # Implementation here\n'


def _get_settings_template(self) -> str:
    return '"""Application settings."""\nimport os\n\nDATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///{{project_name}}.db")\n'


def _get_env_template(self) -> str:
    return "# Environment variables\nDATABASE_URL=sqlite:///{{project_name}}.db\nDEBUG=true\n"


def _get_enterprise_readme_template(self) -> str:
    return self._get_readme_template()


def _get_enterprise_pyproject_template(self) -> str:
    return self._get_pyproject_template()


def _get_enterprise_makefile_template(self) -> str:
    return self._get_makefile_template()


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
