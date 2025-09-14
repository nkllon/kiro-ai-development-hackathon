
def _suggest_quality_goals(self, team_id: str, qa_results: Dict[str, Any]) -> List[str]:
    """Suggest next quality goals for team"""
    goals = []
    current_coverage = qa_results.get('coverage_percentage', 0.8)
    if current_coverage < 0.95:
        goals.append(f'Achieve {int((current_coverage + 0.05) * 100)}% test coverage')
    goals.append('Implement systematic quality gates in CI/CD')
    goals.append('Establish quality metrics baseline for continuous improvement')
    return goals
