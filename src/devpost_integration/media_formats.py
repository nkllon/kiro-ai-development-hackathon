#!/usr/bin/env python3
"""
Media Formats - Media format definitions and validation

Extracted from media_detector.py for RM-DDD compliance.
Single responsibility: Media format definitions and validation.
"""

import mimetypes
from pathlib import Path
from typing import Dict, Set, Optional, Tuple
import logging

from .models import MediaType
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
            'name': 'Media Formats',
            'description': 'media_formats module for DevPost integration',
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


class MediaFormatRegistry(ReflectiveModule):
    """Registry for supported media formats and their properties"""
    
    def __init__(self):
        super().__init__(module_id="media_formats", version="1.0.0")
        self._start_time = datetime.now()
        register_module(self)

        """Initialize media format registry"""
        self.supported_image_formats = {
            '.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.tif',
            '.svg', '.webp', '.ico', '.raw', '.cr2', '.nef', '.arw'
        }
        
        self.supported_video_formats = {
            '.mp4', '.avi', '.mov', '.wmv', '.flv', '.webm', '.mkv',
            '.m4v', '.3gp', '.ogv', '.mts', '.m2ts'
        }
        
        self.supported_audio_formats = {
            '.mp3', '.wav', '.flac', '.aac', '.ogg', '.wma', '.m4a',
            '.opus', '.aiff', '.au'
        }
        
        self.supported_document_formats = {
            '.pdf', '.doc', '.docx', '.ppt', '.pptx', '.xls', '.xlsx',
            '.odt', '.odp', '.ods', '.rtf', '.txt'
        }
        
        self.supported_archive_formats = {
            '.zip', '.rar', '.7z', '.tar', '.gz', '.bz2', '.xz'
        }
        
        # Format properties
        self.format_properties = {
            # Image formats
            '.jpg': {'media_type': MediaType.IMAGE, 'mime_type': 'image/jpeg', 'max_size_mb': 50},
            '.jpeg': {'media_type': MediaType.IMAGE, 'mime_type': 'image/jpeg', 'max_size_mb': 50},
            '.png': {'media_type': MediaType.IMAGE, 'mime_type': 'image/png', 'max_size_mb': 50},
            '.gif': {'media_type': MediaType.IMAGE, 'mime_type': 'image/gif', 'max_size_mb': 20},
            '.bmp': {'media_type': MediaType.IMAGE, 'mime_type': 'image/bmp', 'max_size_mb': 100},
            '.tiff': {'media_type': MediaType.IMAGE, 'mime_type': 'image/tiff', 'max_size_mb': 200},
            '.tif': {'media_type': MediaType.IMAGE, 'mime_type': 'image/tiff', 'max_size_mb': 200},
            '.svg': {'media_type': MediaType.IMAGE, 'mime_type': 'image/svg+xml', 'max_size_mb': 10},
            '.webp': {'media_type': MediaType.IMAGE, 'mime_type': 'image/webp', 'max_size_mb': 30},
            '.ico': {'media_type': MediaType.IMAGE, 'mime_type': 'image/x-icon', 'max_size_mb': 1},
            
            # Video formats
            '.mp4': {'media_type': MediaType.VIDEO, 'mime_type': 'video/mp4', 'max_size_mb': 500},
            '.avi': {'media_type': MediaType.VIDEO, 'mime_type': 'video/x-msvideo', 'max_size_mb': 1000},
            '.mov': {'media_type': MediaType.VIDEO, 'mime_type': 'video/quicktime', 'max_size_mb': 1000},
            '.wmv': {'media_type': MediaType.VIDEO, 'mime_type': 'video/x-ms-wmv', 'max_size_mb': 500},
            '.flv': {'media_type': MediaType.VIDEO, 'mime_type': 'video/x-flv', 'max_size_mb': 500},
            '.webm': {'media_type': MediaType.VIDEO, 'mime_type': 'video/webm', 'max_size_mb': 500},
            '.mkv': {'media_type': MediaType.VIDEO, 'mime_type': 'video/x-matroska', 'max_size_mb': 1000},
            
            # Audio formats
            '.mp3': {'media_type': MediaType.AUDIO, 'mime_type': 'audio/mpeg', 'max_size_mb': 50},
            '.wav': {'media_type': MediaType.AUDIO, 'mime_type': 'audio/wav', 'max_size_mb': 100},
            '.flac': {'media_type': MediaType.AUDIO, 'mime_type': 'audio/flac', 'max_size_mb': 200},
            '.aac': {'media_type': MediaType.AUDIO, 'mime_type': 'audio/aac', 'max_size_mb': 50},
            '.ogg': {'media_type': MediaType.AUDIO, 'mime_type': 'audio/ogg', 'max_size_mb': 50},
            '.wma': {'media_type': MediaType.AUDIO, 'mime_type': 'audio/x-ms-wma', 'max_size_mb': 50},
            '.m4a': {'media_type': MediaType.AUDIO, 'mime_type': 'audio/mp4', 'max_size_mb': 50},
            
            # Document formats
            '.pdf': {'media_type': MediaType.DOCUMENT, 'mime_type': 'application/pdf', 'max_size_mb': 100},
            '.doc': {'media_type': MediaType.DOCUMENT, 'mime_type': 'application/msword', 'max_size_mb': 50},
            '.docx': {'media_type': MediaType.DOCUMENT, 'mime_type': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document', 'max_size_mb': 50},
            '.ppt': {'media_type': MediaType.DOCUMENT, 'mime_type': 'application/vnd.ms-powerpoint', 'max_size_mb': 50},
            '.pptx': {'media_type': MediaType.DOCUMENT, 'mime_type': 'application/vnd.openxmlformats-officedocument.presentationml.presentation', 'max_size_mb': 50},
            '.xls': {'media_type': MediaType.DOCUMENT, 'mime_type': 'application/vnd.ms-excel', 'max_size_mb': 50},
            '.xlsx': {'media_type': MediaType.DOCUMENT, 'mime_type': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', 'max_size_mb': 50},
            '.txt': {'media_type': MediaType.DOCUMENT, 'mime_type': 'text/plain', 'max_size_mb': 10},
        }
    
    def get_media_type(self, file_path: Path) -> Optional[MediaType]:
        """Get media type for file based on extension"""
        extension = file_path.suffix.lower()
        
        if extension in self.supported_image_formats:
            return MediaType.IMAGE
        elif extension in self.supported_video_formats:
            return MediaType.VIDEO
        elif extension in self.supported_audio_formats:
            return MediaType.AUDIO
        elif extension in self.supported_document_formats:
            return MediaType.DOCUMENT
        elif extension in self.supported_archive_formats:
            return MediaType.ARCHIVE
        else:
            return None
    
    def is_supported_format(self, file_path: Path) -> bool:
        """Check if file format is supported"""
        return self.get_media_type(file_path) is not None
    
    def get_mime_type(self, file_path: Path) -> Optional[str]:
        """Get MIME type for file"""
        extension = file_path.suffix.lower()
        
        if extension in self.format_properties:
            return self.format_properties[extension]['mime_type']
        
        # Fallback to system MIME type detection
        mime_type, _ = mimetypes.guess_type(str(file_path))
        return mime_type
    
    def get_max_size_mb(self, file_path: Path) -> Optional[int]:
        """Get maximum recommended size in MB for file format"""
        extension = file_path.suffix.lower()
        
        if extension in self.format_properties:
            return self.format_properties[extension]['max_size_mb']
        
        return None
    
    def get_format_properties(self, file_path: Path) -> Dict[str, any]:
        """Get all properties for file format"""
        extension = file_path.suffix.lower()
        
        if extension in self.format_properties:
            return self.format_properties[extension].copy()
        
        return {}
    
    def get_all_supported_formats(self) -> Dict[MediaType, Set[str]]:
        """Get all supported formats by media type"""
        return {
            MediaType.IMAGE: self.supported_image_formats,
            MediaType.VIDEO: self.supported_video_formats,
            MediaType.AUDIO: self.supported_audio_formats,
            MediaType.DOCUMENT: self.supported_document_formats,
            MediaType.ARCHIVE: self.supported_archive_formats
        }
    
    def add_custom_format(self, extension: str, media_type: MediaType, 
                         mime_type: str, max_size_mb: int = 50) -> None:
        """Add custom format to registry"""
        extension = extension.lower()
        if not extension.startswith('.'):
            extension = f'.{extension}'
        
        self.format_properties[extension] = {
            'media_type': media_type,
            'mime_type': mime_type,
            'max_size_mb': max_size_mb
        }
        
        # Add to appropriate format set
        if media_type == MediaType.IMAGE:
            self.supported_image_formats.add(extension)
        elif media_type == MediaType.VIDEO:
            self.supported_video_formats.add(extension)
        elif media_type == MediaType.AUDIO:
            self.supported_audio_formats.add(extension)
        elif media_type == MediaType.DOCUMENT:
            self.supported_document_formats.add(extension)
        elif media_type == MediaType.ARCHIVE:
            self.supported_archive_formats.add(extension)
    
    def validate_file_size(self, file_path: Path) -> Tuple[bool, str]:
        """Validate file size against format limits"""
        try:
            file_size_mb = file_path.stat().st_size / (1024 * 1024)
            max_size_mb = self.get_max_size_mb(file_path)
            
            if max_size_mb is None:
                return True, "No size limit defined"
            
            if file_size_mb > max_size_mb:
                return False, f"File size {file_size_mb:.1f}MB exceeds limit of {max_size_mb}MB"
            
            return True, f"File size {file_size_mb:.1f}MB is within limit"
            
        except Exception as e:
            return False, f"Error validating file size: {str(e)}"
    
    def get_format_info(self, file_path: Path) -> Dict[str, any]:
        """Get comprehensive format information for file"""
        return {
            'extension': file_path.suffix.lower(),
            'media_type': self.get_media_type(file_path),
            'mime_type': self.get_mime_type(file_path),
            'is_supported': self.is_supported_format(file_path),
            'max_size_mb': self.get_max_size_mb(file_path),
            'properties': self.get_format_properties(file_path)
        }
