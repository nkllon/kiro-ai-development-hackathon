#!/usr/bin/env python3
"""
Disk Space Manager for DAG Orchestration System
===============================================

Monitors and manages disk space to prevent system failures due to disk exhaustion.
Provides cleanup strategies and space monitoring for the DAG orchestration system.

Author: Beast Mode Framework
Date: 2025-01-27
Version: 1.0
"""

import os
import shutil
import logging
import subprocess
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path

from src.rm_ddd.core.unified_reflective_module import (
    ReflectiveModule,
    ModuleHealth,
    ModuleStatus,
    ModuleCapability,
    GracefulDegradationResult
)


@dataclass
class DiskUsageInfo:
    """Information about disk usage for a specific path."""
    path: str
    size_bytes: int
    size_human: str
    file_count: int
    last_modified: datetime


@dataclass
class CleanupAction:
    """Represents a potential cleanup action."""
    action_type: str  # 'delete', 'compress', 'archive', 'truncate'
    target_path: str
    estimated_savings_bytes: int
    estimated_savings_human: str
    risk_level: str  # 'low', 'medium', 'high'
    description: str


@dataclass
class DiskSpaceReport:
    """Comprehensive disk space analysis report."""
    total_space_gb: float
    used_space_gb: float
    free_space_gb: float
    usage_percent: float
    critical_threshold_reached: bool
    warning_threshold_reached: bool
    large_consumers: List[DiskUsageInfo]
    cleanup_recommendations: List[CleanupAction]
    generated_at: datetime


