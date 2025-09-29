"""
Multi-Project Context Management for AI Memory Palace.

Provides project detection, automatic context switching, cross-project isolation,
shared context handling, and project context migration tools.
"""

import json
import asyncio
import os
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Set, Tuple
from pathlib import Path
import uuid
import hashlib
import threading
import time
from dataclasses import dataclass, field
from enum import Enum

from ..core.reflective_module import ReflectiveModule
from .models import SessionContext, ContextEvent, ProjectState
from .context_registry import ContextRegistry
from .context_manager import ContextManager
from .security import ContextSecurity


class ProjectType(Enum):
    """Types of projects detected"""
    PYTHON = "python"
    JAVASCRIPT = "javascript"
    TYPESCRIPT = "typescript"
    RUST = "rust"
    GO = "go"
    JAVA = "java"
    CSHARP = "csharp"
    GENERIC = "generic"
    KIRO_SPEC = "kiro_spec"
    MULTI_LANGUAGE = "multi_language"


class ProjectScope(Enum):
    """Project context scope levels"""
    ISOLATED = "isolated"          # Completely separate contexts
    SHARED_READ = "shared_read"    # Can read from other projects
    SHARED_WRITE = "shared_write"  # Can read/write to shared contexts
    GLOBAL = "global"              # Access to all project contexts


@dataclass
class ProjectMetadata:
    """Metadata for detected projects"""
    project_id: str
    project_name: str
    project_type: ProjectType
    root_path: Path
    scope: ProjectScope
    created: datetime
    last_accessed: datetime
    context_size_bytes: int = 0
    active_sessions: int = 0
    shared_contexts: List[str] = field(default_factory=list)
    security_level: str = "standard"
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "project_id": self.project_id,
            "project_name": self.project_name,
            "project_type": self.project_type.value,
            "root_path": str(self.root_path),
            "scope": self.scope.value,
            "created": self.created.isoformat(),
            "last_accessed": self.last_accessed.isoformat(),
            "context_size_bytes": self.context_size_bytes,
            "active_sessions": self.active_sessions,
            "shared_contexts": self.shared_contexts,
            "security_level": self.security_level
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ProjectMetadata':
        return cls(
            project_id=data["project_id"],
            project_name=data["project_name"],
            project_type=ProjectType(data["project_type"]),
            root_path=Path(data["root_path"]),
            scope=ProjectScope(data["scope"]),
            created=datetime.fromisoformat(data["created"]),
            last_accessed=datetime.fromisoformat(data["last_accessed"]),
            context_size_bytes=data.get("context_size_bytes", 0),
            active_sessions=data.get("active_sessions", 0),
            shared_contexts=data.get("shared_contexts", []),
            security_level=data.get("security_level", "standard")
        )


@dataclass
class SharedContextConfig:
    """Configuration for shared context between projects"""
    shared_id: str
    name: str
    description: str
    participating_projects: List[str]
    access_permissions: Dict[str, str]  # project_id -> permission level
    created: datetime
    last_updated: datetime
    size_limit_mb: int = 10
    retention_days: int = 30
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "shared_id": self.shared_id,
            "name": self.name,
            "description": self.description,
            "participating_projects": self.participating_projects,
            "access_permissions": self.access_permissions,
            "created": self.created.isoformat(),
            "last_updated": self.last_updated.isoformat(),
            "size_limit_mb": self.size_limit_mb,
            "retention_days": self.retention_days
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'SharedContextConfig':
        return cls(
            shared_id=data["shared_id"],
            name=data["name"],
            description=data["description"],
            participating_projects=data["participating_projects"],
            access_permissions=data["access_permissions"],
            created=datetime.fromisoformat(data["created"]),
            last_updated=datetime.fromisoformat(data["last_updated"]),
            size_limit_mb=data.get("size_limit_mb", 10),
            retention_days=data.get("retention_days", 30)
        )


