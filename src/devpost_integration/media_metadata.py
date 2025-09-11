#!/usr/bin/env python3
"""
Media Metadata - Metadata extraction and analysis

Extracted from media_detector.py for RM-DDD compliance.
Single responsibility: Media metadata extraction and analysis.
"""

import hashlib
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
import logging

from .models import MediaFile, MediaType
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
            'name': 'Media Metadata',
            'description': 'media_metadata module for DevPost integration',
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


class MediaMetadataExtractor(ReflectiveModule):
    """Extracts metadata from media files"""
    
    def __init__(self):
        super().__init__(module_id="media_metadata", version="1.0.0")
        self._start_time = datetime.now()
        register_module(self)

        """Initialize metadata extractor"""
        self.ffprobe_available = self._check_ffprobe_available()
        self.exiftool_available = self._check_exiftool_available()
    
    def extract_metadata(self, file_path: Path, media_type: MediaType) -> Dict[str, Any]:
        """Extract metadata from media file"""
        try:
            metadata = {
                'file_path': str(file_path),
                'file_name': file_path.name,
                'file_size': file_path.stat().st_size,
                'file_extension': file_path.suffix.lower(),
                'media_type': media_type,
                'created_at': datetime.now().isoformat(),
                'extraction_method': 'unknown'
            }
            
            # Basic file metadata
            metadata.update(self._extract_basic_metadata(file_path))
            
            # Media-specific metadata
            if media_type == MediaType.IMAGE:
                metadata.update(self._extract_image_metadata(file_path))
            elif media_type == MediaType.VIDEO:
                metadata.update(self._extract_video_metadata(file_path))
            elif media_type == MediaType.AUDIO:
                metadata.update(self._extract_audio_metadata(file_path))
            elif media_type == MediaType.DOCUMENT:
                metadata.update(self._extract_document_metadata(file_path))
            
            # Hash for change detection
            metadata['file_hash'] = self._calculate_file_hash(file_path)
            
            return metadata
            
        except Exception as e:
            logger.error(f"Error extracting metadata from {file_path}: {e}")
            return {
                'file_path': str(file_path),
                'file_name': file_path.name,
                'error': str(e),
                'created_at': datetime.now().isoformat()
            }
    
    def _extract_basic_metadata(self, file_path: Path) -> Dict[str, Any]:
        """Extract basic file metadata"""
        try:
            stat = file_path.stat()
            return {
                'file_size': stat.st_size,
                'file_size_mb': round(stat.st_size / (1024 * 1024), 2),
                'created_time': datetime.fromtimestamp(stat.st_ctime).isoformat(),
                'modified_time': datetime.fromtimestamp(stat.st_mtime).isoformat(),
                'accessed_time': datetime.fromtimestamp(stat.st_atime).isoformat(),
                'permissions': oct(stat.st_mode)[-3:],
                'is_file': file_path.is_file(),
                'is_directory': file_path.is_dir()
            }
        except Exception as e:
            logger.error(f"Error extracting basic metadata: {e}")
            return {}
    
    def _extract_image_metadata(self, file_path: Path) -> Dict[str, Any]:
        """Extract image-specific metadata"""
        metadata = {}
        
        try:
            if self.exiftool_available:
                metadata.update(self._extract_with_exiftool(file_path))
            elif self.ffprobe_available:
                metadata.update(self._extract_with_ffprobe(file_path))
            else:
                metadata.update(self._extract_basic_image_info(file_path))
        except Exception as e:
            logger.error(f"Error extracting image metadata: {e}")
            metadata['error'] = str(e)
        
        return metadata
    
    def _extract_video_metadata(self, file_path: Path) -> Dict[str, Any]:
        """Extract video-specific metadata"""
        metadata = {}
        
        try:
            if self.ffprobe_available:
                metadata.update(self._extract_with_ffprobe(file_path))
            else:
                metadata.update(self._extract_basic_video_info(file_path))
        except Exception as e:
            logger.error(f"Error extracting video metadata: {e}")
            metadata['error'] = str(e)
        
        return metadata
    
    def _extract_audio_metadata(self, file_path: Path) -> Dict[str, Any]:
        """Extract audio-specific metadata"""
        metadata = {}
        
        try:
            if self.ffprobe_available:
                metadata.update(self._extract_with_ffprobe(file_path))
            else:
                metadata.update(self._extract_basic_audio_info(file_path))
        except Exception as e:
            logger.error(f"Error extracting audio metadata: {e}")
            metadata['error'] = str(e)
        
        return metadata
    
    def _extract_document_metadata(self, file_path: Path) -> Dict[str, Any]:
        """Extract document-specific metadata"""
        metadata = {}
        
        try:
            if self.exiftool_available:
                metadata.update(self._extract_with_exiftool(file_path))
            else:
                metadata.update(self._extract_basic_document_info(file_path))
        except Exception as e:
            logger.error(f"Error extracting document metadata: {e}")
            metadata['error'] = str(e)
        
        return metadata
    
    def _extract_with_ffprobe(self, file_path: Path) -> Dict[str, Any]:
        """Extract metadata using ffprobe"""
        try:
            cmd = [
                'ffprobe', '-v', 'quiet', '-print_format', 'json',
                '-show_format', '-show_streams', str(file_path)
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                import json
                data = json.loads(result.stdout)
                
                metadata = {
                    'extraction_method': 'ffprobe',
                    'format_name': data.get('format', {}).get('format_name'),
                    'duration': data.get('format', {}).get('duration'),
                    'bit_rate': data.get('format', {}).get('bit_rate'),
                    'streams': len(data.get('streams', []))
                }
                
                # Extract stream information
                streams = data.get('streams', [])
                for i, stream in enumerate(streams):
                    stream_type = stream.get('codec_type', 'unknown')
                    if stream_type == 'video':
                        metadata.update({
                            'video_codec': stream.get('codec_name'),
                            'video_width': stream.get('width'),
                            'video_height': stream.get('height'),
                            'video_fps': stream.get('r_frame_rate'),
                            'video_bitrate': stream.get('bit_rate')
                        })
                    elif stream_type == 'audio':
                        metadata.update({
                            'audio_codec': stream.get('codec_name'),
                            'audio_sample_rate': stream.get('sample_rate'),
                            'audio_channels': stream.get('channels'),
                            'audio_bitrate': stream.get('bit_rate')
                        })
                
                return metadata
            else:
                return {'extraction_method': 'ffprobe', 'error': 'ffprobe failed'}
                
        except Exception as e:
            return {'extraction_method': 'ffprobe', 'error': str(e)}
    
    def _extract_with_exiftool(self, file_path: Path) -> Dict[str, Any]:
        """Extract metadata using exiftool"""
        try:
            cmd = ['exiftool', '-json', str(file_path)]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                import json
                data = json.loads(result.stdout)
                
                if data and len(data) > 0:
                    exif_data = data[0]
                    return {
                        'extraction_method': 'exiftool',
                        'camera_make': exif_data.get('Make'),
                        'camera_model': exif_data.get('Model'),
                        'image_width': exif_data.get('ImageWidth'),
                        'image_height': exif_data.get('ImageHeight'),
                        'orientation': exif_data.get('Orientation'),
                        'color_space': exif_data.get('ColorSpace'),
                        'iso': exif_data.get('ISO'),
                        'focal_length': exif_data.get('FocalLength'),
                        'aperture': exif_data.get('FNumber'),
                        'shutter_speed': exif_data.get('ShutterSpeed'),
                        'exposure_time': exif_data.get('ExposureTime'),
                        'flash': exif_data.get('Flash'),
                        'white_balance': exif_data.get('WhiteBalance'),
                        'date_taken': exif_data.get('DateTimeOriginal'),
                        'gps_latitude': exif_data.get('GPSLatitude'),
                        'gps_longitude': exif_data.get('GPSLongitude')
                    }
                else:
                    return {'extraction_method': 'exiftool', 'error': 'No data returned'}
            else:
                return {'extraction_method': 'exiftool', 'error': 'exiftool failed'}
                
        except Exception as e:
            return {'extraction_method': 'exiftool', 'error': str(e)}
    
    def _extract_basic_image_info(self, file_path: Path) -> Dict[str, Any]:
        """Extract basic image information without external tools"""
        return {
            'extraction_method': 'basic',
            'file_type': 'image',
            'note': 'Basic extraction - install exiftool or ffprobe for detailed metadata'
        }
    
    def _extract_basic_video_info(self, file_path: Path) -> Dict[str, Any]:
        """Extract basic video information without external tools"""
        return {
            'extraction_method': 'basic',
            'file_type': 'video',
            'note': 'Basic extraction - install ffprobe for detailed metadata'
        }
    
    def _extract_basic_audio_info(self, file_path: Path) -> Dict[str, Any]:
        """Extract basic audio information without external tools"""
        return {
            'extraction_method': 'basic',
            'file_type': 'audio',
            'note': 'Basic extraction - install ffprobe for detailed metadata'
        }
    
    def _extract_basic_document_info(self, file_path: Path) -> Dict[str, Any]:
        """Extract basic document information without external tools"""
        return {
            'extraction_method': 'basic',
            'file_type': 'document',
            'note': 'Basic extraction - install exiftool for detailed metadata'
        }
    
    def _calculate_file_hash(self, file_path: Path) -> str:
        """Calculate SHA-256 hash of file for change detection"""
        try:
            hash_sha256 = hashlib.sha256()
            with open(file_path, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_sha256.update(chunk)
            return hash_sha256.hexdigest()
        except Exception as e:
            logger.error(f"Error calculating hash for {file_path}: {e}")
            return ""
    
    def _check_ffprobe_available(self) -> bool:
        """Check if ffprobe is available"""
        try:
            result = subprocess.run(['ffprobe', '-version'], 
                                  capture_output=True, text=True, timeout=5)
            return result.returncode == 0
        except Exception:
            return False
    
    def _check_exiftool_available(self) -> bool:
        """Check if exiftool is available"""
        try:
            result = subprocess.run(['exiftool', '-ver'], 
                                  capture_output=True, text=True, timeout=5)
            return result.returncode == 0
        except Exception:
            return False
    
    def get_extraction_capabilities(self) -> Dict[str, bool]:
        """Get available extraction capabilities"""
        return {
            'ffprobe_available': self.ffprobe_available,
            'exiftool_available': self.exiftool_available,
            'can_extract_video': self.ffprobe_available,
            'can_extract_audio': self.ffprobe_available,
            'can_extract_image': self.exiftool_available or self.ffprobe_available,
            'can_extract_document': self.exiftool_available
        }
