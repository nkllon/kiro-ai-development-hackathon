#!/usr/bin/env python3
"""
Sophisticated Indirect Verification - RDI Compliant
==================================================

REFACTORED: Split from 579 lines to 200 lines for RDI compliance.
Main functionality moved to src/verification_consolidated/ modules.

Author: Beast Mode Framework
Date: 2025-01-27
Purpose: RDI compliant wrapper for consolidated verification modules
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.verification_consolidated.core_verification import SophisticatedVerificationSystem
from src.verification_consolidated.test_scenarios import create_test_scenarios


def main():
    """Run sophisticated indirect verification - RDI compliant wrapper."""
    print("🎯 SOPHISTICATED INDIRECT VERIFICATION SYSTEM")
    print("=" * 70)
    
    try:
        from langgraph_devpost_workflow import DevPostWorkflow

        # Create workflow
        workflow = DevPostWorkflow()
        print("✅ Workflow created successfully")
        
        # Create test scenarios
        test_scenarios = create_test_scenarios()
        print(f"📊 Created {len(test_scenarios)} test scenarios")
        
        # Run verification
        verification_system = SophisticatedVerificationSystem()
        result = verification_system.verify_integration(workflow, test_scenarios)
        
        # Display results
        print("\n🎯 VERIFICATION RESULTS")
        print("=" * 50)
        print(f"Node Type: {result.node_type}")
        print(f"Confidence: {result.confidence:.2f}")
        print(f"Evidence Count: {len(result.evidence)}")
        print("\n📊 Evidence:")
        for evidence in result.evidence:
            print(f"   • {evidence}")
        print("\n📈 Execution Characteristics:")
        print(
            f"   Monolithic Score: {result.execution_characteristics['monolithic_score']:.2f}"
        )
        print(
            f"   Modular Score: {result.execution_characteristics['modular_score']:.2f}"
        )
        print("\n🔍 State Mutations:")
        print(f"   Modular Indicators: {result.state_mutations['modular_indicators']}")
        print(
            f"   Monolithic Indicators: {result.state_mutations['monolithic_indicators']}"
        )
        print("\n⚡ Performance Metrics:")
        print(f"   Performance Type: {result.performance_metrics['performance_type']}")
        print(f"   Confidence: {result.performance_metrics['confidence']:.2f}")
        print(
            f"   Avg Execution Time: {result.performance_metrics['avg_execution_time']:.4f}s"
        )
        
        # Final determination
        if result.confidence >= 0.7 and result.node_type == "modular":
            print(
                "\n🎉 DEFINITIVE RESULT: Refactored modular components are integrated!"
            )
            return True
        elif result.confidence >= 0.5 and result.node_type == "modular":
            print("\n✅ LIKELY RESULT: Refactored components are probably integrated")
            return True
        elif result.confidence >= 0.7 and result.node_type == "monolithic":
            print(
                "\n❌ DEFINITIVE RESULT: Old monolithic components are still being used!"
            )
            return False
        else:
            print(
                "\n❓ UNCLEAR RESULT: Cannot definitively determine which components are used"
            )
            return False
            
    except Exception as e:
        print(f"❌ Verification failed: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)