from datetime import datetime
from typing import Dict, List, Any
from src.rm_ddd.core.health import ModuleHealth


    def extract_metadata(image_data: bytes) -> Dict[str, Any]:
        """
        Extract metadata from PNG image bytes.
        
        Args:
            image_data: Raw PNG bytes
            
        Returns:
            Dictionary containing extracted metadata
        """
        metadata = {}
        
        try:
            with Image.open(io.BytesIO(image_data)) as img:
                # Basic image properties
                metadata['original_format'] = img.format
                metadata['original_mode'] = img.mode
                metadata['original_size'] = img.size
                
                # DPI information
                if hasattr(img, 'info') and 'dpi' in img.info:
                    metadata['original_dpi'] = img.info['dpi']
                
                # Extract EXIF data if present
                if hasattr(img, '_getexif') and img._getexif():
                    metadata['exif'] = dict(img._getexif())
                
                # PNG-specific metadata
                if img.format == 'PNG' and hasattr(img, 'text'):
                    metadata['png_text'] = dict(img.text)
                
                # Color profile information
                if hasattr(img, 'info') and 'icc_profile' in img.info:
                    metadata['has_color_profile'] = True
                
        except Exception as e:
            metadata['extraction_error'] = str(e)
        
        return metadata
    
    @staticmethod