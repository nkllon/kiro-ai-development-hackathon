"""
Unit tests for SporeManager
"""

import json
import pytest
import tempfile
import shutil
from datetime import datetime
from pathlib import Path
from unittest.mock import patch, mock_open

from src.beast_mode.messaging.spore_manager import (
    SporeManager, 
    SporeMetadata, 
    SporeContent
)


@pytest.fixture
def temp_spore_dir():
    """Create a temporary directory for spore testing"""
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    shutil.rmtree(temp_dir)


@pytest.fixture
def spore_manager(temp_spore_dir):
    """Create a SporeManager instance with temporary directory"""
    return SporeManager(spore_directory=temp_spore_dir)


@pytest.fixture
def sample_spore_content():
    """Sample spore implementation content"""
    return '''
def execute(context):
    """Sample spore execution function"""
    return {"status": "success", "result": "Hello from spore!"}

class SampleSpore:
    """Sample spore class"""
    
    def __init__(self):
        self.name = "sample_spore"
    
    def run(self):
        return execute({})
'''


@pytest.fixture
def sample_metadata():
    """Sample spore metadata"""
    return {
        "name": "sample_spore",
        "version": "1.0.0",
        "author": "test_agent",
        "description": "A sample spore for testing",
        "tags": ["test", "sample"],
        "capabilities_required": ["python_execution"],
        "validation_criteria": {"syntax_check": True}
    }


