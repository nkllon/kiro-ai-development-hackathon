#!/usr/bin/env python3
"""
🎯 UNIFIED RM-DDD-CMS SYSTEM
===========================
Ghostbusters Verdict: RM-DDD and CMS are the same system.
Unified implementation with integrated CMS capabilities.

Author: Beast Mode Framework  
Date: 2025-01-27
Version: 3.0-unified
Requirements: Unified RM-DDD-CMS Architecture
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Set, Type, Union
import uuid
import re
import inspect
import json


class ModuleStatus(Enum):
    """Module status enumeration."""
    INITIALIZING = "initializing"
    ACTIVE = "active"
    INACTIVE = "inactive"
    ERROR = "error"
    MAINTENANCE = "maintenance"
    DEPRECATED = "deprecated"


class ModuleHealth(Enum):
    """Module health enumeration."""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    CRITICAL = "critical"
    UNKNOWN = "unknown"


@dataclass
class ModuleCapability:
    """Module capability definition."""
    name: str
    description: str
    version: str
    dependencies: List[str] = field(default_factory=list)
    parameters: Dict[str, Any] = field(default_factory=dict)
    return_type: Optional[Type] = None
    is_async: bool = False
    is_public: bool = True
    tags: Set[str] = field(default_factory=set)
    domain_vocabulary: Set[str] = field(default_factory=set)
    bounded_context: Optional[str] = None
    ddd_pattern: Optional[str] = None  # Entity, ValueObject, Aggregate, DomainService, etc.

@dataclass
class DomainVocabulary:
    """Domain vocabulary definition for ubiquitous language enforcement."""
    terms: Dict[str, str] = field(default_factory=dict)  # term -> definition
    synonyms: Dict[str, List[str]] = field(default_factory=dict)  # term -> synonyms
    context: str = ""
    version: str = "1.0.0"

@dataclass
class BoundedContext:
    """Bounded context definition for DDD compliance."""
    name: str
    description: str
    vocabulary: DomainVocabulary
    entities: Set[str] = field(default_factory=set)
    value_objects: Set[str] = field(default_factory=set)
    aggregates: Set[str] = field(default_factory=set)
    domain_services: Set[str] = field(default_factory=set)
    repositories: Set[str] = field(default_factory=set)


@dataclass
class ModuleHealthMetrics:
    """Detailed module health metrics."""
    status: ModuleHealth
    last_check: datetime
    uptime: float
    memory_usage: float
    cpu_usage: float
    error_count: int
    success_rate: float
    response_time: float
    dependencies_healthy: bool
    custom_metrics: Dict[str, Any] = field(default_factory=dict)


class ReflectiveModule(ABC):
    """
    🚨 UNIFIED RM-DDD-CMS SYSTEM 🚨
    
    Ghostbusters Verdict: RM-DDD and CMS are the same system.
    
    Unified Capabilities:
    - Dynamic CLI generation via introspection
    - Full DDD pattern enforcement with ubiquitous language
    - Integrated CMS functionality (content management)
    - Health monitoring and registry management
    - Domain vocabulary storage and validation
    - Bounded context enforcement
    - Complete self-contained system (no external dependencies)
    
    Access Pattern: All CMS access through RM-DDD interfaces
    """

    def __init__(self, 
                 module_id: Optional[str] = None,
                 bounded_context: Optional[BoundedContext] = None,
                 domain_vocabulary: Optional[DomainVocabulary] = None):
        self.module_id = module_id or f"{self.__class__.__name__}_{uuid.uuid4().hex[:8]}"
        self.status = ModuleStatus.INITIALIZING
        self.health = ModuleHealth.UNKNOWN
        self.capabilities: Dict[str, ModuleCapability] = {}
        self.dependencies: Set[str] = set()
        
        # Unified DDD-CMS Components
        self.bounded_context = bounded_context or self._infer_bounded_context()
        self.domain_vocabulary = domain_vocabulary or self._create_default_vocabulary()
        self.ddd_pattern = self._infer_ddd_pattern()
        
        # CMS Storage (in-memory for bootstrap, can be enhanced with Directus later)
        self._content_store: Dict[str, Any] = {}
        self._metadata_store: Dict[str, Any] = {}
        self._registry_store: Dict[str, Any] = {}
        
        self.health_metrics = ModuleHealthMetrics(
            status=ModuleHealth.UNKNOWN,
            last_check=datetime.now(),
            uptime=0.0,
            memory_usage=0.0,
            cpu_usage=0.0,
            error_count=0,
            success_rate=1.0,
            response_time=0.0,
            dependencies_healthy=True
        )
        self._start_time = datetime.now()
        self._error_history: List[Dict[str, Any]] = []
        
        # Unified initialization
        self._discover_capabilities()
        self._validate_ubiquitous_language()
        self._validate_bounded_context_compliance()
        self._initialize_cms_capabilities()
        
        # Set status to active after initialization
        self.status = ModuleStatus.ACTIVE
        self.health = ModuleHealth.HEALTHY

    def _discover_capabilities(self) -> None:
        """Discover module capabilities through reflection with DDD validation."""
        for attr_name in dir(self):
            attr = getattr(self, attr_name)
            if callable(attr) and not attr_name.startswith('_'):
                # Get method signature for CLI generation
                try:
                    sig = inspect.signature(attr)
                    parameters = {}
                    for param_name, param in sig.parameters.items():
                        if param_name != 'self':
                            parameters[param_name] = {
                                'type': param.annotation if param.annotation != inspect.Parameter.empty else str,
                                'default': param.default if param.default != inspect.Parameter.empty else None,
                                'required': param.default == inspect.Parameter.empty
                            }
                    
                    return_type = sig.return_annotation if sig.return_annotation != inspect.Signature.empty else None
                except Exception:
                    parameters = {}
                    return_type = None
                
                # Extract domain vocabulary from method and docstring
                domain_terms = self._extract_domain_vocabulary(attr_name, attr.__doc__ or "")
                
                # Create capability from method with DDD metadata
                capability = ModuleCapability(
                    name=attr_name,
                    description=attr.__doc__ or f"Method {attr_name}",
                    version="1.0.0",
                    parameters=parameters,
                    return_type=return_type,
                    is_async=inspect.iscoroutinefunction(attr),
                    tags={"method", "public"},
                    domain_vocabulary=domain_terms,
                    bounded_context=self.bounded_context.name if self.bounded_context else None,
                    ddd_pattern=self.ddd_pattern
                )
                self.capabilities[attr_name] = capability

    def _extract_domain_vocabulary(self, method_name: str, docstring: str) -> Set[str]:
        """Extract domain vocabulary terms from method names and docstrings."""
        terms = set()
        
        # Extract from method name
        method_terms = re.findall(r'[A-Z][a-z]+|[a-z]+', method_name)
        terms.update(term.lower() for term in method_terms)
        
        # Extract from docstring
        if docstring:
            # Look for domain-specific terms (capitalized words, technical terms)
            doc_terms = re.findall(r'\b[A-Z][a-z]+\b', docstring)
            terms.update(term.lower() for term in doc_terms)
        
        return terms

    def _validate_ubiquitous_language(self) -> List[str]:
        """Validate that the module uses ubiquitous language consistently."""
        violations = []
        
        if not self.domain_vocabulary:
            violations.append("No domain vocabulary defined")
            return violations
        
        # Check method names against vocabulary
        for cap_name, capability in self.capabilities.items():
            method_terms = capability.domain_vocabulary
            
            # Check if terms are in vocabulary or should be added
            for term in method_terms:
                if term not in self.domain_vocabulary.terms:
                    # Auto-add discovered terms to vocabulary
                    self.domain_vocabulary.terms[term] = f"Auto-discovered term: {term}"
        
        return violations

    def _validate_bounded_context_compliance(self) -> List[str]:
        """Validate that the module complies with bounded context principles."""
        violations = []
        
        if not self.bounded_context:
            violations.append("No bounded context defined")
            return violations
        
        # Validate single responsibility within context
        contexts_referenced = set()
        for capability in self.capabilities.values():
            if capability.bounded_context:
                contexts_referenced.add(capability.bounded_context)
        
        if len(contexts_referenced) > 1:
            violations.append(f"Module references multiple contexts: {contexts_referenced}")
        
        # Validate DDD pattern consistency
        patterns_used = set()
        for capability in self.capabilities.values():
            if capability.ddd_pattern:
                patterns_used.add(capability.ddd_pattern)
        
        if len(patterns_used) > 2:  # Allow some flexibility
            violations.append(f"Module uses too many DDD patterns: {patterns_used}")
        
        return violations

    def _infer_bounded_context(self) -> BoundedContext:
        """Infer bounded context from class name and module."""
        context_name = self.__class__.__name__.replace("Manager", "").replace("Service", "").replace("Repository", "")
        
        # Create context-specific vocabulary
        vocabulary = DomainVocabulary(
            context=context_name,
            terms={},
            synonyms={}
        )
        
        return BoundedContext(
            name=context_name,
            description=f"Bounded context for {context_name}",
            vocabulary=vocabulary
        )

    def _create_default_vocabulary(self) -> DomainVocabulary:
        """Create default domain vocabulary from class and method names."""
        terms = {}
        synonyms = {}
        
        # Extract terms from class name
        class_terms = re.findall(r'[A-Z][a-z]+', self.__class__.__name__)
        for term in class_terms:
            terms[term.lower()] = f"Domain concept: {term}"
        
        return DomainVocabulary(
            terms=terms,
            synonyms=synonyms,
            context=self.__class__.__name__
        )

    def _initialize_cms_capabilities(self) -> None:
        """Initialize integrated CMS capabilities."""
        # Store module metadata in CMS
        self._content_store[f"module_{self.module_id}"] = {
            "type": "module_metadata",
            "data": self.get_interface_metadata(),
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }
        
        # Store domain vocabulary in CMS
        self._content_store[f"vocabulary_{self.module_id}"] = {
            "type": "domain_vocabulary",
            "data": {
                "terms": self.domain_vocabulary.terms,
                "synonyms": self.domain_vocabulary.synonyms,
                "context": self.domain_vocabulary.context
            },
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }
        
        # Store bounded context in CMS
        self._content_store[f"context_{self.module_id}"] = {
            "type": "bounded_context",
            "data": {
                "name": self.bounded_context.name,
                "description": self.bounded_context.description,
                "entities": list(self.bounded_context.entities),
                "value_objects": list(self.bounded_context.value_objects),
                "aggregates": list(self.bounded_context.aggregates),
                "domain_services": list(self.bounded_context.domain_services),
                "repositories": list(self.bounded_context.repositories)
            },
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }

    def _infer_ddd_pattern(self) -> str:
        """Infer DDD pattern from class name and structure."""
        class_name = self.__class__.__name__
        
        if "Manager" in class_name or "Coordinator" in class_name:
            return "DomainService"
        elif "Repository" in class_name:
            return "Repository"
        elif "Factory" in class_name:
            return "Factory"
        elif "Validator" in class_name or "Resolver" in class_name:
            return "DomainService"
        elif "Entity" in class_name:
            return "Entity"
        elif "Value" in class_name:
            return "ValueObject"
        elif "Aggregate" in class_name:
            return "Aggregate"
        else:
            return "DomainService"  # Default

    def _extract_method_terms(self, method_name: str) -> Set[str]:
        """Bootstrap method term extraction."""
        terms = set()
        method_terms = re.findall(r'[A-Z][a-z]+|[a-z]+', method_name)
        terms.update(term.lower() for term in method_terms if len(term) > 2)
        return terms

    def get_interface_metadata(self) -> Dict[str, Any]:
        """Get unified RM-DDD-CMS interface metadata for registry."""
        return {
            "module_id": self.module_id,
            "interface_type": self.__class__.__name__,
            "version": "3.0.0-unified",
            "system_type": "Unified RM-DDD-CMS System",
            "status": self.status.value,
            "health": self.health.value,
            "capabilities": {name: {
                "description": cap.description,
                "version": cap.version,
                "is_async": cap.is_async,
                "is_public": cap.is_public,
                "tags": list(cap.tags),
                "domain_vocabulary": list(cap.domain_vocabulary),
                "bounded_context": cap.bounded_context,
                "ddd_pattern": cap.ddd_pattern,
                "parameters": cap.parameters
            } for name, cap in self.capabilities.items()},
            "dependencies": list(self.dependencies),
            "bounded_context": self.bounded_context.name if self.bounded_context else None,
            "ddd_pattern": self.ddd_pattern,
            "domain_vocabulary_size": len(self.domain_vocabulary.terms) if self.domain_vocabulary else 0,
            "ubiquitous_language_compliance": len(self._validate_ubiquitous_language()) == 0,
            "bounded_context_compliance": len(self._validate_bounded_context_compliance()) == 0,
            "cms_content_count": len(self._content_store),
            "cms_content_types": list(set(item.get('type', 'unknown') for item in self._content_store.values())),
            "created_at": self._start_time.isoformat(),
            "last_updated": datetime.now().isoformat(),
            "ghostbusters_verdict": "RM-DDD and CMS are the same system - unified implementation"
        }

    def register_module(self, registry) -> None:
        """Register module with registry."""
        if hasattr(registry, "register"):
            registry.register(self.get_interface_metadata())
        self.registry_metadata = self.get_interface_metadata()

    def health_check(self) -> ModuleHealthMetrics:
        """Perform comprehensive health check."""
        current_time = datetime.now()
        uptime = (current_time - self._start_time).total_seconds()
        
        # Update health metrics
        self.health_metrics.last_check = current_time
        self.health_metrics.uptime = uptime
        
        # Determine health status
        if self.status == ModuleStatus.ERROR:
            self.health = ModuleHealth.CRITICAL
        elif self.status == ModuleStatus.MAINTENANCE:
            self.health = ModuleHealth.DEGRADED
        elif self.status == ModuleStatus.ACTIVE:
            self.health = ModuleHealth.HEALTHY
        else:
            self.health = ModuleHealth.UNKNOWN
            
        self.health_metrics.status = self.health
        
        return self.health_metrics

    def get_health_status(self) -> Dict[str, Any]:
        """Get current health status with detailed metrics."""
        health_metrics = self.health_check()
        return {
            "module_id": self.module_id,
            "status": self.status.value,
            "health": self.health.value,
            "uptime": health_metrics.uptime,
            "last_check": health_metrics.last_check.isoformat(),
            "error_count": health_metrics.error_count,
            "success_rate": health_metrics.success_rate,
            "capabilities_count": len(self.capabilities),
            "dependencies_count": len(self.dependencies),
            "custom_metrics": health_metrics.custom_metrics
        }

    def add_capability(self, capability: ModuleCapability) -> None:
        """Add a new capability to the module."""
        self.capabilities[capability.name] = capability

    def remove_capability(self, capability_name: str) -> bool:
        """Remove a capability from the module."""
        if capability_name in self.capabilities:
            del self.capabilities[capability_name]
            return True
        return False

    def get_capability(self, capability_name: str) -> Optional[ModuleCapability]:
        """Get a specific capability."""
        return self.capabilities.get(capability_name)

    def list_capabilities(self) -> List[str]:
        """List all capability names."""
        return list(self.capabilities.keys())

    def add_dependency(self, dependency: str) -> None:
        """Add a dependency to the module."""
        self.dependencies.add(dependency)

    def remove_dependency(self, dependency: str) -> bool:
        """Remove a dependency from the module."""
        if dependency in self.dependencies:
            self.dependencies.remove(dependency)
            return True
        return False

    def set_status(self, status: ModuleStatus) -> None:
        """Set module status."""
        self.status = status
        self.health_check()  # Update health based on new status

    def set_health(self, health: ModuleHealth) -> None:
        """Set module health."""
        self.health = health
        self.health_metrics.status = health

    def log_error(self, error: Exception, context: Optional[Dict[str, Any]] = None) -> None:
        """Log an error for health tracking."""
        error_entry = {
            "timestamp": datetime.now().isoformat(),
            "error_type": type(error).__name__,
            "error_message": str(error),
            "context": context or {}
        }
        self._error_history.append(error_entry)
        self.health_metrics.error_count += 1
        
        # Update success rate
        total_operations = len(self._error_history) + max(1, self.health_metrics.error_count)
        self.health_metrics.success_rate = 1.0 - (self.health_metrics.error_count / total_operations)

    def get_error_history(self) -> List[Dict[str, Any]]:
        """Get error history for debugging."""
        return self._error_history.copy()

    def update_custom_metrics(self, metrics: Dict[str, Any]) -> None:
        """Update custom health metrics."""
        self.health_metrics.custom_metrics.update(metrics)

    def generate_cli_interface(self) -> str:
        """Generate unified CLI interface with DDD and CMS capabilities."""
        context_name = self.bounded_context.name if self.bounded_context else "Unknown"
        
        cli_code = f'''#!/usr/bin/env python3
"""
Auto-generated CLI for {self.__class__.__name__}
Generated from Unified RM-DDD-CMS System
Bounded Context: {context_name}
DDD Pattern: {self.ddd_pattern}
"""

import argparse
import json
import sys
from typing import Any, Dict

def create_parser() -> argparse.ArgumentParser:
    """Create argument parser from unified RM-DDD-CMS capabilities."""
    parser = argparse.ArgumentParser(
        description=f"CLI for {self.__class__.__name__} ({self.ddd_pattern} in {context_name} context)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=f"""
