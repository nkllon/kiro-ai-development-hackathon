"""
Error Prevention Package for Directus CMS

Modular components for comprehensive error prevention with <300 lines per file.
Each component follows SRP with focused error handling responsibility.

Requirements Addressed:
- 4.1-4.5: Comprehensive error prevention and recovery
- 11.1-11.5: Modular component architecture with file size governance
"""

from .error_prevention import ErrorPreventionOrchestrator
from .auth_validator import AuthenticationValidator
from .schema_validator import SchemaConsistencyValidator
from .api_handler import APIErrorHandler

__all__ = [
    "ErrorPreventionOrchestrator",
    "AuthenticationValidator",
    "SchemaConsistencyValidator", 
    "APIErrorHandler"
]