from src.rm_ddd.core.health import ModuleHealth

    def format_response(self, result: ActionResult) -> str:
        """Format result as human-readable text."""
        return result.to_response_string()
