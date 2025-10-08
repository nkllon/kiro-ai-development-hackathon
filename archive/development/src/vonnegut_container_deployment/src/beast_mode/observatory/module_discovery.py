"""
Module Discovery Engine - Discovers and catalogs reflective modules in Beast Mode framework.

This module provides automatic discovery of Beast Mode components that inherit from
ReflectiveModule and validates their capabilities for Observatory integration.
"""

import asyncio
import importlib
import inspect
import logging
import pkgutil
import sys
import time
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any, Set, Type, Union

from src.rm_ddd.core.unified_reflective_module import (
    ReflectiveModule,
    ModuleHealth,
    ModuleStatus,
    ModuleCapability,
)


logger = logging.getLogger(__name__)


@dataclass
class ModuleInfo:
    """Information about a discovered Beast Mode module."""
    module_id: str
    module_path: str
    class_name: str
    module_class: Type[ReflectiveModule]
    instance: Optional[ReflectiveModule] = None
    capabilities: List[ModuleCapability] = field(default_factory=list)
    has_get_metrics: bool = False
    has_get_health_status: bool = False
    last_seen: datetime = field(default_factory=datetime.now)
    discovery_errors: List[str] = field(default_factory=list)


@dataclass
class ModuleCapabilities:
    """Capabilities assessment for a discovered module."""
    has_reflective_interface: bool
    has_get_metrics: bool
    has_get_health_status: bool
    has_get_module_info: bool
    has_get_capabilities: bool
    supported_capabilities: List[ModuleCapability]
    validation_errors: List[str]


