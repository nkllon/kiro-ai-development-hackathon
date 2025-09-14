
    def get_active_help_requests(self) -> List:
        """Get all active help requests"""
        return [req.__dict__ for req in self.help_system.get_active_requests()]
