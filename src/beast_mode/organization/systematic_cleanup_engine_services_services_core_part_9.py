
def _assess_cleanup_priority(self, file_path: Path, category: FileCategory) -> CleanupPriority:
    """Assess cleanup priority based on systematic impact"""
    name = file_path.name.lower()
    if category == FileCategory.TEMPORARY or name in ['.ds_store', '.coverage']:
        return CleanupPriority.CRITICAL
    if category in [FileCategory.DEVELOPMENT_ARTIFACT, FileCategory.UNKNOWN]:
        return CleanupPriority.HIGH
    if category in [FileCategory.SCRIPT, FileCategory.CONFIGURATION]:
        return CleanupPriority.MEDIUM
    return CleanupPriority.LOW
