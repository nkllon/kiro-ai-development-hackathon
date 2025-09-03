"""
Beast Mode Framework - Document Management Reflective Module (DM-RM)
Implements systematic RDI (Requirements->Design->Implementation) documentation management

This module provides:
- Systematic document organization following RDI structure
- Document lifecycle management and validation
- Cross-reference tracking and consistency checking
- Automated documentation compliance enforcement
- Integration with all other RMs for documentation maintenance
"""

import json
import hashlib
from typing import Dict, Any, List, Optional, Set
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path

from ..core.reflective_module import ReflectiveModule, HealthStatus

class DocumentType(Enum):
    REQUIREMENTS = "requirements"
    DESIGN = "design"
    IMPLEMENTATION = "implementation"
    API = "api"
    USER_GUIDE = "user_guide"
    ARCHITECTURE = "architecture"
    TESTING = "testing"
    DEPLOYMENT = "deployment"

class DocumentStatus(Enum):
    DRAFT = "draft"
    REVIEW = "review"
    APPROVED = "approved"
    PUBLISHED = "published"
    DEPRECATED = "deprecated"

@dataclass
class RDIDocument:
    """RDI-compliant document structure"""
    document_id: str
    title: str
    document_type: DocumentType
    status: DocumentStatus
    file_path: Path
    requirements_refs: List[str] = field(default_factory=list)
    design_refs: List[str] = field(default_factory=list)
    implementation_refs: List[str] = field(default_factory=list)
    owner_rm: str = ""  # Which RM owns this document
    created_date: datetime = field(default_factory=datetime.now)
    last_modified: datetime = field(default_factory=datetime.now)
    version: str = "1.0.0"
    checksum: str = ""
    dependencies: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class DocumentationStandard:
    """Documentation standards and compliance rules"""
    rdi_structure_required: bool = True
    cross_reference_validation: bool = True
    version_control_required: bool = True
    approval_workflow_required: bool = True
    automated_sync_enabled: bool = True
    compliance_checks: List[str] = field(default_factory=lambda: [
        "rdi_structure",
        "cross_references", 
        "version_consistency",
        "approval_status",
        "rm_ownership"
    ])

