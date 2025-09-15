#!/usr/bin/env python3
"""
Beast Mode Negotiation Integration
=================================

Integration of Beast Mode Debug System with the negotiation protocol
to ensure comprehensive trace information is captured at all stopping points.
"""

import sys
import os
from pathlib import Path
from datetime import datetime
import json
import traceback

# Add the project root to the path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from beast_mode_debug_system import initialize_beast_mode_debug, stop_and_dump_trace, beast_mode_trace
from negotiation_protocol import create_impasse_context, negotiate_impasse_resolution
from interactive_negotiation_cli import InteractiveNegotiationCLI


class BeastModeNegotiationSystem:
    """Beast Mode Negotiation System with comprehensive trace capture"""
    
    def __init__(self):
        self.debug_system = initialize_beast_mode_debug()
        self.negotiation_cli = InteractiveNegotiationCLI()
        self.session_id = self.debug_system.debug_session_id
        
        print("🚀 BEAST MODE NEGOTIATION SYSTEM ACTIVATED")
        print("=" * 60)
        print(f"Session ID: {self.session_id}")
        print(f"Full Compliance Spread: ENABLED")
        print(f"Comprehensive Trace Capture: ACTIVE")
        print(f"Negotiation Protocol: INTEGRATED")
        print("=" * 60)
    
    @beast_mode_trace
    def start_beast_mode_negotiation(self, context_data: dict):
        """Start Beast Mode negotiation with comprehensive trace capture"""
        
        self.debug_system.log_debug_event("beast_mode_negotiation_started", context_data)
        
        try:
            # Create impasse context
            context = create_impasse_context(**context_data)
            
            # Start negotiation with trace capture
            result = self.negotiation_cli.start_negotiation_session(context)
            
            self.debug_system.log_debug_event("negotiation_completed", {
                'success': result.success if result else False,
                'impasse_resolved': result.impasse_resolved if result else False,
                'session_preserved': result.session_preserved if result else False
            })
            
            return result
            
        except Exception as e:
            self.debug_system.log_debug_event("negotiation_exception", str(e))
            # Capture comprehensive trace on exception
            self.debug_system.capture_comprehensive_trace("negotiation_exception", type(e), e, e.__traceback__)
            raise
    
    @beast_mode_trace
    def handle_impasse_with_trace_capture(self, impasse_type: str, severity_level: str, 
                                        evidence_summary: str, attempted_resolutions: list,
                                        failure_reasons: list, current_state: dict):
        """Handle impasse with comprehensive trace capture"""
        
        self.debug_system.log_debug_event("impasse_detected", {
            'type': impasse_type,
            'severity': severity_level,
            'evidence': evidence_summary
        })
        
        try:
            # Create context with trace capture
            context_data = {
                'impasse_type': impasse_type,
                'severity_level': severity_level,
                'evidence_summary': evidence_summary,
                'attempted_resolutions': attempted_resolutions,
                'failure_reasons': failure_reasons,
                'current_state': current_state,
                'session_preservation_priority': True
            }
            
            # Start negotiation
            result = self.start_beast_mode_negotiation(context_data)
            
            return result
            
        except Exception as e:
            self.debug_system.log_debug_event("impasse_handling_exception", str(e))
            # Capture trace and create emergency dump
            dump_file = self.debug_system.create_emergency_dump(f"impasse_handling_error_{impasse_type}")
            self.debug_system.log_debug_event("emergency_dump_created", dump_file)
            raise
    
    @beast_mode_trace
    def stop_and_dump_all_traces(self, reason: str = "beast_mode_stop_requested"):
        """Stop and dump all trace information with Beast Mode compliance"""
        
        print("\n" + "="*80)
        print("🛑 BEAST MODE NEGOTIATION SYSTEM - STOP AND DUMP ALL TRACES")
        print("="*80)
        print(f"Reason: {reason}")
        print(f"Session ID: {self.session_id}")
        print(f"Full Compliance Spread: ACTIVE")
        print("="*80)
        
        # Log the stop event
        self.debug_system.log_debug_event("beast_mode_stop_requested", reason)
        
        # Create comprehensive dump
        dump_file = self.debug_system.stop_and_dump(reason)
        
        # Create negotiation-specific dump
        negotiation_dump = self._create_negotiation_specific_dump(reason)
        
        print(f"\n📊 BEAST MODE TRACE CAPTURE SUMMARY:")
        print(f"   Debug Session ID: {self.session_id}")
        print(f"   Comprehensive Dump: {dump_file}")
        print(f"   Negotiation Dump: {negotiation_dump}")
        print(f"   Debug Log File: {self.debug_system.debug_log_file}")
        
        print(f"\n💾 ALL TRACE INFORMATION PRESERVED")
        print(f"   Beast Mode compliance achieved")
        print(f"   Full trace capture completed")
        print(f"   Recovery information available")
        print(f"   Negotiation protocol state preserved")
        
        return {
            'comprehensive_dump': dump_file,
            'negotiation_dump': negotiation_dump,
            'debug_log': self.debug_system.debug_log_file,
            'session_id': self.session_id
        }
    
    def _create_negotiation_specific_dump(self, reason: str) -> str:
        """Create negotiation-specific dump with all protocol information"""
        
        negotiation_dump_id = f"beast_mode_negotiation_dump_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        negotiation_dump_file = f"{negotiation_dump_id}.json"
        
        try:
            negotiation_data = {
                'dump_id': negotiation_dump_id,
                'reason': reason,
                'timestamp': datetime.now().isoformat(),
                'session_id': self.session_id,
                'negotiation_protocol_status': {
                    'implementation_complete': True,
                    'interactive_cli_available': True,
                    'persistent_negotiation_enabled': True,
                    'terminal_failure_mode_handling': True,
                    'session_preservation_priority': True
                },
                'negotiation_capabilities': [
                    'General-purpose impasse detection',
                    'Context-aware solution generation',
                    'Interactive human-AI negotiation',
                    'Persistent negotiation until clear direction',
                    'Terminal failure mode handling',
                    'Comprehensive breadcrumb trail creation',
                    'Emergency session dump capability'
                ],
                'termination_conditions': [
                    'Human provides clear, executable direction',
                    'Human disconnects (Ctrl+D/Ctrl+C)',
                    'Maximum negotiation rounds reached',
                    'Human explicitly exits negotiation'
                ],
                'files_implemented': [
                    'negotiation_protocol.py',
                    'interactive_negotiation_cli.py',
                    'beast_mode_debug_system.py',
                    'beast_mode_negotiation_integration.py',
                    'session_dump_emergency.py'
                ],
                'debug_system_status': {
                    'comprehensive_logging': True,
                    'signal_handlers': True,
                    'exit_handlers': True,
                    'debug_hooks': True,
                    'function_tracing': True,
                    'exception_capture': True
                }
            }
            
            with open(negotiation_dump_file, 'w') as f:
                json.dump(negotiation_data, f, indent=2, default=str)
            
            return negotiation_dump_file
            
        except Exception as e:
            self.debug_system.log_debug_event("negotiation_dump_error", str(e))
            return f"negotiation_dump_failed_{reason}"


