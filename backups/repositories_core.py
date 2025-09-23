"""
Repositories Core

This module was extracted from repositories.py
as part of RM-DDD compliance refactoring.
"""

import logging
from abc import ABC, abstractmethod
from typing import Any, Dict, Generic, List, Optional, TypeVar, Union
from datetime import datetime
from ..core.base import DomainReflectiveModule
from ..core.compliance import ValidationResult
from ..models import (
    ModuleStatus,
    ModuleCapability,
    DomainBoundaries,
    DomainCriteria,
    DomainException,
    EntityId,
)
from ..core.health import ModuleHealth


class Repository(ABC, Generic[T, ID]):
    """
    Abstract repository interface for domain layer.

    Provides the contract for data access operations without exposing
    infrastructure concerns to the domain layer. This interface should
    be implemented by infrastructure layer components.

    Key Responsibilities:
    - Define domain-appropriate data access operations
    - Abstract infrastructure concerns from domain layer
    - Provide domain-specific query capabilities
    - Maintain domain object lifecycle
    - Support domain-driven query patterns

    Accountability Chain:
    - Domain Expert: Responsible for defining domain-appropriate operations
    - Repository Designer: Responsible for interface design
    - Infrastructure Team: Responsible for implementation
    """

    @abstractmethod
    async def get_by_id(self, entity_id: ID) -> Optional[T]:
        """
        Get entity by ID.

        Args:
            entity_id: Unique identifier of the entity

        Returns:
            Entity if found, None otherwise
        """
        pass

    @abstractmethod
    async def save(self, entity: T) -> T:
        """
        Save entity.

        Args:
            entity: Entity to save

        Returns:
            Saved entity (may include generated IDs, updated timestamps, etc.)
        """
        pass

    @abstractmethod
    async def delete(self, entity_id: ID) -> bool:
        """
        Delete entity by ID.

        Args:
            entity_id: Unique identifier of the entity to delete

        Returns:
            True if entity was deleted, False if not found
        """
        pass

    @abstractmethod
    async def find_by_criteria(self, criteria: DomainCriteria) -> List[T]:
        """
        Find entities by domain criteria.

        Args:
            criteria: Domain-specific search criteria

        Returns:
            List of entities matching the criteria
        """
        pass

    @abstractmethod
    async def count_by_criteria(self, criteria: DomainCriteria) -> int:
        """
        Count entities by domain criteria.

        Args:
            criteria: Domain-specific search criteria

        Returns:
            Number of entities matching the criteria
        """
        pass

    @abstractmethod
    async def exists(self, entity_id: ID) -> bool:
        """
        Check if entity exists.

        Args:
            entity_id: Unique identifier of the entity

        Returns:
            True if entity exists, False otherwise
        """
        pass


