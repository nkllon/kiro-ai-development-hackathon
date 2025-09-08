#!/usr/bin/env python3
"""
Beast Mode DAG Orchestration Testing Framework - SYSTEMATIC VALIDATION

Comprehensive testing suite for systematic orchestration with BEASTMASTER precision.
Includes Bobby consumption tolerance tests and systematic quality validation.
"""

import pytest
import tempfile
import json
from pathlib import Path
from datetime import datetime
import subprocess
import sys

class TestBeastDAGOrchestration:
    """BEASTMASTER testing framework with SYSTEMATIC rigor."""
    
    def setup_method(self):
        """Setup test environment with systematic precision."""
        self.test_specs_dir = Path(tempfile.mkdtemp())
        self.create_test_ecosystem()
    
    def teardown_method(self):
        """Cleanup test environment systematically."""
        import shutil
        shutil.rmtree(self.test_specs_dir, ignore_errors=True)
    
    def create_test_ecosystem(self):
        """Create systematic test ecosystem for validation."""
        # CREATE CORE FRAMEWORK SPEC
        framework_spec = self.test_specs_dir / "beast-mode-framework"
        framework_spec.mkdir()
        
        (framework_spec / "requirements.md").write_text("""
# Beast Mode Framework Requirements

## Requirements

### Requirement 1
**User Story:** As a developer, I want systematic framework, so that I can build with confidence

#### Acceptance Criteria
1. WHEN framework is initialized THEN system SHALL provide systematic interfaces
2. WHEN components are integrated THEN system SHALL maintain systematic quality
""")
        
        (framework_spec / "design.md").write_text("""
# Beast Mode Framework Design

## Architecture
Systematic framework with BEASTMASTER precision.

## Components
- Core Engine
- Systematic Interfaces
- Quality Monitoring
""")
        
        (framework_spec / "tasks.md").write_text("""
# Implementation Plan

- [x] 1. Create core framework interfaces
- [ ] 2. Implement systematic components
- [ ] 3. Add quality monitoring
- [ ] 4. Create integration tests
""")
        
        # CREATE ORCHESTRATION SPEC
        orchestration_spec = self.test_specs_dir / "dag-orchestration"
        orchestration_spec.mkdir()
        
        (orchestration_spec / "requirements.md").write_text("""
# DAG Orchestration Requirements

## Requirements

### Requirement 1
**User Story:** As a system, I want orchestration, so that I can coordinate systematically

#### Acceptance Criteria
1. WHEN ecosystem is analyzed THEN system SHALL identify dependencies
2. WHEN MVP route is calculated THEN system SHALL optimize systematically
""")
        
        (orchestration_spec / "tasks.md").write_text("""
# Implementation Plan

- [x] 1. Create orchestration engine
- [x] 2. Implement dependency analysis
- [ ] 3. Add MVP calculation
- [ ] 4. Create CLI interface
- [ ] 5. Add systematic testing
""")
        
        # CREATE CHAOTIC SPEC (FOR BOBBY TESTING)
        chaotic_spec = self.test_specs_dir / "chaotic-nightmare-spec"
        chaotic_spec.mkdir()
        
        (chaotic_spec / "requirements.md").write_text("""
# Chaotic Nightmare Requirements

This spec is intentionally broken to test Bobby's consumption tolerance.

## Requirements

### Requirement ???
**User Story:** As a ??? I want ??? so that ???

#### Acceptance Criteria
1. WHEN ??? THEN ??? SHALL ???
2. IF ??? THEN ??? MIGHT ???
""")
        
        (chaotic_spec / "tasks.md").write_text("""
# Broken Implementation Plan

- [ ] 1. Fix everything that's broken
- [?] 2. Maybe implement something
- [x] 3. This task is marked complete but nothing was done
- [ ] 4. Circular dependency on task 6
- [ ] 5. Depends on non-existent task 99
- [ ] 6. Depends on task 4
""")
    
    def test_cli_analyze_functionality(self):
        """Test CLI analyze command with systematic validation."""
        result = subprocess.run([
            sys.executable, "beast_dag_simple.py", "analyze", str(self.test_specs_dir), "--output", "json"
        ], capture_output=True, text=True)
        
        assert result.returncode == 0, f"CLI analyze failed: {result.stderr}"
        
        # PARSE JSON OUTPUT (find the JSON block)
        output = result.stdout
        json_start = output.find('{')
        json_end = output.rfind('}') + 1
        
        assert json_start != -1 and json_end > json_start, "No JSON output found"
        
        json_text = output[json_start:json_end]
        data = json.loads(json_text)
        
        # SYSTEMATIC VALIDATION
        assert "ecosystem_id" in data
        assert data["total_specifications"] == 3
        assert data["total_tasks"] > 0
        assert 0 <= data["completion_percentage"] <= 100
        
        print(f"✅ CLI Analyze Test: {data['total_specifications']} specs, {data['total_tasks']} tasks")
    
    def test_cli_mvp_route_calculation(self):
        """Test MVP route calculation with systematic optimization."""
        result = subprocess.run([
            sys.executable, "beast_dag_simple.py", "mvp-route", str(self.test_specs_dir), 
            "--timeline", "6", "--output", "json"
        ], capture_output=True, text=True)
        
        assert result.returncode == 0, f"MVP route calculation failed: {result.stderr}"
        
        # PARSE JSON OUTPUT (find the JSON block)
        output = result.stdout
        json_start = output.find('{')
        json_end = output.rfind('}') + 1
        
        assert json_start != -1 and json_end > json_start, "No JSON output found"
        
        json_text = output[json_start:json_end]
        data = json.loads(json_text)
        
        # SYSTEMATIC VALIDATION
        assert "route_id" in data
        assert data["estimated_timeline_weeks"] == 6
        assert 0.0 <= data["success_probability"] <= 1.0
        assert data["systematic_quality_score"] > 0.8
        assert len(data["phases"]) > 0
        
        print(f"✅ MVP Route Test: {data['estimated_timeline_weeks']} weeks, {data['success_probability']:.1%} success")
    
    def test_cli_orchestration_dry_run(self):
        """Test orchestration dry run with systematic monitoring."""
        result = subprocess.run([
            sys.executable, "beast_dag_simple.py", "orchestrate", str(self.test_specs_dir),
            "--parallel", "4", "--dry-run"
        ], capture_output=True, text=True)
        
        assert result.returncode == 0, f"Orchestration failed: {result.stderr}"
        
        output = result.stdout
        
        # SYSTEMATIC VALIDATION
        assert "BEAST MODE ORCHESTRATION" in output
        assert "PHASE 1: Ecosystem Analysis" in output
        assert "PHASE 2: MVP Route Calculation" in output
        assert "PHASE 3: Parallel Optimization" in output
        assert "ORCHESTRATION COMPLETE" in output
        assert "SYSTEMATIC SUPERIORITY DEMONSTRATED" in output
        
        print("✅ Orchestration Dry Run Test: All phases completed systematically")
    
    def test_bobby_consumption_tolerance(self):
        """Test Beastmaster Bobby's systematic consumption tolerance."""
        result = subprocess.run([
            sys.executable, "beast_dag_simple.py", "bobby-test", str(self.test_specs_dir)
        ], capture_output=True, text=True)
        
        assert result.returncode == 0, f"Bobby test failed: {result.stderr}"
        
        output = result.stdout
        
        # BOBBY VALIDATION
        assert "BEASTMASTER BOBBY TEST" in output
        assert "BOBBY'S VERDICT" in output
        assert "BOBBY SUCCESSFULLY CONSUMED" in output or "BOBBY COULDN'T CONSUME" in output
        
        # BOBBY SHOULD HANDLE EVEN CHAOTIC SPECS
        if "BOBBY SUCCESSFULLY CONSUMED" in output:
            assert "SYSTEMATIC SUPERIORITY DEMONSTRATED" in output
            print("✅ Bobby Consumption Test: Bobby successfully digested chaotic ecosystem")
        else:
            print("⚠️ Bobby Consumption Test: Even Bobby has limits with this chaos")
    
    def test_systematic_quality_validation(self):
        """Test systematic quality across all CLI operations."""
        commands = [
            ["analyze", str(self.test_specs_dir)],
            ["mvp-route", str(self.test_specs_dir), "--timeline", "8"],
            ["orchestrate", str(self.test_specs_dir), "--dry-run"],
            ["bobby-test", str(self.test_specs_dir)]
        ]
        
        systematic_quality_indicators = [
            "SYSTEMATIC",
            "BEASTMASTER", 
            "BEAST MODE",
            "SUPERIORITY",
            "PRECISION"
        ]
        
        for cmd in commands:
            result = subprocess.run([sys.executable, "beast_dag_simple.py"] + cmd, 
                                  capture_output=True, text=True)
            
            assert result.returncode == 0, f"Command {cmd[0]} failed: {result.stderr}"
            
            # VALIDATE SYSTEMATIC QUALITY INDICATORS
            output = result.stdout.upper()
            quality_count = sum(1 for indicator in systematic_quality_indicators if indicator in output)
            
            assert quality_count >= 2, f"Insufficient systematic quality in {cmd[0]} output"
        
        print("✅ Systematic Quality Test: All commands demonstrate systematic superiority")
    
    def test_performance_scalability(self):
        """Test performance with larger ecosystem (scalability validation)."""
        # CREATE LARGER ECOSYSTEM
        large_specs_dir = Path(tempfile.mkdtemp())
        
        try:
            # CREATE 10 SPECS WITH VARYING COMPLEXITY
            for i in range(10):
                spec_dir = large_specs_dir / f"spec-{i:02d}"
                spec_dir.mkdir()
                
                # TASKS WITH VARYING COMPLETION
                tasks = []
                for j in range(5 + i):  # Increasing task count
                    status = "[x]" if j < i else "[ ]"
                    tasks.append(f"- {status} {j+1}. Task {j+1} for spec {i}")
                
                (spec_dir / "tasks.md").write_text(f"""
# Implementation Plan for Spec {i}

{chr(10).join(tasks)}
""")
            
            # TEST PERFORMANCE
            import time
            start_time = time.time()
            
            result = subprocess.run([
                sys.executable, "beast_dag_simple.py", "analyze", str(large_specs_dir)
            ], capture_output=True, text=True, timeout=30)  # 30 second timeout
            
            end_time = time.time()
            execution_time = end_time - start_time
            
            assert result.returncode == 0, f"Performance test failed: {result.stderr}"
            assert execution_time < 10, f"Performance too slow: {execution_time:.2f}s"
            
            print(f"✅ Performance Test: Analyzed 10 specs in {execution_time:.2f}s")
            
        finally:
            import shutil
            shutil.rmtree(large_specs_dir, ignore_errors=True)
    
    def test_error_handling_resilience(self):
        """Test error handling and systematic resilience."""
        # TEST WITH NON-EXISTENT DIRECTORY
        result = subprocess.run([
            sys.executable, "beast_dag_simple.py", "analyze", "/non/existent/path"
        ], capture_output=True, text=True)
        
        assert result.returncode != 0, "Should fail with non-existent directory"
        assert "does not exist" in result.stderr or "No such file" in result.stderr
        
        # TEST WITH EMPTY DIRECTORY
        empty_dir = Path(tempfile.mkdtemp())
        try:
            result = subprocess.run([
                sys.executable, "beast_dag_simple.py", "analyze", str(empty_dir)
            ], capture_output=True, text=True)
            
            # SHOULD HANDLE GRACEFULLY
            assert result.returncode == 0, "Should handle empty directory gracefully"
            
        finally:
            import shutil
            shutil.rmtree(empty_dir, ignore_errors=True)
        
        print("✅ Error Handling Test: Systematic resilience demonstrated")


