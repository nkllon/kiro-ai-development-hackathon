from src.rm_ddd.core.health import ModuleHealth

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