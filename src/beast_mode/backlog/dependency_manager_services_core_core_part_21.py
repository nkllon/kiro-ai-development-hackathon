from src.rm_ddd.core.health import ModuleHealth

    def dfs_longest(node: str, current_path: List[str], current_duration: timedelta) -> Tuple[List[str], timedelta]:
        nonlocal path, duration
        if len(current_path) > len(path):
            path = current_path.copy()
            duration = current_duration
        visited.add(node)
        for dependent in graph.get_dependents(node):
            if dependent in valid_nodes and dependent not in visited:
                dep_duration = self._estimate_dependency_duration(node, dependent)
                dfs_longest(dependent, current_path + [dependent], current_duration + dep_duration)
        visited.remove(node)
        return (path, duration)
    return dfs_longest(start_node, [start_node], timedelta(0))
