from src.rm_ddd.core.health import ModuleHealth

def load_spore(self, spore_name: str) -> Optional[Dict[str, Any]]:
    """
        Load a spore by name
        
        Args:
            spore_name: Name of the spore to load
            
        Returns:
            Dict containing spore data or None if not found
        """
    try:
        if spore_name in self._spore_cache:
            spore = self._spore_cache[spore_name]
            return spore.model_dump()
        metadata_path, content_path = self._get_spore_paths(spore_name)
        if not metadata_path.exists() or not content_path.exists():
            logger.warning(f'Spore not found: {spore_name}')
            return None
        with open(metadata_path, 'r') as f:
            metadata_dict = json.load(f)
        with open(content_path, 'r') as f:
            content = f.read()
        expected_checksum = metadata_dict.get('checksum', '')
        actual_checksum = self._calculate_checksum(content)
        if expected_checksum and expected_checksum != actual_checksum:
            logger.warning(f'Checksum mismatch for spore {spore_name}')
        metadata = SporeMetadata(**metadata_dict)
        spore = SporeContent(metadata=metadata, implementation=content)
        self._spore_cache[spore_name] = spore
        return spore.model_dump()
    except Exception as e:
        logger.error(f'Failed to load spore {spore_name}: {e}')
        return None

    def register_module(self, registry):
        """Register module with registry."""
        metadata = self.get_interface_metadata()
        if hasattr(registry, 'register'):
            registry.register(metadata)
            
    def get_interface_metadata(self):
        """Get interface metadata for registry."""
        return {
            'module_id': getattr(self, 'module_id', self.__class__.__name__),
            'interface_type': self.__class__.__name__,
            'version': '1.0.0',
            'dependencies': [],
            'capabilities': []
        }

