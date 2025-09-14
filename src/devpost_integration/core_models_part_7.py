from src.rm_ddd.core.health import ModuleHealth

    def _generate_operation_id(self) -> str:
        """Generate unique operation ID."""
        return f"sync_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{id(self)}"
