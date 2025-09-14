
    def __init__(self, instance_id: str):
        super().__init__('TextProtocolHandler', '1.0.0')
        self.instance_id = instance_id
        self.command_patterns: dict[str, CommandPattern] = {}
        self.action_handlers: dict[str, Callable[[StructuredAction], ActionResult]] = {}
        self.command_history: list[StructuredAction] = []
        self.execution_stats = {'total_commands': 0, 'successful_commands': 0, 'failed_commands': 0, 'average_execution_time': 0.0}
        self._register_default_patterns()
