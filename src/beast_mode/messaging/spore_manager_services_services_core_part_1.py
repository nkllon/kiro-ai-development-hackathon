
def __init__(self, spore_directory: str='spores'):
    """
        Initialize SporeManager
        
        Args:
            spore_directory: Directory to store spores
        """
    self.spore_directory = Path(spore_directory)
    self.spore_directory.mkdir(parents=True, exist_ok=True)
    self.metadata_dir = self.spore_directory / 'metadata'
    self.content_dir = self.spore_directory / 'content'
    self.versions_dir = self.spore_directory / 'versions'
    for directory in [self.metadata_dir, self.content_dir, self.versions_dir]:
        directory.mkdir(parents=True, exist_ok=True)
    self._spore_cache: Dict[str, SporeContent] = {}
    self._load_existing_spores()
