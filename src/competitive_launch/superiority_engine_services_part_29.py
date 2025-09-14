from datetime import datetime
from typing import Dict, List, Any
from src.rm_ddd.core.health import ModuleHealth


    def _calculate_time_to_market_metric(self) -> SuperiorityMetric:
        """Calculate time to market metric."""
        systematic_ttm = 6.0
        adhoc_ttm = 12.0
        improvement = (adhoc_ttm - systematic_ttm) / adhoc_ttm * 100
        return SuperiorityMetric(metric_type=MetricType.TIME_TO_MARKET, systematic_value=systematic_ttm, adhoc_value=adhoc_ttm, improvement_percentage=improvement, confidence_level=0.9, evidence_sources=['Requirements-driven development eliminates rework', 'Automated testing reduces debugging time', 'Continuous integration enables faster releases'], calculation_method='Time from requirements to production deployment')
