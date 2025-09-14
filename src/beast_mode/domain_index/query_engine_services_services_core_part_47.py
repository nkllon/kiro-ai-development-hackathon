
    def dfs_cycle_detection(current: str, path: List[str], visited: Set[str]) -> None:
        if current in path:
            cycle_start = path.index(current)
            cycle = path[cycle_start:] + [current]
            if domain_name in cycle:
                circular_chains.append(cycle)
            return
        if current in visited or current not in all_domains:
            return
        visited.add(current)
        path.append(current)
        for dep in all_domains[current].dependencies:
            dfs_cycle_detection(dep, path.copy(), visited.copy())
    dfs_cycle_detection(domain_name, [], set())
    return circular_chains
