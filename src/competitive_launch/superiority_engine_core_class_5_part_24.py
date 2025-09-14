from src.rm_ddd.core.registry import register_module

def _calculate_competitive_advantage_level(self) -> str:
    try:
        pass  # TODO: Add method implementation
    except Exception as e:
        logging.error(f"Error in method: {e}")
        raise
    """Calculate overall competitive advantage level."""
    if not self.metrics:
        return 'Unknown'
    avg_improvement = sum((m.improvement_percentage for m in self.metrics)) / len(self.metrics)
    if avg_improvement > 50:
        return 'Exceptional'
    elif avg_improvement > 30:
        return 'Significant'
    elif avg_improvement > 15:
        return 'Moderate'
    else:
        return 'Minimal'