class ProjectDetector(ReflectiveModule):
    """Detects and classifies projects in the workspace"""
    
    def __init__(self):
        super().__init__()
        
        # Project detection patterns
        self.detection_patterns = {
            ProjectType.PYTHON: [
                "requirements.txt", "setup.py", "pyproject.toml", "Pipfile", 
                "poetry.lock", "conda.yml", "environment.yml"
            ],
            ProjectType.JAVASCRIPT: [
                "package.json", "yarn.lock", "npm-shrinkwrap.json"
            ],
            ProjectType.TYPESCRIPT: [
                "tsconfig.json", "package.json"  # Combined with .ts files
            ],
            ProjectType.RUST: [
                "Cargo.toml", "Cargo.lock"
            ],
            ProjectType.GO: [
                "go.mod", "go.sum", "Gopkg.toml"
            ],
            ProjectType.JAVA: [
                "pom.xml", "build.gradle", "gradle.properties", "build.xml"
            ],
            ProjectType.CSHARP: [
                "*.csproj", "*.sln", "packages.config", "project.json"
            ],
            ProjectType.KIRO_SPEC: [
                ".kiro/specs", ".kiro/steering", ".kiro/hooks"
            ]
        }
        
        # Detection metrics
        self._projects_detected = 0
        self._detection_runs = 0
        self._false_positives = 0
        
        self.logger.info("🔍 ProjectDetector initialized")
    
    def detect_projects(self, root_path: Path, max_depth: int = 3) -> List[ProjectMetadata]:
        """Detect all projects in the given root path"""
        try:
            self._detection_runs += 1
            detected_projects = []
            
            # Scan directory tree
            for current_path in self._scan_directories(root_path, max_depth):
                project_types = self._detect_project_types(current_path)
                
                if project_types:
                    # Create project metadata
                    project_id = self._generate_project_id(current_path)
                    project_name = current_path.name
                    
                    # Determine primary project type
                    primary_type = self._determine_primary_type(project_types)
                    
                    # Determine default scope based on project type
                    scope = self._determine_default_scope(primary_type, current_path)
                    
                    metadata = ProjectMetadata(
                        project_id=project_id,
                        project_name=project_name,
                        project_type=primary_type,
                        root_path=current_path,
                        scope=scope,
                        created=datetime.now(),
                        last_accessed=datetime.now()
                    )
                    
                    detected_projects.append(metadata)
                    self._projects_detected += 1
            
            # Emit detection observation
            self.emit_observation({
                "type": "projects_detected",
                "projects_found": len(detected_projects),
                "root_path": str(root_path),
                "max_depth": max_depth,
                "detection_timestamp": datetime.now().isoformat()
            })
            
            self.logger.info(f"🔍 Detected {len(detected_projects)} projects in {root_path}")
            return detected_projects
            
        except Exception as e:
            self.logger.error(f"💥 Project detection error: {e}")
            return []
    
    def detect_current_project(self, current_path: Path) -> Optional[ProjectMetadata]:
        """Detect the project for the current working directory"""
        try:
            # Walk up the directory tree to find project markers
            search_path = current_path.resolve()
            
            while search_path != search_path.parent:
                project_types = self._detect_project_types(search_path)
                
                if project_types:
                    project_id = self._generate_project_id(search_path)
                    project_name = search_path.name
                    primary_type = self._determine_primary_type(project_types)
                    scope = self._determine_default_scope(primary_type, search_path)
                    
                    metadata = ProjectMetadata(
                        project_id=project_id,
                        project_name=project_name,
                        project_type=primary_type,
                        root_path=search_path,
                        scope=scope,
                        created=datetime.now(),
                        last_accessed=datetime.now()
                    )
                    
                    self.logger.info(f"🎯 Current project detected: {project_name} ({primary_type.value})")
                    return metadata
                
                search_path = search_path.parent
            
            # No project detected - create generic project
            project_id = self._generate_project_id(current_path)
            
            return ProjectMetadata(
                project_id=project_id,
                project_name=current_path.name,
                project_type=ProjectType.GENERIC,
                root_path=current_path,
                scope=ProjectScope.ISOLATED,
                created=datetime.now(),
                last_accessed=datetime.now()
            )
            
        except Exception as e:
            self.logger.error(f"💥 Current project detection error: {e}")
            return None
    
    def _scan_directories(self, root_path: Path, max_depth: int) -> List[Path]:
        """Scan directory tree for potential projects"""
        directories = []
        
        def scan_recursive(path: Path, depth: int):
            if depth > max_depth:
                return
            
            try:
                if path.is_dir() and not self._should_skip_directory(path):
                    directories.append(path)
                    
                    for child in path.iterdir():
                        if child.is_dir():
                            scan_recursive(child, depth + 1)
            except (PermissionError, OSError):
                # Skip directories we can't access
                pass
        
        scan_recursive(root_path, 0)
        return directories
    
    def _should_skip_directory(self, path: Path) -> bool:
        """Check if directory should be skipped during scanning"""
        skip_patterns = {
            ".git", ".svn", ".hg",  # Version control
            "node_modules", "__pycache__", ".pytest_cache",  # Build artifacts
            ".venv", "venv", "env",  # Virtual environments
            "target", "build", "dist",  # Build directories
            ".idea", ".vscode",  # IDE directories
            "tmp", "temp", "cache"  # Temporary directories
        }
        
        return path.name in skip_patterns or path.name.startswith('.')
    
    def _detect_project_types(self, path: Path) -> List[ProjectType]:
        """Detect project types in the given directory"""
        detected_types = []
        
        try:
            # Get list of files and directories in path
            items = set()
            for item in path.iterdir():
                items.add(item.name)
                if item.is_file():
                    items.add(item.suffix)
            
            # Check each project type
            for project_type, patterns in self.detection_patterns.items():
                if self._matches_patterns(items, patterns, path):
                    detected_types.append(project_type)
            
            # Special case: TypeScript detection
            if ProjectType.JAVASCRIPT in detected_types:
                # Check for .ts files to determine if it's TypeScript
                ts_files = list(path.glob("**/*.ts"))
                if ts_files and ProjectType.TYPESCRIPT not in detected_types:
                    detected_types.append(ProjectType.TYPESCRIPT)
            
            return detected_types
            
        except Exception as e:
            self.logger.error(f"💥 Error detecting project types in {path}: {e}")
            return []
    
    def _matches_patterns(self, items: Set[str], patterns: List[str], path: Path) -> bool:
        """Check if directory items match project patterns"""
        for pattern in patterns:
            if pattern.startswith('.kiro/'):
                # Special handling for Kiro directories
                kiro_path = path / pattern
                if kiro_path.exists():
                    return True
            elif '*' in pattern:
                # Glob pattern matching
                matches = list(path.glob(pattern))
                if matches:
                    return True
            else:
                # Direct file/directory matching
                if pattern in items:
                    return True
        
        return False
    
    def _determine_primary_type(self, project_types: List[ProjectType]) -> ProjectType:
        """Determine the primary project type from detected types"""
        if not project_types:
            return ProjectType.GENERIC
        
        # Priority order for project types
        priority_order = [
            ProjectType.KIRO_SPEC,
            ProjectType.TYPESCRIPT,
            ProjectType.PYTHON,
            ProjectType.RUST,
            ProjectType.GO,
            ProjectType.JAVA,
            ProjectType.CSHARP,
            ProjectType.JAVASCRIPT,
            ProjectType.GENERIC
        ]
        
        # Return highest priority type found
        for project_type in priority_order:
            if project_type in project_types:
                return project_type
        
        # Multiple types detected
        if len(project_types) > 1:
            return ProjectType.MULTI_LANGUAGE
        
        return project_types[0]
    
    def _determine_default_scope(self, project_type: ProjectType, path: Path) -> ProjectScope:
        """Determine default scope based on project type and characteristics"""
        # Kiro spec projects get shared access by default
        if project_type == ProjectType.KIRO_SPEC:
            return ProjectScope.SHARED_WRITE
        
        # Multi-language projects might need shared access
        if project_type == ProjectType.MULTI_LANGUAGE:
            return ProjectScope.SHARED_READ
        
        # Check for monorepo indicators
        if self._is_monorepo(path):
            return ProjectScope.SHARED_READ
        
        # Default to isolated for security
        return ProjectScope.ISOLATED
    
    def _is_monorepo(self, path: Path) -> bool:
        """Check if path appears to be a monorepo"""
        monorepo_indicators = [
            "lerna.json", "nx.json", "rush.json",
            "packages", "apps", "libs", "modules"
        ]
        
        for indicator in monorepo_indicators:
            if (path / indicator).exists():
                return True
        
        return False
    
    def _generate_project_id(self, path: Path) -> str:
        """Generate unique project ID based on path"""
        # Use path hash for consistent IDs
        path_str = str(path.resolve())
        path_hash = hashlib.md5(path_str.encode()).hexdigest()[:8]
        return f"proj_{path.name}_{path_hash}"


