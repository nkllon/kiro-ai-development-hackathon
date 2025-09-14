from src.rm_ddd.core.registry import register_module
class FormatRouter(ReflectiveModule):
def get_health_indicators(self) -> Dict[str, any]:
    """Get health indicators for this module."""
    return {
    "module_id": self.module_id,
    "status": self.health_status,
    "last_updated": self.last_updated,
    "capabilities_count": len(self.capabilities),
    "dependencies_count": len(self.dependencies)
    }
class GethealthindicatorsClass:
    """Auto-generated class for functions."""

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
    """Routes input data to appropriate format processors."""
    def __init__(self):
    register_module(self.__class__.__name__, self)
    """Initialize the format router."""
    self.processors: Dict[str, ProcessorInterface] = {}
    self._mime_to_format = {
    'image/svg+xml': 'svg',
    'application/pdf': 'pdf',
    'text/html': 'html',
    'text/plain': 'mermaid',  # Mermaid is plain text
    'image/png': 'png',
    'image/jpeg': 'jpeg',
    'image/gif': 'gif'
    }
    def register_processor(self, processor: ProcessorInterface) -> None:
    """
    Register a format processor.
    Args:
    processor: ProcessorInterface implementation
    """
    for format_type in processor.supported_formats:
    self.processors[format_type.lower()] = processor
    def detect_format(self, input_data: bytes, filename: Optional[str] = None) -> str:
    """
    Detect the format of input data.
    Args:
    input_data: Raw input bytes
    filename: Optional filename for extension-based detection
    Returns:
    Detected format string
    Raises:
    ValueError: If format cannot be detected
    """
    if filename:
    format_from_extension = self._detect_from_extension(filename)
    if format_from_extension:
    return format_from_extension
    format_from_magic = self._detect_from_magic_numbers(input_data)
    if format_from_magic:
    return format_from_magic
    format_from_content = self._detect_from_content(input_data)
    if format_from_content:
    return format_from_content
    raise ValueError("Unable to detect input format")
    def route_to_processor(self, format_type: str, input_data: bytes) -> ProcessorInterface:
    """
    Route to appropriate processor for the format.
    Args:
    format_type: Detected format string
    input_data: Raw input bytes
    Returns:
    ProcessorInterface for handling the format
    Raises:
    ValueError: If no processor available for format
    """
    format_key = format_type.lower()
    if format_key not in self.processors:
    raise ValueError(f"No processor available for format: {format_type}")
    processor = self.processors[format_key]
    if not processor.can_process(input_data):
    raise ValueError(f"Processor for {format_type} cannot handle this data")
    return processor
    def get_supported_formats(self) -> List[str]:
    """Get list of all supported formats."""
    return list(self.processors.keys())
    def _detect_from_extension(self, filename: str) -> Optional[str]:
    """Detect format from file extension."""
    if not filename:
    return None
    filename_lower = filename.lower()
    extension_map = {
    '.svg': 'svg',
    '.pdf': 'pdf',
    '.html': 'html',
    '.htm': 'html',
    '.mmd': 'mermaid',
    '.mermaid': 'mermaid',
    '.png': 'png',
    '.jpg': 'jpeg',
    '.jpeg': 'jpeg',
    '.gif': 'gif'
    }
    for ext, format_type in extension_map.items():
    if filename_lower.endswith(ext):
    return format_type
    return None
    def _detect_from_magic_numbers(self, data: bytes) -> Optional[str]:
    """Detect format from magic number signatures."""
    if len(data) < 8:
    return None
    if data.startswith(b'\x89PNG\r\n\x1a\n'):
    return 'png'
    if data.startswith(b'%PDF-'):
    return 'pdf'
    if data.startswith(b'\xff\xd8\xff'):
    return 'jpeg'
    if data.startswith(b'GIF87a') or data.startswith(b'GIF89a'):
    return 'gif'
    return None
    def _detect_from_content(self, data: bytes) -> Optional[str]:
    """Detect format from content analysis."""
    try:
    text_content = data.decode('utf-8', errors='ignore')
    text_lower = text_content.lower().strip()
    if text_lower.startswith('<?xml') and '<svg' in text_lower:
    return 'svg'
    if text_lower.startswith('<svg'):
    return 'svg'
    if text_lower.startswith('<!doctype html') or text_lower.startswith('<html'):
    return 'html'
    mermaid_keywords = ['graph', 'flowchart', 'sequencediagram', 'classDiagram',
    'stateDiagram', 'erDiagram', 'journey', 'gantt']
    first_line = text_content.split('\n')[0].strip().lower()
    for keyword in mermaid_keywords:
    if first_line.startswith(keyword.lower()):
    return 'mermaid'
    if any(keyword in text_lower for keyword in mermaid_keywords):
    if '-->' in text_content or '--->' in text_content or '-.->' in text_content:
    return 'mermaid'
    except UnicodeDecodeError:
    pass
    return None
    def get_interface_metadata(self):
    """Get interface metadata for registry."""
    return {
    'module_id': getattr(self, 'module_id', self.__class__.__name__),
    'interface_type': self.__class__.__name__,
    'version': '1.0.0',
    'dependencies': [],
    'capabilities': []
    }
    def register_module(self, registry):
    """Register module with registry."""
    if hasattr(registry, 'register'):
    registry.register(self.get_interface_metadata())
    def health_check(self):
    """Perform health check."""
    return {
    'status': 'healthy',
    'timestamp': datetime.now().isoformat(),
    'module_id': getattr(self, 'module_id', self.__class__.__name__)
    }
    def get_health_status(self):
    """Get current health status."""
    return self.health_check()
