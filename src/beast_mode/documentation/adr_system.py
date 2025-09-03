"""
Beast Mode Framework - Architectural Decision Record (ADR) System
Implements UC-18: ADR documentation system for design decisions and trade-offs
Provides systematic decision tracking and historical context preservation
"""

import json
import uuid
from typing import Dict, Any, List, Optional, Union
from dataclasses import dataclass, field, asdict
from datetime import datetime
from enum import Enum
from pathlib import Path

from ..core.reflective_module import ReflectiveModule, HealthStatus

class DecisionStatus(Enum):
    PROPOSED = "proposed"
    ACCEPTED = "accepted"
    DEPRECATED = "deprecated"
    SUPERSEDED = "superseded"

class DecisionCategory(Enum):
    ARCHITECTURE = "architecture"
    TECHNOLOGY = "technology"
    PROCESS = "process"
    CONSTRAINT = "constraint"
    INTEGRATION = "integration"
    SECURITY = "security"
    PERFORMANCE = "performance"

@dataclass
class DecisionContext:
    problem_statement: str
    business_drivers: List[str]
    technical_constraints: List[str]
    stakeholders: List[str]
    timeline: str
    risk_factors: List[str] = field(default_factory=list)

@dataclass
class DecisionOption:
    option_id: str
    title: str
    description: str
    pros: List[str]
    cons: List[str]
    implementation_effort: str  # low, medium, high
    risk_level: str  # low, medium, high
    cost_impact: str  # low, medium, high
    technical_debt: str  # none, low, medium, high

@dataclass
class DecisionConsequence:
    positive_outcomes: List[str]
    negative_outcomes: List[str]
    mitigation_strategies: List[str]
    monitoring_requirements: List[str]
    success_metrics: List[str]

@dataclass
class ArchitecturalDecisionRecord:
    adr_id: str
    title: str
    status: DecisionStatus
    category: DecisionCategory
    date_created: datetime
    date_decided: Optional[datetime]
    decision_makers: List[str]
    context: DecisionContext
    options_considered: List[DecisionOption]
    chosen_option: Optional[str]  # option_id of chosen option
    rationale: str
    consequences: DecisionConsequence
    related_decisions: List[str] = field(default_factory=list)  # ADR IDs
    superseded_by: Optional[str] = None  # ADR ID
    implementation_notes: List[str] = field(default_factory=list)
    review_date: Optional[datetime] = None
    tags: List[str] = field(default_factory=list)
    attachments: List[str] = field(default_factory=list)

