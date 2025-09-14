
def _parallel_health_checks(self, domains: Dict[str, Domain]) -> HealthStatusCollection:
    """Perform health checks in parallel"""
    health_statuses = {}
    with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
        future_to_domain = {executor.submit(self._perform_health_check, domain): domain_name for domain_name, domain in domains.items()}
        for future in as_completed(future_to_domain, timeout=self.check_timeout * len(domains)):
            domain_name = future_to_domain[future]
            try:
                health_status = future.result()
                health_statuses[domain_name] = health_status
            except Exception as e:
                self.failed_checks += 1
                self.logger.error(f'Parallel health check failed for {domain_name}: {e}')
                health_statuses[domain_name] = self._create_failed_health_status(str(e))
    return health_statuses
