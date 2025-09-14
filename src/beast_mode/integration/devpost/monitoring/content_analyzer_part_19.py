from datetime import datetime
from typing import Dict, List, Any
from src.rm_ddd.core.health import ModuleHealth


    def detect_git_releases(self) -> List[Dict[str, Any]]:
        """Detect new Git releases and tags."""
        releases = []
        if not self._git_repo:
            return releases
        try:
            tags = list(self._git_repo.tags)
            tags.sort(key=lambda t: t.commit.committed_datetime, reverse=True)
            recent_threshold = datetime.now().timestamp() - 24 * 60 * 60
            for tag in tags[:10]:
                tag_date = tag.commit.committed_datetime.timestamp()
                if tag_date > recent_threshold:
                    releases.append({'tag_name': tag.name, 'commit_hash': tag.commit.hexsha, 'commit_message': tag.commit.message.strip(), 'created_at': tag.commit.committed_datetime, 'is_release': self._is_release_tag(tag.name)})
        except Exception as e:
            logger.error(f'Error detecting Git releases: {e}')
        return releases

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

