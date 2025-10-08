"""
Document storage and file operations for the Spec Framework.

This module provides file-based storage implementation with atomic operations,
version tracking, and CRUD operations for specification documents.
"""

import os
import json
import shutil
import tempfile
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import asdict
import fcntl
from contextlib import contextmanager

from .models import (
    SpecificationDocument,
    SemanticVersion,
    WorkflowStage,
    ApprovalStatus,
    AuditEntry,
    ChangeSet,
)


class DocumentStorageError(Exception):
    """Exception raised for document storage operations."""
    pass


class DocumentRepository:
    """File-based repository for specification documents with atomic operations."""
    
    def __init__(self, base_path: str = ".kiro/specs"):
        """Initialize document repository with base storage path."""
        self.base_path = Path(base_path)
        self.base_path.mkdir(parents=True, exist_ok=True)
        
        # Version tracking directory
        self.versions_path = self.base_path / "_versions"
        self.versions_path.mkdir(exist_ok=True)
        
        # Metadata storage
        self.metadata_path = self.base_path / "_metadata"
        self.metadata_path.mkdir(exist_ok=True)
    
    def create(self, spec_doc: SpecificationDocument) -> SpecificationDocument:
        """Create a new specification document with atomic file operations."""
        spec_dir = self.base_path / spec_doc.id
        
        if spec_dir.exists():
            raise DocumentStorageError(f"Specification {spec_doc.id} already exists")
        
        try:
            # Create spec directory atomically
            temp_dir = Path(tempfile.mkdtemp(prefix=f"{spec_doc.id}_", dir=self.base_path))
            
            # Create metadata file
            metadata = self._spec_to_metadata(spec_doc)
            metadata_file = temp_dir / "metadata.json"
            self._write_json_atomic(metadata_file, metadata)
            
            # Create requirements file if it doesn't exist
            if not Path(spec_doc.requirements_path).exists():
                requirements_file = temp_dir / "requirements.md"
                self._create_requirements_template(requirements_file, spec_doc)
                spec_doc.requirements_path = str(requirements_file.relative_to(self.base_path))
            
            # Atomic rename to final location
            temp_dir.rename(spec_dir)
            
            # Update paths to be relative to base_path
            spec_doc.requirements_path = str(Path(spec_doc.id) / "requirements.md")
            
            # Create version entry
            self._create_version_entry(spec_doc, "created")
            
            return spec_doc
            
        except Exception as e:
            # Cleanup on failure
            if temp_dir.exists():
                shutil.rmtree(temp_dir)
            raise DocumentStorageError(f"Failed to create specification: {e}")
    
    def read(self, spec_id: str) -> Optional[SpecificationDocument]:
        """Read a specification document by ID."""
        spec_dir = self.base_path / spec_id
        metadata_file = spec_dir / "metadata.json"
        
        if not metadata_file.exists():
            return None
        
        try:
            with self._file_lock(metadata_file):
                metadata = self._read_json(metadata_file)
                return self._metadata_to_spec(metadata)
        except Exception as e:
            raise DocumentStorageError(f"Failed to read specification {spec_id}: {e}")
    
    def update(self, spec_doc: SpecificationDocument, changes: ChangeSet) -> SpecificationDocument:
        """Update a specification document with change tracking."""
        spec_dir = self.base_path / spec_doc.id
        metadata_file = spec_dir / "metadata.json"
        
        if not spec_dir.exists():
            raise DocumentStorageError(f"Specification {spec_doc.id} does not exist")
        
        try:
            with self._file_lock(metadata_file):
                # Update timestamp and audit trail
                spec_doc.updated_at = datetime.now()
                
                # Add audit entry for changes
                audit_entry = AuditEntry(
                    timestamp=spec_doc.updated_at,
                    event_type="document_updated",
                    user_id=os.getenv("USER", "system"),
                    changes=changes,
                    correlation_id=""  # Will be auto-generated
                )
                spec_doc.audit_trail.append(audit_entry)
                
                # Write updated metadata atomically
                metadata = self._spec_to_metadata(spec_doc)
                self._write_json_atomic(metadata_file, metadata)
                
                # Create version entry
                self._create_version_entry(spec_doc, "updated", changes)
                
                return spec_doc
                
        except Exception as e:
            raise DocumentStorageError(f"Failed to update specification {spec_doc.id}: {e}")
    
    def delete(self, spec_id: str) -> bool:
        """Delete a specification document."""
        spec_dir = self.base_path / spec_id
        
        if not spec_dir.exists():
            return False
        
        try:
            # Move to trash directory instead of permanent deletion
            trash_dir = self.base_path / "_trash"
            trash_dir.mkdir(exist_ok=True)
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            trash_location = trash_dir / f"{spec_id}_{timestamp}"
            
            spec_dir.rename(trash_location)
            return True
            
        except Exception as e:
            raise DocumentStorageError(f"Failed to delete specification {spec_id}: {e}")
    
    def list_all(self) -> List[str]:
        """List all specification IDs."""
        spec_ids = []
        
        for item in self.base_path.iterdir():
            if item.is_dir() and not item.name.startswith("_"):
                metadata_file = item / "metadata.json"
                if metadata_file.exists():
                    spec_ids.append(item.name)
        
        return sorted(spec_ids)
    
    def get_versions(self, spec_id: str) -> List[Dict[str, Any]]:
        """Get version history for a specification."""
        version_file = self.versions_path / f"{spec_id}.json"
        
        if not version_file.exists():
            return []
        
        try:
            return self._read_json(version_file)
        except Exception:
            return []
    
    @contextmanager
    def _file_lock(self, file_path: Path):
        """Context manager for file locking."""
        lock_file = file_path.with_suffix(file_path.suffix + ".lock")
        
        try:
            with open(lock_file, 'w') as f:
                fcntl.flock(f.fileno(), fcntl.LOCK_EX)
                yield
        finally:
            if lock_file.exists():
                lock_file.unlink()
    
    def _write_json_atomic(self, file_path: Path, data: Dict[str, Any]):
        """Write JSON data atomically using temporary file."""
        temp_file = file_path.with_suffix(file_path.suffix + ".tmp")
        
        try:
            with open(temp_file, 'w') as f:
                json.dump(data, f, indent=2, default=str)
            
            # Atomic rename
            temp_file.rename(file_path)
            
        except Exception:
            if temp_file.exists():
                temp_file.unlink()
            raise
    
    def _read_json(self, file_path: Path) -> Dict[str, Any]:
        """Read JSON data from file."""
        with open(file_path, 'r') as f:
            return json.load(f)
    
    def _spec_to_metadata(self, spec_doc: SpecificationDocument) -> Dict[str, Any]:
        """Convert SpecificationDocument to metadata dictionary."""
        # Convert dataclass to dict, handling special types
        metadata = {
            "id": spec_doc.id,
            "name": spec_doc.name,
            "version": {
                "major": spec_doc.version.major,
                "minor": spec_doc.version.minor,
                "patch": spec_doc.version.patch
            },
            "requirements_path": spec_doc.requirements_path,
            "design_path": spec_doc.design_path,
            "tasks_path": spec_doc.tasks_path,
            "dependencies": [
                {
                    "source_spec": dep.source_spec,
                    "target_spec": dep.target_spec,
                    "dependency_type": dep.dependency_type.value
                }
                for dep in spec_doc.dependencies
            ],
            "workflow_stage": spec_doc.workflow_stage.value,
            "approval_status": spec_doc.approval_status.value,
            "created_at": spec_doc.created_at.isoformat(),
            "updated_at": spec_doc.updated_at.isoformat(),
            "audit_trail": [
                {
                    "timestamp": entry.timestamp.isoformat(),
                    "event_type": entry.event_type,
                    "user_id": entry.user_id,
                    "changes": {
                        "added_sections": entry.changes.added_sections,
                        "modified_sections": entry.changes.modified_sections,
                        "removed_sections": entry.changes.removed_sections,
                        "metadata_changes": entry.changes.metadata_changes
                    },
                    "correlation_id": entry.correlation_id
                }
                for entry in spec_doc.audit_trail
            ]
        }
        
        return metadata
    
    def _metadata_to_spec(self, metadata: Dict[str, Any]) -> SpecificationDocument:
        """Convert metadata dictionary to SpecificationDocument."""
        from .models import Dependency, DependencyType
        
        # Parse version
        version_data = metadata["version"]
        version = SemanticVersion(
            major=version_data["major"],
            minor=version_data["minor"],
            patch=version_data["patch"]
        )
        
        # Parse dependencies
        dependencies = []
        for dep_data in metadata.get("dependencies", []):
            dependency = Dependency(
                source_spec=dep_data["source_spec"],
                target_spec=dep_data["target_spec"],
                dependency_type=DependencyType(dep_data["dependency_type"])
            )
            dependencies.append(dependency)
        
        # Parse audit trail
        audit_trail = []
        for entry_data in metadata.get("audit_trail", []):
            changes = ChangeSet(
                added_sections=entry_data["changes"]["added_sections"],
                modified_sections=entry_data["changes"]["modified_sections"],
                removed_sections=entry_data["changes"]["removed_sections"],
                metadata_changes=entry_data["changes"]["metadata_changes"]
            )
            
            audit_entry = AuditEntry(
                timestamp=datetime.fromisoformat(entry_data["timestamp"]),
                event_type=entry_data["event_type"],
                user_id=entry_data["user_id"],
                changes=changes,
                correlation_id=entry_data["correlation_id"]
            )
            audit_trail.append(audit_entry)
        
        return SpecificationDocument(
            id=metadata["id"],
            name=metadata["name"],
            version=version,
            requirements_path=metadata["requirements_path"],
            design_path=metadata.get("design_path"),
            tasks_path=metadata.get("tasks_path"),
            dependencies=dependencies,
            workflow_stage=WorkflowStage(metadata["workflow_stage"]),
            approval_status=ApprovalStatus(metadata["approval_status"]),
            created_at=datetime.fromisoformat(metadata["created_at"]),
            updated_at=datetime.fromisoformat(metadata["updated_at"]),
            audit_trail=audit_trail
        )
    
    def _create_requirements_template(self, file_path: Path, spec_doc: SpecificationDocument):
        """Create a requirements template file."""
        template = f"""# {spec_doc.name} Requirements

## Introduction

[Provide an introduction to this specification]

## Requirements

### Requirement 1: [Requirement Name]

**User Story:** As a [role], I want [feature], so that [benefit]

#### Acceptance Criteria

1. WHEN [event] THEN [system] SHALL [response]
2. WHEN [event] AND [condition] THEN [system] SHALL [response]

### Requirement 2: [Requirement Name]

**User Story:** As a [role], I want [feature], so that [benefit]

#### Acceptance Criteria

1. WHEN [event] THEN [system] SHALL [response]
2. IF [precondition] THEN [system] SHALL [response]
"""
        
        with open(file_path, 'w') as f:
            f.write(template)
    
    def _create_version_entry(self, spec_doc: SpecificationDocument, event_type: str, changes: Optional[ChangeSet] = None):
        """Create a version history entry."""
        version_file = self.versions_path / f"{spec_doc.id}.json"
        
        # Load existing versions
        versions = []
        if version_file.exists():
            try:
                versions = self._read_json(version_file)
            except Exception:
                versions = []
        
        # Create new version entry
        version_entry = {
            "version": str(spec_doc.version),
            "timestamp": spec_doc.updated_at.isoformat(),
            "event_type": event_type,
            "workflow_stage": spec_doc.workflow_stage.value,
            "approval_status": spec_doc.approval_status.value,
            "user_id": os.getenv("USER", "system")
        }
        
        if changes:
            version_entry["changes"] = {
                "added_sections": changes.added_sections,
                "modified_sections": changes.modified_sections,
                "removed_sections": changes.removed_sections,
                "metadata_changes": changes.metadata_changes
            }
        
        versions.append(version_entry)
        
        # Write updated versions
        self._write_json_atomic(version_file, versions)