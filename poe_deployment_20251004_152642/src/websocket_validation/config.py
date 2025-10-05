"""
Configuration management for WebSocket validation framework.
"""

import os
from dataclasses import dataclass
from typing import Dict, List, Optional
from pathlib import Path


@dataclass
class ValidationConfig:
    """Configuration settings for validation framework."""
    
    # Test endpoints
    production_base_url: str = "https://observatory.nkllon.com"
    local_base_url: str = "http://localhost:8888"
    websocket_endpoints: List[str] = None
    
    # Timeouts and retries
    connection_timeout: float = 30.0
    websocket_timeout: float = 10.0
    max_retries: int = 3
    retry_backoff: float = 1.0
    
    # Evidence collection
    evidence_dir: Path = Path("validation_evidence")
    encrypt_evidence: bool = True
    evidence_retention_days: int = 30
    
    # Analysis settings
    documentation_accuracy_threshold: float = 0.95
    implementation_completeness_threshold: float = 0.90
    
    # Logging
    log_level: str = "INFO"
    log_format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    correlation_id_header: str = "X-Validation-ID"
    
    # Security
    verify_ssl: bool = True
    user_agent: str = "WebSocket-Validation-Framework/1.0.0"
    
    def __post_init__(self):
        """Initialize default values after creation."""
        if self.websocket_endpoints is None:
            self.websocket_endpoints = [
                "/ws/emoji-rain",
                "/ws/status",
                "/ws/health"
            ]
        
        # Convert evidence_dir to Path if it's a string
        if isinstance(self.evidence_dir, str):
            self.evidence_dir = Path(self.evidence_dir)
        
        # Ensure evidence directory exists
        self.evidence_dir.mkdir(parents=True, exist_ok=True)
    
    @classmethod
    def from_env(cls) -> 'ValidationConfig':
        """Create configuration from environment variables."""
        return cls(
            production_base_url=os.getenv("VALIDATION_PROD_URL", "https://observatory.nkllon.com"),
            local_base_url=os.getenv("VALIDATION_LOCAL_URL", "http://localhost:8888"),
            connection_timeout=float(os.getenv("VALIDATION_TIMEOUT", "30.0")),
            websocket_timeout=float(os.getenv("VALIDATION_WS_TIMEOUT", "10.0")),
            max_retries=int(os.getenv("VALIDATION_MAX_RETRIES", "3")),
            evidence_dir=Path(os.getenv("VALIDATION_EVIDENCE_DIR", "validation_evidence")),
            encrypt_evidence=os.getenv("VALIDATION_ENCRYPT", "true").lower() == "true",
            log_level=os.getenv("VALIDATION_LOG_LEVEL", "INFO"),
            verify_ssl=os.getenv("VALIDATION_VERIFY_SSL", "true").lower() == "true"
        )
    
    def to_dict(self) -> Dict:
        """Convert configuration to dictionary."""
        return {
            "production_base_url": self.production_base_url,
            "local_base_url": self.local_base_url,
            "websocket_endpoints": self.websocket_endpoints,
            "connection_timeout": self.connection_timeout,
            "websocket_timeout": self.websocket_timeout,
            "max_retries": self.max_retries,
            "retry_backoff": self.retry_backoff,
            "evidence_dir": str(self.evidence_dir),
            "encrypt_evidence": self.encrypt_evidence,
            "evidence_retention_days": self.evidence_retention_days,
            "documentation_accuracy_threshold": self.documentation_accuracy_threshold,
            "implementation_completeness_threshold": self.implementation_completeness_threshold,
            "log_level": self.log_level,
            "verify_ssl": self.verify_ssl,
            "user_agent": self.user_agent
        }


# Global configuration instance
config = ValidationConfig.from_env()