class RepositoryRM(Repository[T, ID], DomainReflectiveModule):
    """
    RM-compliant repository base class.

    Extends the Repository interface with RM compliance, health monitoring,
    and systematic validation capabilities.

    Additional Responsibilities:
    - RM compliance and health monitoring
    - Repository performance tracking
    - Domain boundary validation
    - Connection health management
    - Query performance monitoring

    Accountability Chain:
    - Repository Owner: Responsible for repository-specific implementation
    - Domain Expert: Responsible for domain-appropriate operations
    - Infrastructure Team: Responsible for underlying data access
    - RM Framework: Responsible for systematic compliance
    """

    def __init__(
        self, domain_context: str, entity_type: str, module_id: Optional[str] = None
    ):
        """
        Initialize RM-compliant repository.

        Args:
            domain_context: The bounded context this repository operates within
            entity_type: Type of entity this repository manages
            module_id: Optional RM module identifier
        """
        self.entity_type = entity_type
        self._query_count = 0
        self._save_count = 0
        self._delete_count = 0
        self._error_count = 0
        self._last_operation_time: Optional[datetime] = None
        self._connection_healthy = True
        super().__init__(domain_context, module_id)
        logger.info(
            f"RepositoryRM initialized: {entity_type} in context: {domain_context}"
        )

    def _record_operation(self, operation_type: str, success: bool = True):
        """
        Record repository operation for monitoring.

        Args:
            operation_type: Type of operation (query, save, delete)
            success: Whether the operation was successful
        """
        self._last_operation_time = datetime.now()
        if operation_type == "query":
            self._query_count += 1
        elif operation_type == "save":
            self._save_count += 1
        elif operation_type == "delete":
            self._delete_count += 1
        if not success:
            self._error_count += 1
        logger.debug(
            f"Repository operation recorded: {operation_type} for {self.entity_type}"
        )

    @abstractmethod
    async def _perform_health_check(self):
        """
        Perform repository-specific health check.

        This method should be implemented by concrete repository classes
        to check the health of their underlying data store connections.

        Raises:
            Exception: If health check fails
        """
        pass

    def get_repository_capabilities(self) -> List[str]:
        """
        Get repository-specific capabilities.

        Returns:
            List of capability names provided by this repository
        """
        return [
            f"{self.entity_type.lower()}_read",
            f"{self.entity_type.lower()}_write",
            f"{self.entity_type.lower()}_delete",
            f"{self.entity_type.lower()}_query",
        ]

    def validate_repository_constraints(self) -> ValidationResult:
        """
        Validate repository-specific constraints.

        Returns:
            ValidationResult: Result of repository constraint validation
        """
        result = ValidationResult(is_valid=True)
        if not self.entity_type or not self.entity_type.strip():
            result.add_error(
                "Repository must have a valid entity type",
                code="REPO_001",
                component=self.__class__.__name__,
            )
        if not self.domain_context or not self.domain_context.strip():
            result.add_error(
                "Repository must have a valid domain context",
                code="REPO_002",
                component=self.__class__.__name__,
            )
        if not self._connection_healthy:
            result.add_error(
                "Repository connection is unhealthy",
                code="REPO_003",
                component=self.__class__.__name__,
            )
        return result

    def get_repository_info(self) -> Dict[str, Any]:
        """Get comprehensive repository information."""
        return {
            "entity_type": self.entity_type,
            "repository_type": self.__class__.__name__,
            "domain_context": self.domain_context,
            "module_id": self.module_id,
            "query_count": self._query_count,
            "save_count": self._save_count,
            "delete_count": self._delete_count,
            "error_count": self._error_count,
            "last_operation": (
                self._last_operation_time.isoformat()
                if self._last_operation_time
                else None
            ),
            "connection_healthy": self._connection_healthy,
            "capabilities": self.get_repository_capabilities(),
        }

    async def get_by_id(self, entity_id: ID) -> Optional[T]:
        """Get entity by ID with monitoring."""
        try:
            result = await self._get_by_id_impl(entity_id)
            self._record_operation("query", success=True)
            return result
        except Exception as e:
            self._record_operation("query", success=False)
            logger.error(f"Failed to get {self.entity_type} by ID {entity_id}: {e}")
            raise

    async def save(self, entity: T) -> T:
        """Save entity with monitoring."""
        try:
            result = await self._save_impl(entity)
            self._record_operation("save", success=True)
            return result
        except Exception as e:
            self._record_operation("save", success=False)
            logger.error(f"Failed to save {self.entity_type}: {e}")
            raise

    async def delete(self, entity_id: ID) -> bool:
        """Delete entity with monitoring."""
        try:
            result = await self._delete_impl(entity_id)
            self._record_operation("delete", success=True)
            return result
        except Exception as e:
            self._record_operation("delete", success=False)
            logger.error(
                f"Failed to delete {self.entity_type} with ID {entity_id}: {e}"
            )
            raise

    async def find_by_criteria(self, criteria: DomainCriteria) -> List[T]:
        """Find entities by criteria with monitoring."""
        try:
            result = await self._find_by_criteria_impl(criteria)
            self._record_operation("query", success=True)
            return result
        except Exception as e:
            self._record_operation("query", success=False)
            logger.error(f"Failed to find {self.entity_type} by criteria: {e}")
            raise

    async def count_by_criteria(self, criteria: DomainCriteria) -> int:
        """Count entities by criteria with monitoring."""
        try:
            result = await self._count_by_criteria_impl(criteria)
            self._record_operation("query", success=True)
            return result
        except Exception as e:
            self._record_operation("query", success=False)
            logger.error(f"Failed to count {self.entity_type} by criteria: {e}")
            raise

    async def exists(self, entity_id: ID) -> bool:
        """Check if entity exists with monitoring."""
        try:
            result = await self._exists_impl(entity_id)
            self._record_operation("query", success=True)
            return result
        except Exception as e:
            self._record_operation("query", success=False)
            logger.error(
                f"Failed to check existence of {self.entity_type} with ID {entity_id}: {e}"
            )
            raise

    @abstractmethod
    async def _get_by_id_impl(self, entity_id: ID) -> Optional[T]:
        """Implementation-specific get by ID."""
        pass

    @abstractmethod
    async def _save_impl(self, entity: T) -> T:
        """Implementation-specific save."""
        pass

    @abstractmethod
    async def _delete_impl(self, entity_id: ID) -> bool:
        """Implementation-specific delete."""
        pass

    @abstractmethod
    async def _find_by_criteria_impl(self, criteria: DomainCriteria) -> List[T]:
        """Implementation-specific find by criteria."""
        pass

    @abstractmethod
    async def _count_by_criteria_impl(self, criteria: DomainCriteria) -> int:
        """Implementation-specific count by criteria."""
        pass

    @abstractmethod
    async def _exists_impl(self, entity_id: ID) -> bool:
        """Implementation-specific exists check."""
        pass

    async def get_module_status(self) -> "ModuleHealth":
        """Get repository health status."""
        from ..core.health import ModuleHealth

        validation_result = self.validate_repository_constraints()
        domain_result = self.validate_domain_invariants()
        validation_result.merge(domain_result)
        try:
            await self._perform_health_check()
            self._connection_healthy = True
        except Exception as e:
            self._connection_healthy = False
            validation_result.add_error(
                f"Repository health check failed: {str(e)}",
                code="REPO_004",
                component=self.__class__.__name__,
            )
        status = (
            ModuleStatus.AVAILABLE
            if validation_result.is_valid
            else ModuleStatus.DEGRADED
        )
        message = f"Repository for {self.entity_type}"
        if not validation_result.is_valid:
            message += f" - {len(validation_result.errors)} validation errors"
        return ModuleHealth(
            status=status,
            message=message,
            capabilities=await self.get_module_capabilities(),
            domain_health=await self.get_domain_health(),
        )

    async def get_module_capabilities(self) -> List[ModuleCapability]:
        """Get repository capabilities."""
        capabilities = []
        for capability_name in self.get_repository_capabilities():
            capabilities.append(
                ModuleCapability(
                    name=capability_name,
                    description=f"Repository capability: {capability_name}",
                    available=await self.is_healthy(),
                    version="1.0.0",
                    metadata={
                        "entity_type": self.entity_type,
                        "domain_context": self.domain_context,
                    },
                )
            )
        return capabilities

    async def is_healthy(self) -> bool:
        """Check if repository is healthy."""
        try:
            repo_result = self.validate_repository_constraints()
            if not repo_result.is_valid:
                return False
            domain_result = self.validate_domain_invariants()
            if not domain_result.is_valid:
                return False
            await self._perform_health_check()
            return True
        except Exception as e:
            logger.error(f"Health check failed for repository {self.entity_type}: {e}")
            return False

    async def get_health_indicators(self) -> Dict[str, Any]:
        """Get detailed health indicators."""
        repo_validation = self.validate_repository_constraints()
        domain_validation = self.validate_domain_invariants()
        total_operations = self._query_count + self._save_count + self._delete_count
        success_rate = (
            (total_operations - self._error_count) / max(total_operations, 1) * 100
            if total_operations > 0
            else 100.0
        )
        return {
            "entity_type": self.entity_type,
            "repository_type": self.__class__.__name__,
            "domain_context": self.domain_context,
            "connection_healthy": self._connection_healthy,
            "repository_valid": repo_validation.is_valid,
            "domain_valid": domain_validation.is_valid,
            "total_operations": total_operations,
            "query_count": self._query_count,
            "save_count": self._save_count,
            "delete_count": self._delete_count,
            "error_count": self._error_count,
            "success_rate": success_rate,
            "last_operation": (
                self._last_operation_time.isoformat()
                if self._last_operation_time
                else None
            ),
            "validation_errors": len(repo_validation.errors)
            + len(domain_validation.errors),
            "validation_warnings": len(repo_validation.warnings)
            + len(domain_validation.warnings),
            "capabilities": self.get_repository_capabilities(),
        }


