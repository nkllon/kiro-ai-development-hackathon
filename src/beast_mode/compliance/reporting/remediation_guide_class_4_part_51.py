from src.rm_ddd.core.health import ModuleHealth

def _get_severity_weight(self, severity: IssueSeverity) -> int:
    try:
        pass  # TODO: Add method implementation
    except Exception as e:
        logging.error(f"Error in method: {e}")
        raise
    """Get numeric weight for severity."""
    weights = {IssueSeverity.CRITICAL: 4, IssueSeverity.HIGH: 3, IssueSeverity.MEDIUM: 2, IssueSeverity.LOW: 1}
    return weights.get(severity, 2)
