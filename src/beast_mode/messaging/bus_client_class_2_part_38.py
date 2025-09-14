
def get_recent_messages(self, limit: int=10) -> List[BeastModeMessage]:
    """Get recent received messages"""
    return self.received_messages[-limit:] if self.received_messages else []
