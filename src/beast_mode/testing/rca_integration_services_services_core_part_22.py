from src.rm_ddd.core.health import ModuleHealth

def _build_correlation_matrix(self, failures: List[TestFailureData]) -> List[List[float]]:
    """Build correlation matrix for failures within a group"""
    n = len(failures)
    matrix = [[0.0 for _ in range(n)] for _ in range(n)]
    for i in range(n):
        for j in range(n):
            if i == j:
                matrix[i][j] = 1.0
            else:
                matrix[i][j] = self._calculate_failure_similarity(failures[i], failures[j])
    return matrix
