"""
Domain context initializer for RM-DDD projects.

Provides systematic initialization of bounded contexts with proper
domain structure, validation, and best practices.
"""

import logging
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from ..core.base import DomainReflectiveModule
from ..core.compliance import ValidationResult
from ..models import DomainException


logger = logging.getLogger(__name__)


@dataclass
class BoundedContextConfig:
    """Configuration for bounded context initialization."""

    context_name: str
    description: str = ""
    entities: List[str] = field(default_factory=list)
    value_objects: List[str] = field(default_factory=list)
    domain_services: List[str] = field(default_factory=list)
    repositories: List[str] = field(default_factory=list)
    events: List[str] = field(default_factory=list)
    ubiquitous_language: Dict[str, str] = field(default_factory=dict)
    integration_patterns: List[str] = field(default_factory=list)

    def validate_config(self) -> ValidationResult:
        """Validate bounded context configuration."""
        result = ValidationResult(is_valid=True)

        if not self.context_name:
            result.add_error("Context name is required")
        elif not self.context_name.replace("_", "").isalnum():
            result.add_error("Context name must be alphanumeric with underscores")

        if not self.entities and not self.value_objects:
            result.add_warning("Context has no entities or value objects defined")

        return result


@dataclass
class DomainSetupResult:
    """Result of domain context setup."""

    context_name: str
    created_files: List[Path] = field(default_factory=list)
    created_directories: List[Path] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)
    setup_time: datetime = field(default_factory=datetime.now)

    @property
    def success(self) -> bool:
        """Check if setup was successful."""
        return len(self.errors) == 0


