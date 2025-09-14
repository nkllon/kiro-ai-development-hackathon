from src.rm_ddd.core.health import ModuleHealth

    def _calculate_diagnosis_confidence(self, issues: List[str], root_causes: List[str]) -> float:
        """Calculate confidence in diagnosis accuracy"""
        if not issues:
            return 1.0
        confidence = 0.8 if root_causes else 0.5
        return confidence
