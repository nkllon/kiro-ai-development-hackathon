from src.rm_ddd.core.health import ModuleHealth

def _get_commit_info(self, commit_hash: str) -> Optional[CommitInfo]:
    """Get detailed information for a specific commit."""
    try:
        cmd = ['git', 'show', '--format=%H|%an|%at|%s', '--name-status', '--no-merges', commit_hash]
        result = subprocess.run(cmd, cwd=self.repository_path, capture_output=True, text=True, timeout=self._config['git_timeout'])
        if result.returncode != 0:
            self.logger.error(f'Failed to get commit info for {commit_hash}: {result.stderr}')
            return None
        lines = result.stdout.strip().split('\n')
        if not lines:
            return None
        metadata_parts = lines[0].split('|', 3)
        if len(metadata_parts) != 4:
            self.logger.error(f'Invalid commit metadata format for {commit_hash}')
            return None
        hash_val, author, timestamp_str, message = metadata_parts
        timestamp = datetime.fromtimestamp(int(timestamp_str))
        added_files = []
        modified_files = []
        deleted_files = []
        for line in lines[1:]:
            if not line.strip():
                continue
            parts = line.split('\t', 1)
            if len(parts) != 2:
                continue
            status, file_path = parts
            if status == 'A':
                added_files.append(file_path)
            elif status == 'M':
                modified_files.append(file_path)
            elif status == 'D':
                deleted_files.append(file_path)
            elif status.startswith('R'):
                modified_files.append(file_path.split('\t')[-1])
        return CommitInfo(commit_hash=hash_val, author=author, timestamp=timestamp, message=message, modified_files=modified_files, added_files=added_files, deleted_files=deleted_files)
    except subprocess.TimeoutExpired:
        self.logger.error(f'Git command timed out for commit {commit_hash}')
        return None
    except Exception as e:
        self.logger.error(f'Error getting commit info for {commit_hash}: {str(e)}')
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

