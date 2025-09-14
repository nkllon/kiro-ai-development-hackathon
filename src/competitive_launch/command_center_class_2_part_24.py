from src.rm_ddd.core.registry import register_module
from src.rm_ddd.core.health import ModuleHealth


def _generate_competitive_advantage_evidence(self) -> Dict[str, Any]:
    """Generate evidence of competitive advantage."""
    logger.info('Generating competitive advantage evidence')
    try:
        superiority_metrics = self.competitive_intelligence.calculate_competitive_advantage()
        evidence_packages = self._create_evidence_packages(superiority_metrics)
        advantage_score = superiority_metrics.get('overall_advantage', 0.0)
        logger.info(f'Competitive advantage evidence generated: {advantage_score:.2%} advantage')
        return {'advantage_score': advantage_score, 'evidence_packages': evidence_packages, 'superiority_metrics': superiority_metrics}
    except Exception as e:
        logger.error(f'Competitive advantage evidence generation failed: {e}')
        return {'advantage_score': 0.0, 'evidence_packages': [], 'superiority_metrics': {}}
