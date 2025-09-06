"""
Devpost Preview Generator - Minimal Implementation

Generates local HTML preview of Devpost submission.
"""

from pathlib import Path
from typing import Dict, Any
import json


class DevpostPreviewGenerator:
    """Generates local preview of Devpost submission."""
    
    def __init__(self):
        self.template = self._get_preview_template()
    
    def generate_preview(self, output_file: str = 'preview.html') -> Path:
        """Generate HTML preview of the project."""
        project_data = self._collect_project_data()
        
        # Generate HTML from template and data
        html_content = self.template.format(**project_data)
        
        output_path = Path(output_file)
        output_path.write_text(html_content, encoding='utf-8')
        
        return output_path
    
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