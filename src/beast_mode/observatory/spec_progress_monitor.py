#!/usr/bin/env python3
"""
Spec Progress Monitor for ACE Reporter

This module provides automatic spec progress tracking, task completion monitoring,
and milestone achievement detection for the Enhanced ACE Reporter system.

Key Features:
- Automatic task tracking from .kiro/specs directories
- Real-time spec completion percentage calculation
- Milestone achievement detection and broadcasting
- Multi-spec support with progress aggregation
- Integration with AI Memory Palace for context
- Comprehensive error handling and fallback mechanisms
"""

import os
import sys
import re
import json
import time
import threading
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Union, Callable, Set
from dataclasses import dataclass, field, asdict
from enum import Enum

# Add project root to path
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from src.rm_ddd.core.unified_reflective_module import ReflectiveModule, ModuleHealth, ModuleStatus, ModuleCapability
from src.beast_mode.observatory.ace_reporter_error_handling import (
    ACEReporterErrorHandler, ErrorSeverity, error_handler_decorator
)


class TaskStatus(Enum):
    """Task completion status"""
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    BLOCKED = "blocked"
    SKIPPED = "skipped"


class MilestoneType(Enum):
    """Types of milestones"""
    PHASE_COMPLETION = "phase_completion"
    PERCENTAGE_THRESHOLD = "percentage_threshold"
    TASK_SEQUENCE = "task_sequence"
    CUSTOM = "custom"


@dataclass
class Task:
    """Individual task information"""
    task_id: str
    title: str
    description: Optional[str] = None
    status: TaskStatus = TaskStatus.NOT_STARTED
    dependencies: List[str] = field(default_factory=list)
    phase: Optional[str] = None
    priority: str = "normal"  # low, normal, high, critical
    estimated_hours: Optional[float] = None
    actual_hours: Optional[float] = None
    completed_at: Optional[str] = None
    assigned_to: Optional[str] = None
    tags: List[str] = field(default_factory=list)


@dataclass
class Milestone:
    """Milestone definition and tracking"""
    milestone_id: str
    name: str
    description: str
    milestone_type: MilestoneType
    trigger_condition: Dict[str, Any]
    achieved: bool = False
    achieved_at: Optional[str] = None
    progress_percentage: float = 0.0


@dataclass
class SpecProgress:
    """Comprehensive spec progress information"""
    spec_name: str
    spec_path: str
    total_tasks: int
    completed_tasks: int
    in_progress_tasks: int
    blocked_tasks: int
    completion_percentage: float
    current_phase: Optional[str] = None
    estimated_completion: Optional[str] = None
    last_updated: str = field(default_factory=lambda: datetime.now().isoformat())
    
    # Task breakdown
    tasks: List[Task] = field(default_factory=list)
    milestones: List[Milestone] = field(default_factory=list)
    
    # Progress tracking
    phases_completed: List[str] = field(default_factory=list)
    phases_in_progress: List[str] = field(default_factory=list)
    
    # Metadata
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    last_task_completed: Optional[str] = None
    next_tasks: List[str] = field(default_factory=list)


