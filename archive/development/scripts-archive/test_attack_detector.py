#!/usr/bin/env python3
"""
Test script for attack detection system.
"""

import asyncio
import sys
from pathlib import Path
from datetime import datetime, timedelta

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

async def test_attack_detector():
    """Test the attack detection system comprehensively."""
    
    print("🧪 Testing Attack Detection System...")
    
    try:
        # Import the detector
        from beast_mode.observatory.bot_defense.attack_detector import get_attack_detector, AttackAnalysis
        from beast_mode.observatory.bot_defense.models import AttackType
        
        detector = get_attack_detector()
        print("✅ Attack detector initialized")
        
        # Test 1: Normal request (should not be suspicious)
        print("\n🔍 Test 1: Normal request")
        analysis = await detector.analyze_request(
            source_ip="192.168.1.100",
            endpoint="/",
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            method="GET"
        )
        print(f"   Normal request: suspicious={analysis.is_suspicious}, confidence={analysis.confidence_score:.2f}")
        assert not analysis.is_suspicious, "Normal request should not be suspicious"
        
        # Test 2: Suspicious endpoint access
        print("\n🔍 Test 2: Suspicious endpoint access")
        analysis = await detector.analyze_request(
            source_ip="192.168.1.101",
            endpoint="/wp-admin/admin.php",
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            method="GET"
        )
        print(f"   Suspicious endpoint: suspicious={analysis.is_suspicious}, confidence={analysis.confidence_score:.2f}")
        print(f"   Reasons: {analysis.reasons}")
        assert analysis.is_suspicious, "Suspicious endpoint should be detected"
        assert analysis.attack_type == AttackType.SUSPICIOUS_ENDPOINT
        
        # Test 3: Bot user agent
        print("\n🔍 Test 3: Bot user agent detection")
        analysis = await detector.analyze_request(
            source_ip="192.168.1.102",
            endpoint="/robots.txt",
            user_agent="Googlebot/2.1 (+http://www.google.com/bot.html)",
            method="GET"
        )
        print(f"   Bot user agent: suspicious={analysis.is_suspicious}, confidence={analysis.confidence_score:.2f}")
        print(f"   Reasons: {analysis.reasons}")
        
        # Test 4: Rate limiting (simulate rapid requests)
        print("\n🔍 Test 4: Rate limiting detection")
        test_ip = "192.168.1.103"
        
        # Send many requests rapidly
        for i in range(70):  # Exceed the 60 requests/minute limit
            await detector.analyze_request(
                source_ip=test_ip,
                endpoint=f"/page{i}",
                user_agent="curl/7.68.0",
                method="GET"
            )
        
        # Check if rate limiting is detected
        analysis = await detector.analyze_request(
            source_ip=test_ip,
            endpoint="/test",
            user_agent="curl/7.68.0",
            method="GET"
        )
        print(f"   Rate limiting: suspicious={analysis.is_suspicious}, confidence={analysis.confidence_score:.2f}")
        print(f"   Reasons: {analysis.reasons}")
        assert analysis.is_suspicious, "Rate limiting should be detected"
        
        # Test 5: SQL injection attempt
        print("\n🔍 Test 5: SQL injection detection")
        analysis = await detector.analyze_request(
            source_ip="192.168.1.104",
            endpoint="/search",
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            method="GET",
            query_params={"q": "'; DROP TABLE users; --"}
        )
        print(f"   SQL injection: suspicious={analysis.is_suspicious}, confidence={analysis.confidence_score:.2f}")
        print(f"   Reasons: {analysis.reasons}")
        assert analysis.is_suspicious, "SQL injection should be detected"
        
        # Test 6: XSS attempt
        print("\n🔍 Test 6: XSS detection")
        analysis = await detector.analyze_request(
            source_ip="192.168.1.105",
            endpoint="/comment",
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            method="POST",
            query_params={"comment": "<script>alert('xss')</script>"}
        )
        print(f"   XSS attempt: suspicious={analysis.is_suspicious}, confidence={analysis.confidence_score:.2f}")
        print(f"   Reasons: {analysis.reasons}")
        assert analysis.is_suspicious, "XSS attempt should be detected"
        
        # Test 7: Path traversal attempt
        print("\n🔍 Test 7: Path traversal detection")
        analysis = await detector.analyze_request(
            source_ip="192.168.1.106",
            endpoint="/file",
            user_agent="curl/7.68.0",
            method="GET",
            query_params={"path": "../../../../etc/passwd"}
        )
        print(f"   Path traversal: suspicious={analysis.is_suspicious}, confidence={analysis.confidence_score:.2f}")
        print(f"   Reasons: {analysis.reasons}")
        assert analysis.is_suspicious, "Path traversal should be detected"
        
        # Test 8: Scanning behavior (many 404s)
        print("\n🔍 Test 8: Scanning behavior detection")
        scanner_ip = "192.168.1.107"
        
        # Simulate directory scanning with many 404s
        for i in range(15):
            await detector.analyze_request(
                source_ip=scanner_ip,
                endpoint=f"/admin{i}/",
                user_agent="curl/7.68.0",
                method="GET",
                response_code=404
            )
        
        analysis = await detector.analyze_request(
            source_ip=scanner_ip,
            endpoint="/admin999/",
            user_agent="curl/7.68.0",
            method="GET",
            response_code=404
        )
        print(f"   Scanning behavior: suspicious={analysis.is_suspicious}, confidence={analysis.confidence_score:.2f}")
        print(f"   Reasons: {analysis.reasons}")
        assert analysis.is_suspicious, "Scanning behavior should be detected"
        
        # Test 9: Get suspicious IPs
        print("\n🔍 Test 9: Suspicious IPs tracking")
        suspicious_ips = await detector.get_suspicious_ips()
        print(f"   Found {len(suspicious_ips)} suspicious IPs")
        for ip_info in suspicious_ips[:3]:  # Show top 3
            print(f"   - {ip_info['ip']}: score={ip_info['suspicion_score']:.2f}, requests={ip_info['request_count']}")
        
        assert len(suspicious_ips) > 0, "Should have detected suspicious IPs"
        
        # Test 10: Detection statistics
        print("\n🔍 Test 10: Detection statistics")
        stats = detector.get_detection_stats()
        print(f"   Total IPs tracked: {stats['total_ips_tracked']}")
        print(f"   Suspicious IPs: {stats['suspicious_ips']}")
        print(f"   Detection patterns: {stats['detection_patterns']}")
        
        assert stats['total_ips_tracked'] > 0, "Should be tracking IPs"
        assert stats['suspicious_ips'] > 0, "Should have found suspicious IPs"
        
        print("\n🎉 All attack detection tests passed!")
        return True
        
    except Exception as e:
        print(f"\n💥 Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(test_attack_detector())
    sys.exit(0 if success else 1)