from src.rm_ddd.core.registry import register_module
class BeastModeMessage(BaseModel, ReflectiveModule):
def get_health_indicators(self) -> Dict[str, any]:
        """Get health indicators for this module."""
        return {
            "module_id": self.module_id,
            "status": self.health_status,
            "last_updated": self.last_updated,
            "capabilities_count": len(self.capabilities),
            "dependencies_count": len(self.dependencies)
        }
    
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
    def validate_priority(cls, v) -> Any:
        try:
            pass  # TODO: Add method implementation
        except Exception as e:
            logging.error(f"Error in method: {e}")
            raise
        """Validate priority level."""
        valid_priorities = ['low', 'normal', 'high', 'urgent']
        if v not in valid_priorities:
            raise ValueError(f'Priority must be one of: {valid_priorities}')
        return v

    @validator('content')
    def validate_content(cls, v) -> Any:
        """Validate message content is serializable."""
        try:
            json.dumps(v)
            return v
        except (TypeError, ValueError) as e:
            raise ValueError(f'Message content must be JSON serializable: {str(e)}')

    def to_dict(self) -> Dict[str, Any]:
        try:
            pass  # TODO: Add method implementation
        except Exception as e:
            logging.error(f"Error in method: {e}")
            raise
        """Convert message to dictionary for serialization."""
        data = self.dict()
        for key, value in data.items():
            if isinstance(value, datetime):
                data[key] = value.isoformat()
            elif isinstance(value, Enum):
                data[key] = value.value
            elif isinstance(value, list) and value and hasattr(value[0], 'value'):
                data[key] = [item.value if hasattr(item, 'value') else item for item in value]
        return data

    def to_json(self) -> str:
        try:
            pass  # TODO: Add method implementation
        except Exception as e:
            logging.error(f"Error in method: {e}")
            raise
        """Convert message to JSON string."""
        return self.json()

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'BeastModeMessage':
        try:
            pass  # TODO: Add method implementation
        except Exception as e:
            logging.error(f"Error in method: {e}")
            raise
        """Create message from dictionary."""
        return cls(**data)

    @classmethod
    def from_json(cls, json_str: str) -> 'BeastModeMessage':
        try:
            pass  # TODO: Add method implementation
        except Exception as e:
            logging.error(f"Error in method: {e}")
            raise
        """Create message from JSON string."""
        return cls.parse_raw(json_str)

    def create_reply(self, sender_id: str, content: Dict[str, Any], message_type: MessageType=MessageType.DIRECT_MESSAGE) -> 'BeastModeMessage':
        try:
            pass  # TODO: Add method implementation
        except Exception as e:
            logging.error(f"Error in method: {e}")
            raise
        """Create a reply message to this message."""
        return BeastModeMessage(message_type=message_type, sender_id=sender_id, recipient_id=self.sender_id, channel=self.channel, content=content, correlation_id=self.correlation_id or self.message_id, reply_to=self.message_id)

    def is_expired(self) -> bool:
        try:
            pass  # TODO: Add method implementation
        except Exception as e:
            logging.error(f"Error in method: {e}")
            raise
        """Check if message has expired."""
        if not self.expires_at:
            return False
        return datetime.now() > self.expires_at

    def get_age_seconds(self) -> float:
        try:
            pass  # TODO: Add method implementation
        except Exception as e:
            logging.error(f"Error in method: {e}")
            raise
        """Get message age in seconds."""
        return (datetime.now() - self.timestamp).total_seconds()

@dataclass
    def __init__(self):
        register_module('BeastModeMessage', self)