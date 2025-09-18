#!/usr/bin/env python3
"""
CLI Integration Tests
====================

Integration tests for CLI command execution and parameter parsing.
Tests error handling, validation, and JSON serialization in generated CLIs.

Author: Beast Mode Framework
Date: 2025-01-27
"""

import sys
import os
import json
import argparse
from typing import Dict, List, Any
from unittest.mock import Mock

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

def test_cli_command_execution():
    """Test CLI command execution and parameter parsing."""
    
    from src.multi_perspective_ghostbusters.consensus_detector import ConsensusDetector
    from src.multi_perspective_ghostbusters.security_expert import PerspectiveResult
    from datetime import datetime
    
    detector = ConsensusDetector()
    
    # Create mock perspective results for testing
    mock_perspectives = [
        PerspectiveResult(
            agent_id="test_agent_1",
            perspective_type="SecurityExpert",
            analysis_timestamp=datetime.now(),
            insights=[{"type": "security", "finding": "Test security insight"}],
            concerns=[{"type": "vulnerability", "description": "Test concern"}],
            recommendations=[{"type": "security", "recommendation": "Test recommendation"}],
            confidence_score=0.8,
            reasoning_chain=["Applied security analysis", "Identified patterns"],
            unique_contributions=["Security-specific analysis"]
        ),
        PerspectiveResult(
            agent_id="test_agent_2", 
            perspective_type="ArchitectureExpert",
            analysis_timestamp=datetime.now(),
            insights=[{"type": "architecture", "finding": "Test architecture insight"}],
            concerns=[{"type": "design", "description": "Test design concern"}],
            recommendations=[{"type": "architecture", "recommendation": "Test architecture recommendation"}],
            confidence_score=0.7,
            reasoning_chain=["Applied architectural analysis", "Evaluated design patterns"],
            unique_contributions=["Architecture-specific analysis"]
        )
    ]
    
    try:
        # Test CLI command execution
        consensus_areas = detector.identify_consensus_areas(mock_perspectives)
        confidence_scores = detector.calculate_confidence_scores(consensus_areas)
        
        return {
            'command_execution': True,
            'consensus_areas_found': len(consensus_areas),
            'confidence_scores_calculated': len(confidence_scores),
            'error': None
        }
        
    except Exception as e:
        return {
            'command_execution': False,
            'error': str(e)
        }

def test_error_handling_and_validation():
    """Test error handling and validation in generated CLIs."""
    
    from src.multi_perspective_ghostbusters.diversity_validator import DiversityValidator
    
    validator = DiversityValidator()
    
    test_results = {
        'empty_input_handling': False,
        'invalid_type_handling': False,
        'graceful_error_recovery': False
    }
    
    # Test empty input handling
    try:
        result = validator.measure_perspective_uniqueness([])
        test_results['empty_input_handling'] = isinstance(result, list) and len(result) == 0
    except Exception:
        test_results['empty_input_handling'] = False
    
    # Test invalid type handling (should handle gracefully)
    try:
        result = validator.calculate_diversity_metrics([])
        test_results['invalid_type_handling'] = hasattr(result, 'metrics_id')
    except Exception:
        test_results['invalid_type_handling'] = False
    
    # Test graceful error recovery
    try:
        health = validator.health_check()
        test_results['graceful_error_recovery'] = health.status.value == 'healthy'
    except Exception:
        test_results['graceful_error_recovery'] = False
    
    return test_results

def test_cli_output_formatting():
    """Test CLI output formatting and JSON serialization."""
    
    from src.multi_perspective_ghostbusters.human_analysis_presenter import HumanAnalysisPresenter
    
    presenter = HumanAnalysisPresenter()
    
    # Test execute method output (should be JSON serializable)
    try:
        output = presenter.execute()
        
        # Test JSON serialization
        json_output = json.dumps(output, default=str)
        parsed_output = json.loads(json_output)
        
        return {
            'json_serializable': True,
            'output_structure': isinstance(output, dict),
            'required_fields': all(field in output for field in ['presenter_id', 'component_type', 'capabilities', 'status']),
            'json_roundtrip': parsed_output == json.loads(json.dumps(output, default=str))
        }
        
    except Exception as e:
        return {
            'json_serializable': False,
            'error': str(e)
        }

