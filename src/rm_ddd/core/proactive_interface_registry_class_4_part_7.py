from src.rm_ddd.core.registry import register_module
from src.rm_ddd.core.health import ModuleHealth


class SetupdefaultrulesClass:
    """Auto-generated class for functions."""

    def setup_default_rules(self):
    """Setup default duplicate prevention rules"""
    self.duplicate_rules = [
    DuplicatePreventionRule(
    rule_name="name_similarity",
    pattern=".*_service$",
    severity="high",
    action="warn",
    description="Prevent creation of similar service interfaces"
    ),
    DuplicatePreventionRule(
    rule_name="type_conflict",
    pattern=".*_module$",
    severity="medium",
    action="suggest",
    description="Suggest alternatives for module interfaces"
    ),
    DuplicatePreventionRule(
    rule_name="domain_overlap",
    pattern=".*_api$",
    severity="low",
    action="info",
    description="Inform about domain overlap in API interfaces"
    )
    ]

    def register_module(self, registry):
    """Register module with registry."""
    metadata = self.get_interface_metadata()
    if hasattr(registry, 'register'):
    registry.register(metadata)

    def get_interface_metadata(self):
    """Get interface metadata for registry."""
    return {
    'module_id': getattr(self, 'module_id', self.__class__.__name__),
    'interface_type': self.__class__.__name__,
    'version': '1.0.0',
    'dependencies': [],
    'capabilities': []
    }

