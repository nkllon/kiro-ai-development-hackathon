
def set_collaboration_callback(self, callback_name: str, callback: Callable) -> None:
    """
        Set a callback for collaboration events.
        
        Args:
            callback_name: Name of the callback
            callback: Callback function
        """
    self.collaboration_scheduler.set_collaboration_callback(callback_name, callback)
