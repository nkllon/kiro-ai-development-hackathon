#!/usr/bin/env python3
"""
Simple Repository Discovery - Leveraging ReflectiveModule Profiling
================================================================

Just discover files, classify them, and use built-in ReflectiveModule profiling.
No over-engineering, no complex metadata extraction, just what we need.

Author: Beast Mode Framework
Date: 2025-09-18
Version: 1.0
"""

import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

from src.rm_ddd.core.unified_reflective_module import ReflectiveModule, ModuleHealth, ModuleStatus, ModuleCapability
from src.repository_discovery.core.content_scanner import ContentScanner
from src.repository_discovery.core.content_classifier import ContentClassifier


@dataclass
class SimpleRepositoryInventory:
    """Simple inventory - just files and their types"""
    discovered_files: List[str]
    content_types: Dict[str, List[str]]  # type -> list of files
    total_files: int
    scan_duration: float
    classification_duration: float


class SimpleRepositoryDiscovery(ReflectiveModule):
    """
    Simple Repository Discovery - RM-DDD Compliant
    
    Just discover files and classify them. Use ReflectiveModule profiling for everything else.
    
    Single Responsibility: Discover repository content simply and efficiently
    """
    
    def __init__(self):
        super().__init__()
        self.module_id = "SimpleRepositoryDiscovery"
        self._logger = logging.getLogger(f"repository_discovery.{self.__class__.__name__}")
        
        # Use existing working components
        self._scanner = ContentScanner()
        self._classifier = ContentClassifier()
        
        self._logger.info("SimpleRepositoryDiscovery initialized - leveraging ReflectiveModule profiling")
    
    def discover_repository(self, root_path: Path, max_depth: Optional[int] = 3) -> SimpleRepositoryInventory:
        """
        Discover repository content simply and efficiently.
        
        Args:
            root_path: Root directory to scan
            max_depth: Maximum directory depth
            
        Returns:
            SimpleRepositoryInventory with discovered content
        """
        with self.trace_operation("discover_repository", root_path=str(root_path)) as trace:
            try:
                # Step 1: Scan filesystem (already working)
                scan_start = datetime.now()
                scan_result = self._scanner.discover_all_content(root_path, max_depth=max_depth)
                scan_duration = (datetime.now() - scan_start).total_seconds()
                
                # Step 2: Classify content types (already working)
                classify_start = datetime.now()
                file_paths = [Path(f) for f in scan_result.discovered_files]
                classification_result = self._classifier.classify_content_types(file_paths, batch_size=50)
                classify_duration = (datetime.now() - classify_start).total_seconds()
                
                # Step 3: Organize by content type
                content_types = {}
                for result in classification_result.results:
                    content_type = result.primary_type.value
                    if content_type not in content_types:
                        content_types[content_type] = []
                    content_types[content_type].append(str(result.file_path))
                
                # Create simple inventory
                inventory = SimpleRepositoryInventory(
                    discovered_files=scan_result.discovered_files,
                    content_types=content_types,
                    total_files=len(scan_result.discovered_files),
                    scan_duration=scan_duration,
                    classification_duration=classify_duration
                )
                
                self._logger.info(f"Repository discovery complete: {inventory.total_files} files, {len(content_types)} types")
                
                trace.output_result = {
                    'total_files': inventory.total_files,
                    'content_types': len(content_types),
                    'scan_duration': scan_duration,
                    'classification_duration': classify_duration
                }
                
                return inventory
                
            except Exception as e:
                error_msg = f"Repository discovery failed: {e}"
                self._logger.error(error_msg)
                trace.output_result = {'success': False, 'error': error_msg}
                raise
    
    def get_specs_inventory(self, root_path: Path) -> Dict[str, List[str]]:
        """Get just the specifications from repository"""
        with self.trace_operation("get_specs_inventory") as trace:
            inventory = self.discover_repository(root_path)
            specs = inventory.content_types.get('specification', [])
            
            trace.output_result = {'specs_found': len(specs)}
            return {'specifications': specs}
    
    def get_source_code_inventory(self, root_path: Path) -> Dict[str, List[str]]:
        """Get just the source code from repository"""
        with self.trace_operation("get_source_code_inventory") as trace:
            inventory = self.discover_repository(root_path)
            source_code = inventory.content_types.get('source_code', [])
            
            trace.output_result = {'source_files_found': len(source_code)}
            return {'source_code': source_code}
    
    # ReflectiveModule interface implementation
    def get_module_info(self) -> Dict[str, Any]:
        """Get module information - RDI Compliant"""
        return {
            "module_id": self.module_id,
            "name": "SimpleRepositoryDiscovery",
            "version": "1.0.0",
            "description": "Simple repository discovery leveraging ReflectiveModule profiling",
            "capabilities": [cap.value for cap in self.get_capabilities()],
            "status": "implemented",
            "uses_reflective_profiling": True,
            "dependencies": ["ContentScanner", "ContentClassifier"]
        }
    
    def get_capabilities(self) -> List[ModuleCapability]:
        """Get module capabilities - RDI Compliant"""
        return [
            ModuleCapability.CORE_FUNCTIONALITY,
            ModuleCapability.DATA_PROCESSING,
            ModuleCapability.MONITORING
        ]
    
    def get_health_status(self) -> ModuleHealth:
        """Get module health status - RDI Compliant"""
        try:
            # Check dependency health
            scanner_health = self._scanner.get_health_status()
            classifier_health = self._classifier.get_health_status()
            
            # Simple health aggregation
            if scanner_health.status == ModuleStatus.HEALTHY and classifier_health.status == ModuleStatus.HEALTHY:
                status = ModuleStatus.HEALTHY
                health_score = 1.0
                issues = []
            else:
                status = ModuleStatus.DEGRADED
                health_score = 0.5
                issues = ["Dependency health issues"]
                
        except Exception as e:
            status = ModuleStatus.ERROR
            health_score = 0.0
            issues = [f"SimpleRepositoryDiscovery health check failed: {str(e)}"]
        
        return ModuleHealth(
            module_id=self.module_id,
            status=status,
            health_score=health_score,
            issues=issues,
            last_check=datetime.now(),
            uptime_seconds=(datetime.now() - self._start_time).total_seconds()
        )
    
    def graceful_degradation(self):
        """Perform graceful degradation - RDI Compliant"""
        from src.rm_ddd.core.unified_reflective_module import GracefulDegradationResult
        
        try:
            # In degraded mode, we can still do basic discovery
            remaining_capabilities = [ModuleCapability.CORE_FUNCTIONALITY]
            degraded_capabilities = [ModuleCapability.DATA_PROCESSING, ModuleCapability.MONITORING]
            
            return GracefulDegradationResult(
                success=True,
                degraded_capabilities=degraded_capabilities,
                remaining_capabilities=remaining_capabilities
            )
        except Exception as e:
            return GracefulDegradationResult(
                success=False,
                degraded_capabilities=[ModuleCapability.CORE_FUNCTIONALITY],
                remaining_capabilities=[],
                error_message=str(e)
            )