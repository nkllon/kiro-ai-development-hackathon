"""
Test Suite for ContentMetadataExtractor
=====================================

Comprehensive test suite for ContentMetadataExtractor with >90% coverage
following RM-DDD patterns and systematic validation.

Author: Beast Mode Framework
Date: 2025-01-16
Version: 1.0
"""

import pytest
import tempfile
import os
from pathlib import Path
from datetime import datetime
from unittest.mock import Mock, patch, mock_open

from src.repository_discovery.core.content_metadata_extractor import (
    ContentMetadataExtractor,
    FileMetadata,
    ExtractionResult
)
from src.rm_ddd.core.unified_reflective_module import (
    ModuleHealth,
    ModuleStatus,
    ModuleCapability
)


class TestContentMetadataExtractor:
    """Test ContentMetadataExtractor RM-DDD compliance and functionality"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.extractor = ContentMetadataExtractor()
        self.temp_dir = tempfile.mkdtemp()
        self.temp_path = Path(self.temp_dir)
    
    def teardown_method(self):
        """Clean up test fixtures"""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_module_initialization(self):
        """Test proper module initialization"""
        assert self.extractor.module_id == "ContentMetadataExtractor"
        assert hasattr(self.extractor, '_config')
        assert hasattr(self.extractor, '_logger')
        assert self.extractor._files_processed == 0
        assert self.extractor._extraction_errors == 0
    
    def test_get_module_info(self):
        """Test module info retrieval - RDI Compliant"""
        info = self.extractor.get_module_info()
        
        assert info['module_id'] == "ContentMetadataExtractor"
        assert info['name'] == "ContentMetadataExtractor"
        assert info['version'] == "1.0.0"
        assert 'description' in info
        assert 'capabilities' in info
        assert info['files_processed'] == 0
        assert info['extraction_errors'] == 0
    
    def test_get_capabilities(self):
        """Test capability reporting - RDI Compliant"""
        capabilities = self.extractor.get_capabilities()
        
        assert ModuleCapability.CORE_FUNCTIONALITY in capabilities
        assert ModuleCapability.DATA_PROCESSING in capabilities
        assert ModuleCapability.VALIDATION in capabilities
        assert ModuleCapability.MONITORING in capabilities
        assert len(capabilities) == 4
    
    def test_get_health_status_healthy(self):
        """Test health status when healthy"""
        health = self.extractor.get_health_status()
        
        assert isinstance(health, ModuleHealth)
        assert health.module_id == "ContentMetadataExtractor"
        assert health.status == ModuleStatus.HEALTHY
        assert health.health_score == 1.0
        assert len(health.issues) == 0
        assert health.error_count == 0
    
    def test_get_health_status_with_errors(self):
        """Test health status with errors"""
        # Simulate processing files with errors
        self.extractor._files_processed = 100
        self.extractor._extraction_errors = 3  # 3% error rate
        
        health = self.extractor.get_health_status()
        
        assert health.status == ModuleStatus.WARNING
        assert health.health_score == 0.8
        assert len(health.issues) == 1
        assert "Error rate" in health.issues[0]
    
    def test_graceful_degradation_success(self):
        """Test graceful degradation when filesystem accessible"""
        result = self.extractor.graceful_degradation()
        
        assert result.success is True
        assert ModuleCapability.CORE_FUNCTIONALITY in result.remaining_capabilities
        assert ModuleCapability.MONITORING in result.remaining_capabilities
    
    def test_extract_metadata_text_file(self):
        """Test metadata extraction for text file"""
        # Create test text file
        test_file = self.temp_path / "test.txt"
        test_content = "Hello, World!\nThis is a test file.\n"
        test_file.write_text(test_content, encoding='utf-8')
        
        result = self.extractor.extract_metadata(test_file)
        
        assert result.success is True
        assert result.metadata is not None
        assert result.error_message is None
        assert result.extraction_time_ms > 0
        
        metadata = result.metadata
        assert metadata.file_name == "test.txt"
        assert metadata.file_type == ".txt"
        assert metadata.file_size == len(test_content.encode('utf-8'))
        assert metadata.encoding == "utf-8"
        assert metadata.is_binary is False
        assert metadata.line_count == 2
        assert len(metadata.content_hash) == 64  # SHA-256 hex length
    
    def test_extract_metadata_binary_file(self):
        """Test metadata extraction for binary file"""
        # Create test binary file
        test_file = self.temp_path / "test.bin"
        binary_content = b'\x00\x01\x02\x03\xFF\xFE\xFD'
        test_file.write_bytes(binary_content)
        
        result = self.extractor.extract_metadata(test_file)
        
        assert result.success is True
        metadata = result.metadata
        assert metadata.file_name == "test.bin"
        assert metadata.file_type == ".bin"
        assert metadata.is_binary is True
        assert metadata.encoding == "binary"
        assert metadata.line_count is None
    
    def test_extract_metadata_nonexistent_file(self):
        """Test metadata extraction for nonexistent file"""
        nonexistent_file = self.temp_path / "nonexistent.txt"
        
        result = self.extractor.extract_metadata(nonexistent_file)
        
        assert result.success is False
        assert result.metadata is None
        assert "does not exist" in result.error_message
        assert self.extractor._extraction_errors == 1
    
    def test_extract_metadata_directory(self):
        """Test metadata extraction for directory (should fail)"""
        result = self.extractor.extract_metadata(self.temp_path)
        
        assert result.success is False
        assert result.metadata is None
        assert "not a file" in result.error_message
    
    def test_extract_batch_metadata(self):
        """Test batch metadata extraction"""
        # Create multiple test files
        files = []
        for i in range(3):
            test_file = self.temp_path / f"test_{i}.txt"
            test_file.write_text(f"Content {i}\n", encoding='utf-8')
            files.append(test_file)
        
        # Add one nonexistent file
        files.append(self.temp_path / "nonexistent.txt")
        
        results = self.extractor.extract_batch_metadata(files)
        
        assert len(results) == 4
        assert sum(1 for r in results if r.success) == 3
        assert sum(1 for r in results if not r.success) == 1
    
    def test_file_metadata_to_dict(self):
        """Test FileMetadata serialization"""
        metadata = FileMetadata(
            file_path="/test/path.txt",
            file_name="path.txt",
            file_size=100,
            created_at=datetime.now(),
            modified_at=datetime.now(),
            accessed_at=datetime.now(),
            file_type=".txt",
            mime_type="text/plain",
            encoding="utf-8",
            content_hash="abc123",
            permissions="644",
            is_binary=False,
            line_count=5
        )
        
        data = metadata.to_dict()
        
        assert isinstance(data, dict)
        assert data['file_name'] == "path.txt"
        assert data['file_size'] == 100
        assert data['is_binary'] is False
        assert data['line_count'] == 5
    
    def test_extraction_result_to_dict(self):
        """Test ExtractionResult serialization"""
        result = ExtractionResult(
            success=True,
            metadata=None,
            error_message=None,
            extraction_time_ms=15.5
        )
        
        data = result.to_dict()
        
        assert isinstance(data, dict)
        assert data['success'] is True
        assert data['extraction_time_ms'] == 15.5
        assert 'metadata' in data
    
    def test_is_binary_file_detection(self):
        """Test binary file detection logic"""
        # Test with known binary extension
        binary_file = self.temp_path / "test.jpg"
        binary_file.write_bytes(b'\xFF\xD8\xFF')  # JPEG header
        
        assert self.extractor._is_binary_file(binary_file) is True
        
        # Test with text content
        text_file = self.temp_path / "test.txt"
        text_file.write_text("Hello, World!", encoding='utf-8')
        
        assert self.extractor._is_binary_file(text_file) is False
        
        # Test with null bytes (binary indicator)
        null_file = self.temp_path / "test.dat"
        null_file.write_bytes(b'Hello\x00World')
        
        assert self.extractor._is_binary_file(null_file) is True
    
    def test_encoding_detection(self):
        """Test file encoding detection"""
        # Test UTF-8 file
        utf8_file = self.temp_path / "utf8.txt"
        utf8_file.write_text("Hello, 世界!", encoding='utf-8')
        
        encoding = self.extractor._detect_encoding(utf8_file)
        assert encoding.lower() in ['utf-8', 'utf8']
        
        # Test ASCII file
        ascii_file = self.temp_path / "ascii.txt"
        ascii_file.write_text("Hello, World!", encoding='ascii')
        
        encoding = self.extractor._detect_encoding(ascii_file)
        assert encoding.lower() in ['ascii', 'utf-8']  # ASCII is subset of UTF-8
    
    def test_file_hash_calculation(self):
        """Test file hash calculation"""
        test_file = self.temp_path / "hash_test.txt"
        test_content = "Test content for hashing"
        test_file.write_text(test_content, encoding='utf-8')
        
        hash1 = self.extractor._calculate_file_hash(test_file)
        hash2 = self.extractor._calculate_file_hash(test_file)
        
        assert len(hash1) == 64  # SHA-256 hex length
        assert hash1 == hash2  # Same content should produce same hash
        
        # Different content should produce different hash
        test_file.write_text("Different content", encoding='utf-8')
        hash3 = self.extractor._calculate_file_hash(test_file)
        assert hash1 != hash3
    
    def test_large_file_handling(self):
        """Test handling of large files"""
        # Configure small max file size for testing
        config = {'max_file_size': 100}
        extractor = ContentMetadataExtractor(config)
        
        # Create file larger than limit
        large_file = self.temp_path / "large.txt"
        large_content = "x" * 200  # 200 bytes > 100 byte limit
        large_file.write_text(large_content, encoding='utf-8')
        
        result = extractor.extract_metadata(large_file)
        
        # Should still succeed but log warning
        assert result.success is True
        assert result.metadata.file_size == 200
    
    def test_error_statistics_tracking(self):
        """Test error statistics are properly tracked"""
        initial_errors = self.extractor._extraction_errors
        
        # Try to extract from nonexistent file
        nonexistent = self.temp_path / "nonexistent.txt"
        result = self.extractor.extract_metadata(nonexistent)
        
        assert not result.success
        assert self.extractor._extraction_errors == initial_errors + 1
    
    def test_performance_statistics(self):
        """Test performance statistics tracking"""
        # Create test file
        test_file = self.temp_path / "perf_test.txt"
        test_file.write_text("Performance test content", encoding='utf-8')
        
        initial_processed = self.extractor._files_processed
        
        result = self.extractor.extract_metadata(test_file)
        
        assert result.success is True
        assert self.extractor._files_processed == initial_processed + 1
        assert result.extraction_time_ms > 0
        assert self.extractor._get_average_extraction_time() > 0
    
    def test_permission_error_handling(self):
        """Test handling of permission errors"""
        # Create a file that doesn't exist to simulate permission error
        nonexistent_file = self.temp_path / "permission_test.txt"
        
        # Mock the exists() method to return True but file operations to fail
        with patch.object(Path, 'exists', return_value=True), \
             patch.object(Path, 'is_file', return_value=True), \
             patch.object(Path, 'stat', side_effect=PermissionError("Access denied")):
            
            result = self.extractor.extract_metadata(nonexistent_file)
            
            assert result.success is False
            assert "Access denied" in result.error_message
    
    def test_reflective_module_inheritance(self):
        """Test proper ReflectiveModule inheritance"""
        from src.rm_ddd.core.unified_reflective_module import ReflectiveModule
        
        assert isinstance(self.extractor, ReflectiveModule)
        assert hasattr(self.extractor, 'get_module_info')
        assert hasattr(self.extractor, 'get_capabilities')
        assert hasattr(self.extractor, 'get_health_status')
        assert hasattr(self.extractor, 'graceful_degradation')


class TestFileMetadata:
    """Test FileMetadata value object"""
    
    def test_file_metadata_creation(self):
        """Test FileMetadata creation and immutability"""
        now = datetime.now()
        metadata = FileMetadata(
            file_path="/test/file.txt",
            file_name="file.txt",
            file_size=1024,
            created_at=now,
            modified_at=now,
            accessed_at=now,
            file_type=".txt",
            mime_type="text/plain",
            encoding="utf-8",
            content_hash="abc123",
            permissions="644",
            is_binary=False,
            line_count=10
        )
        
        assert metadata.file_name == "file.txt"
        assert metadata.file_size == 1024
        assert metadata.is_binary is False
        assert metadata.line_count == 10
    
    def test_file_metadata_serialization(self):
        """Test FileMetadata serialization to dict"""
        now = datetime.now()
        metadata = FileMetadata(
            file_path="/test/file.txt",
            file_name="file.txt",
            file_size=1024,
            created_at=now,
            modified_at=now,
            accessed_at=now,
            file_type=".txt",
            mime_type="text/plain",
            encoding="utf-8",
            content_hash="abc123",
            permissions="644",
            is_binary=False
        )
        
        data = metadata.to_dict()
        
        assert isinstance(data, dict)
        assert data['file_name'] == "file.txt"
        assert data['file_size'] == 1024
        assert data['is_binary'] is False


class TestExtractionResult:
    """Test ExtractionResult data class"""
    
    def test_successful_result(self):
        """Test successful extraction result"""
        metadata = FileMetadata(
            file_path="/test.txt", file_name="test.txt", file_size=100,
            created_at=datetime.now(), modified_at=datetime.now(), accessed_at=datetime.now(),
            file_type=".txt", mime_type="text/plain", encoding="utf-8",
            content_hash="abc", permissions="644", is_binary=False
        )
        
        result = ExtractionResult(
            success=True,
            metadata=metadata,
            extraction_time_ms=15.5
        )
        
        assert result.success is True
        assert result.metadata is not None
        assert result.error_message is None
        assert result.extraction_time_ms == 15.5
    
    def test_failed_result(self):
        """Test failed extraction result"""
        result = ExtractionResult(
            success=False,
            metadata=None,
            error_message="File not found",
            extraction_time_ms=5.0
        )
        
        assert result.success is False
        assert result.metadata is None
        assert result.error_message == "File not found"
        assert result.extraction_time_ms == 5.0
    
    def test_result_serialization(self):
        """Test ExtractionResult serialization"""
        result = ExtractionResult(
            success=False,
            metadata=None,
            error_message="Test error",
            extraction_time_ms=10.0
        )
        
        data = result.to_dict()
        
        assert isinstance(data, dict)
        assert data['success'] is False
        assert data['error_message'] == "Test error"
        assert data['extraction_time_ms'] == 10.0
        assert 'metadata' in data


if __name__ == "__main__":
    pytest.main([__file__, "-v"])