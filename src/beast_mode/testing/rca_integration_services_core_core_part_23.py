
def _split_by_correlation(self, failures: List[TestFailureData], correlation_matrix: List[List[float]]) -> List[List[TestFailureData]]:
    """Split failures into subgroups based on correlation matrix"""
    n = len(failures)
    if n <= 1:
        return [failures]
    threshold = 0.6
    groups = []
    assigned = [False] * n
    for i in range(n):
        if assigned[i]:
            continue
        group = [failures[i]]
        assigned[i] = True
        for j in range(i + 1, n):
            if not assigned[j] and correlation_matrix[i][j] > threshold:
                group.append(failures[j])
                assigned[j] = True
        groups.append(group)
    return groups