class DomainContextInitializer(DomainReflectiveModule):
    """
    Initializes bounded contexts within RM-DDD projects.

    Provides systematic setup of domain contexts with proper structure,
    validation, and integration patterns.
    """

    def __init__(self, domain_context: str = "domain_initialization"):
        super().__init__(domain_context)
        self._initialized_contexts: List[DomainSetupResult] = []

    def initialize_bounded_context(
        self, config: BoundedContextConfig, project_path: Path
    ) -> DomainSetupResult:
        """
        Initialize a bounded context in an existing project.

        Args:
            config: Bounded context configuration
            project_path: Path to the project root

        Returns:
            DomainSetupResult: Setup results
        """
        # Validate configuration
        validation_result = config.validate_config()
        if not validation_result.is_valid:
            result = DomainSetupResult(context_name=config.context_name)
            result.errors.extend(validation_result.errors)
            return result

        try:
            result = self._setup_context_structure(config, project_path)
            self._initialized_contexts.append(result)
            return result

        except Exception as e:
            logger.error(f"Context initialization failed: {e}")
            result = DomainSetupResult(context_name=config.context_name)
            result.errors.append(f"Initialization failed: {str(e)}")
            return result

    def _setup_context_structure(
        self, config: BoundedContextConfig, project_path: Path
    ) -> DomainSetupResult:
        """Set up the bounded context directory structure and files."""
        result = DomainSetupResult(context_name=config.context_name)

        # Create context directory structure
        context_path = project_path / "src" / "domain" / config.context_name

        directories = [
            context_path,
            context_path / "entities",
            context_path / "value_objects",
            context_path / "services",
            context_path / "repositories",
            context_path / "events",
        ]

        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)
            result.created_directories.append(directory)

        # Create __init__.py files
        init_files = [
            context_path / "__init__.py",
            context_path / "entities" / "__init__.py",
            context_path / "value_objects" / "__init__.py",
            context_path / "services" / "__init__.py",
            context_path / "repositories" / "__init__.py",
            context_path / "events" / "__init__.py",
        ]

        for init_file in init_files:
            init_file.write_text(f'"""Domain context: {config.context_name}"""\n')
            result.created_files.append(init_file)

        # Generate entity files
        for entity_name in config.entities:
            entity_file = self._create_entity_file(config, entity_name, context_path)
            result.created_files.append(entity_file)

        # Generate value object files
        for vo_name in config.value_objects:
            vo_file = self._create_value_object_file(config, vo_name, context_path)
            result.created_files.append(vo_file)

        # Generate domain service files
        for service_name in config.domain_services:
            service_file = self._create_domain_service_file(
                config, service_name, context_path
            )
            result.created_files.append(service_file)

        # Generate repository files
        for repo_name in config.repositories:
            repo_file = self._create_repository_file(config, repo_name, context_path)
            result.created_files.append(repo_file)

        # Generate event files
        for event_name in config.events:
            event_file = self._create_event_file(config, event_name, context_path)
            result.created_files.append(event_file)

        # Create context configuration file
        config_file = self._create_context_config_file(config, context_path)
        result.created_files.append(config_file)

        logger.info(f"Initialized bounded context: {config.context_name}")
        return result

    def _create_entity_file(
        self, config: BoundedContextConfig, entity_name: str, context_path: Path
    ) -> Path:
        """Create an entity file."""
        file_path = context_path / "entities" / f"{entity_name.lower()}.py"

        content = f'''"""
{entity_name} entity for {config.context_name} domain context.
"""

from typing import Any, Dict, List, Optional
from uuid import UUID, uuid4
from datetime import datetime

from rm_ddd import Entity, ValidationResult, DomainBoundaries
from rm_ddd.decorators import domain_entity


@domain_entity("{config.context_name}")
class {entity_name}(Entity[UUID]):
    """
    {entity_name} entity in the {config.context_name} bounded context.
    
    {config.description}
    """
    
    def __init__(self, entity_id: Optional[UUID] = None):
        super().__init__(entity_id or uuid4(), "{config.context_name}")
        self.created_at = datetime.now()
        self.updated_at = datetime.now()
        
        # TODO: Add entity-specific attributes
    
    def get_domain_boundaries(self) -> DomainBoundaries:
        """Define domain boundaries for this entity."""
        return DomainBoundaries(
            context="{config.context_name}",
            invariants=[
                # TODO: Define domain invariants
                "Entity must have valid ID",
                "Created date must be before updated date"
            ],
            ubiquitous_language={{
{self._format_ubiquitous_language(config.ubiquitous_language)}
            }}
        )
    
    def validate_domain_invariants(self) -> ValidationResult:
        """Validate domain invariants for this entity."""
        result = ValidationResult(is_valid=True)
        
        # TODO: Implement domain validation logic
        if self.updated_at < self.created_at:
            result.add_error("Updated date cannot be before created date")
        
        return result
'''

        file_path.write_text(content)
        return file_path

    def _create_value_object_file(
        self, config: BoundedContextConfig, vo_name: str, context_path: Path
    ) -> Path:
        """Create a value object file."""
        file_path = context_path / "value_objects" / f"{vo_name.lower()}.py"

        content = f'''"""
{vo_name} value object for {config.context_name} domain context.
"""

from dataclasses import dataclass
from typing import Any

from rm_ddd import ImmutableValueObject, ValidationResult
from rm_ddd.decorators import value_object


@value_object(immutable=True)
@dataclass(frozen=True)
class {vo_name}(ImmutableValueObject):
    """
    {vo_name} value object in the {config.context_name} bounded context.
    
    {config.description}
    """
    
    # TODO: Add value object attributes
    value: str
    
    def __post_init__(self):
        super().__post_init__()
        # TODO: Add validation logic
        if not self.value:
            raise ValueError("{vo_name} value cannot be empty")
    
    def validate(self) -> ValidationResult:
        """Validate value object constraints."""
        result = ValidationResult(is_valid=True)
        
        # TODO: Implement validation logic
        if not self.value:
            result.add_error("Value cannot be empty")
        
        return result
'''

        file_path.write_text(content)
        return file_path

    def _create_domain_service_file(
        self, config: BoundedContextConfig, service_name: str, context_path: Path
    ) -> Path:
        """Create a domain service file."""
        file_path = context_path / "services" / f"{service_name.lower()}.py"

        content = f'''"""
{service_name} domain service for {config.context_name} domain context.
"""

from rm_ddd import DomainService, ValidationResult, DomainBoundaries
from rm_ddd.decorators import domain_service


@domain_service("{config.context_name}", stateless=True)
class {service_name}(DomainService):
    """
    {service_name} domain service in the {config.context_name} bounded context.
    
    {config.description}
    """
    
    def __init__(self):
        super().__init__("{config.context_name}", "{service_name}")
    
    def perform_domain_operation(self, data: str) -> str:
        """
        Perform domain-specific business operation.
        
        Args:
            data: Input data for the operation
            
        Returns:
            str: Result of the operation
        """
        # TODO: Implement domain logic
        return f"Processed by {service_name}: {{data}}"
    
    def get_domain_boundaries(self) -> DomainBoundaries:
        """Define domain boundaries for this service."""
        return DomainBoundaries(
            context="{config.context_name}",
            invariants=[
                "Service must be stateless",
                "Service must contain only domain logic"
            ]
        )
    
    def validate_domain_invariants(self) -> ValidationResult:
        """Validate domain invariants for this service."""
        result = ValidationResult(is_valid=True)
        
        # TODO: Implement service validation logic
        
        return result
'''

        file_path.write_text(content)
        return file_path

    def _create_repository_file(
        self, config: BoundedContextConfig, repo_name: str, context_path: Path
    ) -> Path:
        """Create a repository interface file."""
        file_path = context_path / "repositories" / f"{repo_name.lower()}.py"

        content = f'''"""
{repo_name} repository interface for {config.context_name} domain context.
"""

from abc import ABC, abstractmethod
from typing import List, Optional
from uuid import UUID

from rm_ddd import Repository


class {repo_name}(Repository[Any, UUID], ABC):
    """
    {repo_name} repository interface in the {config.context_name} bounded context.
    
    {config.description}
    """
    
    @abstractmethod
    async def find_by_criteria(self, criteria: str) -> List[Any]:
        """
        Find entities by domain-specific criteria.
        
        Args:
            criteria: Domain criteria for search
            
        Returns:
            List[Any]: Matching entities
        """
        pass
    
    @abstractmethod
    async def save_aggregate(self, aggregate: Any) -> Any:
        """
        Save aggregate with all its entities.
        
        Args:
            aggregate: Aggregate to save
            
        Returns:
            Any: Saved aggregate
        """
        pass
'''

        file_path.write_text(content)
        return file_path

    def _create_event_file(
        self, config: BoundedContextConfig, event_name: str, context_path: Path
    ) -> Path:
        """Create a domain event file."""
        file_path = context_path / "events" / f"{event_name.lower()}.py"

        content = f'''"""
{event_name} domain event for {config.context_name} domain context.
"""

from typing import Any, Dict
from uuid import UUID

from rm_ddd import DomainEvent
from rm_ddd.decorators import domain_event


@domain_event(event_version=1)
class {event_name}(DomainEvent):
    """
    {event_name} domain event in the {config.context_name} bounded context.
    
    {config.description}
    """
    
    def __init__(self, aggregate_id: UUID, **event_data):
        super().__init__(aggregate_id)
        self.event_data = event_data
    
    def get_event_data(self) -> Dict[str, Any]:
        """Get event-specific data."""
        return {{
            "event_type": "{event_name}",
            "context": "{config.context_name}",
            **self.event_data
        }}
'''

        file_path.write_text(content)
        return file_path

    def _create_context_config_file(
        self, config: BoundedContextConfig, context_path: Path
    ) -> Path:
        """Create context configuration file."""
        file_path = context_path / "context_config.py"

        content = f'''"""
Configuration for {config.context_name} bounded context.
"""

from rm_ddd import BoundedContext, ContextRelationshipType, IntegrationPattern

# Bounded context configuration
CONTEXT_NAME = "{config.context_name}"
CONTEXT_DESCRIPTION = "{config.description}"

# Ubiquitous language mapping
UBIQUITOUS_LANGUAGE = {{
{self._format_ubiquitous_language(config.ubiquitous_language)}
}}

# Integration patterns
INTEGRATION_PATTERNS = {config.integration_patterns}

# Context boundaries
DOMAIN_INVARIANTS = [
    # TODO: Define context-level invariants
    "All entities must belong to this bounded context",
    "Cross-context communication must use defined integration patterns"
]

def create_bounded_context() -> BoundedContext:
    """Create and configure the bounded context."""
    context = BoundedContext(
        context_name=CONTEXT_NAME,
        description=CONTEXT_DESCRIPTION
    )
    
    # TODO: Configure context relationships and integrations
    
    return context
'''

        file_path.write_text(content)
        return file_path

    def _format_ubiquitous_language(self, language_mapping: Dict[str, str]) -> str:
        """Format ubiquitous language mapping for code generation."""
        if not language_mapping:
            return "                # TODO: Define ubiquitous language terms"

        formatted_items = []
        for term, definition in language_mapping.items():
            formatted_items.append(f'                "{term}": "{definition}"')

        return ",\n".join(formatted_items)

    def get_initialization_summary(self) -> Dict[str, Any]:
        """Get summary of context initialization activity."""
        successful_contexts = [c for c in self._initialized_contexts if c.success]
        failed_contexts = [c for c in self._initialized_contexts if not c.success]

        return {
            "total_contexts": len(self._initialized_contexts),
            "successful_contexts": len(successful_contexts),
            "failed_contexts": len(failed_contexts),
            "success_rate": len(successful_contexts)
            / max(len(self._initialized_contexts), 1),
            "context_names": [c.context_name for c in successful_contexts],
        }

    # RM Interface Implementation
    async def get_module_status(self):
        """Get module status."""
        from ..core.health import ModuleHealth
        from ..models import ModuleStatus

        summary = self.get_initialization_summary()

        return ModuleHealth(
            status=ModuleStatus.AVAILABLE,
            message=f"Domain initializer - {summary['total_contexts']} contexts initialized",
            capabilities=await self.get_module_capabilities(),
            health_indicators={
                "initialized_contexts": summary["total_contexts"],
                "success_rate": summary["success_rate"],
            },
        )

    async def get_module_capabilities(self):
        """Get module capabilities."""
        from ..models import ModuleCapability

        return [
            ModuleCapability(
                name="domain_context_initialization",
                description="Initializes bounded contexts in RM-DDD projects",
                available=True,
                version="1.0.0",
            )
        ]

    async def is_healthy(self) -> bool:
        """Check if domain initializer is healthy."""
        return True

    async def get_health_indicators(self):
        """Get health indicators."""
        return {
            "initialization_summary": self.get_initialization_summary(),
            "domain_context": self.domain_context,
        }

    def get_domain_boundaries(self):
        """Get domain boundaries."""
        from ..models import DomainBoundaries

        return DomainBoundaries(
            context=self.domain_context,
            invariants=[
                "Context configurations must be valid",
                "Generated files must be syntactically correct",
                "Domain structure must follow RM-DDD patterns",
            ],
        )

    def validate_domain_invariants(self):
        """Validate domain invariants."""
        result = ValidationResult(is_valid=True)

        # Validate initialization results
        for context_result in self._initialized_contexts:
            if not context_result.success:
                result.add_warning(
                    f"Context {context_result.context_name} initialization had errors"
                )

        return result
