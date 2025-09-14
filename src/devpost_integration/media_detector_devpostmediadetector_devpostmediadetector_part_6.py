
    def __init__(self):
        """Initialize media detector"""
        super().__init__(module_id="media_detector", version="1.0.0")
        self.format_registry = MediaFormatRegistry()
        self.metadata_extractor = MediaMetadataExtractor()
        self._start_time = datetime.now()
        self._files_processed = 0
        self._files_detected = 0
        self._errors = 0
        register_module(self)
    