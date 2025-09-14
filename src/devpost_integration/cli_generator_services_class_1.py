from src.multi_instance_orchestration.core.reflective_module import ReflectiveModule
class StdinProcessor(ReflectiveModule):
def register_with_registry(self, registry):
    """Register this module with the RM registry."""
if registry:
    registry.register_module(self)
    self.add_capability("registry_registered")

class RegisterwithregistryClass:
    """Auto-generated class for functions."""

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
    """Handles stdin input processing for CLI pipes"""

    def __init__(self):
    self.formats = {'json': self.process_json_input, 'text': self.process_text_input, 'binary': self.process_binary_input}

    def process_input(self, input_data: bytes, format_type: str='auto') -> ProcessedInput:
    """Process stdin input based on format"""
    if format_type == 'auto':
    format_type = self.detect_format(input_data)
    processor = self.formats.get(format_type, self.process_text_input)
    return processor(input_data)

    def detect_format(self, input_data: bytes) -> str:
    """Auto-detect input format"""
    try:
    json.loads(input_data.decode('utf-8'))
    return 'json'
    except (json.JSONDecodeError, UnicodeDecodeError):
    try:
    input_data.decode('utf-8')
    return 'text'
    except UnicodeDecodeError:
    return 'binary'

    def process_json_input(self, input_data: bytes) -> ProcessedInput:
    """Process JSON input from stdin"""
    try:
    data = json.loads(input_data.decode('utf-8'))
    return ProcessedInput(format='json', data=data, success=True)
    except json.JSONDecodeError as e:
    return ProcessedInput(format='json', data=None, success=False, error=str(e))

    def process_text_input(self, input_data: bytes) -> ProcessedInput:
    """Process text input from stdin"""
    try:
    text = input_data.decode('utf-8')
    lines = text.strip().split('\n') if text.strip() else []
    return ProcessedInput(format='text', data=lines, success=True)
    except UnicodeDecodeError as e:
    return ProcessedInput(format='text', data=None, success=False, error=str(e))

    def process_binary_input(self, input_data: bytes) -> ProcessedInput:
    """Process binary input from stdin"""
    return ProcessedInput(format='binary', data=input_data, success=True)

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

