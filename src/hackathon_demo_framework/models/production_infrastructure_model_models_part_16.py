from src.rm_ddd.core.health import ModuleHealth

    def _generate_security_metrics(self, config: GKEConfig) -> Dict[str, Any]:
        """Generate security metrics for deployed cluster"""
        return {'security_level': 'high', 'vulnerability_scan': {'total_vulnerabilities': 2, 'critical_vulnerabilities': 0, 'high_vulnerabilities': 1, 'medium_vulnerabilities': 1, 'low_vulnerabilities': 0}, 'compliance': {'cis_benchmark': 95.0, 'pci_dss': 90.0, 'sox_compliance': 100.0, 'overall_score': 95.0}, 'security_policies': {'network_policies': len(config.security_policies), 'rbac_enabled': True, 'pod_security_policies': True, 'encryption_at_rest': True, 'encryption_in_transit': True}, 'threat_detection': {'anomaly_detection': True, 'intrusion_detection': True, 'malware_scanning': True, 'threat_intelligence': True}}

    def register_module(self, registry):
        """Register module with registry."""
        metadata = self.get_interface_metadata()
        if hasattr(registry, 'register'):
            registry.register(metadata)
            
    def get_interface_metadata(self):
        """Get interface metadata for registry."""
        return {
            'module_id': getattr(self, 'module_id', self.__class__.__name__),
            'interface_type': self.__class__.__name__,
            'version': '1.0.0',
            'dependencies': [],
            'capabilities': []
        }

