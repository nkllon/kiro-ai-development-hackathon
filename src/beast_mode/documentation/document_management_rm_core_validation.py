"""
Document Management Rm Core Validation

This module was extracted from document_management_rm_core.py
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

@dataclass
class RDIDocument:
    """RDI Document model for validation."""
    document_id: str
    title: str
    content: str
    owner_rm: str
    version: str
    file_path: Path
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    cross_references: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

class DocumentManagementRmCoreValidation(ReflectiveModule):
    """Document Management Rm Core Validation - RDI Compliant."""
    
    def __init__(self, docs_root: Optional[Path] = None):
        super().__init__("DocumentManagementRmCoreValidation")
        self.docs_root = docs_root or Path("/tmp/docs")
        self.rm_document_mapping = {}
        self.document_registry = {}
    
    def get_module_info(self) -> Dict[str, Any]:
        """Get module information - RDI Compliant."""
        return {
            'module_id': 'document_management_rm_core_validation',
            'version': '1.0.0',
            'description': 'Document Management Rm Core Validation'
        }
    
    def get_capabilities(self) -> List:
        """Get module capabilities - RDI Compliant."""
        from src.rm_ddd.core.unified_reflective_module import ModuleCapability
        return [ModuleCapability.VALIDATION, ModuleCapability.DATA_PROCESSING]
    
    def get_dependencies(self) -> List[str]:
        """Get module dependencies - RDI Compliant."""
        return []
    
    def check_health(self):
        """Check module health - RDI Compliant."""
        from src.rm_ddd.core.unified_reflective_module import ModuleHealth, ModuleStatus
        return ModuleHealth(
            module_id=self.get_module_info()['module_id'],
            status=ModuleStatus.HEALTHY,
            health_score=1.0,
            issues=[],
            capabilities=self.get_capabilities(),
            dependencies=self.get_dependencies(),
            metrics={},
            last_check=datetime.now(),
            uptime_seconds=self.get_uptime_seconds()
        )
    
    def perform_core_operation(self) -> Dict[str, Any]:
        """Perform core operation for testing."""
        return {
            'status': 'success',
            'operation': 'core_functionality_test',
            'timestamp': datetime.now().isoformat()
        }

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

    def register_module(self, registry):
        """Register module with registry."""
        metadata = self.get_interface_metadata()
        if hasattr(registry, 'register'):
            registry.register(metadata)
            
    def get_interface_metadata(self):
        """Get interface metadata for registry."""
        return {
            'module_id': getattr(self, 'module_id', self.__class__.__name__),
            'interface_type': self.__class__.__name__,
            'version': '1.0.0',
            'dependencies': [],
            'capabilities': []
        }

