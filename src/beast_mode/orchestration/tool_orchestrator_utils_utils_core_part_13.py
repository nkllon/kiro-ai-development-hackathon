
def _calculate_overall_systematic_compliance(self) -> Dict[str, Any]:
    """Calculate overall systematic compliance metrics"""
    if not self.tool_metrics:
        return {'compliance_rate': 1.0, 'message': 'No metrics available'}
    total_compliance = sum((metrics.systematic_compliance_rate for metrics in self.tool_metrics.values()))
    average_compliance = total_compliance / len(self.tool_metrics)
    return {'overall_compliance_rate': average_compliance, 'compliant_tools': len(self.tool_metrics), 'total_tools': len(self.tool_metrics)}
