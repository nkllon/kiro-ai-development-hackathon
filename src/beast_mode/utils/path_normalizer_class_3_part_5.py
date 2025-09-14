from src.rm_ddd.core.registry import register_module

    def validate_file_extension(path: Union[str, Path], allowed_extensions: List[str]) -> bool:
        """
        Validate that a file has an allowed extension.
        
        Args:
            path: File path to validate
            allowed_extensions: List of allowed extensions (with or without dots)
            
        Returns:
            bool: True if extension is allowed, False otherwise
        """
        path_obj = Path(path)
        extension = path_obj.suffix.lower()
        normalized_extensions = []
        for ext in allowed_extensions:
            if not ext.startswith('.'):
                ext = '.' + ext
            normalized_extensions.append(ext.lower())
        return extension in normalized_extensions

    @staticmethod