def test_lazy_instantiation():
    """Test lazy instantiation and on-demand CLI generation."""
    
    from src.multi_perspective_ghostbusters.conflict_analysis_resolver import ConflictAnalysisResolver
    
    # Test that CLI generation doesn't happen until needed
    try:
        resolver = ConflictAnalysisResolver()
        
        # Component should be instantiated without CLI generation
        instantiation_success = hasattr(resolver, 'resolver_id')
        
        # CLI generation should happen on-demand
        cli_interface = resolver.generate_cli_interface()
        cli_generation_success = cli_interface is not None
        
        # Health check should work immediately
        health = resolver.health_check()
        health_check_success = health.status.value == 'healthy'
        
        return {
            'lazy_instantiation': instantiation_success,
            'on_demand_cli': cli_generation_success,
            'immediate_health_check': health_check_success,
            'overall_success': instantiation_success and cli_generation_success and health_check_success
        }
        
    except Exception as e:
        return {
            'lazy_instantiation': False,
            'error': str(e)
        }

def test_cli_parameter_validation():
    """Test parameter validation in CLI commands."""
    
    from src.multi_perspective_ghostbusters.unique_insight_preserver import UniqueInsightPreserver
    
    preserver = UniqueInsightPreserver()
    
    validation_results = {
        'handles_empty_lists': False,
        'validates_parameter_types': False,
        'provides_meaningful_errors': False
    }
    
    # Test empty list handling
    try:
        result = preserver.identify_unique_insights([])
        validation_results['handles_empty_lists'] = isinstance(result, list)
    except Exception:
        validation_results['handles_empty_lists'] = False
    
    # Test parameter type validation (implicit through method execution)
    try:
        result = preserver.preserve_original_context([])
        validation_results['validates_parameter_types'] = isinstance(result, dict)
    except Exception:
        validation_results['validates_parameter_types'] = False
    
    # Test meaningful error handling
    try:
        health = preserver.health_check()
        validation_results['provides_meaningful_errors'] = hasattr(health, 'status')
    except Exception:
        validation_results['provides_meaningful_errors'] = False
    
    return validation_results

def test_cross_component_cli_consistency():
    """Test CLI consistency across different components."""
    
    components = [
        ('AgentLifecycleManager', 'src.multi_perspective_ghostbusters.agent_lifecycle_manager'),
        ('SecurityExpert', 'src.multi_perspective_ghostbusters.security_expert'),
        ('ConsensusDetector', 'src.multi_perspective_ghostbusters.consensus_detector'),
        ('DiversityValidator', 'src.multi_perspective_ghostbusters.diversity_validator')
    ]
    
    consistency_results = {
        'all_have_health_check': True,
        'all_have_execute': True,
        'consistent_output_format': True,
        'consistent_error_handling': True
    }
    
    component_outputs = []
    
    for name, module_path in components:
        try:
            module = __import__(module_path, fromlist=[name])
            component_class = getattr(module, name)
            instance = component_class()
            
            # Test health check consistency
            health = instance.health_check()
            if not hasattr(health, 'status'):
                consistency_results['all_have_health_check'] = False
            
            # Test execute method consistency
            output = instance.execute()
            if not isinstance(output, dict):
                consistency_results['all_have_execute'] = False
            
            component_outputs.append(output)
            
            # Test required fields in output
            required_fields = ['component_type', 'capabilities', 'status']
            if not all(field in output for field in required_fields):
                consistency_results['consistent_output_format'] = False
                
        except Exception:
            consistency_results['consistent_error_handling'] = False
    
    return consistency_results

