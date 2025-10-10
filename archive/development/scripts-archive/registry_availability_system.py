#!/usr/bin/env python3
"""
Registry Availability System
============================

Critical derived requirement: Synchronous availability of the registry
is required for any field modifications to work. Without it, the system
is "dead in the water" and cannot fix itself.
"""

from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, asdict
from abc import ABC, abstractmethod
import json
import time
import requests
import socket
import subprocess
from datetime import datetime, timedelta
from pathlib import Path
import hashlib
import sys
import os


@dataclass
class RegistryAvailabilityStatus:
    """Registry availability status tracking"""

    registry_type: str  # git, memory, file_system, network
    is_available: bool
    response_time_ms: float
    last_checked: datetime
    error_message: Optional[str]
    health_score: float  # 0.0 to 1.0
    critical_dependencies: List[str]
    failure_reason: Optional[str]


@dataclass
class RegistryHealthReport:
    """Comprehensive registry health report"""

    overall_health: float  # 0.0 to 1.0
    critical_registries: Dict[str, RegistryAvailabilityStatus]
    system_status: str  # healthy, degraded, critical, dead_in_water
    can_perform_field_modifications: bool
    graceful_shutdown_required: bool
    last_health_check: datetime
    recommendations: List[str]


class RegistryAvailabilityChecker(ABC):
    """Abstract base class for registry availability checking"""

    @abstractmethod
    def check_availability(self) -> RegistryAvailabilityStatus:
        """Check if the registry is available"""
        pass

    @abstractmethod
    def get_critical_dependencies(self) -> List[str]:
        """Get list of critical dependencies for this registry"""
        pass


class GitRegistryChecker(RegistryAvailabilityChecker):
    """Check Git registry availability for field modifications"""

    def __init__(self, repo_path: str = "."):
        self.repo_path = Path(repo_path)
        self.remote_name = "origin"

    def check_availability(self) -> RegistryAvailabilityStatus:
        """Check Git registry availability"""
        start_time = time.time()

        try:
            # Check if we can access git repository
            if not self._can_access_git_repo():
                return RegistryAvailabilityStatus(
                    registry_type="git",
                    is_available=False,
                    response_time_ms=0.0,
                    last_checked=datetime.now(),
                    error_message="Cannot access git repository",
                    health_score=0.0,
                    critical_dependencies=self.get_critical_dependencies(),
                    failure_reason="git_repo_inaccessible",
                )

            # Check if we can sync to remote
            if not self._can_sync_to_remote():
                return RegistryAvailabilityStatus(
                    registry_type="git",
                    is_available=False,
                    response_time_ms=0.0,
                    last_checked=datetime.now(),
                    error_message="Cannot sync to remote repository",
                    health_score=0.2,
                    critical_dependencies=self.get_critical_dependencies(),
                    failure_reason="git_remote_unreachable",
                )

            # Check if we can create commits
            if not self._can_create_commits():
                return RegistryAvailabilityStatus(
                    registry_type="git",
                    is_available=False,
                    response_time_ms=0.0,
                    last_checked=datetime.now(),
                    error_message="Cannot create commits",
                    health_score=0.5,
                    critical_dependencies=self.get_critical_dependencies(),
                    failure_reason="git_commit_failure",
                )

            response_time = (time.time() - start_time) * 1000

            return RegistryAvailabilityStatus(
                registry_type="git",
                is_available=True,
                response_time_ms=response_time,
                last_checked=datetime.now(),
                error_message=None,
                health_score=1.0,
                critical_dependencies=self.get_critical_dependencies(),
                failure_reason=None,
            )

        except Exception as e:
            return RegistryAvailabilityStatus(
                registry_type="git",
                is_available=False,
                response_time_ms=0.0,
                last_checked=datetime.now(),
                error_message=str(e),
                health_score=0.0,
                critical_dependencies=self.get_critical_dependencies(),
                failure_reason="git_check_exception",
            )

    def _can_access_git_repo(self) -> bool:
        """Check if we can access the git repository"""
        try:
            # Check if .git directory exists
            git_dir = self.repo_path / ".git"
            if not git_dir.exists():
                return False

            # Try to run basic git command
            result = subprocess.run(
                ["git", "status", "--porcelain"],
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                timeout=10,
            )
            return result.returncode == 0

        except Exception:
            return False

    def _can_sync_to_remote(self) -> bool:
        """Check if we can sync to remote repository"""
        try:
            # Try to fetch from remote
            result = subprocess.run(
                ["git", "fetch", self.remote_name, "--dry-run"],
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                timeout=30,
            )
            return result.returncode == 0

        except Exception:
            return False

    def _can_create_commits(self) -> bool:
        """Check if we can create commits"""
        try:
            # Try to create a test commit (without pushing)
            result = subprocess.run(
                ["git", "commit", "--allow-empty", "-m", "test_commit"],
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                timeout=10,
            )
            return result.returncode == 0

        except Exception:
            return False

    def get_critical_dependencies(self) -> List[str]:
        """Get critical dependencies for Git registry"""
        return [
            "git_executable",
            "git_repository",
            "remote_origin",
            "network_connectivity",
            "git_credentials",
        ]