class ADRSystem(ReflectiveModule):
    """
    Architectural Decision Record system for systematic decision tracking
    Implements UC-18: Decision documentation and historical context preservation
    """
    
    def __init__(self, storage_path: str = ".kiro/adrs"):
        super().__init__("adr_system")
        
        # Storage configuration
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(parents=True, exist_ok=True)
        
        # ADR management
        self.adrs = {}
        self.decision_index = {}  # For fast searching
        self.category_index = {}
        self.stakeholder_index = {}
        
        # Templates and workflows
        self.adr_templates = {}
        self.decision_workflows = {}
        
        # Analytics
        self.adr_metrics = {
            'total_decisions': 0,
            'decisions_by_status': {},
            'decisions_by_category': {},
            'average_decision_time_days': 0.0,
            'implementation_success_rate': 0.0
        }
        
        # Load existing ADRs
        self._load_existing_adrs()
        
        # Initialize default templates
        self._initialize_default_templates()
        
        self._update_health_indicator(
            "adr_system",
            HealthStatus.HEALTHY,
            "operational",
            "ADR system ready for decision documentation"
        )
        
    def get_module_status(self) -> Dict[str, Any]:
        """ADR system operational status"""
        return {
            "module_name": self.module_name,
            "status": "operational" if self.is_healthy() else "degraded",
            "total_adrs": len(self.adrs),
            "active_decisions": len([adr for adr in self.adrs.values() if adr.status == DecisionStatus.PROPOSED]),
            "accepted_decisions": len([adr for adr in self.adrs.values() if adr.status == DecisionStatus.ACCEPTED]),
            "categories_covered": len(self.category_index),
            "storage_path": str(self.storage_path)
        }
        
    def is_healthy(self) -> bool:
        """Health assessment for ADR system"""
        return (
            self.storage_path.exists() and
            not self._degradation_active
        )
        
    def get_health_indicators(self) -> Dict[str, Any]:
        """Detailed health metrics for ADR system"""
        return {
            "storage_status": {
                "path_exists": self.storage_path.exists(),
                "path_writable": self.storage_path.is_dir(),
                "total_files": len(list(self.storage_path.glob("*.json")))
            },
            "decision_metrics": self.adr_metrics,
            "index_status": {
                "decision_index_size": len(self.decision_index),
                "category_index_size": len(self.category_index),
                "stakeholder_index_size": len(self.stakeholder_index)
            }
        }
        
    def _get_primary_responsibility(self) -> str:
        """Single responsibility: architectural decision documentation and tracking"""
        return "architectural_decision_documentation_and_tracking"   
 def create_adr(self, title: str, category: DecisionCategory, 
                  context: DecisionContext, decision_makers: List[str],
                  template_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Create new Architectural Decision Record
        """
        adr_id = f"ADR-{len(self.adrs) + 1:04d}"
        
        # Create ADR from template if specified
        if template_id and template_id in self.adr_templates:
            template = self.adr_templates[template_id]
            adr = self._create_from_template(adr_id, title, category, context, decision_makers, template)
        else:
            adr = ArchitecturalDecisionRecord(
                adr_id=adr_id,
                title=title,
                status=DecisionStatus.PROPOSED,
                category=category,
                date_created=datetime.now(),
                date_decided=None,
                decision_makers=decision_makers,
                context=context,
                options_considered=[],
                chosen_option=None,
                rationale="",
                consequences=DecisionConsequence([], [], [], [], [])
            )
        
        # Store ADR
        self.adrs[adr_id] = adr
        
        # Update indices
        self._update_indices(adr)
        
        # Save to storage
        self._save_adr(adr)
        
        # Update metrics
        self._update_adr_metrics()
        
        self.logger.info(f"ADR created: {title} ({adr_id})")
        
        return {
            "success": True,
            "adr_id": adr_id,
            "title": title,
            "status": adr.status.value,
            "category": category.value
        }
        
    def add_decision_option(self, adr_id: str, option: DecisionOption) -> Dict[str, Any]:
        """
        Add decision option to existing ADR
        """
        if adr_id not in self.adrs:
            return {"error": "ADR not found"}
            
        adr = self.adrs[adr_id]
        
        if adr.status != DecisionStatus.PROPOSED:
            return {"error": "Cannot add options to non-proposed ADR"}
            
        # Validate option
        if not self._validate_decision_option(option):
            return {"error": "Invalid decision option"}
            
        # Add option
        adr.options_considered.append(option)
        
        # Save changes
        self._save_adr(adr)
        
        self.logger.info(f"Decision option added to {adr_id}: {option.title}")
        
        return {
            "success": True,
            "adr_id": adr_id,
            "option_id": option.option_id,
            "total_options": len(adr.options_considered)
        }
        
    def make_decision(self, adr_id: str, chosen_option_id: str, 
                     rationale: str, consequences: DecisionConsequence) -> Dict[str, Any]:
        """
        Make final decision on ADR
        """
        if adr_id not in self.adrs:
            return {"error": "ADR not found"}
            
        adr = self.adrs[adr_id]
        
        if adr.status != DecisionStatus.PROPOSED:
            return {"error": "Decision already made or ADR not in proposed state"}
            
        # Validate chosen option exists
        if not any(opt.option_id == chosen_option_id for opt in adr.options_considered):
            return {"error": "Chosen option not found in considered options"}
            
        # Update ADR
        adr.chosen_option = chosen_option_id
        adr.rationale = rationale
        adr.consequences = consequences
        adr.status = DecisionStatus.ACCEPTED
        adr.date_decided = datetime.now()
        
        # Update indices
        self._update_indices(adr)
        
        # Save changes
        self._save_adr(adr)
        
        # Update metrics
        self._update_adr_metrics()
        
        self.logger.info(f"Decision made for {adr_id}: Option {chosen_option_id} chosen")
        
        return {
            "success": True,
            "adr_id": adr_id,
            "chosen_option": chosen_option_id,
            "status": adr.status.value,
            "decision_date": adr.date_decided.isoformat()
        }
        
    def supersede_adr(self, old_adr_id: str, new_adr_id: str, reason: str) -> Dict[str, Any]:
        """
        Mark ADR as superseded by newer decision
        """
        if old_adr_id not in self.adrs or new_adr_id not in self.adrs:
            return {"error": "One or both ADRs not found"}
            
        old_adr = self.adrs[old_adr_id]
        new_adr = self.adrs[new_adr_id]
        
        # Update old ADR
        old_adr.status = DecisionStatus.SUPERSEDED
        old_adr.superseded_by = new_adr_id
        old_adr.implementation_notes.append(f"Superseded by {new_adr_id}: {reason}")
        
        # Update new ADR
        new_adr.related_decisions.append(old_adr_id)
        
        # Save changes
        self._save_adr(old_adr)
        self._save_adr(new_adr)
        
        # Update indices
        self._update_indices(old_adr)
        self._update_indices(new_adr)
        
        self.logger.info(f"ADR {old_adr_id} superseded by {new_adr_id}")
        
        return {
            "success": True,
            "superseded_adr": old_adr_id,
            "superseding_adr": new_adr_id,
            "reason": reason
        }
        
    def search_adrs(self, query: str, filters: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """
        Search ADRs by text query and filters
        """
        results = []
        filters = filters or {}
        
        for adr in self.adrs.values():
            # Text search
            if query:
                searchable_text = f"{adr.title} {adr.context.problem_statement} {adr.rationale}".lower()
                if query.lower() not in searchable_text:
                    continue
                    
            # Apply filters
            if "status" in filters and adr.status.value not in filters["status"]:
                continue
            if "category" in filters and adr.category.value not in filters["category"]:
                continue
            if "decision_maker" in filters and not any(dm in adr.decision_makers for dm in filters["decision_maker"]):
                continue
            if "tag" in filters and not any(tag in adr.tags for tag in filters["tag"]):
                continue
                
            # Add to results
            results.append({
                "adr_id": adr.adr_id,
                "title": adr.title,
                "status": adr.status.value,
                "category": adr.category.value,
                "date_created": adr.date_created.isoformat(),
                "decision_makers": adr.decision_makers,
                "summary": adr.context.problem_statement[:200] + "..." if len(adr.context.problem_statement) > 200 else adr.context.problem_statement
            })
            
        # Sort by date (newest first)
        results.sort(key=lambda x: x["date_created"], reverse=True)
        
        return results
        
    def get_adr_details(self, adr_id: str) -> Dict[str, Any]:
        """
        Get complete ADR details
        """
        if adr_id not in self.adrs:
            return {"error": "ADR not found"}
            
        adr = self.adrs[adr_id]
        
        return {
            "adr": asdict(adr),
            "related_adrs": [
                {"adr_id": rel_id, "title": self.adrs[rel_id].title}
                for rel_id in adr.related_decisions
                if rel_id in self.adrs
            ],
            "superseding_adr": {
                "adr_id": adr.superseded_by,
                "title": self.adrs[adr.superseded_by].title
            } if adr.superseded_by and adr.superseded_by in self.adrs else None
        }
        
    def generate_adr_report(self, filters: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Generate comprehensive ADR report
        """
        filtered_adrs = []
        filters = filters or {}
        
        for adr in self.adrs.values():
            # Apply filters
            if "status" in filters and adr.status.value not in filters["status"]:
                continue
            if "category" in filters and adr.category.value not in filters["category"]:
                continue
            if "date_range" in filters:
                start_date = datetime.fromisoformat(filters["date_range"]["start"])
                end_date = datetime.fromisoformat(filters["date_range"]["end"])
                if not (start_date <= adr.date_created <= end_date):
                    continue
                    
            filtered_adrs.append(adr)
            
        return {
            "report_generated": datetime.now().isoformat(),
            "total_adrs": len(filtered_adrs),
            "summary_statistics": self._generate_summary_statistics(filtered_adrs),
            "decision_timeline": self._generate_decision_timeline(filtered_adrs),
            "category_breakdown": self._generate_category_breakdown(filtered_adrs),
            "stakeholder_involvement": self._generate_stakeholder_analysis(filtered_adrs),
            "implementation_tracking": self._generate_implementation_tracking(filtered_adrs),
            "recommendations": self._generate_adr_recommendations(filtered_adrs)
        }
        
    def export_adrs(self, format: str = "json", filters: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Export ADRs in specified format
        """
        filtered_adrs = []
        filters = filters or {}
        
        for adr in self.adrs.values():
            # Apply filters (same logic as generate_adr_report)
            if "status" in filters and adr.status.value not in filters["status"]:
                continue
            if "category" in filters and adr.category.value not in filters["category"]:
                continue
                
            filtered_adrs.append(adr)
            
        if format.lower() == "json":
            export_data = [asdict(adr) for adr in filtered_adrs]
            export_content = json.dumps(export_data, indent=2, default=str)
        elif format.lower() == "markdown":
            export_content = self._export_to_markdown(filtered_adrs)
        else:
            return {"error": f"Unsupported export format: {format}"}
            
        return {
            "success": True,
            "format": format,
            "adr_count": len(filtered_adrs),
            "content": export_content,
            "export_timestamp": datetime.now().isoformat()
        }
        
    def get_adr_analytics(self) -> Dict[str, Any]:
        """
        Get comprehensive ADR analytics
        """
        return {
            "overview_metrics": self.adr_metrics,
            "decision_patterns": self._analyze_decision_patterns(),
            "stakeholder_analysis": self._analyze_stakeholder_patterns(),
            "category_trends": self._analyze_category_trends(),
            "implementation_success": self._analyze_implementation_success(),
            "decision_quality_metrics": self._calculate_decision_quality_metrics(),
            "recommendations": self._generate_analytics_recommendations()
        }