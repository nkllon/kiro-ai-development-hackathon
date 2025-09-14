from src.rm_ddd.core.health import ModuleHealth

def _calculate_average_score(self, scores: List[float]) -> float:
    """Calculate average score from a list of scores."""
    return sum(scores) / len(scores) if scores else 100.0