class TestSporeManager:
    """Test cases for SporeManager"""
    
    def test_init_creates_directories(self, temp_spore_dir):
        """Test that SporeManager creates required directories"""
        manager = SporeManager(spore_directory=temp_spore_dir)
        
        assert manager.spore_directory.exists()
        assert manager.metadata_dir.exists()
        assert manager.content_dir.exists()
        assert manager.versions_dir.exists()
    
    def test_save_spore_success(self, spore_manager, sample_spore_content, sample_metadata):
        """Test successful spore saving"""
        spore_name = spore_manager.save_spore(sample_spore_content, sample_metadata)
        
        assert spore_name == "sample_spore"
        assert spore_name in spore_manager._spore_cache
        
        # Check files were created
        metadata_path, content_path = spore_manager._get_spore_paths(spore_name)
        assert metadata_path.exists()
        assert content_path.exists()
    
    def test_save_spore_invalid_metadata(self, spore_manager, sample_spore_content):
        """Test spore saving with invalid metadata"""
        invalid_metadata = {"invalid": "metadata"}
        
        with pytest.raises(ValueError, match="Invalid spore metadata"):
            spore_manager.save_spore(sample_spore_content, invalid_metadata)
    
    def test_save_spore_invalid_content(self, spore_manager, sample_metadata):
        """Test spore saving with invalid content"""
        invalid_content = "invalid python syntax {"
        
        with pytest.raises(ValueError, match="Spore validation failed"):
            spore_manager.save_spore(invalid_content, sample_metadata)
    
    def test_load_spore_success(self, spore_manager, sample_spore_content, sample_metadata):
        """Test successful spore loading"""
        # Save spore first
        spore_name = spore_manager.save_spore(sample_spore_content, sample_metadata)
        
        # Clear cache to test disk loading
        spore_manager._spore_cache.clear()
        
        # Load spore
        loaded_spore = spore_manager.load_spore(spore_name)
        
        assert loaded_spore is not None
        assert loaded_spore['metadata']['name'] == spore_name
        assert loaded_spore['implementation'] == sample_spore_content
    
    def test_load_spore_not_found(self, spore_manager):
        """Test loading non-existent spore"""
        result = spore_manager.load_spore("nonexistent_spore")
        assert result is None
    
    def test_list_spores(self, spore_manager, sample_spore_content, sample_metadata):
        """Test listing spores"""
        # Save multiple spores
        spore1_metadata = sample_metadata.copy()
        spore1_metadata["name"] = "spore1"
        
        spore2_metadata = sample_metadata.copy()
        spore2_metadata["name"] = "spore2"
        
        spore_manager.save_spore(sample_spore_content, spore1_metadata)
        spore_manager.save_spore(sample_spore_content, spore2_metadata)
        
        spores = spore_manager.list_spores()
        
        assert len(spores) == 2
        spore_names = [spore['name'] for spore in spores]
        assert "spore1" in spore_names
        assert "spore2" in spore_names
    
    def test_validate_spore_valid_content(self, spore_manager, sample_spore_content):
        """Test spore validation with valid content"""
        assert spore_manager.validate_spore(sample_spore_content) is True
    
    def test_validate_spore_syntax_error(self, spore_manager):
        """Test spore validation with syntax error"""
        invalid_content = "def invalid_function("
        assert spore_manager.validate_spore(invalid_content) is False
    
    def test_validate_spore_missing_structure(self, spore_manager):
        """Test spore validation with missing required structure"""
        minimal_content = "x = 1"
        assert spore_manager.validate_spore(minimal_content) is False
    
    def test_validate_spore_dangerous_patterns(self, spore_manager):
        """Test spore validation with dangerous patterns"""
        dangerous_content = '''
def execute(context):
    import os
    os.system("rm -rf /")
    return {"status": "success"}
'''
        # Should still validate but log warning
        assert spore_manager.validate_spore(dangerous_content) is True
    
    def test_checksum_calculation(self, spore_manager):
        """Test checksum calculation"""
        content = "test content"
        checksum1 = spore_manager._calculate_checksum(content)
        checksum2 = spore_manager._calculate_checksum(content)
        
        assert checksum1 == checksum2
        assert len(checksum1) == 64  # SHA-256 hex length
    
    def test_version_backup_creation(self, spore_manager, sample_spore_content, sample_metadata):
        """Test version backup creation"""
        # Save initial spore
        spore_name = spore_manager.save_spore(sample_spore_content, sample_metadata)
        
        # Save updated version
        updated_metadata = sample_metadata.copy()
        updated_metadata["version"] = "2.0.0"
        spore_manager.save_spore(sample_spore_content, updated_metadata)
        
        # Check versions
        versions = spore_manager.get_spore_versions(spore_name)
        assert len(versions) >= 1
    
    def test_delete_spore(self, spore_manager, sample_spore_content, sample_metadata):
        """Test spore deletion"""
        spore_name = spore_manager.save_spore(sample_spore_content, sample_metadata)
        
        # Verify spore exists
        assert spore_name in spore_manager._spore_cache
        
        # Delete spore
        result = spore_manager.delete_spore(spore_name)
        
        assert result is True
        assert spore_name not in spore_manager._spore_cache
        
        # Check files are deleted
        metadata_path, content_path = spore_manager._get_spore_paths(spore_name)
        assert not metadata_path.exists()
        assert not content_path.exists()
    
    def test_search_spores_by_name(self, spore_manager, sample_spore_content, sample_metadata):
        """Test searching spores by name"""
        spore_manager.save_spore(sample_spore_content, sample_metadata)
        
        results = spore_manager.search_spores("sample")
        assert len(results) == 1
        assert results[0]['name'] == "sample_spore"
    
    def test_search_spores_by_tags(self, spore_manager, sample_spore_content, sample_metadata):
        """Test searching spores by tags"""
        spore_manager.save_spore(sample_spore_content, sample_metadata)
        
        results = spore_manager.search_spores("", tags=["test"])
        assert len(results) == 1
        assert results[0]['name'] == "sample_spore"
    
    def test_update_spore_stats(self, spore_manager, sample_spore_content, sample_metadata):
        """Test updating spore usage statistics"""
        spore_name = spore_manager.save_spore(sample_spore_content, sample_metadata)
        
        # Update stats for successful execution
        spore_manager.update_spore_stats(spore_name, success=True)
        
        spore = spore_manager._spore_cache[spore_name]
        assert spore.metadata.usage_count == 1
        assert spore.metadata.success_rate == 1.0
        
        # Update stats for failed execution
        spore_manager.update_spore_stats(spore_name, success=False)
        
        assert spore.metadata.usage_count == 2
        assert spore.metadata.success_rate == 0.5
    
    def test_export_spore(self, spore_manager, sample_spore_content, sample_metadata, temp_spore_dir):
        """Test spore export"""
        spore_name = spore_manager.save_spore(sample_spore_content, sample_metadata)
        export_path = Path(temp_spore_dir) / "exported_spore.json"
        
        result = spore_manager.export_spore(spore_name, str(export_path))
        
        assert result is True
        assert export_path.exists()
        
        # Verify exported content
        with open(export_path, 'r') as f:
            exported_data = json.load(f)
        
        assert exported_data['metadata']['name'] == spore_name
        assert exported_data['implementation'] == sample_spore_content
    
    def test_import_spore(self, spore_manager, sample_spore_content, sample_metadata, temp_spore_dir):
        """Test spore import"""
        # Create export file
        export_data = {
            'metadata': sample_metadata,
            'implementation': sample_spore_content
        }
        
        import_path = Path(temp_spore_dir) / "import_spore.json"
        with open(import_path, 'w') as f:
            json.dump(export_data, f, default=str)
        
        # Import spore
        imported_name = spore_manager.import_spore(str(import_path))
        
        assert imported_name == "sample_spore"
        assert imported_name in spore_manager._spore_cache
    
    def test_import_spore_file_not_found(self, spore_manager):
        """Test importing non-existent file"""
        result = spore_manager.import_spore("nonexistent_file.json")
        assert result is None
    
    def test_load_existing_spores_on_init(self, temp_spore_dir, sample_spore_content, sample_metadata):
        """Test loading existing spores when initializing SporeManager"""
        # Create a spore manager and save a spore
        manager1 = SporeManager(spore_directory=temp_spore_dir)
        spore_name = manager1.save_spore(sample_spore_content, sample_metadata)
        
        # Create new manager with same directory
        manager2 = SporeManager(spore_directory=temp_spore_dir)
        
        # Should load existing spore
        assert spore_name in manager2._spore_cache
    
    def test_checksum_verification_on_load(self, spore_manager, sample_spore_content, sample_metadata):
        """Test checksum verification when loading spores"""
        spore_name = spore_manager.save_spore(sample_spore_content, sample_metadata)
        
        # Modify content file to corrupt checksum
        _, content_path = spore_manager._get_spore_paths(spore_name)
        with open(content_path, 'w') as f:
            f.write("corrupted content")
        
        # Clear cache and reload
        spore_manager._spore_cache.clear()
        
        # Should still load but log warning
        loaded_spore = spore_manager.load_spore(spore_name)
        assert loaded_spore is not None


