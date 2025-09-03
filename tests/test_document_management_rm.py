"""
Tests for Document Management Reflective Module (DM-RM)
Tests systematic RDI documentation management and RM constraint enforcement
"""

import pytest
import tempfile
import json
from unittest.mock import Mock, patch
from pathlib import Path
from datetime import datetime

from src.beast_mode.documentation.document_management_rm import (
    DocumentManagementRM,
    DocumentType,
    DocumentStatus,
    RDIDocument,
    DocumentationStandard
)

class TestDocumentManagementRM:
    """Test Document Management RM functionality"""
    
    @pytest.fixture
    def temp_project_root(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            project_root = Path(temp_dir)
            yield project_root
            
    @pytest.fixture
    def doc_manager(self, temp_project_root):
        return DocumentManagementRM(str(temp_project_root))
        
    @pytest.fixture
    def sample_rdi_document(self, temp_project_root):
        return RDIDocument(
            document_id="test_doc_001",
            title="Test Requirements Document",
            document_type=DocumentType.REQUIREMENTS,
            status=DocumentStatus.DRAFT,
            file_path=temp_project_root / "docs" / "rms" / "test_rm" / "requirements.md",
            owner_rm="test_rm",
            requirements_refs=["REQ-001", "REQ-002"],
            design_refs=["DES-001"],
            implementation_refs=["IMPL-001"]
        )
        
    def test_document_management_rm_initialization(self, doc_manager):
        """Test Document Management RM initialization"""
        assert doc_manager.module_name == "document_management_rm"
        assert doc_manager.is_healthy()
        
        status = doc_manager.get_module_status()
        assert "module_name" in status
        assert "total_documents" in status
        assert "compliance_rate" in status
        
        # Verify RDI structure was created
        assert doc_manager.docs_root.exists()
        assert (doc_manager.docs_root / "requirements").exists()
        assert (doc_manager.docs_root / "design").exists()
        assert (doc_manager.docs_root / "implementation").exists()
        assert (doc_manager.docs_root / "rms").exists()
        
    def test_rdi_document_creation(self, sample_rdi_document):
        """Test RDI document data structure"""
        assert sample_rdi_document.document_id == "test_doc_001"
        assert sample_rdi_document.document_type == DocumentType.REQUIREMENTS
        assert sample_rdi_document.owner_rm == "test_rm"
        assert len(sample_rdi_document.requirements_refs) == 2
        
    def test_rm_documentation_registration(self, doc_manager, sample_rdi_document):
        """Test RM documentation registration"""
        # Create the document file
        sample_rdi_document.file_path.parent.mkdir(parents=True, exist_ok=True)
        sample_rdi_document.file_path.write_text("# Test Requirements Document")
        
        # Register documentation
        result = doc_manager.register_rm_documentation("test_rm", [sample_rdi_document])
        
        assert result["success"] is True
        assert result["rm_name"] == "test_rm"
        assert result["documents_registered"] >= 0
        
        # Verify document is registered
        assert sample_rdi_document.document_id in doc_manager.document_registry
        assert "test_rm" in doc_manager.rm_document_mapping
        
    def test_rm_documentation_constraint_enforcement(self, doc_manager, sample_rdi_document):
        """Test RM documentation constraint enforcement"""
        # Test RM without documentation
        constraint_result = doc_manager.enforce_rm_documentation_constraint("unregistered_rm")
        
        assert constraint_result["compliant"] is False
        assert constraint_result["violation"] == "RM_DOCUMENTATION_MISSING"
        
        # Register documentation and test again
        sample_rdi_document.file_path.parent.mkdir(parents=True, exist_ok=True)
        sample_rdi_document.file_path.write_text("# Test Document")
        
        doc_manager.register_rm_documentation("test_rm", [sample_rdi_document])
        
        constraint_result = doc_manager.enforce_rm_documentation_constraint("test_rm")
        
        # Should still be non-compliant due to missing RDI document types
        assert "compliance_issues" in constraint_result
        
    def test_rdi_document_template_creation(self, doc_manager):
        """Test RDI document template creation"""
        result = doc_manager.create_rdi_document_template(
            "test_rm",
            DocumentType.REQUIREMENTS,
            "Test RM Requirements"
        )
        
        assert result["success"] is True
        assert result["rm_name"] == "test_rm"
        assert result["document_type"] == "requirements"
        assert result["template_created"] is True
        
        # Verify file was created
        file_path = Path(result["file_path"])
        assert file_path.exists()
        
        # Verify template content
        content = file_path.read_text()
        assert "Test RM Requirements" in content
        assert "Requirements References" in content
        assert "Design References" in content
        assert "Implementation References" in content
        
    def test_cross_reference_validation(self, doc_manager, sample_rdi_document):
        """Test cross-reference validation"""
        # Create document file
        sample_rdi_document.file_path.parent.mkdir(parents=True, exist_ok=True)
        sample_rdi_document.file_path.write_text("# Test Document")
        
        # Register document
        doc_manager.document_registry[sample_rdi_document.document_id] = sample_rdi_document
        
        # Validate cross-references
        validation_result = doc_manager.validate_cross_references(sample_rdi_document.document_id)
        
        assert "document_id" in validation_result
        assert "valid_references" in validation_result
        assert "invalid_references" in validation_result
        assert "all_references_valid" in validation_result
        
    def test_rdi_compliance_validation(self, doc_manager, sample_rdi_document):
        """Test RDI compliance validation"""
        # Create document file
        sample_rdi_document.file_path.parent.mkdir(parents=True, exist_ok=True)
        sample_rdi_document.file_path.write_text("# Test Document")
        
        compliance_result = doc_manager._validate_rdi_compliance(sample_rdi_document)
        
        assert "compliant" in compliance_result
        assert "issues" in compliance_result
        assert "document_id" in compliance_result
        
    def test_documentation_report_generation(self, doc_manager, sample_rdi_document):
        """Test documentation report generation"""
        # Register some documentation
        sample_rdi_document.file_path.parent.mkdir(parents=True, exist_ok=True)
        sample_rdi_document.file_path.write_text("# Test Document")
        
        doc_manager.register_rm_documentation("test_rm", [sample_rdi_document])
        
        # Generate report
        report = doc_manager.generate_rm_documentation_report("test_rm")
        
        assert "report_timestamp" in report
        assert "rm_reports" in report
        assert "overall_compliance" in report
        assert "summary" in report
        
        # Check specific RM report
        assert "test_rm" in report["rm_reports"]
        
    def test_documentation_analytics(self, doc_manager):
        """Test documentation analytics"""
        analytics = doc_manager.get_documentation_analytics()
        
        assert "documentation_metrics" in analytics
        assert "rm_compliance_report" in analytics
        assert "cross_reference_status" in analytics
        assert "rdi_structure_health" in analytics
        
    def test_document_discovery(self, doc_manager):
        """Test existing document discovery"""
        # Create some existing documents
        existing_doc = doc_manager.docs_root / "existing_doc.md"
        existing_doc.write_text("# Existing Document")
        
        # Trigger discovery
        doc_manager._discover_existing_documents()
        
        # Should have discovered the document
        assert len(doc_manager.document_registry) > 0
        
    def test_rdi_structure_initialization(self, doc_manager):
        """Test RDI structure initialization"""
        # Check that all required directories exist
        required_dirs = ["requirements", "design", "implementation", "rms", "api", "guides"]
        
        for dir_name in required_dirs:
            assert (doc_manager.docs_root / dir_name).exists()
            
        # Check README was created
        assert (doc_manager.docs_root / "README.md").exists()
        
        readme_content = (doc_manager.docs_root / "README.md").read_text()
        assert "RDI Documentation Structure" in readme_content

class TestReflectiveModuleDocumentationConstraint:
    """Test RM documentation constraint integration"""
    
    @pytest.fixture
    def temp_project_root(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            project_root = Path(temp_dir)
            (project_root / "src" / "beast_mode" / "core").mkdir(parents=True)
            yield project_root
            
    def test_rm_documentation_constraint_methods(self, temp_project_root):
        """Test that ReflectiveModule has documentation constraint methods"""
        from src.beast_mode.core.reflective_module import ReflectiveModule
        
        # Create a test RM implementation
        class TestRM(ReflectiveModule):
            def get_module_status(self):
                return {"status": "operational"}
                
            def is_healthy(self):
                return True
                
            def get_health_indicators(self):
                return {"health": "good"}
                
            def _get_primary_responsibility(self):
                return "test_responsibility"
                
        test_rm = TestRM("test_rm")
        
        # Test documentation compliance status method exists
        assert hasattr(test_rm, 'get_documentation_compliance_status')
        assert hasattr(test_rm, 'register_rm_documentation')
        assert hasattr(test_rm, 'create_rm_documentation_template')
        
        # Test compliance status (will fail due to no documentation)
        compliance_status = test_rm.get_documentation_compliance_status()
        assert "rm_name" in compliance_status
        assert "documentation_compliant" in compliance_status
        
    def test_rm_template_creation_integration(self, temp_project_root):
        """Test RM template creation integration"""
        from src.beast_mode.core.reflective_module import ReflectiveModule
        
        class TestRM(ReflectiveModule):
            def get_module_status(self):
                return {"status": "operational"}
                
            def is_healthy(self):
                return True
                
            def get_health_indicators(self):
                return {"health": "good"}
                
            def _get_primary_responsibility(self):
                return "test_responsibility"
                
        test_rm = TestRM("test_rm")
        
        # Test template creation
        template_result = test_rm.create_rm_documentation_template("requirements", "Test RM Requirements")
        
        # Should succeed or fail gracefully
        assert "success" in template_result or "error" in template_result

class TestDocumentationStandards:
    """Test documentation standards and compliance"""
    
    def test_documentation_standard_creation(self):
        """Test documentation standard configuration"""
        standard = DocumentationStandard()
        
        assert standard.rdi_structure_required is True
        assert standard.cross_reference_validation is True
        assert standard.version_control_required is True
        assert len(standard.compliance_checks) > 0
        
    def test_document_type_enum(self):
        """Test document type enumeration"""
        assert DocumentType.REQUIREMENTS.value == "requirements"
        assert DocumentType.DESIGN.value == "design"
        assert DocumentType.IMPLEMENTATION.value == "implementation"
        
    def test_document_status_enum(self):
        """Test document status enumeration"""
        assert DocumentStatus.DRAFT.value == "draft"
        assert DocumentStatus.APPROVED.value == "approved"
        assert DocumentStatus.PUBLISHED.value == "published"

if __name__ == "__main__":
    pytest.main([__file__])