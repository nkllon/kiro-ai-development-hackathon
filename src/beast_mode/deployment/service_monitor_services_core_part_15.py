
def export_metrics(self, output_file: str):
    """Export service metrics to file"""
    metrics_data = {'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'), 'services': {}}
    for service_name, service in self.services.items():
        metrics_data['services'][service_name] = {'status': service.status.value, 'metrics': {'cpu_percent': service.metrics.cpu_percent, 'memory_percent': service.metrics.memory_percent, 'memory_mb': service.metrics.memory_mb, 'uptime_seconds': service.metrics.uptime_seconds, 'restart_count': service.metrics.restart_count, 'open_files': service.metrics.open_files, 'connections': service.metrics.connections}}
    with open(output_file, 'w') as f:
        json.dump(metrics_data, f, indent=2)
    self.logger.info(f'Metrics exported to {output_file}')
