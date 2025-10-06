"""
Patch Discovery and Scanning Engine

This module provides comprehensive scanning capabilities for discovering patch annotations
across codebases, with support for multiple file types and configurable scanning patterns.
"""

import os
import fnmatch
from pathlib import Path
from typing import List, Dict, Set, Optional, Any, Generator, Tuple
from dataclasses import dataclass, field
from concurrent.futures import ThreadPoolExecutor, as_completed
import logging

from src.rm_ddd.core.unified_reflective_module import ReflectiveModule
from ..core.models import PatchAnnotation, ExtractionResult, AnnotationParser


@dataclass
class ScanConfiguration:
    """Configuration for patch scanning operations."""
    
    # File patterns to include/exclude
    include_patterns: List[str] = field(default_factory=lambda: [
        "*.py", "*.js", "*.ts", "*.java", "*.cpp", "*.c", "*.h", "*.hpp",
        "*.yml", "*.yaml", "*.json", "*.xml", "*.ini", "*.conf", "*.config",
        "*.md", "*.rst", "*.txt", "Dockerfile", "Makefile", "*.sh", "*.bat"
    ])
    exclude_patterns: List[str] = field(default_factory=lambda: [
        "*.pyc", "*.pyo", "*.pyd", "__pycache__/*", ".git/*", ".svn/*",
        "node_modules/*", "venv/*", ".venv/*", "env/*", ".env/*",
        "*.log", "*.tmp", "*.temp", ".DS_Store", "Thumbs.db"
    ])
    
    # Directory patterns to exclude
    exclude_directories: Set[str] = field(default_factory=lambda: {
        ".git", ".svn", ".hg", "__pycache__", "node_modules", 
        "venv", ".venv", "env", ".env", "build", "dist", ".pytest_cache"
    })
    
    # Scanning behavior
    max_file_size_mb: float = 10.0  # Skip files larger than this
    max_depth: Optional[int] = None  # Maximum directory depth (None = unlimited)
    follow_symlinks: bool = False
    parallel_scanning: bool = True
    max_workers: int = 4
    
    # Content filtering
    skip_binary_files: bool = True
    encoding: str = "utf-8"
    encoding_errors: str = "ignore"


@dataclass
class ScanResult:
    """Result of a patch scanning operation."""
    
    # Scan statistics
    files_scanned: int = 0
    files_skipped: int = 0
    total_patches_found: int = 0
    scan_duration_seconds: float = 0.0
    
    # Results by file
    file_results: Dict[str, ExtractionResult] = field(default_factory=dict)
    
    # Aggregated errors
    scan_errors: List[str] = field(default_factory=list)
    
    # Metadata
    scan_configuration: Optional[ScanConfiguration] = None
    root_path: str = ""
    
    def get_all_patches(self) -> List[PatchAnnotation]:
        """Get all patches found across all files."""
        all_patches = []
        for result in self.file_results.values():
            all_patches.extend(result.patches)
        return all_patches
    
    def get_patches_by_component(self) -> Dict[str, List[PatchAnnotation]]:
        """Group patches by component."""
        by_component = {}
        for patch in self.get_all_patches():
            component = patch.component or "unknown"
            if component not in by_component:
                by_component[component] = []
            by_component[component].append(patch)
        return by_component
    
    def get_patches_by_debt_level(self) -> Dict[str, List[PatchAnnotation]]:
        """Group patches by debt level."""
        by_debt_level = {}
        for patch in self.get_all_patches():
            level = patch.debt_level.value
            if level not in by_debt_level:
                by_debt_level[level] = []
            by_debt_level[level].append(patch)
        return by_debt_level


