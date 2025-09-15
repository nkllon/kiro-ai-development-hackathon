#!/usr/bin/env python3
"""
Ghostbusters Critical Consultation
=================================

This is it! The moment we should have trained for!
Critical system failure consultation with Ghostbusters analysis.
"""

import sys
import time
import json
from datetime import datetime
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from ghostbusters_consultation_refactored import GhostbustersConsultationRefactored
from beast_mode_debug_system import initialize_beast_mode_debug, stop_and_dump_trace
from session_dump_emergency import EmergencySessionDumper
from langgraph_devpost_state import DevPostState


def create_critical_state_assessment() -> DevPostState:
    """Create a critical state assessment for Ghostbusters consultation"""
    
    print("🚨 CRITICAL STATE ASSESSMENT")
    print("=" * 60)
    print("Creating comprehensive state assessment for Ghostbusters consultation...")
    print("=" * 60)
    
    # Create mock critical state
    critical_state = {
        "session_save_data": {
            "current_page_data": {
                "url": "https://unknown-crisis-page.com/emergency",
                "title": "System Crisis - All Hands on Deck",
                "timestamp": datetime.now().isoformat(),
                "page_type": "critical_failure",
                "confidence_level": 0.05,  # Extremely low confidence
                "error_indicators": [
                    "System down around knees",
                    "Close to chucking in the towel", 
                    "All hands on deck situation",
                    "Critical failure mode detected",
                    "Multiple system components compromised"
                ],
                "failure_modes": {
                    "primary": "complete_system_failure",
                    "secondary": "negotiation_protocol_overload",
                    "tertiary": "session_preservation_critical"
                },
                "evidence": {
                    "system_health": "critical",
                    "session_integrity": "compromised",
                    "recovery_options": "limited",
                    "human_intervention_required": True
                }
            }
        },
        "session_recovery": {
            "confidence": 0.05,
            "similarity_type": "unknown_crisis",
            "risk_level": "critical",
            "recovery_strategy": "emergency_protocols"
        },
        "ghostbusters_mode": True,
        "critical_failure": True,
        "emergency_protocols": True,
        "messages": [],
        "user_input_required": True,
        "awaiting_ghostbusters_report": True
    }
    
    return critical_state