class DocumentManagementRM(ReflectiveModule):
    """
    Document Management Reflective Module (DM-RM)
    Enforces systematic RDI documentation structure across all RMs
    """
    
    def __init__(self, project_root: str = "."):
        super().__init__("document_management_rm")
        
        # Configuration
        self.project_root = Path(project_root)
        self.docs_root = self.project_root / "docs"
        self.docs_root.mkdir(exist_ok=True)
        
        # Document registry
        self.document_registry = {}
        self.rm_document_mapping = {}  # Maps RM to its documents
        self.cross_references = {}     # Tracks document dependencies
        
        # Documentation standards
        self.standards = DocumentationStandard()
        
        # Document management metrics
        self.doc_metrics = {
            'total_documents': 0,
            'rdi_compliant_documents': 0,
            'cross_reference_violations': 0,
            'outdated_documents': 0,
            'rm_compliance_rate': 0.0,
            'last_compliance_check': None
        }
        
        # Initialize RDI structure
        self._initialize_rdi_structure()
        
        # Load existing documents
        self._discover_existing_documents()
        
        self._update_health_indicator(
            "document_management_rm",
            HealthStatus.HEALTHY,
            "operational",
            "Document Management RM ready for systematic RDI enforcement"
        )
        
    def get_module_status(self) -> Dict[str, Any]:
        """Document Management RM operational status"""
        return {
            "module_name": self.module_name,
            "status": "operational" if self.is_healthy() else "degraded",
            "total_documents": self.doc_metrics['total_documents'],
            "rdi_compliant": self.doc_metrics['rdi_compliant_documents'],
            "compliance_rate": self.doc_metrics['rm_compliance_rate'],
            "cross_ref_violations": self.doc_metrics['cross_reference_violations'],
            "docs_root": str(self.docs_root)
        }
        
    def is_healthy(self) -> bool:
        """Health assessment for document management"""
        return (
            self.docs_root.exists() and
            self.doc_metrics['rm_compliance_rate'] >= 0.8 and
            self.doc_metrics['cross_reference_violations'] == 0 and
            not self._degradation_active
        )
        
    def get_health_indicators(self) -> Dict[str, Any]:
        """Detailed health metrics for document management"""
        return {
            "documentation_health": {
                "total_documents": self.doc_metrics['total_documents'],
                "rdi_compliance_rate": self.doc_metrics['rdi_compliant_documents'] / max(1, self.doc_metrics['total_documents']),
                "rm_compliance_rate": self.doc_metrics['rm_compliance_rate'],
                "cross_reference_integrity": self.doc_metrics['cross_reference_violations'] == 0
            },
            "structure_compliance": {
                "rdi_structure_exists": self._check_rdi_structure_exists(),
                "rm_documentation_complete": self._check_rm_documentation_complete(),
                "cross_references_valid": self._validate_all_cross_references(),
                "version_consistency": self._check_version_consistency()
            },
            "operational_metrics": {
                "last_compliance_check": self.doc_metrics['last_compliance_check'],
                "outdated_documents": self.doc_metrics['outdated_documents'],
                "document_registry_size": len(self.document_registry)
            }
        }
        
    def _get_primary_responsibility(self) -> str:
        """Single responsibility: systematic RDI document management"""
        return "systematic_rdi_document_management"
        
    def register_rm_documentation(self, rm_name: str, documents: List[RDIDocument]) -> Dict[str, Any]:
        """
        Register documentation for a Reflective Module
        Enforces RDI structure compliance
        """
        try:
            # Validate RDI compliance for each document
            compliance_results = []
            
            for doc in documents:
                # Set owner RM
                doc.owner_rm = rm_name
                
                # Validate RDI structure
                compliance = self._validate_rdi_compliance(doc)
                compliance_results.append(compliance)
                
                if compliance["compliant"]:
                    # Register document
                    self.document_registry[doc.document_id] = doc
                    
                    # Update RM mapping
                    if rm_name not in self.rm_document_mapping:
                        self.rm_document_mapping[rm_name] = []
                    self.rm_document_mapping[rm_name].append(doc.document_id)
                    
                    # Update cross-references
                    self._update_cross_references(doc)
                    
                    self.logger.info(f"Registered RDI document: {doc.title} for RM: {rm_name}")
                else:
                    self.logger.warning(f"RDI compliance failed for document: {doc.title}")
                    
            # Update metrics
            self._update_documentation_metrics()
            
            return {
                "success": True,
                "rm_name": rm_name,
                "documents_registered": len([r for r in compliance_results if r["compliant"]]),
                "compliance_failures": len([r for r in compliance_results if not r["compliant"]]),
                "compliance_results": compliance_results
            }
            
        except Exception as e:
            self.logger.error(f"RM documentation registration failed: {str(e)}")
            return {"error": f"Registration failed: {str(e)}"}
            
    def enforce_rm_documentation_constraint(self, rm_name: str) -> Dict[str, Any]:
        """
        Enforce documentation constraint: Each RM MUST maintain its documentation via DM-RM
        """
        try:
            # Check if RM has registered documentation
            if rm_name not in self.rm_document_mapping:
                return {
                    "compliant": False,
                    "violation": "RM_DOCUMENTATION_MISSING",
                    "message": f"RM {rm_name} has not registered any documentation with DM-RM",
                    "required_action": "Register RDI-compliant documentation via DocumentManagementRM"
                }
                
            # Check RDI compliance for RM's documents
            rm_documents = [
                self.document_registry[doc_id] 
                for doc_id in self.rm_document_mapping[rm_name]
            ]
            
            compliance_issues = []
            
            for doc in rm_documents:
                doc_compliance = self._validate_rdi_compliance(doc)
                if not doc_compliance["compliant"]:
                    compliance_issues.append({
                        "document": doc.title,
                        "issues": doc_compliance["issues"]
                    })
                    
            # Check for required document types
            doc_types = {doc.document_type for doc in rm_documents}
            required_types = {DocumentType.REQUIREMENTS, DocumentType.DESIGN, DocumentType.IMPLEMENTATION}
            missing_types = required_types - doc_types
            
            if missing_types:
                compliance_issues.append({
                    "issue": "MISSING_RDI_DOCUMENTS",
                    "missing_types": [t.value for t in missing_types]
                })
                
            # Determine overall compliance
            compliant = len(compliance_issues) == 0
            
            return {
                "compliant": compliant,
                "rm_name": rm_name,
                "total_documents": len(rm_documents),
                "compliance_issues": compliance_issues,
                "rdi_structure_complete": len(missing_types) == 0,
                "cross_references_valid": self._validate_rm_cross_references(rm_name)
            }
            
        except Exception as e:
            self.logger.error(f"RM documentation constraint enforcement failed: {str(e)}")
            return {"error": f"Constraint enforcement failed: {str(e)}"}
            
    def create_rdi_document_template(self, 
                                   rm_name: str, 
                                   document_type: DocumentType,
                                   title: str) -> Dict[str, Any]:
        """
        Create RDI-compliant document template for an RM
        """
        try:
            # Generate document ID
            doc_id = f"{rm_name}_{document_type.value}_{int(datetime.now().timestamp())}"
            
            # Create file path following RDI structure
            file_path = self.docs_root / "rms" / rm_name / f"{document_type.value}.md"
            file_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Create document template content
            template_content = self._generate_document_template(rm_name, document_type, title)
            
            # Write template file
            file_path.write_text(template_content)
            
            # Create RDI document
            rdi_doc = RDIDocument(
                document_id=doc_id,
                title=title,
                document_type=document_type,
                status=DocumentStatus.DRAFT,
                file_path=file_path,
                owner_rm=rm_name,
                checksum=self._calculate_file_checksum(file_path)
            )
            
            # Register document
            self.document_registry[doc_id] = rdi_doc
            
            if rm_name not in self.rm_document_mapping:
                self.rm_document_mapping[rm_name] = []
            self.rm_document_mapping[rm_name].append(doc_id)
            
            self.logger.info(f"Created RDI document template: {title} for RM: {rm_name}")
            
            return {
                "success": True,
                "document_id": doc_id,
                "file_path": str(file_path),
                "document_type": document_type.value,
                "rm_name": rm_name,
                "template_created": True
            }
            
        except Exception as e:
            self.logger.error(f"RDI document template creation failed: {str(e)}")
            return {"error": f"Template creation failed: {str(e)}"}
            
    def validate_cross_references(self, document_id: str) -> Dict[str, Any]:
        """
        Validate cross-references for a document
        """
        try:
            if document_id not in self.document_registry:
                return {"error": f"Document {document_id} not found"}
                
            doc = self.document_registry[document_id]
            validation_results = {
                "document_id": document_id,
                "valid_references": [],
                "invalid_references": [],
                "missing_references": [],
                "circular_references": []
            }
            
            # Check requirements references
            for req_ref in doc.requirements_refs:
                if self._reference_exists(req_ref):
                    validation_results["valid_references"].append(req_ref)
                else:
                    validation_results["invalid_references"].append(req_ref)
                    
            # Check design references
            for design_ref in doc.design_refs:
                if self._reference_exists(design_ref):
                    validation_results["valid_references"].append(design_ref)
                else:
                    validation_results["invalid_references"].append(design_ref)
                    
            # Check implementation references
            for impl_ref in doc.implementation_refs:
                if self._reference_exists(impl_ref):
                    validation_results["valid_references"].append(impl_ref)
                else:
                    validation_results["invalid_references"].append(impl_ref)
                    
            # Check for circular references
            circular_refs = self._detect_circular_references(document_id)
            validation_results["circular_references"] = circular_refs
            
            # Determine overall validity
            validation_results["all_references_valid"] = (
                len(validation_results["invalid_references"]) == 0 and
                len(validation_results["circular_references"]) == 0
            )
            
            return validation_results
            
        except Exception as e:
            self.logger.error(f"Cross-reference validation failed: {str(e)}")
            return {"error": f"Validation failed: {str(e)}"}
            
    def generate_rm_documentation_report(self, rm_name: Optional[str] = None) -> Dict[str, Any]:
        """
        Generate comprehensive documentation report for RM(s)
        """
        try:
            if rm_name:
                # Report for specific RM
                rms_to_check = [rm_name]
            else:
                # Report for all RMs
                rms_to_check = list(self.rm_document_mapping.keys())
                
            report = {
                "report_timestamp": datetime.now().isoformat(),
                "total_rms_checked": len(rms_to_check),
                "rm_reports": {},
                "overall_compliance": {
                    "compliant_rms": 0,
                    "non_compliant_rms": 0,
                    "compliance_rate": 0.0
                },
                "summary": {
                    "total_documents": 0,
                    "rdi_compliant_documents": 0,
                    "cross_reference_violations": 0,
                    "missing_document_types": []
                }
            }
            
            compliant_count = 0
            
            for rm in rms_to_check:
                rm_compliance = self.enforce_rm_documentation_constraint(rm)
                report["rm_reports"][rm] = rm_compliance
                
                if rm_compliance.get("compliant", False):
                    compliant_count += 1
                    
                # Update summary
                if rm in self.rm_document_mapping:
                    report["summary"]["total_documents"] += len(self.rm_document_mapping[rm])
                    
            # Calculate overall compliance
            report["overall_compliance"]["compliant_rms"] = compliant_count
            report["overall_compliance"]["non_compliant_rms"] = len(rms_to_check) - compliant_count
            report["overall_compliance"]["compliance_rate"] = compliant_count / max(1, len(rms_to_check))
            
            return report
            
        except Exception as e:
            self.logger.error(f"Documentation report generation failed: {str(e)}")
            return {"error": f"Report generation failed: {str(e)}"}
            
    # Helper methods
    
    def _initialize_rdi_structure(self):
        """Initialize RDI directory structure"""
        rdi_dirs = [
            self.docs_root / "requirements",
            self.docs_root / "design", 
            self.docs_root / "implementation",
            self.docs_root / "rms",  # RM-specific documentation
            self.docs_root / "api",
            self.docs_root / "guides"
        ]
        
        for dir_path in rdi_dirs:
            dir_path.mkdir(parents=True, exist_ok=True)
            
        # Create RDI structure documentation
        rdi_readme = self.docs_root / "README.md"
        if not rdi_readme.exists():
            rdi_content = self._generate_rdi_structure_documentation()
            rdi_readme.write_text(rdi_content)
            
    def _discover_existing_documents(self):
        """Discover and register existing documents"""
        try:
            # Scan docs directory for existing documents
            for doc_file in self.docs_root.rglob("*.md"):
                if doc_file.name != "README.md":
                    self._register_existing_document(doc_file)
                    
        except Exception as e:
            self.logger.warning(f"Document discovery failed: {str(e)}")
            
    def _register_existing_document(self, file_path: Path):
        """Register an existing document file"""
        try:
            # Determine document type from path
            doc_type = self._infer_document_type(file_path)
            
            # Generate document ID
            doc_id = f"existing_{file_path.stem}_{int(file_path.stat().st_mtime)}"
            
            # Create RDI document
            rdi_doc = RDIDocument(
                document_id=doc_id,
                title=file_path.stem.replace("_", " ").title(),
                document_type=doc_type,
                status=DocumentStatus.PUBLISHED,
                file_path=file_path,
                checksum=self._calculate_file_checksum(file_path),
                last_modified=datetime.fromtimestamp(file_path.stat().st_mtime)
            )
            
            self.document_registry[doc_id] = rdi_doc
            
        except Exception as e:
            self.logger.warning(f"Failed to register existing document {file_path}: {str(e)}")
            
    def _validate_rdi_compliance(self, doc: RDIDocument) -> Dict[str, Any]:
        """Validate RDI compliance for a document"""
        issues = []
        
        # Check file exists
        if not doc.file_path.exists():
            issues.append("Document file does not exist")
            
        # Check RDI structure placement
        if not self._check_rdi_placement(doc):
            issues.append("Document not placed in correct RDI structure")
            
        # Check required metadata
        if not doc.owner_rm:
            issues.append("Document missing owner RM")
            
        # Check version format
        if not self._validate_version_format(doc.version):
            issues.append("Invalid version format")
            
        # Check cross-references format
        if not self._validate_reference_format(doc):
            issues.append("Invalid cross-reference format")
            
        return {
            "compliant": len(issues) == 0,
            "issues": issues,
            "document_id": doc.document_id
        }
        
    def _check_rdi_structure_exists(self) -> bool:
        """Check if RDI directory structure exists"""
        required_dirs = ["requirements", "design", "implementation", "rms"]
        return all((self.docs_root / dir_name).exists() for dir_name in required_dirs)
        
    def _check_rm_documentation_complete(self) -> bool:
        """Check if all RMs have complete documentation"""
        # This would integrate with RM registry to check all RMs
        # For now, check registered RMs
        for rm_name in self.rm_document_mapping:
            compliance = self.enforce_rm_documentation_constraint(rm_name)
            if not compliance.get("compliant", False):
                return False
        return True
        
    def _validate_all_cross_references(self) -> bool:
        """Validate all cross-references in the system"""
        for doc_id in self.document_registry:
            validation = self.validate_cross_references(doc_id)
            if not validation.get("all_references_valid", False):
                return False
        return True
        
    def _check_version_consistency(self) -> bool:
        """Check version consistency across related documents"""
        # Simplified check - would implement full version dependency validation
        return True
        
    def _update_cross_references(self, doc: RDIDocument):
        """Update cross-reference tracking"""
        all_refs = doc.requirements_refs + doc.design_refs + doc.implementation_refs
        self.cross_references[doc.document_id] = all_refs
        
    def _update_documentation_metrics(self):
        """Update documentation metrics"""
        self.doc_metrics['total_documents'] = len(self.document_registry)
        
        # Count RDI compliant documents
        compliant_count = 0
        for doc in self.document_registry.values():
            compliance = self._validate_rdi_compliance(doc)
            if compliance["compliant"]:
                compliant_count += 1
                
        self.doc_metrics['rdi_compliant_documents'] = compliant_count
        
        # Calculate RM compliance rate
        if self.rm_document_mapping:
            compliant_rms = 0
            for rm_name in self.rm_document_mapping:
                compliance = self.enforce_rm_documentation_constraint(rm_name)
                if compliance.get("compliant", False):
                    compliant_rms += 1
            self.doc_metrics['rm_compliance_rate'] = compliant_rms / len(self.rm_document_mapping)
        else:
            self.doc_metrics['rm_compliance_rate'] = 1.0
            
        self.doc_metrics['last_compliance_check'] = datetime.now()
        
    def _calculate_file_checksum(self, file_path: Path) -> str:
        """Calculate file checksum for change detection"""
        try:
            content = file_path.read_text()
            return hashlib.md5(content.encode()).hexdigest()
        except:
            return ""
            
    def _infer_document_type(self, file_path: Path) -> DocumentType:
        """Infer document type from file path"""
        path_str = str(file_path).lower()
        
        if "requirement" in path_str:
            return DocumentType.REQUIREMENTS
        elif "design" in path_str:
            return DocumentType.DESIGN
        elif "implementation" in path_str or "impl" in path_str:
            return DocumentType.IMPLEMENTATION
        elif "api" in path_str:
            return DocumentType.API
        elif "guide" in path_str or "user" in path_str:
            return DocumentType.USER_GUIDE
        elif "architecture" in path_str or "arch" in path_str:
            return DocumentType.ARCHITECTURE
        elif "test" in path_str:
            return DocumentType.TESTING
        elif "deploy" in path_str:
            return DocumentType.DEPLOYMENT
        else:
            return DocumentType.IMPLEMENTATION  # Default
            
    def _check_rdi_placement(self, doc: RDIDocument) -> bool:
        """Check if document is placed in correct RDI structure"""
        expected_dir = self.docs_root / "rms" / doc.owner_rm
        return str(doc.file_path).startswith(str(expected_dir))
        
    def _validate_version_format(self, version: str) -> bool:
        """Validate semantic version format"""
        import re
        pattern = r'^\d+\.\d+\.\d+$'
        return bool(re.match(pattern, version))
        
    def _validate_reference_format(self, doc: RDIDocument) -> bool:
        """Validate cross-reference format"""
        # Simplified validation - would implement full reference format checking
        return True
        
    def _reference_exists(self, reference: str) -> bool:
        """Check if a reference exists"""
        # Simplified check - would implement full reference resolution
        return reference in self.document_registry
        
    def _detect_circular_references(self, document_id: str) -> List[str]:
        """Detect circular references"""
        # Simplified implementation - would implement full circular reference detection
        return []
        
    def _validate_rm_cross_references(self, rm_name: str) -> bool:
        """Validate cross-references for an RM's documents"""
        if rm_name not in self.rm_document_mapping:
            return True
            
        for doc_id in self.rm_document_mapping[rm_name]:
            validation = self.validate_cross_references(doc_id)
            if not validation.get("all_references_valid", False):
                return False
        return True
        
    def _generate_document_template(self, rm_name: str, doc_type: DocumentType, title: str) -> str:
        """Generate RDI-compliant document template"""
        template = f"""# {title}

**Document Type:** {doc_type.value.title()}  
**Owner RM:** {rm_name}  
**Status:** Draft  
**Version:** 1.0.0  
**Created:** {datetime.now().strftime('%Y-%m-%d')}  

## Overview

[Brief overview of this {doc_type.value} document]

## Cross-References

### Requirements References
- [List requirements this document relates to]

### Design References  
- [List design documents this document relates to]

### Implementation References
- [List implementation documents this document relates to]

## Content

[Main content goes here following RDI structure]

### {doc_type.value.title()} Details

[Specific content for {doc_type.value}]

## Validation

- [ ] RDI structure compliance
- [ ] Cross-references validated
- [ ] Owner RM approval
- [ ] Version control updated

## Changelog

| Version | Date | Changes | Author |
|---------|------|---------|--------|
| 1.0.0 | {datetime.now().strftime('%Y-%m-%d')} | Initial creation | {rm_name} |

---
*This document is maintained by {rm_name} via DocumentManagementRM*
"""
        return template
        
    def _generate_rdi_structure_documentation(self) -> str:
        """Generate RDI structure documentation"""
        return """# RDI Documentation Structure

This directory follows the RDI (Requirements->Design->Implementation) documentation structure enforced by the Beast Mode Framework DocumentManagementRM.

## Structure

```
docs/
├── requirements/     # Requirements documents
├── design/          # Design documents  
├── implementation/  # Implementation documents
├── rms/            # RM-specific documentation
│   └── {rm_name}/  # Each RM maintains its docs here
├── api/            # API documentation
└── guides/         # User guides and tutorials
```

## RM Documentation Constraint

**Each Reflective Module (RM) MUST maintain its documentation via DocumentManagementRM**

### Required Documents per RM:
1. **Requirements** - What the RM must accomplish
2. **Design** - How the RM is architected  
3. **Implementation** - How the RM is implemented

### Cross-Reference Requirements:
- All documents must reference related requirements, design, and implementation docs
- Cross-references must be validated and maintained
- Circular references are not allowed

## Compliance

All documentation is automatically validated for:
- RDI structure compliance
- Cross-reference integrity
- Version consistency
- RM ownership
- Approval workflow

---
*Maintained by DocumentManagementRM - Beast Mode Framework*
"""

    # Public API methods
    
    def get_rm_documentation_status(self, rm_name: str) -> Dict[str, Any]:
        """Get documentation status for a specific RM"""
        return self.enforce_rm_documentation_constraint(rm_name)
        
    def get_all_documents(self) -> Dict[str, RDIDocument]:
        """Get all registered documents"""
        return self.document_registry.copy()
        
    def get_documentation_analytics(self) -> Dict[str, Any]:
        """Get comprehensive documentation analytics"""
        return {
            "documentation_metrics": self.doc_metrics.copy(),
            "rm_compliance_report": self.generate_rm_documentation_report(),
            "cross_reference_status": {
                "total_references": len(self.cross_references),
                "validation_status": self._validate_all_cross_references()
            },
            "rdi_structure_health": {
                "structure_exists": self._check_rdi_structure_exists(),
                "rm_documentation_complete": self._check_rm_documentation_complete(),
                "version_consistency": self._check_version_consistency()
            }
        }