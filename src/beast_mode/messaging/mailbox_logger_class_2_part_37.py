from src.rm_ddd.core.registry import register_module

def save_full_content(self, message: BeastModeMessage) -> str:
    """
        Save full message content to a separate detailed log.
        
        Args:
            message: The message to save
            
        Returns:
            str: Path to the saved content file
        """
    try:
        content_dir = self.log_directory / 'detailed_content'
        content_dir.mkdir(exist_ok=True)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'message_{timestamp}_{message.id[:8]}.json'
        content_file = content_dir / filename
        detailed_content = {'message': message.model_dump(), 'saved_at': datetime.now().isoformat(), 'logger_stats': self.get_logger_stats()}
        with open(content_file, 'w', encoding='utf-8') as f:
            json.dump(detailed_content, f, indent=2, default=str)
        logger.debug(f'Saved detailed content to: {content_file}')
        return str(content_file)
    except Exception as e:
        logger.error(f'Error saving detailed content: {e}')
        raise