class ModuleDiscoveryEngine:
    """
    Discovers and catalogs Beast Mode reflective modules for Observatory integration.
    
    Features:
    - Automatic scanning of Beast Mode framework for ReflectiveModule subclasses
    - Safe module loading with error handling and isolation
    - Capability validation and interface compliance checking
    - Module registry with health tracking and performance monitoring
    """
    
    def __init__(self):
        self.module_id = "module_discovery_engine"
        self._discovered_modules: Dict[str, ModuleInfo] = {}
        self._discovery_errors: List[str] = []
        self._last_discovery: Optional[datetime] = None
        self._discovery_count = 0
        
        # Performance tracking
        self._start_time = time.time()
        self._total_discoveries = 0
        self._failed_discoveries = 0
        
        logger.info("🔍 ModuleDiscoveryEngine initialized - Ready to discover Beast Mode modules")
    
    async def discover_reflective_modules(self) -> Dict[str, ModuleInfo]:
        """
        Discover all reflective modules in the Beast Mode framework.
        
        Returns:
            Dictionary mapping module_id to ModuleInfo for discovered modules
        """
        logger.info("🔍 Starting Beast Mode module discovery...")
        discovery_start = time.time()
        
        try:
            # Clear previous discovery results
            self._discovered_modules.clear()
            self._discovery_errors.clear()
            
            # Scan Beast Mode framework
            await self._scan_beast_mode_modules()
            
            # Validate discovered modules
            await self._validate_discovered_modules()
            
            # Update discovery statistics
            self._last_discovery = datetime.now()
            self._discovery_count += 1
            self._total_discoveries += len(self._discovered_modules)
            
            discovery_duration = time.time() - discovery_start
            
            logger.info(
                f"✅ Module discovery complete: {len(self._discovered_modules)} modules found "
                f"in {discovery_duration:.2f}s"
            )
            
            if self._discovery_errors:
                logger.warning(f"⚠️ Discovery encountered {len(self._discovery_errors)} errors")
                for error in self._discovery_errors[:5]:  # Log first 5 errors
                    logger.warning(f"   - {error}")
            
            return self._discovered_modules.copy()
            
        except Exception as e:
            logger.error(f"❌ Module discovery failed: {e}")
            self._failed_discoveries += 1
            raise
    
    async def _scan_beast_mode_modules(self) -> None:
        """Scan the Beast Mode framework for reflective modules."""
        beast_mode_path = Path(__file__).parent.parent
        logger.debug(f"🔍 Scanning Beast Mode path: {beast_mode_path}")
        
        # Walk through all Beast Mode modules
        for module_info in pkgutil.walk_packages([str(beast_mode_path)], "beast_mode."):
            try:
                # Skip certain modules to avoid issues
                if self._should_skip_module(module_info.name):
                    continue
                
                await self._discover_module(module_info.name)
                
            except Exception as e:
                error_msg = f"Failed to scan module {module_info.name}: {e}"
                self._discovery_errors.append(error_msg)
                logger.debug(error_msg)
                continue
    
    def _should_skip_module(self, module_name: str) -> bool:
        """Check if a module should be skipped during discovery."""
        skip_patterns = [
            "beast_mode.observatory.module_discovery",  # Avoid self-discovery
            "beast_mode.tests",  # Skip test modules
            "beast_mode.__pycache__",  # Skip cache
        ]
        
        return any(pattern in module_name for pattern in skip_patterns)
    
    async def _discover_module(self, module_name: str) -> None:
        """Discover reflective modules in a specific Python module."""
        try:
            # Import the module safely
            module = importlib.import_module(module_name)
            
            # Look for ReflectiveModule subclasses
            for name, obj in inspect.getmembers(module, inspect.isclass):
                if self._is_reflective_module(obj):
                    await self._register_discovered_module(module_name, name, obj)
                    
        except ImportError as e:
            # Module can't be imported (missing dependencies, etc.)
            logger.debug(f"Skipped module {module_name}: {e}")
        except Exception as e:
            error_msg = f"Error discovering module {module_name}: {e}"
            self._discovery_errors.append(error_msg)
            logger.debug(error_msg)
    
    def _is_reflective_module(self, cls: Type) -> bool:
        """Check if a class is a ReflectiveModule subclass."""
        try:
            # Check if it's a subclass of ReflectiveModule
            if not inspect.isclass(cls):
                return False
            
            # Check inheritance chain
            return (
                issubclass(cls, ReflectiveModule) and 
                cls != ReflectiveModule  # Don't include the base class itself
            )
            
        except Exception:
            return False
    
    async def _register_discovered_module(self, module_path: str, class_name: str, module_class: Type[ReflectiveModule]) -> None:
        """Register a discovered reflective module."""
        try:
            module_id = f"{module_path}.{class_name}"
            
            # Validate module capabilities
            capabilities = await self.validate_module_capabilities(module_class)
            
            # Create module info
            module_info = ModuleInfo(
                module_id=module_id,
                module_path=module_path,
                class_name=class_name,
                module_class=module_class,
                capabilities=capabilities.supported_capabilities,
                has_get_metrics=capabilities.has_get_metrics,
                has_get_health_status=capabilities.has_get_health_status,
                discovery_errors=capabilities.validation_errors
            )
            
            # Try to create an instance for testing
            try:
                instance = module_class()
                module_info.instance = instance
                logger.debug(f"✅ Successfully instantiated {module_id}")
            except Exception as e:
                error_msg = f"Failed to instantiate {module_id}: {e}"
                module_info.discovery_errors.append(error_msg)
                logger.debug(error_msg)
            
            # Register the module
            self._discovered_modules[module_id] = module_info
            logger.debug(f"🔍 Discovered module: {module_id}")
            
        except Exception as e:
            error_msg = f"Failed to register module {module_path}.{class_name}: {e}"
            self._discovery_errors.append(error_msg)
            logger.debug(error_msg)
    
    async def validate_module_capabilities(self, module_class: Type[ReflectiveModule]) -> ModuleCapabilities:
        """
        Validate that a module implements required interfaces.
        
        Args:
            module_class: The ReflectiveModule subclass to validate
            
        Returns:
            ModuleCapabilities with validation results
        """
        capabilities = ModuleCapabilities(
            has_reflective_interface=True,  # Already validated by inheritance check
            has_get_metrics=False,
            has_get_health_status=False,
            has_get_module_info=False,
            has_get_capabilities=False,
            supported_capabilities=[],
            validation_errors=[]
        )
        
        try:
            # Check for required methods
            capabilities.has_get_health_status = hasattr(module_class, 'get_health_status')
            capabilities.has_get_module_info = hasattr(module_class, 'get_module_info')
            capabilities.has_get_capabilities = hasattr(module_class, 'get_capabilities')
            
            # Check for get_metrics method (Observatory-specific)
            capabilities.has_get_metrics = hasattr(module_class, 'get_metrics')
            
            # Try to instantiate and get capabilities
            try:
                instance = module_class()
                if hasattr(instance, 'get_capabilities'):
                    module_capabilities = instance.get_capabilities()
                    if isinstance(module_capabilities, list):
                        capabilities.supported_capabilities = module_capabilities
            except Exception as e:
                capabilities.validation_errors.append(f"Failed to get capabilities: {e}")
            
            # Validate required abstract methods are implemented
            if not capabilities.has_get_health_status:
                capabilities.validation_errors.append("Missing get_health_status method")
            
            if not capabilities.has_get_module_info:
                capabilities.validation_errors.append("Missing get_module_info method")
            
            if not capabilities.has_get_capabilities:
                capabilities.validation_errors.append("Missing get_capabilities method")
            
        except Exception as e:
            capabilities.validation_errors.append(f"Validation error: {e}")
        
        return capabilities
    
    async def _validate_discovered_modules(self) -> None:
        """Validate all discovered modules for Observatory compatibility."""
        logger.debug("🔍 Validating discovered modules...")
        
        valid_modules = {}
        
        for module_id, module_info in self._discovered_modules.items():
            try:
                # Check if module has critical errors
                if module_info.discovery_errors:
                    logger.debug(f"⚠️ Module {module_id} has validation errors: {module_info.discovery_errors}")
                
                # Module is valid if it has basic reflective interface
                if module_info.has_get_health_status:
                    valid_modules[module_id] = module_info
                    logger.debug(f"✅ Module {module_id} validated for Observatory")
                else:
                    logger.debug(f"❌ Module {module_id} missing required interfaces")
                    
            except Exception as e:
                error_msg = f"Validation failed for {module_id}: {e}"
                self._discovery_errors.append(error_msg)
                logger.debug(error_msg)
        
        # Update discovered modules to only include valid ones
        self._discovered_modules = valid_modules
        logger.debug(f"✅ Validation complete: {len(valid_modules)} valid modules")
    
    async def refresh_module_registry(self) -> None:
        """Refresh the module registry by re-discovering modules."""
        logger.info("🔄 Refreshing module registry...")
        await self.discover_reflective_modules()
    
    def get_discovered_modules(self) -> Dict[str, ModuleInfo]:
        """Get all discovered modules."""
        return self._discovered_modules.copy()
    
    def get_module_by_id(self, module_id: str) -> Optional[ModuleInfo]:
        """Get a specific module by ID."""
        return self._discovered_modules.get(module_id)
    
    def get_modules_with_metrics(self) -> Dict[str, ModuleInfo]:
        """Get modules that implement get_metrics method."""
        return {
            module_id: module_info
            for module_id, module_info in self._discovered_modules.items()
            if module_info.has_get_metrics
        }
    
    def get_discovery_stats(self) -> Dict[str, Any]:
        """Get discovery performance statistics."""
        uptime = time.time() - self._start_time
        
        return {
            "uptime_seconds": uptime,
            "discovery_count": self._discovery_count,
            "total_discoveries": self._total_discoveries,
            "failed_discoveries": self._failed_discoveries,
            "last_discovery": self._last_discovery.isoformat() if self._last_discovery else None,
            "discovered_modules": len(self._discovered_modules),
            "modules_with_metrics": len(self.get_modules_with_metrics()),
            "discovery_errors": len(self._discovery_errors),
            "discovery_success_rate": (
                (self._total_discoveries / max(1, self._total_discoveries + self._failed_discoveries)) * 100
            )
        }
    
    def get_health_status(self) -> ModuleHealth:
        """Get health status of the discovery engine."""
        if not self._discovered_modules:
            status = ModuleStatus.WARNING
            health_score = 0.5
            issues = ["No modules discovered yet"]
        elif self._discovery_errors:
            status = ModuleStatus.WARNING
            health_score = 0.7
            issues = [f"{len(self._discovery_errors)} discovery errors"]
        else:
            status = ModuleStatus.HEALTHY
            health_score = 1.0
            issues = []
        
        return ModuleHealth(
            module_id=self.module_id,
            status=status,
            health_score=health_score,
            issues=issues,
            last_check=datetime.now(),
            uptime_seconds=time.time() - self._start_time,
            error_count=self._failed_discoveries,
            warning_count=len(self._discovery_errors)
        )