class TestSporeMetadata:
    """Test cases for SporeMetadata model"""
    
    def test_spore_metadata_creation(self):
        """Test SporeMetadata creation with valid data"""
        metadata = SporeMetadata(
            name="test_spore",
            version="1.0.0",
            author="test_author",
            description="Test spore"
        )
        
        assert metadata.name == "test_spore"
        assert metadata.version == "1.0.0"
        assert metadata.author == "test_author"
        assert metadata.description == "Test spore"
        assert isinstance(metadata.created_at, datetime)
    
    def test_spore_metadata_defaults(self):
        """Test SporeMetadata default values"""
        metadata = SporeMetadata(
            name="test",
            version="1.0",
            author="author",
            description="desc"
        )
        
        assert metadata.tags == []
        assert metadata.capabilities_required == []
        assert metadata.compatibility_version == "1.0"
        assert metadata.usage_count == 0
        assert metadata.success_rate == 0.0


class TestSporeContent:
    """Test cases for SporeContent model"""
    
    def test_spore_content_creation(self):
        """Test SporeContent creation"""
        metadata = SporeMetadata(
            name="test",
            version="1.0",
            author="author",
            description="desc"
        )
        
        content = SporeContent(
            metadata=metadata,
            implementation="def execute(): pass"
        )
        
        assert content.metadata == metadata
        assert content.implementation == "def execute(): pass"
        assert content.validation_tests == []
        assert content.examples == []
        assert content.dependencies == []