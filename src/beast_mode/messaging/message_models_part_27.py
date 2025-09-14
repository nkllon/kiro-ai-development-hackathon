from datetime import datetime
from typing import Dict, List, Any
from src.rm_ddd.core.health import ModuleHealth


    def get_status_report(self) -> Dict[str, any]:
        """Get comprehensive status report for this module."""
        return {
            "module_id": self.module_id,
            "health_status": self.health_status,
            "capabilities": self.capabilities,
            "dependencies": self.dependencies,
            "last_updated": self.last_updated,
            "performance_metrics": self.get_metrics()
        }
    """
        Core Beast Mode message model with comprehensive validation.
        
        Provides systematic message structure for agent collaboration
        with proper serialization and validation.
        """
    message_id: str = Field(default_factory=lambda: str(uuid4()), description='Unique message identifier')
    message_type: MessageType = Field(..., description='Type of message')
    timestamp: datetime = Field(default_factory=datetime.now, description='Message creation timestamp')
    sender_id: str = Field(..., description='Sender agent identifier')
    recipient_id: Optional[str] = Field(None, description='Target recipient (None for broadcast)')
    channel: str = Field(default='beast_mode_general', description='Communication channel')
    subject: Optional[str] = Field(None, description='Message subject/title')
    content: Dict[str, Any] = Field(default_factory=dict, description='Message payload')
    attachments: List[Dict[str, Any]] = Field(default_factory=list, description='File attachments or references')
    correlation_id: Optional[str] = Field(None, description='Correlation ID for message chains')
    reply_to: Optional[str] = Field(None, description='Message ID this is replying to')
    priority: str = Field(default='normal', description='Message priority level')
    expires_at: Optional[datetime] = Field(None, description='Message expiration time')
    requires_response: bool = Field(default=False, description='Whether response is required')
    capabilities_required: List[AgentCapability] = Field(default_factory=list, description='Required capabilities for handling')
    spore_references: List[str] = Field(default_factory=list, description='Referenced spore IDs')

    @validator('priority')