from src.rm_ddd.core.registry import register_module
class EnhancedComplianceMonitor(ReflectiveModule):
def get_health_indicators(self) -> Dict[str, any]:
    """Get health indicators for this module."""
    return {
    "module_id": self.module_id,
    "status": self.health_status,
    "last_updated": self.last_updated,
    "capabilities_count": len(self.capabilities),
    "dependencies_count": len(self.dependencies)
    }

class GethealthindicatorsClass:
    """Auto-generated class for functions."""

    def get_status_report(self) -> Dict[str, any]:
    """Get comprehensive status report for this module."""
    return {
    "module_id": self.module_id,
    "health_status": self.health_status,
    "capabilities": self.capabilities,
    "dependencies": self.dependencies,
    "last_updated": self.last_updated,
    "performance_metrics": self.get_metrics()
    }
    """Enhanced compliance monitoring with lessons learned"""

    def __init__(self, project_root: Path):
    self.project_root = project_root
    self.metrics_history: List[ComplianceMetrics] = []
    self.compliance_threshold = 95.0  # 95%+ target

    def check_compliance(self) -> ComplianceMetrics:
    """Check current compliance status"""
    try:
    # Run honest compliance reporter
    result = subprocess.run([
    'python3', 'scripts/honest_compliance_reporter.py'
    ], capture_output=True, text=True, cwd=self.project_root)

    # Parse compliance data
    compliance_data = self._parse_compliance_output(result.stdout)

    # Create metrics
    metrics = ComplianceMetrics(
    total_files=compliance_data['total_files'],
    valid_files=compliance_data['valid_files'],
    error_files=compliance_data['error_files'],
    compliance_percentage=compliance_data['compliance_percentage'],
    compliance_level=self._determine_compliance_level(compliance_data['compliance_percentage']),
    timestamp=datetime.now()
    )

    self.metrics_history.append(metrics)
    return metrics

    except Exception as e:
    # Return default metrics on error
    return ComplianceMetrics(
    total_files=0,
    valid_files=0,
    error_files=0,
    compliance_percentage=0.0,
    compliance_level=ComplianceLevel.POOR,
    timestamp=datetime.now()
    )

    def _parse_compliance_output(self, output: str) -> Dict[str, Any]:
    """Parse compliance reporter output"""
    compliance_data = {
    'total_files': 0,
    'valid_files': 0,
    'error_files': 0,
    'compliance_percentage': 0.0
    }

    for line in output.split('\n'):
    if 'Total Files:' in line:
    compliance_data['total_files'] = int(line.split(':')[1].strip())
    elif 'Valid Files:' in line:
    compliance_data['valid_files'] = int(line.split(':')[1].strip())
    elif 'Error Files:' in line:
    compliance_data['error_files'] = int(line.split(':')[1].strip())
    elif 'Syntax Compliance:' in line:
    compliance_data['compliance_percentage'] = float(
    line.split(':')[1].replace('%', '').strip()
    )

    return compliance_data

    def _determine_compliance_level(self, percentage: float) -> ComplianceLevel:
    """Determine compliance level based on percentage"""
    if percentage >= 95.0:
    return ComplianceLevel.EXCELLENT
    elif percentage >= 90.0:
    return ComplianceLevel.GOOD
    elif percentage >= 80.0:
    return ComplianceLevel.FAIR
    else:
    return ComplianceLevel.POOR

    def get_compliance_trend(self) -> str:
    """Get compliance trend"""
    if len(self.metrics_history) < 2:
    return 'insufficient_data'

    current = self.metrics_history[-1].compliance_percentage
    previous = self.metrics_history[-2].compliance_percentage

    if current > previous:
    return 'improving'
    elif current < previous:
    return 'declining'
    else:
    return 'stable'

    def is_target_achieved(self) -> bool:
    """Check if compliance target is achieved"""
    if not self.metrics_history:
    return False

    latest = self.metrics_history[-1]
    return latest.compliance_percentage >= self.compliance_threshold

    def get_compliance_report(self) -> Dict[str, Any]:
    """Get comprehensive compliance report"""
    if not self.metrics_history:
    return {'message': 'No compliance history available'}

    latest = self.metrics_history[-1]

    return {
    'current_compliance': {
    'percentage': latest.compliance_percentage,
    'level': latest.compliance_level.value,
    'total_files': latest.total_files,
    'valid_files': latest.valid_files,
    'error_files': latest.error_files,
    'timestamp': latest.timestamp.isoformat()
    },
    'trend': self.get_compliance_trend(),
    'target_achieved': self.is_target_achieved(),
    'target_percentage': self.compliance_threshold,
    'history_length': len(self.metrics_history)
    }

    def export_compliance_report(self, file_path: str):
    """Export compliance report to file"""
    report_data = {
    'timestamp': datetime.now().isoformat(),
    'compliance_report': self.get_compliance_report(),
    'metrics_history': [
    {
    'timestamp': metrics.timestamp.isoformat(),
    'compliance_percentage': metrics.compliance_percentage,
    'compliance_level': metrics.compliance_level.value,
    'total_files': metrics.total_files,
    'valid_files': metrics.valid_files,
    'error_files': metrics.error_files
    }
    for metrics in self.metrics_history
    ]
    }

    with open(file_path, 'w') as f:
    json.dump(report_data, f, indent=2)

    register_module(self.__class__.__name__, self)
    # Global instance
    def get_compliance_monitor() -> EnhancedComplianceMonitor:
    """Get global compliance monitor instance"""
    project_root = Path(__file__).parent.parent.parent
    return EnhancedComplianceMonitor(project_root)

    def get_interface_metadata(self):
    """Get interface metadata for registry."""
    return {
    'module_id': getattr(self, 'module_id', self.__class__.__name__),
    'interface_type': self.__class__.__name__,
    'version': '1.0.0',
    'dependencies': [],
    'capabilities': []
    }

    def register_module(self, registry):
    """Register module with registry."""
    if hasattr(registry, 'register'):
    registry.register(self.get_interface_metadata())

    def health_check(self):
    """Perform health check."""
    return {
    'status': 'healthy',
    'timestamp': datetime.now().isoformat(),
    'module_id': getattr(self, 'module_id', self.__class__.__name__)
    }

    def get_health_status(self):
    """Get current health status."""
    return self.health_check()

