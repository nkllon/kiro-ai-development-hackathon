
    def _extract_domain_terms_from_path(self, file_path: str) -> List[str]:
        """Extract domain terms from file path"""
        import re
from src.rm_ddd.core.health import ModuleHealth

        path_parts = Path(file_path).parts
        domain_terms = []
        
        for part in path_parts:
            # Split camelCase and snake_case
            words = re.findall(r'[A-Z][a-z]*|[a-z]+', part)
            domain_terms.extend([word.lower() for word in words])
        
        return list(set(domain_terms))  # Remove duplicates

# Global registry instance
registry = InterfaceRegistry()

