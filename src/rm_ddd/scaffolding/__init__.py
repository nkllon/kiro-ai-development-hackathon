"""
Project scaffolding and initialization for RM-DDD projects.

This module provides systematic project generation capabilities for creating
new RM-DDD projects with proper structure, configuration, and best practices.
"""

from .project_generator import (
    ProjectGenerator,
    ProjectTemplate,
    ProjectConfig,
    ScaffoldingResult,
)
from .domain_initializer import (
    DomainContextInitializer,
    BoundedContextConfig,
    DomainSetupResult,
)
from .templates import (
    get_default_project_templates,
    create_custom_project_template,
)

__all__ = [
    "ProjectGenerator",
    "ProjectTemplate", 
    "ProjectConfig",
    "ScaffoldingResult",
    "DomainContextInitializer",
    "BoundedContextConfig",
    "DomainSetupResult",
    "get_default_project_templates",
    "create_custom_project_template",
]