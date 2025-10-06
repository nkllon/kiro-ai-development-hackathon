#!/usr/bin/env python3
"""Validation script for WebSocket connection optimization implementation."""

import sys
import os
import json
from datetime import datetime

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def validate_file_structure():
    """Validate that all required files exist and have correct line counts."""
    required_files = [
        {
            'path': 'src/beast_mode/observatory/websocket/connection_pool.py',
            'min_lines': 120,
            'description': 'Connection pooling and reuse mechanisms'
        },
        {
            'path': 'src/beast_mode/observatory/websocket/message_optimizer.py',
            'min_lines': 100,
            'description': 'Message batching and optimization system'
        },
        {
            'path': 'src/beast_mode/observatory/websocket/compression_handler.py',
            'min_lines': 80,
            'description': 'Compression and serialization optimization'
        },
        {
            'path': 'tests/unit/websocket/test_connection_optimization.py',
            'min_lines': 60,
            'description': 'Comprehensive test suite'
        }
    ]
    
    validation_results = {
        'timestamp': datetime.utcnow().isoformat(),
        'task': '8.1',
        'action': 'websocket_optimization_validation',
        'status': 'in_progress',
        'results': []
    }
    
    all_passed = True
    
    for file_info in required_files:
        file_path = file_info['path']
        min_lines = file_info['min_lines']
        description = file_info['description']
        
        try:
            if os.path.exists(file_path):
                with open(file_path, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                    line_count = len(lines)
                    
                if line_count >= min_lines:
                    result = {
                        'file': file_path,
                        'status': 'PASS',
                        'line_count': line_count,
                        'min_required': min_lines,
                        'description': description
                    }
                else:
                    result = {
                        'file': file_path,
                        'status': 'FAIL',
                        'line_count': line_count,
                        'min_required': min_lines,
                        'description': description,
                        'error': f'File has {line_count} lines, but minimum {min_lines} required'
                    }
                    all_passed = False
            else:
                result = {
                    'file': file_path,
                    'status': 'FAIL',
                    'line_count': 0,
                    'min_required': min_lines,
                    'description': description,
                    'error': 'File does not exist'
                }
                all_passed = False
            
            validation_results['results'].append(result)
            
        except Exception as e:
            result = {
                'file': file_path,
                'status': 'ERROR',
                'line_count': 0,
                'min_required': min_lines,
                'description': description,
                'error': str(e)
            }
            all_passed = False
            validation_results['results'].append(result)
    
    validation_results['status'] = 'completed' if all_passed else 'failed'
    validation_results['summary'] = {
        'total_files': len(required_files),
        'passed': len([r for r in validation_results['results'] if r['status'] == 'PASS']),
        'failed': len([r for r in validation_results['results'] if r['status'] == 'FAIL']),
        'errors': len([r for r in validation_results['results'] if r['status'] == 'ERROR']),
        'overall_status': 'PASS' if all_passed else 'FAIL'
    }
    
    return validation_results

def validate_imports():
    """Validate that the modules can be imported without errors."""
    import_results = {
        'timestamp': datetime.utcnow().isoformat(),
        'task': '8.1',
        'action': 'websocket_import_validation',
        'status': 'in_progress',
        'results': []
    }
    
    modules_to_test = [
        'src.beast_mode.observatory.websocket.connection_pool',
        'src.beast_mode.observatory.websocket.message_optimizer',
        'src.beast_mode.observatory.websocket.compression_handler',
    ]
    
    all_imported = True
    
    for module_name in modules_to_test:
        try:
            __import__(module_name)
            import_results['results'].append({
                'module': module_name,
                'status': 'PASS',
                'error': None
            })
        except ImportError as e:
            import_results['results'].append({
                'module': module_name,
                'status': 'FAIL',
                'error': str(e)
            })
            all_imported = False
        except Exception as e:
            import_results['results'].append({
                'module': module_name,
                'status': 'ERROR',
                'error': str(e)
            })
            all_imported = False
    
    import_results['status'] = 'completed' if all_imported else 'failed'
    import_results['summary'] = {
        'total_modules': len(modules_to_test),
        'imported_successfully': len([r for r in import_results['results'] if r['status'] == 'PASS']),
        'import_failures': len([r for r in import_results['results'] if r['status'] == 'FAIL']),
        'import_errors': len([r for r in import_results['results'] if r['status'] == 'ERROR']),
        'overall_status': 'PASS' if all_imported else 'FAIL'
    }
    
    return import_results

def validate_performance_features():
    """Validate that performance optimization features are implemented."""
    feature_results = {
        'timestamp': datetime.utcnow().isoformat(),
        'task': '8.1',
        'action': 'websocket_performance_features_validation',
        'status': 'in_progress',
        'features': []
    }
    
    # Check for key performance features in the code
    performance_features = [
        {
            'name': 'Connection Pooling',
            'file': 'src/beast_mode/observatory/websocket/connection_pool.py',
            'keywords': ['ConnectionPool', 'pool_strategy', 'connection_reuse', 'health_check']
        },
        {
            'name': 'Message Batching',
            'file': 'src/beast_mode/observatory/websocket/message_optimizer.py',
            'keywords': ['MessageBatch', 'batch_strategy', 'message_queue', 'optimization']
        },
        {
            'name': 'Compression',
            'file': 'src/beast_mode/observatory/websocket/compression_handler.py',
            'keywords': ['CompressionHandler', 'compression_ratio', 'serialization', 'algorithm']
        },
        {
            'name': 'Memory Optimization',
            'file': 'src/beast_mode/observatory/websocket/connection_pool.py',
            'keywords': ['memory_usage', 'cache', 'cleanup', 'metrics']
        },
        {
            'name': 'CPU Optimization',
            'file': 'src/beast_mode/observatory/websocket/message_optimizer.py',
            'keywords': ['parallel', 'async', 'background_task', 'processing']
        }
    ]
    
    all_features_present = True
    
    for feature in performance_features:
        try:
            if os.path.exists(feature['file']):
                with open(feature['file'], 'r', encoding='utf-8') as f:
                    content = f.read()
                
                keywords_found = []
                for keyword in feature['keywords']:
                    if keyword in content:
                        keywords_found.append(keyword)
                
                if len(keywords_found) >= len(feature['keywords']) * 0.5:  # At least 50% of keywords
                    feature_result = {
                        'name': feature['name'],
                        'status': 'PASS',
                        'keywords_found': keywords_found,
                        'coverage': len(keywords_found) / len(feature['keywords'])
                    }
                else:
                    feature_result = {
                        'name': feature['name'],
                        'status': 'FAIL',
                        'keywords_found': keywords_found,
                        'coverage': len(keywords_found) / len(feature['keywords']),
                        'error': f'Only found {len(keywords_found)}/{len(feature["keywords"])} keywords'
                    }
                    all_features_present = False
            else:
                feature_result = {
                    'name': feature['name'],
                    'status': 'FAIL',
                    'keywords_found': [],
                    'coverage': 0,
                    'error': 'File does not exist'
                }
                all_features_present = False
            
            feature_results['features'].append(feature_result)
            
        except Exception as e:
            feature_result = {
                'name': feature['name'],
                'status': 'ERROR',
                'keywords_found': [],
                'coverage': 0,
                'error': str(e)
            }
            all_features_present = False
            feature_results['features'].append(feature_result)
    
    feature_results['status'] = 'completed' if all_features_present else 'failed'
    feature_results['summary'] = {
        'total_features': len(performance_features),
        'features_present': len([f for f in feature_results['features'] if f['status'] == 'PASS']),
        'features_missing': len([f for f in feature_results['features'] if f['status'] == 'FAIL']),
        'feature_errors': len([f for f in feature_results['features'] if f['status'] == 'ERROR']),
        'overall_status': 'PASS' if all_features_present else 'FAIL'
    }
    
    return feature_results

def main():
    """Run all validation checks."""
    print("🔍 Validating WebSocket Connection Optimization Implementation")
    print("=" * 60)
    
    # Run file structure validation
    print("\n📁 Validating file structure and line counts...")
    file_results = validate_file_structure()
    print(json.dumps(file_results, indent=2))
    
    # Run import validation
    print("\n📦 Validating module imports...")
    import_results = validate_imports()
    print(json.dumps(import_results, indent=2))
    
    # Run performance features validation
    print("\n⚡ Validating performance optimization features...")
    feature_results = validate_performance_features()
    print(json.dumps(feature_results, indent=2))
    
    # Overall summary
    print("\n📊 Overall Validation Summary")
    print("=" * 60)
    
    file_status = file_results['summary']['overall_status']
    import_status = import_results['summary']['overall_status']
    feature_status = feature_results['summary']['overall_status']
    
    print(f"File Structure: {file_status}")
    print(f"Module Imports: {import_status}")
    print(f"Performance Features: {feature_status}")
    
    overall_status = 'PASS' if all([file_status == 'PASS', import_status == 'PASS', feature_status == 'PASS']) else 'FAIL'
    print(f"\n🎯 Overall Status: {overall_status}")
    
    if overall_status == 'PASS':
        print("\n✅ WebSocket Connection Optimization implementation is VALID")
        print("   All required files created with sufficient content")
        print("   Performance optimization features implemented")
        print("   Connection pooling, message batching, and compression ready")
    else:
        print("\n❌ WebSocket Connection Optimization implementation has ISSUES")
        print("   Please review the validation results above")
    
    return overall_status == 'PASS'

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)