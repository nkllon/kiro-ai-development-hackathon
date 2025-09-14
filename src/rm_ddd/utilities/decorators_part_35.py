from src.rm_ddd.core.health import ModuleHealth, ModuleStatus

    def check_complexity(self):
        """Check if class complexity exceeds limits."""
        current_complexity = len([m for m in dir(self) if not m.startswith('_')])
        if current_complexity > max_complexity:
            logger.warning(f'Class {cls.__name__} complexity ({current_complexity}) exceeds limit ({max_complexity})')
        return current_complexity
    cls._check_complexity = check_complexity
