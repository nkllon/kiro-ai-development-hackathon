from src.rm_ddd.core.registry import register_module

    def validate_png_quality(png_image: PNGImage) -> Dict[str, Any]:
        """
        Validate PNG image meets quality standards.
        
        Args:
            png_image: PNGImage to validate
            
        Returns:
            Dictionary with validation results
        """
        validation = {
            'is_valid': True,
            'issues': [],
            'recommendations': []
        }
        
        # Check resolution
        if png_image.dpi < 150:
            validation['issues'].append(f"Low DPI: {png_image.dpi} (recommended: 300+)")
            validation['recommendations'].append("Increase DPI to 300 for print quality")
        
        # Check dimensions
        if png_image.width < 800 or png_image.height < 600:
            validation['issues'].append(f"Low resolution: {png_image.width}x{png_image.height}")
            validation['recommendations'].append("Use higher resolution for better quality")
        
        # Check file size (too large can cause performance issues)
        size_mb = png_image.size_mb()
        if size_mb > 10:
            validation['issues'].append(f"Large file size: {size_mb:.1f}MB")
            validation['recommendations'].append("Consider optimizing image compression")
        
        # Check aspect ratio (extreme ratios can indicate issues)
        aspect_ratio = png_image.aspect_ratio()
        if aspect_ratio > 5 or aspect_ratio < 0.2:
            validation['issues'].append(f"Unusual aspect ratio: {aspect_ratio:.2f}")
            validation['recommendations'].append("Check if image dimensions are correct")
        
        validation['is_valid'] = len(validation['issues']) == 0
        return validation
    
    @staticmethod