from src.rm_ddd.core.health import ModuleHealth

def register_message_handler(self, message_type: MessageType, handler: Callable[[BeastModeMessage], None]) -> None:
    """Register a custom message handler"""
    if message_type not in self.message_handlers:
        self.message_handlers[message_type] = []
    self.message_handlers[message_type].append(handler)
    logger.info(f'Registered handler for {message_type}')