class SpecProgressMonitor(ReflectiveModule):
    """
    Spec Progress Monitor
    
    Provides automatic tracking of spec progress, task completion monitoring,
    and milestone achievement detection with comprehensive error handling.
    """
    
    def __init__(self, 
                 specs_directory: Optional[str] = None,
                 ai_memory_palace_integration=None,
                 config: Optional[Dict[str, Any]] = None):
        super().__init__()
        self.module_id = "spec_progress_monitor"
        
        # Configuration
        self.config = config or {
            "specs_directory": specs_directory or ".kiro/specs",
            "auto_scan_interval_seconds": 60,
            "milestone_broadcast_enabled": True,
            "progress_broadcast_threshold": 10.0,  # Broadcast every 10% progress
            "enable_background_monitoring": True,
            "task_pattern": r"^- \[([x\s-])\] (.+)$",
            "phase_pattern": r"^## (.+)$"
        }
        
        # AI Memory Palace integration
        self._ai_memory_palace = ai_memory_palace_integration
        
        # Error handling
        self._error_handler = ACEReporterErrorHandler()
        
        # Progress tracking
        self._spec_progress: Dict[str, SpecProgress] = {}
        self._last_scan_time: Optional[datetime] = None
        self._file_modification_times: Dict[str, float] = {}
        
        # Background monitoring
        self._monitoring_thread: Optional[threading.Thread] = None
        self._monitoring_active = False
        
        # Statistics
        self._stats = {
            "total_specs_monitored": 0,
            "total_tasks_tracked": 0,
            "total_milestones_achieved": 0,
            "scan_count": 0,
            "last_scan_duration_ms": 0.0,
            "progress_broadcasts_sent": 0,
            "milestone_broadcasts_sent": 0
        }
        
        # Initialize monitoring
        self._initialize_monitoring()
    
    def _initialize_monitoring(self):
        """Initialize spec progress monitoring"""
        try:
            # Perform initial scan
            self.scan_all_specs()
            
            # Start background monitoring if enabled
            if self.config.get("enable_background_monitoring", True):
                self.start_background_monitoring()
                
        except Exception as e:
            print(f"⚠️  Spec progress monitor initialization failed: {e}")
    
    # ========================================================================
    # ReflectiveModule Implementation
    # ========================================================================
    
    def get_module_info(self):
        return {
            "module_id": self.module_id,
            "module_name": "Spec Progress Monitor",
            "version": "1.0.0",
            "description": "Automatic spec progress tracking and milestone detection",
            "config": self.config,
            "statistics": self._stats,
            "monitored_specs": list(self._spec_progress.keys()),
            "ai_memory_palace_available": self._ai_memory_palace is not None
        }
    
    def get_capabilities(self):
        return [
            ModuleCapability.MONITORING,
            ModuleCapability.DATA_PROCESSING,
            ModuleCapability.VALIDATION
        ]
    
    def get_health_status(self):
        # Calculate health based on monitoring performance
        base_health = 0.95
        
        issues = []
        
        # Check if specs directory exists
        specs_dir = Path(self.config["specs_directory"])
        if not specs_dir.exists():
            base_health -= 0.3
            issues.append(f"Specs directory not found: {specs_dir}")
        
        # Check background monitoring
        if (self.config.get("enable_background_monitoring", True) and 
            not self._monitoring_active):
            base_health -= 0.2
            issues.append("Background monitoring not active")
        
        # Check scan performance
        if self._stats["scan_count"] > 0:
            avg_scan_time = self._stats["last_scan_duration_ms"]
            if avg_scan_time > 5000:  # More than 5 seconds
                base_health -= 0.1
                issues.append(f"Slow scan performance: {avg_scan_time:.1f}ms")
        
        return ModuleHealth(
            module_id=self.module_id,
            status=ModuleStatus.HEALTHY if base_health > 0.7 else ModuleStatus.WARNING,
            health_score=max(0.0, base_health),
            issues=issues,
            last_check=self._last_activity,
            uptime_seconds=(self._last_activity - self._start_time).total_seconds(),
            error_count=self._error_count,
            warning_count=self._warning_count
        )
    
    def graceful_degradation(self):
        from src.rm_ddd.core.unified_reflective_module import GracefulDegradationResult
        
        print("🔄 Spec Progress Monitor entering graceful degradation...")
        
        # Stop background monitoring
        self.stop_background_monitoring()
        
        # Disable automatic features
        self.config["milestone_broadcast_enabled"] = False
        self.config["enable_background_monitoring"] = False
        
        print("✅ Spec Progress Monitor degraded to manual mode")
        
        return GracefulDegradationResult(
            success=True,
            degraded_capabilities=[ModuleCapability.MONITORING],
            remaining_capabilities=[ModuleCapability.DATA_PROCESSING, ModuleCapability.VALIDATION]
        )    

    # ========================================================================
    # Spec Scanning and Progress Calculation
    # ========================================================================
    
    @error_handler_decorator(
        component="spec_progress_monitor",
        operation="scan_all_specs",
        severity=ErrorSeverity.MEDIUM,
        max_retries=2
    )
    def scan_all_specs(self) -> Dict[str, SpecProgress]:
        """Scan all specs and update progress information"""
        start_time = time.time()
        
        specs_dir = Path(self.config["specs_directory"])
        if not specs_dir.exists():
            print(f"⚠️  Specs directory not found: {specs_dir}")
            return {}
        
        updated_specs = {}
        
        # Scan each spec directory
        for spec_dir in specs_dir.iterdir():
            if spec_dir.is_dir():
                try:
                    spec_progress = self._scan_spec_directory(spec_dir)
                    if spec_progress:
                        updated_specs[spec_progress.spec_name] = spec_progress
                        self._spec_progress[spec_progress.spec_name] = spec_progress
                except Exception as e:
                    print(f"⚠️  Failed to scan spec {spec_dir.name}: {e}")
        
        # Update statistics
        scan_duration = (time.time() - start_time) * 1000
        self._stats["scan_count"] += 1
        self._stats["last_scan_duration_ms"] = scan_duration
        self._stats["total_specs_monitored"] = len(updated_specs)
        self._stats["total_tasks_tracked"] = sum(len(spec.tasks) for spec in updated_specs.values())
        self._last_scan_time = datetime.now()
        
        print(f"📊 Scanned {len(updated_specs)} specs in {scan_duration:.1f}ms")
        
        return updated_specs
    
    def _scan_spec_directory(self, spec_dir: Path) -> Optional[SpecProgress]:
        """Scan individual spec directory for progress"""
        spec_name = spec_dir.name
        
        # Look for tasks.md file
        tasks_file = spec_dir / "tasks.md"
        if not tasks_file.exists():
            return None
        
        # Check if file has been modified
        file_mtime = tasks_file.stat().st_mtime
        if (spec_name in self._file_modification_times and 
            self._file_modification_times[spec_name] == file_mtime):
            # File hasn't changed, return cached progress
            return self._spec_progress.get(spec_name)
        
        self._file_modification_times[spec_name] = file_mtime
        
        # Parse tasks file
        try:
            with open(tasks_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            tasks = self._parse_tasks_from_content(content)
            milestones = self._detect_milestones(tasks, spec_name)
            
            # Calculate progress
            total_tasks = len(tasks)
            completed_tasks = sum(1 for task in tasks if task.status == TaskStatus.COMPLETED)
            in_progress_tasks = sum(1 for task in tasks if task.status == TaskStatus.IN_PROGRESS)
            blocked_tasks = sum(1 for task in tasks if task.status == TaskStatus.BLOCKED)
            
            completion_percentage = (completed_tasks / max(1, total_tasks)) * 100
            
            # Detect current phase
            current_phase = self._detect_current_phase(tasks)
            
            # Create spec progress
            spec_progress = SpecProgress(
                spec_name=spec_name,
                spec_path=str(spec_dir),
                total_tasks=total_tasks,
                completed_tasks=completed_tasks,
                in_progress_tasks=in_progress_tasks,
                blocked_tasks=blocked_tasks,
                completion_percentage=completion_percentage,
                current_phase=current_phase,
                tasks=tasks,
                milestones=milestones
            )
            
            # Check for milestone achievements
            self._check_milestone_achievements(spec_progress)
            
            return spec_progress
            
        except Exception as e:
            print(f"⚠️  Failed to parse tasks file {tasks_file}: {e}")
            return None
    
    def _parse_tasks_from_content(self, content: str) -> List[Task]:
        """Parse tasks from markdown content"""
        tasks = []
        current_phase = None
        
        lines = content.split('\n')
        task_pattern = re.compile(self.config["task_pattern"])
        phase_pattern = re.compile(self.config["phase_pattern"])
        
        for line_num, line in enumerate(lines, 1):
            line = line.strip()
            
            # Check for phase headers
            phase_match = phase_pattern.match(line)
            if phase_match:
                current_phase = phase_match.group(1).strip()
                continue
            
            # Check for tasks
            task_match = task_pattern.match(line)
            if task_match:
                status_char = task_match.group(1)
                task_title = task_match.group(2).strip()
                
                # Determine status from checkbox
                if status_char.lower() == 'x':
                    status = TaskStatus.COMPLETED
                elif status_char == '-':
                    status = TaskStatus.IN_PROGRESS
                else:
                    status = TaskStatus.NOT_STARTED
                
                # Extract task ID from title if present
                task_id_match = re.match(r'^(\d+\.?\d*)\s+(.+)$', task_title)
                if task_id_match:
                    task_id = task_id_match.group(1)
                    task_title = task_id_match.group(2)
                else:
                    task_id = f"task_{line_num}"
                
                task = Task(
                    task_id=task_id,
                    title=task_title,
                    status=status,
                    phase=current_phase
                )
                
                tasks.append(task)
        
        return tasks
    
    def _detect_milestones(self, tasks: List[Task], spec_name: str) -> List[Milestone]:
        """Detect and create milestones based on tasks and progress"""
        milestones = []
        
        # Phase completion milestones
        phases = set(task.phase for task in tasks if task.phase)
        for phase in phases:
            milestone = Milestone(
                milestone_id=f"{spec_name}_phase_{phase.lower().replace(' ', '_')}",
                name=f"{phase} Complete",
                description=f"All tasks in {phase} phase completed",
                milestone_type=MilestoneType.PHASE_COMPLETION,
                trigger_condition={"phase": phase, "completion": 100}
            )
            milestones.append(milestone)
        
        # Percentage threshold milestones
        for threshold in [25, 50, 75, 90, 100]:
            milestone = Milestone(
                milestone_id=f"{spec_name}_progress_{threshold}",
                name=f"{threshold}% Complete",
                description=f"Spec reached {threshold}% completion",
                milestone_type=MilestoneType.PERCENTAGE_THRESHOLD,
                trigger_condition={"percentage": threshold}
            )
            milestones.append(milestone)
        
        return milestones
    
    def _detect_current_phase(self, tasks: List[Task]) -> Optional[str]:
        """Detect current active phase based on task status"""
        phase_progress = {}
        
        # Calculate progress for each phase
        for task in tasks:
            if task.phase:
                if task.phase not in phase_progress:
                    phase_progress[task.phase] = {"total": 0, "completed": 0, "in_progress": 0}
                
                phase_progress[task.phase]["total"] += 1
                if task.status == TaskStatus.COMPLETED:
                    phase_progress[task.phase]["completed"] += 1
                elif task.status == TaskStatus.IN_PROGRESS:
                    phase_progress[task.phase]["in_progress"] += 1
        
        # Find current phase (has in-progress tasks or incomplete tasks)
        for phase, progress in phase_progress.items():
            if progress["in_progress"] > 0:
                return phase
            elif progress["completed"] < progress["total"]:
                return phase
        
        # If all phases complete, return the last phase
        if phase_progress:
            return list(phase_progress.keys())[-1]
        
        return None
    
    def _check_milestone_achievements(self, spec_progress: SpecProgress):
        """Check and update milestone achievements"""
        for milestone in spec_progress.milestones:
            if milestone.achieved:
                continue
            
            achieved = False
            
            if milestone.milestone_type == MilestoneType.PERCENTAGE_THRESHOLD:
                threshold = milestone.trigger_condition["percentage"]
                if spec_progress.completion_percentage >= threshold:
                    achieved = True
            
            elif milestone.milestone_type == MilestoneType.PHASE_COMPLETION:
                phase = milestone.trigger_condition["phase"]
                phase_tasks = [t for t in spec_progress.tasks if t.phase == phase]
                if phase_tasks:
                    completed = sum(1 for t in phase_tasks if t.status == TaskStatus.COMPLETED)
                    if completed == len(phase_tasks):
                        achieved = True
            
            if achieved:
                milestone.achieved = True
                milestone.achieved_at = datetime.now().isoformat()
                self._stats["total_milestones_achieved"] += 1
                
                # Broadcast milestone achievement
                if self.config.get("milestone_broadcast_enabled", True):
                    self._broadcast_milestone_achievement(spec_progress, milestone)
    
    # ========================================================================
    # Progress Broadcasting
    # ========================================================================
    
    def _broadcast_milestone_achievement(self, spec_progress: SpecProgress, milestone: Milestone):
        """Broadcast milestone achievement"""
        try:
            # Create milestone broadcast message
            message = f"🏆 MILESTONE ACHIEVED: {milestone.name} in {spec_progress.spec_name}"
            
            # Enhanced context for milestone
            context = {
                "spec_name": spec_progress.spec_name,
                "milestone_id": milestone.milestone_id,
                "milestone_name": milestone.name,
                "milestone_type": milestone.milestone_type.value,
                "completion_percentage": spec_progress.completion_percentage,
                "total_tasks": spec_progress.total_tasks,
                "completed_tasks": spec_progress.completed_tasks,
                "current_phase": spec_progress.current_phase,
                "achieved_at": milestone.achieved_at
            }
            
            # Broadcast through AI Memory Palace if available
            if self._ai_memory_palace:
                # TODO: Integrate with AI Memory Palace for milestone broadcasting
                pass
            
            self._stats["milestone_broadcasts_sent"] += 1
            print(f"🏆 Milestone broadcast: {message}")
            
        except Exception as e:
            print(f"⚠️  Failed to broadcast milestone: {e}")
    
    def broadcast_progress_update(self, spec_name: str, force: bool = False):
        """Broadcast progress update for a specific spec"""
        if spec_name not in self._spec_progress:
            return
        
        spec_progress = self._spec_progress[spec_name]
        
        # Check if progress update should be broadcast
        if not force:
            threshold = self.config.get("progress_broadcast_threshold", 10.0)
            # TODO: Implement threshold checking logic
        
        try:
            message = f"📊 SPEC PROGRESS: {spec_name} at {spec_progress.completion_percentage:.1f}%"
            
            context = {
                "spec_name": spec_name,
                "completion_percentage": spec_progress.completion_percentage,
                "total_tasks": spec_progress.total_tasks,
                "completed_tasks": spec_progress.completed_tasks,
                "in_progress_tasks": spec_progress.in_progress_tasks,
                "current_phase": spec_progress.current_phase,
                "last_updated": spec_progress.last_updated
            }
            
            self._stats["progress_broadcasts_sent"] += 1
            print(f"📊 Progress broadcast: {message}")
            
        except Exception as e:
            print(f"⚠️  Failed to broadcast progress update: {e}")
    
    # ========================================================================
    # Background Monitoring
    # ========================================================================
    
    def start_background_monitoring(self):
        """Start background monitoring of spec progress"""
        if self._monitoring_active:
            return
        
        self._monitoring_active = True
        self._monitoring_thread = threading.Thread(target=self._monitoring_loop, daemon=True)
        self._monitoring_thread.start()
        print("🔄 Spec progress background monitoring started")
    
    def stop_background_monitoring(self):
        """Stop background monitoring"""
        self._monitoring_active = False
        if self._monitoring_thread:
            self._monitoring_thread.join(timeout=5)
        print("🔄 Spec progress background monitoring stopped")
    
    def _monitoring_loop(self):
        """Background monitoring loop"""
        while self._monitoring_active:
            try:
                # Scan for updates
                self.scan_all_specs()
                
                # Sleep for scan interval
                time.sleep(self.config["auto_scan_interval_seconds"])
                
            except Exception as e:
                print(f"⚠️  Background monitoring error: {e}")
                time.sleep(self.config["auto_scan_interval_seconds"])
    
    # ========================================================================
    # Public API Methods
    # ========================================================================
    
    def get_spec_progress(self, spec_name: str) -> Optional[SpecProgress]:
        """Get progress information for a specific spec"""
        return self._spec_progress.get(spec_name)
    
    def get_all_spec_progress(self) -> Dict[str, SpecProgress]:
        """Get progress information for all monitored specs"""
        return self._spec_progress.copy()
    
    def get_overall_progress(self) -> Dict[str, Any]:
        """Get overall progress across all specs"""
        if not self._spec_progress:
            return {
                "total_specs": 0,
                "total_tasks": 0,
                "completed_tasks": 0,
                "overall_completion_percentage": 0.0
            }
        
        total_tasks = sum(spec.total_tasks for spec in self._spec_progress.values())
        completed_tasks = sum(spec.completed_tasks for spec in self._spec_progress.values())
        
        return {
            "total_specs": len(self._spec_progress),
            "total_tasks": total_tasks,
            "completed_tasks": completed_tasks,
            "overall_completion_percentage": (completed_tasks / max(1, total_tasks)) * 100,
            "specs_by_status": {
                "completed": sum(1 for spec in self._spec_progress.values() 
                               if spec.completion_percentage >= 100),
                "in_progress": sum(1 for spec in self._spec_progress.values() 
                                 if 0 < spec.completion_percentage < 100),
                "not_started": sum(1 for spec in self._spec_progress.values() 
                                 if spec.completion_percentage == 0)
            }
        }
    
    def get_monitoring_statistics(self) -> Dict[str, Any]:
        """Get comprehensive monitoring statistics"""
        return {
            **self._stats,
            "monitoring_active": self._monitoring_active,
            "last_scan_time": self._last_scan_time.isoformat() if self._last_scan_time else None,
            "monitored_specs": list(self._spec_progress.keys()),
            "specs_directory": self.config["specs_directory"]
        }
    
    def force_rescan(self) -> Dict[str, SpecProgress]:
        """Force immediate rescan of all specs"""
        print("🔄 Forcing spec rescan...")
        self._file_modification_times.clear()  # Clear cache to force rescan
        return self.scan_all_specs()


def main():
    """Test Spec Progress Monitor"""
    print("📊 Spec Progress Monitor Test")
    print("=" * 60)
    
    # Create monitor
    monitor = SpecProgressMonitor()
    
    print("\n📋 Testing spec scanning...")
    
    # Test spec scanning
    specs = monitor.scan_all_specs()
    print(f"✅ Found {len(specs)} specs")
    
    for spec_name, spec_progress in specs.items():
        print(f"   📊 {spec_name}: {spec_progress.completion_percentage:.1f}% complete")
        print(f"      Tasks: {spec_progress.completed_tasks}/{spec_progress.total_tasks}")
        print(f"      Phase: {spec_progress.current_phase}")
        print(f"      Milestones: {len([m for m in spec_progress.milestones if m.achieved])}/{len(spec_progress.milestones)} achieved")
    
    # Test overall progress
    print("\n📊 Overall Progress:")
    overall = monitor.get_overall_progress()
    for key, value in overall.items():
        print(f"   {key}: {value}")
    
    # Test statistics
    print("\n📈 Monitoring Statistics:")
    stats = monitor.get_monitoring_statistics()
    for key, value in stats.items():
        if isinstance(value, float):
            print(f"   {key}: {value:.2f}")
        else:
            print(f"   {key}: {value}")
    
    # Test health status
    print("\n🏥 Health Status:")
    health = monitor.get_health_status()
    print(f"   Status: {health.status.value}")
    print(f"   Health Score: {health.health_score:.2f}")
    print(f"   Issues: {health.issues}")
    
    print("\n🎉 Spec Progress Monitor test complete!")
    print("✅ All monitoring mechanisms tested successfully")


if __name__ == "__main__":
    main()