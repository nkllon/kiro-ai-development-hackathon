from src.rm_ddd.core.health import ModuleHealth

def _generate_placement_rationale(self, file_path: Path, category: FileCategory, location: str) -> str:
    """Generate systematic rationale for file placement"""
    rationales = {FileCategory.SYSTEMATIC_DOCUMENT: f'Systematic document should be organized in docs/ for accessibility', FileCategory.DEVELOPMENT_ARTIFACT: f'Development artifact should be archived to reduce root clutter', FileCategory.TEST_FILE: f'Test file belongs in tests/ directory for systematic organization', FileCategory.SCRIPT: f'Script should be organized in scripts/ for systematic access', FileCategory.RESEARCH: f'Research document should be archived for systematic knowledge management', FileCategory.CONFIGURATION: f'Configuration file should be in config/ for systematic management', FileCategory.MEDIA: f'Media file should be archived to reduce root directory clutter', FileCategory.TEMPORARY: f'Temporary file should be removed to maintain systematic cleanliness', FileCategory.UNKNOWN: f'Unknown file type should be archived pending systematic categorization'}
    return rationales.get(category, 'File requires systematic placement analysis')
