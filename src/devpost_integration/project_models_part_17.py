
    def update_project_data(self, updates: Dict[str, Any]) -> bool:
        """Update project data."""
        try:
            self.project_data.update(updates)
            if 'project_id' in updates:
                self.project_id = updates['project_id']
            if 'title' in updates:
                self.title = updates['title']
            if 'description' in updates:
                self.description = updates['description']
            if 'status' in updates:
                self.status = updates['status']
            self._operation_count += 1
            return True
        except Exception as e:
            logger.error(f'Failed to update project data: {e}')
            self._errors += 1
            return False
