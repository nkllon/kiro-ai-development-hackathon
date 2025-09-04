"""
Domain Registry Manager

This module provides the core domain registry management functionality,
including loading, parsing, and managing the project_model_registry.json file.
"""

import json
import time
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime

from .base import CachedComponent
from .interfaces import DomainRegistryInterface
from .models import (
    Domain, DomainTools, DomainMetadata, PackagePotential,
    DomainCollection, ValidationResult, DependencyGraph
)
from .exceptions import (
    DomainRegistryError, DomainNotFoundError, DomainValidationError,
    RegistryCorruptionError
)
from .config import get_config


class DomainRegistryManager(CachedComponent, DomainRegistryInterface):
    """
    Enhanced manager for the project domain registry
    
    Provides comprehensive domain management including:
    - JSON registry loading and parsing
    - Domain retrieval with caching
    - Validation and consistency checking
    - Dependency graph analysis
    """
    
    def __init__(self, registry_path: Optional[str] = None, config: Optional[Dict[str, Any]] = None):
        super().__init__("domain_registry_manager", config)
        
        # Configuration
        self.config_obj = get_config()
        self.registry_path = Path(registry_path or self.config_obj.get("registry_path"))
        self.backup_dir = Path(self.config_obj.get("registry_backup_dir"))
        
        # Registry data
        self._raw_registry_data = {}
        self._domains = {}
        self._registry_loaded = False
        self._last_load_time = None
        self._registry_version = None
        
        # Statistics
        self.load_count = 0
        self.validation_count = 0
        
        self.logger.info(f"Initialized DomainRegistryManager with registry: {self.registry_path}")
    
    def load_registry(self) -> bool:
        """Load the domain registry from JSON file"""
        with self._time_operation("load_registry"):
            try:
                if not self.registry_path.exists():
                    raise DomainRegistryError(f"Registry file not found: {self.registry_path}")
                
                # Load raw JSON data
                with open(self.registry_path, 'r', encoding='utf-8') as f:
                    self._raw_registry_data = json.load(f)
                
                # Parse domains from registry
                self._parse_domains()
                
                # Update metadata
                self._registry_loaded = True
                self._last_load_time = datetime.now()
                self.load_count += 1
                
                # Clear cache since we have new data
                self._clear_cache()
                
                self.logger.info(f"Successfully loaded {len(self._domains)} domains from registry")
                return True
                
            except json.JSONDecodeError as e:
                error_msg = f"Invalid JSON in registry file: {e}"
                self.logger.error(error_msg)
                raise RegistryCorruptionError(str(self.registry_path), error_msg)
            
            except Exception as e:
                self._handle_error(e, "load_registry")
                return False
    
    def _parse_domains(self) -> None:
        """Parse domains from raw registry data"""
        self._domains = {}
        
        # Get domain architecture section
        domain_arch = self._raw_registry_data.get("domain_architecture", {})
        
        # Parse each domain category
        for category_name, category_data in domain_arch.items():
            if category_name == "overview":
                continue
                
            if isinstance(category_data, dict) and "domains" in category_data:
                for domain_name in category_data["domains"]:
                    domain = self._create_domain_from_registry(domain_name, category_name, category_data)
                    if domain:
                        self._domains[domain_name] = domain
    
    def _create_domain_from_registry(self, domain_name: str, category: str, category_data: Dict) -> Optional[Domain]:
        """Create a Domain object from registry data"""
        try:
            # Create basic domain tools (will be enhanced later)
            tools = DomainTools(
                linter="pylint",
                formatter="black",
                validator="mypy",
                exclusions=["__pycache__", "*.pyc"]
            )
            
            # Create package potential assessment
            package_potential = PackagePotential(
                score=0.5,  # Default score, will be calculated later
                reasons=["Domain identified in registry"],
                dependencies=[],
                estimated_effort="medium",
                blockers=[]
            )
            
            # Create domain metadata
            metadata = DomainMetadata(
                demo_role=category,
                extraction_candidate="unknown",
                package_potential=package_potential,
                status="active",
                tags=[category],
                last_updated=datetime.now()
            )
            
            # Create domain with basic information
            domain = Domain(
                name=domain_name,
                description=category_data.get("description", f"Domain in {category} category"),
                patterns=[f"src/**/{domain_name}/**/*.py"],  # Default pattern
                content_indicators=[domain_name.replace("_", ""), domain_name.replace("-", "")],
                requirements=[],  # Will be populated later
                dependencies=[],  # Will be analyzed later
                tools=tools,
                metadata=metadata
            )
            
            return domain
            
        except Exception as e:
            self.logger.warning(f"Failed to create domain {domain_name}: {e}")
            return None
    
    def get_domain(self, domain_name: str) -> Optional[Domain]:
        """Retrieve a specific domain by name"""
        # Check cache first
        cached_domain = self._get_from_cache(f"domain_{domain_name}")
        if cached_domain:
            return cached_domain
        
        with self._time_operation("get_domain"):
            # Ensure registry is loaded
            if not self._registry_loaded:
                self.load_registry()
            
            domain = self._domains.get(domain_name)
            if not domain:
                raise DomainNotFoundError(domain_name)
            
            # Cache the result
            self._set_in_cache(f"domain_{domain_name}", domain)
            
            return domain
    
    def get_all_domains(self) -> DomainCollection:
        """Retrieve all domains"""
        # Check cache first
        cached_domains = self._get_from_cache("all_domains")
        if cached_domains:
            return cached_domains
        
        with self._time_operation("get_all_domains"):
            # Ensure registry is loaded
            if not self._registry_loaded:
                self.load_registry()
            
            # Cache the result
            self._set_in_cache("all_domains", self._domains.copy())
            
            return self._domains.copy()
    
    def search_domains(self, query: str, filters: Optional[Dict[str, Any]] = None) -> List[Domain]:
        """Search domains with optional filters"""
        with self._time_operation("search_domains"):
            all_domains = self.get_all_domains()
            results = []
            
            query_lower = query.lower()
            
            for domain in all_domains.values():
                # Basic text search
                if (query_lower in domain.name.lower() or 
                    query_lower in domain.description.lower() or
                    any(query_lower in pattern.lower() for pattern in domain.patterns)):
                    
                    # Apply filters if provided
                    if filters:
                        if not self._apply_filters(domain, filters):
                            continue
                    
                    results.append(domain)
            
            return results
    
    def _apply_filters(self, domain: Domain, filters: Dict[str, Any]) -> bool:
        """Apply filters to a domain"""
        for filter_key, filter_value in filters.items():
            if filter_key == "category":
                if domain.metadata.demo_role != filter_value:
                    return False
            elif filter_key == "status":
                if domain.metadata.status != filter_value:
                    return False
            elif filter_key == "has_pattern":
                if not any(filter_value in pattern for pattern in domain.patterns):
                    return False
        
        return True
    
    def get_dependencies(self, domain_name: str) -> DependencyGraph:
        """Get dependency graph for a domain"""
        with self._time_operation("get_dependencies"):
            domain = self.get_domain(domain_name)
            
            # For now, create a basic dependency graph
            # This will be enhanced when we have actual dependency analysis
            return DependencyGraph(
                domain=domain_name,
                direct_dependencies=domain.dependencies,
                transitive_dependencies=[],  # Will be calculated later
                dependents=[],  # Will be calculated later
                circular_dependencies=[],  # Will be detected later
                dependency_depth=len(domain.dependencies),
                coupling_score=0.5  # Will be calculated later
            )
    
    def validate_domain(self, domain: Domain) -> ValidationResult:
        """Validate domain structure and requirements"""
        with self._time_operation("validate_domain"):
            self.validation_count += 1
            
            errors = []
            warnings = []
            suggestions = []
            
            # Basic validation
            if not domain.name:
                errors.append("Domain name is required")
            
            if not domain.description:
                warnings.append("Domain description is empty")
            
            if not domain.patterns:
                errors.append("Domain must have at least one file pattern")
            
            # Pattern validation
            for pattern in domain.patterns:
                if not isinstance(pattern, str):
                    errors.append(f"Invalid pattern type: {type(pattern)}")
                elif not pattern.strip():
                    errors.append("Empty pattern found")
            
            # Dependency validation (basic)
            for dep in domain.dependencies:
                if dep not in self._domains:
                    warnings.append(f"Dependency '{dep}' not found in registry")
            
            # Suggestions
            if len(domain.patterns) == 1 and "**" not in domain.patterns[0]:
                suggestions.append("Consider using recursive patterns (**) for better coverage")
            
            if not domain.content_indicators:
                suggestions.append("Adding content indicators can improve domain detection")
            
            return ValidationResult(
                is_valid=len(errors) == 0,
                errors=errors,
                warnings=warnings,
                suggestions=suggestions,
                validation_time_ms=0.0  # Will be set by timing decorator
            )
    
    def update_domain(self, domain: Domain) -> bool:
        """Update a domain in the registry"""
        with self._time_operation("update_domain"):
            try:
                # Validate domain first
                validation = self.validate_domain(domain)
                if not validation.is_valid:
                    raise DomainValidationError(domain.name, validation.errors)
                
                # Update in memory
                self._domains[domain.name] = domain
                
                # Clear relevant cache entries
                self._remove_from_cache(f"domain_{domain.name}")
                self._remove_from_cache("all_domains")
                
                self.logger.info(f"Updated domain: {domain.name}")
                return True
                
            except Exception as e:
                self._handle_error(e, "update_domain")
                return False
    
    def create_domain(self, domain: Domain) -> bool:
        """Create a new domain in the registry"""
        with self._time_operation("create_domain"):
            try:
                # Check if domain already exists
                if domain.name in self._domains:
                    raise DomainRegistryError(f"Domain '{domain.name}' already exists")
                
                # Validate domain
                validation = self.validate_domain(domain)
                if not validation.is_valid:
                    raise DomainValidationError(domain.name, validation.errors)
                
                # Add to registry
                self._domains[domain.name] = domain
                
                # Clear cache
                self._remove_from_cache("all_domains")
                
                self.logger.info(f"Created new domain: {domain.name}")
                return True
                
            except Exception as e:
                self._handle_error(e, "create_domain")
                return False
    
    def delete_domain(self, domain_name: str) -> bool:
        """Delete a domain from the registry"""
        with self._time_operation("delete_domain"):
            try:
                if domain_name not in self._domains:
                    raise DomainNotFoundError(domain_name)
                
                # Remove from registry
                del self._domains[domain_name]
                
                # Clear cache
                self._remove_from_cache(f"domain_{domain_name}")
                self._remove_from_cache("all_domains")
                
                self.logger.info(f"Deleted domain: {domain_name}")
                return True
                
            except Exception as e:
                self._handle_error(e, "delete_domain")
                return False
    
    def get_registry_stats(self) -> Dict[str, Any]:
        """Get registry statistics"""
        return {
            "total_domains": len(self._domains),
            "registry_loaded": self._registry_loaded,
            "last_load_time": self._last_load_time.isoformat() if self._last_load_time else None,
            "load_count": self.load_count,
            "validation_count": self.validation_count,
            "registry_path": str(self.registry_path),
            "cache_stats": self.get_cache_stats()
        }
    
    def reload_registry(self) -> bool:
        """Reload registry from file"""
        self.logger.info("Reloading domain registry")
        self._registry_loaded = False
        self._clear_cache()
        return self.load_registry()