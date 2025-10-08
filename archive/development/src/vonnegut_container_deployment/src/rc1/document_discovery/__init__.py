"""
Document Discovery Package
=========================

Implements the Document Discovery DAG component for scanning, analyzing,
and classifying all documents in the repository.
"""

from .document_scanner import DocumentScanner, Document, DocumentMetadata

__all__ = ["DocumentScanner", "Document", "DocumentMetadata"]
