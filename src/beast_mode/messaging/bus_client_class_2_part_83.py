
def set_message_callback(self, callback_name: str, callback: Callable) -> None:
    """
        Set a callback for the message router.
        
        Args:
            callback_name: Name of the callback (e.g., 'on_simple_message')
            callback: Callback function
        """
    if self.message_router:
        self.message_router.set_callback(callback_name, callback)
    else:
        logger.warning('Message router not initialized, callback not set')
