
    def get_metrics(self) -> Dict[str, Any]:
        """Get module metrics."""
        uptime = (datetime.now() - self._start_time).total_seconds()
        stats = self.get_media_statistics()
        
        return {
            'uptime_seconds': uptime,
            'uptime_hours': uptime / 3600,
            'files_processed': stats['files_processed'],
            'files_detected': stats['files_detected'],
            'detection_rate': stats['detection_rate'],
            'errors': stats['errors'],
            'error_rate': stats['error_rate'],
            'supported_formats': stats['supported_formats'],
            'last_check': datetime.now().isoformat()
        }
    