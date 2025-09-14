from src.rm_ddd.core.health import ModuleHealth

def _apply_group_size_limits(self, groups: Dict[str, List[TestFailureData]]) -> Dict[str, List[TestFailureData]]:
    """Apply size limits and create overflow groups"""
    limited_groups = {}
    for group_name, group_failures in groups.items():
        if len(group_failures) <= self.max_failures_per_group:
            limited_groups[group_name] = group_failures
        else:
            for i in range(0, len(group_failures), self.max_failures_per_group):
                chunk = group_failures[i:i + self.max_failures_per_group]
                chunk_name = f'{group_name}_chunk_{i // self.max_failures_per_group}'
                limited_groups[chunk_name] = chunk
    return limited_groups