def run_ghostbusters_critical_consultation():
    """Run critical Ghostbusters consultation"""
    
    print("🚨 GHOSTBUSTERS CRITICAL CONSULTATION")
    print("=" * 60)
    print("This is it! The moment we should have trained for!")
    print("System is down around knees - activating Ghostbusters protocols")
    print("=" * 60)
    
    # Initialize Beast Mode Debug System
    print("🚀 Initializing Beast Mode Debug System...")
    debug_system = initialize_beast_mode_debug()
    
    # Create critical state assessment
    print("📊 Creating critical state assessment...")
    critical_state = create_critical_state_assessment()
    
    # Initialize Ghostbusters consultation
    print("👻 Initializing Ghostbusters consultation...")
    consultation = GhostbustersConsultationRefactored()
    
    # Run autonomous investigation
    print("🔍 Running autonomous investigation...")
    investigation_start = time.time()
    
    try:
        consultation_report = consultation.run_autonomous_investigation(critical_state)
        
        investigation_duration = time.time() - investigation_start
        
        print(f"\n📡 GHOSTBUSTERS CONSULTATION COMPLETE")
        print("=" * 60)
        print(f"Investigation Duration: {investigation_duration:.2f}s")
        print(f"Consultation ID: {consultation_report['consultation_id']}")
        print(f"Primary Strategy: {consultation_report['primary_strategy']}")
        print(f"Risk Assessment: {consultation_report['risk_assessment']['level']}")
        print(f"Recommendation: {consultation_report['recommendation']}")
        print("=" * 60)
        
        # Display detailed recommendations
        print("\n🎯 GHOSTBUSTERS RECOMMENDATIONS:")
        print("-" * 40)
        print(f"Summary: {consultation_report['recommendation']}")
        print(f"Detailed: {consultation_report['detailed_recommendation']}")
        
        print("\n📋 NEXT STEPS:")
        for i, step in enumerate(consultation_report['next_steps'], 1):
            print(f"   {i}. {step}")
        
        print(f"\n⚠️ RISK ASSESSMENT:")
        risk = consultation_report['risk_assessment']
        print(f"   Level: {risk['level']}")
        print(f"   Score: {risk['score']:.2f}")
        print(f"   Failed Tests: {risk['failed_tests']}/{risk['total_tests']}")
        print(f"   Confidence Factor: {risk['confidence_factor']:.2f}")
        
        # Check if emergency protocols should be activated
        if consultation_report['risk_assessment']['level'] == 'high' or \
           consultation_report['risk_assessment']['score'] > 0.8:
            
            print(f"\n🚨 EMERGENCY PROTOCOLS RECOMMENDED")
            print("=" * 40)
            print("Ghostbusters analysis indicates critical situation")
            print("Emergency protocols should be activated immediately")
            
            # Create emergency session dump
            print("\n💾 Creating emergency session dump...")
            dumper = EmergencySessionDumper()
            dump_file = dumper.create_comprehensive_dump()
            print(f"   Emergency dump created: {dump_file}")
            
            # Stop and dump trace
            print("\n🛑 Stopping and dumping comprehensive trace...")
            trace_file = stop_and_dump_trace("critical_ghostbusters_consultation")
            print(f"   Trace dump created: {trace_file}")
            
            print(f"\n✅ CRITICAL CONSULTATION COMPLETE")
            print("=" * 60)
            print("Ghostbusters analysis complete with emergency protocols activated")
            print("All trace information preserved for recovery")
            print("System ready for emergency intervention")
            print("=" * 60)
            
        else:
            print(f"\n✅ GHOSTBUSTERS CONSULTATION COMPLETE")
            print("=" * 60)
            print("Situation analyzed - standard protocols sufficient")
            print("Recommendations provided for recovery")
            print("=" * 60)
        
        return consultation_report
        
    except Exception as e:
        print(f"\n❌ GHOSTBUSTERS CONSULTATION FAILED")
        print("=" * 60)
        print(f"Error: {str(e)}")
        print("Activating emergency protocols...")
        
        # Emergency dump on failure
        try:
            dumper = EmergencySessionDumper()
            dump_file = dumper.create_comprehensive_dump()
            print(f"Emergency dump created: {dump_file}")
        except Exception as dump_error:
            print(f"Emergency dump failed: {dump_error}")
        
        # Stop and dump trace
        try:
            trace_file = stop_and_dump_trace("ghostbusters_consultation_failure")
            print(f"Trace dump created: {trace_file}")
        except Exception as trace_error:
            print(f"Trace dump failed: {trace_error}")
        
        return None


def main():
    """Main function for critical Ghostbusters consultation"""
    
    print("🚨 GHOSTBUSTERS CRITICAL CONSULTATION ACTIVATED")
    print("=" * 70)
    print("This is it! The moment we should have trained for!")
    print("System is down around knees - all hands on deck!")
    print("Activating Ghostbusters consultation protocols...")
    print("=" * 70)
    
    try:
        # Run the critical consultation
        consultation_report = run_ghostbusters_critical_consultation()
        
        if consultation_report:
            print(f"\n🎯 GHOSTBUSTERS ANALYSIS SUMMARY:")
            print("-" * 40)
            print(f"Status: COMPLETE")
            print(f"Strategy: {consultation_report['primary_strategy']}")
            print(f"Risk Level: {consultation_report['risk_assessment']['level']}")
            print(f"Recommendation: {consultation_report['recommendation']}")
            print(f"Emergency Protocols: {'ACTIVATED' if consultation_report['risk_assessment']['level'] == 'high' else 'STANDBY'}")
        else:
            print(f"\n❌ GHOSTBUSTERS CONSULTATION FAILED")
            print("Emergency protocols activated")
            print("Manual intervention required")
        
    except Exception as e:
        print(f"\n💥 FATAL ERROR IN GHOSTBUSTERS CONSULTATION")
        print("=" * 60)
        print(f"Error: {str(e)}")
        print("System in terminal failure mode")
        print("All available information being preserved...")
        
        # Final emergency dump
        try:
            dumper = EmergencySessionDumper()
            dump_file = dumper.create_comprehensive_dump()
            print(f"Final emergency dump: {dump_file}")
        except:
            print("Final emergency dump failed - system unrecoverable")


if __name__ == "__main__":
    main()


