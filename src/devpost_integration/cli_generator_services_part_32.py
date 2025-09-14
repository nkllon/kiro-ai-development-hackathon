from src.rm_ddd.core.health import ModuleHealth

    def _extract_method_return_type(self, method: callable) -> str:
        """Extract return type from method"""
        try:
            sig = inspect.signature(method)
            return_type = sig.return_annotation
            if return_type != inspect.Parameter.empty:
                return str(return_type)
            else:
                return 'Any'
        except:
            return 'Any'
