from src.rm_ddd.core.health import ModuleHealth

    def _generic_systematic_repair(self, diagnosis: MakefileDiagnosisResult) -> str:
        """Generic systematic repair for unknown issues"""
        return f'Systematic analysis and repair of: {diagnosis.root_cause}'
