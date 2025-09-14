"""
DevpostMediaDetector Module

Extracted from media_detector.py for RDI compliance.
This module contains the DevpostMediaDetector class implementation.
"""

import logging
from datetime import datetime
from .reflective_module import ReflectiveModule, register_module, ModuleHealth, ModuleStatus, ModuleCapability
from typing import Dict, List, Any, Optional

class DevpostMediaDetector(ReflectiveModule):
def register_with_registry(self, registry):
        """Register this module with the RM registry."""
        if registry:
            registry.register_module(self)
            self.add_capability("registry_registered")
    
    def get_module_metadata(self) -> Dict[str, any]:
        """Get module metadata for registry."""
        return {
            "module_id": self.module_id,
            "module_type": self.module_type,
            "capabilities": self.capabilities,
            "dependencies": self.dependencies,
            "health_status": self.health_status,
            "last_updated": self.last_updated
        }
def get_health_indicators(self) -> Dict[str, any]:
        """Get health indicators for this module."""
        return {
            "module_id": self.module_id,
            "status": self.health_status,
            "last_updated": self.last_updated,
            "capabilities_count": len(self.capabilities),
            "dependencies_count": len(self.dependencies)
        }
    
    def get_status_report(self) -> Dict[str, any]:
        """Get comprehensive status report for this module."""
        return {
            "module_id": self.module_id,
            "health_status": self.health_status,
            "capabilities": self.capabilities,
            "dependencies": self.dependencies,
            "last_updated": self.last_updated,
            "performance_metrics": self.get_metrics()
        }
    """Main media detector with RM-DDD compliance"""
    
    def __init__(self):
        """Initialize media detector"""
        super().__init__(module_id="media_detector", version="1.0.0")
        self.format_registry = MediaFormatRegistry()
        self.metadata_extractor = MediaMetadataExtractor()
        self._start_time = datetime.now()
        self._files_processed = 0
        self._files_detected = 0
        self._errors = 0
        register_module(self)
    
    def detect_media_files(self, directory: Path, recursive: bool = True) -> List[MediaFile]:
        """Detect media files in directory"""
        try:
            media_files = []
            
            if not directory.exists():
                logger.warning(f"Directory does not exist: {directory}")
                return media_files
            
            # Get file pattern
            pattern = "**/*" if recursive else "*"
            
            for file_path in directory.glob(pattern):
                if file_path.is_file():
                    self._files_processed += 1
                    
                    # Check if file is media
                    if self.is_media_file(file_path):
                        media_file = self.create_media_file(file_path)
                        if media_file:
                            media_files.append(media_file)
                            self._files_detected += 1
            
            logger.info(f"Detected {len(media_files)} media files in {directory}")
            return media_files
            
        except Exception as e:
            self._errors += 1
            logger.error(f"Error detecting media files: {e}")
            return []
    
    def is_media_file(self, file_path: Path) -> bool:
        """Check if file is a media file"""
        try:
            return self.format_registry.is_media_file(file_path)
        except Exception as e:
            self._errors += 1
            logger.error(f"Error checking media file {file_path}: {e}")
            return False
    
    def create_media_file(self, file_path: Path) -> Optional[MediaFile]:
        """Create MediaFile object from path"""
        try:
            if not self.is_media_file(file_path):
                return None
            
            # Get file info
            stat = file_path.stat()
            
            # Determine media type
            media_type = self.format_registry.get_media_type(file_path)
            
            # Extract metadata
            metadata = self.metadata_extractor.extract_metadata(file_path)
            
            return MediaFile(
                path=file_path,
                name=file_path.name,
                size=stat.st_size,
                media_type=media_type,
                metadata=metadata,
                created_at=datetime.fromtimestamp(stat.st_ctime),
                modified_at=datetime.fromtimestamp(stat.st_mtime)
            )
            
        except Exception as e:
            self._errors += 1
            logger.error(f"Error creating media file {file_path}: {e}")
            return None
    
    def get_supported_formats(self) -> Dict[MediaType, List[str]]:
        """Get supported media formats by type"""
        return self.format_registry.get_supported_formats()
    
    def get_media_statistics(self) -> Dict[str, Any]:
        """Get media detection statistics"""
        return {
            'files_processed': self._files_processed,
            'files_detected': self._files_detected,
            'detection_rate': (self._files_detected / self._files_processed) if self._files_processed > 0 else 0.0,
            'errors': self._errors,
            'error_rate': (self._errors / self._files_processed) if self._files_processed > 0 else 0.0,
            'supported_formats': len(self.format_registry.get_all_extensions())
        }
    
    # ReflectiveModule interface implementation
    def get_module_info(self) -> Dict[str, Any]:
        """Get comprehensive module information."""
        return {
            'module_id': self.module_id,
            'version': self.version,
            'name': 'DevPost Media Detector',
            'description': 'Media file detection and analysis for DevPost integration',
            'author': 'DevPost Integration Team',
            'created_at': self._start_time.isoformat(),
            'interface_version': self.get_interface_version()
        }
    
    def get_capabilities(self) -> List[ModuleCapability]:
        """Get module capabilities."""
        return [
            ModuleCapability.CORE_FUNCTIONALITY,
            ModuleCapability.HEALTH_MONITORING,
            ModuleCapability.CONFIGURATION,
            ModuleCapability.LOGGING,
            ModuleCapability.METRICS,
            ModuleCapability.PERSISTENCE
        ]
    
    def get_dependencies(self) -> List[str]:
        """Get module dependencies."""
        return [
            'media_formats',
            'media_metadata'
        ]
    
    def check_health(self) -> ModuleHealth:
        """Check module health with comprehensive monitoring"""
        try:
            if not hasattr(self, '_start_time'):
                return ModuleHealth.UNHEALTHY
            uptime = (datetime.now() - self._start_time).total_seconds()
            if uptime < 0:
                return ModuleHealth.UNHEALTHY
            error_count = getattr(self, '_error_count', 0)
            total_operations = getattr(self, '_command_count', 1)
            error_rate = error_count / total_operations if total_operations > 0 else 0
            if error_rate > 0.5:
                return ModuleHealth.UNHEALTHY
            elif error_rate > 0.1:
                return ModuleHealth.DEGRADED
            else:
                return ModuleHealth.HEALTHY
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return ModuleHealth.UNHEALTHY
        """Perform comprehensive health check."""
        issues = []
        health_score = 1.0
        
        try:
            # Check format registry
            if not hasattr(self, 'format_registry'):
                issues.append("Missing format registry")
                health_score -= 0.3
            
            # Check metadata extractor
            if not hasattr(self, 'metadata_extractor'):
                issues.append("Missing metadata extractor")
                health_score -= 0.3
            
            # Check error rate
            if self._files_processed > 0:
                error_rate = self._errors / self._files_processed
                if error_rate > 0.1:  # More than 10% error rate
                    issues.append(f"High error rate: {error_rate:.1%}")
                    health_score -= 0.2
            
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
            parameters={
                'supported_formats': self.get_supported_formats(),
                'recursive_scan': True
            },
            required_parameters=[],
            optional_parameters=['recursive_scan'],
            validation_rules={
                'recursive_scan': [True, False]
            },
            last_updated=datetime.now()
        )
    
    def update_configuration(self, config: ModuleConfiguration) -> bool:
        """Update module configuration."""
        try:
            if not config.is_valid():
                return False
            
            # Update configuration parameters
            logger.info(f"Configuration updated for {self.module_id}")
            return True
            
        except Exception as e:
            logger.error(f"Configuration update error: {e}")
            return False
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get module metrics."""
        uptime = (datetime.now() - self._start_time).total_seconds()
        stats = self.get_media_statistics()
        
        return {
            'uptime_seconds': uptime,
            'uptime_hours': uptime / 3600,
            'files_processed': stats['files_processed'],
            'files_detected': stats['files_detected'],
            'detection_rate': stats['detection_rate'],
            'errors': stats['errors'],
            'error_rate': stats['error_rate'],
            'supported_formats': stats['supported_formats'],
            'last_check': datetime.now().isoformat()
        }
    
    def reset_metrics(self) -> None:
        """Reset module metrics to initial state."""
        self._files_processed = 0
        self._files_detected = 0
        self._errors = 0
        self._start_time = datetime.now()
        logger.info("Metrics reset for media detector module")