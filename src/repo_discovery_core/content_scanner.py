#!/usr/bin/env python3
"""
Content Scanner - Repository Discovery System
===========================================

Systematically discovers repository content with complete monitoring integration.
Provides filesystem traversal with filtering, exclusion patterns, and progress tracking.

Author: Beast Mode Framework
Date: 2025-09-18
Version: 1.0
"""

import os
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List, Optional, Callable, Set
from dataclasses import dataclass, asdict
import fnmatch
import uuid

# Import unified ReflectiveModule
from ._reflective import (
    ReflectiveModule, 
    ModuleHealth, 
    ModuleStatus, 
    ModuleCapability,
    GracefulDegradationResult
)


@dataclass
class ScanProgress:
    """Value object for scan progress tracking"""
    scan_id: str
    total_files: int
    processed_files: int
    current_file: str
    start_time: datetime
    estimated_completion: Optional[datetime]
    errors: List[str]
    
    @property
    def percentage_complete(self) -> float:
        if self.total_files == 0:
            return 100.0
        return (self.processed_files / self.total_files) * 100.0


@dataclass
class ContentScanResult:
    """Value object for scan results"""
    scan_id: str
    root_path: str
    discovered_files: List[str]
    discovered_directories: List[str]
    excluded_files: List[str]
    scan_duration: float
    total_size: int
    error_count: int
    errors: List[str]


class ContentDiscoveryError(Exception):
    """Exception for content discovery failures"""
    pass


