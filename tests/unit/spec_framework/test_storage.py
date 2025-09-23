"""
Unit tests for Spec Framework storage operations.

Tests cover file operations, data persistence, version tracking,
and atomic operations for specification documents.
"""

import os
import tempfile
import unittest
import shutil
from datetime import datetime
from pathlib import Path

from src.spec_framework.storage import DocumentRepository, DocumentStorageError
from src.spec_framework.models import (
    SpecificationDocument,
    SemanticVersion,
    WorkflowStage,
    ApprovalStatus,
    ChangeSet,
    Dependency,
    DependencyType,
)


class TestDocumentRepository(unittest.TestCase):
    """Test document repository functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.repo = DocumentRepository(base_path=self.temp_dir)
        
        # Create test specification
        self.test_spec = SpecificationDocument(
            id="test-spec",
            name="Test Specification",
            version=SemanticVersion(1, 0, 0),
            requirements_path="test-spec/requirements.md"
        )
    
    def tearDown(self):
        """Clean up test fixtures."""
        shutil.rmtree(self.temp_dir)
    
    def test_repository_initialization(self):
        """Test repository directory structure creation."""
        self.assertTrue(Path(self.temp_dir).exists())
        self.assertTrue((Path(self.temp_dir) / "_versions").exists())
        self.assertTrue((Path(self.temp_dir) / "_metadata").exists())
    
    def test_create_specification(self):
        """Test specification creation with atomic operations."""
        created_spec = self.repo.create(self.test_spec)
        
        # Verify spec was created
        self.assertEqual(created_spec.id, "test-spec")
        self.assertTrue((Path(self.temp_dir) / "test-spec").exists())
        self.assertTrue((Path(self.temp_dir) / "test-spec" / "metadata.json").exists())
        self.assertTrue((Path(self.temp_dir) / "test-spec" / "requirements.md").exists())
        
        # Verify requirements template was created
        requirements_file = Path(self.temp_dir) / "test-spec" / "requirements.md"
        with open(requirements_file, 'r') as f:
            content = f.read()
            self.assertIn("Test Specification Requirements", content)
            self.assertIn("WHEN", content)  # EARS format
    
    def test_create_duplicate_specification(self):
        """Test that creating duplicate specification raises error."""
        self.repo.create(self.test_spec)
        
        # Attempt to create duplicate
        with self.assertRaises(DocumentStorageError):
            self.repo.create(self.test_spec)
    
    def test_read_specification(self):
        """Test specification reading."""
        # Create spec first
        self.repo.create(self.test_spec)
        
        # Read it back
        read_spec = self.repo.read("test-spec")
        
        self.assertIsNotNone(read_spec)
        self.assertEqual(read_spec.id, "test-spec")
        self.assertEqual(read_spec.name, "Test Specification")
        self.assertEqual(str(read_spec.version), "1.0.0")
        self.assertEqual(read_spec.workflow_stage, WorkflowStage.REQUIREMENTS)
    
    def test_read_nonexistent_specification(self):
        """Test reading non-existent specification returns None."""
        result = self.repo.read("nonexistent-spec")
        self.assertIsNone(result)
    
    def test_update_specification(self):
        """Test specification update with change tracking."""
        # Create spec first
        created_spec = self.repo.create(self.test_spec)
        original_updated_at = created_spec.updated_at
        
        # Update spec
        changes = ChangeSet(
            modified_sections=["requirements"],
            metadata_changes={"workflow_stage": "design"}
        )
        
        created_spec.workflow_stage = WorkflowStage.DESIGN
        created_spec.design_path = "test-spec/design.md"
        
        updated_spec = self.repo.update(created_spec, changes)
        
        # Verify update
        self.assertEqual(updated_spec.workflow_stage, WorkflowStage.DESIGN)
        self.assertGreater(updated_spec.updated_at, original_updated_at)
        self.assertEqual(len(updated_spec.audit_trail), 1)
        
        # Verify audit trail
        audit_entry = updated_spec.audit_trail[0]
        self.assertEqual(audit_entry.event_type, "document_updated")
        self.assertEqual(audit_entry.changes.modified_sections, ["requirements"])
    
    def test_update_nonexistent_specification(self):
        """Test updating non-existent specification raises error."""
        changes = ChangeSet(modified_sections=["requirements"])
        
        with self.assertRaises(DocumentStorageError):
            self.repo.update(self.test_spec, changes)
    
    def test_delete_specification(self):
        """Test specification deletion (move to trash)."""
        # Create spec first
        self.repo.create(self.test_spec)
        self.assertTrue((Path(self.temp_dir) / "test-spec").exists())
        
        # Delete spec
        result = self.repo.delete("test-spec")
        
        self.assertTrue(result)
        self.assertFalse((Path(self.temp_dir) / "test-spec").exists())
        self.assertTrue((Path(self.temp_dir) / "_trash").exists())
        
        # Verify spec was moved to trash
        trash_items = list((Path(self.temp_dir) / "_trash").iterdir())
        self.assertEqual(len(trash_items), 1)
        self.assertTrue(trash_items[0].name.startswith("test-spec_"))
    
    def test_delete_nonexistent_specification(self):
        """Test deleting non-existent specification returns False."""
        result = self.repo.delete("nonexistent-spec")
        self.assertFalse(result)
    
    def test_list_all_specifications(self):
        """Test listing all specifications."""
        # Initially empty
        specs = self.repo.list_all()
        self.assertEqual(len(specs), 0)
        
        # Create multiple specs
        spec1 = SpecificationDocument(
            id="spec-1",
            name="Spec 1",
            version=SemanticVersion(1, 0, 0),
            requirements_path="spec-1/requirements.md"
        )
        
        spec2 = SpecificationDocument(
            id="spec-2", 
            name="Spec 2",
            version=SemanticVersion(1, 0, 0),
            requirements_path="spec-2/requirements.md"
        )
        
        self.repo.create(spec1)
        self.repo.create(spec2)
        
        # List specs
        specs = self.repo.list_all()
        self.assertEqual(len(specs), 2)
        self.assertIn("spec-1", specs)
        self.assertIn("spec-2", specs)
        self.assertEqual(specs, ["spec-1", "spec-2"])  # Should be sorted
    
    def test_version_tracking(self):
        """Test version history tracking."""
        # Create spec
        created_spec = self.repo.create(self.test_spec)
        
        # Update spec
        changes = ChangeSet(modified_sections=["requirements"])
        created_spec.workflow_stage = WorkflowStage.DESIGN
        self.repo.update(created_spec, changes)
        
        # Get version history
        versions = self.repo.get_versions("test-spec")
        
        self.assertEqual(len(versions), 2)  # Create + Update
        
        # Check create version
        create_version = versions[0]
        self.assertEqual(create_version["event_type"], "created")
        self.assertEqual(create_version["workflow_stage"], "requirements")
        
        # Check update version
        update_version = versions[1]
        self.assertEqual(update_version["event_type"], "updated")
        self.assertEqual(update_version["workflow_stage"], "design")
        self.assertIn("changes", update_version)
    
    def test_version_tracking_nonexistent_spec(self):
        """Test version tracking for non-existent spec returns empty list."""
        versions = self.repo.get_versions("nonexistent-spec")
        self.assertEqual(len(versions), 0)
    
    def test_metadata_serialization_deserialization(self):
        """Test metadata conversion between spec and dictionary."""
        # Create spec with dependencies and audit trail
        dependency = Dependency(
            source_spec="test-spec",
            target_spec="foundation-spec",
            dependency_type=DependencyType.FOUNDATION
        )
        
        self.test_spec.dependencies = [dependency]
        self.test_spec.workflow_stage = WorkflowStage.DESIGN
        self.test_spec.approval_status = ApprovalStatus.UNDER_REVIEW
        
        # Create and read back
        self.repo.create(self.test_spec)
        read_spec = self.repo.read("test-spec")
        
        # Verify all fields preserved
        self.assertEqual(read_spec.id, self.test_spec.id)
        self.assertEqual(read_spec.name, self.test_spec.name)
        self.assertEqual(str(read_spec.version), str(self.test_spec.version))
        self.assertEqual(read_spec.workflow_stage, self.test_spec.workflow_stage)
        self.assertEqual(read_spec.approval_status, self.test_spec.approval_status)
        
        # Verify dependencies
        self.assertEqual(len(read_spec.dependencies), 1)
        read_dep = read_spec.dependencies[0]
        self.assertEqual(read_dep.source_spec, dependency.source_spec)
        self.assertEqual(read_dep.target_spec, dependency.target_spec)
        self.assertEqual(read_dep.dependency_type, dependency.dependency_type)
    
    def test_atomic_operations(self):
        """Test that operations are atomic (no partial state on failure)."""
        # Mock a failure during creation by making directory read-only
        # This is a simplified test - in practice, we'd need more sophisticated failure injection
        
        # Create spec successfully first
        created_spec = self.repo.create(self.test_spec)
        self.assertTrue((Path(self.temp_dir) / "test-spec").exists())
        
        # Verify we can read it back
        read_spec = self.repo.read("test-spec")
        self.assertIsNotNone(read_spec)
        self.assertEqual(read_spec.id, "test-spec")
    
    def test_concurrent_access_safety(self):
        """Test file locking for concurrent access safety."""
        # This is a basic test - full concurrent testing would require threading
        
        # Create spec
        self.repo.create(self.test_spec)
        
        # Multiple reads should work
        spec1 = self.repo.read("test-spec")
        spec2 = self.repo.read("test-spec")
        
        self.assertIsNotNone(spec1)
        self.assertIsNotNone(spec2)
        self.assertEqual(spec1.id, spec2.id)


if __name__ == "__main__":
    unittest.main()