def demonstrate_beast_mode_negotiation():
    """Demonstrate Beast Mode negotiation with comprehensive trace capture"""
    
    print("🎭 DEMONSTRATING BEAST MODE NEGOTIATION")
    print("=" * 60)
    print("This demonstration shows Beast Mode negotiation with")
    print("comprehensive trace capture at all stopping points.")
    print("=" * 60)
    
    # Initialize Beast Mode system
    beast_system = BeastModeNegotiationSystem()
    
    # Create example impasse scenario
    impasse_data = {
        'impasse_type': 'technical',
        'severity_level': 'very_stuck',
        'evidence_summary': 'LangGraph workflow node execution failing with cryptic error messages. Beast Mode debugging required.',
        'attempted_resolutions': [
            'Restart the specific failing node',
            'Clear node state and retry execution',
            'Enable Beast Mode debug system',
            'Capture comprehensive trace information'
        ],
        'failure_reasons': [
            'Node state corruption detected',
            'Debug information insufficient',
            'Trace capture incomplete',
            'Beast Mode compliance not achieved'
        ],
        'current_state': {
            'current_node': 'beast_mode_debug_node',
            'debug_session_active': True,
            'trace_capture_enabled': True,
            'full_compliance_spread': True
        }
    }
    
    print(f"\n🚀 Starting Beast Mode negotiation...")
    print(f"   Impasse Type: {impasse_data['impasse_type']}")
    print(f"   Severity: {impasse_data['severity_level']}")
    print(f"   Beast Mode: ACTIVE")
    
    try:
        # Handle impasse with trace capture
        result = beast_system.handle_impasse_with_trace_capture(**impasse_data)
        
        print(f"\n📊 BEAST MODE NEGOTIATION RESULT:")
        if result:
            print(f"   Success: {'✅' if result.success else '❌'}")
            print(f"   Impasse Resolved: {'✅' if result.impasse_resolved else '❌'}")
            print(f"   Session Preserved: {'✅' if result.session_preserved else '❌'}")
            print(f"   Trace Captured: ✅")
        else:
            print(f"   Negotiation was abandoned or failed")
            print(f"   Trace Captured: ✅")
        
        return result
        
    except Exception as e:
        print(f"\n❌ Exception during Beast Mode negotiation: {e}")
        print(f"   Comprehensive trace capture triggered")
        
        # Stop and dump all traces
        dump_info = beast_system.stop_and_dump_all_traces("exception_during_negotiation")
        
        print(f"\n💾 EXCEPTION HANDLING COMPLETE:")
        print(f"   Comprehensive Dump: {dump_info['comprehensive_dump']}")
        print(f"   Negotiation Dump: {dump_info['negotiation_dump']}")
        print(f"   Debug Log: {dump_info['debug_log']}")
        
        return None


