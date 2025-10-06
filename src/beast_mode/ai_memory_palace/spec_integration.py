"""
Spec Workflow Integration for AI Memory Palace.

Connects the context system to spec creation, update, and completion tracking.
Provides automatic context updates when tasks are marked complete and
implements spec state synchronization with context registry.
"""

class SystemDiscovery:
    """Simple system discovery for spec integration"""
    
    @staticmethod
    def discover_project_structure():
        """Discover basic project structure"""
        return {
            'project_root': '.',
            'specs_dir': '.kiro/specs',
            'src_dir': 'src'
        }

import json
import os
import re
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple, Set
from pathlib import Path
import uuid
import hashlib
import threading
import time
from dataclasses import dataclass, field
from enum import Enum

from src.beast_mode.core.beastly_module import BeastlyModule
from .models import SessionContext, ContextEvent, ContextEventType, Decision, WorkItem
from .context_manager import ContextManager
from .context_registry import ContextRegistry
from .multi_project_manager import MultiProjectContextManager


class SpecPhase(Enum):
    """Spec development phases"""
    REQUIREMENTS = "requirements"
    DESIGN = "design"
    TASKS = "tasks"
    IMPLEMENTATION = "implementation"
    COMPLETED = "completed"


class TaskStatus(Enum):
    """Task completion status"""
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    BLOCKED = "blocked"
    CANCELLED = "cancelled"


@dataclass
class SpecState:
    """State of a specification"""
    spec_name: str
    spec_path: Path
    current_phase: SpecPhase
    created: datetime
    last_updated: datetime
    requirements_complete: bool = False
    design_complete: bool = False
    tasks_complete: bool = False
    implementation_progress: float = 0.0
    total_tasks: int = 0
    completed_tasks: int = 0
    blocked_tasks: int = 0
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "spec_name": self.spec_name,
            "spec_path": str(self.spec_path),
            "current_phase": self.current_phase.value,
            "created": self.created.isoformat(),
            "last_updated": self.last_updated.isoformat(),
            "requirements_complete": self.requirements_complete,
            "design_complete": self.design_complete,
            "tasks_complete": self.tasks_complete,
            "implementation_progress": self.implementation_progress,
            "total_tasks": self.total_tasks,
            "completed_tasks": self.completed_tasks,
            "blocked_tasks": self.blocked_tasks
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'SpecState':
        return cls(
            spec_name=data["spec_name"],
            spec_path=Path(data["spec_path"]),
            current_phase=SpecPhase(data["current_phase"]),
            created=datetime.fromisoformat(data["created"]),
            last_updated=datetime.fromisoformat(data["last_updated"]),
            requirements_complete=data.get("requirements_complete", False),
            design_complete=data.get("design_complete", False),
            tasks_complete=data.get("tasks_complete", False),
            implementation_progress=data.get("implementation_progress", 0.0),
            total_tasks=data.get("total_tasks", 0),
            completed_tasks=data.get("completed_tasks", 0),
            blocked_tasks=data.get("blocked_tasks", 0)
        )


@dataclass
class TaskInfo:
    """Information about a specific task"""
    task_id: str
    task_number: str
    title: str
    description: str
    status: TaskStatus
    dependencies: List[str] = field(default_factory=list)
    requirements_refs: List[str] = field(default_factory=list)
    estimated_hours: Optional[float] = None
    actual_hours: Optional[float] = None
    assignee: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "task_id": self.task_id,
            "task_number": self.task_number,
            "title": self.title,
            "description": self.description,
            "status": self.status.value,
            "dependencies": self.dependencies,
            "requirements_refs": self.requirements_refs,
            "estimated_hours": self.estimated_hours,
            "actual_hours": self.actual_hours,
            "assignee": self.assignee
        }