class InMemoryRepository(RepositoryRM[T, ID]):
    """
    In-memory repository implementation for testing and prototyping.

    Provides a simple in-memory implementation of the repository pattern
    suitable for testing, prototyping, and development scenarios.

    Note:
        This implementation is not suitable for production use as data
        is not persisted and will be lost when the application restarts.
    """

    def __init__(
        self, domain_context: str, entity_type: str, module_id: Optional[str] = None
    ):
        """
        Initialize in-memory repository.

        Args:
            domain_context: The bounded context this repository operates within
            entity_type: Type of entity this repository manages
            module_id: Optional RM module identifier
        """
        super().__init__(domain_context, entity_type, module_id)
        self._storage: Dict[ID, T] = {}
        logger.info(f"InMemoryRepository initialized for {entity_type}")

    async def _perform_health_check(self):
        """Perform health check for in-memory repository."""
        pass

    async def _get_by_id_impl(self, entity_id: ID) -> Optional[T]:
        """Get entity by ID from memory."""
        return self._storage.get(entity_id)

    async def _save_impl(self, entity: T) -> T:
        """Save entity to memory."""
        if hasattr(entity, "id"):
            self._storage[entity.id] = entity
        else:
            raise DomainException(
                f"Entity {type(entity).__name__} must have an 'id' attribute",
                error_code="ENTITY_NO_ID",
            )
        return entity

    async def _delete_impl(self, entity_id: ID) -> bool:
        """Delete entity from memory."""
        if entity_id in self._storage:
            del self._storage[entity_id]
            return True
        return False

    async def _find_by_criteria_impl(self, criteria: DomainCriteria) -> List[T]:
        """Find entities by criteria in memory."""
        all_entities = list(self._storage.values())
        if criteria.filters:
            filtered_entities = []
            for entity in all_entities:
                matches = True
                for field, value in criteria.filters.items():
                    if hasattr(entity, field) and getattr(entity, field) != value:
                        matches = False
                        break
                if matches:
                    filtered_entities.append(entity)
            all_entities = filtered_entities
        if criteria.pagination:
            offset = criteria.pagination.get("offset", 0)
            limit = criteria.pagination.get("limit", len(all_entities))
            all_entities = all_entities[offset : offset + limit]
        return all_entities

    async def _count_by_criteria_impl(self, criteria: DomainCriteria) -> int:
        """Count entities by criteria in memory."""
        entities = await self._find_by_criteria_impl(criteria)
        return len(entities)

    async def _exists_impl(self, entity_id: ID) -> bool:
        """Check if entity exists in memory."""
        return entity_id in self._storage

    def get_storage_info(self) -> Dict[str, Any]:
        """Get information about the in-memory storage."""
        return {
            "total_entities": len(self._storage),
            "entity_ids": list(self._storage.keys()),
            "storage_type": "in_memory",
        }


