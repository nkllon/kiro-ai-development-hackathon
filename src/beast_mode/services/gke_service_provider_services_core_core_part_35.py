
def _identify_compliance_requirements(self, gcp_constraints: List[str]) -> List[str]:
    """Identify compliance requirements from constraints"""
    compliance_map = {'gdpr': 'GDPR compliance required', 'hipaa': 'HIPAA compliance required', 'sox': 'SOX compliance required', 'pci': 'PCI DSS compliance required'}
    return [compliance_map[constraint] for constraint in gcp_constraints if constraint in compliance_map]
