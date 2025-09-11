"""
RM-DDD SDK: Systematic Domain-Driven Development

The foundational package for systematic domain-driven development
using the Beast Mode framework and Reflective Module architecture.

Core Philosophy: "The Requirements ARE the Solution"
"""

__version__ = "0.1.0"
__author__ = "Beast Mode Development Team"
__email__ = "team@beastmode.dev"

# Core RM Layer
from .core.base import ReflectiveModuleBase, DomainReflectiveModule
from .core.health import ModuleHealth, DomainHealth, HealthMonitor
from .core.registry import get_global_registry, ModuleCapability
from .core.compliance import ComplianceValidator, ValidationResult

# DDD Pattern Layer
from .domain.entities import Entity, AggregateRoot
from .domain.value_objects import ValueObject, ImmutableValueObject
from .domain.services import DomainService
from .domain.repositories import Repository, RepositoryRM
from .domain.events import DomainEvent, DomainEventPublisher, DomainEventHandler
from .domain.event_sourcing import (
    EventStore,
    SnapshotStore,
    EventSourcedAggregate,
    EventSourcingRepository,
    InMemoryEventStore,
    InMemorySnapshotStore,
)
from .domain.contexts import (
    BoundedContext, 
    ContextMapper,
    ContextRelationshipType,
    IntegrationPattern,
)
from .domain.shared_kernel import (
    SharedKernel,
    SharedKernelRegistry,
    SharedElement,
    SharedElementType,
)

# Infrastructure Layer
from .infrastructure.separation import (
    DependencyValidator,
    LayerViolation,
    LayerSeparationEnforcer,
    validate_dependency_direction,
)
from .infrastructure.anticorruption import (
    AntiCorruptionLayer,
    ContextTranslator,
    DomainAdapter,
    ExternalSystemAdapter,
)

# Convenience Layer
from .utilities.decorators import (
    domain_entity,
    aggregate_root,
    domain_service,
    ubiquitous_language,
    value_object,
    domain_event,
)
from .utilities.validators import (
    DomainValidator,
    BusinessRuleValidator,
    InvariantValidator,
    validate_entity_invariants,
    validate_aggregate_boundaries,
)
from .utilities.complexity import (
    ComplexityMonitor,
    ComplexityReport,
    ComplexityType,
    analyze_class_complexity,
    analyze_method_complexity,
)
from .utilities.generators import RMDDDCodeGenerator

# Scaffolding Layer
from .scaffolding import (
    ProjectGenerator,
    ProjectTemplate,
    ProjectConfig,
    ScaffoldingResult,
    DomainContextInitializer,
    BoundedContextConfig,
    DomainSetupResult,
    get_default_project_templates,
    create_custom_project_template,
)

# Data Models
from .models import (
    ModuleStatus,
    AggregateBoundaries,
    DomainCriteria,
    Money,
    DomainException,
)

# Export main classes for easy import
__all__ = [
    # Version info
    "__version__",
    "__author__",
    "__email__",
    
    # Core RM Layer
    "ReflectiveModuleBase",
    "DomainReflectiveModule",
    "ModuleHealth",
    "DomainHealth",
    "HealthMonitor",
    "get_global_registry",
    "ModuleCapability",
    "ComplianceValidator",
    "ValidationResult",
    
    # DDD Pattern Layer
    "Entity",
    "AggregateRoot",
    "ValueObject",
    "ImmutableValueObject",
    "DomainService",
    "Repository",
    "RepositoryRM",
    "DomainEvent",
    "DomainEventPublisher",
    "DomainEventHandler",
    "EventStore",
    "SnapshotStore",
    "EventSourcedAggregate",
    "EventSourcingRepository",
    "InMemoryEventStore",
    "InMemorySnapshotStore",
    "BoundedContext",
    "ContextMapper",
    "ContextRelationshipType", 
    "IntegrationPattern",
    "SharedKernel",
    "SharedKernelRegistry",
    "SharedElement",
    "SharedElementType",
    
    # Infrastructure Layer
    "DependencyValidator",
    "LayerViolation",
    "LayerSeparationEnforcer",
    "validate_dependency_direction",
    "AntiCorruptionLayer",
    "ContextTranslator",
    "DomainAdapter",
    "ExternalSystemAdapter",
    
    # Convenience Layer
    "domain_entity",
    "aggregate_root",
    "domain_service",
    "ubiquitous_language",
    "value_object",
    "domain_event",
    "DomainValidator",
    "BusinessRuleValidator",
    "InvariantValidator",
    "validate_entity_invariants",
    "validate_aggregate_boundaries",
    "ComplexityMonitor",
    "ComplexityReport",
    "ComplexityType",
    "analyze_class_complexity",
    "analyze_method_complexity",
    "RMDDDCodeGenerator",
    
    # Scaffolding Layer
    "ProjectGenerator",
    "ProjectTemplate",
    "ProjectConfig", 
    "ScaffoldingResult",
    "DomainContextInitializer",
    "BoundedContextConfig",
    "DomainSetupResult",
    "get_default_project_templates",
    "create_custom_project_template",
    
    # Data Models
    "ModuleStatus",
    "AggregateBoundaries",
    "DomainCriteria",
    "Money",
    "DomainException",
]

# Ecosystem integration shortcuts
def get_ecosystem_info():
    """Get information about the complete Beast Mode ecosystem."""
    return {
        "rm_ddd_version": __version__,
        "ecosystem_components": [
            "Beast Mode Framework",
            "Ghostbusters AI Agents", 
            "Spec-to-Code Engine",
            "Intelligent Quality System",
            "RM Registry",
        ],
        "philosophy": "The Requirements ARE the Solution",
        "documentation": "https://rm-ddd.readthedocs.io/",
        "ecosystem_docs": "https://beast-mode.dev/ecosystem",
    }

def quick_start_example():
    """Get a quick start code example."""
    return '''
from rm_ddd import DomainEntity, AggregateRoot
from rm_ddd.decorators import domain_entity

@domain_entity("order_management")
class Order(AggregateRoot[str]):
    def __init__(self, order_id: str, customer_id: str):
        super().__init__(order_id, "order_management")
        self.customer_id = customer_id
        self.items = []
        self.status = "pending"
    
    def add_item(self, product_id: str, quantity: int, price: float):
        if quantity <= 0:
            raise ValueError("Quantity must be positive")
        
        self.items.append({
            "product_id": product_id,
            "quantity": quantity,
            "price": price
        })
        
        # Emit domain event
        self.add_domain_event(OrderItemAdded(
            order_id=self.id,
            product_id=product_id,
            quantity=quantity
        ))
    
    def get_domain_boundaries(self):
        return DomainBoundaries(
            context="order_management",
            invariants=["total_amount >= 0", "items not empty when confirmed"]
        )
    
    def validate_domain_invariants(self):
        result = ValidationResult(is_valid=True)
        
        if self.status == "confirmed" and not self.items:
            result.add_error("Confirmed order must have items")
        
        total = sum(item["price"] * item["quantity"] for item in self.items)
        if total < 0:
            result.add_error("Order total cannot be negative")
        
        return result
'''