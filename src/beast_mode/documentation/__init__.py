"""
Beast Mode Framework - Documentation Module
Implements systematic document management with RDI (Requirements->Design->Implementation) structure
"""

from .document_management_rm import (
    DocumentManagementRM,
    DocumentType,
    DocumentStatus,
    RDIDocument,
    DocumentationStandard
)

__all__ = [
    'DocumentManagementRM',
    'DocumentType',
    'DocumentStatus', 
    'RDIDocument',
    'DocumentationStandard'
]