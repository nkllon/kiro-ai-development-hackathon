from src.rm_ddd.core.health import ModuleHealth

    def create_backlog_item(self, item_spec: BacklogItemSpec) -> BacklogItem:
        """Create a new backlog item with validation"""
        return self._core_operations.create_backlog_item(item_spec, len(self._backlog_items))
            