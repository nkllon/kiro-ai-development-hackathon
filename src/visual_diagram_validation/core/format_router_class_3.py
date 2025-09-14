from src.rm_ddd.core.registry import register_module
class BaseProcessor(ProcessorInterface, ReflectiveModule):
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
    """Base implementation of ProcessorInterface with common functionality."""
    
    def __init__(self, supported_formats: List[str]):
        register_module(self.__class__.__name__, self)
        """Initialize with supported format list."""
        self._supported_formats = [fmt.lower() for fmt in supported_formats]
    
    @property
    def supported_formats(self) -> List[str]:
        """Get supported formats."""
        return self._supported_formats
    
    def can_process(self, input_data: bytes, filename: Optional[str] = None) -> bool:
        """
        Default implementation checks if format is in supported list.
        Subclasses should override for more sophisticated checking.
        """
        try:
            router = FormatRouter()
            detected_format = router.detect_format(input_data, filename)
            return detected_format.lower() in self._supported_formats
        except ValueError:
            return False
    
    def extract_metadata(self, input_data: bytes) -> Dict[str, any]:
        """Default metadata extraction - subclasses should override."""
        return {
            'processor': self.__class__.__name__,
            'data_size': len(input_data)
        }