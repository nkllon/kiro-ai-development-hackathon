from src.rm_ddd.core.health import ModuleHealth

def save_spore(self, spore_content: str, metadata: Dict[str, Any]) -> str:
    """
        Save a spore with metadata and content
        
        Args:
            spore_content: The implementation content of the spore
            metadata: Spore metadata dictionary
            
        Returns:
            str: The spore identifier/name
            
        Raises:
            ValueError: If spore validation fails
        """
    try:
        spore_metadata = SporeMetadata(**metadata)
        spore_name = spore_metadata.name
        checksum = self._calculate_checksum(spore_content)
        spore_metadata.checksum = checksum
        spore_metadata.updated_at = datetime.now()
        metadata_path, content_path = self._get_spore_paths(spore_name)
        spore_metadata.file_path = str(content_path)
        if not self.validate_spore(spore_content):
            raise ValueError(f'Spore validation failed for {spore_name}')
        if spore_name in self._spore_cache:
            self._create_version_backup(spore_name)
        with open(metadata_path, 'w') as f:
            json.dump(spore_metadata.model_dump(), f, indent=2, default=str)
        with open(content_path, 'w') as f:
            f.write(spore_content)
        spore = SporeContent(metadata=spore_metadata, implementation=spore_content)
        self._spore_cache[spore_name] = spore
        logger.info(f'Successfully saved spore: {spore_name}')
        return spore_name
    except ValidationError as e:
        logger.error(f'Metadata validation failed: {e}')
        raise ValueError(f'Invalid spore metadata: {e}')
    except Exception as e:
        logger.error(f'Failed to save spore: {e}')
        raise

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

