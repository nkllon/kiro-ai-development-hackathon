"""
Spec Scrub Ingestion

Transforms unstructured requirements from outside the Fort into EARS-compliant format.
Handles the brownfield reality of messy requirements and provides systematic
gateway into structured specification development.
"""

from .unstructured_requirements_ingester import (
    UnstructuredRequirementsIngester,
    RequirementSource,
    UnstructuredRequirement,
    EARSRequirement
)

__all__ = [
    'UnstructuredRequirementsIngester',
    'RequirementSource', 
    'UnstructuredRequirement',
    'EARSRequirement'
]