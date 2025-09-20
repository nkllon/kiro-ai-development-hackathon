"""
UI Configuration Package for Directus CMS

Modular components for systematic UI configuration and relationship management.
Each component follows SRP with <300 lines per file.

Requirements Addressed:
- 6.1-6.5: User Interface Excellence with Relationship Management
- 11.1-11.5: Modular Component Architecture and File Size Governance
"""

from .configurator import UIConfigurator
from .relationship_display import RelationshipDisplayManager
from .navigation import NavigationManager

__all__ = [
    "UIConfigurator",
    "RelationshipDisplayManager", 
    "NavigationManager"
]