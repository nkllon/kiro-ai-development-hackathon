from datetime import datetime
from typing import Dict, List, Any
from src.rm_ddd.core.health import ModuleHealth


def generate_evidence_package(self, package_title: str='Systematic Development Superiority') -> EvidencePackage:
    """Generate comprehensive evidence package for marketing/sales."""
    logger.info(f'Generating evidence package: {package_title}')
    try:
        if not self.metrics:
            self.generate_superiority_metrics()
        roi_calculation = self.calculate_roi()
        competitive_advantages = self._generate_competitive_advantages()
        customer_testimonials = self._generate_customer_testimonials()
        case_studies = self._generate_case_studies()
        package_id = f'evidence_{int(datetime.now().timestamp())}'
        evidence_package = EvidencePackage(package_id=package_id, title=package_title, metrics=self.metrics, roi_calculation=roi_calculation, competitive_advantages=competitive_advantages, customer_testimonials=customer_testimonials, case_studies=case_studies)
        self.evidence_packages.append(evidence_package)
        logger.info(f'Evidence package generated: {package_id}')
        return evidence_package
    except Exception as e:
        logger.error(f'Failed to generate evidence package: {e}')
        return None
