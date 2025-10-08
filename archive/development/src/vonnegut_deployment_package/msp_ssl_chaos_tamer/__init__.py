"""
MSP SSL Chaos Tamer - Open Source Certificate Management for MSPs

A zero-trust, multi-CA certificate management system designed specifically 
for Managed Service Providers who need to tame SSL certificate chaos across
multiple clients and certificate authorities.
"""

__version__ = "0.1.0"
__author__ = "MSP SSL Chaos Tamer Contributors"
__license__ = "MIT"

from .core.orchestrator import CertificateOrchestrator
from .core.models import Certificate, Client, MSP
from .core.interfaces import CAPlugin, ReflectiveModule

__all__ = [
    "CertificateOrchestrator",
    "Certificate", 
    "Client",
    "MSP",
    "CAPlugin",
    "ReflectiveModule"
]