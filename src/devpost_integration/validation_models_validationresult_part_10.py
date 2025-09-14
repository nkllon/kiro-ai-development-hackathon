
    def check_health(self) -> ModuleHealth:
        """Check module health."""
        issues = []
        health_score = self._calculate_health_score()
        
        if self._errors > 0:
            issues.append(f"{self._errors} internal errors occurred")
        
        if len(self.errors) > 10:
            issues.append(f"High error count: {len(self.errors)}")
        
        if not self.validation_data:
            issues.append("No validation data available")
        
        status = ModuleStatus.HEALTHY if health_score >= 0.9 else ModuleStatus.WARNING
        
        return ModuleHealth(
            module_id=self.module_id,
            status=status,
            health_score=health_score,
            issues=issues,
            capabilities=self.get_capabilities(),
            dependencies=self.get_dependencies(),
            metrics=self.get_metrics(),
            last_check=datetime.now()
        )
    