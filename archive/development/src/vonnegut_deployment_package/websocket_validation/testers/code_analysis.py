"""
CodeAnalysisTester - Analyzes actual FastAPI server implementation and code structure.
"""

import ast
import os
import re
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any, Optional, Set, Tuple
from ..models import (
    TestResult, TestStatus, RouteAnalysis, HandlerAnalysis, 
    DependencyAnalysis, CompletenessAnalysis, EvidenceType
)
from ..config import ValidationConfig
from ..collectors import EvidenceCollector
from ..utils import get_logger
from ..utils.logging import log_test_start, log_test_end
from ..utils.errors import ValidationError, create_config_error


class CodeAnalysisTester:
    """
    Analyzes actual FastAPI server implementation and code structure.
    
    Parses FastAPI server configuration, identifies registered WebSocket routes,
    analyzes route handler implementations, and verifies import dependencies.
    """
    
    def __init__(self, config: ValidationConfig, evidence_collector: EvidenceCollector):
        """Initialize CodeAnalysisTester."""
        self.config = config
        self.evidence_collector = evidence_collector
        self.logger = get_logger(__name__)
        
        # Common paths to search for FastAPI server files
        self.search_paths = [
            "src/beast_mode/observatory/server.py",
            "server.py",
            "main.py",
            "app.py",
            "src/server.py",
            "src/main.py",
            "src/app.py",
            "backend/server.py",
            "backend/main.py",
            "api/server.py",
            "api/main.py"
        ]
    
    def run_all_tests(self) -> List[TestResult]:
        """Run all code analysis tests."""
        self.logger.info("Running all code analysis tests")
        
        results = []
        
        # Run FastAPI route discovery
        try:
            route_results = self.analyze_fastapi_routes()
            results.extend(route_results)
        except Exception as e:
            self.logger.error(f"FastAPI route analysis failed: {e}")
            error_result = TestResult(
                test_name="fastapi_route_analysis",
                test_category="code_analysis",
                status=TestStatus.ERROR,
                error_details=str(e)
            )
            results.append(error_result)
        
        # Run WebSocket handler analysis (placeholder for now)
        try:
            handler_results = self.verify_websocket_handlers()
            results.extend(handler_results)
        except Exception as e:
            self.logger.error(f"WebSocket handler analysis failed: {e}")
            error_result = TestResult(
                test_name="websocket_handler_analysis",
                test_category="code_analysis",
                status=TestStatus.ERROR,
                error_details=str(e)
            )
            results.append(error_result)
        
        # Run dependency analysis (placeholder for now)
        try:
            dependency_results = self.check_dependency_imports()
            results.extend(dependency_results)
        except Exception as e:
            self.logger.error(f"Dependency analysis failed: {e}")
            error_result = TestResult(
                test_name="dependency_analysis",
                test_category="code_analysis",
                status=TestStatus.ERROR,
                error_details=str(e)
            )
            results.append(error_result)
        
        return results
    
    def analyze_fastapi_routes(self) -> List[TestResult]:
        """
        Analyze FastAPI routes and identify WebSocket endpoints.
        
        Implements requirements 2.1, 2.2, 2.5:
        - Parse server.py and related files for WebSocket route registrations
        - Identify @app.websocket() decorators and route definitions
        - Extract route paths, handlers, and middleware configurations
        - Validate route handler function implementations exist
        
        Returns:
            List[TestResult]: Results from FastAPI route analysis
        """
        self.logger.info("Analyzing FastAPI routes")
        results = []
        
        # Test 1: Discover FastAPI server files
        discovery_result = self._discover_fastapi_files()
        results.append(discovery_result)
        
        # Test 2: Parse and analyze routes
        if discovery_result.status == TestStatus.PASSED:
            server_files = discovery_result.metrics.get("server_files", [])
            for server_file in server_files:
                analysis_result = self._analyze_server_file(server_file)
                results.append(analysis_result)
        
        return results
    
    def _discover_fastapi_files(self) -> TestResult:
        """Discover FastAPI server files in the project."""
        test_name = "fastapi_file_discovery"
        start_time = datetime.utcnow()
        
        log_test_start(self.logger, test_name, "code_analysis")
        
        try:
            found_files = []
            searched_paths = []
            
            # Search for server files
            for search_path in self.search_paths:
                searched_paths.append(search_path)
                if os.path.exists(search_path):
                    found_files.append(search_path)
                    self.logger.info(f"Found FastAPI server file: {search_path}")
            
            # Also search for any Python files containing FastAPI imports
            additional_files = self._find_files_with_fastapi_imports()
            found_files.extend(additional_files)
            
            # Remove duplicates
            found_files = list(set(found_files))
            
            # Store discovery results as evidence
            discovery_data = {
                "searched_paths": searched_paths,
                "found_files": found_files,
                "additional_files": additional_files,
                "discovery_timestamp": datetime.utcnow().isoformat()
            }
            
            evidence_id = self.evidence_collector.snapshot_configuration(
                config_type="fastapi_file_discovery",
                config_data=discovery_data
            )
            
            # Determine test status
            if found_files:
                status = TestStatus.PASSED
                assertions_passed = len(found_files)
                assertions_failed = 0
                error_details = None
            else:
                status = TestStatus.FAILED
                assertions_passed = 0
                assertions_failed = 1
                error_details = "No FastAPI server files found"
            
            end_time = datetime.utcnow()
            execution_time = (end_time - start_time).total_seconds()
            
            test_result = TestResult(
                test_name=test_name,
                test_category="code_analysis",
                status=status,
                start_time=start_time,
                end_time=end_time,
                execution_time=execution_time,
                evidence_ids=[evidence_id],
                metrics={
                    "server_files": found_files,
                    "searched_paths": len(searched_paths),
                    "files_found": len(found_files)
                },
                error_details=error_details,
                assertions_passed=assertions_passed,
                assertions_failed=assertions_failed
            )
            
            log_test_end(
                self.logger, test_name, "code_analysis", 
                status.value, execution_time,
                f"{len(found_files)} server files found"
            )
            
            return test_result
            
        except Exception as e:
            end_time = datetime.utcnow()
            execution_time = (end_time - start_time).total_seconds()
            
            self.logger.error(f"FastAPI file discovery failed: {e}")
            
            test_result = TestResult(
                test_name=test_name,
                test_category="code_analysis",
                status=TestStatus.ERROR,
                start_time=start_time,
                end_time=end_time,
                execution_time=execution_time,
                error_details=str(e),
                assertions_passed=0,
                assertions_failed=1
            )
            
            log_test_end(
                self.logger, test_name, "code_analysis", 
                "ERROR", execution_time, str(e)
            )
            
            return test_result
    
    def _find_files_with_fastapi_imports(self) -> List[str]:
        """Find Python files that import FastAPI."""
        fastapi_files = []
        
        # Search common directories
        search_dirs = ["src", ".", "backend", "api", "app"]
        
        for search_dir in search_dirs:
            if os.path.exists(search_dir):
                for root, dirs, files in os.walk(search_dir):
                    for file in files:
                        if file.endswith('.py'):
                            file_path = os.path.join(root, file)
                            try:
                                with open(file_path, 'r', encoding='utf-8') as f:
                                    content = f.read()
                                    if self._contains_fastapi_imports(content):
                                        fastapi_files.append(file_path)
                                        self.logger.debug(f"Found FastAPI imports in: {file_path}")
                            except Exception as e:
                                self.logger.debug(f"Could not read {file_path}: {e}")
        
        return fastapi_files
    
    def _contains_fastapi_imports(self, content: str) -> bool:
        """Check if file content contains FastAPI imports."""
        fastapi_patterns = [
            r'from\s+fastapi\s+import',
            r'import\s+fastapi',
            r'from\s+fastapi\.',
            r'FastAPI\s*\(',
            r'@app\.websocket',
            r'@app\.get',
            r'@app\.post'
        ]
        
        for pattern in fastapi_patterns:
            if re.search(pattern, content, re.IGNORECASE):
                return True
        
        return False
    
    def _analyze_server_file(self, file_path: str) -> TestResult:
        """Analyze a specific server file for FastAPI routes."""
        test_name = f"route_analysis_{os.path.basename(file_path)}"
        start_time = datetime.utcnow()
        
        log_test_start(self.logger, test_name, "code_analysis")
        
        try:
            # Read and parse the file
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Parse AST
            try:
                tree = ast.parse(content, filename=file_path)
            except SyntaxError as e:
                raise ValidationError(
                    "CODE_ANALYSIS_ERROR",
                    f"Syntax error in {file_path}: {e}",
                    {"file_path": file_path, "syntax_error": str(e)}
                )
            
            # Analyze the AST for routes
            route_analysis = self._extract_routes_from_ast(tree, file_path)
            
            # Store analysis results as evidence
            analysis_data = {
                "file_path": file_path,
                "file_size": len(content),
                "line_count": content.count('\n') + 1,
                "route_analysis": {
                    "total_routes": route_analysis.total_routes,
                    "websocket_routes": route_analysis.websocket_routes,
                    "http_routes": route_analysis.http_routes,
                    "route_handlers": route_analysis.route_handlers,
                    "middleware_count": route_analysis.middleware_count,
                    "dependencies": route_analysis.dependencies
                },
                "analysis_timestamp": route_analysis.analysis_timestamp.isoformat()
            }
            
            evidence_id = self.evidence_collector.snapshot_configuration(
                config_type="route_analysis",
                config_data=analysis_data
            )
            
            # Determine test status
            if route_analysis.websocket_routes:
                status = TestStatus.PASSED
                assertions_passed = len(route_analysis.websocket_routes)
                assertions_failed = 0
                error_details = None
            else:
                status = TestStatus.FAILED
                assertions_passed = 0
                assertions_failed = 1
                error_details = f"No WebSocket routes found in {file_path}"
            
            end_time = datetime.utcnow()
            execution_time = (end_time - start_time).total_seconds()
            
            test_result = TestResult(
                test_name=test_name,
                test_category="code_analysis",
                status=status,
                start_time=start_time,
                end_time=end_time,
                execution_time=execution_time,
                evidence_ids=[evidence_id],
                metrics={
                    "file_path": file_path,
                    "total_routes": route_analysis.total_routes,
                    "websocket_routes": len(route_analysis.websocket_routes),
                    "http_routes": len(route_analysis.http_routes),
                    "route_handlers": len(route_analysis.route_handlers),
                    "middleware_count": route_analysis.middleware_count,
                    "dependencies": len(route_analysis.dependencies)
                },
                error_details=error_details,
                assertions_passed=assertions_passed,
                assertions_failed=assertions_failed
            )
            
            log_test_end(
                self.logger, test_name, "code_analysis", 
                status.value, execution_time,
                f"{len(route_analysis.websocket_routes)} WebSocket routes found"
            )
            
            return test_result
            
        except Exception as e:
            end_time = datetime.utcnow()
            execution_time = (end_time - start_time).total_seconds()
            
            self.logger.error(f"Route analysis failed for {file_path}: {e}")
            
            test_result = TestResult(
                test_name=test_name,
                test_category="code_analysis",
                status=TestStatus.ERROR,
                start_time=start_time,
                end_time=end_time,
                execution_time=execution_time,
                error_details=str(e),
                assertions_passed=0,
                assertions_failed=1
            )
            
            log_test_end(
                self.logger, test_name, "code_analysis", 
                "ERROR", execution_time, str(e)
            )
            
            return test_result
    
    def _extract_routes_from_ast(self, tree: ast.AST, file_path: str) -> RouteAnalysis:
        """Extract route information from AST."""
        websocket_routes = []
        http_routes = []
        route_handlers = {}
        dependencies = []
        middleware_count = 0
        
        # Walk through all nodes in the AST
        for node in ast.walk(tree):
            # Look for function definitions with decorators (both sync and async)
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                for decorator in node.decorator_list:
                    route_info = self._analyze_decorator(decorator, node.name)
                    if route_info:
                        route_type, route_path = route_info
                        if route_type == "websocket":
                            websocket_routes.append(route_path)
                            route_handlers[route_path] = node.name
                        else:
                            http_routes.append(route_path)
                            route_handlers[route_path] = node.name
            
            # Look for imports to identify dependencies
            elif isinstance(node, ast.Import):
                for alias in node.names:
                    if self._is_relevant_dependency(alias.name):
                        dependencies.append(alias.name)
            
            elif isinstance(node, ast.ImportFrom):
                if node.module and self._is_relevant_dependency(node.module):
                    dependencies.append(node.module)
                    for alias in node.names:
                        dependencies.append(f"{node.module}.{alias.name}")
            
            # Look for middleware (simplified detection)
            elif isinstance(node, ast.Call):
                if self._is_middleware_call(node):
                    middleware_count += 1
        
        return RouteAnalysis(
            total_routes=len(websocket_routes) + len(http_routes),
            websocket_routes=websocket_routes,
            http_routes=http_routes,
            route_handlers=route_handlers,
            middleware_count=middleware_count,
            dependencies=list(set(dependencies)),  # Remove duplicates
            analysis_timestamp=datetime.utcnow()
        )
    
    def _analyze_decorator(self, decorator: ast.AST, function_name: str) -> Optional[Tuple[str, str]]:
        """Analyze a decorator to extract route information."""
        # Handle @app.websocket("/path")
        if isinstance(decorator, ast.Call):
            if isinstance(decorator.func, ast.Attribute):
                if decorator.func.attr in ["websocket", "get", "post", "put", "delete", "patch"]:
                    # Extract the route path
                    if decorator.args and isinstance(decorator.args[0], ast.Str):
                        route_path = decorator.args[0].s
                        return decorator.func.attr, route_path
                    elif decorator.args and isinstance(decorator.args[0], ast.Constant):
                        route_path = decorator.args[0].value
                        return decorator.func.attr, route_path
        
        # Handle @app.websocket without parentheses (less common)
        elif isinstance(decorator, ast.Attribute):
            if decorator.attr in ["websocket", "get", "post", "put", "delete", "patch"]:
                # No explicit path, might use function name
                return decorator.attr, f"/{function_name}"
        
        return None
    
    def _is_relevant_dependency(self, module_name: str) -> bool:
        """Check if a module is relevant for WebSocket analysis."""
        relevant_modules = [
            "fastapi",
            "websockets",
            "starlette",
            "uvicorn",
            "asyncio",
            "websocket",
            "socket",
            "aiohttp"
        ]
        
        return any(relevant in module_name.lower() for relevant in relevant_modules)
    
    def _is_middleware_call(self, node: ast.Call) -> bool:
        """Check if a call is middleware-related."""
        if isinstance(node.func, ast.Attribute):
            if node.func.attr in ["add_middleware", "middleware"]:
                return True
        
        return False
    
    def verify_websocket_handlers(self) -> List[TestResult]:
        """
        Verify WebSocket handler implementations.
        
        Implements requirements 2.2, 2.4, 2.5:
        - Analyze WebSocket handler function implementations
        - Verify proper WebSocket accept/receive/send logic
        - Check for error handling and connection management code
        - Validate WebSocket library usage and integration
        
        Returns:
            List[TestResult]: Results from WebSocket handler analysis
        """
        self.logger.info("Verifying WebSocket handlers")
        results = []
        
        # First, discover FastAPI files to get WebSocket routes
        discovery_result = self._discover_fastapi_files()
        if discovery_result.status != TestStatus.PASSED:
            self.logger.warning("No FastAPI files found for handler analysis")
            return [
                TestResult(
                    test_name="websocket_handler_analysis",
                    test_category="code_analysis",
                    status=TestStatus.FAILED,
                    error_details="No FastAPI files found for analysis",
                    start_time=datetime.utcnow(),
                    end_time=datetime.utcnow(),
                    execution_time=0.1
                )
            ]
        
        server_files = discovery_result.metrics.get("server_files", [])
        
        # Analyze handlers in each server file
        for server_file in server_files:
            handler_result = self._analyze_websocket_handlers_in_file(server_file)
            results.append(handler_result)
        
        return results
    
    def _analyze_websocket_handlers_in_file(self, file_path: str) -> TestResult:
        """Analyze WebSocket handlers in a specific file."""
        test_name = f"websocket_handler_analysis_{os.path.basename(file_path)}"
        start_time = datetime.utcnow()
        
        log_test_start(self.logger, test_name, "code_analysis")
        
        try:
            # Read and parse the file
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Parse AST
            try:
                tree = ast.parse(content, filename=file_path)
            except SyntaxError as e:
                raise ValidationError(
                    "CODE_ANALYSIS_ERROR",
                    f"Syntax error in {file_path}: {e}",
                    {"file_path": file_path, "syntax_error": str(e)}
                )
            
            # Extract WebSocket handlers and analyze them
            handler_analyses = self._analyze_websocket_handlers_in_ast(tree, file_path)
            
            # Store analysis results as evidence
            analysis_data = {
                "file_path": file_path,
                "file_size": len(content),
                "line_count": content.count('\n') + 1,
                "handlers_analyzed": len(handler_analyses),
                "handler_analyses": [
                    {
                        "handler_name": analysis.handler_name,
                        "has_accept_logic": analysis.has_accept_logic,
                        "has_receive_logic": analysis.has_receive_logic,
                        "has_send_logic": analysis.has_send_logic,
                        "has_error_handling": analysis.has_error_handling,
                        "imports_websocket": analysis.imports_websocket,
                        "complexity_score": analysis.complexity_score,
                        "line_count": analysis.line_count
                    }
                    for analysis in handler_analyses
                ],
                "analysis_timestamp": datetime.utcnow().isoformat()
            }
            
            evidence_id = self.evidence_collector.snapshot_configuration(
                config_type="websocket_handler_analysis",
                config_data=analysis_data
            )
            
            # Calculate overall quality metrics
            total_handlers = len(handler_analyses)
            if total_handlers == 0:
                status = TestStatus.FAILED
                assertions_passed = 0
                assertions_failed = 1
                error_details = f"No WebSocket handlers found in {file_path}"
            else:
                # Count handlers with proper implementation
                proper_handlers = sum(1 for h in handler_analyses 
                                    if h.has_accept_logic and h.has_receive_logic and h.has_send_logic)
                handlers_with_error_handling = sum(1 for h in handler_analyses if h.has_error_handling)
                
                # Determine status based on implementation quality
                if proper_handlers >= total_handlers * 0.8:  # 80% threshold
                    status = TestStatus.PASSED
                    assertions_passed = proper_handlers
                    assertions_failed = total_handlers - proper_handlers
                    error_details = None
                else:
                    status = TestStatus.FAILED
                    assertions_passed = proper_handlers
                    assertions_failed = total_handlers - proper_handlers
                    error_details = f"Only {proper_handlers}/{total_handlers} handlers have proper WebSocket implementation"
            
            end_time = datetime.utcnow()
            execution_time = (end_time - start_time).total_seconds()
            
            test_result = TestResult(
                test_name=test_name,
                test_category="code_analysis",
                status=status,
                start_time=start_time,
                end_time=end_time,
                execution_time=execution_time,
                evidence_ids=[evidence_id],
                metrics={
                    "file_path": file_path,
                    "total_handlers": total_handlers,
                    "proper_handlers": proper_handlers if total_handlers > 0 else 0,
                    "handlers_with_error_handling": handlers_with_error_handling if total_handlers > 0 else 0,
                    "average_complexity": sum(h.complexity_score for h in handler_analyses) / total_handlers if total_handlers > 0 else 0,
                    "average_line_count": sum(h.line_count for h in handler_analyses) / total_handlers if total_handlers > 0 else 0
                },
                error_details=error_details,
                assertions_passed=assertions_passed,
                assertions_failed=assertions_failed
            )
            
            log_test_end(
                self.logger, test_name, "code_analysis", 
                status.value, execution_time,
                f"{proper_handlers if total_handlers > 0 else 0}/{total_handlers} handlers properly implemented"
            )
            
            return test_result
            
        except Exception as e:
            end_time = datetime.utcnow()
            execution_time = (end_time - start_time).total_seconds()
            
            self.logger.error(f"WebSocket handler analysis failed for {file_path}: {e}")
            
            test_result = TestResult(
                test_name=test_name,
                test_category="code_analysis",
                status=TestStatus.ERROR,
                start_time=start_time,
                end_time=end_time,
                execution_time=execution_time,
                error_details=str(e),
                assertions_passed=0,
                assertions_failed=1
            )
            
            log_test_end(
                self.logger, test_name, "code_analysis", 
                "ERROR", execution_time, str(e)
            )
            
            return test_result
    
    def _analyze_websocket_handlers_in_ast(self, tree: ast.AST, file_path: str) -> List[HandlerAnalysis]:
        """Analyze WebSocket handlers in an AST."""
        handler_analyses = []
        
        # Walk through all nodes to find WebSocket handlers
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                # Check if this function is a WebSocket handler
                is_websocket_handler = False
                for decorator in node.decorator_list:
                    route_info = self._analyze_decorator(decorator, node.name)
                    if route_info and route_info[0] == "websocket":
                        is_websocket_handler = True
                        break
                
                if is_websocket_handler:
                    analysis = self._analyze_single_websocket_handler(node, file_path)
                    handler_analyses.append(analysis)
        
        return handler_analyses
    
    def _analyze_single_websocket_handler(self, func_node: ast.AST, file_path: str) -> HandlerAnalysis:
        """Analyze a single WebSocket handler function."""
        handler_name = func_node.name
        
        # Initialize analysis results
        has_accept_logic = False
        has_receive_logic = False
        has_send_logic = False
        has_error_handling = False
        imports_websocket = False
        complexity_score = 0
        line_count = 0
        
        # Calculate line count
        if hasattr(func_node, 'lineno') and hasattr(func_node, 'end_lineno'):
            line_count = func_node.end_lineno - func_node.lineno + 1
        
        # Check function parameters for WebSocket parameter
        websocket_param_found = False
        if hasattr(func_node, 'args'):
            for arg in func_node.args.args:
                if 'websocket' in arg.arg.lower():
                    websocket_param_found = True
                    imports_websocket = True
                    break
        
        # Analyze function body
        for node in ast.walk(func_node):
            # Count complexity indicators
            if isinstance(node, (ast.If, ast.For, ast.While, ast.Try, ast.With)):
                complexity_score += 1
            
            # Look for WebSocket operations
            if isinstance(node, ast.Attribute):
                attr_name = node.attr.lower()
                if 'accept' in attr_name:
                    has_accept_logic = True
                elif 'receive' in attr_name or 'recv' in attr_name:
                    has_receive_logic = True
                elif 'send' in attr_name:
                    has_send_logic = True
            
            # Look for await calls (common in WebSocket handlers)
            elif isinstance(node, ast.Await):
                if isinstance(node.value, ast.Attribute):
                    attr_name = node.value.attr.lower()
                    if 'accept' in attr_name:
                        has_accept_logic = True
                    elif 'receive' in attr_name or 'recv' in attr_name:
                        has_receive_logic = True
                    elif 'send' in attr_name:
                        has_send_logic = True
            
            # Look for error handling
            elif isinstance(node, (ast.Try, ast.ExceptHandler)):
                has_error_handling = True
            
            # Look for WebSocket-related exceptions
            elif isinstance(node, ast.Name):
                if 'disconnect' in node.id.lower() or 'websocket' in node.id.lower():
                    has_error_handling = True
        
        return HandlerAnalysis(
            handler_name=handler_name,
            has_accept_logic=has_accept_logic,
            has_receive_logic=has_receive_logic,
            has_send_logic=has_send_logic,
            has_error_handling=has_error_handling,
            imports_websocket=imports_websocket,
            complexity_score=complexity_score,
            line_count=line_count,
            analysis_timestamp=datetime.utcnow()
        )
    
    def check_dependency_imports(self) -> List[TestResult]:
        """
        Check dependency imports (placeholder).
        
        This will be implemented in task 3.3.
        """
        self.logger.info("Checking dependency imports (placeholder)")
        
        return [
            TestResult(
                test_name="dependency_imports_placeholder",
                test_category="code_analysis",
                status=TestStatus.PASSED,
                start_time=datetime.utcnow(),
                end_time=datetime.utcnow(),
                execution_time=0.1
            )
        ]
    
    def assess_implementation_completeness(self) -> CompletenessAnalysis:
        """
        Assess overall implementation completeness (placeholder).
        
        This will be enhanced as more analysis capabilities are added.
        """
        return CompletenessAnalysis(
            total_features=0,
            implemented_features=0,
            missing_features=[],
            partial_features=[],
            completeness_percentage=0.0,
            analysis_timestamp=datetime.utcnow()
        )