"""
Content Metadata Extractor - Repository Discovery System
======================================================

Systematically extracts metadata from repository files including size, dates, 
encoding, and basic relationships. Implements RM-DDD patterns with complete 
monitoring integration.

Author: Beast Mode Framework
Date: 2025-01-16
Version: 1.0
"""

import os
import hashlib
import mimetypes
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List, Optional, Set
from dataclasses import dataclass, asdict
import logging
try:
    import chardet
except ImportError:
    chardet = None

# Import unified ReflectiveModule
from src.rm_ddd.core.unified_reflective_module import (
    ReflectiveModule, 
    ModuleHealth, 
    ModuleStatus, 
    ModuleCapability,
    GracefulDegradationResult
)


@dataclass
class FileMetadata:
    """Value object for file metadata - immutable and complete"""
    file_path: str
    file_name: str
    file_size: int
    created_at: datetime
    modified_at: datetime
    accessed_at: datetime
    file_type: str
    mime_type: str
    encoding: str
    content_hash: str
    permissions: str
    is_binary: bool
    line_count: Optional[int] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return asdict(self)


@dataclass
class ExtractionResult:
    """Result of metadata extraction operation"""
    success: bool
    metadata: Optional[FileMetadata]
    error_message: Optional[str] = None
    extraction_time_ms: float = 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        result = {
            'success': self.success,
            'error_message': self.error_message,
            'extraction_time_ms': self.extraction_time_ms,
            'metadata': self.metadata.to_dict() if self.metadata else None
        }
        return result


