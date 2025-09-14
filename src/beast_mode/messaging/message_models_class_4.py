class AgentCapabilities(BaseModel, ReflectiveModule):
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
    """Agent capabilities model with validation."""
    agent_id: str = Field(..., description='Unique agent identifier')
    agent_name: str = Field(..., description='Human-readable agent name')
    capabilities: List[AgentCapability] = Field(default_factory=list, description='List of agent capabilities')
    specializations: List[str] = Field(default_factory=list, description='Specialized skills or domains')
    availability: str = Field(default='available', description='Current availability status')
    office_hours: Optional[Dict[str, str]] = Field(None, description='Office hours schedule')
    max_concurrent_tasks: int = Field(default=3, description='Maximum concurrent tasks')
    current_load: int = Field(default=0, description='Current task load')
    trust_score: float = Field(default=0.5, ge=0.0, le=1.0, description='Trust score based on past performance')
    last_seen: datetime = Field(default_factory=datetime.now, description='Last activity timestamp')

    @validator('capabilities')
    def validate_capabilities(cls, v) -> Any:
        try:
            pass  # TODO: Add method implementation
        except Exception as e:
            logging.error(f"Error in method: {e}")
            raise
        """Validate capabilities list."""
        if not v:
            raise ValueError('Agent must have at least one capability')
        return v

    @validator('agent_id')
    def validate_agent_id(cls, v) -> Any:
        try:
            pass  # TODO: Add method implementation
        except Exception as e:
            logging.error(f"Error in method: {e}")
            raise
        """Validate agent ID format."""
        if not v or len(v) < 3:
            raise ValueError('Agent ID must be at least 3 characters')
        return v
