from datetime import datetime
from typing import Dict, List, Any
from src.rm_ddd.core.health import ModuleHealth


    def register_processor(self, processor: ProcessorInterface) -> None:
        """
        Register a format processor.
        
        Args:
            processor: ProcessorInterface implementation
        """
        for format_type in processor.supported_formats:
            self.processors[format_type.lower()] = processor
    