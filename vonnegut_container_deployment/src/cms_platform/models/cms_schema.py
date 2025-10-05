"""CMS Core Data Model Schema"""

from enum import Enum
from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, Field


class ContentType(str, Enum):
    """Content type enumeration."""
    CODE_FILE = "code_file"
    DOCUMENT = "document"
    SPECIFICATION = "specification"
    TASK = "task"
    REQUIREMENT = "requirement"


class StakeholderRole(str, Enum):
    """Stakeholder role enumeration."""
    DEVELOPER = "developer"
    DEVOPS = "devops"
    CFO = "cfo"
    CTO = "cto"
    ARCHITECT = "architect"


class BaseEntity(BaseModel):
    """Base entity with common fields."""
    id: str = Field(..., description="Unique identifier")
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    created_by: Optional[str] = None
    updated_by: Optional[str] = None


class Specification(BaseEntity):
    """Specification entity."""
    name: str
    description: str
    version: str
    status: str
    requirements: List[str] = []
    tasks: List[str] = []
    dependencies: List[str] = []


class CodeFile(BaseEntity):
    """Code file entity."""
    file_path: str
    content_hash: str
    language: str
    size_bytes: int
    specification_id: Optional[str] = None
    patterns: List[str] = []
    governance_violations: List[str] = []


class Document(BaseEntity):
    """Document entity."""
    title: str
    content: str
    document_type: str
    specification_id: Optional[str] = None
    references: List[str] = []
    sections: List[str] = []


class Task(BaseEntity):
    """Task entity."""
    title: str
    description: str
    status: str
    priority: str
    estimated_effort: int
    specification_id: str
    dependencies: List[str] = []
    assignees: List[str] = []


class GovernanceViolation(BaseEntity):
    """Governance violation entity."""
    code_file_id: str
    rule_id: str
    violation_type: str
    severity: str
    description: str
    resolved: bool = False


class DeploymentPattern(BaseEntity):
    """Deployment pattern entity."""
    pattern_name: str
    description: str
    pattern_type: str
    success_rate: float
    usage_count: int = 0
    metadata: dict = {}


class DevelopmentCost(BaseEntity):
    """Development cost entity."""
    specification_id: str
    cost_type: str
    amount: float
    currency: str = "USD"
    period_start: datetime
    period_end: datetime