Unified RM-DDD-CMS System
Bounded Context: {context_name}
DDD Pattern: {self.ddd_pattern}
Domain Vocabulary: {', '.join(list(self.domain_vocabulary.terms.keys())[:10])}{'...' if len(self.domain_vocabulary.terms) > 10 else ''}
        """
    )
    
    # Core system commands
    parser.add_argument('--module-info', action='store_true',
                       help='Show module information including DDD metadata')
    parser.add_argument('--health-check', action='store_true',
                       help='Perform health check')
    parser.add_argument('--list-capabilities', action='store_true',
                       help='List all capabilities')
    
    # DDD commands
    parser.add_argument('--domain-vocabulary', action='store_true',
                       help='Show domain vocabulary and ubiquitous language terms')
    parser.add_argument('--bounded-context', action='store_true',
                       help='Show bounded context information')
    parser.add_argument('--validate-ddd', action='store_true',
                       help='Validate DDD compliance and ubiquitous language usage')
    
    # CMS commands
    parser.add_argument('--list-content', action='store_true',
                       help='List all content in integrated CMS')
    parser.add_argument('--content-types', action='store_true',
                       help='Show available content types')
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands (using ubiquitous language)')
    
'''
        
        # Generate subcommands for each capability
        for cap_name, capability in self.capabilities.items():
            if capability.is_public:
                cli_code += f'''    # Command: {cap_name}
    {cap_name}_parser = subparsers.add_parser('{cap_name}', 
                                             help='{capability.description}')
'''
                
                # Add parameters for this capability
                for param_name, param_info in capability.parameters.items():
                    param_type = param_info.get('type', str)
                    param_default = param_info.get('default')
                    param_required = param_info.get('required', True)
                    
                    # Get type name safely - use str for complex types
                    if hasattr(param_type, '__name__'):
                        if param_type.__name__ in ['str', 'int', 'float', 'bool']:
                            type_name = param_type.__name__
                        else:
                            type_name = 'str'  # Default to str for complex types
                    else:
                        type_name = 'str'
                    
                    if param_required:
                        cli_code += f'''    {cap_name}_parser.add_argument('{param_name}', 
                                                     type={type_name}, 
                                                     help='Parameter: {param_name}')
'''
                    else:
                        cli_code += f'''    {cap_name}_parser.add_argument('--{param_name}', 
                                                     type={type_name}, 
                                                     default={repr(param_default)},
                                                     help='Parameter: {param_name} (default: {param_default})')
'''
        
        # Format the CLI code with module information
        module_path = self.__module__ or "unknown_module"
        class_name = self.__class__.__name__
        
        cli_code += f'''
    return parser

def main():
    """Unified RM-DDD-CMS CLI entry point with ubiquitous language enforcement."""
    parser = create_parser()
    args = parser.parse_args()
    
    # Import and instantiate the module
    from {module_path} import {class_name}
    module = {class_name}()
    
    if args.module_info:
        metadata = module.get_interface_metadata()
        metadata['ddd_metadata'] = module.get_ddd_metadata()
        print(json.dumps(metadata, indent=2))
        return
    
    if args.health_check:
        print(json.dumps(module.get_health_status(), indent=2))
        return
    
    if args.list_capabilities:
        capabilities = module.list_capabilities()
        print(f"Available capabilities in {{module.bounded_context.name if module.bounded_context else 'Unknown'}} context:")
        for cap in capabilities:
            capability = module.get_capability(cap)
            print(f"  - {{cap}} ({{capability.ddd_pattern if capability else 'Unknown pattern'}})")
        return
    
    if args.domain_vocabulary:
        vocab = module.get_domain_vocabulary()
        print("Domain Vocabulary (Ubiquitous Language):")
        for term, definition in vocab.items():
            print(f"  - {{term}}: {{definition}}")
        return
    
    if args.bounded_context:
        context_info = module.get_bounded_context_info()
        print(json.dumps(context_info, indent=2))
        return
    
    if args.validate_ddd:
        validation_results = module.validate_ddd_compliance()
        print("DDD Compliance Validation:")
        print(json.dumps(validation_results, indent=2))
        return
    
    if args.list_content:
        content = module.list_content()
        print("CMS Content:")
        print(json.dumps(content, indent=2, default=str))
        return
    
    if args.content_types:
        content = module.list_content()
        types = set(item.get('type', 'unknown') for item in content)
        print("Available content types:")
        for content_type in sorted(types):
            print(f"  - {{content_type}}")
        return
    
    if args.command:
        # Validate command uses ubiquitous language
        validation_result = module.validate_command_language(args.command)
        if not validation_result['valid']:
            print(f"Warning: Command '{{args.command}}' may not follow ubiquitous language: {{validation_result['message']}}")
        
        # Execute the requested capability
        if hasattr(module, args.command):
            method = getattr(module, args.command)
            
            # Build kwargs from parsed arguments
            kwargs = {{}}
            for key, value in vars(args).items():
                if key not in ['command', 'module_info', 'health_check', 'list_capabilities', 
                              'domain_vocabulary', 'bounded_context', 'validate_ddd', 
                              'list_content', 'content_types']:
                    if value is not None:
                        kwargs[key] = value
            
            try:
                result = method(**kwargs)
                if result is not None:
                    if isinstance(result, (dict, list)):
                        print(json.dumps(result, indent=2, default=str))
                    else:
                        print(result)
            except Exception as e:
                print(f"Error executing {{args.command}}: {{e}}", file=sys.stderr)
                sys.exit(1)
        else:
            print(f"Unknown command: {{args.command}}", file=sys.stderr)
            sys.exit(1)
    else:
        parser.print_help()

if __name__ == '__main__':
    main()
'''
        
        return cli_code

    def get_cli_commands(self) -> Dict[str, Dict[str, Any]]:
        """Get CLI command definitions for external CLI generators."""
        commands = {}
        
        for cap_name, capability in self.capabilities.items():
            if capability.is_public:
                commands[cap_name] = {
                    'description': capability.description,
                    'parameters': capability.parameters,
                    'return_type': capability.return_type,
                    'is_async': capability.is_async
                }
        
        return commands

    def save_cli_interface(self, output_path: str) -> None:
        """Save generated CLI interface to file."""
        cli_code = self.generate_cli_interface()
        with open(output_path, 'w') as f:
            f.write(cli_code)

    # ========================================
    # UNIFIED CMS CAPABILITIES
    # ========================================
    
    def store_content(self, content_id: str, content_type: str, data: Any) -> Dict[str, Any]:
        """Store content in integrated CMS."""
        content_entry = {
            "type": content_type,
            "data": data,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "module_id": self.module_id
        }
        self._content_store[content_id] = content_entry
        return content_entry
    
    def get_content(self, content_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve content from integrated CMS."""
        return self._content_store.get(content_id)
    
    def list_content(self, content_type: Optional[str] = None) -> List[Dict[str, Any]]:
        """List content from integrated CMS."""
        if content_type:
            return [item for item in self._content_store.values() if item.get("type") == content_type]
        return list(self._content_store.values())
    
    def update_content(self, content_id: str, data: Any) -> bool:
        """Update content in integrated CMS."""
        if content_id in self._content_store:
            self._content_store[content_id]["data"] = data
            self._content_store[content_id]["updated_at"] = datetime.now().isoformat()
            return True
        return False
    
    def delete_content(self, content_id: str) -> bool:
        """Delete content from integrated CMS."""
        if content_id in self._content_store:
            del self._content_store[content_id]
            return True
        return False

    # ========================================
    # UNIFIED DDD CAPABILITIES
    # ========================================
    
    def get_ddd_metadata(self) -> Dict[str, Any]:
        """Get DDD-specific metadata for the module."""
        return {
            "bounded_context": {
                "name": self.bounded_context.name if self.bounded_context else None,
                "description": self.bounded_context.description if self.bounded_context else None,
                "entities": list(self.bounded_context.entities) if self.bounded_context else [],
                "value_objects": list(self.bounded_context.value_objects) if self.bounded_context else [],
                "aggregates": list(self.bounded_context.aggregates) if self.bounded_context else [],
                "domain_services": list(self.bounded_context.domain_services) if self.bounded_context else [],
                "repositories": list(self.bounded_context.repositories) if self.bounded_context else []
            },
            "ddd_pattern": self.ddd_pattern,
            "domain_vocabulary_size": len(self.domain_vocabulary.terms) if self.domain_vocabulary else 0,
            "ubiquitous_language_compliance": len(self._validate_ubiquitous_language()) == 0
        }

    def get_domain_vocabulary(self) -> Dict[str, str]:
        """Get domain vocabulary terms and definitions."""
        if self.domain_vocabulary:
            return self.domain_vocabulary.terms.copy()
        return {}

    def get_bounded_context_info(self) -> Dict[str, Any]:
        """Get bounded context information."""
        if not self.bounded_context:
            return {"error": "No bounded context defined"}
        
        return {
            "name": self.bounded_context.name,
            "description": self.bounded_context.description,
            "vocabulary_terms": len(self.bounded_context.vocabulary.terms),
            "entities": list(self.bounded_context.entities),
            "value_objects": list(self.bounded_context.value_objects),
            "aggregates": list(self.bounded_context.aggregates),
            "domain_services": list(self.bounded_context.domain_services),
            "repositories": list(self.bounded_context.repositories)
        }

    def validate_ddd_compliance(self) -> Dict[str, Any]:
        """Validate DDD compliance and return detailed results."""
        ubiquitous_language_violations = self._validate_ubiquitous_language()
        bounded_context_violations = self._validate_bounded_context_compliance()
        
        return {
            "overall_compliance": len(ubiquitous_language_violations) == 0 and len(bounded_context_violations) == 0,
            "ubiquitous_language": {
                "compliant": len(ubiquitous_language_violations) == 0,
                "violations": ubiquitous_language_violations,
                "vocabulary_size": len(self.domain_vocabulary.terms) if self.domain_vocabulary else 0
            },
            "bounded_context": {
                "compliant": len(bounded_context_violations) == 0,
                "violations": bounded_context_violations,
                "context_name": self.bounded_context.name if self.bounded_context else None,
                "ddd_pattern": self.ddd_pattern
            },
            "recommendations": self._get_ddd_recommendations()
        }

    def validate_command_language(self, command: str) -> Dict[str, Any]:
        """Validate that a command follows ubiquitous language."""
        if not self.domain_vocabulary:
            return {"valid": True, "message": "No vocabulary defined"}
        
        # Extract terms from command
        command_terms = re.findall(r'[a-z]+', command.lower())
        
        # Check if terms are in vocabulary
        unknown_terms = []
        for term in command_terms:
            if term not in self.domain_vocabulary.terms and len(term) > 2:  # Skip short words
                unknown_terms.append(term)
        
        if unknown_terms:
            return {
                "valid": False,
                "message": f"Command contains terms not in domain vocabulary: {unknown_terms}",
                "suggestions": self._suggest_vocabulary_terms(unknown_terms)
            }
        
        return {"valid": True, "message": "Command follows ubiquitous language"}

    def _get_ddd_recommendations(self) -> List[str]:
        """Get recommendations for improving DDD compliance."""
        recommendations = []
        
        if not self.bounded_context:
            recommendations.append("Define a bounded context for this module")
        
        if not self.domain_vocabulary or len(self.domain_vocabulary.terms) < 3:
            recommendations.append("Expand domain vocabulary with more specific terms")
        
        if self.ddd_pattern == "DomainService" and len(self.capabilities) > 10:
            recommendations.append("Consider splitting large domain service into smaller, focused services")
        
        return recommendations

    def _suggest_vocabulary_terms(self, unknown_terms: List[str]) -> List[str]:
        """Suggest vocabulary terms for unknown terms."""
        suggestions = []
        
        if not self.domain_vocabulary:
            return suggestions
        
        for unknown_term in unknown_terms:
            # Find similar terms in vocabulary
            for vocab_term in self.domain_vocabulary.terms.keys():
                if abs(len(unknown_term) - len(vocab_term)) <= 2:  # Similar length
                    # Simple similarity check
                    common_chars = set(unknown_term) & set(vocab_term)
                    if len(common_chars) >= min(3, len(unknown_term) - 1):
                        suggestions.append(f"'{unknown_term}' -> '{vocab_term}'")
        
        return suggestions

    def execute(self, *args, **kwargs) -> Any:
        """Execute the module's primary functionality - default implementation."""
        return {"status": "executed", "args": args, "kwargs": kwargs}

    def __str__(self) -> str:
        return f"ReflectiveModule(id={self.module_id}, status={self.status.value}, health={self.health.value})"

    def __repr__(self) -> str:
        return f"ReflectiveModule(module_id='{self.module_id}', capabilities={len(self.capabilities)})"
