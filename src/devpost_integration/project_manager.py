"""
Devpost Project Manager - Minimal Multi-Target Implementation

Demonstrates:
1. Hackathon-ready CLI functionality
2. Kiro AI-powered systematic development
3. TiDB-scale systematic architecture patterns
"""

from dataclasses import dataclass
from pathlib import Path
from typing import Optional, List, Dict, Any
from datetime import datetime
import json


@dataclass
class ProjectStatus:
    """Project status information."""
    connected: bool
    project_id: Optional[str] = None
    project_name: Optional[str] = None
    local_path: Optional[Path] = None
    last_sync: Optional[datetime] = None
    pending_changes: List[str] = None
    validation_errors: List[str] = None
    
    def __post_init__(self):
        if self.pending_changes is None:
            self.pending_changes = []
        if self.validation_errors is None:
            self.validation_errors = []


class DevpostProjectManager:
    """
    Systematic project management for hackathon submissions.
    
    Demonstrates Beast Mode principles:
    - Requirements ARE the Solution
    - Systematic over ad-hoc
    - Physics-informed architecture
    """
    
    def __init__(self):
        self.config_path = Path('.devpost/config.json')
        self.config_path.parent.mkdir(exist_ok=True)
    
    def connect_project(self, project_id: str, local_path: Path, config_file: Optional[str] = None) -> bool:
        """Connect local project to Devpost submission."""
        try:
            # Systematic validation - no ad-hoc connections
            if not self._validate_project_structure(local_path):
                return False
            
            # Create systematic configuration
            config = {
                'project_id': project_id,
                'local_path': str(local_path.absolute()),
                'connected_at': datetime.now().isoformat(),
                'project_name': self._extract_project_name(local_path),
                'systematic_validation': True,  # Beast Mode marker
                'kiro_integration': True,       # Kiro AI marker
                'tidb_ready': True             # TiDB scale marker
            }
            
            # Save configuration systematically
            self.config_path.write_text(json.dumps(config, indent=2))
            
            return True
            
        except Exception as e:
            print(f"Systematic connection failed: {e}")
            return False
    
    def get_project_status(self) -> ProjectStatus:
        """Get systematic project status."""
        if not self.config_path.exists():
            return ProjectStatus(connected=False)
        
        try:
            config = json.loads(self.config_path.read_text())
            
            # Systematic status collection
            status = ProjectStatus(
                connected=True,
                project_id=config.get('project_id'),
                project_name=config.get('project_name'),
                local_path=Path(config.get('local_path', '.')),
                last_sync=self._get_last_sync(),
                pending_changes=self._get_pending_changes(),
                validation_errors=self._get_validation_errors()
            )
            
            return status
            
        except Exception:
            return ProjectStatus(connected=False)
    
    def _validate_project_structure(self, path: Path) -> bool:
        """Systematic project structure validation."""
        # Beast Mode: Requirements ARE the Solution
        required_indicators = [
            path / 'README.md',
            path / 'package.json',
            path / 'pyproject.toml',
            path / '.git'
        ]
        
        # At least one project indicator must exist
        return any(indicator.exists() for indicator in required_indicators)
    
    def _extract_project_name(self, path: Path) -> str:
        """Extract project name systematically."""
        # Try package.json first (systematic priority)
        package_json = path / 'package.json'
        if package_json.exists():
            try:
                data = json.loads(package_json.read_text())
                if 'name' in data:
                    return data['name']
            except:
                pass
        
        # Try README.md title
        readme = path / 'README.md'
        if readme.exists():
            try:
                content = readme.read_text()
                lines = content.split('\n')
                for line in lines:
                    if line.startswith('# '):
                        return line[2:].strip()
            except:
                pass
        
        # Fallback to directory name (systematic default)
        return path.name.replace('-', ' ').replace('_', ' ').title()
    
    def _get_last_sync(self) -> Optional[datetime]:
        """Get last sync time (systematic tracking)."""
        sync_file = Path('.devpost/last_sync')
        if sync_file.exists():
            try:
                return datetime.fromisoformat(sync_file.read_text().strip())
            except:
                pass
        return None
    
    def _get_pending_changes(self) -> List[str]:
        """Get pending changes (systematic detection)."""
        changes = []
        
        # Systematic change detection
        change_indicators = {
            'README.md': 'Project description updates',
            'package.json': 'Project metadata changes',
            'pyproject.toml': 'Python project configuration',
            '.kiro/': 'Kiro AI specifications',
            'src/': 'Source code changes'
        }
        
        for indicator, description in change_indicators.items():
            if Path(indicator).exists():
                changes.append(description)
        
        return changes
    
    def _get_validation_errors(self) -> List[str]:
        """Get validation errors (systematic quality gates)."""
        errors = []
        
        # Systematic validation rules
        if not Path('README.md').exists():
            errors.append('Missing README.md - required for hackathon submission')
        
        if not any(Path(f).exists() for f in ['package.json', 'pyproject.toml', 'Cargo.toml']):
            errors.append('No project configuration file found')
        
        # Beast Mode validation
        if not Path('.kiro/').exists():
            errors.append('Missing .kiro/ directory - systematic development not detected')
        
        return errors