class MultiProjectContextManager(ReflectiveModule):
    """Manages context across multiple projects with isolation and sharing"""
    
    def __init__(self, context_registry: ContextRegistry, security: ContextSecurity):
        super().__init__()
        
        self.context_registry = context_registry
        self.security = security
        self.detector = ProjectDetector()
        
        # Project registry
        self.projects: Dict[str, ProjectMetadata] = {}
        self.shared_contexts: Dict[str, SharedContextConfig] = {}
        
        # Current active project
        self.current_project_id: Optional[str] = None
        
        # Project switching metrics
        self._project_switches = 0
        self._context_isolations_enforced = 0
        self._shared_context_accesses = 0
        
        # Auto-detection settings
        self.auto_detection_enabled = True
        self.detection_interval = 60  # seconds
        
        # Background detection thread
        self._detection_thread = None
        self._detection_stop_event = threading.Event()
        
        self.logger.info("🏗️ MultiProjectContextManager initialized")
    
    def start_auto_detection(self):
        """Start automatic project detection"""
        if self._detection_thread and self._detection_thread.is_alive():
            return
        
        self._detection_stop_event.clear()
        self._detection_thread = threading.Thread(target=self._detection_worker, daemon=True)
        self._detection_thread.start()
        
        self.logger.info("🔄 Auto project detection started")
    
    def stop_auto_detection(self):
        """Stop automatic project detection"""
        if self._detection_thread:
            self._detection_stop_event.set()
            self._detection_thread.join(timeout=5)
        
        self.logger.info("⏹️ Auto project detection stopped")
    
    def detect_and_switch_project(self, current_path: Optional[Path] = None) -> Optional[str]:
        """Detect current project and switch context if needed"""
        try:
            if not current_path:
                current_path = Path.cwd()
            
            # Detect current project
            project_metadata = self.detector.detect_current_project(current_path)
            if not project_metadata:
                return None
            
            # Register project if not already known
            if project_metadata.project_id not in self.projects:
                self.register_project(project_metadata)
            
            # Switch to project if different from current
            if self.current_project_id != project_metadata.project_id:
                return self.switch_to_project(project_metadata.project_id)
            
            return project_metadata.project_id
            
        except Exception as e:
            self.logger.error(f"💥 Project detection and switch error: {e}")
            return None
    
    def register_project(self, project_metadata: ProjectMetadata) -> bool:
        """Register a new project"""
        try:
            # Validate project metadata
            if not self._validate_project_metadata(project_metadata):
                return False
            
            # Store project metadata
            self.projects[project_metadata.project_id] = project_metadata
            
            # Create project-specific context directory
            self._ensure_project_context_directory(project_metadata.project_id)
            
            # Emit registration observation
            self.emit_observation({
                "type": "project_registered",
                "project_id": project_metadata.project_id,
                "project_name": project_metadata.project_name,
                "project_type": project_metadata.project_type.value,
                "scope": project_metadata.scope.value,
                "registration_timestamp": datetime.now().isoformat()
            })
            
            self.logger.info(f"📝 Project registered: {project_metadata.project_name}")
            return True
            
        except Exception as e:
            self.logger.error(f"💥 Project registration error: {e}")
            return False
    
    def switch_to_project(self, project_id: str) -> Optional[str]:
        """Switch active context to specified project"""
        try:
            if project_id not in self.projects:
                self.logger.error(f"Unknown project: {project_id}")
                return None
            
            # Update current project
            old_project_id = self.current_project_id
            self.current_project_id = project_id
            self._project_switches += 1
            
            # Update project access time
            self.projects[project_id].last_accessed = datetime.now()
            
            # Emit switch observation
            self.emit_observation({
                "type": "project_switched",
                "old_project_id": old_project_id,
                "new_project_id": project_id,
                "project_name": self.projects[project_id].project_name,
                "switch_timestamp": datetime.now().isoformat()
            })
            
            self.logger.info(f"🔄 Switched to project: {self.projects[project_id].project_name}")
            return project_id
            
        except Exception as e:
            self.logger.error(f"💥 Project switch error: {e}")
            return None
    
    def get_project_context(self, project_id: Optional[str] = None, 
                           session_id: Optional[str] = None) -> Optional[SessionContext]:
        """Get context for specified project with isolation enforcement"""
        try:
            target_project_id = project_id or self.current_project_id
            
            if not target_project_id:
                self.logger.warning("No project specified and no current project")
                return None
            
            # Enforce access control
            if not self._can_access_project_context(self.current_project_id, target_project_id):
                self._context_isolations_enforced += 1
                self.logger.warning(f"Access denied to project {target_project_id} from {self.current_project_id}")
                return None
            
            # Load context through registry
            context = self.context_registry.load_context(target_project_id, session_id)
            
            # Apply security filtering if accessing different project
            if target_project_id != self.current_project_id and context:
                context = self.security.filter_cross_project_context(context, self.current_project_id)
            
            return context
            
        except Exception as e:
            self.logger.error(f"💥 Error getting project context: {e}")
            return None
    
    def store_project_context(self, context: SessionContext, 
                             project_id: Optional[str] = None) -> bool:
        """Store context for specified project with isolation enforcement"""
        try:
            target_project_id = project_id or self.current_project_id
            
            if not target_project_id:
                return False
            
            # Enforce access control
            if not self._can_modify_project_context(self.current_project_id, target_project_id):
                self._context_isolations_enforced += 1
                self.logger.warning(f"Modification denied to project {target_project_id} from {self.current_project_id}")
                return False
            
            # Update context project ID
            context.project_id = target_project_id
            
            # Store through registry
            success = self.context_registry.store_context(context)
            
            if success:
                # Update project metadata
                if target_project_id in self.projects:
                    self.projects[target_project_id].context_size_bytes = context.get_context_size()
                    self.projects[target_project_id].last_accessed = datetime.now()
            
            return success
            
        except Exception as e:
            self.logger.error(f"💥 Error storing project context: {e}")
            return False
    
    def create_shared_context(self, name: str, description: str, 
                             participating_projects: List[str],
                             permissions: Optional[Dict[str, str]] = None) -> Optional[str]:
        """Create shared context between projects"""
        try:
            # Validate participating projects
            for project_id in participating_projects:
                if project_id not in self.projects:
                    self.logger.error(f"Unknown project in shared context: {project_id}")
                    return None
            
            # Generate shared context ID
            shared_id = str(uuid.uuid4())
            
            # Default permissions
            if not permissions:
                permissions = {pid: "read_write" for pid in participating_projects}
            
            # Create shared context config
            shared_config = SharedContextConfig(
                shared_id=shared_id,
                name=name,
                description=description,
                participating_projects=participating_projects,
                access_permissions=permissions,
                created=datetime.now(),
                last_updated=datetime.now()
            )
            
            # Store shared context config
            self.shared_contexts[shared_id] = shared_config
            
            # Update project metadata
            for project_id in participating_projects:
                if project_id in self.projects:
                    self.projects[project_id].shared_contexts.append(shared_id)
            
            # Emit shared context creation observation
            self.emit_observation({
                "type": "shared_context_created",
                "shared_id": shared_id,
                "name": name,
                "participating_projects": participating_projects,
                "creation_timestamp": datetime.now().isoformat()
            })
            
            self.logger.info(f"🤝 Shared context created: {name}")
            return shared_id
            
        except Exception as e:
            self.logger.error(f"💥 Shared context creation error: {e}")
            return None
    
    def access_shared_context(self, shared_id: str) -> Optional[SessionContext]:
        """Access shared context with permission checking"""
        try:
            if shared_id not in self.shared_contexts:
                return None
            
            shared_config = self.shared_contexts[shared_id]
            
            # Check if current project has access
            if self.current_project_id not in shared_config.participating_projects:
                self.logger.warning(f"Access denied to shared context {shared_id}")
                return None
            
            # Check permission level
            permission = shared_config.access_permissions.get(self.current_project_id, "none")
            if permission == "none":
                return None
            
            self._shared_context_accesses += 1
            
            # Load shared context (stored with shared_id as project_id)
            context = self.context_registry.load_context(f"shared_{shared_id}")
            
            # Apply security filtering
            if context:
                context = self.security.filter_shared_context(context, self.current_project_id, permission)
            
            return context
            
        except Exception as e:
            self.logger.error(f"💥 Shared context access error: {e}")
            return None
    
    def list_projects(self) -> List[Dict[str, Any]]:
        """List all registered projects"""
        return [project.to_dict() for project in self.projects.values()]
    
    def list_shared_contexts(self) -> List[Dict[str, Any]]:
        """List shared contexts accessible to current project"""
        accessible_contexts = []
        
        if not self.current_project_id:
            return accessible_contexts
        
        for shared_config in self.shared_contexts.values():
            if self.current_project_id in shared_config.participating_projects:
                accessible_contexts.append(shared_config.to_dict())
        
        return accessible_contexts
    
    def migrate_project_context(self, source_project_id: str, target_project_id: str,
                               migration_strategy: str = "copy") -> bool:
        """Migrate context from one project to another"""
        try:
            # Validate projects exist
            if source_project_id not in self.projects or target_project_id not in self.projects:
                return False
            
            # Load source context
            source_context = self.context_registry.load_context(source_project_id)
            if not source_context:
                return False
            
            # Apply migration strategy
            if migration_strategy == "copy":
                # Copy context to target project
                migrated_context = self._copy_context_for_migration(source_context, target_project_id)
                success = self.context_registry.store_context(migrated_context)
            
            elif migration_strategy == "move":
                # Move context to target project
                migrated_context = self._copy_context_for_migration(source_context, target_project_id)
                success = self.context_registry.store_context(migrated_context)
                
                if success:
                    # Clear source context
                    self.context_registry.clear_context(source_project_id)
            
            elif migration_strategy == "merge":
                # Merge with existing target context
                target_context = self.context_registry.load_context(target_project_id)
                if target_context:
                    merged_context = self._merge_contexts_for_migration(source_context, target_context)
                else:
                    merged_context = self._copy_context_for_migration(source_context, target_project_id)
                
                success = self.context_registry.store_context(merged_context)
            
            else:
                return False
            
            if success:
                # Emit migration observation
                self.emit_observation({
                    "type": "project_context_migrated",
                    "source_project_id": source_project_id,
                    "target_project_id": target_project_id,
                    "migration_strategy": migration_strategy,
                    "migration_timestamp": datetime.now().isoformat()
                })
                
                self.logger.info(f"📦 Context migrated from {source_project_id} to {target_project_id}")
            
            return success
            
        except Exception as e:
            self.logger.error(f"💥 Context migration error: {e}")
            return False
    
    def cleanup_inactive_projects(self, inactive_days: int = 30) -> int:
        """Clean up contexts for inactive projects"""
        try:
            cutoff_date = datetime.now() - timedelta(days=inactive_days)
            cleaned_count = 0
            
            inactive_projects = [
                project_id for project_id, project in self.projects.items()
                if project.last_accessed < cutoff_date
            ]
            
            for project_id in inactive_projects:
                # Archive context before cleanup
                context = self.context_registry.load_context(project_id)
                if context:
                    self._archive_project_context(project_id, context)
                
                # Clear context
                if self.context_registry.clear_context(project_id):
                    cleaned_count += 1
                    
                    # Remove from projects registry
                    del self.projects[project_id]
            
            self.logger.info(f"🧹 Cleaned up {cleaned_count} inactive projects")
            return cleaned_count
            
        except Exception as e:
            self.logger.error(f"💥 Project cleanup error: {e}")
            return 0
    
    def get_multi_project_statistics(self) -> Dict[str, Any]:
        """Get multi-project management statistics"""
        try:
            total_context_size = sum(p.context_size_bytes for p in self.projects.values())
            
            return {
                "total_projects": len(self.projects),
                "current_project_id": self.current_project_id,
                "current_project_name": self.projects[self.current_project_id].project_name if self.current_project_id else None,
                "shared_contexts": len(self.shared_contexts),
                "total_context_size_mb": round(total_context_size / 1024 / 1024, 2),
                "project_switches": self._project_switches,
                "context_isolations_enforced": self._context_isolations_enforced,
                "shared_context_accesses": self._shared_context_accesses,
                "auto_detection_enabled": self.auto_detection_enabled,
                "projects_by_type": self._get_projects_by_type(),
                "projects_by_scope": self._get_projects_by_scope()
            }
            
        except Exception as e:
            self.logger.error(f"💥 Error getting multi-project statistics: {e}")
            return {"error": str(e)}
    
    def _detection_worker(self):
        """Background worker for automatic project detection"""
        while not self._detection_stop_event.wait(self.detection_interval):
            try:
                self.detect_and_switch_project()
            except Exception as e:
                self.logger.error(f"💥 Detection worker error: {e}")
    
    def _validate_project_metadata(self, metadata: ProjectMetadata) -> bool:
        """Validate project metadata"""
        if not metadata.project_id or not metadata.project_name:
            return False
        
        if not metadata.root_path.exists():
            return False
        
        return True
    
    def _ensure_project_context_directory(self, project_id: str):
        """Ensure project-specific context directory exists"""
        project_dir = self.context_registry.storage.storage_dir / project_id
        project_dir.mkdir(exist_ok=True)
    
    def _can_access_project_context(self, requesting_project: Optional[str], 
                                   target_project: str) -> bool:
        """Check if requesting project can access target project context"""
        if not requesting_project or requesting_project == target_project:
            return True
        
        if requesting_project not in self.projects:
            return False
        
        requesting_scope = self.projects[requesting_project].scope
        
        # Check scope permissions
        if requesting_scope in [ProjectScope.SHARED_READ, ProjectScope.SHARED_WRITE, ProjectScope.GLOBAL]:
            return True
        
        return False
    
    def _can_modify_project_context(self, requesting_project: Optional[str], 
                                   target_project: str) -> bool:
        """Check if requesting project can modify target project context"""
        if not requesting_project or requesting_project == target_project:
            return True
        
        if requesting_project not in self.projects:
            return False
        
        requesting_scope = self.projects[requesting_project].scope
        
        # Only shared_write and global can modify other project contexts
        if requesting_scope in [ProjectScope.SHARED_WRITE, ProjectScope.GLOBAL]:
            return True
        
        return False
    
    def _copy_context_for_migration(self, source_context: SessionContext, 
                                   target_project_id: str) -> SessionContext:
        """Copy context for migration to another project"""
        # Create new context with updated project ID
        migrated_context = SessionContext(
            project_id=target_project_id,
            session_id=str(uuid.uuid4()),  # New session ID
            timestamp=datetime.now(),
            conversation_history=source_context.conversation_history.copy(),
            decisions_made=source_context.decisions_made.copy(),
            work_completed=source_context.work_completed.copy(),
            system_discoveries=source_context.system_discoveries.copy(),
            project_state=source_context.project_state,
            spec_states=source_context.spec_states.copy()
        )
        
        return migrated_context
    
    def _merge_contexts_for_migration(self, source_context: SessionContext, 
                                     target_context: SessionContext) -> SessionContext:
        """Merge source context into target context"""
        # Merge conversation history
        merged_conversations = target_context.conversation_history.copy()
        existing_event_ids = {event.event_id for event in merged_conversations}
        
        for event in source_context.conversation_history:
            if event.event_id not in existing_event_ids:
                merged_conversations.append(event)
        
        # Sort by timestamp
        merged_conversations.sort(key=lambda x: x.timestamp)
        
        # Merge other components (simplified)
        target_context.conversation_history = merged_conversations
        target_context.decisions_made.extend(source_context.decisions_made)
        target_context.work_completed.extend(source_context.work_completed)
        target_context.system_discoveries.extend(source_context.system_discoveries)
        
        return target_context
    
    def _archive_project_context(self, project_id: str, context: SessionContext):
        """Archive project context before cleanup"""
        try:
            archive_dir = Path.home() / ".kiro" / "archived_contexts"
            archive_dir.mkdir(parents=True, exist_ok=True)
            
            archive_file = archive_dir / f"{project_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            
            with open(archive_file, 'w') as f:
                json.dump(context.to_dict(), f, indent=2)
            
            self.logger.info(f"📦 Archived context for project {project_id}")
            
        except Exception as e:
            self.logger.error(f"💥 Context archival error: {e}")
    
    def _get_projects_by_type(self) -> Dict[str, int]:
        """Get project count by type"""
        type_counts = {}
        for project in self.projects.values():
            project_type = project.project_type.value
            type_counts[project_type] = type_counts.get(project_type, 0) + 1
        return type_counts
    
    def _get_projects_by_scope(self) -> Dict[str, int]:
        """Get project count by scope"""
        scope_counts = {}
        for project in self.projects.values():
            scope = project.scope.value
            scope_counts[scope] = scope_counts.get(scope, 0) + 1
        return scope_counts