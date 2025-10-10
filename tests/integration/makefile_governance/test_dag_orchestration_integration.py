#!/usr/bin/env python3
"""
Integration Tests for Makefile DAG Orchestration

Tests the integration between makefile governance components and
DAG orchestration for parallel execution.
"""

import asyncio
import pytest
import tempfile
from pathlib import Path
from typing import List

from src.makefile_governance.integration.dag_orchestration_integration import (
    MakefileDAGOrchestrator,
    create_makefile_dag_orchestrator
)


class TestMakefileDAGOrchestration:
    """Test suite for makefile DAG orchestration integration."""
    
    @pytest.fixture
    def orchestrator(self):
        """Create orchestrator for testing."""
        return create_makefile_dag_orchestrator(max_workers=2)
    
    @pytest.fixture
    def temp_makefiles(self):
        """Create temporary makefiles for testing."""
        temp_files = []
        
        # Valid makefile
        valid_makefile = tempfile.NamedTemporaryFile(mode='w', suffix='_Makefile', delete=False)
        valid_makefile.write("""
.PHONY: help clean test

help: ## Show help
\t@echo "Available targets:"

clean: ## Clean files
\t@rm -rf build/

test: ## Run tests
\t@python -m pytest
""")
        valid_makefile.close()
        temp_files.append(Path(valid_makefile.name))
        
        # Invalid makefile with syntax errors
        invalid_makefile = tempfile.NamedTemporaryFile(mode='w', suffix='_Makefile', delete=False)
        invalid_makefile.write("""
help:
    echo "This should use tabs, not spaces"

build_project:
\techo "This target name should use kebab-case"

test: build_project
echo "Missing tab separator"
""")
        invalid_makefile.close()
        temp_files.append(Path(invalid_makefile.name))
        
        yield temp_files
        
        # Cleanup
        for temp_file in temp_files:
            try:
                temp_file.unlink()
            except FileNotFoundError:
                pass
    
    @pytest.mark.asyncio
    async def test_orchestrator_initialization(self, orchestrator):
        """Test orchestrator initialization."""
        assert orchestrator is not None
        assert orchestrator.module_id == "makefile_dag_orchestrator"
        
        # Check module info
        info = orchestrator.get_module_info()
        assert info["module_id"] == "makefile_dag_orchestrator"
        assert info["name"] == "Makefile DAG Orchestrator"
        assert "components" in info
        assert "statistics" in info
        
        # Check capabilities
        capabilities = orchestrator.get_capabilities()
        assert len(capabilities) > 0
        
        # Check health status
        health = orchestrator.get_health_status()
        assert health is not None
        assert health.module_id == "makefile_dag_orchestrator"
    
    @pytest.mark.asyncio
    async def test_parallel_validation_single_file(self, orchestrator, temp_makefiles):
        """Test parallel validation with a single makefile."""
        makefile_path = temp_makefiles[0]  # Use valid makefile
        
        results = await orchestrator.validate_makefiles_parallel([makefile_path])
        
        # Check orchestration summary
        assert "orchestration_summary" in results
        summary = results["orchestration_summary"]
        assert summary["status"] in ["completed", "failed"]
        assert summary["total_tasks"] > 0
        
        # Check validation results
        assert "syntax_results" in results
        assert "governance_results" in results
        assert str(makefile_path) in results["syntax_results"]
    
    @pytest.mark.asyncio
    async def test_parallel_validation_multiple_files(self, orchestrator, temp_makefiles):
        """Test parallel validation with multiple makefiles."""
        results = await orchestrator.validate_makefiles_parallel(temp_makefiles)
        
        # Check orchestration summary
        summary = results["orchestration_summary"]
        assert summary["total_tasks"] >= len(temp_makefiles) * 3  # 3 tasks per makefile
        
        # Check that all makefiles were processed
        syntax_results = results["syntax_results"]
        assert len(syntax_results) == len(temp_makefiles)
        
        for makefile_path in temp_makefiles:
            assert str(makefile_path) in syntax_results
    
    @pytest.mark.asyncio
    async def test_parallel_validation_with_options(self, orchestrator, temp_makefiles):
        """Test parallel validation with custom options."""
        validation_options = {
            "syntax_priority": 15,
            "governance_priority": 10,
            "health_priority": 5
        }
        
        results = await orchestrator.validate_makefiles_parallel(
            temp_makefiles, validation_options
        )
        
        # Should complete successfully with custom options
        assert "orchestration_summary" in results
        assert results["orchestration_summary"]["status"] in ["completed", "failed"]
    
    @pytest.mark.asyncio
    async def test_parallel_repair_functionality(self, orchestrator, temp_makefiles):
        """Test parallel repair functionality."""
        # Use the invalid makefile for repair testing
        invalid_makefile = temp_makefiles[1]
        
        repair_options = {
            "create_backup": True,
            "repair_priority": 10
        }
        
        results = await orchestrator.repair_makefiles_parallel(
            [invalid_makefile], repair_options
        )
        
        # Check orchestration summary
        assert "orchestration_summary" in results
        summary = results["orchestration_summary"]
        assert summary["status"] in ["completed", "failed"]
        
        # Check repair results
        assert "repair_results" in results
        assert str(invalid_makefile) in results["repair_results"]
        
        repair_result = results["repair_results"][str(invalid_makefile)]
        # Note: repair might succeed or fail depending on the specific errors
        assert "repair_successful" in repair_result
    
    @pytest.mark.asyncio
    async def test_validation_error_handling(self, orchestrator):
        """Test error handling for non-existent makefiles."""
        non_existent_path = Path("/non/existent/makefile")
        
        results = await orchestrator.validate_makefiles_parallel([non_existent_path])
        
        # Should handle the error gracefully
        assert "orchestration_summary" in results
        # The orchestration might complete but individual tasks may fail
        assert results["orchestration_summary"]["status"] in ["completed", "failed"]
    
    @pytest.mark.asyncio
    async def test_orchestration_statistics(self, orchestrator, temp_makefiles):
        """Test orchestration statistics collection."""
        # Run a validation to generate statistics
        await orchestrator.validate_makefiles_parallel(temp_makefiles[:1])
        
        # Get statistics
        stats = orchestrator.get_orchestration_statistics()
        
        # Check structure
        assert "makefile_orchestrator" in stats
        assert "dag_orchestrator" in stats
        assert "system_health" in stats
        
        # Check makefile orchestrator stats
        makefile_stats = stats["makefile_orchestrator"]
        assert "total_orchestrations" in makefile_stats
        assert "successful_orchestrations" in makefile_stats
        assert "failed_orchestrations" in makefile_stats
        assert "success_rate" in makefile_stats
        
        # Should have at least one orchestration
        assert makefile_stats["total_orchestrations"] >= 1
    
    @pytest.mark.asyncio
    async def test_health_monitoring_integration(self, orchestrator):
        """Test health monitoring integration."""
        # Get initial health status
        initial_health = orchestrator.get_health_status()
        assert initial_health is not None
        
        # Health score should be between 0 and 1
        assert 0.0 <= initial_health.health_score <= 1.0
        
        # Should have valid status
        assert initial_health.status.value in ["healthy", "warning", "error"]
    
    @pytest.mark.asyncio
    async def test_graceful_degradation(self, orchestrator):
        """Test graceful degradation functionality."""
        degradation_result = orchestrator.graceful_degradation()
        
        assert degradation_result is not None
        assert hasattr(degradation_result, 'success')
        assert hasattr(degradation_result, 'remaining_capabilities')
        assert hasattr(degradation_result, 'degraded_capabilities')
    
    @pytest.mark.asyncio
    async def test_concurrent_orchestrations(self, orchestrator, temp_makefiles):
        """Test handling of concurrent orchestration requests."""
        # This test verifies that the orchestrator can handle multiple
        # concurrent requests properly (though they may be serialized internally)
        
        # Create multiple validation tasks
        tasks = [
            orchestrator.validate_makefiles_parallel([temp_makefiles[0]]),
            orchestrator.validate_makefiles_parallel([temp_makefiles[1]])
        ]
        
        # Run concurrently
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Both should complete (successfully or with errors)
        assert len(results) == 2
        for result in results:
            if isinstance(result, Exception):
                # If there's an exception, it should be a reasonable one
                # (not a concurrency-related crash)
                assert not isinstance(result, (RuntimeError, asyncio.CancelledError))
            else:
                # If successful, should have proper structure
                assert "orchestration_summary" in result
    
    def test_factory_function(self):
        """Test the factory function for creating orchestrators."""
        orchestrator = create_makefile_dag_orchestrator(max_workers=8)
        
        assert orchestrator is not None
        assert isinstance(orchestrator, MakefileDAGOrchestrator)
        
        # Check that max_workers setting is applied
        info = orchestrator.get_module_info()
        # The max_workers might be reflected in component configurations
        assert "components" in info


