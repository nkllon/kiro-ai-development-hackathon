#!/usr/bin/env python3
"""
Media Detector - Main media detection orchestration

Refactored from media_detector.py for RM-DDD compliance.
Single responsibility: Media detection orchestration and coordination.
"""

import logging
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple, Any

from .models import MediaFile, MediaType, FileChangeEvent, ChangeType
from .media_formats import MediaFormatRegistry
from .media_metadata import MediaMetadataExtractor
from .reflective_module import (
    ReflectiveModule, ModuleHealth, ModuleStatus, ModuleCapability, 
    ModuleConfiguration, register_module
)
from datetime import datetime


logger = logging.getLogger(__name__)

    # ReflectiveModule interface implementation
    def get_module_info(self) -> Dict[str, Any]:
        """Get comprehensive module information."""
        return {
            'module_id': self.module_id,
            'version': self.version,
            'name': 'Media Detector',
            'description': 'media_detector module for DevPost integration',
            'author': 'DevPost Integration Team',
            'created_at': self._start_time.isoformat(),
            'interface_version': self.get_interface_version()
        }
    
    def get_capabilities(self) -> List[ModuleCapability]:
        """Get module capabilities."""
        return []
    
    def get_dependencies(self) -> List[str]:
        """Get module dependencies."""
        return []
    
    def check_health(self) -> ModuleHealth:
        """Perform comprehensive health check."""
        issues = []
        health_score = 1.0
        
        try:
            # Basic health checks
            if not hasattr(self, 'module_id'):
                issues.append("Missing module_id")
                health_score -= 0.2
            
            # Add module-specific health checks here
            
            
            # Determine status
            if health_score >= 0.9:
                status = ModuleStatus.HEALTHY
            elif health_score >= 0.7:
                status = ModuleStatus.DEGRADED
            else:
                status = ModuleStatus.UNHEALTHY
            
            return ModuleHealth(
                module_id=self.module_id,
                status=status,
                last_check=datetime.now(),
                health_score=max(0.0, health_score),
                issues=issues,
                capabilities=self.get_capabilities(),
                dependencies=self.get_dependencies(),
                metrics=self.get_metrics()
            )
            
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return ModuleHealth(
                module_id=self.module_id,
                status=ModuleStatus.UNHEALTHY,
                last_check=datetime.now(),
                health_score=0.0,
                issues=[f"Health check exception: {e}"],
                capabilities=self.get_capabilities(),
                dependencies=self.get_dependencies(),
                metrics={}
            )
    
    def get_configuration(self) -> ModuleConfiguration:
        """Get module configuration."""
        return ModuleConfiguration(
            module_id=self.module_id,
            config_version="1.0.0",
            parameters={},
            required_parameters=[],
            optional_parameters=[],
            validation_rules={},
            last_updated=datetime.now()
        )
    
    def update_configuration(self, config: ModuleConfiguration) -> bool:
        """Update module configuration."""
        try:
            if not config.is_valid():
                logger.error("Invalid configuration provided")
                return False
            
            logger.info(f"Configuration updated for {self.module_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error updating configuration: {e}")
            return False
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get module metrics."""
        uptime = (datetime.now() - self._start_time).total_seconds()
        
        return {
            'uptime_seconds': uptime,
            'uptime_hours': uptime / 3600,
            'last_check': datetime.now().isoformat()
        }
    
    def reset_metrics(self) -> None:
        """Reset module metrics to initial state."""
        self._start_time = datetime.now()
        logger.info("Metrics reset for {self.module_id} module")


class MediaFileDetector(ReflectiveModule):
    """
    Intelligent media file detection and analysis.
    
    Detects media files, extracts metadata, validates formats,
    and provides media-specific change analysis.
    """
    
    def __init__(self):
        super().__init__(module_id="media_detector", version="1.0.0")
        self._start_time = datetime.now()
        register_module(self)

        """Initialize media file detector."""
        self.format_registry = MediaFormatRegistry()
        self.metadata_extractor = MediaMetadataExtractor()
        
        # Detection statistics
        self.stats = {
            'files_processed': 0,
            'media_files_found': 0,
            'images_detected': 0,
            'videos_detected': 0,
            'audio_detected': 0,
            'documents_detected': 0,
            'archives_detected': 0,
            'unsupported_files': 0,
            'errors_encountered': 0
        }
    
    def detect_media_file(self, file_path: Path) -> Optional[MediaFile]:
        """Detect and analyze a media file"""
        try:
            self.stats['files_processed'] += 1
            
            # Check if file exists
            if not file_path.exists():
                logger.warning(f"File does not exist: {file_path}")
                return None
            
            # Get media type
            media_type = self.format_registry.get_media_type(file_path)
            if not media_type:
                self.stats['unsupported_files'] += 1
                return None
            
            # Update statistics
            self._update_media_stats(media_type)
            
            # Extract metadata
            metadata = self.metadata_extractor.extract_metadata(file_path, media_type)
            
            # Validate file size
            is_valid_size, size_message = self.format_registry.validate_file_size(file_path)
            if not is_valid_size:
                logger.warning(f"File size validation failed for {file_path}: {size_message}")
            
            # Create MediaFile object
            media_file = MediaFile(
                file_path=str(file_path),
                file_name=file_path.name,
                media_type=media_type,
                file_size=file_path.stat().st_size,
                mime_type=self.format_registry.get_mime_type(file_path),
                metadata=metadata,
                is_valid=is_valid_size,
                validation_message=size_message,
                detected_at=metadata.get('created_at', ''),
                file_hash=metadata.get('file_hash', '')
            )
            
            self.stats['media_files_found'] += 1
            logger.debug(f"Detected media file: {file_path} ({media_type})")
            
            return media_file
            
        except Exception as e:
            self.stats['errors_encountered'] += 1
            logger.error(f"Error detecting media file {file_path}: {e}")
            return None
    
    def detect_media_files(self, directory_path: Path, 
                          recursive: bool = True) -> List[MediaFile]:
        """Detect all media files in a directory"""
        media_files = []
        
        try:
            if not directory_path.exists():
                logger.error(f"Directory does not exist: {directory_path}")
                return media_files
            
            if not directory_path.is_dir():
                logger.error(f"Path is not a directory: {directory_path}")
                return media_files
            
            # Get file paths
            if recursive:
                file_paths = [f for f in directory_path.rglob('*') if f.is_file()]
            else:
                file_paths = [f for f in directory_path.iterdir() if f.is_file()]
            
            # Process each file
            for file_path in file_paths:
                media_file = self.detect_media_file(file_path)
                if media_file:
                    media_files.append(media_file)
            
            logger.info(f"Detected {len(media_files)} media files in {directory_path}")
            return media_files
            
        except Exception as e:
            logger.error(f"Error detecting media files in {directory_path}: {e}")
            return media_files
    
    def analyze_media_changes(self, old_media_files: List[MediaFile], 
                             new_media_files: List[MediaFile]) -> List[FileChangeEvent]:
        """Analyze changes between old and new media file sets"""
        try:
            changes = []
            
            # Create lookup dictionaries
            old_files = {mf.file_path: mf for mf in old_media_files}
            new_files = {mf.file_path: mf for mf in new_media_files}
            
            # Find added files
            for file_path, media_file in new_files.items():
                if file_path not in old_files:
                    changes.append(FileChangeEvent(
                        file_path=file_path,
                        change_type=ChangeType.ADDED,
                        content_type=media_file.media_type,
                        timestamp=media_file.detected_at,
                        metadata={'media_file': media_file.to_dict()}
                    ))
            
            # Find removed files
            for file_path, media_file in old_files.items():
                if file_path not in new_files:
                    changes.append(FileChangeEvent(
                        file_path=file_path,
                        change_type=ChangeType.REMOVED,
                        content_type=media_file.media_type,
                        timestamp=media_file.detected_at,
                        metadata={'media_file': media_file.to_dict()}
                    ))
            
            # Find modified files
            for file_path, new_media_file in new_files.items():
                if file_path in old_files:
                    old_media_file = old_files[file_path]
                    
                    # Check if file has changed (using hash)
                    if (old_media_file.file_hash and new_media_file.file_hash and
                        old_media_file.file_hash != new_media_file.file_hash):
                        changes.append(FileChangeEvent(
                            file_path=file_path,
                            change_type=ChangeType.MODIFIED,
                            content_type=new_media_file.media_type,
                            timestamp=new_media_file.detected_at,
                            metadata={
                                'old_media_file': old_media_file.to_dict(),
                                'new_media_file': new_media_file.to_dict()
                            }
                        ))
            
            logger.info(f"Analyzed media changes: {len(changes)} changes detected")
            return changes
            
        except Exception as e:
            logger.error(f"Error analyzing media changes: {e}")
            return []
    
    def get_supported_formats(self) -> Dict[MediaType, Set[str]]:
        """Get all supported media formats"""
        return self.format_registry.get_all_supported_formats()
    
    def is_media_file(self, file_path: Path) -> bool:
        """Check if file is a supported media file"""
        return self.format_registry.is_supported_format(file_path)
    
    def get_media_type(self, file_path: Path) -> Optional[MediaType]:
        """Get media type for file"""
        return self.format_registry.get_media_type(file_path)
    
    def validate_media_file(self, file_path: Path) -> Tuple[bool, str]:
        """Validate media file format and size"""
        if not self.is_media_file(file_path):
            return False, "Unsupported media format"
        
        return self.format_registry.validate_file_size(file_path)
    
    def get_detection_stats(self) -> Dict[str, Any]:
        """Get detection statistics"""
        return {
            'detection_stats': self.stats.copy(),
            'extraction_capabilities': self.metadata_extractor.get_extraction_capabilities(),
            'supported_formats': {
                media_type.value: list(formats) 
                for media_type, formats in self.get_supported_formats().items()
            }
        }
    
    def reset_stats(self) -> None:
        """Reset detection statistics"""
        self.stats = {
            'files_processed': 0,
            'media_files_found': 0,
            'images_detected': 0,
            'videos_detected': 0,
            'audio_detected': 0,
            'documents_detected': 0,
            'archives_detected': 0,
            'unsupported_files': 0,
            'errors_encountered': 0
        }
    
    def _update_media_stats(self, media_type: MediaType) -> None:
        """Update media type statistics"""
        if media_type == MediaType.IMAGE:
            self.stats['images_detected'] += 1
        elif media_type == MediaType.VIDEO:
            self.stats['videos_detected'] += 1
        elif media_type == MediaType.AUDIO:
            self.stats['audio_detected'] += 1
        elif media_type == MediaType.DOCUMENT:
            self.stats['documents_detected'] += 1
        elif media_type == MediaType.ARCHIVE:
            self.stats['archives_detected'] += 1
    
    def is_healthy(self) -> bool:
        """Check if media detector is healthy"""
        try:
            # Check if format registry is working
            formats = self.get_supported_formats()
            if not formats:
                return False
            
            # Check if metadata extractor is working
            capabilities = self.metadata_extractor.get_extraction_capabilities()
            if not isinstance(capabilities, dict):
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return False
    
    def get_health_indicators(self) -> Dict[str, Any]:
        """Get detailed health indicators"""
        try:
            return {
                'detector_healthy': self.is_healthy(),
                'detection_stats': self.stats,
                'extraction_capabilities': self.metadata_extractor.get_extraction_capabilities(),
                'supported_formats_count': sum(len(formats) for formats in self.get_supported_formats().values()),
                'format_registry_working': bool(self.get_supported_formats()),
                'metadata_extractor_working': bool(self.metadata_extractor.get_extraction_capabilities())
            }
            
        except Exception as e:
            logger.error(f"Error getting health indicators: {e}")
            return {
                'detector_healthy': False,
                'error': str(e)
            }
