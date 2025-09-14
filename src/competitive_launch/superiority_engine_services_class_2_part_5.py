from src.rm_ddd.core.registry import register_module

    def generate_superiority_metrics(self) -> List[SuperiorityMetric]:
        """Generate comprehensive superiority metrics."""
        logger.info('Generating systematic superiority metrics')
        try:
            self.metrics.clear()
            metric_types = [MetricType.DEVELOPMENT_VELOCITY, MetricType.QUALITY_IMPROVEMENT, MetricType.TECHNICAL_DEBT_REDUCTION, MetricType.COST_EFFICIENCY, MetricType.RISK_MITIGATION, MetricType.CUSTOMER_SATISFACTION, MetricType.TIME_TO_MARKET, MetricType.MAINTENANCE_EFFICIENCY]
            for metric_type in metric_types:
                metric = self._calculate_metric(metric_type)
                if metric:
                    self.metrics.append(metric)
            logger.info(f'Generated {len(self.metrics)} superiority metrics')
            return self.metrics
        except Exception as e:
            logger.error(f'Failed to generate superiority metrics: {e}')
            return []
