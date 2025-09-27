"""
Unit tests for CodeAnalysisTester.
"""

import ast
import os
import tempfile
import pytest
from datetime import datetime
from unittest.mock import Mock, patch, mock_open

from src.websocket_validation.testers.code_analysis import CodeAnalysisTester
from src.websocket_validation.config import ValidationConfig
from src.websocket_validation.collectors import EvidenceCollector
from src.websocket_validation.models import TestStatus, RouteAnalysis


class TestCodeAnalysisTester:
    """Test CodeAnalysisTester functionality."""
    
    @pytest.fixture
    def config(self):
        """Create test configuration."""
        return ValidationConfig(
            evidence_dir="test_evidence"
        )
    
    @pytest.fixture
    def evidence_collector(self, config):
        """Create evidence collector for testing."""
        return EvidenceCollector(config)
    
    @pytest.fixture
    def code_tester(self, config, evidence_collector):
        """Create CodeAnalysisTester instance."""
        return CodeAnalysisTester(config, evidence_collector)
    
    def test_initialization(self, config, evidence_collector):
        """Test CodeAnalysisTester initialization."""
        tester = CodeAnalysisTester(config, evidence_collector)
        
        assert tester.config == config
        assert tester.evidence_collector == evidence_collector
        assert tester.logger is not None
        assert len(tester.search_paths) > 0
        assert "server.py" in tester.search_paths
        assert "src/beast_mode/observatory/server.py" in tester.search_paths
    
    def test_contains_fastapi_imports(self, code_tester):
        """Test FastAPI import detection."""
        # Test various FastAPI import patterns
        test_cases = [
            ("from fastapi import FastAPI", True),
            ("import fastapi", True),
            ("from fastapi.websockets import WebSocket", True),
            ("app = FastAPI()", True),
            ("@app.websocket('/ws')", True),
            ("@app.get('/api')", True),
            ("import requests", False),
            ("from django import models", False),
            ("print('hello world')", False)
        ]
        
        for content, expected in test_cases:
            result = code_tester._contains_fastapi_imports(content)
            assert result == expected, f"Failed for content: {content}"
    
    def test_analyze_decorator_websocket(self, code_tester):
        """Test WebSocket decorator analysis."""
        # Create AST for @app.websocket("/ws/test")
        code = '''
@app.websocket("/ws/test")
async def websocket_endpoint(websocket):
    pass
'''
        tree = ast.parse(code)
        func_node = tree.body[0]
        decorator = func_node.decorator_list[0]
        
        result = code_tester._analyze_decorator(decorator, "websocket_endpoint")
        
        assert result is not None
        route_type, route_path = result
        assert route_type == "websocket"
        assert route_path == "/ws/test"
    
    def test_analyze_decorator_http(self, code_tester):
        """Test HTTP decorator analysis."""
        # Create AST for @app.get("/api/test")
        code = '''
@app.get("/api/test")
async def get_endpoint():
    pass
'''
        tree = ast.parse(code)
        func_node = tree.body[0]
        decorator = func_node.decorator_list[0]
        
        result = code_tester._analyze_decorator(decorator, "get_endpoint")
        
        assert result is not None
        route_type, route_path = result
        assert route_type == "get"
        assert route_path == "/api/test"
    
    def test_analyze_decorator_no_route(self, code_tester):
        """Test decorator analysis with non-route decorator."""
        # Create AST for @property
        code = '''
@property
def some_property(self):
    pass
'''
        tree = ast.parse(code)
        func_node = tree.body[0]
        decorator = func_node.decorator_list[0]
        
        result = code_tester._analyze_decorator(decorator, "some_property")
        
        assert result is None
    
    def test_is_relevant_dependency(self, code_tester):
        """Test relevant dependency detection."""
        test_cases = [
            ("fastapi", True),
            ("websockets", True),
            ("starlette", True),
            ("uvicorn", True),
            ("asyncio", True),
            ("requests", False),
            ("django", False),
            ("flask", False),
            ("fastapi.websockets", True),
            ("websocket.client", True)
        ]
        
        for module_name, expected in test_cases:
            result = code_tester._is_relevant_dependency(module_name)
            assert result == expected, f"Failed for module: {module_name}"
    
    def test_extract_routes_from_ast_websocket(self, code_tester):
        """Test route extraction from AST with WebSocket routes."""
        code = '''
from fastapi import FastAPI
from fastapi.websockets import WebSocket

app = FastAPI()

@app.websocket("/ws/emoji-rain")
async def emoji_rain_endpoint(websocket: WebSocket):
    await websocket.accept()
    
@app.websocket("/ws/status")
async def status_endpoint(websocket: WebSocket):
    await websocket.accept()

@app.get("/api/health")
async def health_check():
    return {"status": "ok"}
'''
        tree = ast.parse(code)
        analysis = code_tester._extract_routes_from_ast(tree, "test_server.py")
        
        assert isinstance(analysis, RouteAnalysis)
        assert analysis.total_routes == 3
        assert len(analysis.websocket_routes) == 2
        assert len(analysis.http_routes) == 1
        assert "/ws/emoji-rain" in analysis.websocket_routes
        assert "/ws/status" in analysis.websocket_routes
        assert "/api/health" in analysis.http_routes
        assert analysis.route_handlers["/ws/emoji-rain"] == "emoji_rain_endpoint"
        assert analysis.route_handlers["/ws/status"] == "status_endpoint"
        assert analysis.route_handlers["/api/health"] == "health_check"
        assert "fastapi" in analysis.dependencies
        assert "fastapi.websockets" in analysis.dependencies
    
    def test_extract_routes_from_ast_no_routes(self, code_tester):
        """Test route extraction from AST with no routes."""
        code = '''
import os
import sys

def helper_function():
    return "helper"

class UtilityClass:
    def method(self):
        pass
'''
        tree = ast.parse(code)
        analysis = code_tester._extract_routes_from_ast(tree, "test_utils.py")
        
        assert isinstance(analysis, RouteAnalysis)
        assert analysis.total_routes == 0
        assert len(analysis.websocket_routes) == 0
        assert len(analysis.http_routes) == 0
        assert len(analysis.route_handlers) == 0
        assert len(analysis.dependencies) == 0  # No relevant dependencies
    
    @patch('os.path.exists')
    def test_discover_fastapi_files_found(self, mock_exists, code_tester):
        """Test FastAPI file discovery when files exist."""
        # Mock that server.py exists
        mock_exists.side_effect = lambda path: path == "server.py"
        
        with patch.object(code_tester, '_find_files_with_fastapi_imports', return_value=["src/app.py"]):
            result = code_tester._discover_fastapi_files()
        
        assert result.status == TestStatus.PASSED
        assert result.test_name == "fastapi_file_discovery"
        assert result.test_category == "code_analysis"
        assert result.assertions_passed == 2  # server.py + src/app.py
        assert result.assertions_failed == 0
        assert "server.py" in result.metrics["server_files"]
        assert "src/app.py" in result.metrics["server_files"]
    
    @patch('os.path.exists')
    def test_discover_fastapi_files_not_found(self, mock_exists, code_tester):
        """Test FastAPI file discovery when no files exist."""
        # Mock that no files exist
        mock_exists.return_value = False
        
        with patch.object(code_tester, '_find_files_with_fastapi_imports', return_value=[]):
            result = code_tester._discover_fastapi_files()
        
        assert result.status == TestStatus.FAILED
        assert result.test_name == "fastapi_file_discovery"
        assert result.test_category == "code_analysis"
        assert result.assertions_passed == 0
        assert result.assertions_failed == 1
        assert result.error_details == "No FastAPI server files found"
        assert result.metrics["files_found"] == 0
    
    def test_analyze_server_file_success(self, code_tester):
        """Test successful server file analysis."""
        server_code = '''
from fastapi import FastAPI
from fastapi.websockets import WebSocket

app = FastAPI()

@app.websocket("/ws/test")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    await websocket.send_text("Hello WebSocket!")

@app.get("/api/status")
async def status():
    return {"status": "ok"}
'''
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(server_code)
            temp_file = f.name
        
        try:
            result = code_tester._analyze_server_file(temp_file)
            
            assert result.status == TestStatus.PASSED
            assert result.test_category == "code_analysis"
            assert result.assertions_passed == 1  # 1 WebSocket route found
            assert result.assertions_failed == 0
            assert result.metrics["websocket_routes"] == 1
            assert result.metrics["http_routes"] == 1
            assert result.metrics["total_routes"] == 2
            
        finally:
            os.unlink(temp_file)
    
    def test_analyze_server_file_no_websocket_routes(self, code_tester):
        """Test server file analysis with no WebSocket routes."""
        server_code = '''
from fastapi import FastAPI

app = FastAPI()

@app.get("/api/status")
async def status():
    return {"status": "ok"}

@app.post("/api/data")
async def create_data():
    return {"message": "created"}
'''
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(server_code)
            temp_file = f.name
        
        try:
            result = code_tester._analyze_server_file(temp_file)
            
            assert result.status == TestStatus.FAILED
            assert result.test_category == "code_analysis"
            assert result.assertions_passed == 0
            assert result.assertions_failed == 1
            assert result.metrics["websocket_routes"] == 0
            assert result.metrics["http_routes"] == 2
            assert result.metrics["total_routes"] == 2
            assert "No WebSocket routes found" in result.error_details
            
        finally:
            os.unlink(temp_file)
    
    def test_analyze_server_file_syntax_error(self, code_tester):
        """Test server file analysis with syntax error."""
        invalid_code = '''
from fastapi import FastAPI

app = FastAPI(

# Missing closing parenthesis - syntax error
'''
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(invalid_code)
            temp_file = f.name
        
        try:
            result = code_tester._analyze_server_file(temp_file)
            
            assert result.status == TestStatus.ERROR
            assert result.test_category == "code_analysis"
            assert result.assertions_passed == 0
            assert result.assertions_failed == 1
            assert "Syntax error" in result.error_details
            
        finally:
            os.unlink(temp_file)
    
    def test_analyze_server_file_not_found(self, code_tester):
        """Test server file analysis with non-existent file."""
        result = code_tester._analyze_server_file("non_existent_file.py")
        
        assert result.status == TestStatus.ERROR
        assert result.test_category == "code_analysis"
        assert result.assertions_passed == 0
        assert result.assertions_failed == 1
        assert result.error_details is not None
    
    @patch('os.walk')
    @patch('os.path.exists')
    def test_find_files_with_fastapi_imports(self, mock_exists, mock_walk, code_tester):
        """Test finding files with FastAPI imports."""
        # Mock directory structure
        mock_exists.side_effect = lambda path: path in ["src", "."]
        mock_walk.side_effect = [
            [("src", [], ["server.py", "utils.py", "models.py"])],
            [(".", [], ["main.py", "config.py"])]
        ]
        
        # Mock file reading
        file_contents = {
            "src/server.py": "from fastapi import FastAPI\napp = FastAPI()",
            "src/utils.py": "import os\nimport sys",
            "src/models.py": "from pydantic import BaseModel",
            "main.py": "from fastapi.websockets import WebSocket",
            "config.py": "DEBUG = True"
        }
        
        def mock_open_func(file_path, *args, **kwargs):
            content = file_contents.get(file_path, "")
            return mock_open(read_data=content).return_value
        
        with patch('builtins.open', side_effect=mock_open_func):
            result = code_tester._find_files_with_fastapi_imports()
        
        assert "src/server.py" in result
        assert "main.py" in result
        assert "src/utils.py" not in result
        assert "config.py" not in result
    
    def test_run_all_tests_integration(self, code_tester):
        """Test the complete run_all_tests method."""
        with patch.object(code_tester, 'analyze_fastapi_routes', return_value=[
            Mock(test_name="test1", status=TestStatus.PASSED)
        ]):
            with patch.object(code_tester, 'verify_websocket_handlers', return_value=[
                Mock(test_name="test2", status=TestStatus.PASSED)
            ]):
                with patch.object(code_tester, 'check_dependency_imports', return_value=[
                    Mock(test_name="test3", status=TestStatus.PASSED)
                ]):
                    results = code_tester.run_all_tests()
        
        assert len(results) == 3
        assert all(hasattr(result, 'test_name') for result in results)
        assert all(hasattr(result, 'status') for result in results)


