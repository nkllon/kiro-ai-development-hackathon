from src.rm_ddd.core.health import ModuleHealth

    def get_dependencies(self) -> List[str]:
        """Get module dependencies."""
        return [
            'media_formats',
            'media_metadata'
        ]
    