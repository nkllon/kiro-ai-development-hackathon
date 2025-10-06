"""
UI Configuration Package for Directus CMS

Modular components for systematic UI configuration with <300 lines per file.
Each component follows SRP with focused responsibility.

Requirements Addressed:
- 6.1-6.5: User interface excellence with relationship management
- 11.1-11.5: Modular component architecture with file size governance
"""

from .configurator import UIConfigurator
from .relationship_display import RelationshipDisplayManager
from .navigation import NavigationManager

__all__ = [
    "UIConfigurator",
    "RelationshipDisplayManager", 
    "NavigationManager"
]