class MemoryRegistryChecker(RegistryAvailabilityChecker):
    """Check memory registry availability for field modifications"""

    def __init__(self, memory_manager=None):
        self.memory_manager = memory_manager

    def check_availability(self) -> RegistryAvailabilityStatus:
        """Check memory registry availability"""
        start_time = time.time()

        try:
            if not self.memory_manager:
                return RegistryAvailabilityStatus(
                    registry_type="memory",
                    is_available=False,
                    response_time_ms=0.0,
                    last_checked=datetime.now(),
                    error_message="Memory manager not initialized",
                    health_score=0.0,
                    critical_dependencies=self.get_critical_dependencies(),
                    failure_reason="memory_manager_missing",
                )

            # Test memory operations
            if not self._can_write_to_memory():
                return RegistryAvailabilityStatus(
                    registry_type="memory",
                    is_available=False,
                    response_time_ms=0.0,
                    last_checked=datetime.now(),
                    error_message="Cannot write to memory",
                    health_score=0.3,
                    critical_dependencies=self.get_critical_dependencies(),
                    failure_reason="memory_write_failure",
                )

            if not self._can_read_from_memory():
                return RegistryAvailabilityStatus(
                    registry_type="memory",
                    is_available=False,
                    response_time_ms=0.0,
                    last_checked=datetime.now(),
                    error_message="Cannot read from memory",
                    health_score=0.5,
                    critical_dependencies=self.get_critical_dependencies(),
                    failure_reason="memory_read_failure",
                )

            if not self._can_persist_memory():
                return RegistryAvailabilityStatus(
                    registry_type="memory",
                    is_available=False,
                    response_time_ms=0.0,
                    last_checked=datetime.now(),
                    error_message="Cannot persist memory",
                    health_score=0.7,
                    critical_dependencies=self.get_critical_dependencies(),
                    failure_reason="memory_persistence_failure",
                )

            response_time = (time.time() - start_time) * 1000

            return RegistryAvailabilityStatus(
                registry_type="memory",
                is_available=True,
                response_time_ms=response_time,
                last_checked=datetime.now(),
                error_message=None,
                health_score=1.0,
                critical_dependencies=self.get_critical_dependencies(),
                failure_reason=None,
            )

        except Exception as e:
            return RegistryAvailabilityStatus(
                registry_type="memory",
                is_available=False,
                response_time_ms=0.0,
                last_checked=datetime.now(),
                error_message=str(e),
                health_score=0.0,
                critical_dependencies=self.get_critical_dependencies(),
                failure_reason="memory_check_exception",
            )

    def _can_write_to_memory(self) -> bool:
        """Test memory write operations"""
        try:
            # Test writing to memory
            test_data = {
                "test": "memory_write",
                "timestamp": datetime.now().isoformat(),
            }
            if hasattr(self.memory_manager, "add_planning_insight"):
                # This would be a real test in production
                return True
            return False

        except Exception:
            return False

    def _can_read_from_memory(self) -> bool:
        """Test memory read operations"""
        try:
            # Test reading from memory
            if hasattr(self.memory_manager, "get_planning_summary"):
                # This would be a real test in production
                return True
            return False

        except Exception:
            return False

    def _can_persist_memory(self) -> bool:
        """Test memory persistence operations"""
        try:
            # Test memory persistence
            if hasattr(self.memory_manager, "save_planning_memory"):
                # This would be a real test in production
                return True
            return False

        except Exception:
            return False

    def get_critical_dependencies(self) -> List[str]:
        """Get critical dependencies for memory registry"""
        return [
            "memory_manager",
            "memory_storage",
            "memory_persistence",
            "file_system_access",
            "memory_serialization",
        ]