class ContentScanner(ReflectiveModule):
    """
    Content Scanner - RM-DDD Compliant
    
    Systematically discovers repository content with complete monitoring.
    
    Single Responsibility: Discover and catalog all repository content
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        super().__init__()
        self.module_id = "ContentScanner"
        self._config = config or {}
        self._logger = logging.getLogger(f"repository_discovery.core.{self.__class__.__name__}")
        
        # Default exclusion patterns
        self._default_exclusions = [
            ".git/*", ".git/**/*",
            "node_modules/*", "node_modules/**/*", 
            "__pycache__/*", "__pycache__/**/*",
            "*.pyc", "*.pyo", "*.pyd",
            ".DS_Store", "Thumbs.db",
            "*.log", "*.tmp", "*.temp"
        ]
        
        # Active scans tracking
        self._active_scans: Dict[str, ScanProgress] = {}
        self._cancelled_scans: Set[str] = set()
        
        self._logger.info(f"ContentScanner initialized with {len(self._default_exclusions)} default exclusions")
    
    def discover_all_content(
        self,
        root_path: Path,
        exclusion_patterns: Optional[List[str]] = None,
        max_depth: Optional[int] = None,
        follow_symlinks: bool = False,
        progress_callback: Optional[Callable[[ScanProgress], None]] = None
    ) -> ContentScanResult:
        """
        Systematically scan repository filesystem with comprehensive monitoring.
        
        Args:
            root_path: Root directory to scan
            exclusion_patterns: Additional patterns to exclude
            max_depth: Maximum directory depth (None for unlimited)
            follow_symlinks: Whether to follow symbolic links
            progress_callback: Optional callback for progress updates
            
        Returns:
            ContentScanResult with discovered content
            
        Raises:
            ContentDiscoveryError: When filesystem access fails
            ValidationError: When exclusion patterns are invalid
            PermissionError: When access is denied
        """
        with self.trace_operation("discover_all_content") as trace:
            scan_id = str(uuid.uuid4())
            start_time = datetime.now()
            
            try:
                # Validate inputs
                if not root_path.exists():
                    raise ContentDiscoveryError(f"Root path does not exist: {root_path}")
                
                if not root_path.is_dir():
                    raise ContentDiscoveryError(f"Root path is not a directory: {root_path}")
                
                # Combine exclusion patterns
                all_exclusions = self._default_exclusions.copy()
                if exclusion_patterns:
                    all_exclusions.extend(exclusion_patterns)
                
                # Initialize scan progress
                progress = ScanProgress(
                    scan_id=scan_id,
                    total_files=0,
                    processed_files=0,
                    current_file="",
                    start_time=start_time,
                    estimated_completion=None,
                    errors=[]
                )
                
                self._active_scans[scan_id] = progress
                
                # First pass: count total files for progress tracking
                total_files = self._count_files(root_path, all_exclusions, max_depth, follow_symlinks)
                progress.total_files = total_files
                
                # Second pass: actual discovery
                discovered_files = []
                discovered_directories = []
                excluded_files = []
                total_size = 0
                
                for file_path in self._walk_filesystem(root_path, all_exclusions, max_depth, follow_symlinks):
                    # Check for cancellation
                    if scan_id in self._cancelled_scans:
                        self._logger.info(f"Scan {scan_id} cancelled by user")
                        break
                    
                    try:
                        if file_path.is_file():
                            discovered_files.append(str(file_path))
                            total_size += file_path.stat().st_size
                        elif file_path.is_dir():
                            discovered_directories.append(str(file_path))
                        
                        progress.processed_files += 1
                        progress.current_file = str(file_path)
                        
                        # Call progress callback if provided
                        if progress_callback and progress.processed_files % 100 == 0:
                            progress_callback(progress)
                            
                    except (OSError, PermissionError) as e:
                        error_msg = f"Error accessing {file_path}: {e}"
                        progress.errors.append(error_msg)
                        self._logger.warning(error_msg)
                
                # Calculate final results
                scan_duration = (datetime.now() - start_time).total_seconds()
                
                result = ContentScanResult(
                    scan_id=scan_id,
                    root_path=str(root_path),
                    discovered_files=discovered_files,
                    discovered_directories=discovered_directories,
                    excluded_files=excluded_files,
                    scan_duration=scan_duration,
                    total_size=total_size,
                    error_count=len(progress.errors),
                    errors=progress.errors
                )
                
                # Clean up active scan tracking
                if scan_id in self._active_scans:
                    del self._active_scans[scan_id]
                if scan_id in self._cancelled_scans:
                    self._cancelled_scans.remove(scan_id)
                
                self._logger.info(f"Scan completed: {len(discovered_files)} files, {len(discovered_directories)} directories")
                
                trace.output_result = asdict(result)
                return result
                
            except Exception as e:
                error_msg = f"Content discovery failed: {e}"
                self._logger.error(error_msg)
                trace.output_result = {'success': False, 'error': error_msg}
                
                # Clean up on error
                if scan_id in self._active_scans:
                    del self._active_scans[scan_id]
                if scan_id in self._cancelled_scans:
                    self._cancelled_scans.remove(scan_id)
                    
                raise ContentDiscoveryError(error_msg) from e
    
    def get_scan_progress(self, scan_id: str) -> Optional[ScanProgress]:
        """Get real-time progress of ongoing scan operation"""
        with self.trace_operation("get_scan_progress") as trace:
            progress = self._active_scans.get(scan_id)
            trace.output_result = asdict(progress) if progress else None
            return progress
    
    def cancel_scan(self, scan_id: str) -> bool:
        """Cancel ongoing scan operation gracefully"""
        with self.trace_operation("cancel_scan") as trace:
            if scan_id in self._active_scans:
                self._cancelled_scans.add(scan_id)
                self._logger.info(f"Scan {scan_id} marked for cancellation")
                trace.output_result = {'cancelled': True, 'scan_id': scan_id}
                return True
            else:
                self._logger.warning(f"Cannot cancel scan {scan_id}: not found in active scans")
                trace.output_result = {'cancelled': False, 'scan_id': scan_id, 'reason': 'not_found'}
                return False
    
    def _count_files(self, root_path: Path, exclusions: List[str], max_depth: Optional[int], follow_symlinks: bool) -> int:
        """Count total files for progress tracking"""
        count = 0
        try:
            for _ in self._walk_filesystem(root_path, exclusions, max_depth, follow_symlinks):
                count += 1
        except Exception as e:
            self._logger.warning(f"Error counting files: {e}")
        return count
    
    def _walk_filesystem(self, root_path: Path, exclusions: List[str], max_depth: Optional[int], follow_symlinks: bool):
        """Generator for filesystem traversal with exclusion patterns"""
        def _should_exclude(path: Path) -> bool:
            path_str = str(path)
            relative_path = str(path.relative_to(root_path))
            
            for pattern in exclusions:
                if fnmatch.fnmatch(path_str, pattern) or fnmatch.fnmatch(relative_path, pattern):
                    return True
            return False
        
        def _walk_recursive(current_path: Path, current_depth: int):
            if max_depth is not None and current_depth > max_depth:
                return
            
            try:
                for item in current_path.iterdir():
                    if _should_exclude(item):
                        continue
                    
                    # Handle symlinks
                    if item.is_symlink() and not follow_symlinks:
                        continue
                    
                    yield item
                    
                    if item.is_dir():
                        yield from _walk_recursive(item, current_depth + 1)
                        
            except (OSError, PermissionError) as e:
                self._logger.warning(f"Cannot access directory {current_path}: {e}")
        
        yield from _walk_recursive(root_path, 0)
    
    # ReflectiveModule interface implementation
    def get_module_info(self) -> Dict[str, Any]:
        """Get module information - RDI Compliant"""
        return {
            "module_id": self.module_id,
            "name": "ContentScanner",
            "version": "1.0.0",
            "description": "Systematically discovers repository content with monitoring",
            "capabilities": [cap.value for cap in self.get_capabilities()],
            "status": "implemented",
            "active_scans": len(self._active_scans),
            "default_exclusions": len(self._default_exclusions)
        }
    
    def get_capabilities(self) -> List[ModuleCapability]:
        """Get module capabilities - RDI Compliant"""
        return [
            ModuleCapability.CORE_FUNCTIONALITY,
            ModuleCapability.DATA_PROCESSING,
            ModuleCapability.VALIDATION,
            ModuleCapability.MONITORING
        ]
    
    def get_health_status(self) -> ModuleHealth:
        """Get module health status - RDI Compliant"""
        try:
            # Test filesystem access
            test_path = Path(".")
            can_read = test_path.exists() and os.access(test_path, os.R_OK)
            
            if can_read:
                status = ModuleStatus.HEALTHY
                health_score = 1.0
                issues = []
            else:
                status = ModuleStatus.DEGRADED
                health_score = 0.5
                issues = ["Limited filesystem access"]
                
        except Exception as e:
            status = ModuleStatus.ERROR
            health_score = 0.0
            issues = [f"ContentScanner health check failed: {str(e)}"]
        
        return ModuleHealth(
            module_id=self.module_id,
            status=status,
            health_score=health_score,
            issues=issues,
            last_check=datetime.now(),
            uptime_seconds=(datetime.now() - self._start_time).total_seconds()
        )
    
    def graceful_degradation(self) -> GracefulDegradationResult:
        """Perform graceful degradation - RDI Compliant"""
        try:
            # In degraded mode, we can still scan but with limited functionality
            remaining_capabilities = [
                ModuleCapability.CORE_FUNCTIONALITY
            ]
            
            degraded_capabilities = [
                ModuleCapability.DATA_PROCESSING,
                ModuleCapability.VALIDATION,
                ModuleCapability.MONITORING
            ]
            
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