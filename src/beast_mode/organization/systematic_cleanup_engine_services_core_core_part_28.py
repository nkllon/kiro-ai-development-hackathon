
def _load_file_patterns(self) -> Dict[str, List[str]]:
    """Load file categorization patterns"""
    return {'systematic_documents': ['*beast*', '*systematic*', '*test*summary*', '*analysis*'], 'temporary_files': ['.*', '*.tmp', '*.temp', '.coverage*'], 'development_artifacts': ['*.log', '*report*.json', '*audit*'], 'scripts': ['*.py', '*.sh', '*.js'], 'media': ['*.mov', '*.mp4', '*.pdf', '*.docx', '*.png']}
