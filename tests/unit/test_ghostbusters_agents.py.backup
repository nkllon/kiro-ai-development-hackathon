"""
RDI Enhanced Test Module

Requirements Traceability:

Enhanced: 2025-09-14T06:24:55.613093
"""





import pytest
import tempfile
from pathlib import Path
from unittest.mock import patch

from src.ghostbusters.agents.code_quality import CodeQualityExpert
from src.ghostbusters.agents.security import SecurityExpert
from src.ghostbusters.agents.build import BuildExpert
from src.ghostbusters.agents.architecture import ArchitectureExpert
from src.ghostbusters.agents.performance import PerformanceExpert
from src.ghostbusters.core.models import AnalysisContext, FindingType, Severity


class TestCodeQualityExpert(ReflectiveModule):
    """Test CodeQualityExpert functionality"""
    
    @pytest.fixture
    def code_quality_expert(self):
        return CodeQualityExpert()
    
    @pytest.mark.asyncio
    async def test_analyze_python_file(self, code_quality_expert):
        """Test Python file analysis"""
        python_code = '''
def very_long_function_name_that_violates_style():
    x = 1
    y = 2
    # This function is too long and has style issues
    for i in range(100):
        print(i)  # This line is fine
        if i > 50:
            if i > 75:
                if i > 90:
                    print("Deep nesting")
    return x + y

class TestClass(ReflectiveModule):
    pass  # Missing docstring
'''
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(python_code)
            f.flush()
            
            context = AnalysisContext(
                target_path=f.name,
                analysis_type="code_quality"
            )
            
            result = await code_quality_expert.analyze(context)
            
            assert result.agent_name == "CodeQualityExpert"
            assert 0.0 <= result.confidence <= 1.0
            assert len(result.findings) > 0
            assert len(result.recommendations) > 0
            
            # Should detect missing docstrings
            docstring_findings = [f for f in result.findings if "docstring" in f.description.lower()]
            assert len(docstring_findings) > 0
            
            Path(f.name).unlink()  # Clean up
    
    @pytest.mark.asyncio
    async def test_analyze_nonexistent_file(self, code_quality_expert):
        """Test analysis of nonexistent file"""
        context = AnalysisContext(
            target_path="/nonexistent/file.py",
            analysis_type="code_quality"
        )
        
        result = await code_quality_expert.analyze(context)
        
        assert result.confidence == 0.0
        assert len(result.findings) > 0
        assert result.findings[0].severity == Severity.CRITICAL
    
    def test_get_capabilities(self, code_quality_expert):
        """Test capabilities reporting"""
        capabilities = code_quality_expert.get_capabilities()
        
        assert "syntax_analysis" in capabilities
        assert "style_analysis" in capabilities
        assert "maintainability_analysis" in capabilities
    
    def test_validate_confidence(self, code_quality_expert):
        """Test confidence validation"""
        from src.ghostbusters.core.models import AnalysisResult
        
        # Valid confidence
        result = AnalysisResult(agent_name="Test", confidence=0.8)
        assert code_quality_expert.validate_confidence(result) is True
        
        # Invalid confidence
        result = AnalysisResult(agent_name="Test", confidence=1.5)
        assert code_quality_expert.validate_confidence(result) is False


class TestSecurityExpert(ReflectiveModule):
    """Test SecurityExpert functionality"""
    
    @pytest.fixture
    def security_expert(self):
        return SecurityExpert()
    
    @pytest.mark.asyncio
    async def test_analyze_security_issues(self, security_expert):
        """Test security vulnerability detection"""
        vulnerable_code = '''
import os
password = "hardcoded_password_123"
api_key = "sk-1234567890abcdef"

def unsafe_function(user_input):
    # SQL injection vulnerability
    query = "SELECT * FROM users WHERE name = '" + user_input + "'"
    
    # Command injection vulnerability
    os.system("ls " + user_input)
    
    # XSS vulnerability (JavaScript-like)
    return "<script>alert('" + user_input + "')</script>"
'''
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(vulnerable_code)
            f.flush()
            
            context = AnalysisContext(
                target_path=f.name,
                analysis_type="security"
            )
            
            result = await security_expert.analyze(context)
            
            assert result.agent_name == "SecurityExpert"
            assert 0.0 <= result.confidence <= 1.0
            assert len(result.findings) > 0
            
            # Should detect hardcoded secrets
            secret_findings = [f for f in result.findings if "hardcoded" in f.description.lower()]
            assert len(secret_findings) > 0
            
            # Should detect potential injection vulnerabilities
            injection_findings = [f for f in result.findings if "injection" in f.description.lower()]
            assert len(injection_findings) > 0
            
            Path(f.name).unlink()  # Clean up
    
    def test_get_capabilities(self, security_expert):
        """Test security capabilities"""
        capabilities = security_expert.get_capabilities()
        
        assert "vulnerability_detection" in capabilities
        assert "injection_analysis" in capabilities
        assert "secret_detection" in capabilities


