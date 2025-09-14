
    def check_health(self) -> ModuleHealth:
        """Check module health with comprehensive monitoring"""
        try:
            if not hasattr(self, '_start_time'):
                return ModuleHealth.UNHEALTHY
            uptime = (datetime.now() - self._start_time).total_seconds()
            if uptime < 0:
                return ModuleHealth.UNHEALTHY
            error_count = getattr(self, '_error_count', 0)
            total_operations = getattr(self, '_command_count', 1)
            error_rate = error_count / total_operations if total_operations > 0 else 0
            if error_rate > 0.5:
                return ModuleHealth.UNHEALTHY
            elif error_rate > 0.1:
                return ModuleHealth.DEGRADED
            else:
                return ModuleHealth.HEALTHY
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return ModuleHealth.UNHEALTHY
        """Perform comprehensive health check."""
        issues = []
        health_score = 1.0
        
        try:
            # Check format registry
            if not hasattr(self, 'format_registry'):
                issues.append("Missing format registry")
                health_score -= 0.3
            
            # Check metadata extractor
            if not hasattr(self, 'metadata_extractor'):
                issues.append("Missing metadata extractor")
                health_score -= 0.3
            
            # Check error rate
            if self._files_processed > 0:
                error_rate = self._errors / self._files_processed
                if error_rate > 0.1:  # More than 10% error rate
                    issues.append(f"High error rate: {error_rate:.1%}")
                    health_score -= 0.2
            
            # Determine status
            if health_score >= 0.9:
                status = ModuleStatus.HEALTHY
            elif health_score >= 0.7:
                status = ModuleStatus.DEGRADED
            else:
                status = ModuleStatus.UNHEALTHY
            
            return ModuleHealth(
                module_id=self.module_id,
                status=status,
                last_check=datetime.now(),
                health_score=max(0.0, health_score),
                issues=issues,
                capabilities=self.get_capabilities(),
                dependencies=self.get_dependencies(),
                metrics=self.get_metrics()
            )
            
        except Exception as e:
            return ModuleHealth(
                module_id=self.module_id,
                status=ModuleStatus.UNHEALTHY,
                last_check=datetime.now(),
                health_score=0.0,
                issues=[f"Health check exception: {e}"],
                capabilities=self.get_capabilities(),
                dependencies=self.get_dependencies(),
                metrics={}
            )
    