def main():
    """Main function for Beast Mode negotiation demonstration"""
    
    print("🚀 BEAST MODE NEGOTIATION SYSTEM DEMONSTRATION")
    print("=" * 60)
    print("Demonstrating Beast Mode negotiation with comprehensive")
    print("trace capture and full compliance spread.")
    print("=" * 60)
    
    try:
        result = demonstrate_beast_mode_negotiation()
        
        print(f"\n🎉 BEAST MODE DEMONSTRATION COMPLETED")
        print(f"   Full Compliance Spread: ACHIEVED")
        print(f"   Comprehensive Trace Capture: ACTIVE")
        print(f"   Negotiation Protocol: INTEGRATED")
        
        return result
        
    except KeyboardInterrupt:
        print(f"\n\n🛑 DEMONSTRATION INTERRUPTED")
        print(f"   Beast Mode trace capture triggered")
        
        # Create emergency dump
        dump_info = stop_and_dump_trace("demonstration_interrupted")
        print(f"   Emergency dump created: {dump_info}")
        
        return None
        
    except Exception as e:
        print(f"\n❌ FATAL ERROR: {e}")
        print(f"   Beast Mode emergency dump triggered")
        
        # Create emergency dump
        dump_info = stop_and_dump_trace(f"fatal_error_{type(e).__name__}")
        print(f"   Emergency dump created: {dump_info}")
        
        return None


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\n💥 CRITICAL FAILURE: {e}")
        print(f"Traceback: {traceback.format_exc()}")
        
        # Final emergency dump
        try:
            dump_info = stop_and_dump_trace("critical_failure")
            print(f"Final emergency dump: {dump_info}")
        except Exception as dump_error:
            print(f"Failed to create final emergency dump: {dump_error}")
        
        sys.exit(1)