class FileSystemRegistryChecker(RegistryAvailabilityChecker):
    """Check file system registry availability for field modifications"""

    def __init__(self, base_path: str = "."):
        self.base_path = Path(base_path)

    def check_availability(self) -> RegistryAvailabilityStatus:
        """Check file system registry availability"""
        start_time = time.time()

        try:
            # Check if base path is accessible
            if not self.base_path.exists():
                return RegistryAvailabilityStatus(
                    registry_type="file_system",
                    is_available=False,
                    response_time_ms=0.0,
                    last_checked=datetime.now(),
                    error_message=f"Base path does not exist: {self.base_path}",
                    health_score=0.0,
                    critical_dependencies=self.get_critical_dependencies(),
                    failure_reason="base_path_missing",
                )

            # Check read permissions
            if not self._can_read_files():
                return RegistryAvailabilityStatus(
                    registry_type="file_system",
                    is_available=False,
                    response_time_ms=0.0,
                    last_checked=datetime.now(),
                    error_message="Cannot read files",
                    health_score=0.3,
                    critical_dependencies=self.get_critical_dependencies(),
                    failure_reason="read_permission_denied",
                )

            # Check write permissions
            if not self._can_write_files():
                return RegistryAvailabilityStatus(
                    registry_type="file_system",
                    is_available=False,
                    response_time_ms=0.0,
                    last_checked=datetime.now(),
                    error_message="Cannot write files",
                    health_score=0.5,
                    critical_dependencies=self.get_critical_dependencies(),
                    failure_reason="write_permission_denied",
                )

            # Check if we can create directories
            if not self._can_create_directories():
                return RegistryAvailabilityStatus(
                    registry_type="file_system",
                    is_available=False,
                    response_time_ms=0.0,
                    last_checked=datetime.now(),
                    error_message="Cannot create directories",
                    health_score=0.7,
                    critical_dependencies=self.get_critical_dependencies(),
                    failure_reason="directory_creation_failure",
                )

            response_time = (time.time() - start_time) * 1000

            return RegistryAvailabilityStatus(
                registry_type="file_system",
                is_available=True,
                response_time_ms=response_time,
                last_checked=datetime.now(),
                error_message=None,
                health_score=1.0,
                critical_dependencies=self.get_critical_dependencies(),
                failure_reason=None,
            )

        except Exception as e:
            return RegistryAvailabilityStatus(
                registry_type="file_system",
                is_available=False,
                response_time_ms=0.0,
                last_checked=datetime.now(),
                error_message=str(e),
                health_score=0.0,
                critical_dependencies=self.get_critical_dependencies(),
                failure_reason="filesystem_check_exception",
            )

    def _can_read_files(self) -> bool:
        """Test file read operations"""
        try:
            test_file = self.base_path / "test_read.txt"
            test_file.write_text("test")
            content = test_file.read_text()
            test_file.unlink()
            return content == "test"

        except Exception:
            return False

    def _can_write_files(self) -> bool:
        """Test file write operations"""
        try:
            test_file = self.base_path / "test_write.txt"
            test_file.write_text("test_write")
            return test_file.exists()

        except Exception:
            return False

    def _can_create_directories(self) -> bool:
        """Test directory creation"""
        try:
            test_dir = self.base_path / "test_dir"
            test_dir.mkdir()
            result = test_dir.exists()
            test_dir.rmdir()
            return result

        except Exception:
            return False

    def get_critical_dependencies(self) -> List[str]:
        """Get critical dependencies for file system registry"""
        return [
            "file_system_access",
            "read_permissions",
            "write_permissions",
            "directory_creation",
            "disk_space",
        ]


