from src.rm_ddd.core.health import ModuleHealth

    def refresh_all_dashboards(self) -> Dict[str, Any]:
        """
        Refresh all active dashboards
        """
        start_time = time.time()
        results = {}
        try:
            self.logger.info(f'Starting dashboard refresh for {len(self.dashboards)} dashboards')
            for dashboard_id, config in self.dashboards.items():
                if not config.enabled:
                    continue
                try:
                    self.logger.info(f'Refreshing dashboard: {dashboard_id} ({config.dashboard_type.value})')
                    if config.dashboard_type == DashboardType.HEALTH_MONITORING:
                        results[dashboard_id] = self.generate_health_monitoring_dashboard()
                    elif config.dashboard_type == DashboardType.SUPERIORITY_METRICS:
                        results[dashboard_id] = self.generate_superiority_metrics_dashboard()
                    elif config.dashboard_type == DashboardType.PERFORMANCE_ANALYTICS:
                        results[dashboard_id] = self.generate_performance_analytics_dashboard()
                    elif config.dashboard_type == DashboardType.UNKNOWN_RISKS:
                        results[dashboard_id] = self.generate_unknown_risks_dashboard()
                    else:
                        results[dashboard_id] = {'error': f'Unknown dashboard type: {config.dashboard_type}'}
                except Exception as e:
                    self.logger.error(f'Dashboard {dashboard_id} refresh failed: {str(e)}')
                    results[dashboard_id] = {'error': f'Dashboard refresh failed: {str(e)}'}
            refresh_time = int((time.time() - start_time) * 1000)
            self._update_refresh_metrics(refresh_time)
            successful_refreshes = len([r for r in results.values() if 'error' not in r])
            self.logger.info(f'Dashboard refresh completed: {successful_refreshes}/{len(results)} successful, {refresh_time}ms')
            return {'success': True, 'dashboards_refreshed': successful_refreshes, 'total_dashboards': len(results), 'refresh_time_ms': refresh_time, 'results': results}
        except Exception as e:
            self.logger.error(f'Dashboard refresh failed: {str(e)}')
            return {'error': f'Dashboard refresh failed: {str(e)}'}
