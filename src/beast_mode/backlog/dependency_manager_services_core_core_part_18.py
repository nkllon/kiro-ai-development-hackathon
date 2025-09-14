
def _generate_cycle_resolution_suggestions(self, cycles: List[List[str]]) -> List[str]:
    """Generate suggestions for resolving circular dependencies"""
    suggestions = []
    for i, cycle in enumerate(cycles):
        suggestions.append(f"Cycle {i + 1}: {' -> '.join(cycle)}")
        suggestions.append(f'  - Consider removing dependency between {cycle[-2]} and {cycle[-1]}')
        suggestions.append(f'  - Or restructure to eliminate circular relationship')
    if not cycles:
        suggestions.append('No circular dependencies detected')
    return suggestions
