"""
Spec Registry - Central registry for all specifications with lifecycle management.

Maintains a JSON index of all specs with metadata, lifecycle states, and
dependency information for systematic management.
"""

import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional, Set
from dataclasses import dataclass, asdict
from enum import Enum

from .validator import SpecValidator


class LifecycleState(Enum):
    """Spec lifecycle states."""
    DRAFT = "draft"
    ACTIVE = "active"
    COMPLETED = "completed"
    DEPRECATED = "deprecated"
    ARCHIVED = "archived"


@dataclass
class SpecMetadata:
    """Metadata for a single specification."""
    name: str
    path: str
    lifecycle_state: LifecycleState
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    completed_at: Optional[str] = None
    is_complete: bool = False
    has_extra_files: bool = False
    files_found: List[str] = None
    extra_files: List[str] = None
    dependencies: List[str] = None
    tags: List[str] = None
    description: Optional[str] = None
    
    def __post_init__(self):
        if self.files_found is None:
            self.files_found = []
        if self.extra_files is None:
            self.extra_files = []
        if self.dependencies is None:
            self.dependencies = []
        if self.tags is None:
            self.tags = []


class SpecRegistry:
    """Central registry for all specifications."""
    
    def __init__(self, specs_dir: Path = None, validator: SpecValidator = None):
        self.specs_dir = specs_dir or Path(".kiro/specs")
        self.validator = validator or SpecValidator(self.specs_dir)
        self.registry_file = Path(".kiro/spec-registry.json")
        
        self._specs: Dict[str, SpecMetadata] = {}
        self.load_registry()
    
    def load_registry(self):
        """Load registry from disk or build from filesystem."""
        if self.registry_file.exists():
            try:
                with open(self.registry_file, 'r') as f:
                    data = json.load(f)
                
                self._specs = {}
                for spec_name, spec_data in data.get("specs", {}).items():
                    # Convert lifecycle state string back to enum
                    if "lifecycle_state" in spec_data:
                        spec_data["lifecycle_state"] = LifecycleState(spec_data["lifecycle_state"])
                    
                    self._specs[spec_name] = SpecMetadata(**spec_data)
                
                return
            except (json.JSONDecodeError, KeyError, ValueError) as e:
                print(f"Warning: Could not load registry file: {e}")
        
        # Build registry from filesystem
        self.rebuild_registry()
    
    def rebuild_registry(self):
        """Rebuild registry by scanning filesystem."""
        self._specs = {}
        
        if not self.specs_dir.exists():
            return
        
        # Get validation report for all specs
        validation_report = self.validator.validate_all_specs()
        
        # Scan all spec directories
        for spec_dir in self.specs_dir.iterdir():
            if not spec_dir.is_dir() or spec_dir.name.startswith('.'):
                continue
            
            spec_name = spec_dir.name
            validation_result = validation_report.validation_results.get(spec_name)
            
            # Load lifecycle state from .spec-state file
            lifecycle_state = self._load_spec_state(spec_dir)
            
            # Extract metadata
            metadata = SpecMetadata(
                name=spec_name,
                path=str(spec_dir.relative_to(Path.cwd())),
                lifecycle_state=lifecycle_state,
                created_at=datetime.now().isoformat(),
                updated_at=datetime.now().isoformat(),
                is_complete=validation_result.is_complete if validation_result else False,
                has_extra_files=bool(validation_result.extra_files) if validation_result else False,
                files_found=list(validation_result.files_found) if validation_result else [],
                extra_files=list(validation_result.extra_files) if validation_result else [],
                description=self._extract_description(spec_dir)
            )
            
            self._specs[spec_name] = metadata
        
        self.save_registry()
    
    def save_registry(self):
        """Save registry to disk."""
        # Convert to serializable format
        registry_data = {
            "version": "1.0.0",
            "generated_at": datetime.now().isoformat(),
            "total_specs": len(self._specs),
            "specs": {}
        }
        
        for spec_name, metadata in self._specs.items():
            spec_dict = asdict(metadata)
            # Convert enum to string
            spec_dict["lifecycle_state"] = metadata.lifecycle_state.value
            registry_data["specs"][spec_name] = spec_dict
        
        # Ensure directory exists
        self.registry_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Save to file
        with open(self.registry_file, 'w') as f:
            json.dump(registry_data, f, indent=2)
    
    def register_spec(self, spec_name: str, lifecycle_state: LifecycleState = LifecycleState.DRAFT) -> bool:
        """Register a new spec in the registry."""
        if spec_name in self._specs:
            return False  # Already exists
        
        spec_path = self.specs_dir / spec_name
        
        metadata = SpecMetadata(
            name=spec_name,
            path=str(spec_path.relative_to(Path.cwd())),
            lifecycle_state=lifecycle_state,
            created_at=datetime.now().isoformat(),
            updated_at=datetime.now().isoformat()
        )
        
        self._specs[spec_name] = metadata
        self._save_spec_state(spec_path, lifecycle_state)
        self.save_registry()
        
        return True
    
    def update_spec_state(self, spec_name: str, new_state: LifecycleState) -> bool:
        """Update the lifecycle state of a spec."""
        if spec_name not in self._specs:
            return False
        
        self._specs[spec_name].lifecycle_state = new_state
        self._specs[spec_name].updated_at = datetime.now().isoformat()
        
        if new_state == LifecycleState.COMPLETED:
            self._specs[spec_name].completed_at = datetime.now().isoformat()
        
        # Update .spec-state file
        spec_path = self.specs_dir / spec_name
        self._save_spec_state(spec_path, new_state)
        
        self.save_registry()
        return True
    
    def get_spec(self, spec_name: str) -> Optional[SpecMetadata]:
        """Get metadata for a specific spec."""
        return self._specs.get(spec_name)
    
    def list_specs(self, lifecycle_state: Optional[LifecycleState] = None) -> List[SpecMetadata]:
        """List all specs, optionally filtered by lifecycle state."""
        specs = list(self._specs.values())
        
        if lifecycle_state:
            specs = [spec for spec in specs if spec.lifecycle_state == lifecycle_state]
        
        return sorted(specs, key=lambda x: x.name)
    
    def get_incomplete_specs(self) -> List[str]:
        """Get list of incomplete spec names."""
        return [name for name, metadata in self._specs.items() if not metadata.is_complete]
    
    def get_specs_with_extra_files(self) -> List[str]:
        """Get list of specs with extra files."""
        return [name for name, metadata in self._specs.items() if metadata.has_extra_files]
    
    def get_lifecycle_distribution(self) -> Dict[str, int]:
        """Get distribution of specs by lifecycle state."""
        distribution = {}
        for state in LifecycleState:
            distribution[state.value] = 0
        
        for metadata in self._specs.values():
            distribution[metadata.lifecycle_state.value] += 1
        
        return distribution
    
    def _load_spec_state(self, spec_dir: Path) -> LifecycleState:
        """Load lifecycle state from .spec-state file."""
        state_file = spec_dir / ".spec-state"
        
        if state_file.exists():
            try:
                with open(state_file, 'r') as f:
                    data = json.load(f)
                return LifecycleState(data.get("lifecycle_state", "draft"))
            except (json.JSONDecodeError, KeyError, ValueError):
                pass
        
        # Default to draft if no state file or invalid
        return LifecycleState.DRAFT
    
    def _save_spec_state(self, spec_dir: Path, state: LifecycleState):
        """Save lifecycle state to .spec-state file."""
        state_file = spec_dir / ".spec-state"
        
        state_data = {
            "lifecycle_state": state.value,
            "updated_at": datetime.now().isoformat()
        }
        
        spec_dir.mkdir(parents=True, exist_ok=True)
        with open(state_file, 'w') as f:
            json.dump(state_data, f, indent=2)
    
    def _extract_description(self, spec_dir: Path) -> Optional[str]:
        """Extract description from requirements.md if available."""
        requirements_file = spec_dir / "requirements.md"
        
        if requirements_file.exists():
            try:
                with open(requirements_file, 'r') as f:
                    content = f.read()
                
                # Look for introduction or first paragraph
                lines = content.split('\n')
                for i, line in enumerate(lines):
                    if line.strip().lower().startswith('## introduction'):
                        # Get next non-empty line
                        for j in range(i + 1, len(lines)):
                            if lines[j].strip() and not lines[j].startswith('#'):
                                return lines[j].strip()[:200] + "..." if len(lines[j]) > 200 else lines[j].strip()
                
                # Fallback to first non-header line
                for line in lines:
                    if line.strip() and not line.startswith('#'):
                        return line.strip()[:200] + "..." if len(line) > 200 else line.strip()
            
            except Exception:
                pass
        
        return None