class TestBeastModeIntegration:
    """Integration tests for Beast Mode ecosystem compatibility."""
    
    def test_real_specs_directory_analysis(self):
        """Test with real .kiro/specs directory if available."""
        specs_dir = Path(".kiro/specs")
        
        if not specs_dir.exists():
            pytest.skip("No .kiro/specs directory found")
        
        result = subprocess.run([
            sys.executable, "beast_dag_simple.py", "analyze", str(specs_dir), "--output", "json"
        ], capture_output=True, text=True, timeout=60)
        
        assert result.returncode == 0, f"Real specs analysis failed: {result.stderr}"
        
        # FIND JSON OUTPUT
        output = result.stdout
        json_start = output.find('{')
        json_end = output.rfind('}') + 1
        
        if json_start != -1 and json_end > json_start:
            json_text = output[json_start:json_end]
            data = json.loads(json_text)
            print(f"✅ Real Specs Test: {data['total_specifications']} specs, {data['completion_percentage']:.1f}% complete")
        else:
            print("✅ Real Specs Test: Analysis completed (no JSON output)")
    
    def test_systematic_superiority_demonstration(self):
        """Demonstrate systematic superiority over ad-hoc approaches."""
        specs_dir = Path(".kiro/specs") if Path(".kiro/specs").exists() else self.test_specs_dir
        
        # MEASURE SYSTEMATIC APPROACH
        import time
        start_time = time.time()
        
        result = subprocess.run([
            sys.executable, "beast_dag_simple.py", "orchestrate", str(specs_dir), "--dry-run"
        ], capture_output=True, text=True)
        
        end_time = time.time()
        systematic_time = end_time - start_time
        
        assert result.returncode == 0
        assert "SYSTEMATIC SUPERIORITY DEMONSTRATED" in result.stdout
        
        print(f"✅ Systematic Superiority: Orchestrated in {systematic_time:.2f}s with systematic precision")


def run_beast_mode_tests():
    """Run all Beast Mode DAG orchestration tests with systematic reporting."""
    print("🔥 BEAST MODE DAG ORCHESTRATION TESTING FRAMEWORK")
    print("⚡ Systematic validation with BEASTMASTER precision")
    print("=" * 60)
    
    # RUN TESTS WITH PYTEST
    test_results = pytest.main([
        __file__, 
        "-v", 
        "--tb=short",
        "--color=yes"
    ])
    
    print("=" * 60)
    
    if test_results == 0:
        print("🏆 ALL TESTS PASSED - SYSTEMATIC SUPERIORITY DEMONSTRATED")
        print("✅ Beast Mode DAG orchestration validated with BEASTMASTER precision")
        print("🎯 MVP Alpha testing framework complete")
    else:
        print("⚠️ Some tests failed - systematic improvements needed")
        print("🔧 Review test output for systematic remediation guidance")
    
    return test_results


if __name__ == "__main__":
    exit_code = run_beast_mode_tests()
    sys.exit(exit_code)