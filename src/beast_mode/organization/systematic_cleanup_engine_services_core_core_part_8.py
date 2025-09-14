from src.rm_ddd.core.health import ModuleHealth

def _determine_systematic_location(self, file_path: Path, category: FileCategory) -> str:
    """Determine systematic location for file based on category"""
    location_mapping = {FileCategory.SYSTEMATIC_DOCUMENT: 'docs/systematic/', FileCategory.DEVELOPMENT_ARTIFACT: 'archive/development-artifacts/', FileCategory.TEST_FILE: 'tests/', FileCategory.SCRIPT: 'scripts/', FileCategory.RESEARCH: 'archive/research/', FileCategory.CONFIGURATION: 'config/', FileCategory.MEDIA: 'archive/media/', FileCategory.TEMPORARY: 'DELETE', FileCategory.UNKNOWN: 'archive/uncategorized/'}
    return location_mapping.get(category, 'archive/uncategorized/')
