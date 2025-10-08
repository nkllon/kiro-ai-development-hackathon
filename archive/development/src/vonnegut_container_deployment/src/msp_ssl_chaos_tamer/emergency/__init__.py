"""
Emergency certificate management for MSP SSL Chaos Tamer

This module contains the "oh shit" button functionality for handling
certificate emergencies like expiration and compromise.
"""

from .detector import EmergencyDetector
from .provisioner import EmergencyProvisioner

__all__ = [
    "EmergencyDetector",
    "EmergencyProvisioner"
]