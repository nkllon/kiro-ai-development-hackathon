
    def _get_commit_line_changes(self, commit_hash: str) -> Tuple[int, int]:
        """Get the number of lines added and deleted in a commit."""
        try:
            cmd = ['git', 'show', '--numstat', '--format=', commit_hash]
            result = subprocess.run(cmd, cwd=self.repository_path, capture_output=True, text=True, timeout=self._config['git_timeout'])
            if result.returncode != 0:
                return (0, 0)
            lines_added = 0
            lines_deleted = 0
            for line in result.stdout.strip().split('\n'):
                if not line.strip():
                    continue
                parts = line.split('\t')
                if len(parts) >= 2:
                    try:
                        added = int(parts[0]) if parts[0] != '-' else 0
                        deleted = int(parts[1]) if parts[1] != '-' else 0
                        lines_added += added
                        lines_deleted += deleted
                    except ValueError:
                        continue
            return (lines_added, lines_deleted)
        except Exception:
            return (0, 0)
