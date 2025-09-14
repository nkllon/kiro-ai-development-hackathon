
def _categorize_file(self, file_path: Path) -> FileCategory:
    """Systematically categorize file based on name, extension, and content patterns"""
    name = file_path.name.lower()
    suffix = file_path.suffix.lower()
    if any((keyword in name for keyword in ['beast', 'systematic', 'test', 'summary', 'analysis', 'report'])):
        if suffix == '.md':
            return FileCategory.SYSTEMATIC_DOCUMENT
    if name.startswith('test_') or 'test' in name:
        if suffix == '.py':
            return FileCategory.TEST_FILE
    if suffix in ['.py', '.sh', '.js'] and (not name.startswith('test_')):
        return FileCategory.SCRIPT
    if suffix in ['.json', '.yaml', '.yml', '.toml', '.cfg', '.ini']:
        return FileCategory.CONFIGURATION
    if suffix in ['.mov', '.mp4', '.pdf', '.docx', '.png', '.jpg']:
        return FileCategory.MEDIA
    if suffix == '.md' and any((keyword in name for keyword in ['research', 'rdi', 'analysis'])):
        return FileCategory.RESEARCH
    if suffix in ['.log', '.txt'] or name in ['.coverage', '.ds_store']:
        return FileCategory.DEVELOPMENT_ARTIFACT
    if name.startswith('.') or suffix in ['.tmp', '.temp']:
        return FileCategory.TEMPORARY
    return FileCategory.UNKNOWN
