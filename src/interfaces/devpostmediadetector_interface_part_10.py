from src.rm_ddd.core.health import ModuleHealth

    def get_supported_formats(self) -> Dict[MediaType, List[str]]:
        """Get supported media formats by type"""
        return self.format_registry.get_supported_formats()
    