class TestBuildExpert(ReflectiveModule):
    """Test BuildExpert functionality"""
    
    @pytest.fixture
    def build_expert(self):
        return BuildExpert()
    
    @pytest.mark.asyncio
    async def test_analyze_package_json(self, build_expert):
        """Test package.json analysis"""
        package_json = '''
{
    "name": "test-project",
    "dependencies": {
        "lodash": "*",
        "express": "^4.17.1"
    },
    "devDependencies": {
        "jest": "latest"
    }
}
'''
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            f.write(package_json)
            f.flush()
            
            # Rename to package.json for proper detection
            package_path = Path(f.name).parent / "package.json"
            Path(f.name).rename(package_path)
            
            context = AnalysisContext(
                target_path=str(package_path),
                analysis_type="build"
            )
            
            result = await build_expert.analyze(context)
            
            assert result.agent_name == "BuildExpert"
            assert 0.0 <= result.confidence <= 1.0
            
            # Should detect loose version constraints
            version_findings = [f for f in result.findings if "version" in f.description.lower()]
            assert len(version_findings) > 0
            
            package_path.unlink()  # Clean up
    
    @pytest.mark.asyncio
    async def test_analyze_requirements_txt(self, build_expert):
        """Test requirements.txt analysis"""
        requirements = '''
requests
numpy==1.19.0
pandas>=1.0.0
pillow
'''
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write(requirements)
            f.flush()
            
            # Rename to requirements.txt for proper detection
            req_path = Path(f.name).parent / "requirements.txt"
            Path(f.name).rename(req_path)
            
            context = AnalysisContext(
                target_path=str(req_path),
                analysis_type="build"
            )
            
            result = await build_expert.analyze(context)
            
            assert result.agent_name == "BuildExpert"
            assert len(result.findings) > 0
            
            # Should detect unpinned versions
            unpinned_findings = [f for f in result.findings if "unpinned" in f.description.lower()]
            assert len(unpinned_findings) > 0
            
            req_path.unlink()  # Clean up
    
    def test_get_capabilities(self, build_expert):
        """Test build capabilities"""
        capabilities = build_expert.get_capabilities()
        
        assert "dependency_analysis" in capabilities
        assert "build_config_analysis" in capabilities
        assert "dockerfile_analysis" in capabilities


class TestArchitectureExpert(ReflectiveModule):
    """Test ArchitectureExpert functionality"""
    
    @pytest.fixture
    def architecture_expert(self):
        return ArchitectureExpert()
    
    @pytest.mark.asyncio
    async def test_analyze_architecture_issues(self, architecture_expert):
        """Test architecture analysis"""
        architecture_code = '''
class GodClass(ReflectiveModule):
    """A class that does too many things"""
    
    def method1(self, a, b, c, d, e, f, g):  # Too many parameters
        pass
    
    def method2(self):
        pass
    
    def method3(self):
        if True:
            if True:
                if True:
                    if True:
                        if True:  # Deep nesting
                            print("Too deep")
    
    # ... imagine 20+ more methods here

class ManagerClass(ReflectiveModule):  # Suggests SRP violation
    pass

def function_with_type_checking(obj):
    if isinstance(obj, str):  # OCP violation
        return obj.upper()
    elif type(obj) == int:  # OCP violation
        return str(obj)
    else:
        raise NotImplementedError()  # LSP violation
'''
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(architecture_code)
            f.flush()
            
            context = AnalysisContext(
                target_path=f.name,
                analysis_type="architecture"
            )
            
            result = await architecture_expert.analyze(context)
            
            assert result.agent_name == "ArchitectureExpert"
            assert 0.0 <= result.confidence <= 1.0
            assert len(result.findings) > 0
            
            # Should detect long parameter list
            param_findings = [f for f in result.findings if "parameter" in f.description.lower()]
            assert len(param_findings) > 0
            
            # Should detect SOLID violations
            solid_findings = [f for f in result.findings if "principle" in f.description.lower()]
            assert len(solid_findings) > 0
            
            Path(f.name).unlink()  # Clean up
    
    def test_get_capabilities(self, architecture_expert):
        """Test architecture capabilities"""
        capabilities = architecture_expert.get_capabilities()
        
        assert "design_pattern_analysis" in capabilities
        assert "solid_principles_analysis" in capabilities
        assert "coupling_analysis" in capabilities