def create_repository(
    repository_class: type, domain_context: str, entity_type: str, **kwargs
) -> RepositoryRM:
    """
    Create a repository instance with validation.

    Args:
        repository_class: The repository class to instantiate
        domain_context: The bounded context for the repository
        entity_type: Type of entity the repository manages
        **kwargs: Additional arguments for repository initialization

    Returns:
        Repository instance

    Raises:
        DomainException: If the repository cannot be created or is invalid
    """
    if not issubclass(repository_class, RepositoryRM):
        raise DomainException(
            f"Repository class {repository_class.__name__} must inherit from RepositoryRM",
            error_code="INVALID_REPOSITORY_CLASS",
        )
    try:
        repository = repository_class(domain_context, entity_type, **kwargs)
        validation_result = repository.validate_repository_constraints()
        if not validation_result.is_valid:
            raise DomainException(
                f"Repository validation failed: {validation_result.errors}",
                error_code="REPOSITORY_VALIDATION_FAILED",
                context={"validation_errors": validation_result.errors},
            )
        return repository
    except Exception as e:
        logger.error(f"Failed to create repository for {entity_type}: {e}")
        raise DomainException(
            f"Failed to create repository: {str(e)}",
            error_code="REPOSITORY_CREATION_FAILED",
        ) from e


