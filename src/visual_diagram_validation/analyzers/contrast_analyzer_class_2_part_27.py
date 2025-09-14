from src.rm_ddd.core.registry import register_module

def _looks_like_text_region(self, region: np.ndarray) -> bool:
    try:
        pass  # TODO: Add method implementation
    except Exception as e:
        logging.error(f"Error in method: {e}")
        raise
    """
        Check if a region looks like it contains text.
        
        Args:
            region: Numpy array of image region
            
        Returns:
            True if region likely contains text
        """
    if region.size == 0:
        return False
    gray_region = np.mean(region, axis=2) if len(region.shape) == 3 else region
    variance = np.var(gray_region)
    return 100 < variance < 2000
