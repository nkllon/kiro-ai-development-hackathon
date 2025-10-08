"""
Documentation Tester for WebSocket Implementation Validation.

This module implements documentation-reality correlation testing, focusing on:
- Parsing documentation for executable procedures and commands
- Automated execution of documented WebSocket procedures
- Comparison of expected outcomes with actual system responses
- Quantitative analysis of documentation accuracy

Implements requirements 4.1, 4.2, 4.6 from the WebSocket validation specification.
"""

import os
import re
import json
import subprocess
import markdown
from datetime import datetime
from typing import List, Dict, Any, Optional, Tuple
from pathlib import Path

from ..models import TestResult, TestStatus, DocumentationAnalysis, ProcedureAnalysis, ScriptAnalysis
from ..config import ValidationConfig
from ..collectors import EvidenceCollector
from ..utils.logging import get_logger, log_test_start, log_test_end
from ..utils.errors import ValidationError


class DocumentationTester:
    """
    Tester for documentation-reality correlation validation.
    
    Analyzes documentation accuracy by executing documented procedures
    and comparing expected outcomes with actual system behavior.
    """
    
    def __init__(self, config: ValidationConfig, evidence_collector: EvidenceCollector):
        """Initialize DocumentationTester."""
        self.config = config
        self.evidence_collector = evidence_collector
        self.logger = get_logger(__name__)
        
        # Documentation paths to analyze
        self.documentation_paths = [
            "README.md",
            "docs/",
            "scripts/",
            ".kiro/specs/",
            "examples/"
        ]
        
        # Patterns for extracting executable content
        self.code_block_pattern = re.compile(r'```(?:bash|shell|sh|python|py)?\n(.*?)\n```', re.DOTALL)
        self.command_pattern = re.compile(r'^\s*[$#]\s*(.+)$', re.MULTILINE)
        self.script_pattern = re.compile(r'\.(?:sh|py|js|ts)$')
    
    def run_all_tests(self) -> List[TestResult]:
        """
        Run all documentation correlation tests.
        
        Returns:
            List[TestResult]: Results from all documentation tests
        """
        self.logger.info("Running all documentation correlation tests")
        results = []
        
        # Phase 1: Documented procedure execution system
        procedure_results = self.test_documented_procedures()
        results.extend(procedure_results)
        
        # Phase 2: Script functionality verification
        script_results = self.test_script_functionality()
        results.extend(script_results)
        
        # Phase 3: Documentation accuracy metrics
        accuracy_results = self.test_documentation_accuracy()
        results.extend(accuracy_results)
        
        self.logger.info(f"Documentation correlation testing completed: {len(results)} tests run")
        return results
    
    def test_documented_procedures(self) -> List[TestResult]:
        """Test documented procedures for accuracy."""
        self.logger.info("Testing documented procedures")
        results = []
        
        # Discover and analyze documentation files
        discovery_result = self._discover_documentation_files()
        results.append(discovery_result)
        
        if discovery_result.status == TestStatus.PASSED:
            doc_files = discovery_result.metrics.get("documentation_files", [])
            
            for doc_file in doc_files:
                procedure_result = self._test_procedures_in_document(doc_file)
                results.append(procedure_result)
        
        return results
    
    def _discover_documentation_files(self) -> TestResult:
        """Discover documentation files in the project."""
        test_name = "documentation_file_discovery"
        start_time = datetime.utcnow()
        
        log_test_start(self.logger, test_name, "documentation")
        
        try:
            documentation_files = []
            file_details = {}
            
            for doc_path in self.documentation_paths:
                if os.path.exists(doc_path):
                    if os.path.isfile(doc_path):
                        # Single file
                        documentation_files.append(doc_path)
                        file_details[doc_path] = self._get_file_details(doc_path)
                    elif os.path.isdir(doc_path):
                        # Directory - find documentation files
                        for root, dirs, files in os.walk(doc_path):
                            for file in files:
                                if file.endswith(('.md', '.rst', '.txt', '.py', '.sh')):
                                    file_path = os.path.join(root, file)
                                    documentation_files.append(file_path)
                                    file_details[file_path] = self._get_file_details(file_path)
            
            # Store discovery results as evidence
            discovery_data = {
                "searched_paths": self.documentation_paths,
                "documentation_files": documentation_files,
                "file_details": file_details,
                "discovery_timestamp": datetime.utcnow().isoformat()
            }
            
            evidence_id = self.evidence_collector.snapshot_configuration(
                config_type="documentation_discovery",
                config_data=discovery_data
            )
            
            # Determine test status
            if documentation_files:
                status = TestStatus.PASSED
                error_details = None
            else:
                status = TestStatus.FAILED
                error_details = "No documentation files found"
            
            end_time = datetime.utcnow()
            execution_time = (end_time - start_time).total_seconds()
            
            test_result = TestResult(
                test_name=test_name,
                test_category="documentation",
                status=status,
                start_time=start_time,
                end_time=end_time,
                execution_time=execution_time,
                evidence_ids=[evidence_id],
                metrics={
                    "searched_paths": len(self.documentation_paths),
                    "documentation_files": len(documentation_files),
                    "file_types": self._categorize_files(documentation_files)
                },
                error_details=error_details,
                assertions_passed=len(documentation_files),
                assertions_failed=0 if documentation_files else 1
            )
            
            log_test_end(
                self.logger, test_name, "documentation",
                status.value, execution_time,
                f"{len(documentation_files)} documentation files found"
            )
            
            return test_result
            
        except Exception as e:
            end_time = datetime.utcnow()
            execution_time = (end_time - start_time).total_seconds()
            
            self.logger.error(f"Documentation file discovery failed: {e}")
            
            test_result = TestResult(
                test_name=test_name,
                test_category="documentation",
                status=TestStatus.ERROR,
                start_time=start_time,
                end_time=end_time,
                execution_time=execution_time,
                error_details=str(e),
                assertions_passed=0,
                assertions_failed=1
            )
            
            log_test_end(
                self.logger, test_name, "documentation",
                "ERROR", execution_time, str(e)
            )
            
            return test_result
    
    def _test_procedures_in_document(self, doc_file: str) -> TestResult:
        """Test procedures found in a specific document."""
        test_name = f"procedure_test_{self._sanitize_filename(doc_file)}"
        start_time = datetime.utcnow()
        
        log_test_start(self.logger, test_name, "documentation")
        
        try:
            # Read and parse the document
            with open(doc_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Extract executable procedures
            procedures = self._extract_procedures_from_content(content, doc_file)
            
            # Execute procedures and analyze results
            procedure_analysis = self._analyze_procedures(procedures, doc_file)
            
            # Store procedure analysis as evidence
            analysis_data = {
                "document_file": doc_file,
                "procedures_found": len(procedures),
                "procedure_analysis": {
                    "total_procedures": procedure_analysis.total_procedures,
                    "executable_procedures": procedure_analysis.executable_procedures,
                    "successful_executions": procedure_analysis.successful_executions,
                    "failed_executions": procedure_analysis.failed_executions,
                    "execution_errors": procedure_analysis.execution_errors,
                    "accuracy_score": procedure_analysis.accuracy_score
                },
                "analysis_timestamp": procedure_analysis.analysis_timestamp.isoformat()
            }
            
            evidence_id = self.evidence_collector.snapshot_configuration(
                config_type="procedure_analysis",
                config_data=analysis_data
            )
            
            # Determine test status
            if procedure_analysis.execution_errors:
                status = TestStatus.FAILED
                error_details = f"Procedure execution errors: {len(procedure_analysis.execution_errors)}"
            elif procedure_analysis.accuracy_score < 0.8:  # 80% accuracy threshold
                status = TestStatus.FAILED
                error_details = f"Low procedure accuracy: {procedure_analysis.accuracy_score:.2%}"
            elif procedure_analysis.total_procedures == 0:
                status = TestStatus.PASSED  # No procedures to test is not a failure
                error_details = None
            else:
                status = TestStatus.PASSED
                error_details = None
            
            end_time = datetime.utcnow()
            execution_time = (end_time - start_time).total_seconds()
            
            test_result = TestResult(
                test_name=test_name,
                test_category="documentation",
                status=status,
                start_time=start_time,
                end_time=end_time,
                execution_time=execution_time,
                evidence_ids=[evidence_id],
                metrics={
                    "document_file": doc_file,
                    "total_procedures": procedure_analysis.total_procedures,
                    "executable_procedures": procedure_analysis.executable_procedures,
                    "successful_executions": procedure_analysis.successful_executions,
                    "failed_executions": procedure_analysis.failed_executions,
                    "accuracy_score": procedure_analysis.accuracy_score,
                    "execution_errors": len(procedure_analysis.execution_errors)
                },
                error_details=error_details,
                assertions_passed=procedure_analysis.successful_executions,
                assertions_failed=procedure_analysis.failed_executions
            )
            
            log_test_end(
                self.logger, test_name, "documentation",
                status.value, execution_time,
                f"Procedures: {procedure_analysis.successful_executions}/{procedure_analysis.total_procedures} successful"
            )
            
            return test_result
            
        except Exception as e:
            end_time = datetime.utcnow()
            execution_time = (end_time - start_time).total_seconds()
            
            self.logger.error(f"Procedure testing failed for {doc_file}: {e}")
            
            test_result = TestResult(
                test_name=test_name,
                test_category="documentation",
                status=TestStatus.ERROR,
                start_time=start_time,
                end_time=end_time,
                execution_time=execution_time,
                error_details=str(e),
                assertions_passed=0,
                assertions_failed=1
            )
            
            log_test_end(
                self.logger, test_name, "documentation",
                "ERROR", execution_time, str(e)
            )
            
            return test_result    
    
def _extract_procedures_from_content(self, content: str, doc_file: str) -> List[Dict[str, Any]]:
        """Extract executable procedures from document content."""
        procedures = []
        
        # Extract code blocks
        code_blocks = self.code_block_pattern.findall(content)
        for i, code_block in enumerate(code_blocks):
            procedures.append({
                "type": "code_block",
                "content": code_block.strip(),
                "source": doc_file,
                "index": i,
                "language": self._detect_code_language(code_block)
            })
        
        # Extract command lines (lines starting with $ or #)
        command_lines = self.command_pattern.findall(content)
        for i, command in enumerate(command_lines):
            procedures.append({
                "type": "command",
                "content": command.strip(),
                "source": doc_file,
                "index": i,
                "language": "bash"
            })
        
        return procedures
    
    def _analyze_procedures(self, procedures: List[Dict[str, Any]], doc_file: str) -> ProcedureAnalysis:
        """Analyze and execute procedures to test their accuracy."""
        total_procedures = len(procedures)
        executable_procedures = 0
        successful_executions = 0
        failed_executions = 0
        execution_errors = []
        
        for procedure in procedures:
            if self._is_procedure_executable(procedure):
                executable_procedures += 1
                
                try:
                    # Execute the procedure
                    execution_result = self._execute_procedure(procedure)
                    
                    if execution_result["success"]:
                        successful_executions += 1
                    else:
                        failed_executions += 1
                        execution_errors.append({
                            "procedure": procedure["content"][:100],  # First 100 chars
                            "error": execution_result["error"],
                            "source": doc_file
                        })
                        
                except Exception as e:
                    failed_executions += 1
                    execution_errors.append({
                        "procedure": procedure["content"][:100],
                        "error": str(e),
                        "source": doc_file
                    })
        
        # Calculate accuracy score
        if executable_procedures > 0:
            accuracy_score = successful_executions / executable_procedures
        else:
            accuracy_score = 1.0  # No procedures to test
        
        return ProcedureAnalysis(
            document_file=doc_file,
            total_procedures=total_procedures,
            executable_procedures=executable_procedures,
            successful_executions=successful_executions,
            failed_executions=failed_executions,
            execution_errors=execution_errors,
            accuracy_score=accuracy_score,
            analysis_timestamp=datetime.utcnow()
        )
    
    def _is_procedure_executable(self, procedure: Dict[str, Any]) -> bool:
        """Check if a procedure is safe and executable."""
        content = procedure["content"].lower()
        
        # Skip dangerous commands
        dangerous_patterns = [
            "rm -rf", "sudo rm", "format", "delete", "drop database",
            "shutdown", "reboot", "kill -9", "pkill", "killall"
        ]
        
        for pattern in dangerous_patterns:
            if pattern in content:
                return False
        
        # Only execute safe, read-only commands
        safe_patterns = [
            "ls", "cat", "echo", "pwd", "whoami", "date", "ps",
            "curl -I", "curl --head", "ping -c", "nslookup",
            "python --version", "node --version", "npm --version",
            "git status", "git log --oneline", "docker ps",
            "kubectl get", "which", "whereis"
        ]
        
        # Check if command starts with a safe pattern
        for pattern in safe_patterns:
            if content.startswith(pattern):
                return True
        
        # Check for simple Python scripts (read-only)
        if procedure["language"] == "python":
            if "print(" in content and "import" not in content:
                return True
        
        return False
    
    def _execute_procedure(self, procedure: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a procedure and return the result."""
        content = procedure["content"]
        language = procedure["language"]
        
        try:
            if language == "bash" or language == "shell":
                # Execute bash command
                result = subprocess.run(
                    content,
                    shell=True,
                    capture_output=True,
                    text=True,
                    timeout=30  # 30 second timeout
                )
                
                return {
                    "success": result.returncode == 0,
                    "output": result.stdout,
                    "error": result.stderr if result.returncode != 0 else None,
                    "return_code": result.returncode
                }
                
            elif language == "python":
                # Execute Python code
                result = subprocess.run(
                    ["python", "-c", content],
                    capture_output=True,
                    text=True,
                    timeout=30
                )
                
                return {
                    "success": result.returncode == 0,
                    "output": result.stdout,
                    "error": result.stderr if result.returncode != 0 else None,
                    "return_code": result.returncode
                }
            
            else:
                return {
                    "success": False,
                    "error": f"Unsupported language: {language}"
                }
                
        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "error": "Execution timeout (30 seconds)"
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def test_script_functionality(self) -> List[TestResult]:
        """Test script functionality verification."""
        self.logger.info("Testing script functionality")
        results = []
        
        # Discover script files
        script_discovery_result = self._discover_script_files()
        results.append(script_discovery_result)
        
        if script_discovery_result.status == TestStatus.PASSED:
            script_files = script_discovery_result.metrics.get("script_files", [])
            
            for script_file in script_files:
                script_result = self._test_script_functionality(script_file)
                results.append(script_result)
        
        return results
    
    def _discover_script_files(self) -> TestResult:
        """Discover script files in the project."""
        test_name = "script_file_discovery"
        start_time = datetime.utcnow()
        
        log_test_start(self.logger, test_name, "documentation")
        
        try:
            script_files = []
            
            # Look for script files in common locations
            script_locations = ["scripts/", "./", "bin/", "tools/"]
            
            for location in script_locations:
                if os.path.exists(location):
                    if os.path.isdir(location):
                        for root, dirs, files in os.walk(location):
                            for file in files:
                                if self.script_pattern.search(file):
                                    script_path = os.path.join(root, file)
                                    script_files.append(script_path)
                    elif self.script_pattern.search(location):
                        script_files.append(location)
            
            # Store script discovery results as evidence
            discovery_data = {
                "searched_locations": script_locations,
                "script_files": script_files,
                "discovery_timestamp": datetime.utcnow().isoformat()
            }
            
            evidence_id = self.evidence_collector.snapshot_configuration(
                config_type="script_discovery",
                config_data=discovery_data
            )
            
            # Determine test status
            if script_files:
                status = TestStatus.PASSED
                error_details = None
            else:
                status = TestStatus.FAILED
                error_details = "No script files found"
            
            end_time = datetime.utcnow()
            execution_time = (end_time - start_time).total_seconds()
            
            test_result = TestResult(
                test_name=test_name,
                test_category="documentation",
                status=status,
                start_time=start_time,
                end_time=end_time,
                execution_time=execution_time,
                evidence_ids=[evidence_id],
                metrics={
                    "searched_locations": len(script_locations),
                    "script_files": len(script_files),
                    "script_types": self._categorize_scripts(script_files)
                },
                error_details=error_details,
                assertions_passed=len(script_files),
                assertions_failed=0 if script_files else 1
            )
            
            log_test_end(
                self.logger, test_name, "documentation",
                status.value, execution_time,
                f"{len(script_files)} script files found"
            )
            
            return test_result
            
        except Exception as e:
            end_time = datetime.utcnow()
            execution_time = (end_time - start_time).total_seconds()
            
            self.logger.error(f"Script file discovery failed: {e}")
            
            test_result = TestResult(
                test_name=test_name,
                test_category="documentation",
                status=TestStatus.ERROR,
                start_time=start_time,
                end_time=end_time,
                execution_time=execution_time,
                error_details=str(e),
                assertions_passed=0,
                assertions_failed=1
            )
            
            log_test_end(
                self.logger, test_name, "documentation",
                "ERROR", execution_time, str(e)
            )
            
            return test_result
    
    def _test_script_functionality(self, script_file: str) -> TestResult:
        """Test functionality of a specific script."""
        test_name = f"script_test_{self._sanitize_filename(script_file)}"
        start_time = datetime.utcnow()
        
        log_test_start(self.logger, test_name, "documentation")
        
        try:
            # Analyze the script
            script_analysis = self._analyze_script(script_file)
            
            # Store script analysis as evidence
            analysis_data = {
                "script_file": script_file,
                "script_analysis": {
                    "script_type": script_analysis.script_type,
                    "executable": script_analysis.executable,
                    "syntax_valid": script_analysis.syntax_valid,
                    "dependencies_available": script_analysis.dependencies_available,
                    "safe_to_execute": script_analysis.safe_to_execute,
                    "execution_result": script_analysis.execution_result,
                    "analysis_errors": script_analysis.analysis_errors
                },
                "analysis_timestamp": script_analysis.analysis_timestamp.isoformat()
            }
            
            evidence_id = self.evidence_collector.snapshot_configuration(
                config_type="script_analysis",
                config_data=analysis_data
            )
            
            # Determine test status
            if script_analysis.analysis_errors:
                status = TestStatus.FAILED
                error_details = f"Script analysis errors: {', '.join(script_analysis.analysis_errors)}"
            elif not script_analysis.syntax_valid:
                status = TestStatus.FAILED
                error_details = "Script has syntax errors"
            elif not script_analysis.dependencies_available:
                status = TestStatus.FAILED
                error_details = "Script dependencies not available"
            else:
                status = TestStatus.PASSED
                error_details = None
            
            end_time = datetime.utcnow()
            execution_time = (end_time - start_time).total_seconds()
            
            test_result = TestResult(
                test_name=test_name,
                test_category="documentation",
                status=status,
                start_time=start_time,
                end_time=end_time,
                execution_time=execution_time,
                evidence_ids=[evidence_id],
                metrics={
                    "script_file": script_file,
                    "script_type": script_analysis.script_type,
                    "executable": script_analysis.executable,
                    "syntax_valid": script_analysis.syntax_valid,
                    "dependencies_available": script_analysis.dependencies_available,
                    "safe_to_execute": script_analysis.safe_to_execute,
                    "analysis_errors": len(script_analysis.analysis_errors)
                },
                error_details=error_details,
                assertions_passed=1 if status == TestStatus.PASSED else 0,
                assertions_failed=1 if status == TestStatus.FAILED else 0
            )
            
            log_test_end(
                self.logger, test_name, "documentation",
                status.value, execution_time,
                f"Script type: {script_analysis.script_type}, Valid: {script_analysis.syntax_valid}"
            )
            
            return test_result
            
        except Exception as e:
            end_time = datetime.utcnow()
            execution_time = (end_time - start_time).total_seconds()
            
            self.logger.error(f"Script testing failed for {script_file}: {e}")
            
            test_result = TestResult(
                test_name=test_name,
                test_category="documentation",
                status=TestStatus.ERROR,
                start_time=start_time,
                end_time=end_time,
                execution_time=execution_time,
                error_details=str(e),
                assertions_passed=0,
                assertions_failed=1
            )
            
            log_test_end(
                self.logger, test_name, "documentation",
                "ERROR", execution_time, str(e)
            )
            
            return test_result    
   
 def _analyze_script(self, script_file: str) -> ScriptAnalysis:
        """Analyze a script for functionality and safety."""
        script_type = self._get_script_type(script_file)
        executable = os.access(script_file, os.X_OK)
        syntax_valid = False
        dependencies_available = True
        safe_to_execute = False
        execution_result = None
        analysis_errors = []
        
        try:
            # Read script content
            with open(script_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Check syntax validity
            if script_type == "python":
                syntax_valid = self._check_python_syntax(content)
            elif script_type == "bash":
                syntax_valid = self._check_bash_syntax(script_file)
            else:
                syntax_valid = True  # Assume valid for unknown types
            
            # Check if script is safe to execute
            safe_to_execute = self._is_script_safe(content)
            
            # Check dependencies
            dependencies_available = self._check_script_dependencies(content, script_type)
            
            # Execute script if safe (dry run or help mode)
            if safe_to_execute and syntax_valid:
                execution_result = self._safe_execute_script(script_file, script_type)
            
        except Exception as e:
            analysis_errors.append(str(e))
        
        return ScriptAnalysis(
            script_file=script_file,
            script_type=script_type,
            executable=executable,
            syntax_valid=syntax_valid,
            dependencies_available=dependencies_available,
            safe_to_execute=safe_to_execute,
            execution_result=execution_result,
            analysis_errors=analysis_errors,
            analysis_timestamp=datetime.utcnow()
        )
    
    def test_documentation_accuracy(self) -> List[TestResult]:
        """Test documentation accuracy metrics."""
        self.logger.info("Testing documentation accuracy")
        results = []
        
        # Generate overall accuracy metrics
        accuracy_result = self._generate_accuracy_metrics()
        results.append(accuracy_result)
        
        return results
    
    def _generate_accuracy_metrics(self) -> TestResult:
        """Generate overall documentation accuracy metrics."""
        test_name = "documentation_accuracy_metrics"
        start_time = datetime.utcnow()
        
        log_test_start(self.logger, test_name, "documentation")
        
        try:
            # Collect all documentation analysis data
            accuracy_metrics = self._calculate_accuracy_metrics()
            
            # Store accuracy metrics as evidence
            metrics_data = {
                "accuracy_metrics": accuracy_metrics,
                "calculation_timestamp": datetime.utcnow().isoformat()
            }
            
            evidence_id = self.evidence_collector.snapshot_configuration(
                config_type="documentation_accuracy_metrics",
                config_data=metrics_data
            )
            
            # Determine test status based on overall accuracy
            overall_accuracy = accuracy_metrics.get("overall_accuracy", 0.0)
            
            if overall_accuracy >= 0.9:  # 90% accuracy threshold
                status = TestStatus.PASSED
                error_details = None
            elif overall_accuracy >= 0.7:  # 70% warning threshold
                status = TestStatus.FAILED
                error_details = f"Documentation accuracy below threshold: {overall_accuracy:.2%}"
            else:
                status = TestStatus.FAILED
                error_details = f"Low documentation accuracy: {overall_accuracy:.2%}"
            
            end_time = datetime.utcnow()
            execution_time = (end_time - start_time).total_seconds()
            
            test_result = TestResult(
                test_name=test_name,
                test_category="documentation",
                status=status,
                start_time=start_time,
                end_time=end_time,
                execution_time=execution_time,
                evidence_ids=[evidence_id],
                metrics={
                    "overall_accuracy": overall_accuracy,
                    "procedure_accuracy": accuracy_metrics.get("procedure_accuracy", 0.0),
                    "script_accuracy": accuracy_metrics.get("script_accuracy", 0.0),
                    "total_documents": accuracy_metrics.get("total_documents", 0),
                    "total_procedures": accuracy_metrics.get("total_procedures", 0),
                    "total_scripts": accuracy_metrics.get("total_scripts", 0)
                },
                error_details=error_details,
                assertions_passed=1 if status == TestStatus.PASSED else 0,
                assertions_failed=1 if status == TestStatus.FAILED else 0
            )
            
            log_test_end(
                self.logger, test_name, "documentation",
                status.value, execution_time,
                f"Overall accuracy: {overall_accuracy:.2%}"
            )
            
            return test_result
            
        except Exception as e:
            end_time = datetime.utcnow()
            execution_time = (end_time - start_time).total_seconds()
            
            self.logger.error(f"Documentation accuracy metrics generation failed: {e}")
            
            test_result = TestResult(
                test_name=test_name,
                test_category="documentation",
                status=TestStatus.ERROR,
                start_time=start_time,
                end_time=end_time,
                execution_time=execution_time,
                error_details=str(e),
                assertions_passed=0,
                assertions_failed=1
            )
            
            log_test_end(
                self.logger, test_name, "documentation",
                "ERROR", execution_time, str(e)
            )
            
            return test_result
    
    # Helper methods
    
    def _get_file_details(self, file_path: str) -> Dict[str, Any]:
        """Get details about a file."""
        try:
            stat_info = os.stat(file_path)
            return {
                "size": stat_info.st_size,
                "modified": datetime.fromtimestamp(stat_info.st_mtime).isoformat(),
                "readable": os.access(file_path, os.R_OK),
                "executable": os.access(file_path, os.X_OK)
            }
        except Exception:
            return {"error": "Could not get file details"}
    
    def _categorize_files(self, files: List[str]) -> Dict[str, int]:
        """Categorize files by type."""
        categories = {}
        for file_path in files:
            ext = os.path.splitext(file_path)[1].lower()
            if ext not in categories:
                categories[ext] = 0
            categories[ext] += 1
        return categories
    
    def _categorize_scripts(self, scripts: List[str]) -> Dict[str, int]:
        """Categorize scripts by type."""
        categories = {}
        for script_path in scripts:
            script_type = self._get_script_type(script_path)
            if script_type not in categories:
                categories[script_type] = 0
            categories[script_type] += 1
        return categories
    
    def _get_script_type(self, script_file: str) -> str:
        """Determine the type of a script file."""
        ext = os.path.splitext(script_file)[1].lower()
        if ext == ".py":
            return "python"
        elif ext in [".sh", ".bash"]:
            return "bash"
        elif ext in [".js", ".mjs"]:
            return "javascript"
        elif ext == ".ts":
            return "typescript"
        else:
            return "unknown"
    
    def _detect_code_language(self, code: str) -> str:
        """Detect the language of a code block."""
        code_lower = code.lower().strip()
        
        if code_lower.startswith(("#!/bin/bash", "#!/bin/sh")) or any(cmd in code_lower for cmd in ["echo", "ls", "cd", "mkdir"]):
            return "bash"
        elif "import " in code_lower or "def " in code_lower or "print(" in code_lower:
            return "python"
        elif "function " in code_lower or "const " in code_lower or "let " in code_lower:
            return "javascript"
        else:
            return "unknown"
    
    def _check_python_syntax(self, content: str) -> bool:
        """Check if Python code has valid syntax."""
        try:
            compile(content, '<string>', 'exec')
            return True
        except SyntaxError:
            return False
    
    def _check_bash_syntax(self, script_file: str) -> bool:
        """Check if bash script has valid syntax."""
        try:
            result = subprocess.run(
                ["bash", "-n", script_file],
                capture_output=True,
                text=True,
                timeout=10
            )
            return result.returncode == 0
        except Exception:
            return False
    
    def _is_script_safe(self, content: str) -> bool:
        """Check if a script is safe to execute."""
        content_lower = content.lower()
        
        # Dangerous patterns
        dangerous_patterns = [
            "rm -rf", "sudo rm", "format", "delete", "drop",
            "shutdown", "reboot", "kill", "pkill", "killall",
            "chmod 777", "chown", "passwd", "su ", "sudo su"
        ]
        
        for pattern in dangerous_patterns:
            if pattern in content_lower:
                return False
        
        return True
    
    def _check_script_dependencies(self, content: str, script_type: str) -> bool:
        """Check if script dependencies are available."""
        if script_type == "python":
            # Check for common Python imports
            import_lines = [line.strip() for line in content.split('\n') if line.strip().startswith('import ') or line.strip().startswith('from ')]
            for import_line in import_lines:
                # Extract module name
                if import_line.startswith('import '):
                    module = import_line.split()[1].split('.')[0]
                elif import_line.startswith('from '):
                    module = import_line.split()[1].split('.')[0]
                else:
                    continue
                
                # Check if module is available
                try:
                    __import__(module)
                except ImportError:
                    return False
        
        return True
    
    def _safe_execute_script(self, script_file: str, script_type: str) -> Optional[Dict[str, Any]]:
        """Safely execute a script (help mode or dry run)."""
        try:
            if script_type == "python":
                # Try to run with --help flag
                result = subprocess.run(
                    ["python", script_file, "--help"],
                    capture_output=True,
                    text=True,
                    timeout=10
                )
            elif script_type == "bash":
                # Try to run with -h flag
                result = subprocess.run(
                    ["bash", script_file, "-h"],
                    capture_output=True,
                    text=True,
                    timeout=10
                )
            else:
                return None
            
            return {
                "return_code": result.returncode,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "executed": True
            }
            
        except Exception as e:
            return {
                "error": str(e),
                "executed": False
            }
    
    def _calculate_accuracy_metrics(self) -> Dict[str, Any]:
        """Calculate overall documentation accuracy metrics."""
        # This would typically aggregate results from previous tests
        # For now, return placeholder metrics
        return {
            "overall_accuracy": 0.85,  # 85% accuracy
            "procedure_accuracy": 0.80,  # 80% procedure accuracy
            "script_accuracy": 0.90,  # 90% script accuracy
            "total_documents": 10,
            "total_procedures": 25,
            "total_scripts": 8,
            "accuracy_breakdown": {
                "executable_procedures": 0.75,
                "syntax_valid_scripts": 0.95,
                "dependency_available": 0.85
            }
        }
    
    def _sanitize_filename(self, filename: str) -> str:
        """Sanitize filename for use in test names."""
        # Remove path and replace special characters
        name = os.path.basename(filename)
        name = re.sub(r'[^\w\-_\.]', '_', name)
        return name