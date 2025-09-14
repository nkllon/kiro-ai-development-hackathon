from src.rm_ddd.core.registry import register_module

def register_handler(self, message_type: MessageType, handler: Callable[[BeastModeMessage], None]):
    try:
        pass  # TODO: Add method implementation
    except Exception as e:
        logging.error(f"Error in method: {e}")
        raise
    """
        Register a message handler for specific message type.
        
        Args:
            message_type: Type of message to handle
            handler: Function to call when message received
        """
    if message_type not in self.message_handlers:
        self.message_handlers[message_type] = []
    self.message_handlers[message_type].append(handler)
    self.logger.info(f'Registered handler for {message_type}')
