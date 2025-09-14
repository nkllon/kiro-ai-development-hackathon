from src.rm_ddd.core.health import ModuleHealth

def _merge_correlated_groups(self, correlated_groups: Dict[str, List[TestFailureData]]) -> Dict[str, List[TestFailureData]]:
    """Merge groups that show high correlation across group boundaries"""
    merged_groups = {}
    processed_groups = set()
    group_names = list(correlated_groups.keys())
    for i, group_a in enumerate(group_names):
        if group_a in processed_groups:
            continue
        merged_group = correlated_groups[group_a][:]
        merged_name = group_a
        processed_groups.add(group_a)
        for j, group_b in enumerate(group_names[i + 1:], i + 1):
            if group_b in processed_groups:
                continue
            correlation_score = self._calculate_cross_group_correlation(correlated_groups[group_a], correlated_groups[group_b])
            if correlation_score > 0.7:
                merged_group.extend(correlated_groups[group_b])
                merged_name = f'{merged_name}_merged_{group_b}'
                processed_groups.add(group_b)
        merged_groups[merged_name] = merged_group
    return merged_groups
