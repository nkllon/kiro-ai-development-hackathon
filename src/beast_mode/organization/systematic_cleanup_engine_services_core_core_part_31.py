
def get_module_status(self) -> str:
    """Get current module status"""
    return f'CLEANUP_ENGINE:ACTIVE:{len(self.cleanup_history)}_PLANS'
