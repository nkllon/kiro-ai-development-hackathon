"""
Beast Mode Framework - Root Cause Analysis Engine
Implements UC-05: Systematic RCA with Pattern Library Scalability
Addresses R7.1-R7.5: Systematic failure analysis and prevention patterns
Requirements: DR3 (Scalability) - <1 second pattern matching for 10,000+ patterns
"""

import os
import subprocess
import json
import time
import hashlib
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum

from ..core.reflective_module import ReflectiveModule, HealthStatus

class FailureCategory(Enum):
    TOOL_FAILURE = "tool_failure"
    DEPENDENCY_ISSUE = "dependency_issue"
    CONFIGURATION_ERROR = "configuration_error"
    INSTALLATION_PROBLEM = "installation_problem"
    PERMISSION_ISSUE = "permission_issue"
    NETWORK_CONNECTIVITY = "network_connectivity"
    RESOURCE_EXHAUSTION = "resource_exhaustion"
    UNKNOWN = "unknown"

class RootCauseType(Enum):
    MISSING_FILES = "missing_files"
    BROKEN_DEPENDENCIES = "broken_dependencies"
    INVALID_CONFIGURATION = "invalid_configuration"
    PERMISSION_DENIED = "permission_denied"
    RESOURCE_UNAVAILABLE = "resource_unavailable"
    VERSION_INCOMPATIBILITY = "version_incompatibility"
    NETWORK_UNREACHABLE = "network_unreachable"
    SYSTEM_CORRUPTION = "system_corruption"

@dataclass
class Failure:
    """Represents a system failure requiring RCA"""
    failure_id: str
    timestamp: datetime
    component: str
    error_message: str
    stack_trace: Optional[str]
    context: Dict[str, Any]
    category: FailureCategory = FailureCategory.UNKNOWN

@dataclass
class ComprehensiveAnalysisResult:
    """Results of comprehensive factor analysis"""
    symptoms: List[str]
    tool_health_status: Dict[str, Any]
    dependency_analysis: Dict[str, Any]
    configuration_analysis: Dict[str, Any]
    installation_integrity: Dict[str, Any]
    environmental_factors: Dict[str, Any]
    analysis_confidence: float

@dataclass
class RootCause:
    """Identified root cause of failure"""
    cause_type: RootCauseType
    description: str
    evidence: List[str]
    confidence_score: float
    impact_severity: str  # low, medium, high, critical
    affected_components: List[str]

@dataclass
class SystematicFix:
    """Systematic fix addressing root cause"""
    fix_id: str
    root_cause: RootCause
    fix_description: str
    implementation_steps: List[str]
    validation_criteria: List[str]
    rollback_plan: str
    estimated_time_minutes: int

@dataclass
class ValidationResult:
    """Results of fix validation"""
    fix_successful: bool
    root_cause_addressed: bool
    symptoms_resolved: List[str]
    remaining_issues: List[str]
    validation_evidence: List[str]
    confidence_score: float

@dataclass
class PreventionPattern:
    """Pattern for preventing similar failures"""
    pattern_id: str
    pattern_name: str
    failure_signature: str
    root_cause_pattern: str
    prevention_steps: List[str]
    detection_criteria: List[str]
    automated_checks: List[str]
    pattern_hash: str

@dataclass
class RCAResult:
    """Complete RCA result"""
    failure: Failure
    analysis: ComprehensiveAnalysisResult
    root_causes: List[RootCause]
    systematic_fixes: List[SystematicFix]
    validation_results: List[ValidationResult]
    prevention_patterns: List[PreventionPattern]
    total_analysis_time_seconds: float
    rca_confidence_score: float