class TestWebSocketHandlerAnalysis:
    """Test WebSocket handler analysis functionality."""
    
    @pytest.fixture
    def config(self):
        """Create test configuration."""
        return ValidationConfig(evidence_dir="test_evidence")
    
    @pytest.fixture
    def evidence_collector(self, config):
        """Create evidence collector for testing."""
        return EvidenceCollector(config)
    
    @pytest.fixture
    def code_tester(self, config, evidence_collector):
        """Create CodeAnalysisTester instance."""
        return CodeAnalysisTester(config, evidence_collector)
    
    def test_analyze_single_websocket_handler_complete(self, code_tester):
        """Test analysis of a complete WebSocket handler."""
        handler_code = '''
@app.websocket("/ws/test")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_text()
            await websocket.send_text(f"Echo: {data}")
    except WebSocketDisconnect:
        pass
'''
        tree = ast.parse(handler_code)
        func_node = tree.body[0]  # The function definition
        
        analysis = code_tester._analyze_single_websocket_handler(func_node, "test.py")
        
        assert analysis.handler_name == "websocket_endpoint"
        assert analysis.has_accept_logic == True
        assert analysis.has_receive_logic == True
        assert analysis.has_send_logic == True
        assert analysis.has_error_handling == True
        assert analysis.imports_websocket == True
        assert analysis.complexity_score >= 2  # try block + while loop
        assert analysis.line_count > 0
    
    def test_analyze_single_websocket_handler_incomplete(self, code_tester):
        """Test analysis of an incomplete WebSocket handler."""
        handler_code = '''
@app.websocket("/ws/incomplete")
async def incomplete_handler(websocket: WebSocket):
    await websocket.accept()
    # Missing receive/send logic and error handling
    pass
'''
        tree = ast.parse(handler_code)
        func_node = tree.body[0]
        
        analysis = code_tester._analyze_single_websocket_handler(func_node, "test.py")
        
        assert analysis.handler_name == "incomplete_handler"
        assert analysis.has_accept_logic == True
        assert analysis.has_receive_logic == False
        assert analysis.has_send_logic == False
        assert analysis.has_error_handling == False
        assert analysis.imports_websocket == True
    
    def test_analyze_single_websocket_handler_no_websocket_param(self, code_tester):
        """Test analysis of handler without WebSocket parameter."""
        handler_code = '''
@app.websocket("/ws/noparam")
async def no_param_handler():
    # No websocket parameter
    pass
'''
        tree = ast.parse(handler_code)
        func_node = tree.body[0]
        
        analysis = code_tester._analyze_single_websocket_handler(func_node, "test.py")
        
        assert analysis.handler_name == "no_param_handler"
        assert analysis.imports_websocket == False
        assert analysis.has_accept_logic == False
        assert analysis.has_receive_logic == False
        assert analysis.has_send_logic == False
    
    def test_analyze_websocket_handlers_in_ast(self, code_tester):
        """Test analysis of multiple WebSocket handlers in AST."""
        code = '''
from fastapi import FastAPI, WebSocket, WebSocketDisconnect

app = FastAPI()

@app.websocket("/ws/good")
async def good_handler(websocket: WebSocket):
    await websocket.accept()
    try:
        data = await websocket.receive_text()
        await websocket.send_text(data)
    except WebSocketDisconnect:
        pass

@app.websocket("/ws/bad")
async def bad_handler(websocket: WebSocket):
    # Missing proper implementation
    pass

@app.get("/api/not-websocket")
async def http_handler():
    return {"message": "not a websocket"}
'''
        tree = ast.parse(code)
        analyses = code_tester._analyze_websocket_handlers_in_ast(tree, "test.py")
        
        assert len(analyses) == 2  # Only WebSocket handlers
        
        # Check good handler
        good_handler = next(a for a in analyses if a.handler_name == "good_handler")
        assert good_handler.has_accept_logic == True
        assert good_handler.has_receive_logic == True
        assert good_handler.has_send_logic == True
        assert good_handler.has_error_handling == True
        
        # Check bad handler
        bad_handler = next(a for a in analyses if a.handler_name == "bad_handler")
        assert bad_handler.has_accept_logic == False
        assert bad_handler.has_receive_logic == False
        assert bad_handler.has_send_logic == False
        assert bad_handler.has_error_handling == False
    
    def test_analyze_websocket_handlers_in_file_success(self, code_tester):
        """Test successful analysis of WebSocket handlers in a file."""
        websocket_code = '''
from fastapi import FastAPI, WebSocket, WebSocketDisconnect

app = FastAPI()

@app.websocket("/ws/emoji-rain")
async def emoji_rain_handler(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_text()
            await websocket.send_text(f"🌧️ {data}")
    except WebSocketDisconnect:
        print("Client disconnected")

@app.websocket("/ws/status")
async def status_handler(websocket: WebSocket):
    await websocket.accept()
    await websocket.send_json({"status": "connected"})
'''
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(websocket_code)
            temp_file = f.name
        
        try:
            result = code_tester._analyze_websocket_handlers_in_file(temp_file)
            
            assert result.status == TestStatus.PASSED  # 1/2 handlers properly implemented (50% < 80% threshold)
            assert result.test_category == "code_analysis"
            assert result.metrics["total_handlers"] == 2
            assert result.metrics["proper_handlers"] >= 1  # At least emoji_rain_handler is proper
            assert len(result.evidence_ids) == 1
            
        finally:
            os.unlink(temp_file)
    
    def test_analyze_websocket_handlers_in_file_no_handlers(self, code_tester):
        """Test analysis of file with no WebSocket handlers."""
        no_websocket_code = '''
from fastapi import FastAPI

app = FastAPI()

@app.get("/api/health")
async def health_check():
    return {"status": "ok"}

@app.post("/api/data")
async def create_data(data: dict):
    return {"message": "created"}
'''
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(no_websocket_code)
            temp_file = f.name
        
        try:
            result = code_tester._analyze_websocket_handlers_in_file(temp_file)
            
            assert result.status == TestStatus.FAILED
            assert result.test_category == "code_analysis"
            assert result.metrics["total_handlers"] == 0
            assert "No WebSocket handlers found" in result.error_details
            
        finally:
            os.unlink(temp_file)
    
    def test_analyze_websocket_handlers_in_file_syntax_error(self, code_tester):
        """Test analysis of file with syntax errors."""
        invalid_code = '''
from fastapi import FastAPI

app = FastAPI(

# Missing closing parenthesis
'''
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(invalid_code)
            temp_file = f.name
        
        try:
            result = code_tester._analyze_websocket_handlers_in_file(temp_file)
            
            assert result.status == TestStatus.ERROR
            assert result.test_category == "code_analysis"
            assert "Syntax error" in result.error_details
            
        finally:
            os.unlink(temp_file)
    
    @patch.object(CodeAnalysisTester, '_discover_fastapi_files')
    def test_verify_websocket_handlers_no_files(self, mock_discovery, code_tester):
        """Test handler verification when no FastAPI files are found."""
        # Mock discovery to return failure
        mock_discovery.return_value = TestResult(
            test_name="discovery",
            status=TestStatus.FAILED,
            metrics={"server_files": []}
        )
        
        results = code_tester.verify_websocket_handlers()
        
        assert len(results) == 1
        assert results[0].status == TestStatus.FAILED
        assert "No FastAPI files found" in results[0].error_details
    
    @patch.object(CodeAnalysisTester, '_discover_fastapi_files')
    @patch.object(CodeAnalysisTester, '_analyze_websocket_handlers_in_file')
    def test_verify_websocket_handlers_with_files(self, mock_analyze, mock_discovery, code_tester):
        """Test handler verification with FastAPI files."""
        # Mock discovery to return success
        mock_discovery.return_value = TestResult(
            test_name="discovery",
            status=TestStatus.PASSED,
            metrics={"server_files": ["server1.py", "server2.py"]}
        )
        
        # Mock analysis results
        mock_analyze.return_value = TestResult(
            test_name="analysis",
            status=TestStatus.PASSED
        )
        
        results = code_tester.verify_websocket_handlers()
        
        assert len(results) == 2  # One for each server file
        assert mock_analyze.call_count == 2
        mock_analyze.assert_any_call("server1.py")
        mock_analyze.assert_any_call("server2.py")


