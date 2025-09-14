
def _update_average_metric(self, metric_name: str, new_value: float) -> None:
    """Update running average for performance metric."""
    current_avg = self.performance_metrics[metric_name]
    count = self.performance_metrics.get(f'{metric_name}_count', 0)
    new_avg = (current_avg * count + new_value) / (count + 1)
    self.performance_metrics[metric_name] = new_avg
    self.performance_metrics[f'{metric_name}_count'] = count + 1
