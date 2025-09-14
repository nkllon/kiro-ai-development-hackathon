
def _create_basic_failure_groups(self, failures: List[TestFailureData]) -> Dict[str, List[TestFailureData]]:
    """Create initial failure groups based on basic characteristics"""
    basic_groups = {}
    for failure in failures:
        group_key = self._generate_failure_group_key(failure)
        if group_key not in basic_groups:
            basic_groups[group_key] = []
        basic_groups[group_key].append(failure)
    return basic_groups
