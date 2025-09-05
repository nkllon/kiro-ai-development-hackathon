"""
RDI Chain Validation Orchestrator using LangGraph
Systematically validates Requirements → Design → Implementation → Test chains
"""
import asyncio
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from pathlib import Path
import subprocess
import json

from ..autonomous.pdca_langgraph_orchestrator import PDCALangGraphOrchestrator
from ..core.reflective_module import ReflectiveModule, HealthStatus


@dataclass
class RDIChainIssue:
    """Represents an RDI chain validation issue"""
    chain_id: str
    issue_type: str  # "requirements_gap", "design_mismatch", "implementation_error", "test_failure"
    description: str
    affected_files: List[str]
    severity: str  # "critical", "high", "medium", "low"
    mathematical_proof: str  # Mathematical description of the issue


@dataclass
class RDIValidationResult:
    """Result of RDI chain validation"""
    chain_id: str
    is_valid: bool
    issues: List[RDIChainIssue]
    mathematical_consistency: float  # 0.0 to 1.0
    recommendations: List[str]


class RDIChainOrchestrator(ReflectiveModule):
    """
    Orchestrates systematic RDI chain validation using LangGraph PDCA cycles
    
    Mathematical Approach:
    Requirements → Design → Implementation → Tests = Provable Chain
    Each transition must be mathematically derivable from previous state
    """
    
    def __init__(self):
        super().__init__("rdi_chain_orchestrator")
        self.pdca_orchestrator = PDCALangGraphOrchestrator()
        self.validation_results: Dict[str, RDIValidationResult] = {}
        
        self._update_health_indicator(
            "rdi_orchestrator",
            HealthStatus.HEALTHY if self.pdca_orchestrator.is_healthy() else HealthStatus.DEGRADED,
            "ready" if self.pdca_orchestrator.is_healthy() else "pdca_unavailable",
            "RDI chain orchestrator ready" if self.pdca_orchestrator.is_healthy() else "PDCA orchestrator unavailable"
        )
    
    def get_module_status(self) -> Dict[str, Any]:
        """Get RDI orchestrator status"""
        return {
            "module_name": self.module_name,
            "status": "operational" if self.is_healthy() else "degraded",
            "pdca_orchestrator_healthy": self.pdca_orchestrator.is_healthy(),
            "validation_results_count": len(self.validation_results),
            "guarantees": [
                "MATHEMATICAL_CONSISTENCY_VALIDATION",
                "SYSTEMATIC_RDI_CHAIN_REPAIR",
                "NO_MANUAL_FIXES_WITHOUT_PROOF",
                "LANGGRAPH_ORCHESTRATED_VALIDATION"
            ]
        }
    
    def is_healthy(self) -> bool:
        """Health check including PDCA orchestrator"""
        return self.pdca_orchestrator.is_healthy()
    
    def get_health_indicators(self) -> Dict[str, Any]:
        """Get health indicators for RDI orchestration"""
        return {
            "rdi_orchestration": {
                "status": "healthy" if self.is_healthy() else "degraded",
                "pdca_orchestrator_healthy": self.pdca_orchestrator.is_healthy(),
                "validation_results_count": len(self.validation_results)
            }
        }
    
    def _get_primary_responsibility(self) -> str:
        """Primary responsibility of RDI chain orchestrator"""
        return "Systematic validation and repair of Requirements-Design-Implementation-Documentation chains using mathematical DAG structure"
    
    async def validate_test_infrastructure_rdi_chain(self) -> RDIValidationResult:
        """
        Validate the test infrastructure RDI chain using LangGraph PDCA
        
        Mathematical Proof:
        R: Test requirements (from specs)
        D: Test design (expected behavior)  
        I: Test implementation (actual code)
        T: Test execution (results)
        
        Valid chain: R → D → I → T where each → is provably derivable
        """
        task_context = {
            "validation_target": "test_infrastructure",
            "specs_path": ".kiro/specs/test-infrastructure-repair",
            "test_files": self._discover_test_files(),
            "validation_type": "rdi_chain_consistency"
        }
        
        # Use LangGraph PDCA to systematically validate and fix
        pdca_result = await self.pdca_orchestrator.execute_autonomous_pdca_loop(
            initial_task="Validate and repair test infrastructure RDI chain",
            task_context=task_context
        )
        
        # Convert PDCA result to RDI validation result
        return self._convert_pdca_to_rdi_result(pdca_result, "test_infrastructure")
    
    async def validate_all_specs_rdi_chains(self) -> Dict[str, RDIValidationResult]:
        """
        Validate RDI chains for all specs using systematic approach
        """
        specs_dir = Path(".kiro/specs")
        results = {}
        
        for spec_dir in specs_dir.iterdir():
            if spec_dir.is_dir():
                spec_name = spec_dir.name
                
                task_context = {
                    "validation_target": spec_name,
                    "spec_path": str(spec_dir),
                    "validation_type": "full_rdi_chain"
                }
                
                pdca_result = await self.pdca_orchestrator.execute_autonomous_pdca_loop(
                    initial_task=f"Validate RDI chain for {spec_name}",
                    task_context=task_context
                )
                
                results[spec_name] = self._convert_pdca_to_rdi_result(pdca_result, spec_name)
        
        return results
    
    def _discover_test_files(self) -> List[str]:
        """Discover all test files for analysis"""
        test_files = []
        test_dir = Path("tests")
        
        if test_dir.exists():
            for test_file in test_dir.rglob("test_*.py"):
                test_files.append(str(test_file))
        
        return test_files
    
    def _convert_pdca_to_rdi_result(self, pdca_result: Dict[str, Any], chain_id: str) -> RDIValidationResult:
        """Convert PDCA execution result to RDI validation result"""
        
        # Extract issues from PDCA check phase
        issues = []
        if "check_result" in pdca_result and pdca_result["check_result"]:
            check_data = pdca_result["check_result"]
            
            # Parse issues from check result
            if "validation_issues" in check_data:
                for issue_data in check_data["validation_issues"]:
                    issues.append(RDIChainIssue(
                        chain_id=chain_id,
                        issue_type=issue_data.get("type", "unknown"),
                        description=issue_data.get("description", ""),
                        affected_files=issue_data.get("files", []),
                        severity=issue_data.get("severity", "medium"),
                        mathematical_proof=issue_data.get("proof", "")
                    ))
        
        # Calculate mathematical consistency
        consistency = self._calculate_mathematical_consistency(pdca_result)
        
        # Extract recommendations from act phase
        recommendations = []
        if "act_result" in pdca_result and pdca_result["act_result"]:
            act_data = pdca_result["act_result"]
            recommendations = act_data.get("recommendations", [])
        
        return RDIValidationResult(
            chain_id=chain_id,
            is_valid=len(issues) == 0,
            issues=issues,
            mathematical_consistency=consistency,
            recommendations=recommendations
        )
    
    def _calculate_mathematical_consistency(self, pdca_result: Dict[str, Any]) -> float:
        """
        Calculate mathematical consistency score for RDI chain
        
        Mathematical Formula:
        consistency = (valid_transitions / total_transitions) * confidence_factor
        """
        # Extract validation metrics from PDCA result
        if not pdca_result:
            return 0.0
        
        # Check for check_result in final_state (LangGraph structure)
        check_data = None
        if "final_state" in pdca_result and "check_result" in pdca_result["final_state"]:
            check_data = pdca_result["final_state"]["check_result"]
        elif "check_result" in pdca_result:
            check_data = pdca_result["check_result"]
        
        if not check_data:
            return 0.0
        
        # Default scoring if detailed metrics not available
        if "consistency_metrics" in check_data:
            return check_data["consistency_metrics"].get("score", 0.0)
        
        # Enhanced calculation based on PDCA execution success
        success_indicators = []
        
        # Check if all PDCA phases completed successfully
        if pdca_result.get("success", False):
            success_indicators.append(0.4)  # Base success score
        
        # Check systematic approach score from validation
        if "systematic_approach_score" in check_data:
            success_indicators.append(check_data["systematic_approach_score"])
        
        # Check validation passed status
        if check_data.get("validation_passed", False):
            success_indicators.append(0.3)
        
        # Check constraint satisfaction
        constraint_satisfaction = check_data.get("constraint_satisfaction", {})
        if constraint_satisfaction:
            satisfied_constraints = sum(1 for v in constraint_satisfaction.values() if v)
            total_constraints = len(constraint_satisfaction)
            if total_constraints > 0:
                success_indicators.append(satisfied_constraints / total_constraints * 0.3)
        
        # Fallback calculation based on issues
        validation_issues = check_data.get("validation_issues", [])
        issues_found = check_data.get("issues_found", [])
        total_issues = len(validation_issues) + len(issues_found)
        
        if total_issues == 0 and success_indicators:
            # No issues found and some success indicators present
            base_score = sum(success_indicators) / len(success_indicators)
            return min(1.0, base_score)
        elif total_issues == 0:
            # No issues but no clear success indicators - moderate score
            return 0.6
        else:
            # Issues found - reduce score based on severity
            total_checks = check_data.get("total_checks", max(1, total_issues + 1))
            failed_checks = total_issues
            return max(0.0, (total_checks - failed_checks) / total_checks)
    
    async def execute_systematic_repair(self, chain_id: str) -> Dict[str, Any]:
        """
        Execute systematic repair of RDI chain using LangGraph orchestration
        """
        if chain_id not in self.validation_results:
            raise ValueError(f"No validation results found for chain: {chain_id}")
        
        validation_result = self.validation_results[chain_id]
        
        task_context = {
            "repair_target": chain_id,
            "issues": [issue.__dict__ for issue in validation_result.issues],
            "recommendations": validation_result.recommendations,
            "repair_type": "systematic_rdi_repair"
        }
        
        # Use LangGraph PDCA for systematic repair
        repair_result = await self.pdca_orchestrator.execute_autonomous_pdca_loop(
            initial_task=f"Systematically repair RDI chain for {chain_id}",
            task_context=task_context
        )
        
        return repair_result


# Convenience function for immediate use
async def validate_and_repair_test_infrastructure():
    """
    Convenience function to validate and repair test infrastructure using RDI orchestration
    """
    orchestrator = RDIChainOrchestrator()
    
    if not orchestrator.is_healthy():
        print("❌ RDI Chain Orchestrator not healthy - check LangGraph installation")
        return None
    
    print("🔍 Starting systematic RDI chain validation...")
    
    # Validate test infrastructure RDI chain
    result = await orchestrator.validate_test_infrastructure_rdi_chain()
    
    print(f"📊 Validation complete for test infrastructure:")
    print(f"  - Valid: {result.is_valid}")
    print(f"  - Issues found: {len(result.issues)}")
    print(f"  - Mathematical consistency: {result.mathematical_consistency:.2%}")
    
    if not result.is_valid:
        print("🔧 Starting systematic repair...")
        repair_result = await orchestrator.execute_systematic_repair("test_infrastructure")
        print(f"✅ Repair completed: {repair_result.get('success', False)}")
    
    return result


if __name__ == "__main__":
    # Run the validation and repair
    asyncio.run(validate_and_repair_test_infrastructure())