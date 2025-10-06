"""
Certificate Orchestrator - Central coordination engine for MSP SSL Chaos Tamer

This is the main coordination engine that manages all certificate operations,
CA plugin lifecycle, and MSP-specific workflows with systematic observability.
"""

import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta

from .interfaces import (
    CAPlugin, ReflectiveModule, CertificateRequest, CertificateStatus,
    MSPSSLError, EmergencyProvisioningError
)
from .models import Certificate, Client, MSP


class CertificateOrchestrator(ReflectiveModule):
    """
    Central coordination engine for MSP SSL certificate management
    
    Coordinates discovery, renewal, emergency operations, and integrates
    with MSP-specific workflows while providing systematic observability.
    """
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__()
        self.config = config
        self.logger = logging.getLogger("msp_ssl.orchestrator")
        
        # Plugin registry
        self.ca_plugins: Dict[str, CAPlugin] = {}
        self.active_plugins: Dict[str, bool] = {}
        
        # Component references (will be injected)
        self.discovery_engine = None
        self.renewal_scheduler = None
        self.renewal_executor = None
        self.emergency_detector = None
        self.emergency_provisioner = None
        self.credential_store = None
        self.certificate_db = None
        
        # MSP configuration
        self.msp_config = config.get("msp", {})
        self.default_ca = config.get("default_ca", "letsencrypt")
        
        self.logger.info("Certificate Orchestrator initialized")
    
    def register_ca_plugin(self, plugin_name: str, plugin: CAPlugin) -> bool:
        """
        Register a Certificate Authority plugin
        
        Args:
            plugin_name: Name of the CA plugin
            plugin: CAPlugin instance
            
        Returns:
            bool: True if registration successful
        """
        try:
            self.ca_plugins[plugin_name] = plugin
            self.active_plugins[plugin_name] = True
            self.logger.info(f"Registered CA plugin: {plugin_name}")
            return True
        except Exception as e:
            self.logger.error(f"Failed to register CA plugin {plugin_name}: {e}")
            return False
    
    def get_available_cas(self) -> List[str]:
        """Get list of available Certificate Authorities"""
        return [name for name, active in self.active_plugins.items() if active]
    
    def discover_certificates(self, domain_list: List[str]) -> Dict[str, Any]:
        """
        Discover certificates across client domains
        
        Args:
            domain_list: List of domains to scan
            
        Returns:
            Dict containing discovery results and certificate inventory
        """
        if not self.discovery_engine:
            raise MSPSSLError("Discovery engine not initialized")
        
        self.logger.info(f"Starting certificate discovery for {len(domain_list)} domains")
        
        try:
            # Use discovery engine to scan domains
            discovered_certs = self.discovery_engine.discover_certificates(domain_list)
            
            # Update certificate inventory
            inventory_results = {
                "discovered_count": len(discovered_certs),
                "domains_scanned": len(domain_list),
                "certificates": discovered_certs,
                "scan_timestamp": datetime.utcnow().isoformat()
            }
            
            self.logger.info(f"Discovery complete: {len(discovered_certs)} certificates found")
            return inventory_results
            
        except Exception as e:
            self.logger.error(f"Certificate discovery failed: {e}")
            raise MSPSSLError(f"Discovery failed: {e}")
    
    def schedule_renewal(self, cert_id: str, renewal_policy: Dict[str, Any]) -> bool:
        """
        Schedule certificate renewal with MSP-specific policies
        
        Args:
            cert_id: Certificate ID to schedule for renewal
            renewal_policy: Renewal policy configuration
            
        Returns:
            bool: True if scheduling successful
        """
        if not self.renewal_scheduler:
            raise MSPSSLError("Renewal scheduler not initialized")
        
        try:
            # Get certificate details
            cert_info = self.certificate_db.get_certificate(cert_id)
            if not cert_info:
                raise MSPSSLError(f"Certificate {cert_id} not found")
            
            # Calculate renewal timing based on CA-specific delays
            ca_name = cert_info.get("ca_provider")
            ca_delays = self.config.get("ca_delays", {}).get(ca_name, {"processing_days": 1})
            
            # Schedule with buffer for CA processing time
            days_before_expiry = renewal_policy.get("days_before_expiry", 30)
            buffer_days = ca_delays.get("processing_days", 1)
            effective_days = days_before_expiry + buffer_days
            
            success = self.renewal_scheduler.schedule_renewal(cert_id, effective_days)
            
            if success:
                self.logger.info(f"Scheduled renewal for certificate {cert_id}")
            else:
                self.logger.error(f"Failed to schedule renewal for certificate {cert_id}")
            
            return success
            
        except Exception as e:
            self.logger.error(f"Renewal scheduling failed for {cert_id}: {e}")
            return False
    
    def emergency_provision(self, domain: str, emergency_type: str) -> Dict[str, Any]:
        """
        Emergency certificate provisioning - "Oh shit" button functionality
        
        Args:
            domain: Domain needing emergency certificate
            emergency_type: Type of emergency (expired, compromised, etc.)
            
        Returns:
            Dict containing emergency certificate details
        """
        if not self.emergency_provisioner:
            raise EmergencyProvisioningError("Emergency provisioner not initialized")
        
        self.logger.warning(f"EMERGENCY: {emergency_type} for domain {domain}")
        
        try:
            # Use fastest available CA (typically Let's Encrypt)
            emergency_ca = self.config.get("emergency_ca", "letsencrypt")
            
            if emergency_ca not in self.active_plugins:
                # Fallback to any available CA
                available_cas = self.get_available_cas()
                if not available_cas:
                    raise EmergencyProvisioningError("No CA plugins available for emergency provisioning")
                emergency_ca = available_cas[0]
            
            # Create emergency certificate request
            emergency_request = CertificateRequest(
                domain=domain,
                client_id="emergency",  # Will be updated with actual client ID
                ca_provider=emergency_ca,
                emergency=True,
                validity_days=90  # Standard emergency certificate validity
            )
            
            # Execute emergency provisioning
            cert_id = self.emergency_provisioner.emergency_provision(domain, emergency_request)
            
            # Track emergency certificate
            emergency_result = {
                "certificate_id": cert_id,
                "domain": domain,
                "ca_provider": emergency_ca,
                "emergency_type": emergency_type,
                "provisioned_at": datetime.utcnow().isoformat(),
                "status": "emergency_active"
            }
            
            self.logger.info(f"Emergency certificate provisioned: {cert_id} for {domain}")
            return emergency_result
            
        except Exception as e:
            self.logger.error(f"Emergency provisioning failed for {domain}: {e}")
            raise EmergencyProvisioningError(f"Emergency provisioning failed: {e}")
    
    def get_client_status(self, client_id: str) -> Dict[str, Any]:
        """
        Get comprehensive certificate status for an MSP client
        
        Args:
            client_id: Client identifier
            
        Returns:
            Dict containing client certificate status and health metrics
        """
        try:
            # Get client certificates from database
            client_certs = self.certificate_db.get_client_certificates(client_id)
            
            # Calculate health metrics
            total_certs = len(client_certs)
            expired_certs = len([c for c in client_certs if c.get("status") == "expired"])
            expiring_soon = len([c for c in client_certs 
                               if self._is_expiring_soon(c.get("expiration_date"))])
            healthy_certs = total_certs - expired_certs - expiring_soon
            
            # Check for emergencies
            emergency_certs = len([c for c in client_certs if c.get("emergency", False)])
            
            client_status = {
                "client_id": client_id,
                "total_certificates": total_certs,
                "healthy_certificates": healthy_certs,
                "expiring_soon": expiring_soon,
                "expired_certificates": expired_certs,
                "emergency_certificates": emergency_certs,
                "health_score": self._calculate_health_score(total_certs, healthy_certs, expired_certs),
                "last_updated": datetime.utcnow().isoformat(),
                "certificates": client_certs
            }
            
            return client_status
            
        except Exception as e:
            self.logger.error(f"Failed to get client status for {client_id}: {e}")
            raise MSPSSLError(f"Client status retrieval failed: {e}")
    
    def _is_expiring_soon(self, expiration_date: str, days_threshold: int = 30) -> bool:
        """Check if certificate is expiring soon"""
        if not expiration_date:
            return False
        
        try:
            exp_date = datetime.fromisoformat(expiration_date.replace('Z', '+00:00'))
            threshold_date = datetime.utcnow() + timedelta(days=days_threshold)
            return exp_date <= threshold_date
        except Exception:
            return False
    
    def _calculate_health_score(self, total: int, healthy: int, expired: int) -> float:
        """Calculate certificate health score (0-100)"""
        if total == 0:
            return 100.0
        
        # Heavily penalize expired certificates
        expired_penalty = expired * 2
        score = max(0, (healthy - expired_penalty) / total * 100)
        return round(score, 1)
    
    def get_system_health(self) -> Dict[str, Any]:
        """Get overall system health status"""
        return {
            "orchestrator_status": "healthy",
            "active_ca_plugins": len(self.get_available_cas()),
            "total_ca_plugins": len(self.ca_plugins),
            "components_initialized": {
                "discovery_engine": self.discovery_engine is not None,
                "renewal_scheduler": self.renewal_scheduler is not None,
                "renewal_executor": self.renewal_executor is not None,
                "emergency_detector": self.emergency_detector is not None,
                "emergency_provisioner": self.emergency_provisioner is not None,
                "credential_store": self.credential_store is not None,
                "certificate_db": self.certificate_db is not None
            },
            "timestamp": datetime.utcnow().isoformat()
        }
    
    def get_module_info(self) -> Dict[str, Any]:
        """Get orchestrator module information"""
        return {
            "module_name": "certificate_orchestrator",
            "module_type": "orchestrator",
            "version": "1.0.0",
            "description": "Central coordination engine for MSP SSL certificate management"
        }
    
    def get_capabilities(self) -> List[Any]:
        """Get orchestrator capabilities"""
        return [
            {"name": "certificate_discovery", "enabled": True},
            {"name": "renewal_scheduling", "enabled": True},
            {"name": "emergency_provisioning", "enabled": True},
            {"name": "ca_plugin_management", "enabled": True},
            {"name": "client_status_reporting", "enabled": True}
        ]
    
    def get_health_status(self) -> Dict[str, Any]:
        """Get orchestrator health status"""
        components_health = self.get_system_health()
        return {
            "status": "healthy" if components_health["orchestrator_status"] == "healthy" else "degraded",
            "active_ca_plugins": components_health["active_ca_plugins"],
            "components_initialized": components_health["components_initialized"],
            "last_check": datetime.utcnow().isoformat()
        }
    
    def graceful_degradation(self) -> Dict[str, Any]:
        """Perform graceful degradation for orchestrator"""
        # Check if any critical components are failing
        health = self.get_system_health()
        components = health["components_initialized"]
        
        degradation_applied = False
        fallback_mode = None
        
        # If emergency components are down, enable basic mode
        if not components.get("emergency_detector") or not components.get("emergency_provisioner"):
            degradation_applied = True
            fallback_mode = "basic_certificate_management"
        
        return {
            "degradation_applied": degradation_applied,
            "fallback_mode": fallback_mode,
            "message": "Orchestrator operating in fallback mode" if degradation_applied else "Orchestrator operating normally"
        }