class DiskSpaceManager(ReflectiveModule):
    """
    Manages disk space for DAG orchestration system.
    
    Provides:
    - Disk space monitoring and alerting
    - Identification of space consumers
    - Safe cleanup recommendations
    - Automated cleanup capabilities
    """
    
    def __init__(self, workspace_root: Optional[str] = None):
        super().__init__()
        self.module_id = "DiskSpaceManager"
        self._logger = logging.getLogger(f"dag_orchestration.{self.__class__.__name__}")
        
        # Configuration
        self.workspace_root = Path(workspace_root or ".")
        self.critical_threshold_percent = 95  # Critical at 95% usage
        self.warning_threshold_percent = 85   # Warning at 85% usage
        self.min_free_gb = 2.0               # Minimum 2GB free space
        
        # Cleanup configuration
        self.safe_cleanup_paths = [
            ".pytest_cache",
            ".mypy_cache", 
            ".ruff_cache",
            "__pycache__",
            "*.pyc",
            "*.pyo",
            "*.log",
            "temp*",
            "tmp*"
        ]
        
        # Paths to analyze but not auto-clean
        self.analysis_paths = [
            ".venv",
            ".git",
            "node_modules",
            "docker",
            "logs",
            "var"
        ]
        
        self._last_analysis: Optional[DiskSpaceReport] = None
        
        self._logger.info(f"DiskSpaceManager initialized for workspace: {self.workspace_root}")
    
    def get_module_info(self) -> Dict[str, Any]:
        """Get module information - RDI Compliant"""
        return {
            "module_id": self.module_id,
            "name": "DiskSpaceManager",
            "version": "1.0.0",
            "description": "Manages disk space for DAG orchestration system",
            "capabilities": [cap.value for cap in self.get_capabilities()],
            "workspace_root": str(self.workspace_root),
            "thresholds": {
                "critical_percent": self.critical_threshold_percent,
                "warning_percent": self.warning_threshold_percent,
                "min_free_gb": self.min_free_gb
            },
            "last_analysis": self._last_analysis.generated_at.isoformat() if self._last_analysis else None
        }
    
    def get_capabilities(self) -> List[ModuleCapability]:
        """Get module capabilities - RDI Compliant"""
        return [
            ModuleCapability.CORE_FUNCTIONALITY,
            ModuleCapability.MONITORING,
            ModuleCapability.DATA_PROCESSING
        ]
    
    def get_health_status(self) -> ModuleHealth:
        """Get module health status - RDI Compliant"""
        try:
            # Check current disk space
            disk_usage = shutil.disk_usage(self.workspace_root)
            free_gb = disk_usage.free / (1024**3)
            usage_percent = (disk_usage.used / disk_usage.total) * 100
            
            issues = []
            health_score = 1.0
            
            # Check disk space thresholds
            if usage_percent >= self.critical_threshold_percent:
                issues.append(f"Critical disk usage: {usage_percent:.1f}%")
                health_score = 0.2
            elif usage_percent >= self.warning_threshold_percent:
                issues.append(f"High disk usage: {usage_percent:.1f}%")
                health_score = 0.6
            elif free_gb < self.min_free_gb:
                issues.append(f"Low free space: {free_gb:.1f}GB")
                health_score = 0.7
            
            # Determine status
            if health_score >= 0.8:
                status = ModuleStatus.HEALTHY
            elif health_score >= 0.5:
                status = ModuleStatus.WARNING
            else:
                status = ModuleStatus.ERROR
                
        except Exception as e:
            status = ModuleStatus.ERROR
            health_score = 0.0
            issues = [f"Disk space check failed: {str(e)}"]
        
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
            # In degraded mode, we can still monitor but may lose cleanup capabilities
            remaining_capabilities = [
                ModuleCapability.CORE_FUNCTIONALITY,
                ModuleCapability.MONITORING
            ]
            
            degraded_capabilities = [
                ModuleCapability.DATA_PROCESSING  # May lose cleanup processing
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
    
    def analyze_disk_usage(self) -> DiskSpaceReport:
        """
        Perform comprehensive disk usage analysis.
        
        Returns:
            DiskSpaceReport with detailed analysis and recommendations
        """
        with self.trace_operation("analyze_disk_usage") as trace:
            try:
                # Get overall disk usage
                disk_usage = shutil.disk_usage(self.workspace_root)
                total_gb = disk_usage.total / (1024**3)
                used_gb = disk_usage.used / (1024**3)
                free_gb = disk_usage.free / (1024**3)
                usage_percent = (used_gb / total_gb) * 100
                
                # Check thresholds
                critical_threshold_reached = usage_percent >= self.critical_threshold_percent
                warning_threshold_reached = usage_percent >= self.warning_threshold_percent
                
                # Analyze large consumers
                large_consumers = self._analyze_large_consumers()
                
                # Generate cleanup recommendations
                cleanup_recommendations = self._generate_cleanup_recommendations(large_consumers)
                
                # Create report
                report = DiskSpaceReport(
                    total_space_gb=total_gb,
                    used_space_gb=used_gb,
                    free_space_gb=free_gb,
                    usage_percent=usage_percent,
                    critical_threshold_reached=critical_threshold_reached,
                    warning_threshold_reached=warning_threshold_reached,
                    large_consumers=large_consumers,
                    cleanup_recommendations=cleanup_recommendations,
                    generated_at=datetime.now()
                )
                
                self._last_analysis = report
                
                trace.output_result = {
                    'total_gb': total_gb,
                    'used_gb': used_gb,
                    'free_gb': free_gb,
                    'usage_percent': usage_percent,
                    'large_consumers_count': len(large_consumers),
                    'cleanup_recommendations_count': len(cleanup_recommendations)
                }
                
                return report
                
            except Exception as e:
                self._logger.error(f"Disk usage analysis failed: {e}")
                trace.output_result = {'error': str(e)}
                raise
    
    def _analyze_large_consumers(self) -> List[DiskUsageInfo]:
        """Analyze directories and files that consume significant disk space."""
        large_consumers = []
        
        try:
            # Analyze top-level directories
            for item in self.workspace_root.iterdir():
                if item.is_dir():
                    try:
                        size_bytes = self._get_directory_size(item)
                        if size_bytes > 10 * 1024 * 1024:  # > 10MB
                            file_count = self._count_files_in_directory(item)
                            large_consumers.append(DiskUsageInfo(
                                path=str(item.relative_to(self.workspace_root)),
                                size_bytes=size_bytes,
                                size_human=self._format_bytes(size_bytes),
                                file_count=file_count,
                                last_modified=datetime.fromtimestamp(item.stat().st_mtime)
                            ))
                    except (OSError, PermissionError) as e:
                        self._logger.warning(f"Could not analyze {item}: {e}")
            
            # Sort by size (largest first)
            large_consumers.sort(key=lambda x: x.size_bytes, reverse=True)
            
        except Exception as e:
            self._logger.error(f"Error analyzing large consumers: {e}")
        
        return large_consumers
    
    def _generate_cleanup_recommendations(self, large_consumers: List[DiskUsageInfo]) -> List[CleanupAction]:
        """Generate safe cleanup recommendations based on analysis."""
        recommendations = []
        
        try:
            # Check for cache directories
            for consumer in large_consumers:
                path = consumer.path
                
                # Python cache directories
                if any(cache_name in path for cache_name in ['.pytest_cache', '.mypy_cache', '.ruff_cache']):
                    recommendations.append(CleanupAction(
                        action_type='delete',
                        target_path=path,
                        estimated_savings_bytes=consumer.size_bytes,
                        estimated_savings_human=consumer.size_human,
                        risk_level='low',
                        description=f"Safe to delete Python cache directory: {path}"
                    ))
                
                # Log files
                elif 'log' in path.lower() and consumer.size_bytes > 50 * 1024 * 1024:  # > 50MB
                    recommendations.append(CleanupAction(
                        action_type='truncate',
                        target_path=path,
                        estimated_savings_bytes=consumer.size_bytes // 2,  # Estimate 50% savings
                        estimated_savings_human=self._format_bytes(consumer.size_bytes // 2),
                        risk_level='low',
                        description=f"Truncate large log directory: {path}"
                    ))
                
                # Virtual environment (analysis only)
                elif '.venv' in path:
                    recommendations.append(CleanupAction(
                        action_type='analyze',
                        target_path=path,
                        estimated_savings_bytes=0,
                        estimated_savings_human='0B',
                        risk_level='high',
                        description=f"Virtual environment consuming {consumer.size_human} - consider removing unused packages"
                    ))
                
                # Git repository
                elif '.git' in path and consumer.size_bytes > 100 * 1024 * 1024:  # > 100MB
                    recommendations.append(CleanupAction(
                        action_type='compress',
                        target_path=path,
                        estimated_savings_bytes=consumer.size_bytes // 4,  # Estimate 25% savings
                        estimated_savings_human=self._format_bytes(consumer.size_bytes // 4),
                        risk_level='medium',
                        description=f"Git repository is large ({consumer.size_human}) - consider git gc"
                    ))
            
            # Check for specific large files
            self._add_large_file_recommendations(recommendations)
            
        except Exception as e:
            self._logger.error(f"Error generating cleanup recommendations: {e}")
        
        return recommendations
    
    def _add_large_file_recommendations(self, recommendations: List[CleanupAction]):
        """Add recommendations for specific large files."""
        try:
            # Check for large log files
            log_files = list(self.workspace_root.rglob("*.log"))
            for log_file in log_files:
                try:
                    size = log_file.stat().st_size
                    if size > 10 * 1024 * 1024:  # > 10MB
                        recommendations.append(CleanupAction(
                            action_type='truncate',
                            target_path=str(log_file.relative_to(self.workspace_root)),
                            estimated_savings_bytes=size // 2,
                            estimated_savings_human=self._format_bytes(size // 2),
                            risk_level='low',
                            description=f"Truncate large log file: {log_file.name} ({self._format_bytes(size)})"
                        ))
                except (OSError, PermissionError):
                    continue
                    
        except Exception as e:
            self._logger.error(f"Error checking large files: {e}")
    
    def execute_safe_cleanup(self, dry_run: bool = True) -> Dict[str, Any]:
        """
        Execute safe cleanup actions.
        
        Args:
            dry_run: If True, only simulate cleanup without making changes
            
        Returns:
            Dict with cleanup results
        """
        with self.trace_operation("execute_safe_cleanup", dry_run=dry_run) as trace:
            if not self._last_analysis:
                self.analyze_disk_usage()
            
            cleanup_results = {
                'dry_run': dry_run,
                'actions_executed': 0,
                'bytes_freed': 0,
                'actions': []
            }
            
            try:
                # Only execute low-risk cleanup actions
                safe_actions = [
                    action for action in self._last_analysis.cleanup_recommendations
                    if action.risk_level == 'low'
                ]
                
                for action in safe_actions:
                    try:
                        if action.action_type == 'delete':
                            result = self._execute_delete_action(action, dry_run)
                        elif action.action_type == 'truncate':
                            result = self._execute_truncate_action(action, dry_run)
                        else:
                            continue  # Skip non-safe actions
                        
                        cleanup_results['actions'].append(result)
                        if result['success']:
                            cleanup_results['actions_executed'] += 1
                            cleanup_results['bytes_freed'] += result.get('bytes_freed', 0)
                            
                    except Exception as e:
                        self._logger.error(f"Failed to execute cleanup action {action.target_path}: {e}")
                        cleanup_results['actions'].append({
                            'action': action.action_type,
                            'target': action.target_path,
                            'success': False,
                            'error': str(e)
                        })
                
                trace.output_result = {
                    'dry_run': dry_run,
                    'actions_executed': cleanup_results['actions_executed'],
                    'bytes_freed': cleanup_results['bytes_freed'],
                    'total_actions': len(safe_actions)
                }
                
            except Exception as e:
                self._logger.error(f"Cleanup execution failed: {e}")
                trace.output_result = {'error': str(e)}
            
            return cleanup_results
    
    def _execute_delete_action(self, action: CleanupAction, dry_run: bool) -> Dict[str, Any]:
        """Execute a delete cleanup action."""
        target_path = self.workspace_root / action.target_path
        
        if dry_run:
            return {
                'action': 'delete',
                'target': action.target_path,
                'success': True,
                'dry_run': True,
                'estimated_bytes_freed': action.estimated_savings_bytes
            }
        
        try:
            if target_path.is_dir():
                shutil.rmtree(target_path)
            else:
                target_path.unlink()
            
            return {
                'action': 'delete',
                'target': action.target_path,
                'success': True,
                'bytes_freed': action.estimated_savings_bytes
            }
        except Exception as e:
            return {
                'action': 'delete',
                'target': action.target_path,
                'success': False,
                'error': str(e)
            }
    
    def _execute_truncate_action(self, action: CleanupAction, dry_run: bool) -> Dict[str, Any]:
        """Execute a truncate cleanup action."""
        target_path = self.workspace_root / action.target_path
        
        if dry_run:
            return {
                'action': 'truncate',
                'target': action.target_path,
                'success': True,
                'dry_run': True,
                'estimated_bytes_freed': action.estimated_savings_bytes
            }
        
        try:
            if target_path.is_file():
                # Truncate file to last 1000 lines
                with open(target_path, 'r') as f:
                    lines = f.readlines()
                
                if len(lines) > 1000:
                    with open(target_path, 'w') as f:
                        f.writelines(lines[-1000:])
                    
                    return {
                        'action': 'truncate',
                        'target': action.target_path,
                        'success': True,
                        'bytes_freed': action.estimated_savings_bytes
                    }
            
            return {
                'action': 'truncate',
                'target': action.target_path,
                'success': False,
                'error': 'Not a file or too small to truncate'
            }
        except Exception as e:
            return {
                'action': 'truncate',
                'target': action.target_path,
                'success': False,
                'error': str(e)
            }
    
    def _get_directory_size(self, path: Path) -> int:
        """Get total size of directory in bytes."""
        total_size = 0
        try:
            for item in path.rglob('*'):
                if item.is_file():
                    try:
                        total_size += item.stat().st_size
                    except (OSError, PermissionError):
                        continue
        except (OSError, PermissionError):
            pass
        return total_size
    
    def _count_files_in_directory(self, path: Path) -> int:
        """Count total number of files in directory."""
        count = 0
        try:
            for item in path.rglob('*'):
                if item.is_file():
                    count += 1
        except (OSError, PermissionError):
            pass
        return count
    
    def _format_bytes(self, bytes_value: int) -> str:
        """Format bytes into human-readable string."""
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if bytes_value < 1024.0:
                return f"{bytes_value:.1f}{unit}"
            bytes_value /= 1024.0
        return f"{bytes_value:.1f}PB"


# Convenience functions
def analyze_workspace_disk_usage(workspace_root: Optional[str] = None) -> DiskSpaceReport:
    """
    Convenience function to analyze workspace disk usage.
    
    Args:
        workspace_root: Optional workspace root path
        
    Returns:
        DiskSpaceReport with analysis results
    """
    manager = DiskSpaceManager(workspace_root)
    return manager.analyze_disk_usage()


def execute_safe_workspace_cleanup(workspace_root: Optional[str] = None, dry_run: bool = True) -> Dict[str, Any]:
    """
    Convenience function to execute safe workspace cleanup.
    
    Args:
        workspace_root: Optional workspace root path
        dry_run: If True, only simulate cleanup
        
    Returns:
        Dict with cleanup results
    """
    manager = DiskSpaceManager(workspace_root)
    return manager.execute_safe_cleanup(dry_run)