class ContentMetadataExtractor(ReflectiveModule):
    """
    Content Metadata Extractor - RM-DDD Compliant
    
    Systematically extracts comprehensive metadata from repository files
    with complete error handling and monitoring integration.
    
    Single Responsibility: Extract file metadata with systematic error handling
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        super().__init__()
        self.module_id = "ContentMetadataExtractor"
        self._config = config or {}
        self._logger = logging.getLogger(f"repository_discovery.{self.__class__.__name__}")
        
        # Configuration
        self._max_file_size = self._config.get('max_file_size', 100 * 1024 * 1024)  # 100MB
        self._supported_encodings = self._config.get('supported_encodings', ['utf-8', 'latin-1', 'ascii'])
        self._binary_extensions = self._config.get('binary_extensions', {
            '.jpg', '.jpeg', '.png', '.gif', '.pdf', '.zip', '.tar', '.gz',
            '.exe', '.dll', '.so', '.dylib', '.bin', '.dat'
        })
        
        # Statistics
        self._files_processed = 0
        self._extraction_errors = 0
        self._total_extraction_time = 0.0
        
        self._logger.info(f"ContentMetadataExtractor initialized with config: {self._config}")
    
    def get_module_info(self) -> Dict[str, Any]:
        """Get module information - RDI Compliant"""
        return {
            "module_id": self.module_id,
            "name": "ContentMetadataExtractor",
            "version": "1.0.0",
            "description": "Systematic file metadata extraction with RM-DDD compliance",
            "capabilities": [cap.value for cap in self.get_capabilities()],
            "files_processed": self._files_processed,
            "extraction_errors": self._extraction_errors,
            "average_extraction_time_ms": self._get_average_extraction_time()
        }
    
    def get_capabilities(self) -> List[ModuleCapability]:
        """Get module capabilities - RDI Compliant"""
        return [
            ModuleCapability.CORE_FUNCTIONALITY,
            ModuleCapability.DATA_PROCESSING,
            ModuleCapability.VALIDATION,
            ModuleCapability.MONITORING
        ]
    
    def get_health_status(self) -> ModuleHealth:
        """Get module health status - RDI Compliant"""
        # Calculate health score based on error rate
        if self._files_processed == 0:
            health_score = 1.0
            status = ModuleStatus.HEALTHY
            issues = []
        else:
            error_rate = self._extraction_errors / self._files_processed
            if error_rate < 0.01:  # Less than 1% error rate
                health_score = 1.0
                status = ModuleStatus.HEALTHY
                issues = []
            elif error_rate < 0.05:  # Less than 5% error rate
                health_score = 0.8
                status = ModuleStatus.WARNING
                issues = [f"Error rate: {error_rate:.2%}"]
            else:
                health_score = 0.5
                status = ModuleStatus.ERROR
                issues = [f"High error rate: {error_rate:.2%}"]
        
        return ModuleHealth(
            module_id=self.module_id,
            status=status,
            health_score=health_score,
            issues=issues,
            last_check=datetime.now(),
            uptime_seconds=(datetime.now() - self._start_time).total_seconds(),
            error_count=self._extraction_errors,
            warning_count=0
        )
    
    def graceful_degradation(self) -> GracefulDegradationResult:
        """Perform graceful degradation - RDI Compliant"""
        try:
            # In degraded mode, we can still extract basic file stats
            degraded_capabilities = []
            remaining_capabilities = [
                ModuleCapability.CORE_FUNCTIONALITY,
                ModuleCapability.MONITORING
            ]
            
            # Test if we can still access filesystem
            test_path = Path(".")
            if not test_path.exists():
                degraded_capabilities.append(ModuleCapability.DATA_PROCESSING)
                remaining_capabilities = [ModuleCapability.MONITORING]
            
            return GracefulDegradationResult(
                success=True,
                degraded_capabilities=degraded_capabilities,
                remaining_capabilities=remaining_capabilities
            )
        except Exception as e:
            return GracefulDegradationResult(
                success=False,
                degraded_capabilities=[ModuleCapability.CORE_FUNCTIONALITY],
                remaining_capabilities=[],
                error_message=str(e)
            )
    
    def extract_metadata(self, file_path: Path) -> ExtractionResult:
        """
        Extract comprehensive metadata from a file
        
        Args:
            file_path: Path to file for metadata extraction
            
        Returns:
            ExtractionResult with metadata or error information
        """
        with self.trace_operation("extract_metadata", file_path=str(file_path)) as trace:
            start_time = datetime.now()
            
            try:
                self._update_activity()
                
                # Validate file exists and is accessible
                if not file_path.exists():
                    self._extraction_errors += 1
                    result = ExtractionResult(
                        success=False,
                        metadata=None,
                        error_message=f"File does not exist: {file_path}"
                    )
                    trace.output_result = result.to_dict()
                    return result
                
                if not file_path.is_file():
                    self._extraction_errors += 1
                    result = ExtractionResult(
                        success=False,
                        metadata=None,
                        error_message=f"Path is not a file: {file_path}"
                    )
                    trace.output_result = result.to_dict()
                    return result
                
                # Get file stats
                stat_info = file_path.stat()
                
                # Check file size limits
                if stat_info.st_size > self._max_file_size:
                    self._increment_warning_count()
                    self._logger.warning(f"File exceeds size limit: {file_path} ({stat_info.st_size} bytes)")
                
                # Extract basic metadata
                metadata = self._extract_basic_metadata(file_path, stat_info)
                
                # Extract content-specific metadata
                self._extract_content_metadata(file_path, metadata)
                
                # Calculate extraction time
                extraction_time = (datetime.now() - start_time).total_seconds() * 1000
                
                # Update statistics
                self._files_processed += 1
                self._total_extraction_time += extraction_time
                
                self._logger.debug(f"Successfully extracted metadata for {file_path} in {extraction_time:.2f}ms")
                
                result = ExtractionResult(
                    success=True,
                    metadata=metadata,
                    extraction_time_ms=extraction_time
                )
                
                # Store result in trace
                trace.output_result = result.to_dict()
                
                return result
                
            except Exception as e:
                self._extraction_errors += 1
                extraction_time = (datetime.now() - start_time).total_seconds() * 1000
                
                self._logger.error(f"Failed to extract metadata for {file_path}: {e}")
                
                result = ExtractionResult(
                    success=False,
                    metadata=None,
                    error_message=str(e),
                    extraction_time_ms=extraction_time
                )
                
                # Store error result in trace
                trace.output_result = result.to_dict()
                
                return result
    
    def _extract_basic_metadata(self, file_path: Path, stat_info) -> FileMetadata:
        """Extract basic file system metadata"""
        # Get MIME type
        mime_type, _ = mimetypes.guess_type(str(file_path))
        if not mime_type:
            mime_type = 'application/octet-stream'
        
        # Determine if file is binary
        is_binary = self._is_binary_file(file_path)
        
        # Get file hash
        content_hash = self._calculate_file_hash(file_path)
        
        # Get encoding for text files
        encoding = self._detect_encoding(file_path) if not is_binary else 'binary'
        
        return FileMetadata(
            file_path=str(file_path.resolve()),
            file_name=file_path.name,
            file_size=stat_info.st_size,
            created_at=datetime.fromtimestamp(stat_info.st_ctime),
            modified_at=datetime.fromtimestamp(stat_info.st_mtime),
            accessed_at=datetime.fromtimestamp(stat_info.st_atime),
            file_type=file_path.suffix.lower(),
            mime_type=mime_type,
            encoding=encoding,
            content_hash=content_hash,
            permissions=oct(stat_info.st_mode)[-3:],
            is_binary=is_binary
        )
    
    def _extract_content_metadata(self, file_path: Path, metadata: FileMetadata) -> None:
        """Extract content-specific metadata (modifies metadata in place)"""
        if not metadata.is_binary and metadata.file_size < self._max_file_size:
            try:
                # Count lines for text files
                with open(file_path, 'r', encoding=metadata.encoding, errors='ignore') as f:
                    metadata.line_count = sum(1 for _ in f)
            except Exception as e:
                self._logger.warning(f"Could not count lines for {file_path}: {e}")
                metadata.line_count = None
    
    def _is_binary_file(self, file_path: Path) -> bool:
        """Determine if file is binary"""
        # Check extension first
        if file_path.suffix.lower() in self._binary_extensions:
            return True
        
        # Sample first 1024 bytes to check for binary content
        try:
            with open(file_path, 'rb') as f:
                chunk = f.read(1024)
                if b'\x00' in chunk:  # Null bytes indicate binary
                    return True
                # Check for high ratio of non-printable characters
                printable_chars = sum(1 for byte in chunk if 32 <= byte <= 126 or byte in [9, 10, 13])
                if len(chunk) > 0 and printable_chars / len(chunk) < 0.7:
                    return True
        except Exception:
            return True  # Assume binary if we can't read it
        
        return False
    
    def _detect_encoding(self, file_path: Path) -> str:
        """Detect file encoding"""
        try:
            if chardet is not None:
                with open(file_path, 'rb') as f:
                    raw_data = f.read(min(10000, file_path.stat().st_size))  # Sample first 10KB
                    result = chardet.detect(raw_data)
                    encoding = result.get('encoding', 'utf-8')
                    
                    # Validate encoding is supported
                    if encoding and encoding.lower() in [enc.lower() for enc in self._supported_encodings]:
                        return encoding.lower()
                    else:
                        return 'utf-8'  # Default fallback
            else:
                # Fallback encoding detection without chardet
                return self._detect_encoding_fallback(file_path)
        except Exception:
            return 'utf-8'  # Default fallback
    
    def _detect_encoding_fallback(self, file_path: Path) -> str:
        """Fallback encoding detection without chardet"""
        # Try common encodings in order
        for encoding in self._supported_encodings:
            try:
                with open(file_path, 'r', encoding=encoding) as f:
                    f.read(1024)  # Try to read first 1KB
                return encoding
            except UnicodeDecodeError:
                continue
        return 'utf-8'  # Final fallback
    
    def _calculate_file_hash(self, file_path: Path) -> str:
        """Calculate SHA-256 hash of file content"""
        try:
            hash_sha256 = hashlib.sha256()
            with open(file_path, 'rb') as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_sha256.update(chunk)
            return hash_sha256.hexdigest()
        except Exception as e:
            self._logger.warning(f"Could not calculate hash for {file_path}: {e}")
            return ""
    
    def _get_average_extraction_time(self) -> float:
        """Calculate average extraction time in milliseconds"""
        if self._files_processed == 0:
            return 0.0
        return self._total_extraction_time / self._files_processed
    
    def extract_batch_metadata(self, file_paths: List[Path]) -> List[ExtractionResult]:
        """
        Extract metadata for multiple files in batch
        
        Args:
            file_paths: List of file paths to process
            
        Returns:
            List of ExtractionResult objects
        """
        with self.trace_operation("extract_batch_metadata", file_count=len(file_paths)) as trace:
            results = []
            
            self._logger.info(f"Starting batch metadata extraction for {len(file_paths)} files")
            
            for file_path in file_paths:
                result = self.extract_metadata(file_path)
                results.append(result)
            
            success_count = sum(1 for r in results if r.success)
            self._logger.info(f"Batch extraction complete: {success_count}/{len(file_paths)} successful")
            
            # Store batch results in trace
            trace.output_result = {
                'total_files': len(file_paths),
                'successful': success_count,
                'failed': len(file_paths) - success_count,
                'success_rate': success_count / len(file_paths) if file_paths else 0
            }
            
            return results