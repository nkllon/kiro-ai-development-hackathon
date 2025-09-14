
    def _extract_method_docstring(self, method: callable) -> str:
        """Extract docstring from method"""
        try:
            return method.__doc__ or f'Execute {method.__name__} operation'
        except:
            return f'Execute {method.__name__} operation'
