from src.rm_ddd.core.health import ModuleHealth

def check_dependency_consistency(domains: DomainCollection, context: Dict[str, Any]) -> List[HealthIssue]:
    return self.validate_dependencies(domains)