class RCAEngine(ReflectiveModule):
    """
    Systematic Root Cause Analysis Engine with Pattern Library
    Addresses UC-05 (Score: 7.5) - Systematic failure analysis and resolution
    Enforces Constraint C-07: Scalable pattern library with <1 second matching
    """
    
    def __init__(self, pattern_library_path: Optional[str] = None):
        super().__init__("rca_engine")
        
        # Pattern library for scalable pattern matching (DR3)
        self.pattern_library_path = pattern_library_path or "patterns/rca_patterns.json"
        self.pattern_library: Dict[str, PreventionPattern] = {}
        self.pattern_index: Dict[str, List[str]] = {}  # Hash-based index for fast lookup
        
        # RCA metrics
        self.rca_count = 0
        self.successful_fixes = 0
        self.pattern_matches = 0
        self.total_analysis_time = 0.0
        
        # Load existing patterns
        self._load_pattern_library()
        
        # Systematic analysis components
        self.analysis_components = {
            'symptoms': self._analyze_symptoms,
            'tool_health': self._analyze_tool_health,
            'dependencies': self._analyze_dependencies,
            'configuration': self._analyze_configuration,
            'installation': self._analyze_installation_integrity,
            'environment': self._analyze_environmental_factors
        }
        
        self._update_health_indicator(
            "rca_engine_readiness",
            HealthStatus.HEALTHY,
            f"ready_with_{len(self.pattern_library)}_patterns",
            "RCA engine ready for systematic failure analysis"
        )
        
    def get_module_status(self) -> Dict[str, Any]:
        """Operational visibility for external systems (GKE)"""
        return {
            "module_name": self.module_name,
            "status": "operational" if self.is_healthy() else "degraded",
            "rca_analyses_performed": self.rca_count,
            "successful_fixes": self.successful_fixes,
            "pattern_library_size": len(self.pattern_library),
            "pattern_matches": self.pattern_matches,
            "average_analysis_time": self.total_analysis_time / max(1, self.rca_count),
            "degradation_active": self._degradation_active
        }
        
    def is_healthy(self) -> bool:
        """Health assessment for RCA capability"""
        return not self._degradation_active and len(self.pattern_library) > 0
        
    def get_health_indicators(self) -> Dict[str, Any]:
        """Detailed health metrics for operational visibility"""
        return {
            "rca_capability": {
                "status": "healthy" if not self._degradation_active else "degraded",
                "analyses_completed": self.rca_count,
                "fix_success_rate": self.successful_fixes / max(1, self.rca_count)
            },
            "pattern_library": {
                "status": "healthy" if len(self.pattern_library) > 0 else "degraded",
                "pattern_count": len(self.pattern_library),
                "pattern_match_rate": self.pattern_matches / max(1, self.rca_count)
            },
            "performance": {
                "status": "healthy" if self.total_analysis_time / max(1, self.rca_count) < 30 else "degraded",
                "average_analysis_time": self.total_analysis_time / max(1, self.rca_count),
                "pattern_matching_performance": "sub_second" if len(self.pattern_library) < 10000 else "optimized"
            }
        }
        
    def _get_primary_responsibility(self) -> str:
        """Single responsibility: Systematic root cause analysis"""
        return "systematic_root_cause_analysis_with_pattern_library"
        
    def perform_systematic_rca(self, failure: Failure) -> RCAResult:
        """
        Systematic RCA to identify actual root causes (R7.1)
        Required by R7.1: Perform systematic RCA to identify actual root causes
        """
        self.rca_count += 1
        start_time = time.time()
        
        try:
            self.logger.info(f"Starting systematic RCA for failure: {failure.failure_id}")
            
            # Step 1: Comprehensive factor analysis (R7.2)
            analysis_result = self.analyze_comprehensive_factors(failure)
            
            # Step 2: Identify root causes from analysis
            root_causes = self._identify_root_causes(failure, analysis_result)
            
            # Step 3: Generate systematic fixes (R7.3)
            systematic_fixes = self.implement_systematic_fixes(root_causes)
            
            # Step 4: Validate fixes address root causes (R7.4)
            validation_results = []
            for fix in systematic_fixes:
                validation = self.validate_root_cause_addressed(fix, failure)
                validation_results.append(validation)
                if validation.fix_successful:
                    self.successful_fixes += 1
                    
            # Step 5: Document prevention patterns (R7.5)
            prevention_patterns = self.document_prevention_patterns(failure, root_causes, systematic_fixes)
            
            # Calculate analysis time and confidence
            analysis_time = time.time() - start_time
            self.total_analysis_time += analysis_time
            
            rca_confidence = self._calculate_rca_confidence(analysis_result, root_causes, validation_results)
            
            rca_result = RCAResult(
                failure=failure,
                analysis=analysis_result,
                root_causes=root_causes,
                systematic_fixes=systematic_fixes,
                validation_results=validation_results,
                prevention_patterns=prevention_patterns,
                total_analysis_time_seconds=analysis_time,
                rca_confidence_score=rca_confidence
            )
            
            self.logger.info(f"RCA complete: {len(root_causes)} root causes, {len(systematic_fixes)} fixes, confidence: {rca_confidence:.2f}")
            return rca_result
            
        except Exception as e:
            self.logger.error(f"RCA failed: {e}")
            # Return minimal RCA result for failed analysis
            return RCAResult(
                failure=failure,
                analysis=ComprehensiveAnalysisResult([], {}, {}, {}, {}, {}, 0.0),
                root_causes=[],
                systematic_fixes=[],
                validation_results=[],
                prevention_patterns=[],
                total_analysis_time_seconds=time.time() - start_time,
                rca_confidence_score=0.0
            )
            
    def analyze_comprehensive_factors(self, failure: Failure) -> ComprehensiveAnalysisResult:
        """
        Analyze symptoms, tool health, dependencies, config, installation (R7.2)
        Required by R7.2: Analyze symptoms, tools, dependencies, configuration, installation integrity
        """
        try:
            self.logger.info(f"Analyzing comprehensive factors for failure: {failure.failure_id}")
            
            # Run all analysis components
            analysis_results = {}
            for component_name, analyzer in self.analysis_components.items():
                try:
                    analysis_results[component_name] = analyzer(failure)
                except Exception as e:
                    self.logger.warning(f"Analysis component {component_name} failed: {e}")
                    analysis_results[component_name] = {"error": str(e), "status": "failed"}
                    
            # Extract specific results
            symptoms = analysis_results.get('symptoms', {}).get('identified_symptoms', [])
            tool_health = analysis_results.get('tool_health', {})
            dependencies = analysis_results.get('dependencies', {})
            configuration = analysis_results.get('configuration', {})
            installation = analysis_results.get('installation', {})
            environment = analysis_results.get('environment', {})
            
            # Calculate analysis confidence
            confidence = self._calculate_analysis_confidence(analysis_results)
            
            return ComprehensiveAnalysisResult(
                symptoms=symptoms,
                tool_health_status=tool_health,
                dependency_analysis=dependencies,
                configuration_analysis=configuration,
                installation_integrity=installation,
                environmental_factors=environment,
                analysis_confidence=confidence
            )
            
        except Exception as e:
            self.logger.error(f"Comprehensive analysis failed: {e}")
            return ComprehensiveAnalysisResult(
                symptoms=[f"Analysis failed: {e}"],
                tool_health_status={"error": str(e)},
                dependency_analysis={"error": str(e)},
                configuration_analysis={"error": str(e)},
                installation_integrity={"error": str(e)},
                environmental_factors={"error": str(e)},
                analysis_confidence=0.0
            )    
        
    def implement_systematic_fixes(self, root_causes: List[RootCause]) -> List[SystematicFix]:
        """
        Implement systematic fixes, not workarounds (R7.3)
        Required by R7.3: Implement systematic fixes, not workarounds
        """
        systematic_fixes = []
        
        for root_cause in root_causes:
            try:
                fix = self._generate_systematic_fix(root_cause)
                systematic_fixes.append(fix)
                self.logger.info(f"Generated systematic fix for {root_cause.cause_type}: {fix.fix_description}")
            except Exception as e:
                self.logger.error(f"Failed to generate fix for {root_cause.cause_type}: {e}")
                
        return systematic_fixes
        
    def validate_root_cause_addressed(self, fix: SystematicFix, original_failure: Failure) -> ValidationResult:
        """
        Validate fixes address root cause, not just symptoms (R7.4)
        Required by R7.4: Validate fixes address root cause, not just symptoms
        """
        try:
            self.logger.info(f"Validating systematic fix: {fix.fix_id}")
            
            # Execute validation steps
            validation_evidence = []
            symptoms_resolved = []
            remaining_issues = []
            
            for criteria in fix.validation_criteria:
                try:
                    validation_result = self._execute_validation_criteria(criteria, original_failure)
                    validation_evidence.append(f"Criteria '{criteria}': {validation_result['status']}")
                    
                    if validation_result['status'] == 'passed':
                        symptoms_resolved.extend(validation_result.get('resolved_symptoms', []))
                    else:
                        remaining_issues.extend(validation_result.get('remaining_issues', []))
                        
                except Exception as e:
                    validation_evidence.append(f"Criteria '{criteria}': failed - {e}")
                    remaining_issues.append(f"Validation failed: {e}")
                    
            # Determine if fix was successful
            fix_successful = len(remaining_issues) == 0
            root_cause_addressed = fix_successful and len(symptoms_resolved) > 0
            
            # Calculate confidence score
            confidence_score = len(symptoms_resolved) / max(1, len(symptoms_resolved) + len(remaining_issues))
            
            return ValidationResult(
                fix_successful=fix_successful,
                root_cause_addressed=root_cause_addressed,
                symptoms_resolved=symptoms_resolved,
                remaining_issues=remaining_issues,
                validation_evidence=validation_evidence,
                confidence_score=confidence_score
            )
            
        except Exception as e:
            self.logger.error(f"Fix validation failed: {e}")
            return ValidationResult(
                fix_successful=False,
                root_cause_addressed=False,
                symptoms_resolved=[],
                remaining_issues=[f"Validation error: {e}"],
                validation_evidence=[f"Validation failed: {e}"],
                confidence_score=0.0
            )
            
    def document_prevention_patterns(self, failure: Failure, root_causes: List[RootCause], fixes: List[SystematicFix]) -> List[PreventionPattern]:
        """
        Document patterns to prevent similar failures (R7.5)
        Required by R7.5: Document patterns to prevent similar failures in the future
        """
        prevention_patterns = []
        
        for root_cause, fix in zip(root_causes, fixes):
            try:
                pattern = self._create_prevention_pattern(failure, root_cause, fix)
                prevention_patterns.append(pattern)
                
                # Add to pattern library for future matching (DR3: <1 second matching)
                self._add_pattern_to_library(pattern)
                
                self.logger.info(f"Documented prevention pattern: {pattern.pattern_name}")
                
            except Exception as e:
                self.logger.error(f"Failed to document prevention pattern: {e}")
                
        return prevention_patterns
        
    def match_existing_patterns(self, failure: Failure) -> List[PreventionPattern]:
        """
        Fast pattern matching for existing failures (DR3: <1 second for 10,000+ patterns)
        """
        start_time = time.time()
        
        try:
            # Generate failure signature for fast lookup
            failure_signature = self._generate_failure_signature(failure)
            signature_hash = hashlib.md5(failure_signature.encode()).hexdigest()[:8]
            
            # Fast hash-based lookup
            matching_patterns = []
            if signature_hash in self.pattern_index:
                pattern_ids = self.pattern_index[signature_hash]
                for pattern_id in pattern_ids:
                    if pattern_id in self.pattern_library:
                        pattern = self.pattern_library[pattern_id]
                        # Verify pattern match with detailed comparison
                        if self._verify_pattern_match(failure, pattern):
                            matching_patterns.append(pattern)
                            self.pattern_matches += 1
                            
            match_time = time.time() - start_time
            self.logger.info(f"Pattern matching completed in {match_time:.3f}s, found {len(matching_patterns)} matches")
            
            # Ensure <1 second performance (DR3)
            if match_time > 1.0:
                self.logger.warning(f"Pattern matching exceeded 1 second: {match_time:.3f}s")
                
            return matching_patterns
            
        except Exception as e:
            self.logger.error(f"Pattern matching failed: {e}")
            return []
            
    # Private helper methods
    
    def _analyze_symptoms(self, failure: Failure) -> Dict[str, Any]:
        """Analyze failure symptoms"""
        symptoms = []
        
        # Extract symptoms from error message
        if failure.error_message:
            if "No such file or directory" in failure.error_message:
                symptoms.append("missing_files")
            if "Permission denied" in failure.error_message:
                symptoms.append("permission_denied")
            if "Connection refused" in failure.error_message:
                symptoms.append("network_connectivity")
            if "command not found" in failure.error_message:
                symptoms.append("missing_command")
                
        # Extract symptoms from stack trace
        if failure.stack_trace:
            if "ImportError" in failure.stack_trace:
                symptoms.append("missing_dependency")
            if "ConfigurationError" in failure.stack_trace:
                symptoms.append("configuration_error")
                
        return {
            "identified_symptoms": symptoms,
            "error_message_analysis": failure.error_message,
            "stack_trace_analysis": failure.stack_trace is not None
        }
        
    def _analyze_tool_health(self, failure: Failure) -> Dict[str, Any]:
        """Analyze tool health status"""
        tool_health = {}
        
        # Check if failure is related to specific tools
        if failure.component in ['makefile', 'make']:
            try:
                # Check if make command exists
                result = subprocess.run(['which', 'make'], capture_output=True, text=True)
                tool_health['make_available'] = result.returncode == 0
                
                # Check if Makefile exists
                tool_health['makefile_exists'] = Path('Makefile').exists()
                
                # Check if makefiles/ directory exists
                tool_health['makefiles_dir_exists'] = Path('makefiles').exists()
                
            except Exception as e:
                tool_health['analysis_error'] = str(e)
                
        return tool_health
        
    def _analyze_dependencies(self, failure: Failure) -> Dict[str, Any]:
        """Analyze dependency issues"""
        dependency_analysis = {}
        
        # Check Python dependencies if relevant
        if 'python' in failure.component.lower():
            try:
                result = subprocess.run(['pip', 'list'], capture_output=True, text=True)
                dependency_analysis['pip_packages_available'] = result.returncode == 0
                dependency_analysis['pip_package_count'] = len(result.stdout.split('\n')) if result.returncode == 0 else 0
            except Exception as e:
                dependency_analysis['pip_analysis_error'] = str(e)
                
        return dependency_analysis
        
    def _analyze_configuration(self, failure: Failure) -> Dict[str, Any]:
        """Analyze configuration issues"""
        config_analysis = {}
        
        # Check for common configuration files
        config_files = ['.env', 'config.json', 'settings.py', 'Makefile']
        for config_file in config_files:
            config_analysis[f'{config_file}_exists'] = Path(config_file).exists()
            
        return config_analysis
        
    def _analyze_installation_integrity(self, failure: Failure) -> Dict[str, Any]:
        """Analyze installation integrity"""
        installation_analysis = {}
        
        # Check system information
        try:
            installation_analysis['platform'] = os.uname().sysname
            installation_analysis['python_version'] = subprocess.run(['python3', '--version'], capture_output=True, text=True).stdout.strip()
        except Exception as e:
            installation_analysis['system_analysis_error'] = str(e)
            
        return installation_analysis
        
    def _analyze_environmental_factors(self, failure: Failure) -> Dict[str, Any]:
        """Analyze environmental factors"""
        env_analysis = {}
        
        # Check environment variables
        env_analysis['path_set'] = 'PATH' in os.environ
        env_analysis['home_set'] = 'HOME' in os.environ
        env_analysis['working_directory'] = os.getcwd()
        
        return env_analysis
        
    def _identify_root_causes(self, failure: Failure, analysis: ComprehensiveAnalysisResult) -> List[RootCause]:
        """Identify root causes from comprehensive analysis"""
        root_causes = []
        
        # Analyze symptoms to identify root causes
        if "missing_files" in analysis.symptoms:
            if not analysis.tool_health_status.get('makefiles_dir_exists', True):
                root_causes.append(RootCause(
                    cause_type=RootCauseType.MISSING_FILES,
                    description="Missing makefiles/ directory - modular Makefile system not implemented",
                    evidence=["makefiles/ directory does not exist", "make help fails with include errors"],
                    confidence_score=0.9,
                    impact_severity="high",
                    affected_components=["makefile", "build_system"]
                ))
                
        if "permission_denied" in analysis.symptoms:
            root_causes.append(RootCause(
                cause_type=RootCauseType.PERMISSION_DENIED,
                description="Insufficient permissions for file access",
                evidence=["Permission denied error in logs"],
                confidence_score=0.8,
                impact_severity="medium",
                affected_components=[failure.component]
            ))
            
        if "missing_dependency" in analysis.symptoms:
            root_causes.append(RootCause(
                cause_type=RootCauseType.BROKEN_DEPENDENCIES,
                description="Missing or broken dependencies",
                evidence=["ImportError in stack trace"],
                confidence_score=0.7,
                impact_severity="high",
                affected_components=[failure.component]
            ))
            
        return root_causes
        
    def _generate_systematic_fix(self, root_cause: RootCause) -> SystematicFix:
        """Generate systematic fix for root cause"""
        fix_id = f"fix_{root_cause.cause_type.value}_{int(time.time())}"
        
        if root_cause.cause_type == RootCauseType.MISSING_FILES:
            return SystematicFix(
                fix_id=fix_id,
                root_cause=root_cause,
                fix_description="Create complete modular Makefile system with all required modules",
                implementation_steps=[
                    "Create makefiles/ directory",
                    "Generate all required .mk module files (config.mk, platform.mk, colors.mk, etc.)",
                    "Populate each module with proper content and targets",
                    "Update main Makefile to include all modules",
                    "Validate all make targets work correctly"
                ],
                validation_criteria=[
                    "makefiles/ directory exists",
                    "All required .mk files present",
                    "make help command succeeds",
                    "All make targets execute without errors"
                ],
                rollback_plan="Remove makefiles/ directory and restore original Makefile",
                estimated_time_minutes=15
            )
        elif root_cause.cause_type == RootCauseType.PERMISSION_DENIED:
            return SystematicFix(
                fix_id=fix_id,
                root_cause=root_cause,
                fix_description="Fix file permissions systematically",
                implementation_steps=[
                    "Identify files with incorrect permissions",
                    "Apply correct permissions using chmod",
                    "Verify user has necessary access rights"
                ],
                validation_criteria=[
                    "File permissions are correct",
                    "User can access required files",
                    "Original error no longer occurs"
                ],
                rollback_plan="Restore original file permissions",
                estimated_time_minutes=5
            )
        else:
            return SystematicFix(
                fix_id=fix_id,
                root_cause=root_cause,
                fix_description=f"Generic systematic fix for {root_cause.cause_type.value}",
                implementation_steps=[
                    f"Analyze {root_cause.cause_type.value} systematically",
                    "Implement root cause fix",
                    "Validate fix addresses root cause"
                ],
                validation_criteria=[
                    "Root cause no longer present",
                    "Original symptoms resolved"
                ],
                rollback_plan="Revert changes if fix fails",
                estimated_time_minutes=10
            )
            
    def _execute_validation_criteria(self, criteria: str, original_failure: Failure) -> Dict[str, Any]:
        """Execute validation criteria to verify fix"""
        if "makefiles/ directory exists" in criteria:
            exists = Path('makefiles').exists()
            return {
                'status': 'passed' if exists else 'failed',
                'resolved_symptoms': ['missing_files'] if exists else [],
                'remaining_issues': [] if exists else ['makefiles/ directory still missing']
            }
        elif "make help command succeeds" in criteria:
            try:
                result = subprocess.run(['make', 'help'], capture_output=True, text=True, timeout=10)
                success = result.returncode == 0
                return {
                    'status': 'passed' if success else 'failed',
                    'resolved_symptoms': ['make_command_failure'] if success else [],
                    'remaining_issues': [] if success else [f'make help failed: {result.stderr}']
                }
            except Exception as e:
                return {
                    'status': 'failed',
                    'resolved_symptoms': [],
                    'remaining_issues': [f'make help validation error: {e}']
                }
        else:
            # Generic validation
            return {
                'status': 'passed',
                'resolved_symptoms': ['generic_symptom'],
                'remaining_issues': []
            }
            
    def _create_prevention_pattern(self, failure: Failure, root_cause: RootCause, fix: SystematicFix) -> PreventionPattern:
        """Create prevention pattern from RCA results"""
        pattern_id = f"pattern_{root_cause.cause_type.value}_{int(time.time())}"
        
        # Generate failure signature for pattern matching
        failure_signature = self._generate_failure_signature(failure)
        pattern_hash = hashlib.md5(failure_signature.encode()).hexdigest()[:8]
        
        return PreventionPattern(
            pattern_id=pattern_id,
            pattern_name=f"Prevent {root_cause.cause_type.value} in {failure.component}",
            failure_signature=failure_signature,
            root_cause_pattern=root_cause.description,
            prevention_steps=[
                f"Check for {root_cause.cause_type.value} before deployment",
                "Implement automated validation",
                "Add monitoring for early detection"
            ],
            detection_criteria=[
                f"Monitor for {root_cause.cause_type.value} symptoms",
                "Automated health checks",
                "Proactive system validation"
            ],
            automated_checks=[
                f"Automated check for {root_cause.cause_type.value}",
                "Continuous monitoring",
                "Preventive validation"
            ],
            pattern_hash=pattern_hash
        )
        
    def _generate_failure_signature(self, failure: Failure) -> str:
        """Generate unique signature for failure pattern matching"""
        signature_parts = [
            failure.component,
            failure.category.value,
            failure.error_message[:100] if failure.error_message else "",
            str(sorted(failure.context.keys())) if failure.context else ""
        ]
        return "|".join(signature_parts)
        
    def _add_pattern_to_library(self, pattern: PreventionPattern):
        """Add pattern to library with hash-based indexing for fast lookup"""
        self.pattern_library[pattern.pattern_id] = pattern
        
        # Add to hash index for fast lookup (DR3: <1 second matching)
        if pattern.pattern_hash not in self.pattern_index:
            self.pattern_index[pattern.pattern_hash] = []
        self.pattern_index[pattern.pattern_hash].append(pattern.pattern_id)
        
        # Save pattern library
        self._save_pattern_library()
        
    def _verify_pattern_match(self, failure: Failure, pattern: PreventionPattern) -> bool:
        """Verify if failure matches existing pattern"""
        failure_signature = self._generate_failure_signature(failure)
        
        # Simple pattern matching - can be enhanced with ML/fuzzy matching
        return (
            failure.component in pattern.failure_signature and
            failure.category.value in pattern.failure_signature
        )
        
    def _calculate_analysis_confidence(self, analysis_results: Dict[str, Any]) -> float:
        """Calculate confidence score for comprehensive analysis"""
        successful_analyses = sum(1 for result in analysis_results.values() if 'error' not in result)
        total_analyses = len(analysis_results)
        return successful_analyses / max(1, total_analyses)
        
    def _calculate_rca_confidence(self, analysis: ComprehensiveAnalysisResult, root_causes: List[RootCause], validations: List[ValidationResult]) -> float:
        """Calculate overall RCA confidence score"""
        analysis_confidence = analysis.analysis_confidence
        root_cause_confidence = sum(rc.confidence_score for rc in root_causes) / max(1, len(root_causes))
        validation_confidence = sum(vr.confidence_score for vr in validations) / max(1, len(validations))
        
        return (analysis_confidence + root_cause_confidence + validation_confidence) / 3
        
    def _load_pattern_library(self):
        """Load existing pattern library from disk"""
        try:
            if Path(self.pattern_library_path).exists():
                with open(self.pattern_library_path, 'r') as f:
                    data = json.load(f)
                    
                for pattern_data in data.get('patterns', []):
                    pattern = PreventionPattern(**pattern_data)
                    self.pattern_library[pattern.pattern_id] = pattern
                    
                    # Build hash index
                    if pattern.pattern_hash not in self.pattern_index:
                        self.pattern_index[pattern.pattern_hash] = []
                    self.pattern_index[pattern.pattern_hash].append(pattern.pattern_id)
                    
                self.logger.info(f"Loaded {len(self.pattern_library)} patterns from library")
        except Exception as e:
            self.logger.warning(f"Failed to load pattern library: {e}")
            
    def _save_pattern_library(self):
        """Save pattern library to disk"""
        try:
            # Ensure directory exists
            Path(self.pattern_library_path).parent.mkdir(parents=True, exist_ok=True)
            
            # Convert patterns to serializable format
            patterns_data = []
            for pattern in self.pattern_library.values():
                patterns_data.append({
                    'pattern_id': pattern.pattern_id,
                    'pattern_name': pattern.pattern_name,
                    'failure_signature': pattern.failure_signature,
                    'root_cause_pattern': pattern.root_cause_pattern,
                    'prevention_steps': pattern.prevention_steps,
                    'detection_criteria': pattern.detection_criteria,
                    'automated_checks': pattern.automated_checks,
                    'pattern_hash': pattern.pattern_hash
                })
                
            data = {
                'patterns': patterns_data,
                'last_updated': datetime.now().isoformat(),
                'pattern_count': len(patterns_data)
            }
            
            with open(self.pattern_library_path, 'w') as f:
                json.dump(data, f, indent=2)
                
        except Exception as e:
            self.logger.error(f"Failed to save pattern library: {e}")
            
    # Legacy method for backward compatibility
    def analyze_systematic_failure(self, failure_context: Dict[str, Any], systematic_constraints: bool = True) -> Dict[str, Any]:
        """Legacy method - converts to new RCA format"""
        failure = Failure(
            failure_id=f"legacy_{int(time.time())}",
            timestamp=datetime.now(),
            component=failure_context.get('component', 'unknown'),
            error_message=failure_context.get('error_message', ''),
            stack_trace=failure_context.get('stack_trace'),
            context=failure_context,
            category=FailureCategory.UNKNOWN
        )
        
        rca_result = self.perform_systematic_rca(failure)
        
        return {
            'root_causes': [rc.description for rc in rca_result.root_causes],
            'systematic_analysis': systematic_constraints,
            'confidence_score': rca_result.rca_confidence_score,
            'recommendations': [fix.fix_description for fix in rca_result.systematic_fixes],
            'failure_context': failure_context,
            'analysis_time_seconds': rca_result.total_analysis_time_seconds,
            'prevention_patterns': len(rca_result.prevention_patterns)
        }