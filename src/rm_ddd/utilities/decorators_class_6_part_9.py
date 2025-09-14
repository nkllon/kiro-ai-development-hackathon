from src.rm_ddd.core.health import ModuleHealth, ModuleStatus

    def check_aggregate_size(self):
        """Check aggregate size limits."""
        current_size = getattr(self, '_aggregate_size', 0)
        if current_size > max_size:
            raise DomainException(f'Aggregate size ({current_size}) exceeds limit ({max_size})', error_code='AGGREGATE_SIZE_EXCEEDED')
        return current_size
    cls._check_aggregate_size = check_aggregate_size
