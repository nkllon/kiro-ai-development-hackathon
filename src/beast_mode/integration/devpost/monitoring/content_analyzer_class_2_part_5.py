from src.rm_ddd.core.registry import register_module
from src.rm_ddd.core.health import ModuleHealth


    def analyze_file_change(self, file_path: Path, change_type: str) -> Dict[str, Any]:
        """
        Analyze a file change for significance and metadata.
        
        Args:
            file_path: Path to the changed file
            change_type: Type of change (created, modified, deleted)
            
        Returns:
            Dictionary containing analysis results
        """
        analysis = {'is_significant_change': True, 'content_hash': None, 'previous_content_hash': None, 'media_metadata': None, 'git_info': None, 'content_type': None}
        try:
            analysis['content_type'] = self._get_content_type(file_path)
            if change_type == 'deleted':
                analysis['content_hash'] = None
                analysis['previous_content_hash'] = self._content_cache.get(str(file_path))
            else:
                content_hash = self._calculate_content_hash(file_path)
                analysis['content_hash'] = content_hash
                analysis['previous_content_hash'] = self._content_cache.get(str(file_path))
                if analysis['previous_content_hash'] == content_hash:
                    analysis['is_significant_change'] = False
                else:
                    self._content_cache[str(file_path)] = content_hash
                if self._is_documentation_file(file_path):
                    analysis['is_significant_change'] = self._analyze_documentation_change(file_path, analysis['previous_content_hash'], content_hash)
                if self._is_media_file(file_path):
                    analysis['media_metadata'] = self._analyze_media_file(file_path)
            if self._git_repo:
                analysis['git_info'] = self._get_git_info(file_path)
        except Exception as e:
            logger.error(f'Error analyzing file change for {file_path}: {e}')
        return analysis

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

