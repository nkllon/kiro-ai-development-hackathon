
def generate_preview(self, content: str, content_type: str='text') -> bool:
    """Generate preview from content"""
    try:
        self._update_metrics('generate_preview')
        self.preview_data['content_type'] = content_type
        self.preview_data['generated_at'] = datetime.now().isoformat()
        self.preview_data['status'] = 'active'
        if content_type == 'text':
            self.preview_data['title'] = content[:50] + '...' if len(content) > 50 else content
            self.preview_data['description'] = content[:200] + '...' if len(content) > 200 else content
        elif content_type == 'image':
            self.preview_data['title'] = 'Image Preview'
            self.preview_data['description'] = f"Image preview generated at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        elif content_type == 'video':
            self.preview_data['title'] = 'Video Preview'
            self.preview_data['description'] = f"Video preview generated at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        else:
            self.preview_data['title'] = f'{content_type.title()} Preview'
            self.preview_data['description'] = f"{content_type.title()} preview generated at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        self.updated_at = datetime.now()
        self._metrics['previews_generated'] += 1
        self._logger.info(f'Preview generated for {content_type}: {self.preview_id}')
        return True
    except Exception as e:
        self._logger.error(f'Failed to generate preview: {e}')
        self._metrics['error_count'] += 1
        self._metrics['preview_errors'] += 1
        return False