class TestPerformanceExpert(ReflectiveModule):
    """Test PerformanceExpert functionality"""
    
    @pytest.fixture
    def performance_expert(self):
        return PerformanceExpert()
    
    @pytest.mark.asyncio
    async def test_analyze_performance_issues(self, performance_expert):
        """Test performance analysis"""
        performance_code = '''
def inefficient_function(data):
    result = ""
    for item in data:
        result += str(item)  # Inefficient string concatenation
        
        for subitem in item:  # Nested loop - O(n²)
            if len(data) > 100:  # len() in loop
                print(subitem)
    
    return result

def database_issue(users):
    for user in users:
        profile = user.get_profile()  # N+1 query problem
        print(profile.name)

import time
def blocking_operation():
    time.sleep(1)  # Blocking operation
'''
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(performance_code)
            f.flush()
            
            context = AnalysisContext(
                target_path=f.name,
                analysis_type="performance"
            )
            
            result = await performance_expert.analyze(context)
            
            assert result.agent_name == "PerformanceExpert"
            assert 0.0 <= result.confidence <= 1.0
            assert len(result.findings) > 0
            
            # Should detect nested loops
            nested_findings = [f for f in result.findings if "nested" in f.description.lower()]
            assert len(nested_findings) > 0
            
            # Should detect string concatenation issues
            string_findings = [f for f in result.findings if "concatenation" in f.description.lower()]
            assert len(string_findings) > 0
            
            Path(f.name).unlink()  # Clean up
    
    def test_get_capabilities(self, performance_expert):
        """Test performance capabilities"""
        capabilities = performance_expert.get_capabilities()
        
        assert "algorithm_analysis" in capabilities
        assert "complexity_analysis" in capabilities
        assert "memory_usage_analysis" in capabilities


class TestAllExpertsIntegration(ReflectiveModule):
    """Test integration between all expert agents"""
    
    @pytest.mark.asyncio
    async def test_all_experts_on_same_file(self):
        """Test all experts analyzing the same file"""
        test_code = '''
import os
import time

password = "hardcoded_secret_123"  # Security issue

class LargeManagerClass(ReflectiveModule):  # Architecture issue
    """A class that manages everything"""
    
    def process_data(self, data, option1, option2, option3, option4, option5, option6):  # Architecture issue
        result = ""
        for item in data:  # Performance issue
            result += str(item)  # Performance issue
            time.sleep(0.1)  # Performance issue
            
            # Security issue
            os.system("process " + item)
            
            for subitem in item:  # Performance issue - nested loop
                if len(data) > 100:  # Performance issue - len in loop
                    print(subitem)
        
        return result
'''
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(test_code)
            f.flush()
            
            context = AnalysisContext(
                target_path=f.name,
                analysis_type="comprehensive"
            )
            
            # Test all experts
            experts = [
                CodeQualityExpert(),
                SecurityExpert(),
                ArchitectureExpert(),
                PerformanceExpert()
            ]
            
            results = []
            for expert in experts:
                result = await expert.analyze(context)
                results.append(result)
                
                # All should complete successfully
                assert result.agent_name == expert.name
                assert 0.0 <= result.confidence <= 1.0
                assert result.analysis_duration >= 0
            
            # Each expert should find different types of issues
            all_findings = []
            for result in results:
                all_findings.extend(result.findings)
            
            # Should have findings from multiple categories
            finding_types = {f.type for f in all_findings}
            assert len(finding_types) > 1  # Multiple types of issues detected
            
            Path(f.name).unlink()  # Clean up
    
    def test_expert_capabilities_unique(self):
        """Test that each expert has unique capabilities"""
        experts = [
            CodeQualityExpert(),
            SecurityExpert(),
            BuildExpert(),
            ArchitectureExpert(),
            PerformanceExpert()
        ]
        
        all_capabilities = set()
        for expert in experts:
            capabilities = expert.get_capabilities()
            
            # Each expert should have capabilities
            assert len(capabilities) > 0
            
            # Capabilities should be mostly unique (some overlap is OK)
            overlap = all_capabilities.intersection(set(capabilities))
            assert len(overlap) < len(capabilities) / 2  # Less than 50% overlap
            
            all_capabilities.update(capabilities)
    
    def test_expert_confidence_validation(self):
        """Test that all experts validate confidence properly"""
        from src.ghostbusters.core.models import AnalysisResult
from src.multi_instance_orchestration.core.reflective_module import ReflectiveModule

        
        experts = [
            CodeQualityExpert(),
            SecurityExpert(),
            BuildExpert(),
            ArchitectureExpert(),
            PerformanceExpert()
        ]
        
        for expert in experts:
            # Valid confidence should pass
            valid_result = AnalysisResult(agent_name=expert.name, confidence=0.8)
            assert expert.validate_confidence(valid_result) is True
            
            # Invalid confidence should fail
            invalid_result = AnalysisResult(agent_name=expert.name, confidence=1.5)

    def get_interface_metadata(self):
        """Get interface metadata for registry."""
        return {
            'module_id': getattr(self, 'module_id', self.__class__.__name__),
            'interface_type': self.__class__.__name__,
            'version': '1.0.0',
            'dependencies': [],
            'capabilities': []
        }
        
    def register_module(self, registry):
        """Register module with registry."""
        if hasattr(registry, 'register'):
            registry.register(self.get_interface_metadata())
            
    def health_check(self):
        """Perform health check."""
        return {
            'status': 'healthy',
            'timestamp': datetime.now().isoformat(),
            'module_id': getattr(self, 'module_id', self.__class__.__name__)
        }
        
    def get_health_status(self):
        """Get current health status."""
        return self.health_check()

            assert expert.validate_confidence(invalid_result) is False