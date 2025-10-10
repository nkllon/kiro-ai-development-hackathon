"""
Domain Certificate Scanner for MSP SSL Chaos Tamer
Implements certificate discovery using DNS and HTTPS probing with
certificate chain validation and parsing capabilities.
"""

import asyncio
import ssl
import socket
import dns.resolver
import dns.exception
import logging
import time
from typing import Dict, List, Optional, Set, Tuple, Any
from datetime import datetime, timedelta
from urllib.parse import urlparse
from dataclasses import dataclass, field
import concurrent.futures
from contextlib import asynccontextmanager

import aiohttp
import aiodns
from cryptography import x509
from cryptography.hazmat.primitives import hashes
from cryptography.x509.oid import NameOID, ExtensionOID

from ..core.interfaces import ReflectiveModule
from ..core.models import Certificate, CertificateStatus
from ..storage.database import CertificateDatabase


@dataclass
class ScanTarget:
    """Represents a domain/service to scan for certificates"""
    domain: str
    port: int = 443
    protocol: str = "https"
    client_id: Optional[str] = None
    scan_subdomains: bool = False
    custom_headers: Dict[str, str] = field(default_factory=dict)
    timeout: int = 30
    
    def __post_init__(self):
        # Normalize domain
        self.domain = self.domain.lower().strip()
        if self.domain.startswith(('http://', 'https://')):
            parsed = urlparse(self.domain)
            self.domain = parsed.hostname or parsed.netloc
            if parsed.port:
                self.port = parsed.port


@dataclass
class CertificateInfo:
    """Detailed certificate information from scanning"""
    domain: str
    certificate: x509.Certificate
    certificate_chain: List[x509.Certificate]
    port: int
    protocol: str
    discovered_at: datetime
    validation_errors: List[str] = field(default_factory=list)
    trust_chain_valid: bool = False
    hostname_match: bool = False
    
    @property
    def subject_common_name(self) -> Optional[str]:
        """Extract common name from certificate subject"""
        try:
            return self.certificate.subject.get_attributes_for_oid(NameOID.COMMON_NAME)[0].value
        except (IndexError, AttributeError):
            return None
    
    @property
    def subject_alt_names(self) -> List[str]:
        """Extract Subject Alternative Names from certificate"""
        try:
            san_ext = self.certificate.extensions.get_extension_for_oid(ExtensionOID.SUBJECT_ALTERNATIVE_NAME)
            return [name.value for name in san_ext.value]
        except x509.ExtensionNotFound:
            return []
    
    @property
    def issuer_name(self) -> str:
        """Extract issuer common name"""
        try:
            return self.certificate.issuer.get_attributes_for_oid(NameOID.COMMON_NAME)[0].value
        except (IndexError, AttributeError):
            return "Unknown Issuer"
    
    @property
    def serial_number(self) -> str:
        """Get certificate serial number as hex string"""
        return format(self.certificate.serial_number, 'x').upper()
    
    @property
    def fingerprint_sha256(self) -> str:
        """Calculate SHA256 fingerprint"""
        digest = hashes.Hash(hashes.SHA256())
        digest.update(self.certificate.public_bytes(x509.Encoding.DER))
        return digest.finalize().hex().upper()
    
    @property
    def not_valid_before(self) -> datetime:
        """Certificate validity start date"""
        return self.certificate.not_valid_before
    
    @property
    def not_valid_after(self) -> datetime:
        """Certificate validity end date"""
        return self.certificate.not_valid_after
    
    @property
    def days_until_expiry(self) -> int:
        """Days until certificate expires"""
        return (self.not_valid_after - datetime.utcnow()).days
    
    @property
    def is_expired(self) -> bool:
        """Check if certificate is expired"""
        return datetime.utcnow() > self.not_valid_after
    
    @property
    def is_self_signed(self) -> bool:
        """Check if certificate is self-signed"""
        return self.certificate.issuer == self.certificate.subject


