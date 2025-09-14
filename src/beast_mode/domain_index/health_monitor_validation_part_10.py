
def schedule_health_check(self, domain_name: str, interval_minutes: int) -> bool:
    """Schedule periodic health checks"""
    try:
        next_check = datetime.now() + timedelta(minutes=interval_minutes)
        self._scheduled_checks[domain_name] = {'interval_minutes': interval_minutes, 'next_check': next_check}
        self.logger.info(f'Scheduled health check for {domain_name} every {interval_minutes} minutes')
        return True
    except Exception as e:
        self._handle_error(e, 'schedule_health_check')
        return False