@pytest.mark.asyncio
async def test_end_to_end_workflow():
    """Test complete end-to-end workflow."""
    # Create orchestrator
    orchestrator = create_makefile_dag_orchestrator(max_workers=2)
    
    # Create a temporary makefile with known issues
    with tempfile.NamedTemporaryFile(mode='w', suffix='_test_makefile', delete=False) as f:
        f.write("""
# Test makefile with issues
help:
    echo "Spaces instead of tabs"

build_project:
\techo "Bad target name"

test: build_project
echo "Missing tab"
""")
        temp_makefile = Path(f.name)
    
    try:
        # Step 1: Validate (should find issues)
        validation_results = await orchestrator.validate_makefiles_parallel([temp_makefile])
        
        # Should find syntax errors
        syntax_results = validation_results.get("syntax_results", {})
        makefile_syntax = syntax_results.get(str(temp_makefile), {})
        assert not makefile_syntax.get("is_valid", True)  # Should be invalid
        
        # Step 2: Repair
        repair_results = await orchestrator.repair_makefiles_parallel([temp_makefile])
        
        # Should attempt repair
        repair_data = repair_results.get("repair_results", {})
        assert str(temp_makefile) in repair_data
        
        # Step 3: Get final statistics
        final_stats = orchestrator.get_orchestration_statistics()
        
        # Should have run multiple orchestrations
        makefile_stats = final_stats.get("makefile_orchestrator", {})
        assert makefile_stats.get("total_orchestrations", 0) >= 2
        
    finally:
        # Cleanup
        try:
            temp_makefile.unlink()
        except FileNotFoundError:
            pass


if __name__ == "__main__":
    # Run a simple test if executed directly
    async def simple_test():
        orchestrator = create_makefile_dag_orchestrator(max_workers=2)
        health = orchestrator.get_health_status()
        print(f"Orchestrator Health: {health.status.value} (Score: {health.health_score:.2f})")
        
        if health.issues:
            print("Issues:")
            for issue in health.issues:
                print(f"  - {issue}")
        
        print("✅ Basic orchestrator test passed")
    
    asyncio.run(simple_test())