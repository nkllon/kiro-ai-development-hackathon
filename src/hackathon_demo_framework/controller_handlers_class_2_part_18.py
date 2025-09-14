from src.rm_ddd.core.registry import register_module
from src.rm_ddd.core.health import ModuleHealth


    def _optimize_demo_package(self, demo_package: DemoPackage) -> DemoPackage:
        """Optimize demo package based on metrics and analysis."""
        if demo_package.presentation_metrics:
            if demo_package.demo_script.total_duration > self.config.demo_time_limit * 60:
                demo_package.demo_script.timing_breakdown['business_impact'] = min(demo_package.demo_script.timing_breakdown['business_impact'], 45)
                demo_package.demo_script.total_duration = sum(demo_package.demo_script.timing_breakdown.values())
            if demo_package.demo_environment.reliability_score < 95.0:
                demo_package.backup_plans.extend(['Pre-recorded demo video', 'Static screenshot walkthrough', 'Architecture diagram presentation'])
        return demo_package