class SpecFileWatcher(BeastlyModule):
    """Watches spec files for changes and updates context"""
    
    def __init__(self, context_manager: ContextManager):
        super().__init__()
        
        self.context_manager = context_manager
        
        # File watching state
        self.watched_specs: Dict[str, Dict[str, Any]] = {}
        self.file_checksums: Dict[str, str] = {}
        
        # Watching thread
        self._watch_thread = None
        self._watch_stop_event = threading.Event()
        self.watch_interval = 5  # seconds
        
        # Metrics
        self._spec_changes_detected = 0
        self._context_updates_triggered = 0
        
        self.logger.info("👁️ SpecFileWatcher initialized")
    
    def start_watching(self, spec_directories: List[Path]):
        """Start watching spec directories for changes"""
        try:
            if self._watch_thread and self._watch_thread.is_alive():
                return
            
            # Discover specs in directories
            for spec_dir in spec_directories:
                self._discover_specs_in_directory(spec_dir)
            
            # Start watching thread
            self._watch_stop_event.clear()
            self._watch_thread = threading.Thread(target=self._watch_worker, daemon=True)
            self._watch_thread.start()
            
            self.logger.info(f"👁️ Started watching {len(self.watched_specs)} specs")
            
        except Exception as e:
            self.logger.error(f"💥 Error starting spec watcher: {e}")
    
    def stop_watching(self):
        """Stop watching spec files"""
        if self._watch_thread:
            self._watch_stop_event.set()
            self._watch_thread.join(timeout=5)
        
        self.logger.info("👁️ Stopped watching spec files")
    
    def add_spec_to_watch(self, spec_path: Path, project_id: str):
        """Add a specific spec to watch list"""
        try:
            spec_key = str(spec_path.resolve())
            
            self.watched_specs[spec_key] = {
                "path": spec_path,
                "project_id": project_id,
                "last_modified": spec_path.stat().st_mtime if spec_path.exists() else 0,
                "last_checked": datetime.now()
            }
            
            # Calculate initial checksum
            if spec_path.exists():
                self.file_checksums[spec_key] = self._calculate_file_checksum(spec_path)
            
            self.logger.info(f"👁️ Added spec to watch: {spec_path.name}")
            
        except Exception as e:
            self.logger.error(f"💥 Error adding spec to watch: {e}")
    
    def _discover_specs_in_directory(self, directory: Path):
        """Discover all specs in a directory"""
        try:
            if not directory.exists():
                return
            
            # Look for .kiro/specs directories
            kiro_specs_dir = directory / ".kiro" / "specs"
            if kiro_specs_dir.exists():
                for spec_dir in kiro_specs_dir.iterdir():
                    if spec_dir.is_dir():
                        # Check for spec files
                        for spec_file in ["requirements.md", "design.md", "tasks.md"]:
                            spec_path = spec_dir / spec_file
                            if spec_path.exists():
                                # Use directory name as project ID
                                project_id = f"spec_{spec_dir.name}"
                                self.add_spec_to_watch(spec_path, project_id)
            
        except Exception as e:
            self.logger.error(f"💥 Error discovering specs in {directory}: {e}")
    
    def _watch_worker(self):
        """Background worker for file watching"""
        while not self._watch_stop_event.wait(self.watch_interval):
            try:
                self._check_for_changes()
            except Exception as e:
                self.logger.error(f"💥 Spec watch worker error: {e}")
    
    def _check_for_changes(self):
        """Check watched specs for changes"""
        for spec_key, spec_info in self.watched_specs.items():
            try:
                spec_path = spec_info["path"]
                
                if not spec_path.exists():
                    continue
                
                # Check modification time
                current_mtime = spec_path.stat().st_mtime
                last_mtime = spec_info["last_modified"]
                
                if current_mtime > last_mtime:
                    # File has been modified, check content
                    current_checksum = self._calculate_file_checksum(spec_path)
                    last_checksum = self.file_checksums.get(spec_key, "")
                    
                    if current_checksum != last_checksum:
                        # Content has actually changed
                        self._handle_spec_change(spec_info, current_checksum)
                        
                        # Update tracking
                        spec_info["last_modified"] = current_mtime
                        spec_info["last_checked"] = datetime.now()
                        self.file_checksums[spec_key] = current_checksum
                        
                        self._spec_changes_detected += 1
            
            except Exception as e:
                self.logger.error(f"💥 Error checking spec {spec_key}: {e}")
    
    def _handle_spec_change(self, spec_info: Dict[str, Any], new_checksum: str):
        """Handle detected spec file change"""
        try:
            spec_path = spec_info["path"]
            project_id = spec_info["project_id"]
            
            self.logger.info(f"📝 Spec change detected: {spec_path.name}")
            
            # Parse the changed spec file
            spec_content = self._parse_spec_file(spec_path)
            
            # Create context event for the change
            event_id = self.context_manager.add_conversation_event(
                event_type=ContextEventType.SYSTEM_EVENT,
                content=f"Spec file updated: {spec_path.name}",
                metadata={
                    "spec_path": str(spec_path),
                    "spec_type": spec_path.suffix,
                    "change_type": "file_modified",
                    "checksum": new_checksum,
                    "parsed_content": spec_content
                }
            )
            
            if event_id:
                self._context_updates_triggered += 1
                
                # Emit observation
                self.emit_observation({
                    "type": "spec_file_changed",
                    "spec_path": str(spec_path),
                    "project_id": project_id,
                    "event_id": event_id,
                    "change_timestamp": datetime.now().isoformat()
                })
            
        except Exception as e:
            self.logger.error(f"💥 Error handling spec change: {e}")
    
    def _parse_spec_file(self, spec_path: Path) -> Dict[str, Any]:
        """Parse spec file content for structured information"""
        try:
            content = spec_path.read_text(encoding='utf-8')
            
            parsed = {
                "file_type": spec_path.stem,
                "line_count": len(content.splitlines()),
                "word_count": len(content.split()),
                "sections": [],
                "tasks": [],
                "requirements": []
            }
            
            # Parse based on file type
            if spec_path.name == "tasks.md":
                parsed["tasks"] = self._parse_tasks_from_content(content)
            elif spec_path.name == "requirements.md":
                parsed["requirements"] = self._parse_requirements_from_content(content)
            elif spec_path.name == "design.md":
                parsed["sections"] = self._parse_sections_from_content(content)
            
            return parsed
            
        except Exception as e:
            self.logger.error(f"💥 Error parsing spec file {spec_path}: {e}")
            return {"error": str(e)}
    
    def _parse_tasks_from_content(self, content: str) -> List[Dict[str, Any]]:
        """Parse tasks from tasks.md content"""
        tasks = []
        
        # Look for task patterns like "- [ ] 1.1 Task description"
        task_pattern = r'^- \[([ x])\] (\d+(?:\.\d+)*)\s+(.+)$'
        
        for line_num, line in enumerate(content.splitlines(), 1):
            match = re.match(task_pattern, line.strip())
            if match:
                status_char, task_number, description = match.groups()
                
                tasks.append({
                    "task_number": task_number,
                    "description": description.strip(),
                    "status": "completed" if status_char == "x" else "not_started",
                    "line_number": line_num
                })
        
        return tasks
    
    def _parse_requirements_from_content(self, content: str) -> List[Dict[str, Any]]:
        """Parse requirements from requirements.md content"""
        requirements = []
        
        # Look for numbered requirements
        req_pattern = r'^#+\s*(?:Requirement\s+)?(\d+(?:\.\d+)*)'
        
        current_req = None
        for line_num, line in enumerate(content.splitlines(), 1):
            match = re.match(req_pattern, line.strip())
            if match:
                if current_req:
                    requirements.append(current_req)
                
                current_req = {
                    "number": match.group(1),
                    "title": line.strip(),
                    "line_number": line_num,
                    "content": []
                }
            elif current_req and line.strip():
                current_req["content"].append(line.strip())
        
        if current_req:
            requirements.append(current_req)
        
        return requirements
    
    def _parse_sections_from_content(self, content: str) -> List[Dict[str, Any]]:
        """Parse sections from design.md content"""
        sections = []
        
        # Look for markdown headers
        header_pattern = r'^(#+)\s*(.+)$'
        
        current_section = None
        for line_num, line in enumerate(content.splitlines(), 1):
            match = re.match(header_pattern, line.strip())
            if match:
                if current_section:
                    sections.append(current_section)
                
                level = len(match.group(1))
                title = match.group(2).strip()
                
                current_section = {
                    "level": level,
                    "title": title,
                    "line_number": line_num,
                    "content": []
                }
            elif current_section and line.strip():
                current_section["content"].append(line.strip())
        
        if current_section:
            sections.append(current_section)
        
        return sections
    
    def _calculate_file_checksum(self, file_path: Path) -> str:
        """Calculate checksum for file content"""
        try:
            content = file_path.read_text(encoding='utf-8')
            return hashlib.md5(content.encode()).hexdigest()
        except Exception:
            return ""