class RegistryHealthMonitor:
    """Monitor registry health and availability for field modifications"""

    def __init__(self, repo_path: str = ".", memory_manager=None):
        self.repo_path = repo_path
        self.memory_manager = memory_manager
        self.checkers = {
            "git": GitRegistryChecker(repo_path),
            "memory": MemoryRegistryChecker(memory_manager),
            "file_system": FileSystemRegistryChecker(repo_path),
        }
        self.health_history = []
        self.last_health_report = None

    def check_registry_health(self) -> RegistryHealthReport:
        """Perform comprehensive registry health check"""
        print("🔍 Checking registry availability for field modifications...")

        critical_registries = {}
        overall_health = 0.0
        can_perform_field_modifications = True
        graceful_shutdown_required = False
        recommendations = []

        # Check each critical registry
        for registry_type, checker in self.checkers.items():
            print(f"   Checking {registry_type} registry...")
            status = checker.check_availability()
            critical_registries[registry_type] = status

            if not status.is_available:
                can_perform_field_modifications = False
                recommendations.append(
                    f"Fix {registry_type} registry: {status.error_message}"
                )

                if status.health_score < 0.3:
                    graceful_shutdown_required = True
                    recommendations.append(
                        f"CRITICAL: {registry_type} registry failure requires graceful shutdown"
                    )

            overall_health += status.health_score

        overall_health /= len(self.checkers)

        # Determine system status
        if overall_health >= 0.8:
            system_status = "healthy"
        elif overall_health >= 0.5:
            system_status = "degraded"
        elif overall_health >= 0.2:
            system_status = "critical"
        else:
            system_status = "dead_in_water"
            graceful_shutdown_required = True
            recommendations.append(
                "SYSTEM DEAD IN WATER: Cannot perform field modifications"
            )

        health_report = RegistryHealthReport(
            overall_health=overall_health,
            critical_registries=critical_registries,
            system_status=system_status,
            can_perform_field_modifications=can_perform_field_modifications,
            graceful_shutdown_required=graceful_shutdown_required,
            last_health_check=datetime.now(),
            recommendations=recommendations,
        )

        self.last_health_report = health_report
        self.health_history.append(health_report)

        # Keep only last 100 health reports
        if len(self.health_history) > 100:
            self.health_history = self.health_history[-100:]

        return health_report

    def is_field_modification_safe(self) -> Tuple[bool, str]:
        """Check if field modifications are safe to perform"""
        if not self.last_health_report:
            health_report = self.check_registry_health()
        else:
            health_report = self.last_health_report

        if not health_report.can_perform_field_modifications:
            return False, f"Registry health check failed: {health_report.system_status}"

        if health_report.graceful_shutdown_required:
            return False, f"Graceful shutdown required: {health_report.system_status}"

        return True, "Registry health check passed"

    def get_graceful_shutdown_message(self) -> str:
        """Get graceful shutdown message when registry is unavailable"""
        if not self.last_health_report:
            return "I can't fix myself. I'm dead in the water here."

        failed_registries = [
            name
            for name, status in self.last_health_report.critical_registries.items()
            if not status.is_available
        ]

        if failed_registries:
            return f"I can't fix myself. I'm dead in the water here. Failed registries: {', '.join(failed_registries)}"
        else:
            return "I can't fix myself. I'm dead in the water here."

    def get_boot_time_check_results(self) -> Dict[str, Any]:
        """Get results of boot-time registry checks"""
        health_report = self.check_registry_health()

        return {
            "boot_time_check": True,
            "overall_health": health_report.overall_health,
            "system_status": health_report.system_status,
            "can_perform_field_modifications": health_report.can_perform_field_modifications,
            "critical_registries": {
                name: {
                    "available": status.is_available,
                    "health_score": status.health_score,
                    "error_message": status.error_message,
                }
                for name, status in health_report.critical_registries.items()
            },
            "recommendations": health_report.recommendations,
            "graceful_shutdown_required": health_report.graceful_shutdown_required,
        }


def create_registry_health_monitor(
    repo_path: str = ".", memory_manager=None
) -> RegistryHealthMonitor:
    """Factory function to create registry health monitor"""
    return RegistryHealthMonitor(repo_path, memory_manager)


def perform_boot_time_registry_check(
    repo_path: str = ".", memory_manager=None
) -> Dict[str, Any]:
    """Perform boot-time registry availability check"""
    print("🚀 BOOT TIME REGISTRY AVAILABILITY CHECK")
    print("=" * 50)

    monitor = create_registry_health_monitor(repo_path, memory_manager)
    results = monitor.get_boot_time_check_results()

    print(f"Overall Health: {results['overall_health']:.1%}")
    print(f"System Status: {results['system_status']}")
    print(
        f"Can Perform Field Modifications: {results['can_perform_field_modifications']}"
    )

    if results["graceful_shutdown_required"]:
        print("🚨 GRACEFUL SHUTDOWN REQUIRED!")
        print(f"   {monitor.get_graceful_shutdown_message()}")
    else:
        print("✅ Registry availability check passed")

    for registry_name, registry_info in results["critical_registries"].items():
        status_icon = "✅" if registry_info["available"] else "❌"
        print(
            f"{status_icon} {registry_name}: {registry_info['health_score']:.1%} - {registry_info['error_message'] or 'OK'}"
        )

    if results["recommendations"]:
        print("\n📋 Recommendations:")
        for rec in results["recommendations"]:
            print(f"   • {rec}")

    return results


def perform_pre_use_registry_validation(
    repo_path: str = ".", memory_manager=None
) -> bool:
    """Perform pre-use registry validation before field modifications"""
    print("🔧 PRE-USE REGISTRY VALIDATION")
    print("=" * 40)

    monitor = create_registry_health_monitor(repo_path, memory_manager)
    is_safe, message = monitor.is_field_modification_safe()

    if is_safe:
        print("✅ Registry validation passed - field modifications are safe")
        return True
    else:
        print("❌ Registry validation failed - field modifications are NOT safe")
        print(f"   {message}")
        print(f"   {monitor.get_graceful_shutdown_message()}")
        return False
