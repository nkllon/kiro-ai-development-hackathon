
def _build_item_subgraph(self, full_graph: DependencyGraph, item_id: str) -> DependencyGraph:
    """Build subgraph containing dependencies for a specific item"""
    reachable_nodes = set()
