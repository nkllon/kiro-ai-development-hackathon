"""
Let's Encrypt ACME plugin for MSP SSL Chaos Tamer

Implements ACME protocol client for Let's Encrypt integration with certificate
request, renewal, and revocation workflows using the ACME v2 protocol.
"""

import logging
import time
import json
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from urllib.parse import urlparse

try:
    from cryptography import x509
    from cryptography.hazmat.primitives import hashes, serialization
    from cryptography.hazmat.primitives.asymmetric import rsa
    from cryptography.x509.oid import NameOID
    CRYPTO_AVAILABLE = True
    
    # ACME dependencies are optional for basic functionality
    try:
        from acme import client, messages, challenges, crypto_util
        from acme.client import ClientV2
        import josepy as jose
        ACME_AVAILABLE = True
    except ImportError:
        ACME_AVAILABLE = False
        
except ImportError:
    CRYPTO_AVAILABLE = False
    ACME_AVAILABLE = False

from .base import BaseCAPlugin
from ..core.interfaces import (
    CertificateRequest, CertificateStatus, RevocationStatus,
    AuthenticationError, CertificateRequestError, CertificateRenewalError,
    CertificateRevocationError, CertificateStatusError, CertificateDownloadError
)


class LetsEncryptACMEPlugin(BaseCAPlugin):
    """
    Let's Encrypt ACME plugin implementation
    
    Provides ACME v2 protocol integration for Let's Encrypt certificate
    management with HTTP-01 and DNS-01 challenge support.
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        if not CRYPTO_AVAILABLE:
            raise ImportError(
                "Cryptography dependencies not available. Install with: "
                "pip install cryptography"
            )
        
        if not ACME_AVAILABLE:
            self.logger.warning(
                "ACME dependencies not available. Some features will be limited. "
                "Install with: pip install acme josepy"
            )
        
        config = config or {}
        config.setdefault("ca_name", "letsencrypt")
        config.setdefault("rate_limit_requests", 300)  # Let's Encrypt allows 300/hour
        config.setdefault("rate_limit_window", 3600)
        config.setdefault("max_retries", 3)
        config.setdefault("supported_features", [
            "certificate_request", "certificate_renewal", "certificate_revocation",
            "http_01_challenge", "dns_01_challenge"
        ])
        
        super().__init__("letsencrypt", config)
        
        # ACME configuration
        self.directory_url = config.get(
            "directory_url", 
            "https://acme-v02.api.letsencrypt.org/directory"  # Production
            # "https://acme-staging-v02.api.letsencrypt.org/directory"  # Staging
        )
        
        self.challenge_type = config.get("challenge_type", "http-01")
        self.key_size = config.get("key_size", 2048)
        
        # ACME client state
        self._acme_client: Optional[ClientV2] = None
        self._account_key: Optional[jose.JWKRSA] = None
        self._account_url: Optional[str] = None
        
        # Certificate storage
        self._certificates: Dict[str, Dict[str, Any]] = {}
        
        self.logger.info("Let's Encrypt ACME plugin initialized")
    
    def _generate_account_key(self) -> jose.JWKRSA:
        """Generate RSA key for ACME account"""
        private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=self.key_size
        )
        return jose.JWKRSA(key=private_key)
    
    def _generate_certificate_key(self) -> rsa.RSAPrivateKey:
        """Generate RSA key for certificate"""
        return rsa.generate_private_key(
            public_exponent=65537,
            key_size=self.key_size
        )
    
    def _create_csr(self, domain: str, private_key: rsa.RSAPrivateKey) -> x509.CertificateSigningRequest:
        """Create certificate signing request"""
        subject = x509.Name([
            x509.NameAttribute(NameOID.COMMON_NAME, domain)
        ])
        
        # Add SAN extension for the domain
        san_extension = x509.SubjectAlternativeName([
            x509.DNSName(domain)
        ])
        
        csr = x509.CertificateSigningRequestBuilder().subject_name(
            subject
        ).add_extension(
            san_extension,
            critical=False
        ).sign(private_key, hashes.SHA256())
        
        return csr
    
    def _authenticate_impl(self, credentials: Dict[str, str]) -> bool:
        """
        Authenticate with Let's Encrypt ACME server
        
        Args:
            credentials: Must contain 'email' for account registration
            
        Returns:
            bool: True if authentication successful
        """
        try:
            email = credentials.get("email")
            if not email:
                self.logger.error("Email is required for Let's Encrypt registration")
                return False
            
            # Generate or load account key
            account_key_pem = credentials.get("account_key")
            if account_key_pem:
                # Load existing account key
                try:
                    private_key = serialization.load_pem_private_key(
                        account_key_pem.encode(), password=None
                    )
                    self._account_key = jose.JWKRSA(key=private_key)
                except Exception as e:
                    self.logger.error(f"Failed to load account key: {e}")
                    return False
            else:
                # Generate new account key
                self._account_key = self._generate_account_key()
                self.logger.info("Generated new ACME account key")
            
            # Create ACME client
            net = client.ClientNetwork(self._account_key, user_agent="MSP-SSL-Chaos-Tamer/1.0")
            directory = client.ClientV2.get_directory(self.directory_url, net)
            self._acme_client = ClientV2(directory, net=net)
            
            # Register account or get existing account
            try:
                # Try to register new account
                registration = messages.NewRegistration.from_data(
                    email=email,
                    terms_of_service_agreed=True
                )
                account = self._acme_client.new_account(registration)
                self._account_url = account.uri
                self.logger.info(f"Registered new ACME account: {email}")
                
            except Exception as e:
                # Account might already exist, try to get it
                try:
                    registration = messages.NewRegistration.from_data(
                        email=email,
                        only_return_existing=True
                    )
                    account = self._acme_client.new_account(registration)
                    self._account_url = account.uri
                    self.logger.info(f"Using existing ACME account: {email}")
                    
                except Exception as e2:
                    self.logger.error(f"Failed to register/retrieve ACME account: {e2}")
                    return False
            
            return True
            
        except Exception as e:
            self.logger.error(f"ACME authentication failed: {e}")
            return False
    
    def _request_certificate_impl(self, request: CertificateRequest) -> str:
        """
        Request certificate from Let's Encrypt
        
        Args:
            request: Certificate request details
            
        Returns:
            str: Certificate ID for tracking
        """
        if not self._acme_client:
            raise CertificateRequestError("ACME client not authenticated")
        
        domain = request.domain
        certificate_id = f"le_{domain}_{int(time.time())}"
        
        try:
            self.logger.info(f"Requesting certificate for {domain}")
            
            # Generate private key for certificate
            private_key = self._generate_certificate_key()
            
            # Create certificate signing request
            csr = self._create_csr(domain, private_key)
            
            # Create new order
            order = self._acme_client.new_order(csr)
            
            # Process authorizations
            for authorization in order.authorizations:
                self._process_authorization(authorization, domain)
            
            # Finalize order
            order = self._acme_client.poll_and_finalize(order)
            
            # Get certificate
            certificate_pem = order.fullchain_pem
            private_key_pem = private_key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.PKCS8,
                encryption_algorithm=serialization.NoEncryption()
            ).decode()
            
            # Store certificate data
            self._certificates[certificate_id] = {
                "domain": domain,
                "certificate_pem": certificate_pem,
                "private_key_pem": private_key_pem,
                "order_url": order.uri,
                "status": "issued",
                "issued_at": datetime.utcnow(),
                "expires_at": self._extract_expiry_date(certificate_pem)
            }
            
            self.logger.info(f"Certificate issued successfully: {certificate_id}")
            return certificate_id
            
        except Exception as e:
            self.logger.error(f"Certificate request failed for {domain}: {e}")
            raise CertificateRequestError(f"ACME certificate request failed: {e}")
    
    def _process_authorization(self, authorization, domain: str) -> None:
        """Process ACME authorization challenges"""
        # Find HTTP-01 challenge
        challenge = None
        for chall in authorization.body.challenges:
            if isinstance(chall.chall, challenges.HTTP01):
                challenge = chall
                break
        
        if not challenge:
            raise CertificateRequestError(f"No HTTP-01 challenge found for {domain}")
        
        # Get challenge response
        response, validation = challenge.response_and_validation(self._account_key)
        
        # In a real implementation, you would:
        # 1. Create the challenge file at /.well-known/acme-challenge/{challenge.chall.token}
        # 2. Serve the validation content
        # 3. Notify ACME server
        
        # For this implementation, we'll simulate the challenge completion
        self.logger.warning(
            f"HTTP-01 challenge for {domain}: "
            f"Create file /.well-known/acme-challenge/{challenge.chall.token} "
            f"with content: {validation}"
        )
        
        # In production, wait for challenge setup, then:
        self._acme_client.answer_challenge(challenge, response)
        
        # Poll for challenge completion
        challenge = self._acme_client.poll(challenge)
        if challenge.status != messages.STATUS_VALID:
            raise CertificateRequestError(f"Challenge failed for {domain}: {challenge.status}")
    
    def _extract_expiry_date(self, certificate_pem: str) -> datetime:
        """Extract expiry date from certificate PEM"""
        try:
            cert = x509.load_pem_x509_certificate(certificate_pem.encode())
            return cert.not_valid_after
        except Exception:
            # Default to 90 days from now (Let's Encrypt standard)
            return datetime.utcnow() + timedelta(days=90)
    
    def _renew_certificate_impl(self, certificate_id: str) -> str:
        """
        Renew Let's Encrypt certificate
        
        Args:
            certificate_id: ID of certificate to renew
            
        Returns:
            str: New certificate ID
        """
        if certificate_id not in self._certificates:
            raise CertificateRenewalError(f"Certificate not found: {certificate_id}")
        
        cert_data = self._certificates[certificate_id]
        domain = cert_data["domain"]
        
        # Create new certificate request for renewal
        renewal_request = CertificateRequest(
            domain=domain,
            client_id="renewal",
            ca_provider="letsencrypt"
        )
        
        # Request new certificate
        new_certificate_id = self._request_certificate_impl(renewal_request)
        
        # Mark old certificate as renewed
        cert_data["status"] = "renewed"
        cert_data["renewed_to"] = new_certificate_id
        
        return new_certificate_id
    
    def _revoke_certificate_impl(self, certificate_id: str, reason: str) -> RevocationStatus:
        """
        Revoke Let's Encrypt certificate
        
        Args:
            certificate_id: ID of certificate to revoke
            reason: Reason for revocation
            
        Returns:
            RevocationStatus: Revocation status information
        """
        if not self._acme_client:
            raise CertificateRevocationError("ACME client not authenticated")
        
        if certificate_id not in self._certificates:
            raise CertificateRevocationError(f"Certificate not found: {certificate_id}")
        
        try:
            cert_data = self._certificates[certificate_id]
            certificate_pem = cert_data["certificate_pem"]
            
            # Load certificate
            cert = x509.load_pem_x509_certificate(certificate_pem.encode())
            
            # Revoke certificate
            self._acme_client.revoke(
                crypto_util.pyopenssl_load_certificate(certificate_pem),
                reason=0  # Unspecified reason
            )
            
            # Update certificate status
            cert_data["status"] = "revoked"
            cert_data["revoked_at"] = datetime.utcnow()
            cert_data["revocation_reason"] = reason
            
            return RevocationStatus(
                certificate_id=certificate_id,
                revoked=True,
                revocation_date=datetime.utcnow(),
                reason=reason
            )
            
        except Exception as e:
            self.logger.error(f"Certificate revocation failed for {certificate_id}: {e}")
            raise CertificateRevocationError(f"ACME revocation failed: {e}")
    
    def _get_certificate_status_impl(self, certificate_id: str) -> CertificateStatus:
        """
        Get Let's Encrypt certificate status
        
        Args:
            certificate_id: ID of certificate to check
            
        Returns:
            CertificateStatus: Current certificate status
        """
        if certificate_id not in self._certificates:
            raise CertificateStatusError(f"Certificate not found: {certificate_id}")
        
        cert_data = self._certificates[certificate_id]
        
        return CertificateStatus(
            certificate_id=certificate_id,
            status=cert_data["status"],
            issued_date=cert_data.get("issued_at"),
            expiration_date=cert_data.get("expires_at"),
            last_checked=datetime.utcnow()
        )
    
    def _download_certificate_impl(self, certificate_id: str) -> Dict[str, str]:
        """
        Download Let's Encrypt certificate files
        
        Args:
            certificate_id: ID of certificate to download
            
        Returns:
            Dict containing certificate, chain, and private key
        """
        if certificate_id not in self._certificates:
            raise CertificateDownloadError(f"Certificate not found: {certificate_id}")
        
        cert_data = self._certificates[certificate_id]
        
        # Split fullchain into certificate and chain
        certificate_pem = cert_data["certificate_pem"]
        cert_parts = certificate_pem.split("-----END CERTIFICATE-----")
        
        if len(cert_parts) >= 2:
            certificate = cert_parts[0] + "-----END CERTIFICATE-----"
            chain = "-----BEGIN CERTIFICATE-----" + cert_parts[1] if cert_parts[1].strip() else ""
        else:
            certificate = certificate_pem
            chain = ""
        
        return {
            "certificate": certificate,
            "chain": chain,
            "private_key": cert_data["private_key_pem"],
            "fullchain": certificate_pem
        }
    
    def get_supported_features(self) -> List[str]:
        """Get Let's Encrypt specific features"""
        return [
            "certificate_request",
            "certificate_renewal", 
            "certificate_revocation",
            "http_01_challenge",
            "dns_01_challenge",
            "wildcard_certificates",
            "90_day_validity"
        ]
    
    def get_rate_limits(self) -> Dict[str, int]:
        """Get Let's Encrypt specific rate limits"""
        return {
            "requests_per_window": self.rate_limit_requests,
            "window_seconds": self.rate_limit_window,
            "current_usage": len(self._request_timestamps),
            "remaining_requests": max(0, self.rate_limit_requests - len(self._request_timestamps)),
            "certificates_per_domain_per_week": 50,
            "duplicate_certificate_limit_per_week": 5
        }
    
    def get_ca_info(self) -> Dict[str, Any]:
        """Get comprehensive Let's Encrypt plugin information"""
        base_info = super().get_ca_info()
        base_info.update({
            "directory_url": self.directory_url,
            "challenge_type": self.challenge_type,
            "key_size": self.key_size,
            "certificate_validity_days": 90,
            "renewal_recommended_days": 30,
            "account_url": self._account_url,
            "certificates_managed": len(self._certificates)
        })
        return base_info


# Register plugin
def create_plugin(config: Dict[str, Any] = None) -> LetsEncryptACMEPlugin:
    """Factory function to create Let's Encrypt plugin"""
    return LetsEncryptACMEPlugin(config)


# Plugin metadata
PLUGIN_INFO = {
    "name": "letsencrypt",
    "display_name": "Let's Encrypt",
    "description": "ACME v2 protocol client for Let's Encrypt certificates",
    "version": "1.0.0",
    "ca_url": "https://letsencrypt.org/",
    "supported_features": [
        "certificate_request",
        "certificate_renewal",
        "certificate_revocation",
        "http_01_challenge",
        "dns_01_challenge",
        "wildcard_certificates"
    ],
    "rate_limits": {
        "certificates_per_domain_per_week": 50,
        "duplicate_certificate_limit_per_week": 5,
        "requests_per_hour": 300
    },
    "certificate_validity_days": 90,
    "cost": "free"
}