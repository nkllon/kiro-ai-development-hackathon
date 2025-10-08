#!/usr/bin/env python3
"""
Redis Data Explorer
Analyzes Redis data and provides insights for dashboard creation
"""

import redis
import json
import time
from datetime import datetime
from typing import Dict, List, Any

def connect_redis():
    """Connect to Redis."""
    try:
        r = redis.Redis(host='localhost', port=6379, decode_responses=True)
        r.ping()
        print("✅ Connected to Redis")
        return r
    except Exception as e:
        print(f"❌ Failed to connect to Redis: {e}")
        return None

def analyze_stream_data(r: redis.Redis, stream_name: str, count: int = 10) -> Dict[str, Any]:
    """Analyze Redis stream data."""
    try:
        # Get stream length
        length = r.xlen(stream_name)
        
        # Get recent entries
        entries = r.xrevrange(stream_name, count=count)
        
        # Analyze field patterns
        fields = set()
        sample_entry = None
        
        for entry_id, entry_data in entries:
            fields.update(entry_data.keys())
            if not sample_entry:
                sample_entry = entry_data
        
        return {
            'length': length,
            'fields': list(fields),
            'sample_entry': sample_entry,
            'recent_entries': len(entries)
        }
        
    except Exception as e:
        print(f"❌ Error analyzing stream {stream_name}: {e}")
        return {}

def analyze_hash_data(r: redis.Redis, key_name: str) -> Dict[str, Any]:
    """Analyze Redis hash data."""
    try:
        data = r.hgetall(key_name)
        return {
            'field_count': len(data),
            'fields': list(data.keys()),
            'sample_data': data
        }
    except Exception as e:
        print(f"❌ Error analyzing hash {key_name}: {e}")
        return {}

def analyze_list_data(r: redis.Redis, key_name: str) -> Dict[str, Any]:
    """Analyze Redis list data."""
    try:
        length = r.llen(key_name)
        recent_items = r.lrange(key_name, -5, -1)
        
        # Try to parse JSON items
        parsed_items = []
        for item in recent_items:
            try:
                parsed_items.append(json.loads(item))
            except:
                parsed_items.append(item)
        
        return {
            'length': length,
            'recent_items': parsed_items
        }
    except Exception as e:
        print(f"❌ Error analyzing list {key_name}: {e}")
        return {}

def generate_insights(analysis: Dict[str, Any]) -> List[str]:
    """Generate insights from Redis data analysis."""
    insights = []
    
    # Observatory metrics insights
    if 'observatory_metrics' in analysis:
        metrics = analysis['observatory_metrics']
        if metrics.get('length', 0) > 1000000:
            insights.append(f"🚀 Massive metrics collection: {metrics['length']:,} entries!")
        
        fields = metrics.get('fields', [])
        if 'health_score' in fields:
            insights.append("💚 Health monitoring active with health scores")
        if 'error_count' in fields:
            insights.append("🔍 Error tracking enabled")
        if 'memory_usage_mb' in fields:
            insights.append("📊 Resource monitoring (CPU/Memory) active")
    
    # LLM cost insights
    if 'observatory_metrics:llm_costs' in analysis:
        costs = analysis['observatory_metrics:llm_costs']
        if costs.get('length', 0) > 0:
            insights.append(f"💰 LLM cost tracking: {costs['length']} calls recorded")
            
            sample = costs.get('sample_entry', {})
            if 'estimated_cost' in sample:
                try:
                    cost = float(sample['estimated_cost'])
                    insights.append(f"💵 Recent LLM call cost: ${cost:.4f}")
                except:
                    pass
    
    # Analytics insights
    if 'observatory_metrics:analytics' in analysis:
        analytics = analysis['observatory_metrics:analytics']
        if analytics.get('length', 0) > 10000:
            insights.append(f"📈 Rich analytics data: {analytics['length']:,} entries")
    
    # Agent insights
    if 'beast_mode:active_agents' in analysis:
        agents = analysis['beast_mode:active_agents']
        if agents.get('field_count', 0) > 0:
            insights.append(f"🤖 Active agents: {agents['field_count']} registered")
    
    # Message insights
    if 'beast_mode_messages' in analysis:
        messages = analysis['beast_mode_messages']
        if messages.get('length', 0) > 0:
            insights.append(f"💬 Inter-agent communication: {messages['length']} messages")
    
    return insights

def main():
    """Main analysis function."""
    print("🔍 Redis Data Explorer")
    print("=" * 50)
    
    # Connect to Redis
    r = connect_redis()
    if not r:
        return False
    
    # Get all keys
    keys = r.keys('*')
    print(f"📊 Found {len(keys)} Redis keys")
    
    analysis = {}
    
    # Analyze each key
    for key in keys:
        key_type = r.type(key)
        print(f"\n🔑 Analyzing key: {key} (type: {key_type})")
        
        if key_type == 'stream':
            analysis[key] = analyze_stream_data(r, key)
            print(f"   📈 Stream length: {analysis[key].get('length', 0):,}")
            print(f"   🏷️  Fields: {', '.join(analysis[key].get('fields', [])[:5])}")
            
        elif key_type == 'hash':
            analysis[key] = analyze_hash_data(r, key)
            print(f"   🗂️  Hash fields: {analysis[key].get('field_count', 0)}")
            
        elif key_type == 'list':
            analysis[key] = analyze_list_data(r, key)
            print(f"   📝 List length: {analysis[key].get('length', 0)}")
    
    # Generate insights
    print(f"\n🎯 Key Insights:")
    print("-" * 30)
    insights = generate_insights(analysis)
    for insight in insights:
        print(f"   {insight}")
    
    # Dashboard recommendations
    print(f"\n📊 Dashboard Recommendations:")
    print("-" * 35)
    
    if 'observatory_metrics' in analysis and analysis['observatory_metrics'].get('length', 0) > 1000:
        print("   ✅ Component Health Dashboard - Rich health data available")
    
    if 'observatory_metrics:llm_costs' in analysis and analysis['observatory_metrics:llm_costs'].get('length', 0) > 0:
        print("   ✅ LLM Cost Analytics Dashboard - Cost tracking data available")
    
    if 'observatory_metrics:analytics' in analysis and analysis['observatory_metrics:analytics'].get('length', 0) > 100:
        print("   ✅ System Analytics Dashboard - Performance data available")
    
    if 'beast_mode_messages' in analysis and analysis['beast_mode_messages'].get('length', 0) > 0:
        print("   ✅ Agent Communication Dashboard - Message data available")
    
    # Access information
    print(f"\n🌐 Access Information:")
    print("-" * 25)
    print("   📊 Grafana: https://grafana.observatory.nkllon.com")
    print("   🔍 Look for 'Beast Mode' dashboards")
    print("   🔑 Login: admin / admin (or your configured password)")
    
    return True

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)