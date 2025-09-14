from datetime import datetime
from typing import Dict, List, Any
from src.rm_ddd.core.health import ModuleHealth


def calculate_roi(self, project_duration_months: int=12) -> ROICalculation:
    """Calculate ROI for systematic vs ad-hoc approach."""
    logger.info('Calculating ROI for systematic approach')
    try:
        systematic_investment = self._calculate_systematic_investment(project_duration_months)
        adhoc_investment = self._calculate_adhoc_investment(project_duration_months)
        systematic_benefits = self._calculate_systematic_benefits(project_duration_months)
        adhoc_benefits = self._calculate_adhoc_benefits(project_duration_months)
        net_benefit = systematic_benefits - systematic_investment
        roi_percentage = net_benefit / systematic_investment * 100 if systematic_investment > 0 else 0
        monthly_benefit = net_benefit / project_duration_months
        payback_period = systematic_investment / monthly_benefit if monthly_benefit > 0 else float('inf')
        risk_adjusted_roi = roi_percentage * 0.8
        roi_calculation = ROICalculation(investment_cost=systematic_investment, systematic_benefits=systematic_benefits, adhoc_benefits=adhoc_benefits, net_benefit=net_benefit, roi_percentage=roi_percentage, payback_period_months=payback_period, risk_adjusted_roi=risk_adjusted_roi)
        logger.info(f'ROI calculated: {roi_percentage:.1f}% over {project_duration_months} months')
        return roi_calculation
    except Exception as e:
        logger.error(f'Failed to calculate ROI: {e}')
        return ROICalculation(0, 0, 0, 0, 0, 0, 0)