class SpecWorkflowIntegrator(BeastlyModule):
    """Integrates AI Memory Palace with spec workflow"""
    
    def __init__(self, context_manager: ContextManager, 
                 multi_project_manager: MultiProjectContextManager):
        super().__init__()
        
        self.context_manager = context_manager
        self.multi_project_manager = multi_project_manager
        
        # Spec file watcher
        self.file_watcher = SpecFileWatcher(context_manager)
        
        # Spec state tracking
        self.spec_states: Dict[str, SpecState] = {}
        
        # Integration metrics
        self._specs_tracked = 0
        self._tasks_completed = 0
        self._context_syncs = 0
        
        self.logger.info("🔗 SpecWorkflowIntegrator initialized")
    
    def initialize_spec_integration(self, workspace_path: Path):
        """Initialize spec integration for a workspace"""
        try:
            # Discover existing specs
            self._discover_workspace_specs(workspace_path)
            
            # Start file watching
            self.file_watcher.start_watching([workspace_path])
            
            # Sync existing spec states with context
            self._sync_all_spec_states()
            
            self.logger.info(f"🔗 Spec integration initialized for {workspace_path}")
            
        except Exception as e:
            self.logger.error(f"💥 Error initializing spec integration: {e}")
    
    def register_spec(self, spec_name: str, spec_path: Path, project_id: str) -> bool:
        """Register a new spec for tracking"""
        try:
            # Create spec state
            spec_state = SpecState(
                spec_name=spec_name,
                spec_path=spec_path,
                current_phase=SpecPhase.REQUIREMENTS,
                created=datetime.now(),
                last_updated=datetime.now()
            )
            
            # Analyze existing spec files
            self._analyze_spec_files(spec_state)
            
            # Store spec state
            self.spec_states[spec_name] = spec_state
            self._specs_tracked += 1
            
            # Add to file watcher
            spec_dir = spec_path.parent
            for spec_file in ["requirements.md", "design.md", "tasks.md"]:
                file_path = spec_dir / spec_file
                if file_path.exists():
                    self.file_watcher.add_spec_to_watch(file_path, project_id)
            
            # Update context with spec registration
            self._update_context_with_spec_event(
                project_id, "spec_registered", spec_name, spec_state.to_dict()
            )
            
            self.logger.info(f"📋 Registered spec: {spec_name}")
            return True
            
        except Exception as e:
            self.logger.error(f"💥 Error registering spec {spec_name}: {e}")
            return False
    
    def update_task_status(self, spec_name: str, task_number: str, 
                          new_status: TaskStatus, project_id: str) -> bool:
        """Update task status and sync with context"""
        try:
            if spec_name not in self.spec_states:
                self.logger.warning(f"Unknown spec: {spec_name}")
                return False
            
            spec_state = self.spec_states[spec_name]
            
            # Parse current tasks
            tasks = self._parse_spec_tasks(spec_state.spec_path)
            
            # Find and update task
            task_updated = False
            for task in tasks:
                if task.task_number == task_number:
                    old_status = task.status
                    task.status = new_status
                    task_updated = True
                    
                    # Update spec state counters
                    if old_status != TaskStatus.COMPLETED and new_status == TaskStatus.COMPLETED:
                        spec_state.completed_tasks += 1
                        self._tasks_completed += 1
                    elif old_status == TaskStatus.COMPLETED and new_status != TaskStatus.COMPLETED:
                        spec_state.completed_tasks -= 1
                    
                    break
            
            if not task_updated:
                self.logger.warning(f"Task {task_number} not found in spec {spec_name}")
                return False
            
            # Update implementation progress
            if spec_state.total_tasks > 0:
                spec_state.implementation_progress = (spec_state.completed_tasks / spec_state.total_tasks) * 100
            
            # Check if all tasks are complete
            if spec_state.completed_tasks == spec_state.total_tasks and spec_state.total_tasks > 0:
                spec_state.tasks_complete = True
                spec_state.current_phase = SpecPhase.COMPLETED
            
            spec_state.last_updated = datetime.now()
            
            # Create work item for completed task
            if new_status == TaskStatus.COMPLETED:
                work_item = WorkItem(
                    work_id=f"task_{spec_name}_{task_number}",
                    work_type="task_completion",
                    description=f"Completed task {task_number} in spec {spec_name}",
                    timestamp=datetime.now(),
                    files_created=[],
                    files_modified=[],
                    outcome="success"
                )
                
                # Add to context
                context = self.context_manager.get_current_context()
                if context:
                    context.work_completed.append(work_item)
            
            # Update context with task status change
            self._update_context_with_spec_event(
                project_id, "task_status_updated", spec_name, {
                    "task_number": task_number,
                    "old_status": old_status.value if hasattr(old_status, 'value') else str(old_status),
                    "new_status": new_status.value,
                    "implementation_progress": spec_state.implementation_progress,
                    "completed_tasks": spec_state.completed_tasks,
                    "total_tasks": spec_state.total_tasks
                }
            )
            
            self.logger.info(f"📝 Updated task {task_number} in {spec_name}: {new_status.value}")
            return True
            
        except Exception as e:
            self.logger.error(f"💥 Error updating task status: {e}")
            return False
    
    def get_spec_recommendations(self, project_id: str) -> List[Dict[str, Any]]:
        """Get context-aware spec recommendations"""
        try:
            recommendations = []
            
            # Get current context
            context = self.context_manager.get_current_context()
            if not context:
                return recommendations
            
            # Analyze conversation history for spec-related patterns
            recent_conversations = context.conversation_history[-20:] if len(context.conversation_history) > 20 else context.conversation_history
            
            # Look for implementation discussions
            implementation_keywords = ["implement", "build", "create", "add feature", "develop"]
            spec_keywords = ["requirement", "design", "task", "spec", "specification"]
            
            for event in recent_conversations:
                content_lower = event.content.lower()
                
                # Check for implementation without spec
                if any(keyword in content_lower for keyword in implementation_keywords):
                    if not any(keyword in content_lower for keyword in spec_keywords):
                        recommendations.append({
                            "type": "create_spec",
                            "priority": "high",
                            "message": "Consider creating a specification for this implementation work",
                            "context": event.content[:200] + "..." if len(event.content) > 200 else event.content,
                            "suggested_actions": [
                                "Create requirements document",
                                "Define design approach",
                                "Break down into tasks"
                            ]
                        })
            
            # Check for incomplete specs
            for spec_name, spec_state in self.spec_states.items():
                if spec_state.current_phase != SpecPhase.COMPLETED:
                    next_steps = []
                    
                    if not spec_state.requirements_complete:
                        next_steps.append("Complete requirements document")
                    elif not spec_state.design_complete:
                        next_steps.append("Complete design document")
                    elif not spec_state.tasks_complete:
                        next_steps.append(f"Complete remaining {spec_state.total_tasks - spec_state.completed_tasks} tasks")
                    
                    if next_steps:
                        recommendations.append({
                            "type": "continue_spec",
                            "priority": "medium",
                            "spec_name": spec_name,
                            "message": f"Continue work on {spec_name} specification",
                            "progress": spec_state.implementation_progress,
                            "suggested_actions": next_steps
                        })
            
            # Check for blocked tasks
            for spec_name, spec_state in self.spec_states.items():
                if spec_state.blocked_tasks > 0:
                    recommendations.append({
                        "type": "resolve_blocked_tasks",
                        "priority": "high",
                        "spec_name": spec_name,
                        "message": f"{spec_state.blocked_tasks} blocked tasks in {spec_name}",
                        "suggested_actions": [
                            "Review task dependencies",
                            "Resolve blocking issues",
                            "Update task status"
                        ]
                    })
            
            return recommendations
            
        except Exception as e:
            self.logger.error(f"💥 Error getting spec recommendations: {e}")
            return []
    
    def sync_spec_state_with_context(self, spec_name: str, project_id: str) -> bool:
        """Sync spec state with current context"""
        try:
            if spec_name not in self.spec_states:
                return False
            
            spec_state = self.spec_states[spec_name]
            
            # Update context with current spec state
            context = self.context_manager.get_current_context()
            if context:
                context.spec_states[spec_name] = spec_state.to_dict()
                self._context_syncs += 1
            
            # Create context event for sync
            self._update_context_with_spec_event(
                project_id, "spec_state_synced", spec_name, spec_state.to_dict()
            )
            
            return True
            
        except Exception as e:
            self.logger.error(f"💥 Error syncing spec state: {e}")
            return False
    
    def get_spec_navigation_info(self, project_id: str) -> Dict[str, Any]:
        """Get navigation information for specs"""
        try:
            navigation_info = {
                "active_specs": [],
                "recent_activity": [],
                "completion_status": {},
                "next_actions": []
            }
            
            # Get active specs
            for spec_name, spec_state in self.spec_states.items():
                if spec_state.current_phase != SpecPhase.COMPLETED:
                    navigation_info["active_specs"].append({
                        "name": spec_name,
                        "phase": spec_state.current_phase.value,
                        "progress": spec_state.implementation_progress,
                        "last_updated": spec_state.last_updated.isoformat()
                    })
            
            # Get completion status
            total_specs = len(self.spec_states)
            completed_specs = sum(1 for spec in self.spec_states.values() 
                                if spec.current_phase == SpecPhase.COMPLETED)
            
            navigation_info["completion_status"] = {
                "total_specs": total_specs,
                "completed_specs": completed_specs,
                "completion_percentage": (completed_specs / total_specs * 100) if total_specs > 0 else 0
            }
            
            # Get next actions from recommendations
            recommendations = self.get_spec_recommendations(project_id)
            navigation_info["next_actions"] = [
                {
                    "action": rec["message"],
                    "priority": rec["priority"],
                    "type": rec["type"]
                }
                for rec in recommendations[:5]  # Top 5 recommendations
            ]
            
            return navigation_info
            
        except Exception as e:
            self.logger.error(f"💥 Error getting spec navigation info: {e}")
            return {"error": str(e)}
    
    def get_integration_statistics(self) -> Dict[str, Any]:
        """Get spec integration statistics"""
        return {
            "specs_tracked": self._specs_tracked,
            "tasks_completed": self._tasks_completed,
            "context_syncs": self._context_syncs,
            "file_changes_detected": self.file_watcher._spec_changes_detected,
            "context_updates_triggered": self.file_watcher._context_updates_triggered,
            "active_specs": len([s for s in self.spec_states.values() 
                               if s.current_phase != SpecPhase.COMPLETED]),
            "completed_specs": len([s for s in self.spec_states.values() 
                                  if s.current_phase == SpecPhase.COMPLETED])
        }
    
    def _discover_workspace_specs(self, workspace_path: Path):
        """Discover existing specs in workspace"""
        try:
            kiro_specs_dir = workspace_path / ".kiro" / "specs"
            
            if not kiro_specs_dir.exists():
                return
            
            for spec_dir in kiro_specs_dir.iterdir():
                if spec_dir.is_dir():
                    spec_name = spec_dir.name
                    
                    # Check for spec files
                    has_requirements = (spec_dir / "requirements.md").exists()
                    has_design = (spec_dir / "design.md").exists()
                    has_tasks = (spec_dir / "tasks.md").exists()
                    
                    if has_requirements or has_design or has_tasks:
                        project_id = f"spec_{spec_name}"
                        self.register_spec(spec_name, spec_dir, project_id)
            
        except Exception as e:
            self.logger.error(f"💥 Error discovering workspace specs: {e}")
    
    def _analyze_spec_files(self, spec_state: SpecState):
        """Analyze existing spec files to determine state"""
        try:
            spec_dir = spec_state.spec_path
            
            # Check requirements
            requirements_file = spec_dir / "requirements.md"
            if requirements_file.exists():
                content = requirements_file.read_text(encoding='utf-8')
                # Simple heuristic: if file has substantial content, consider complete
                spec_state.requirements_complete = len(content.strip()) > 500
                if spec_state.requirements_complete:
                    spec_state.current_phase = SpecPhase.DESIGN
            
            # Check design
            design_file = spec_dir / "design.md"
            if design_file.exists():
                content = design_file.read_text(encoding='utf-8')
                spec_state.design_complete = len(content.strip()) > 500
                if spec_state.design_complete:
                    spec_state.current_phase = SpecPhase.TASKS
            
            # Check tasks
            tasks_file = spec_dir / "tasks.md"
            if tasks_file.exists():
                tasks = self._parse_spec_tasks_from_file(tasks_file)
                spec_state.total_tasks = len(tasks)
                spec_state.completed_tasks = sum(1 for task in tasks if task.status == TaskStatus.COMPLETED)
                spec_state.blocked_tasks = sum(1 for task in tasks if task.status == TaskStatus.BLOCKED)
                
                if spec_state.total_tasks > 0:
                    spec_state.implementation_progress = (spec_state.completed_tasks / spec_state.total_tasks) * 100
                    spec_state.current_phase = SpecPhase.IMPLEMENTATION
                    
                    if spec_state.completed_tasks == spec_state.total_tasks:
                        spec_state.tasks_complete = True
                        spec_state.current_phase = SpecPhase.COMPLETED
            
        except Exception as e:
            self.logger.error(f"💥 Error analyzing spec files: {e}")
    
    def _parse_spec_tasks(self, spec_path: Path) -> List[TaskInfo]:
        """Parse tasks from spec directory"""
        tasks_file = spec_path / "tasks.md"
        if tasks_file.exists():
            return self._parse_spec_tasks_from_file(tasks_file)
        return []
    
    def _parse_spec_tasks_from_file(self, tasks_file: Path) -> List[TaskInfo]:
        """Parse tasks from tasks.md file"""
        tasks = []
        
        try:
            content = tasks_file.read_text(encoding='utf-8')
            
            # Parse task lines
            task_pattern = r'^- \[([ x])\] (\d+(?:\.\d+)*)\s+(.+)$'
            
            for line in content.splitlines():
                match = re.match(task_pattern, line.strip())
                if match:
                    status_char, task_number, description = match.groups()
                    
                    status = TaskStatus.COMPLETED if status_char == "x" else TaskStatus.NOT_STARTED
                    
                    task = TaskInfo(
                        task_id=f"task_{task_number}",
                        task_number=task_number,
                        title=description.strip(),
                        description=description.strip(),
                        status=status
                    )
                    
                    tasks.append(task)
            
        except Exception as e:
            self.logger.error(f"💥 Error parsing tasks from {tasks_file}: {e}")
        
        return tasks
    
    def _update_context_with_spec_event(self, project_id: str, event_type: str, 
                                       spec_name: str, event_data: Dict[str, Any]):
        """Update context with spec-related event"""
        try:
            event_id = self.context_manager.add_conversation_event(
                event_type=ContextEventType.SYSTEM_EVENT,
                content=f"Spec {event_type}: {spec_name}",
                metadata={
                    "spec_name": spec_name,
                    "event_type": event_type,
                    "event_data": event_data,
                    "project_id": project_id
                }
            )
            
            if event_id:
                # Emit observation
                self.emit_observation({
                    "type": f"spec_{event_type}",
                    "spec_name": spec_name,
                    "project_id": project_id,
                    "event_id": event_id,
                    "event_data": event_data,
                    "timestamp": datetime.now().isoformat()
                })
        
        except Exception as e:
            self.logger.error(f"💥 Error updating context with spec event: {e}")
    
    def _sync_all_spec_states(self):
        """Sync all spec states with context"""
        try:
            context = self.context_manager.get_current_context()
            if not context:
                return
            
            # Update context with all spec states
            for spec_name, spec_state in self.spec_states.items():
                context.spec_states[spec_name] = spec_state.to_dict()
            
            self._context_syncs += 1
            
        except Exception as e:
            self.logger.error(f"💥 Error syncing all spec states: {e}")