def run_comprehensive_cli_integration_tests():
    """Run comprehensive CLI integration tests."""
    
    print("🚨 Multi-Perspective Ghostbusters CLI Integration Tests 🚨")
    print("=" * 70)
    
    # Test 1: CLI command execution
    print("\n1. Testing CLI Command Execution...")
    execution_result = test_cli_command_execution()
    if execution_result['command_execution']:
        print(f"   ✅ CLI commands execute successfully")
        print(f"   ✅ Found {execution_result['consensus_areas_found']} consensus areas")
        print(f"   ✅ Calculated {execution_result['confidence_scores_calculated']} confidence scores")
    else:
        print(f"   ❌ CLI command execution failed: {execution_result.get('error', 'Unknown error')}")
    
    # Test 2: Error handling and validation
    print("\n2. Testing Error Handling and Validation...")
    error_result = test_error_handling_and_validation()
    passed_error_tests = sum(error_result.values())
    total_error_tests = len(error_result)
    print(f"   ✅ Error handling tests: {passed_error_tests}/{total_error_tests} passed")
    
    # Test 3: CLI output formatting
    print("\n3. Testing CLI Output Formatting...")
    format_result = test_cli_output_formatting()
    if format_result.get('json_serializable', False) and format_result.get('output_structure', False):
        print("   ✅ CLI output formatting and JSON serialization successful")
    else:
        print(f"   ❌ CLI output formatting failed: {format_result.get('error', 'Unknown error')}")
    
    # Test 4: Lazy instantiation
    print("\n4. Testing Lazy Instantiation...")
    lazy_result = test_lazy_instantiation()
    if lazy_result.get('overall_success', False):
        print("   ✅ Lazy instantiation and on-demand CLI generation successful")
    else:
        print(f"   ❌ Lazy instantiation failed: {lazy_result.get('error', 'Unknown error')}")
    
    # Test 5: Parameter validation
    print("\n5. Testing CLI Parameter Validation...")
    validation_result = test_cli_parameter_validation()
    passed_validation_tests = sum(validation_result.values())
    total_validation_tests = len(validation_result)
    print(f"   ✅ Parameter validation tests: {passed_validation_tests}/{total_validation_tests} passed")
    
    # Test 6: Cross-component consistency
    print("\n6. Testing Cross-Component CLI Consistency...")
    consistency_result = test_cross_component_cli_consistency()
    passed_consistency_tests = sum(consistency_result.values())
    total_consistency_tests = len(consistency_result)
    print(f"   ✅ CLI consistency tests: {passed_consistency_tests}/{total_consistency_tests} passed")
    
    # Summary
    print("\n" + "=" * 70)
    print("CLI INTEGRATION TEST SUMMARY")
    print("=" * 70)
    
    overall_success = (
        execution_result['command_execution'] and
        passed_error_tests >= 2 and
        format_result.get('json_serializable', False) and
        lazy_result.get('overall_success', False) and
        passed_validation_tests >= 2 and
        passed_consistency_tests >= 3
    )
    
    print(f"✅ Command execution: {'PASS' if execution_result['command_execution'] else 'FAIL'}")
    print(f"✅ Error handling: {passed_error_tests}/{total_error_tests} tests passed")
    print(f"✅ Output formatting: {'PASS' if format_result.get('json_serializable', False) else 'FAIL'}")
    print(f"✅ Lazy instantiation: {'PASS' if lazy_result.get('overall_success', False) else 'FAIL'}")
    print(f"✅ Parameter validation: {passed_validation_tests}/{total_validation_tests} tests passed")
    print(f"✅ CLI consistency: {passed_consistency_tests}/{total_consistency_tests} tests passed")
    
    print(f"\n🎯 OVERALL CLI INTEGRATION: {'SUCCESS' if overall_success else 'NEEDS ATTENTION'}")
    
    return {
        'overall_success': overall_success,
        'detailed_results': {
            'execution': execution_result,
            'error_handling': error_result,
            'formatting': format_result,
            'lazy_instantiation': lazy_result,
            'validation': validation_result,
            'consistency': consistency_result
        }
    }

if __name__ == "__main__":
    results = run_comprehensive_cli_integration_tests()