"""
Productivity Triage Interfaces
=============================

Base interfaces and abstract classes for the Ghostbusters Productivity Triage system.
These define the contracts that all triage components must follow.

Author: Beast Mode Framework + Ghostbusters
Date: 2025-09-24  
Purpose: Interface definitions for coordinating coordinators
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from .models import (
    WorkArtifact, 
    TriageConfig, 
    ExplosionAssessment,
    IntegrationPlan,
    TriageReport,
    FileConflict,
    DependencyAnalysis,
    CommitGroup,
    QualityResults,
    IntegrationResult,
)


class IContentDiscoveryEngine(ABC):
    """Interface for content discovery engines"""
    
    @abstractmethod
    def scan_workspace(self, config: TriageConfig) -> List[WorkArtifact]:
        """Scan workspace for work artifacts"""
        pass
    
    @abstractmethod
    def analyze_open_files(self) -> List[Dict[str, Any]]:
        """Analyze currently open files for active work"""
        pass
    
    @abstractmethod
    def scan_specs(self, specs_path: str) -> List[Dict[str, Any]]:
        """Scan specification directory for spec status"""
        pass
    
    @abstractmethod
    def analyze_git_status(self) -> Dict[str, Any]:
        """Analyze git repository status"""
        pass


class IWorkClassificationSystem(ABC):
    """Interface for work classification systems"""
    
    @abstractmethod
    def classify_by_domain(self, artifacts: List[WorkArtifact]) -> Dict[str, List[WorkArtifact]]:
        """Classify artifacts by domain"""
        pass
    
    @abstractmethod
    def assess_completion_status(self, artifacts: List[WorkArtifact]) -> Dict[str, Any]:
        """Assess completion status of artifacts"""
        pass
    
    @abstractmethod
    def detect_duplicates(self, artifacts: List[WorkArtifact]) -> Dict[str, List[WorkArtifact]]:
        """Detect duplicate or similar artifacts"""
        pass


class IConflictDetectionEngine(ABC):
    """Interface for conflict detection engines"""
    
    @abstractmethod
    def detect_file_conflicts(self, artifacts: List[WorkArtifact]) -> List[FileConflict]:
        """Detect file-level conflicts between artifacts"""
        pass
    
    @abstractmethod
    def analyze_dependencies(self, artifacts: List[WorkArtifact]) -> DependencyAnalysis:
        """Analyze dependencies between artifacts"""
        pass
    
    @abstractmethod
    def predict_merge_conflicts(self, plan: IntegrationPlan) -> List[Dict[str, Any]]:
        """Predict potential merge conflicts"""
        pass


class IIntegrationPlanningSystem(ABC):
    """Interface for integration planning systems"""
    
    @abstractmethod
    def create_commit_groups(self, artifacts: List[WorkArtifact]) -> List[CommitGroup]:
        """Create logical commit groups from artifacts"""
        pass
    
    @abstractmethod
    def sort_by_dependencies(self, groups: List[CommitGroup]) -> List[CommitGroup]:
        """Sort commit groups by dependency order"""
        pass
    
    @abstractmethod
    def generate_integration_plan(self, groups: List[CommitGroup]) -> IntegrationPlan:
        """Generate comprehensive integration plan"""
        pass


class IQualityGateValidator(ABC):
    """Interface for quality gate validators"""
    
    @abstractmethod
    def run_test_suite(self) -> Dict[str, Any]:
        """Run the existing test suite"""
        pass
    
    @abstractmethod
    def validate_code_quality(self, files: List[str]) -> Dict[str, Any]:
        """Validate code quality for specified files"""
        pass
    
    @abstractmethod
    def check_spec_compliance(self, artifacts: List[WorkArtifact]) -> Dict[str, Any]:
        """Check spec compliance for artifacts"""
        pass


class IEmergencyProtocolManager(ABC):
    """Interface for emergency protocol managers"""
    
    @abstractmethod
    def activate_emergency_protocols(self, reason: str) -> Dict[str, Any]:
        """Activate emergency protocols"""
        pass
    
    @abstractmethod
    def create_emergency_backup(self, artifacts: List[WorkArtifact]) -> str:
        """Create emergency backup of work"""
        pass
    
    @abstractmethod
    def generate_recovery_plan(self, failure_info: Dict[str, Any]) -> Dict[str, Any]:
        """Generate recovery plan for manual intervention"""
        pass


class IProductivityTriageOrchestrator(ABC):
    """Interface for the main productivity triage orchestrator"""
    
    @abstractmethod
    def run_triage(self, config: TriageConfig) -> TriageReport:
        """Run complete productivity triage operation"""
        pass
    
    @abstractmethod
    def assess_productivity_explosion(self, config: TriageConfig) -> ExplosionAssessment:
        """Assess the current productivity explosion situation"""
        pass
    
    @abstractmethod
    def create_integration_plan(self, assessment: ExplosionAssessment) -> IntegrationPlan:
        """Create systematic integration plan"""
        pass
    
    @abstractmethod
    def execute_integration(self, plan: IntegrationPlan) -> List[IntegrationResult]:
        """Execute the integration plan"""
        pass


# Base exception classes for triage operations
class ProductivityTriageError(Exception):
    """Base exception for productivity triage operations"""
    pass


class ContentDiscoveryError(ProductivityTriageError):
    """Error during content discovery"""
    pass


class ClassificationError(ProductivityTriageError):
    """Error during work classification"""
    pass


class ConflictDetectionError(ProductivityTriageError):
    """Error during conflict detection"""
    pass


class IntegrationPlanningError(ProductivityTriageError):
    """Error during integration planning"""
    pass


class QualityGateError(ProductivityTriageError):
    """Error during quality gate validation"""
    pass


class EmergencyProtocolError(ProductivityTriageError):
    """Error during emergency protocol activation"""
    pass


class CriticalTriageError(ProductivityTriageError):
    """Critical error requiring immediate emergency protocols"""
    pass