# CLI Integration for Spec Workflow
class SpecWorkflowCLI:
    """Command-line interface for spec workflow integration"""
    
    def __init__(self, integrator: SpecWorkflowIntegrator):
        self.integrator = integrator
    
    def register_spec(self, spec_name: str, spec_path: str, project_id: str) -> Dict[str, Any]:
        """Register a spec for tracking"""
        success = self.integrator.register_spec(spec_name, Path(spec_path), project_id)
        return {"success": success, "spec_name": spec_name}
    
    def update_task(self, spec_name: str, task_number: str, status: str, project_id: str) -> Dict[str, Any]:
        """Update task status"""
        try:
            task_status = TaskStatus(status.lower())
            success = self.integrator.update_task_status(spec_name, task_number, task_status, project_id)
            return {"success": success, "spec_name": spec_name, "task_number": task_number, "status": status}
        except ValueError:
            return {"success": False, "error": f"Invalid status: {status}"}
    
    def get_recommendations(self, project_id: str) -> List[Dict[str, Any]]:
        """Get spec recommendations"""
        return self.integrator.get_spec_recommendations(project_id)
    
    def get_navigation(self, project_id: str) -> Dict[str, Any]:
        """Get spec navigation information"""
        return self.integrator.get_spec_navigation_info(project_id)
    
    def get_stats(self) -> Dict[str, Any]:
        """Get integration statistics"""
        return self.integrator.get_integration_statistics()