#!/usr/bin/env python3
"""
Quick test script for WebSocket ontology analysis
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

try:
    from beast_mode.observatory.ontology.websocket_analyzer import WebSocketOntologyAnalyzer
    
    def test_ontology_loading():
        """Test basic ontology loading"""
        print("🔄 Testing ontology loading...")
        
        ontology_path = Path("docs/ontology/websocket_ontology.ttl")
        if not ontology_path.exists():
            print(f"❌ Ontology file not found: {ontology_path}")
            return False
        
        try:
            analyzer = WebSocketOntologyAnalyzer(ontology_path)
            health = analyzer.health_check()
            
            print(f"✅ Ontology loaded successfully!")
            print(f"   Triples: {health['triple_count']:,}")
            print(f"   Namespaces: {health['namespaces']}")
            print(f"   Status: {health['status']}")
            
            return True
            
        except Exception as e:
            print(f"❌ Failed to load ontology: {e}")
            return False
    
    def test_symptom_analysis():
        """Test symptom analysis"""
        print("\n🔍 Testing symptom analysis...")
        
        try:
            analyzer = WebSocketOntologyAnalyzer()
            symptoms = ["connection drops", "high latency", "polling fallback"]
            
            problems = analyzer.analyze_symptoms(symptoms)
            print(f"✅ Found {len(problems)} potential problems")
            
            for problem in problems[:3]:  # Show first 3
                print(f"   • {problem.problem_type} (confidence: {problem.confidence:.2f})")
            
            return True
            
        except Exception as e:
            print(f"❌ Symptom analysis failed: {e}")
            return False
    
    def test_immediate_fixes():
        """Test immediate fixes query"""
        print("\n⚡ Testing immediate fixes query...")
        
        try:
            analyzer = WebSocketOntologyAnalyzer()
            fixes = analyzer.get_immediate_fixes()
            
            print(f"✅ Found {len(fixes)} immediate fixes")
            
            for fix in fixes[:3]:  # Show first 3
                print(f"   • {fix.solution_type} ({fix.implementation_time})")
            
            return True
            
        except Exception as e:
            print(f"❌ Immediate fixes query failed: {e}")
            return False
    
    def main():
        """Run all tests"""
        print("🧪 WebSocket Ontology Test Suite")
        print("=" * 50)
        
        tests = [
            test_ontology_loading,
            test_symptom_analysis,
            test_immediate_fixes
        ]
        
        passed = 0
        for test in tests:
            if test():
                passed += 1
        
        print(f"\n📊 Results: {passed}/{len(tests)} tests passed")
        
        if passed == len(tests):
            print("🎉 All tests passed! Ontology is ready for use.")
            return 0
        else:
            print("⚠️  Some tests failed. Check the output above.")
            return 1

    if __name__ == "__main__":
        sys.exit(main())

except ImportError as e:
    print(f"❌ Import error: {e}")
    print("💡 Install dependencies with: pip install -r requirements-ontology.txt")
    sys.exit(1)