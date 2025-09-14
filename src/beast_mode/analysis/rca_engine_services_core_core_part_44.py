from src.rm_ddd.core.health import ModuleHealth

def _analyze_resource_availability(self, failure: Failure) -> Dict[str, Any]:
    """Analyze resource availability"""
    resource_analysis = {}
    if 'MemoryError' in failure.error_message or 'resource' in failure.error_message.lower():
        resource_analysis['has_resource_issue'] = True
        resource_analysis['resource_details'] = failure.error_message
    else:
        resource_analysis['has_resource_issue'] = False
    return resource_analysis
