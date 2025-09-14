
    def _extract_method_arguments(self, method: callable) -> List[Dict[str, Any]]:
        """Extract method arguments for CLI generation"""
        try:
            sig = inspect.signature(method)
            arguments = []
            for param_name, param in sig.parameters.items():
                if param_name != 'self':
                    arg_info = {'name': param_name, 'type': str(param.annotation) if param.annotation != inspect.Parameter.empty else 'str', 'default': param.default if param.default != inspect.Parameter.empty else None, 'required': param.default == inspect.Parameter.empty}
                    arguments.append(arg_info)
            return arguments
        except:
            return []
