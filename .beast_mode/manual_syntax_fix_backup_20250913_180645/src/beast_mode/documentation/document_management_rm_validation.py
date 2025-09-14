"""
Document Management Rm Validation

This module was extracted from document_management_rm.py
as part of RM-DDD compliance refactoring.
"""

import json
import hashlib
from typing import Dict, Any, List, Optional, Set
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from ..core.reflective_module import ReflectiveModule, HealthStatus
import re

def validate_cross_references(self, document_id: str) -> Dict[str, Any]:
    """
        Validate cross-references for a document
        """
    try:
        if document_id not in self.document_registry:
            return {'error': f'Document {document_id} not found'}
        doc = self.document_registry[document_id]
        validation_results = {'document_id': document_id, 'valid_references': [], 'invalid_references': [], 'missing_references': [], 'circular_references': []}
        for req_ref in doc.requirements_refs:
            if self._reference_exists(req_ref):
                validation_results['valid_references'].append(req_ref)
            else:
                validation_results['invalid_references'].append(req_ref)
        for design_ref in doc.design_refs:
            if self._reference_exists(design_ref):
                validation_results['valid_references'].append(design_ref)
            else:
                validation_results['invalid_references'].append(design_ref)
        for impl_ref in doc.implementation_refs:
            if self._reference_exists(impl_ref):
                validation_results['valid_references'].append(impl_ref)
            else:
                validation_results['invalid_references'].append(impl_ref)
        circular_refs = self._detect_circular_references(document_id)
        validation_results['circular_references'] = circular_refs
        validation_results['all_references_valid'] = len(validation_results['invalid_references']) == 0 and len(validation_results['circular_references']) == 0
        return validation_results
    except Exception as e:
        self.logger.error(f'Cross-reference validation failed: {str(e)}')
        return {'error': f'Validation failed: {str(e)}'}

def _validate_rdi_compliance(self, doc: RDIDocument) -> Dict[str, Any]:
    """Validate RDI compliance for a document"""
    issues = []
    if not doc.file_path.exists():
        issues.append('Document file does not exist')
    if not self._check_rdi_placement(doc):
        issues.append('Document not placed in correct RDI structure')
    if not doc.owner_rm:
        issues.append('Document missing owner RM')
    if not self._validate_version_format(doc.version):
        issues.append('Invalid version format')
    if not self._validate_reference_format(doc):
        issues.append('Invalid cross-reference format')
    return {'compliant': len(issues) == 0, 'issues': issues, 'document_id': doc.document_id}

def _check_rdi_structure_exists(self) -> bool:
    """Check if RDI directory structure exists"""
    required_dirs = ['requirements', 'design', 'implementation', 'rms']
    return all(((self.docs_root / dir_name).exists() for dir_name in required_dirs))

def _check_rm_documentation_complete(self) -> bool:
    """Check if all RMs have complete documentation"""
    for rm_name in self.rm_document_mapping:
        compliance = self.enforce_rm_documentation_constraint(rm_name)
        if not compliance.get('compliant', False):
            return False
    return True

def _validate_all_cross_references(self) -> bool:
    """Validate all cross-references in the system"""
    for doc_id in self.document_registry:
        validation = self.validate_cross_references(doc_id)
        if not validation.get('all_references_valid', False):
            return False
    return True

def _check_version_consistency(self) -> bool:
    """Check version consistency across related documents"""
    return True

def _calculate_file_checksum(self, file_path: Path) -> str:
    """Calculate file checksum for change detection"""
    try:
        content = file_path.read_text()
        return hashlib.md5(content.encode()).hexdigest()
    except:
        return ''

def _check_rdi_placement(self, doc: RDIDocument) -> bool:
    """Check if document is placed in correct RDI structure"""
    expected_dir = self.docs_root / 'rms' / doc.owner_rm
    return str(doc.file_path).startswith(str(expected_dir))

def _validate_version_format(self, version: str) -> bool:
    """Validate semantic version format"""
    import re
    pattern = '^\\d+\\.\\d+\\.\\d+$'
    return bool(re.match(pattern, version))

def _validate_reference_format(self, doc: RDIDocument) -> bool:
    """Validate cross-reference format"""
    return True

def _validate_rm_cross_references(self, rm_name: str) -> bool:
    """Validate cross-references for an RM's documents"""
    if rm_name not in self.rm_document_mapping:
        return True
    for doc_id in self.rm_document_mapping[rm_name]:
        validation = self.validate_cross_references(doc_id)
        if not validation.get('all_references_valid', False):
            return False
    return True
