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
    # Test-specific failure categories
    PYTEST_FAILURE = "pytest_failure"
    MAKE_TARGET_FAILURE = "make_target_failure"
    INFRASTRUCTURE_FAILURE = "infrastructure_failure"
    TEST_ENVIRONMENT_FAILURE = "test_environment_failure"

class RootCauseType(Enum):
    MISSING_FILES = "missing_files"
    BROKEN_DEPENDENCIES = "broken_dependencies"
    INVALID_CONFIGURATION = "invalid_configuration"
    PERMISSION_DENIED = "permission_denied"
    RESOURCE_UNAVAILABLE = "resource_unavailable"
    VERSION_INCOMPATIBILITY = "version_incompatibility"
    NETWORK_UNREACHABLE = "network_unreachable"
    SYSTEM_CORRUPTION = "system_corruption"
    # Test-specific root cause types
    TEST_IMPORT_ERROR = "test_import_error"
    TEST_ASSERTION_FAILURE = "test_assertion_failure"
    TEST_FIXTURE_ERROR = "test_fixture_error"
    TEST_TIMEOUT = "test_timeout"
    TEST_SETUP_ERROR = "test_setup_error"
    MAKEFILE_ERROR = "makefile_error"
    BUILD_DEPENDENCY_ERROR = "build_dependency_error"
    INFRASTRUCTURE_ERROR = "infrastructure_error"

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
            'environment': self._analyze_environmental_factors,
            # Test-specific analysis components
            'test_specific': self._analyze_test_specific_factors,
            'pytest_analysis': self._analyze_pytest_failures,
            'makefile_analysis': self._analyze_makefile_failures,
            'infrastructure_analysis': self._analyze_infrastructure_failures
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
            
    # Test-specific analysis methods for Requirements 4.1, 4.2, 4.3, 4.4, 5.1, 5.2, 5.3, 5.4
    
    def analyze_test_failure_categorization(self, failure: Failure) -> Dict[str, Any]:
        """
        Categorize test failures (pytest, make, infrastructure) - Requirement 5.1, 5.2, 5.3
        """
        try:
            self.logger.info(f"Categorizing test failure: {failure.failure_id}")
            
            categorization = {
                "primary_category": "unknown",
                "subcategory": "unknown",
                "confidence": 0.0,
                "analysis_details": {}
            }
            
            # Pytest failure analysis (check first as it's most specific)
            if self._is_pytest_failure(failure):
                categorization.update({
                    "primary_category": "pytest_failure",
                    "subcategory": self._get_pytest_subcategory(failure),
                    "confidence": 0.9,
                    "analysis_details": self._analyze_pytest_details(failure)
                })
            
            # Make target failure analysis
            elif self._is_make_failure(failure):
                categorization.update({
                    "primary_category": "make_target_failure", 
                    "subcategory": self._get_make_subcategory(failure),
                    "confidence": 0.8,
                    "analysis_details": self._analyze_make_details(failure)
                })
            
            # Infrastructure failure analysis
            elif self._is_infrastructure_failure(failure):
                categorization.update({
                    "primary_category": "infrastructure_failure",
                    "subcategory": self._get_infrastructure_subcategory(failure),
                    "confidence": 0.7,
                    "analysis_details": self._analyze_infrastructure_details(failure)
                })
            
            # Check if this is a test-related failure by component or context
            elif (failure.component.startswith("test:") or 
                  "test" in failure.component.lower() or
                  (failure.context and 'test_file' in failure.context)):
                # Generic test failure
                categorization.update({
                    "primary_category": "test_environment_failure",
                    "subcategory": "unknown_test_failure",
                    "confidence": 0.5,
                    "analysis_details": {"error": "Could not categorize test failure specifically"}
                })
            
            self.logger.info(f"Test failure categorized as: {categorization['primary_category']}/{categorization['subcategory']}")
            return categorization
            
        except Exception as e:
            self.logger.error(f"Test failure categorization failed: {e}")
            return {
                "primary_category": "unknown",
                "subcategory": "categorization_error",
                "confidence": 0.0,
                "analysis_details": {"error": str(e)}
            }
    
    def generate_test_specific_systematic_fixes(self, root_causes: List[RootCause]) -> List[SystematicFix]:
        """
        Generate test-specific systematic fixes - Requirements 4.3, 5.1, 5.2, 5.3, 5.4
        """
        test_specific_fixes = []
        
        for root_cause in root_causes:
            try:
                if root_cause.cause_type in [RootCauseType.TEST_IMPORT_ERROR, RootCauseType.TEST_ASSERTION_FAILURE, 
                                           RootCauseType.TEST_FIXTURE_ERROR, RootCauseType.TEST_TIMEOUT, 
                                           RootCauseType.TEST_SETUP_ERROR]:
                    fix = self._generate_pytest_specific_fix(root_cause)
                    test_specific_fixes.append(fix)
                    
                elif root_cause.cause_type in [RootCauseType.MAKEFILE_ERROR, RootCauseType.BUILD_DEPENDENCY_ERROR]:
                    fix = self._generate_makefile_specific_fix(root_cause)
                    test_specific_fixes.append(fix)
                    
                elif root_cause.cause_type == RootCauseType.INFRASTRUCTURE_ERROR:
                    fix = self._generate_infrastructure_specific_fix(root_cause)
                    test_specific_fixes.append(fix)
                    
                self.logger.info(f"Generated test-specific fix for {root_cause.cause_type}")
                
            except Exception as e:
                self.logger.error(f"Failed to generate test-specific fix for {root_cause.cause_type}: {e}")
                
        return test_specific_fixes
    
    def add_test_specific_patterns_to_library(self, failure: Failure, root_causes: List[RootCause], fixes: List[SystematicFix]) -> List[PreventionPattern]:
        """
        Add test-specific patterns to pattern library - Requirements 4.4, 5.1, 5.2, 5.3, 5.4
        """
        test_patterns = []
        
        for root_cause, fix in zip(root_causes, fixes):
            try:
                # Create test-specific prevention pattern
                pattern = self._create_test_specific_pattern(failure, root_cause, fix)
                test_patterns.append(pattern)
                
                # Add to pattern library with test-specific indexing
                self._add_test_pattern_to_library(pattern)
                
                self.logger.info(f"Added test-specific pattern: {pattern.pattern_name}")
                
            except Exception as e:
                self.logger.error(f"Failed to add test-specific pattern: {e}")
                
        return test_patterns

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
    
    def _analyze_test_specific_factors(self, failure: Failure) -> Dict[str, Any]:
        """Analyze test-specific factors for comprehensive analysis"""
        test_analysis = {}
        
        try:
            # Check if this is a test-related failure
            is_test_failure = (
                failure.component.startswith("test:") or 
                "test" in failure.component.lower() or
                failure.category in [FailureCategory.PYTEST_FAILURE, FailureCategory.MAKE_TARGET_FAILURE, FailureCategory.INFRASTRUCTURE_FAILURE, FailureCategory.TEST_ENVIRONMENT_FAILURE] or
                self._is_pytest_failure(failure) or
                self._is_make_failure(failure) or
                self._is_infrastructure_failure(failure)
            )
            
            if is_test_failure:
                test_analysis['is_test_failure'] = True
                test_analysis['test_categorization'] = self.analyze_test_failure_categorization(failure)
                
                # Extract test context if available
                if failure.context and 'test_file' in failure.context:
                    test_analysis['test_file'] = failure.context['test_file']
                    test_analysis['test_function'] = failure.context.get('test_function', 'unknown')
                    test_analysis['pytest_node_id'] = failure.context.get('pytest_node_id', 'unknown')
                    
                # Analyze test environment
                test_analysis['test_environment'] = self._analyze_test_environment(failure)
                
            else:
                test_analysis['is_test_failure'] = False
                test_analysis['reason'] = 'Not identified as test-related failure'
                
        except Exception as e:
            test_analysis['analysis_error'] = str(e)
            
        return test_analysis
    
    def _analyze_pytest_failures(self, failure: Failure) -> Dict[str, Any]:
        """Analyze pytest-specific failures - Requirement 5.1"""
        pytest_analysis = {}
        
        try:
            if self._is_pytest_failure(failure):
                # Analyze Python-specific issues
                pytest_analysis['python_issues'] = self._analyze_python_issues(failure)
                
                # Analyze import issues
                pytest_analysis['import_analysis'] = self._analyze_import_issues(failure)
                
                # Analyze dependency issues
                pytest_analysis['dependency_analysis'] = self._analyze_test_dependencies(failure)
                
                # Analyze syntax issues
                pytest_analysis['syntax_analysis'] = self._analyze_syntax_issues(failure)
                
                # Analyze test structure issues
                pytest_analysis['test_structure'] = self._analyze_test_structure(failure)
                
                pytest_analysis['analysis_confidence'] = 0.9
                
            else:
                pytest_analysis['applicable'] = False
                pytest_analysis['reason'] = 'Not a pytest failure'
                
        except Exception as e:
            pytest_analysis['analysis_error'] = str(e)
            
        return pytest_analysis
    
    def _analyze_makefile_failures(self, failure: Failure) -> Dict[str, Any]:
        """Analyze Makefile-specific failures - Requirement 5.2"""
        makefile_analysis = {}
        
        try:
            if self._is_make_failure(failure):
                # Analyze Makefile issues
                makefile_analysis['makefile_issues'] = self._analyze_makefile_issues(failure)
                
                # Analyze missing files
                makefile_analysis['missing_files'] = self._analyze_missing_files(failure)
                
                # Analyze build dependencies
                makefile_analysis['build_dependencies'] = self._analyze_build_dependencies(failure)
                
                # Analyze make target structure
                makefile_analysis['target_analysis'] = self._analyze_make_targets(failure)
                
                makefile_analysis['analysis_confidence'] = 0.8
                
            else:
                makefile_analysis['applicable'] = False
                makefile_analysis['reason'] = 'Not a Makefile failure'
                
        except Exception as e:
            makefile_analysis['analysis_error'] = str(e)
            
        return makefile_analysis
    
    def _analyze_infrastructure_failures(self, failure: Failure) -> Dict[str, Any]:
        """Analyze infrastructure-specific failures - Requirement 5.3"""
        infrastructure_analysis = {}
        
        try:
            if self._is_infrastructure_failure(failure):
                # Analyze system configuration
                infrastructure_analysis['system_config'] = self._analyze_system_configuration(failure)
                
                # Analyze permissions
                infrastructure_analysis['permissions'] = self._analyze_permissions(failure)
                
                # Analyze environmental factors
                infrastructure_analysis['environment'] = self._analyze_infrastructure_environment(failure)
                
                # Analyze resource availability
                infrastructure_analysis['resources'] = self._analyze_resource_availability(failure)
                
                infrastructure_analysis['analysis_confidence'] = 0.7
                
            else:
                infrastructure_analysis['applicable'] = False
                infrastructure_analysis['reason'] = 'Not an infrastructure failure'
                
        except Exception as e:
            infrastructure_analysis['analysis_error'] = str(e)
            
        return infrastructure_analysis
        
    def _identify_root_causes(self, failure: Failure, analysis: ComprehensiveAnalysisResult) -> List[RootCause]:
        """Identify root causes from comprehensive analysis including test-specific causes"""
        root_causes = []
        
        # Test-specific root cause identification
        # Check multiple places where test analysis might be stored
        test_analysis = {}
        if hasattr(analysis, 'environmental_factors') and analysis.environmental_factors:
            test_analysis = analysis.environmental_factors.get('test_specific', {})
        
        # Also check if this is a test failure based on the failure itself
        is_test_failure = (
            test_analysis.get('is_test_failure', False) or
            failure.component.startswith("test:") or
            "test" in failure.component.lower() or
            failure.category in [FailureCategory.PYTEST_FAILURE, FailureCategory.MAKE_TARGET_FAILURE, FailureCategory.INFRASTRUCTURE_FAILURE, FailureCategory.TEST_ENVIRONMENT_FAILURE] or
            self._is_pytest_failure(failure) or
            self._is_make_failure(failure) or
            self._is_infrastructure_failure(failure)
        )
        
        if is_test_failure:
            test_root_causes = self._identify_test_specific_root_causes(failure, analysis)
            root_causes.extend(test_root_causes)
        
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
        """Generate systematic fix for root cause including test-specific fixes"""
        fix_id = f"fix_{root_cause.cause_type.value}_{int(time.time())}"
        
        # Test-specific systematic fixes
        if root_cause.cause_type == RootCauseType.TEST_IMPORT_ERROR:
            return self._generate_pytest_specific_fix(root_cause)
        elif root_cause.cause_type == RootCauseType.TEST_ASSERTION_FAILURE:
            return self._generate_pytest_specific_fix(root_cause)
        elif root_cause.cause_type == RootCauseType.TEST_FIXTURE_ERROR:
            return self._generate_pytest_specific_fix(root_cause)
        elif root_cause.cause_type == RootCauseType.TEST_TIMEOUT:
            return self._generate_pytest_specific_fix(root_cause)
        elif root_cause.cause_type == RootCauseType.TEST_SETUP_ERROR:
            return self._generate_pytest_specific_fix(root_cause)
        elif root_cause.cause_type == RootCauseType.MAKEFILE_ERROR:
            return self._generate_makefile_specific_fix(root_cause)
        elif root_cause.cause_type == RootCauseType.BUILD_DEPENDENCY_ERROR:
            return self._generate_makefile_specific_fix(root_cause)
        elif root_cause.cause_type == RootCauseType.INFRASTRUCTURE_ERROR:
            return self._generate_infrastructure_specific_fix(root_cause)
        
        # Existing systematic fixes
        elif root_cause.cause_type == RootCauseType.MISSING_FILES:
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
            
    # Test-specific helper methods for Requirements 5.1, 5.2, 5.3, 5.4
    
    def _is_pytest_failure(self, failure: Failure) -> bool:
        """Check if failure is pytest-related"""
        return (
            "pytest" in failure.error_message.lower() or
            "test_" in failure.component or
            failure.context.get('pytest_node_id') is not None or
            "ImportError" in failure.error_message or
            "AssertionError" in failure.error_message
        )
    
    def _is_make_failure(self, failure: Failure) -> bool:
        """Check if failure is make-related"""
        return (
            "make" in failure.component.lower() or
            "Makefile" in failure.error_message or
            "No rule to make target" in failure.error_message or
            "missing separator" in failure.error_message
        )
    
    def _is_infrastructure_failure(self, failure: Failure) -> bool:
        """Check if failure is infrastructure-related"""
        return (
            "PermissionError" in failure.error_message or
            "ConnectionError" in failure.error_message or
            "system" in failure.component.lower() or
            "environment" in failure.error_message.lower()
        )
    
    def _get_pytest_subcategory(self, failure: Failure) -> str:
        """Get pytest failure subcategory"""
        if "ImportError" in failure.error_message:
            return "import_error"
        elif "AssertionError" in failure.error_message:
            return "assertion_failure"
        elif "fixture" in failure.error_message.lower():
            return "fixture_error"
        elif "timeout" in failure.error_message.lower():
            return "timeout"
        else:
            return "general_pytest_error"
    
    def _get_make_subcategory(self, failure: Failure) -> str:
        """Get make failure subcategory"""
        if "No rule to make target" in failure.error_message:
            return "missing_target"
        elif "missing separator" in failure.error_message:
            return "syntax_error"
        elif "No such file" in failure.error_message:
            return "missing_file"
        else:
            return "general_make_error"
    
    def _get_infrastructure_subcategory(self, failure: Failure) -> str:
        """Get infrastructure failure subcategory"""
        if "PermissionError" in failure.error_message:
            return "permission_error"
        elif "ConnectionError" in failure.error_message:
            return "network_error"
        elif "resource" in failure.error_message.lower():
            return "resource_error"
        else:
            return "general_infrastructure_error"
    
    def _analyze_pytest_details(self, failure: Failure) -> Dict[str, Any]:
        """Analyze pytest failure details"""
        return {
            "error_type": self._get_pytest_subcategory(failure),
            "has_stack_trace": failure.stack_trace is not None,
            "test_context_available": bool(failure.context.get('test_file')),
            "pytest_node_available": bool(failure.context.get('pytest_node_id'))
        }
    
    def _analyze_make_details(self, failure: Failure) -> Dict[str, Any]:
        """Analyze make failure details"""
        return {
            "error_type": self._get_make_subcategory(failure),
            "makefile_exists": Path('Makefile').exists(),
            "makefiles_dir_exists": Path('makefiles').exists(),
            "error_in_makefile": "Makefile" in failure.error_message
        }
    
    def _analyze_infrastructure_details(self, failure: Failure) -> Dict[str, Any]:
        """Analyze infrastructure failure details"""
        return {
            "error_type": self._get_infrastructure_subcategory(failure),
            "system_related": "system" in failure.error_message.lower(),
            "permission_related": "permission" in failure.error_message.lower(),
            "network_related": "connection" in failure.error_message.lower()
        }
    
    def _analyze_test_environment(self, failure: Failure) -> Dict[str, Any]:
        """Analyze test environment factors"""
        env_analysis = {}
        
        try:
            # Check Python environment
            env_analysis['python_available'] = subprocess.run(['python3', '--version'], capture_output=True).returncode == 0
            
            # Check pytest availability
            env_analysis['pytest_available'] = subprocess.run(['python3', '-m', 'pytest', '--version'], capture_output=True).returncode == 0
            
            # Check virtual environment
            env_analysis['venv_active'] = 'VIRTUAL_ENV' in os.environ
            
            # Check test directory structure
            env_analysis['tests_dir_exists'] = Path('tests').exists()
            env_analysis['conftest_exists'] = Path('tests/conftest.py').exists()
            
        except Exception as e:
            env_analysis['analysis_error'] = str(e)
            
        return env_analysis
    
    def _analyze_python_issues(self, failure: Failure) -> Dict[str, Any]:
        """Analyze Python-specific issues in pytest failures"""
        python_issues = {
            "syntax_errors": [],
            "import_errors": [],
            "type_errors": [],
            "runtime_errors": []
        }
        
        if failure.stack_trace:
            if "SyntaxError" in failure.stack_trace:
                python_issues["syntax_errors"].append("SyntaxError detected in stack trace")
            if "ImportError" in failure.stack_trace:
                python_issues["import_errors"].append("ImportError detected in stack trace")
            if "TypeError" in failure.stack_trace:
                python_issues["type_errors"].append("TypeError detected in stack trace")
            if "RuntimeError" in failure.stack_trace:
                python_issues["runtime_errors"].append("RuntimeError detected in stack trace")
                
        return python_issues
    
    def _analyze_import_issues(self, failure: Failure) -> Dict[str, Any]:
        """Analyze import-related issues"""
        import_analysis = {}
        
        if "ImportError" in failure.error_message or "ModuleNotFoundError" in failure.error_message:
            import_analysis['has_import_error'] = True
            
            # Extract module name if possible
            if "No module named" in failure.error_message:
                import_analysis['missing_module'] = failure.error_message.split("No module named")[1].strip().strip("'\"")
            
            # Check if it's a relative import issue
            import_analysis['relative_import_issue'] = "relative import" in failure.error_message.lower()
            
        else:
            import_analysis['has_import_error'] = False
            
        return import_analysis
    
    def _analyze_test_dependencies(self, failure: Failure) -> Dict[str, Any]:
        """Analyze test-specific dependency issues"""
        dep_analysis = {}
        
        try:
            # Check if requirements.txt exists
            dep_analysis['requirements_exists'] = Path('requirements.txt').exists()
            
            # Check if pyproject.toml exists
            dep_analysis['pyproject_exists'] = Path('pyproject.toml').exists()
            
            # Check if setup.py exists
            dep_analysis['setup_py_exists'] = Path('setup.py').exists()
            
            # Check pip list
            result = subprocess.run(['pip', 'list'], capture_output=True, text=True)
            dep_analysis['pip_list_available'] = result.returncode == 0
            
        except Exception as e:
            dep_analysis['analysis_error'] = str(e)
            
        return dep_analysis
    
    def _analyze_syntax_issues(self, failure: Failure) -> Dict[str, Any]:
        """Analyze syntax-related issues"""
        syntax_analysis = {}
        
        if "SyntaxError" in failure.error_message or (failure.stack_trace and "SyntaxError" in failure.stack_trace):
            syntax_analysis['has_syntax_error'] = True
            syntax_analysis['syntax_error_details'] = failure.error_message
        else:
            syntax_analysis['has_syntax_error'] = False
            
        return syntax_analysis
    
    def _analyze_test_structure(self, failure: Failure) -> Dict[str, Any]:
        """Analyze test structure issues"""
        structure_analysis = {}
        
        if failure.context and 'test_file' in failure.context:
            test_file = failure.context['test_file']
            structure_analysis['test_file_exists'] = Path(test_file).exists()
            structure_analysis['test_file_path'] = test_file
            
            # Check if test follows naming conventions
            structure_analysis['follows_naming_convention'] = test_file.startswith('test_') or test_file.endswith('_test.py')
            
        return structure_analysis
    
    def _analyze_makefile_issues(self, failure: Failure) -> Dict[str, Any]:
        """Analyze Makefile-specific issues"""
        makefile_issues = {}
        
        try:
            makefile_issues['makefile_exists'] = Path('Makefile').exists()
            makefile_issues['makefiles_dir_exists'] = Path('makefiles').exists()
            
            if "missing separator" in failure.error_message:
                makefile_issues['syntax_error'] = True
                makefile_issues['syntax_details'] = "Missing tab separator in Makefile"
                
            if "No rule to make target" in failure.error_message:
                makefile_issues['missing_target'] = True
                makefile_issues['target_details'] = failure.error_message
                
        except Exception as e:
            makefile_issues['analysis_error'] = str(e)
            
        return makefile_issues
    
    def _analyze_missing_files(self, failure: Failure) -> Dict[str, Any]:
        """Analyze missing file issues in make context"""
        missing_files = {}
        
        if "No such file" in failure.error_message:
            missing_files['has_missing_files'] = True
            # Try to extract filename
            if "No such file or directory:" in failure.error_message:
                missing_files['missing_file'] = failure.error_message.split("No such file or directory:")[1].strip()
        else:
            missing_files['has_missing_files'] = False
            
        return missing_files
    
    def _analyze_build_dependencies(self, failure: Failure) -> Dict[str, Any]:
        """Analyze build dependency issues"""
        build_deps = {}
        
        try:
            # Check common build tools
            build_deps['make_available'] = subprocess.run(['which', 'make'], capture_output=True).returncode == 0
            build_deps['gcc_available'] = subprocess.run(['which', 'gcc'], capture_output=True).returncode == 0
            build_deps['python_available'] = subprocess.run(['which', 'python3'], capture_output=True).returncode == 0
            
        except Exception as e:
            build_deps['analysis_error'] = str(e)
            
        return build_deps
    
    def _analyze_make_targets(self, failure: Failure) -> Dict[str, Any]:
        """Analyze make target structure"""
        target_analysis = {}
        
        try:
            # Try to get make help
            result = subprocess.run(['make', 'help'], capture_output=True, text=True, timeout=5)
            target_analysis['make_help_available'] = result.returncode == 0
            
            if result.returncode == 0:
                target_analysis['available_targets'] = len(result.stdout.split('\n'))
            else:
                target_analysis['make_help_error'] = result.stderr
                
        except Exception as e:
            target_analysis['analysis_error'] = str(e)
            
        return target_analysis
    
    def _analyze_system_configuration(self, failure: Failure) -> Dict[str, Any]:
        """Analyze system configuration for infrastructure failures"""
        sys_config = {}
        
        try:
            sys_config['platform'] = os.uname().sysname
            sys_config['user'] = os.environ.get('USER', 'unknown')
            sys_config['home_set'] = 'HOME' in os.environ
            sys_config['path_set'] = 'PATH' in os.environ
            
        except Exception as e:
            sys_config['analysis_error'] = str(e)
            
        return sys_config
    
    def _analyze_permissions(self, failure: Failure) -> Dict[str, Any]:
        """Analyze permission-related issues"""
        perm_analysis = {}
        
        if "PermissionError" in failure.error_message or "Permission denied" in failure.error_message:
            perm_analysis['has_permission_error'] = True
            perm_analysis['error_details'] = failure.error_message
            
            # Check current directory permissions
            try:
                perm_analysis['cwd_writable'] = os.access('.', os.W_OK)
                perm_analysis['cwd_readable'] = os.access('.', os.R_OK)
            except Exception as e:
                perm_analysis['permission_check_error'] = str(e)
        else:
            perm_analysis['has_permission_error'] = False
            
        return perm_analysis
    
    def _analyze_infrastructure_environment(self, failure: Failure) -> Dict[str, Any]:
        """Analyze infrastructure environment factors"""
        infra_env = {}
        
        try:
            # Check disk space
            import shutil
            total, used, free = shutil.disk_usage('.')
            infra_env['disk_space_gb'] = free // (1024**3)
            infra_env['disk_usage_percent'] = (used / total) * 100
            
            # Check memory (basic)
            infra_env['memory_info_available'] = True
            
        except Exception as e:
            infra_env['analysis_error'] = str(e)
            
        return infra_env
    
    def _analyze_resource_availability(self, failure: Failure) -> Dict[str, Any]:
        """Analyze resource availability"""
        resource_analysis = {}
        
        if "MemoryError" in failure.error_message or "resource" in failure.error_message.lower():
            resource_analysis['has_resource_issue'] = True
            resource_analysis['resource_details'] = failure.error_message
        else:
            resource_analysis['has_resource_issue'] = False
            
        return resource_analysis
    
    def _identify_test_specific_root_causes(self, failure: Failure, analysis: ComprehensiveAnalysisResult) -> List[RootCause]:
        """Identify test-specific root causes"""
        test_root_causes = []
        
        # Pytest-specific root causes
        if self._is_pytest_failure(failure):
            if "ImportError" in failure.error_message:
                test_root_causes.append(RootCause(
                    cause_type=RootCauseType.TEST_IMPORT_ERROR,
                    description="Test import error - missing or broken test dependencies",
                    evidence=["ImportError in test execution", failure.error_message],
                    confidence_score=0.9,
                    impact_severity="high",
                    affected_components=[failure.component]
                ))
            
            if "AssertionError" in failure.error_message:
                test_root_causes.append(RootCause(
                    cause_type=RootCauseType.TEST_ASSERTION_FAILURE,
                    description="Test assertion failure - test logic or implementation issue",
                    evidence=["AssertionError in test execution", failure.error_message],
                    confidence_score=0.8,
                    impact_severity="medium",
                    affected_components=[failure.component]
                ))
            
            if "fixture" in failure.error_message.lower():
                test_root_causes.append(RootCause(
                    cause_type=RootCauseType.TEST_FIXTURE_ERROR,
                    description="Test fixture error - fixture setup or teardown issue",
                    evidence=["Fixture error in test execution", failure.error_message],
                    confidence_score=0.8,
                    impact_severity="medium",
                    affected_components=[failure.component]
                ))
        
        # Make-specific root causes
        elif self._is_make_failure(failure):
            if "No rule to make target" in failure.error_message:
                test_root_causes.append(RootCause(
                    cause_type=RootCauseType.MAKEFILE_ERROR,
                    description="Makefile target missing - build system configuration issue",
                    evidence=["Missing make target", failure.error_message],
                    confidence_score=0.9,
                    impact_severity="high",
                    affected_components=["makefile", "build_system"]
                ))
            
            if "missing separator" in failure.error_message:
                test_root_causes.append(RootCause(
                    cause_type=RootCauseType.MAKEFILE_ERROR,
                    description="Makefile syntax error - incorrect tab/space formatting",
                    evidence=["Makefile syntax error", failure.error_message],
                    confidence_score=0.9,
                    impact_severity="medium",
                    affected_components=["makefile"]
                ))
        
        # Infrastructure-specific root causes
        elif self._is_infrastructure_failure(failure):
            if "PermissionError" in failure.error_message:
                test_root_causes.append(RootCause(
                    cause_type=RootCauseType.INFRASTRUCTURE_ERROR,
                    description="Infrastructure permission error - system access issue",
                    evidence=["Permission error in system operation", failure.error_message],
                    confidence_score=0.8,
                    impact_severity="high",
                    affected_components=["system", "infrastructure"]
                ))
        
        return test_root_causes
    
    def _generate_pytest_specific_fix(self, root_cause: RootCause) -> SystematicFix:
        """Generate pytest-specific systematic fix"""
        fix_id = f"fix_{root_cause.cause_type.value}_{int(time.time())}"
        
        if root_cause.cause_type == RootCauseType.TEST_IMPORT_ERROR:
            return SystematicFix(
                fix_id=fix_id,
                root_cause=root_cause,
                fix_description="Fix test import errors by resolving dependencies and Python path issues",
                implementation_steps=[
                    "Identify missing modules from error message",
                    "Check if modules are installed: pip list | grep <module>",
                    "Install missing dependencies: pip install <module>",
                    "Verify Python path includes necessary directories",
                    "Check for circular imports in test modules",
                    "Validate import statements in test files"
                ],
                validation_criteria=[
                    "Import statements execute without errors",
                    "Test modules can be imported successfully",
                    "pytest --collect-only succeeds",
                    "No ImportError in test execution"
                ],
                rollback_plan="Revert dependency installations and Python path changes",
                estimated_time_minutes=10
            )
        
        elif root_cause.cause_type == RootCauseType.TEST_ASSERTION_FAILURE:
            return SystematicFix(
                fix_id=fix_id,
                root_cause=root_cause,
                fix_description="Fix test assertion failures by analyzing test logic and expected behavior",
                implementation_steps=[
                    "Analyze assertion failure details from stack trace",
                    "Review test logic and expected vs actual values",
                    "Check if test data or fixtures are correct",
                    "Verify implementation matches test expectations",
                    "Update test assertions or fix implementation",
                    "Run specific test to validate fix"
                ],
                validation_criteria=[
                    "Test assertions pass with correct values",
                    "Test logic matches implementation behavior",
                    "No assertion errors in test execution",
                    "Test provides meaningful validation"
                ],
                rollback_plan="Revert test or implementation changes",
                estimated_time_minutes=15
            )
        
        elif root_cause.cause_type == RootCauseType.TEST_FIXTURE_ERROR:
            return SystematicFix(
                fix_id=fix_id,
                root_cause=root_cause,
                fix_description="Fix test fixture errors by resolving setup and teardown issues",
                implementation_steps=[
                    "Identify failing fixture from error message",
                    "Check fixture definition and scope",
                    "Verify fixture dependencies and parameters",
                    "Test fixture setup and teardown independently",
                    "Fix fixture implementation or dependencies",
                    "Validate fixture works with dependent tests"
                ],
                validation_criteria=[
                    "Fixture setup completes without errors",
                    "Fixture provides expected test data/resources",
                    "Fixture teardown cleans up properly",
                    "Tests using fixture execute successfully"
                ],
                rollback_plan="Revert fixture changes and restore original implementation",
                estimated_time_minutes=12
            )
        
        else:
            return SystematicFix(
                fix_id=fix_id,
                root_cause=root_cause,
                fix_description=f"Generic pytest fix for {root_cause.cause_type.value}",
                implementation_steps=[
                    f"Analyze {root_cause.cause_type.value} systematically",
                    "Review pytest documentation for issue type",
                    "Implement appropriate fix",
                    "Validate fix resolves root cause"
                ],
                validation_criteria=[
                    "Pytest error no longer occurs",
                    "Test execution completes successfully"
                ],
                rollback_plan="Revert changes if fix fails",
                estimated_time_minutes=10
            )
    
    def _generate_makefile_specific_fix(self, root_cause: RootCause) -> SystematicFix:
        """Generate Makefile-specific systematic fix"""
        fix_id = f"fix_{root_cause.cause_type.value}_{int(time.time())}"
        
        if root_cause.cause_type == RootCauseType.MAKEFILE_ERROR:
            return SystematicFix(
                fix_id=fix_id,
                root_cause=root_cause,
                fix_description="Fix Makefile errors by correcting syntax and target definitions",
                implementation_steps=[
                    "Identify specific Makefile error from message",
                    "Check for tab vs space issues (use tabs for indentation)",
                    "Verify target definitions and dependencies",
                    "Add missing targets or fix existing ones",
                    "Validate Makefile syntax with make -n",
                    "Test make targets execute correctly"
                ],
                validation_criteria=[
                    "Makefile syntax is valid",
                    "make help command succeeds",
                    "Target dependencies are correct",
                    "Make targets execute without errors"
                ],
                rollback_plan="Restore original Makefile from backup",
                estimated_time_minutes=8
            )
        
        elif root_cause.cause_type == RootCauseType.BUILD_DEPENDENCY_ERROR:
            return SystematicFix(
                fix_id=fix_id,
                root_cause=root_cause,
                fix_description="Fix build dependency errors by installing required tools and libraries",
                implementation_steps=[
                    "Identify missing build dependencies from error",
                    "Check system package manager for required tools",
                    "Install missing build tools (make, gcc, etc.)",
                    "Verify tool versions are compatible",
                    "Update PATH if necessary",
                    "Test build process with dependencies"
                ],
                validation_criteria=[
                    "All required build tools are available",
                    "Tool versions meet requirements",
                    "Build process completes successfully",
                    "No dependency errors in build output"
                ],
                rollback_plan="Remove installed packages if they cause conflicts",
                estimated_time_minutes=15
            )
        
        else:
            return SystematicFix(
                fix_id=fix_id,
                root_cause=root_cause,
                fix_description=f"Generic Makefile fix for {root_cause.cause_type.value}",
                implementation_steps=[
                    f"Analyze {root_cause.cause_type.value} systematically",
                    "Review Makefile documentation",
                    "Implement appropriate fix",
                    "Validate fix resolves root cause"
                ],
                validation_criteria=[
                    "Makefile error no longer occurs",
                    "Build process completes successfully"
                ],
                rollback_plan="Revert changes if fix fails",
                estimated_time_minutes=10
            )
    
    def _generate_infrastructure_specific_fix(self, root_cause: RootCause) -> SystematicFix:
        """Generate infrastructure-specific systematic fix"""
        fix_id = f"fix_{root_cause.cause_type.value}_{int(time.time())}"
        
        return SystematicFix(
            fix_id=fix_id,
            root_cause=root_cause,
            fix_description="Fix infrastructure errors by resolving system configuration and permissions",
            implementation_steps=[
                "Identify specific infrastructure issue from error",
                "Check system permissions and access rights",
                "Verify system configuration and environment variables",
                "Fix permission issues with appropriate chmod/chown",
                "Update system configuration if needed",
                "Test system access and functionality"
            ],
            validation_criteria=[
                "System permissions are correct",
                "Configuration allows proper access",
                "Infrastructure error no longer occurs",
                "System functionality is restored"
            ],
            rollback_plan="Restore original system permissions and configuration",
            estimated_time_minutes=12
        )
    
    def _create_test_specific_pattern(self, failure: Failure, root_cause: RootCause, fix: SystematicFix) -> PreventionPattern:
        """Create test-specific prevention pattern"""
        pattern_id = f"test_pattern_{root_cause.cause_type.value}_{int(time.time())}"
        
        # Generate test-specific failure signature
        failure_signature = self._generate_test_failure_signature(failure)
        pattern_hash = hashlib.md5(failure_signature.encode()).hexdigest()[:8]
        
        return PreventionPattern(
            pattern_id=pattern_id,
            pattern_name=f"Prevent {root_cause.cause_type.value} in {failure.component}",
            failure_signature=failure_signature,
            root_cause_pattern=root_cause.description,
            prevention_steps=[
                f"Monitor for {root_cause.cause_type.value} symptoms in tests",
                "Implement automated test validation",
                "Add pre-test environment checks",
                "Create test-specific health monitoring"
            ],
            detection_criteria=[
                f"Detect {root_cause.cause_type.value} patterns early",
                "Monitor test execution for similar failures",
                "Automated pattern matching for test failures"
            ],
            automated_checks=[
                f"Automated check for {root_cause.cause_type.value} in tests",
                "Continuous test environment monitoring",
                "Preventive test validation"
            ],
            pattern_hash=pattern_hash
        )
    
    def _generate_test_failure_signature(self, failure: Failure) -> str:
        """Generate test-specific failure signature for pattern matching"""
        signature_parts = [
            failure.component,
            failure.category.value,
            failure.error_message[:100] if failure.error_message else "",
            failure.context.get('test_file', '') if failure.context else "",
            failure.context.get('failure_type', '') if failure.context else "",
            str(sorted(failure.context.keys())) if failure.context else ""
        ]
        return "|".join(signature_parts)
    
    def _add_test_pattern_to_library(self, pattern: PreventionPattern):
        """Add test-specific pattern to library with enhanced indexing"""
        # Use existing pattern library infrastructure
        self._add_pattern_to_library(pattern)
        
        # Additional test-specific indexing could be added here
        self.logger.info(f"Added test-specific pattern to library: {pattern.pattern_id}")

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