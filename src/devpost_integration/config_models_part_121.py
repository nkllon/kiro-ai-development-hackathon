
def export_configuration(self) -> Dict[str, Any]:
    """Export configuration for backup."""
    try:
        export_data = {'config_data': self.config_data.copy(), 'export_time': datetime.now().isoformat(), 'version': self.version}
        self._operation_count += 1
        return export_data
    except Exception as e:
        logger.error(f'Failed to export configuration: {e}')
        self._errors += 1
        return {}
