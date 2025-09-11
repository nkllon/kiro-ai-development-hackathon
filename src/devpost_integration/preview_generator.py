"""
Devpost Preview Generator - Minimal Implementation

Generates local HTML preview of Devpost submission.
"""

from pathlib import Path
from typing import Dict, Any, Optional, List
import json
from datetime import datetime
from dataclasses import dataclass, field

from .models import ProjectMetadata, ValidationResult, MediaFile, MediaType
from .reflective_module import (
    ReflectiveModule, ModuleHealth, ModuleStatus, ModuleCapability, 
    ModuleConfiguration, register_module
)
from datetime import datetime



@dataclass
class PreviewData(ReflectiveModule):
    """Data for preview generation."""
    project_metadata: ProjectMetadata
    validation_result: ValidationResult
    media_files: List[MediaFile] = field(default_factory=list)
    generated_at: datetime = field(default_factory=datetime.now)
    template_version: str = "1.0"


class DevpostPreviewGenerator:
    """Generates local preview of Devpost submission."""
    
    def __init__(self, project_path: Optional[Path] = None, validation_engine: Optional[Any] = None):
        super().__init__(module_id="preview_generator", version="1.0.0")
        self._start_time = datetime.now()
        register_module(self)

        """
        Initialize the preview generator.
        
        Args:
            project_path: Path to the project directory (optional)
            validation_engine: Validation engine instance (optional)
        """
        self.project_path = Path(project_path) if project_path else Path.cwd()
        self.validation_engine = validation_engine
        self.template = self._get_preview_template()
        
        # Cache attributes for testing
        self._project_data_cache = None
        self._cache_timestamp = None
    
    def generate_preview(self, output_file: str = 'preview.html') -> PreviewData:
        """Generate preview data for the project."""
        # Collect project metadata
        project_metadata = self._get_project_metadata()
        
        # Validate project
        validation_result = self._validate_project()
        
        # Find media files
        media_files = self._find_media_files()
        
        # Generate HTML preview file
        project_data = self._collect_project_data()
        html_content = self.template.format(**project_data)
        output_path = Path(output_file)
        output_path.write_text(html_content, encoding='utf-8')
        
        return PreviewData(
            project_metadata=project_metadata,
            validation_result=validation_result,
            media_files=media_files
        )
    
    def _collect_project_data(self) -> Dict[str, Any]:
        """Collect project data from local files."""
        data = {
            'project_name': 'Beast Mode Framework',
            'tagline': 'Where Requirements ARE the Solution',
            'description': self._get_description(),
            'tech_stack': self._get_tech_stack(),
            'team_info': 'Systematic Development Team',
            'github_url': 'https://github.com/your-repo',
            'demo_url': '#',
            'built_with': ['Python', 'Kiro AI', 'Systematic Architecture']
        }
        
        return data
    
    def _get_project_metadata(self) -> ProjectMetadata:
        """Extract project metadata from project files."""
        # Try to get project name from package.json or README
        project_name = self._extract_project_name()
        
        # Get description from README
        description = self._get_description()
        
        # Get repository URL
        repo_url = self._get_repository_url()
        
        return ProjectMetadata(
            title=project_name,
            tagline="A systematic development project",
            description=description,
            repository_url=repo_url,
            demo_url=None,
            team_members=[],
            tags=self._get_tech_stack()
        )
    
    def _validate_project(self) -> ValidationResult:
        """Validate project against DevPost requirements."""
        errors = []
        warnings = []
        
        # Check if README exists
        readme_path = self.project_path / 'README.md'
        if not readme_path.exists():
            errors.append("README.md is required")
        
        # Check if project has basic structure
        if not (self.project_path / 'src').exists() and not (self.project_path / 'app').exists():
            warnings.append("No src/ or app/ directory found")
        
        is_valid = len(errors) == 0
        
        return ValidationResult(
            is_valid=is_valid,
            missing_fields=[],
            errors=errors,
            warnings=warnings,
            completion_percentage=80.0 if is_valid else 40.0
        )
    
    def _find_media_files(self) -> List[MediaFile]:
        """Find media files in the project."""
        media_files = []
        
        # Look for common media file extensions
        media_extensions = ['.png', '.jpg', '.jpeg', '.gif', '.mp4', '.mov', '.webm']
        
        for ext in media_extensions:
            for file_path in self.project_path.rglob(f'*{ext}'):
                if file_path.is_file():
                    # Map file extension to MediaType
                    media_type = self._get_media_type(ext)
                    media_files.append(MediaFile(
                        filename=file_path.name,
                        file_path=file_path,
                        media_type=media_type,
                        file_size=file_path.stat().st_size
                    ))
        
        return media_files
    
    def _get_media_type(self, extension: str) -> MediaType:
        """Map file extension to MediaType enum."""
        ext = extension.lower()
        if ext in ['.png', '.jpg', '.jpeg', '.gif']:
            return MediaType.IMAGE
        elif ext in ['.mp4', '.mov', '.webm']:
            return MediaType.VIDEO
        else:
            return MediaType.OTHER
    
    def _extract_project_name(self) -> str:
        """Extract project name from package.json or README."""
        # Try package.json first
        package_json = self.project_path / 'package.json'
        if package_json.exists():
            try:
                data = json.loads(package_json.read_text())
                if 'name' in data:
                    return data['name']
            except:
                pass
        
        # Try README.md title
        readme = self.project_path / 'README.md'
        if readme.exists():
            try:
                content = readme.read_text()
                lines = content.split('\n')
                for line in lines:
                    if line.startswith('# '):
                        return line[2:].strip()
            except:
                pass
        
        # Fallback to directory name
        return self.project_path.name.replace('-', ' ').replace('_', ' ').title()
    
    def _get_repository_url(self) -> Optional[str]:
        """Extract repository URL from package.json or git config."""
        # Try package.json
        package_json = self.project_path / 'package.json'
        if package_json.exists():
            try:
                data = json.loads(package_json.read_text())
                if 'repository' in data:
                    repo = data['repository']
                    if isinstance(repo, str):
                        return repo
                    elif isinstance(repo, dict) and 'url' in repo:
                        return repo['url']
            except:
                pass
        
        # Try git config
        try:
            import subprocess
            result = subprocess.run(['git', 'config', '--get', 'remote.origin.url'], 
                                 cwd=self.project_path, capture_output=True, text=True)
            if result.returncode == 0:
                return result.stdout.strip()
        except:
            pass
        
        return None
    
    def _get_description(self) -> str:
        """Get project description from README."""
        readme_path = Path('README.md')
        if readme_path.exists():
            content = readme_path.read_text(encoding='utf-8')
            # Extract first paragraph as description
            lines = content.split('\n')
            for line in lines:
                if line.strip() and not line.startswith('#'):
                    return line.strip()
        
        return "AI-powered development framework for systematic software development."
    
    def _get_tech_stack(self) -> str:
        """Get technology stack information."""
        # Check for common config files
        tech_stack = []
        
        if Path('package.json').exists():
            tech_stack.append('Node.js/JavaScript')
        
        if Path('requirements.txt').exists() or Path('pyproject.toml').exists():
            tech_stack.append('Python')
        
        if Path('Cargo.toml').exists():
            tech_stack.append('Rust')
        
        if Path('go.mod').exists():
            tech_stack.append('Go')
        
        return ', '.join(tech_stack) if tech_stack else 'Multi-language'
    
    def _get_preview_template(self) -> str:
        """Get HTML template for preview."""
        return '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{project_name} - Devpost Preview</title>
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; margin: 0; padding: 20px; background: #f8f9fa; }}
        .container {{ max-width: 800px; margin: 0 auto; background: white; padding: 30px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
        h1 {{ color: #2c3e50; margin-bottom: 10px; }}
        .tagline {{ color: #7f8c8d; font-size: 18px; margin-bottom: 30px; }}
        .section {{ margin-bottom: 30px; }}
        .section h2 {{ color: #34495e; border-bottom: 2px solid #3498db; padding-bottom: 5px; }}
        .tech-stack {{ background: #ecf0f1; padding: 15px; border-radius: 5px; }}
        .links {{ display: flex; gap: 15px; margin-top: 20px; }}
        .link {{ background: #3498db; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px; }}
        .link:hover {{ background: #2980b9; }}
        .requirements-note {{ background: #e8f5e8; border-left: 4px solid #27ae60; padding: 15px; margin-top: 20px; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>{project_name}</h1>
        <div class="tagline">{tagline}</div>
        
        <div class="section">
            <h2>Description</h2>
            <p>{description}</p>
        </div>
        
        <div class="section">
            <h2>Technology Stack</h2>
            <div class="tech-stack">
                <strong>Built with:</strong> {tech_stack}
            </div>
        </div>
        
        <div class="section">
            <h2>Team</h2>
            <p>{team_info}</p>
        </div>
        
        <div class="links">
            <a href="{github_url}" class="link">View Code</a>
            <a href="{demo_url}" class="link">Live Demo</a>
        </div>
        
        <div class="requirements-note">
            <strong>🎯 The Requirements ARE the Solution</strong><br>
            This project demonstrates systematic, requirements-driven development where comprehensive specifications become the solution architecture itself.
        </div>
    </div>
</body>
</html>'''

    # ReflectiveModule interface implementation
    def get_module_info(self) -> Dict[str, Any]:
        """Get comprehensive module information."""
        return {
            'module_id': self.module_id,
            'version': self.version,
            'name': 'Preview Generator',
            'description': 'preview_generator module for DevPost integration',
            'author': 'DevPost Integration Team',
            'created_at': self._start_time.isoformat(),
            'interface_version': self.get_interface_version()
        }
    
    def get_capabilities(self) -> List[ModuleCapability]:
        """Get module capabilities."""
        return []
    
    def get_dependencies(self) -> List[str]:
        """Get module dependencies."""
        return []
    
    def check_health(self) -> ModuleHealth:
        """Perform comprehensive health check."""
        issues = []
        health_score = 1.0
        
        try:
            # Basic health checks
            if not hasattr(self, 'module_id'):
                issues.append("Missing module_id")
                health_score -= 0.2
            
            # Add module-specific health checks here
            
            
            # Determine status
            if health_score >= 0.9:
                status = ModuleStatus.HEALTHY
            elif health_score >= 0.7:
                status = ModuleStatus.DEGRADED
            else:
                status = ModuleStatus.UNHEALTHY
            
            return ModuleHealth(
                module_id=self.module_id,
                status=status,
                last_check=datetime.now(),
                health_score=max(0.0, health_score),
                issues=issues,
                capabilities=self.get_capabilities(),
                dependencies=self.get_dependencies(),
                metrics=self.get_metrics()
            )
            
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return ModuleHealth(
                module_id=self.module_id,
                status=ModuleStatus.UNHEALTHY,
                last_check=datetime.now(),
                health_score=0.0,
                issues=[f"Health check exception: {e}"],
                capabilities=self.get_capabilities(),
                dependencies=self.get_dependencies(),
                metrics={}
            )
    
    def get_configuration(self) -> ModuleConfiguration:
        """Get module configuration."""
        return ModuleConfiguration(
            module_id=self.module_id,
            config_version="1.0.0",
            parameters={},
            required_parameters=[],
            optional_parameters=[],
            validation_rules={},
            last_updated=datetime.now()
        )
    
    def update_configuration(self, config: ModuleConfiguration) -> bool:
        """Update module configuration."""
        try:
            if not config.is_valid():
                logger.error("Invalid configuration provided")
                return False
            
            logger.info(f"Configuration updated for {self.module_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error updating configuration: {e}")
            return False
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get module metrics."""
        uptime = (datetime.now() - self._start_time).total_seconds()
        
        return {
            'uptime_seconds': uptime,
            'uptime_hours': uptime / 3600,
            'last_check': datetime.now().isoformat()
        }
    
    def reset_metrics(self) -> None:
        """Reset module metrics to initial state."""
        self._start_time = datetime.now()
        logger.info("Metrics reset for {self.module_id} module")


class RealtimePreviewManager:
    """Manages real-time preview updates for Devpost submissions."""
    
    def __init__(self, watch_directory: str = ".", preview_generator: Optional[DevpostPreviewGenerator] = None):
        """
        Initialize the realtime preview manager.
        
        Args:
            watch_directory: Directory to watch for changes
            preview_generator: Preview generator instance (optional)
        """
        self.watch_directory = Path(watch_directory)
        self.generator = preview_generator or DevpostPreviewGenerator()
        self.is_watching = False
    
    def start_watching(self) -> None:
        """Start watching for file changes and updating preview."""
        self.is_watching = True
        # Implementation would use file system watchers
        pass
    
    def stop_watching(self) -> None:
        """Stop watching for file changes."""
        self.is_watching = False
    
    def update_preview(self) -> Path:
        """Update the preview with current project state."""
        return self.generator.generate_preview()