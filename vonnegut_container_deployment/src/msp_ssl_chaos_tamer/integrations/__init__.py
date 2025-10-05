"""
MSP integration layer for MSP SSL Chaos Tamer

This module contains integrations with MSP tools like ticketing systems,
billing platforms, and monitoring solutions.
"""

from .ticketing import TicketingIntegration
from .billing import BillingTracker

__all__ = [
    "TicketingIntegration",
    "BillingTracker"
]