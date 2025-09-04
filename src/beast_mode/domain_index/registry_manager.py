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
from .domain_cache import DomainCache, DomainSpecificCache
from .domain_index import DomainIndex
from .domain_validator import DomainValidator


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
        
        # Initialize caching, indexing, and validation systems
        cache_config = self.config.get('cache', {})
        index_config = self.config.get('index', {})
        validator_config = self.config.get('validator', {})
        
        self._cache = DomainCache(cache_config)
        self._domain_cache = DomainSpecificCache(self._cache)
        self._index = DomainIndex(index_config)
        self._validator = DomainValidator(validator_config)
        
        # Statistics
        self.load_count = 0
        self.validation_count = 0
        
        self.logger.info(f"Initialized DomainRegistryManager with registry: {self.registry_path}")
        self.logger.info("Initialized caching, indexing, and validation systems")
    
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
                
                # Rebuild index with new data
                self._index.build_index(self._domains)
                
                # Warm cache with frequently accessed domains
                self._warm_cache()
                
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
        # Check domain-specific cache first
        cached_domain = self._domain_cache.get_domain(domain_name)
        if cached_domain:
            return cached_domain
        
        with self._time_operation("get_domain"):
            # Ensure registry is loaded
            if not self._registry_loaded:
                self.load_registry()
            
            domain = self._domains.get(domain_name)
            if not domain:
                raise DomainNotFoundError(domain_name)
            
            # Cache the result using domain-specific cache
            self._domain_cache.cache_domain(domain)
            
            return domain
    
    def get_all_domains(self) -> DomainCollection:
        """Retrieve all domains"""
        # Check domain-specific cache first
        cached_domains = self._domain_cache.get_domain_collection()
        if cached_domains:
            return cached_domains
        
        with self._time_operation("get_all_domains"):
            # Ensure registry is loaded
            if not self._registry_loaded:
                self.load_registry()
            
            # Cache the result using domain-specific cache
            self._domain_cache.cache_domain_collection(self._domains.copy())
            
            return self._domains.copy()
    
    def search_domains(self, query: str, filters: Optional[Dict[str, Any]] = None) -> List[Domain]:
        """Search domains with optional filters using the index"""
        with self._time_operation("search_domains"):
            # Use index for efficient searching
            domain_names = self._index.search_index(query, filters)
            
            # Convert domain names to domain objects
            results = []
            for domain_name in domain_names:
                try:
                    domain = self.get_domain(domain_name)
                    if domain:
                        results.append(domain)
                except DomainNotFoundError:
                    # Domain might have been removed, skip it
                    continue
            
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
        """Validate domain structure and requirements using comprehensive validator"""
        with self._time_operation("validate_domain"):
            self.validation_count += 1
            
            # Use the comprehensive validator
            context = {'all_domains': self._domains}
            return self._validator.validate_domain(domain, context)
    
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
                
                # Update index
                self._index.update_index(domain)
                
                # Invalidate cache entries
                self._domain_cache.invalidate_domain(domain.name)
                
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
                
                # Update index
                self._index.update_index(domain)
                
                # Invalidate cache
                self._domain_cache.invalidate_domain(domain.name)
                
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
                
                # Update index (remove domain)
                self._index.update_index(Domain(
                    name=domain_name, description="", patterns=[], content_indicators=[],
                    requirements=[], dependencies=[], tools=DomainTools("", "", ""),
                    metadata=DomainMetadata("", "", PackagePotential(0.0, [], [], "", []))
                ))
                
                # Invalidate cache
                self._domain_cache.invalidate_domain(domain_name)
                
                self.logger.info(f"Deleted domain: {domain_name}")
                return True
                
            except Exception as e:
                self._handle_error(e, "delete_domain")
                return False
    
    def get_registry_stats(self) -> Dict[str, Any]:
        """Get comprehensive registry statistics"""
        return {
            "total_domains": len(self._domains),
            "registry_loaded": self._registry_loaded,
            "last_load_time": self._last_load_time.isoformat() if self._last_load_time else None,
            "load_count": self.load_count,
            "validation_count": self.validation_count,
            "registry_path": str(self.registry_path),
            "cache_stats": self._cache.get_stats(),
            "index_stats": self._index.get_index_stats(),
            "validation_stats": self._validator.get_validation_stats(),
            "component_health": self.get_health_indicators()
        }
    
    def reload_registry(self) -> bool:
        """Reload registry from file"""
        self.logger.info("Reloading domain registry")
        self._registry_loaded = False
        self._clear_cache()
        return self.load_registry()
    
    def _warm_cache(self) -> None:
        """Warm cache with frequently accessed domains"""
        try:
            # Get list of domain names to warm
            domain_names = list(self._domains.keys())
            
            # Warm cache with domain loader function
            def domain_loader(domain_name: str) -> Optional[Domain]:
                return self._domains.get(domain_name)
            
            # Warm the most commonly accessed domains first
            priority_domains = domain_names[:20]  # Top 20 domains
            warmed_count = self._domain_cache.warm_domains(domain_loader, priority_domains)
            
            self.logger.debug(f"Warmed cache with {warmed_count} domains")
            
        except Exception as e:
            self.logger.warning(f"Failed to warm cache: {e}")
    
    def get_search_suggestions(self, partial_query: str) -> List[str]:
        """Get search query suggestions"""
        return self._index.suggest_completions(partial_query)
    
    def search_by_pattern(self, pattern: str) -> List[Domain]:
        """Search domains by file pattern"""
        domain_names = self._index.search_by_pattern(pattern)
        return [self.get_domain(name) for name in domain_names if name in self._domains]
    
    def search_by_category(self, category: str) -> List[Domain]:
        """Search domains by category"""
        domain_names = self._index.search_by_category(category)
        return [self.get_domain(name) for name in domain_names if name in self._domains]
    
    def get_domain_relationships(self, domain_name: str) -> Dict[str, List[str]]:
        """Get domain relationships from index"""
        return self._index.get_domain_relationships(domain_name)
    
    def invalidate_cache_by_category(self, category: str) -> int:
        """Invalidate all cached domains in a category"""
        return self._domain_cache.invalidate_by_category(category)
    
    def get_cache_info(self, key: str) -> Optional[Dict[str, Any]]:
        """Get detailed cache information for a key"""
        return self._cache.get_entry_info(key)
    
    def validate_all_domains(self) -> Dict[str, ValidationResult]:
        """Validate all domains in the registry"""
        with self._time_operation("validate_all_domains"):
            return self._validator.validate_domain_collection(self._domains)
    
    def check_domain_consistency(self) -> List[Any]:
        """Check cross-domain consistency"""
        with self._time_operation("check_domain_consistency"):
            return self._validator.check_consistency(self._domains)
    
    def detect_circular_dependencies(self) -> List[List[str]]:
        """Detect circular dependencies between domains"""
        return self._validator.detect_circular_dependencies(self._domains)
    
    def validate_domain_dependencies(self) -> List[Any]:
        """Validate all domain dependencies"""
        return self._validator.validate_dependencies(self._domains)
    
    def get_validation_stats(self) -> Dict[str, Any]:
        """Get validation statistics"""
        return self._validator.get_validation_stats()
    
    def add_validation_rule(self, rule) -> None:
        """Add custom validation rule"""
        self._validator.add_validation_rule(rule)
    
    def add_consistency_check(self, check) -> None:
        """Add custom consistency check"""
        self._validator.add_consistency_check(check)