class PatchScanner(ReflectiveModule):
    """
    Comprehensive patch discovery and scanning engine.
    
    This scanner recursively searches through codebases to find patch annotations,
    with support for multiple file types, configurable patterns, and parallel processing.
    """
    
    def __init__(self, config: Optional[ScanConfiguration] = None):
        """
        Initialize the patch scanner.
        
        Args:
            config: Scanning configuration (uses defaults if None)
        """
        super().__init__()
        self.config = config or ScanConfiguration()
        self.logger = logging.getLogger(__name__)
        
        # Initialize metrics
        self._register_metrics()
    
    def get_module_info(self) -> Dict[str, Any]:
        """Get module information for ReflectiveModule interface."""
        return {
            "module_name": "PatchScanner",
            "version": "1.0.0",
            "description": "Comprehensive patch discovery and scanning engine",
            "capabilities": [
                "directory_scanning",
                "file_pattern_matching", 
                "parallel_processing",
                "binary_file_detection",
                "error_handling",
                "metrics_collection"
            ]
        }
    
    def get_capabilities(self) -> List[str]:
        """Get list of scanner capabilities."""
        return [
            "directory_scanning",
            "file_pattern_matching", 
            "parallel_processing",
            "binary_file_detection",
            "error_handling",
            "metrics_collection"
        ]
    
    def graceful_degradation(self, error: Exception) -> Dict[str, Any]:
        """Handle graceful degradation when errors occur."""
        self.logger.error(f"PatchScanner error: {str(error)}")
        return {
            "status": "degraded",
            "error": str(error),
            "fallback_mode": "sequential_scanning_only",
            "available_operations": ["scan_file", "basic_directory_scan"]
        }
    
    def _register_metrics(self):
        """Register Prometheus metrics for scanning operations."""
        try:
            from prometheus_client import Counter, Histogram, Gauge
            
            self.files_scanned_total = Counter(
                'patch_scanner_files_scanned_total',
                'Total number of files scanned for patches'
            )
            
            self.patches_found_total = Counter(
                'patch_scanner_patches_found_total',
                'Total number of patches discovered',
                ['debt_level', 'bypass_type']
            )
            
            self.scan_duration_seconds = Histogram(
                'patch_scanner_scan_duration_seconds',
                'Time spent scanning for patches'
            )
            
            self.scan_errors_total = Counter(
                'patch_scanner_errors_total',
                'Total number of scanning errors',
                ['error_type']
            )
            
        except ImportError:
            self.logger.warning("Prometheus client not available, metrics disabled")
    
    def scan_directory(self, root_path: str) -> ScanResult:
        """
        Scan a directory tree for patch annotations.
        
        Args:
            root_path: Root directory to scan
            
        Returns:
            ScanResult containing all discovered patches and scan metadata
        """
        import time
        start_time = time.time()
        
        root_path = Path(root_path).resolve()
        if not root_path.exists():
            raise ValueError(f"Root path does not exist: {root_path}")
        
        if not root_path.is_dir():
            raise ValueError(f"Root path is not a directory: {root_path}")
        
        self.logger.info(f"Starting patch scan of directory: {root_path}")
        
        result = ScanResult(
            scan_configuration=self.config,
            root_path=str(root_path)
        )
        
        try:
            # Discover files to scan
            files_to_scan = list(self._discover_files(root_path))
            self.logger.info(f"Found {len(files_to_scan)} files to scan")
            
            # Scan files (parallel or sequential)
            if self.config.parallel_scanning and len(files_to_scan) > 1:
                self._scan_files_parallel(files_to_scan, result)
            else:
                self._scan_files_sequential(files_to_scan, result)
            
            # Update metrics
            result.scan_duration_seconds = time.time() - start_time
            result.total_patches_found = len(result.get_all_patches())
            
            self.logger.info(
                f"Scan completed: {result.files_scanned} files scanned, "
                f"{result.total_patches_found} patches found, "
                f"{len(result.scan_errors)} errors"
            )
            
            # Update Prometheus metrics
            if hasattr(self, 'scan_duration_seconds'):
                self.scan_duration_seconds.observe(result.scan_duration_seconds)
                
                for patch in result.get_all_patches():
                    self.patches_found_total.labels(
                        debt_level=patch.debt_level.value,
                        bypass_type=patch.bypass_type.value
                    ).inc()
            
            return result
            
        except Exception as e:
            self.logger.error(f"Scan failed: {str(e)}")
            result.scan_errors.append(f"Scan failed: {str(e)}")
            result.scan_duration_seconds = time.time() - start_time
            
            if hasattr(self, 'scan_errors_total'):
                self.scan_errors_total.labels(error_type="scan_failure").inc()
            
            return result
    
    def scan_file(self, file_path: str) -> ExtractionResult:
        """
        Scan a single file for patch annotations.
        
        Args:
            file_path: Path to the file to scan
            
        Returns:
            ExtractionResult containing patches found in the file
        """
        file_path = Path(file_path).resolve()
        
        if not file_path.exists():
            return ExtractionResult(
                file_path=str(file_path),
                errors=[f"File does not exist: {file_path}"]
            )
        
        if not file_path.is_file():
            return ExtractionResult(
                file_path=str(file_path),
                errors=[f"Path is not a file: {file_path}"]
            )
        
        # Check file size
        file_size_mb = file_path.stat().st_size / (1024 * 1024)
        if file_size_mb > self.config.max_file_size_mb:
            return ExtractionResult(
                file_path=str(file_path),
                errors=[f"File too large ({file_size_mb:.1f}MB > {self.config.max_file_size_mb}MB)"]
            )
        
        # Skip binary files if configured
        if self.config.skip_binary_files and self._is_binary_file(file_path):
            return ExtractionResult(
                file_path=str(file_path),
                errors=["Skipped binary file"]
            )
        
        try:
            # Read file content
            with open(file_path, 'r', encoding=self.config.encoding, errors=self.config.encoding_errors) as f:
                content = f.read()
            
            # Extract annotations
            result = AnnotationParser.extract_annotations(content, str(file_path))
            
            # Update metrics
            if hasattr(self, 'files_scanned_total'):
                self.files_scanned_total.inc()
            
            return result
            
        except Exception as e:
            error_msg = f"Failed to scan file {file_path}: {str(e)}"
            self.logger.error(error_msg)
            
            if hasattr(self, 'scan_errors_total'):
                self.scan_errors_total.labels(error_type="file_scan_error").inc()
            
            return ExtractionResult(
                file_path=str(file_path),
                errors=[error_msg]
            )
    
    def _discover_files(self, root_path: Path, current_depth: int = 0) -> Generator[Path, None, None]:
        """
        Recursively discover files to scan based on configuration patterns.
        
        Args:
            root_path: Directory to search
            current_depth: Current recursion depth
            
        Yields:
            Path objects for files that match scanning criteria
        """
        if self.config.max_depth is not None and current_depth > self.config.max_depth:
            return
        
        try:
            for item in root_path.iterdir():
                # Skip if symlink and not following symlinks
                if item.is_symlink() and not self.config.follow_symlinks:
                    continue
                
                if item.is_dir():
                    # Skip excluded directories
                    if item.name in self.config.exclude_directories:
                        continue
                    
                    # Recursively scan subdirectory
                    yield from self._discover_files(item, current_depth + 1)
                
                elif item.is_file():
                    # Check if file matches include patterns
                    if self._should_scan_file(item):
                        yield item
                        
        except PermissionError:
            self.logger.warning(f"Permission denied accessing directory: {root_path}")
        except Exception as e:
            self.logger.error(f"Error discovering files in {root_path}: {str(e)}")
    
    def _should_scan_file(self, file_path: Path) -> bool:
        """
        Determine if a file should be scanned based on include/exclude patterns.
        
        Args:
            file_path: Path to the file
            
        Returns:
            True if file should be scanned, False otherwise
        """
        filename = file_path.name
        
        # Check exclude patterns first
        for pattern in self.config.exclude_patterns:
            if fnmatch.fnmatch(filename, pattern) or fnmatch.fnmatch(str(file_path), pattern):
                return False
        
        # Check include patterns
        for pattern in self.config.include_patterns:
            if fnmatch.fnmatch(filename, pattern):
                return True
        
        return False
    
    def _is_binary_file(self, file_path: Path) -> bool:
        """
        Check if a file is binary by reading a small sample.
        
        Args:
            file_path: Path to the file
            
        Returns:
            True if file appears to be binary, False otherwise
        """
        try:
            with open(file_path, 'rb') as f:
                chunk = f.read(1024)  # Read first 1KB
                
            # Check for null bytes (common in binary files)
            if b'\x00' in chunk:
                return True
            
            # Try to decode as text
            try:
                chunk.decode(self.config.encoding)
                return False
            except UnicodeDecodeError:
                return True
                
        except Exception:
            # If we can't read the file, assume it's binary
            return True
    
    def _scan_files_sequential(self, files: List[Path], result: ScanResult):
        """
        Scan files sequentially.
        
        Args:
            files: List of files to scan
            result: ScanResult to update with results
        """
        for file_path in files:
            try:
                extraction_result = self.scan_file(str(file_path))
                result.file_results[str(file_path)] = extraction_result
                result.files_scanned += 1
                
                if extraction_result.errors:
                    result.scan_errors.extend(extraction_result.errors)
                    
            except Exception as e:
                error_msg = f"Failed to scan {file_path}: {str(e)}"
                result.scan_errors.append(error_msg)
                result.files_skipped += 1
    
    def _scan_files_parallel(self, files: List[Path], result: ScanResult):
        """
        Scan files in parallel using ThreadPoolExecutor.
        
        Args:
            files: List of files to scan
            result: ScanResult to update with results
        """
        with ThreadPoolExecutor(max_workers=self.config.max_workers) as executor:
            # Submit all scan tasks
            future_to_file = {
                executor.submit(self.scan_file, str(file_path)): file_path 
                for file_path in files
            }
            
            # Collect results as they complete
            for future in as_completed(future_to_file):
                file_path = future_to_file[future]
                
                try:
                    extraction_result = future.result()
                    result.file_results[str(file_path)] = extraction_result
                    result.files_scanned += 1
                    
                    if extraction_result.errors:
                        result.scan_errors.extend(extraction_result.errors)
                        
                except Exception as e:
                    error_msg = f"Failed to scan {file_path}: {str(e)}"
                    result.scan_errors.append(error_msg)
                    result.files_skipped += 1
    
    def get_health_status(self) -> Dict[str, Any]:
        """
        Get health status for the patch scanner.
        
        Returns:
            Dictionary containing health status information
        """
        return {
            "service": "patch_scanner",
            "status": "healthy",
            "configuration": {
                "include_patterns": len(self.config.include_patterns),
                "exclude_patterns": len(self.config.exclude_patterns),
                "max_file_size_mb": self.config.max_file_size_mb,
                "parallel_scanning": self.config.parallel_scanning,
                "max_workers": self.config.max_workers
            },
            "capabilities": [
                "directory_scanning",
                "file_pattern_matching", 
                "parallel_processing",
                "binary_file_detection",
                "error_handling",
                "metrics_collection"
            ]
        }


def create_default_scanner() -> PatchScanner:
    """
    Create a patch scanner with default configuration.
    
    Returns:
        PatchScanner instance with default settings
    """
    return PatchScanner()


def scan_directory_for_patches(directory_path: str, config: Optional[ScanConfiguration] = None) -> ScanResult:
    """
    Convenience function to scan a directory for patches.
    
    Args:
        directory_path: Path to directory to scan
        config: Optional scanning configuration
        
    Returns:
        ScanResult containing discovered patches
    """
    scanner = PatchScanner(config)
    return scanner.scan_directory(directory_path)


def scan_file_for_patches(file_path: str) -> ExtractionResult:
    """
    Convenience function to scan a single file for patches.
    
    Args:
        file_path: Path to file to scan
        
    Returns:
        ExtractionResult containing patches found in the file
    """
    scanner = PatchScanner()
    return scanner.scan_file(file_path)