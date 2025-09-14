from src.rm_ddd.core.registry import register_module

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
    