class CertificateScanner(ReflectiveModule):
    """
    Domain Certificate Scanner
    
    Discovers and analyzes SSL/TLS certificates across domains and subdomains
    using multiple discovery methods including DNS probing and HTTPS scanning.
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        super().__init__()
        
        default_config = {
            "max_concurrent_scans": 50,
            "default_timeout": 30,
            "dns_timeout": 10,
            "max_retries": 3,
            "retry_delay": 2.0,
            "subdomain_discovery": True,
            "common_subdomains": [
                "www", "mail", "ftp", "webmail", "admin", "api", "app",
                "blog", "dev", "staging", "test", "secure", "shop",
                "portal", "vpn", "remote", "support", "help"
            ],
            "scan_ports": [443, 8443, 993, 995, 465, 587, 636],
            "user_agent": "MSP-SSL-Chaos-Tamer-Scanner/1.0",
            "follow_redirects": True,
            "verify_hostname": True,
            "check_certificate_transparency": False
        }
        
        if config:
            default_config.update(config)
        
        self.config = default_config
        self.db_manager = CertificateDatabase()
        
        # Scanning state
        self._scan_semaphore = asyncio.Semaphore(self.config["max_concurrent_scans"])
        self._scan_results: Dict[str, List[CertificateInfo]] = {}
        self._scan_statistics = {
            "domains_scanned": 0,
            "certificates_discovered": 0,
            "scan_errors": 0,
            "last_scan_time": None
        }
        
        self.logger.info(f"Certificate scanner initialized with {self.config['max_concurrent_scans']} concurrent scans")
    
    async def scan_domain(self, target: ScanTarget) -> List[CertificateInfo]:
        """
        Scan a single domain for certificates
        
        Args:
            target: ScanTarget containing domain and scan parameters
            
        Returns:
            List of discovered certificate information
        """
        async with self._scan_semaphore:
            self.logger.info(f"Starting certificate scan for {target.domain}:{target.port}")
            
            certificates = []
            
            try:
                # Primary domain scan
                cert_info = await self._scan_single_endpoint(target)
                if cert_info:
                    certificates.append(cert_info)
                
                # Subdomain discovery if enabled
                if target.scan_subdomains:
                    subdomain_certs = await self._scan_subdomains(target)
                    certificates.extend(subdomain_certs)
                
                # Additional port scanning
                if target.port == 443:  # Only scan additional ports for HTTPS
                    additional_certs = await self._scan_additional_ports(target)
                    certificates.extend(additional_certs)
                
                # Update statistics
                self._scan_statistics["domains_scanned"] += 1
                self._scan_statistics["certificates_discovered"] += len(certificates)
                self._scan_statistics["last_scan_time"] = datetime.utcnow()
                
                # Store results
                self._scan_results[target.domain] = certificates
                
                self.logger.info(f"Scan completed for {target.domain}: {len(certificates)} certificates found")
                
            except Exception as e:
                self.logger.error(f"Scan failed for {target.domain}: {e}")
                self._scan_statistics["scan_errors"] += 1
                raise
            
            return certificates
    
    async def _scan_single_endpoint(self, target: ScanTarget) -> Optional[CertificateInfo]:
        """Scan a single domain:port endpoint for certificates"""
        try:
            if target.protocol.lower() == "https":
                return await self._scan_https_endpoint(target)
            else:
                return await self._scan_ssl_endpoint(target)
        except Exception as e:
            self.logger.warning(f"Failed to scan {target.domain}:{target.port} - {e}")
            return None
    
    async def _scan_https_endpoint(self, target: ScanTarget) -> Optional[CertificateInfo]:
        """Scan HTTPS endpoint for certificate"""
        connector = aiohttp.TCPConnector(
            ssl=False,  # We'll handle SSL verification manually
            limit=100,
            ttl_dns_cache=300,
            use_dns_cache=True
        )
        
        timeout = aiohttp.ClientTimeout(total=target.timeout)
        
        async with aiohttp.ClientSession(
            connector=connector,
            timeout=timeout,
            headers={"User-Agent": self.config["user_agent"]}
        ) as session:
            
            url = f"https://{target.domain}:{target.port}/"
            
            try:
                # Get certificate through SSL context
                ssl_context = ssl.create_default_context()
                ssl_context.check_hostname = False
                ssl_context.verify_mode = ssl.CERT_NONE
                
                # Connect and get certificate
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(target.timeout)
                
                try:
                    sock.connect((target.domain, target.port))
                    ssl_sock = ssl_context.wrap_socket(sock, server_hostname=target.domain)
                    
                    # Get peer certificate
                    der_cert = ssl_sock.getpeercert(binary_form=True)
                    certificate = x509.load_der_x509_certificate(der_cert)
                    
                    # Get certificate chain
                    cert_chain = []
                    try:
                        chain_der = ssl_sock.getpeercert_chain()
                        if chain_der:
                            cert_chain = [x509.load_der_x509_certificate(cert.public_bytes(x509.Encoding.DER)) 
                                         for cert in chain_der]
                    except:
                        cert_chain = [certificate]  # Fallback to just the leaf certificate
                    
                    # Validate certificate
                    validation_errors = []
                    hostname_match = self._validate_hostname(certificate, target.domain)
                    trust_chain_valid = self._validate_trust_chain(cert_chain)
                    
                    if not hostname_match:
                        validation_errors.append("Hostname does not match certificate")
                    
                    if not trust_chain_valid:
                        validation_errors.append("Certificate chain validation failed")
                    
                    cert_info = CertificateInfo(
                        domain=target.domain,
                        certificate=certificate,
                        certificate_chain=cert_chain,
                        port=target.port,
                        protocol=target.protocol,
                        discovered_at=datetime.utcnow(),
                        validation_errors=validation_errors,
                        trust_chain_valid=trust_chain_valid,
                        hostname_match=hostname_match
                    )
                    
                    return cert_info
                    
                finally:
                    try:
                        ssl_sock.close()
                    except:
                        pass
                    sock.close()
                    
            except Exception as e:
                self.logger.debug(f"HTTPS scan failed for {target.domain}:{target.port} - {e}")
                return None
    
    async def _scan_ssl_endpoint(self, target: ScanTarget) -> Optional[CertificateInfo]:
        """Scan non-HTTPS SSL endpoint for certificate"""
        try:
            # Create SSL context
            ssl_context = ssl.create_default_context()
            ssl_context.check_hostname = False
            ssl_context.verify_mode = ssl.CERT_NONE
            
            # Connect with timeout
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(target.timeout)
            
            try:
                sock.connect((target.domain, target.port))
                ssl_sock = ssl_context.wrap_socket(sock, server_hostname=target.domain)
                
                # Get certificate
                der_cert = ssl_sock.getpeercert(binary_form=True)
                certificate = x509.load_der_x509_certificate(der_cert)
                
                cert_info = CertificateInfo(
                    domain=target.domain,
                    certificate=certificate,
                    certificate_chain=[certificate],
                    port=target.port,
                    protocol=target.protocol,
                    discovered_at=datetime.utcnow(),
                    validation_errors=[],
                    trust_chain_valid=False,  # Can't validate without full chain
                    hostname_match=self._validate_hostname(certificate, target.domain)
                )
                
                return cert_info
                
            finally:
                try:
                    ssl_sock.close()
                except:
                    pass
                sock.close()
                
        except Exception as e:
            self.logger.debug(f"SSL scan failed for {target.domain}:{target.port} - {e}")
            return None
    
    async def _scan_subdomains(self, target: ScanTarget) -> List[CertificateInfo]:
        """Discover and scan subdomains"""
        if not self.config["subdomain_discovery"]:
            return []
        
        subdomains = await self._discover_subdomains(target.domain)
        certificates = []
        
        # Scan discovered subdomains
        tasks = []
        for subdomain in subdomains:
            subdomain_target = ScanTarget(
                domain=subdomain,
                port=target.port,
                protocol=target.protocol,
                client_id=target.client_id,
                timeout=target.timeout
            )
            tasks.append(self._scan_single_endpoint(subdomain_target))
        
        if tasks:
            results = await asyncio.gather(*tasks, return_exceptions=True)
            certificates = [cert for cert in results if isinstance(cert, CertificateInfo)]
        
        return certificates
    
    async def _discover_subdomains(self, domain: str) -> Set[str]:
        """Discover subdomains using DNS and common subdomain lists"""
        subdomains = set()
        
        # Common subdomains
        for subdomain in self.config["common_subdomains"]:
            full_domain = f"{subdomain}.{domain}"
            if await self._dns_resolve(full_domain):
                subdomains.add(full_domain)
        
        # TODO: Add additional subdomain discovery methods:
        # - Certificate Transparency logs
        # - DNS zone transfers (if allowed)
        # - Subdomain brute forcing
        # - Third-party APIs (SecurityTrails, etc.)
        
        return subdomains
    
    async def _dns_resolve(self, domain: str) -> bool:
        """Check if domain resolves via DNS"""
        try:
            resolver = dns.resolver.Resolver()
            resolver.timeout = self.config["dns_timeout"]
            resolver.lifetime = self.config["dns_timeout"]
            
            # Try A record
            try:
                resolver.resolve(domain, 'A')
                return True
            except dns.resolver.NXDOMAIN:
                pass
            
            # Try AAAA record
            try:
                resolver.resolve(domain, 'AAAA')
                return True
            except dns.resolver.NXDOMAIN:
                pass
            
            return False
            
        except Exception:
            return False
    
    async def _scan_additional_ports(self, target: ScanTarget) -> List[CertificateInfo]:
        """Scan additional SSL/TLS ports"""
        certificates = []
        
        for port in self.config["scan_ports"]:
            if port == target.port:
                continue  # Skip the port we already scanned
            
            port_target = ScanTarget(
                domain=target.domain,
                port=port,
                protocol="ssl",
                client_id=target.client_id,
                timeout=target.timeout
            )
            
            cert_info = await self._scan_single_endpoint(port_target)
            if cert_info:
                certificates.append(cert_info)
        
        return certificates
    
    def _validate_hostname(self, certificate: x509.Certificate, hostname: str) -> bool:
        """Validate that certificate matches the hostname"""
        try:
            # Check common name
            cn = certificate.subject.get_attributes_for_oid(NameOID.COMMON_NAME)[0].value
            if self._hostname_matches(cn, hostname):
                return True
            
            # Check Subject Alternative Names
            try:
                san_ext = certificate.extensions.get_extension_for_oid(ExtensionOID.SUBJECT_ALTERNATIVE_NAME)
                for name in san_ext.value:
                    if hasattr(name, 'value') and self._hostname_matches(name.value, hostname):
                        return True
            except x509.ExtensionNotFound:
                pass
            
            return False
            
        except (IndexError, AttributeError):
            return False
    
    def _hostname_matches(self, cert_name: str, hostname: str) -> bool:
        """Check if certificate name matches hostname (supports wildcards)"""
        cert_name = cert_name.lower()
        hostname = hostname.lower()
        
        if cert_name == hostname:
            return True
        
        # Wildcard matching
        if cert_name.startswith('*.'):
            cert_domain = cert_name[2:]
            if '.' in hostname:
                host_domain = hostname.split('.', 1)[1]
                return cert_domain == host_domain
        
        return False
    
    def _validate_trust_chain(self, cert_chain: List[x509.Certificate]) -> bool:
        """Validate certificate trust chain"""
        if not cert_chain:
            return False
        
        # Basic chain validation
        # TODO: Implement full trust chain validation against root CAs
        try:
            for i in range(len(cert_chain) - 1):
                current_cert = cert_chain[i]
                issuer_cert = cert_chain[i + 1]
                
                # Check if issuer matches
                if current_cert.issuer != issuer_cert.subject:
                    return False
                
                # TODO: Verify signature
                # issuer_cert.public_key().verify(
                #     current_cert.signature,
                #     current_cert.tbs_certificate_bytes,
                #     current_cert.signature_algorithm_oid
                # )
            
            return True
            
        except Exception:
            return False
    
    async def scan_multiple_domains(self, targets: List[ScanTarget]) -> Dict[str, List[CertificateInfo]]:
        """Scan multiple domains concurrently"""
        self.logger.info(f"Starting bulk scan of {len(targets)} domains")
        
        tasks = [self.scan_domain(target) for target in targets]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        scan_results = {}
        for target, result in zip(targets, results):
            if isinstance(result, Exception):
                self.logger.error(f"Scan failed for {target.domain}: {result}")
                scan_results[target.domain] = []
            else:
                scan_results[target.domain] = result
        
        return scan_results
    
    async def continuous_scan(self, targets: List[ScanTarget], interval: int = 3600):
        """Run continuous scanning with specified interval"""
        self.logger.info(f"Starting continuous scan with {interval}s interval")
        
        while True:
            try:
                await self.scan_multiple_domains(targets)
                await asyncio.sleep(interval)
            except Exception as e:
                self.logger.error(f"Continuous scan error: {e}")
                await asyncio.sleep(60)  # Wait before retrying
    
    def get_scan_results(self, domain: Optional[str] = None) -> Dict[str, List[CertificateInfo]]:
        """Get scan results for domain or all domains"""
        if domain:
            return {domain: self._scan_results.get(domain, [])}
        return self._scan_results.copy()
    
    def get_scan_statistics(self) -> Dict[str, Any]:
        """Get scanning statistics"""
        return self._scan_statistics.copy()
    
    def clear_scan_results(self, domain: Optional[str] = None):
        """Clear scan results for domain or all domains"""
        if domain:
            self._scan_results.pop(domain, None)
        else:
            self._scan_results.clear()
    
    # ReflectiveModule implementation
    def get_health_status(self) -> Dict[str, Any]:
        """Get scanner health status"""
        return {
            "status": "healthy",
            "active_scans": self.config["max_concurrent_scans"] - self._scan_semaphore._value,
            "total_domains_scanned": self._scan_statistics["domains_scanned"],
            "total_certificates_discovered": self._scan_statistics["certificates_discovered"],
            "scan_errors": self._scan_statistics["scan_errors"],
            "last_scan_time": self._scan_statistics["last_scan_time"].isoformat() if self._scan_statistics["last_scan_time"] else None,
            "configuration": {
                "max_concurrent_scans": self.config["max_concurrent_scans"],
                "subdomain_discovery": self.config["subdomain_discovery"],
                "scan_ports": self.config["scan_ports"]
            }
        }
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get Prometheus metrics"""
        return {
            "msp_ssl_scanner_domains_scanned_total": self._scan_statistics["domains_scanned"],
            "msp_ssl_scanner_certificates_discovered_total": self._scan_statistics["certificates_discovered"],
            "msp_ssl_scanner_errors_total": self._scan_statistics["scan_errors"],
            "msp_ssl_scanner_active_scans": self.config["max_concurrent_scans"] - self._scan_semaphore._value,
            "msp_ssl_scanner_max_concurrent_scans": self.config["max_concurrent_scans"]
        }


# Utility functions
def create_scan_target(domain: str, **kwargs) -> ScanTarget:
    """Create a ScanTarget with sensible defaults"""
    return ScanTarget(domain=domain, **kwargs)


def create_bulk_scan_targets(domains: List[str], **common_kwargs) -> List[ScanTarget]:
    """Create multiple ScanTargets with common configuration"""
    return [ScanTarget(domain=domain, **common_kwargs) for domain in domains]


# Export main classes
__all__ = ["CertificateScanner", "ScanTarget", "CertificateInfo", "create_scan_target", "create_bulk_scan_targets"]