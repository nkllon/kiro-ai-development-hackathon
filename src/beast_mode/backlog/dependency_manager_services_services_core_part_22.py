
def _estimate_dependency_duration(self, source: str, target: str) -> timedelta:
    """Estimate duration for a dependency relationship"""
    for dep_spec in self._dependencies.values():
        if dep_spec.target_item_id == source and '_depends_on_' in dep_spec.dependency_id and (dep_spec.dependency_id.split('_depends_on_')[0] == target):
            if dep_spec.estimated_completion:
                return dep_spec.estimated_completion - datetime.now()
    return timedelta(days=1)
