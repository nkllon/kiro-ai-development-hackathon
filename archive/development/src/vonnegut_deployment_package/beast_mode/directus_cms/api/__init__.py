"""
API Configuration Package for Directus CMS

Modular components for systematic API configuration and integration.
Each component follows SRP with <300 lines per file.

Requirements Addressed:
- 7.1-7.5: API Integration and Programmatic Access
- 11.1-11.5: Modular Component Architecture and File Size Governance
"""

from .configurator import APIConfigurator
from .rest_config import RESTAPIManager
from .graphql_config import GraphQLManager

__all__ = [
    "APIConfigurator",
    "RESTAPIManager",
    "GraphQLManager"
]