class TestRouteAnalysisIntegration:
    """Integration tests for route analysis with real FastAPI code patterns."""
    
    @pytest.fixture
    def code_tester(self):
        """Create CodeAnalysisTester for integration testing."""
        config = ValidationConfig(evidence_dir="test_evidence")
        evidence_collector = EvidenceCollector(config)
        return CodeAnalysisTester(config, evidence_collector)
    
    def test_complex_fastapi_server_analysis(self, code_tester):
        """Test analysis of a complex FastAPI server file."""
        complex_server_code = '''
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.websockets import WebSocketState
import asyncio
import json

app = FastAPI(title="Observatory API", version="1.0.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

manager = ConnectionManager()

@app.websocket("/ws/emoji-rain")
async def emoji_rain_websocket(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_text()
            await websocket.send_text(f"Echo: {data}")
    except WebSocketDisconnect:
        pass

@app.websocket("/ws/status")
async def status_websocket(websocket: WebSocket):
    await websocket.accept()
    await websocket.send_json({"status": "connected"})

@app.websocket("/ws/health")
async def health_websocket(websocket: WebSocket):
    await websocket.accept()
    await websocket.send_json({"health": "ok"})

@app.get("/api/health")
async def health_check():
    return {"status": "healthy"}

@app.get("/api/status")
async def get_status():
    return {"status": "running"}

@app.post("/api/data")
async def create_data(data: dict):
    return {"message": "created", "data": data}

@app.put("/api/data/{item_id}")
async def update_data(item_id: int, data: dict):
    return {"message": "updated", "id": item_id}

@app.delete("/api/data/{item_id}")
async def delete_data(item_id: int):
    return {"message": "deleted", "id": item_id}
'''
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(complex_server_code)
            temp_file = f.name
        
        try:
            result = code_tester._analyze_server_file(temp_file)
            
            # Should pass because WebSocket routes are found
            assert result.status == TestStatus.PASSED
            assert result.metrics["websocket_routes"] == 3
            assert result.metrics["http_routes"] == 5
            assert result.metrics["total_routes"] == 8
            assert result.metrics["middleware_count"] >= 1  # CORS middleware
            
            # Check that evidence was collected
            assert len(result.evidence_ids) == 1
            
        finally:
            os.unlink(temp_file)
    
    def test_real_observatory_server_pattern(self, code_tester):
        """Test analysis pattern similar to actual Observatory server."""
        observatory_pattern = '''
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
import uvicorn

app = FastAPI()

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
async def read_root():
    return HTMLResponse(content="<h1>Observatory</h1>")

@app.websocket("/ws/emoji-rain")
async def emoji_rain_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            # Emoji rain logic would go here
            await asyncio.sleep(1)
            await websocket.send_text("🌧️")
    except WebSocketDisconnect:
        print("Client disconnected")

@app.get("/api/dashboard/all-data")
async def get_dashboard_data():
    return {"data": "dashboard"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8888)
'''
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(observatory_pattern)
            temp_file = f.name
        
        try:
            result = code_tester._analyze_server_file(temp_file)
            
            # Should pass - has WebSocket route
            assert result.status == TestStatus.PASSED
            assert result.metrics["websocket_routes"] == 1
            assert result.metrics["http_routes"] == 2
            assert "/ws/emoji-rain" in result.evidence_ids[0]  # Should be in evidence
            
        finally:
            os.unlink(temp_file)