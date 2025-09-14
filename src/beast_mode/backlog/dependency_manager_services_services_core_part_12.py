
def _would_create_cycle(self, source_item: str, target_item: str, temp_deps: Dict[str, DependencySpec]) -> bool:
    """Check if adding a dependency would create a cycle"""
    if source_item == target_item:
        return False
    temp_graph = self._build_temp_graph(temp_deps)
    if target_item not in temp_graph:
        temp_graph[target_item] = set()
    temp_graph[target_item].add(source_item)
    return self._has_path(temp_graph, source_item, target_item)