def __init__(
    self, domain_context: str, entity_type: str, module_id: Optional[str] = None
):
    """
    Initialize RM-compliant repository.

    Args:
        domain_context: The bounded context this repository operates within
        entity_type: Type of entity this repository manages
        module_id: Optional RM module identifier
    """
    self.entity_type = entity_type
    self._query_count = 0
    self._save_count = 0
    self._delete_count = 0
    self._error_count = 0
    self._last_operation_time: Optional[datetime] = None
    self._connection_healthy = True
    super().__init__(domain_context, module_id)
    logger.info(f"RepositoryRM initialized: {entity_type} in context: {domain_context}")


def _record_operation(self, operation_type: str, success: bool = True):
    """
    Record repository operation for monitoring.

    Args:
        operation_type: Type of operation (query, save, delete)
        success: Whether the operation was successful
    """
    self._last_operation_time = datetime.now()
    if operation_type == "query":
        self._query_count += 1
    elif operation_type == "save":
        self._save_count += 1
    elif operation_type == "delete":
        self._delete_count += 1
    if not success:
        self._error_count += 1
    logger.debug(
        f"Repository operation recorded: {operation_type} for {self.entity_type}"
    )


def get_repository_capabilities(self) -> List[str]:
    """
    Get repository-specific capabilities.

    Returns:
        List of capability names provided by this repository
    """
    return [
        f"{self.entity_type.lower()}_read",
        f"{self.entity_type.lower()}_write",
        f"{self.entity_type.lower()}_delete",
        f"{self.entity_type.lower()}_query",
    ]


def get_repository_info(self) -> Dict[str, Any]:
    """Get comprehensive repository information."""
    return {
        "entity_type": self.entity_type,
        "repository_type": self.__class__.__name__,
        "domain_context": self.domain_context,
        "module_id": self.module_id,
        "query_count": self._query_count,
        "save_count": self._save_count,
        "delete_count": self._delete_count,
        "error_count": self._error_count,
        "last_operation": (
            self._last_operation_time.isoformat() if self._last_operation_time else None
        ),
        "connection_healthy": self._connection_healthy,
        "capabilities": self.get_repository_capabilities(),
    }


def __init__(
    self, domain_context: str, entity_type: str, module_id: Optional[str] = None
):
    """
    Initialize in-memory repository.

    Args:
        domain_context: The bounded context this repository operates within
        entity_type: Type of entity this repository manages
        module_id: Optional RM module identifier
    """
    super().__init__(domain_context, entity_type, module_id)
    self._storage: Dict[ID, T] = {}
    logger.info(f"InMemoryRepository initialized for {entity_type}")


def get_storage_info(self) -> Dict[str, Any]:
    """Get information about the in-memory storage."""
    return {
        "total_entities": len(self._storage),
        "entity_ids": list(self._storage.keys()),
        "storage_type": "in_memory",
    }
