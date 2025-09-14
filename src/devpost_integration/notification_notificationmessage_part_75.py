from src.rm_ddd.core.health import ModuleHealth

def __init__(self, message_data: Dict[str, Any]=None):
    """Initialize notification message."""
    super().__init__()
    self.module_id = 'notification_message'
    self.version = '1.0.0'
    self.message_data = message_data or {}
    self.message_id = self.message_data.get('id', '')
    self.title = self.message_data.get('title', '')
    self.content = self.message_data.get('content', '')
    self.recipients = self.message_data.get('recipients', [])
    self.priority = self.message_data.get('priority', 'normal')
    self.status = self.message_data.get('status', 'pending')
    self.created_at = datetime.now()
    self.sent_at = None
    self._operation_count = 0
    self._errors = 0
    register_module(self)
