
    def register_handler(self, verb: str, noun: str, handler: Callable[[StructuredAction], ActionResult]) -> None:
        """Register an action handler."""
        key = f'{verb}_{noun}'
        self.action_handlers[key] = handler
        self.update_activity()
