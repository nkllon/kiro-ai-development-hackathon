#!/usr/bin/env python3
"""
Import Historical Beast Mode Metrics to Prometheus
=================================================

This script imports the historical performance data from the JSONL file
into Prometheus via a custom metrics exporter.
"""

import json
import time
import requests
from datetime import datetime
from pathlib import Path

def import_historical_data():
    """Import historical metrics data into Prometheus format."""
    
    # Read the historical data
    data_file = Path("metrics_data/gke_velocity_measurements.jsonl")
    
    if not data_file.exists():
        print(f"❌ Data file not found: {data_file}")
        return
    
    print(f"📊 Reading historical data from {data_file}")
    
    metrics_data = []
    with open(data_file, 'r') as f:
        for line in f:
            try:
                data = json.loads(line.strip())
                metrics_data.append(data)
            except json.JSONDecodeError:
                continue
    
    print(f"✅ Loaded {len(metrics_data)} historical measurements")
    
    # Group by measurement type
    before_beast_mode = [d for d in metrics_data if d.get('measurement_type') == 'before_beast_mode']
    after_beast_mode = [d for d in metrics_data if d.get('measurement_type') == 'after_beast_mode']
    
    print(f"📈 Before Beast Mode: {len(before_beast_mode)} measurements")
    print(f"🚀 After Beast Mode: {len(after_beast_mode)} measurements")
    
    # Calculate improvements
    if before_beast_mode and after_beast_mode:
        before_avg = {
            'features_per_day': sum(d['features_completed_per_day'] for d in before_beast_mode) / len(before_beast_mode),
            'bugs_per_day': sum(d['bugs_fixed_per_day'] for d in before_beast_mode) / len(before_beast_mode),
            'code_quality': sum(d['code_quality_score'] for d in before_beast_mode) / len(before_beast_mode),
            'rework_pct': sum(d['rework_percentage'] for d in before_beast_mode) / len(before_beast_mode),
            'resolution_hours': sum(d['time_to_resolution_hours'] for d in before_beast_mode) / len(before_beast_mode)
        }
        
        after_avg = {
            'features_per_day': sum(d['features_completed_per_day'] for d in after_beast_mode) / len(after_beast_mode),
            'bugs_per_day': sum(d['bugs_fixed_per_day'] for d in after_beast_mode) / len(after_beast_mode),
            'code_quality': sum(d['code_quality_score'] for d in after_beast_mode) / len(after_beast_mode),
            'rework_pct': sum(d['rework_percentage'] for d in after_beast_mode) / len(after_beast_mode),
            'resolution_hours': sum(d['time_to_resolution_hours'] for d in after_beast_mode) / len(after_beast_mode)
        }
        
        print("\n🎯 PERFORMANCE IMPROVEMENTS:")
        print(f"   Features/Day: {before_avg['features_per_day']:.2f} → {after_avg['features_per_day']:.2f} (+{((after_avg['features_per_day']/before_avg['features_per_day']-1)*100):.1f}%)")
        print(f"   Bugs Fixed/Day: {before_avg['bugs_per_day']:.2f} → {after_avg['bugs_per_day']:.2f} (+{((after_avg['bugs_per_day']/before_avg['bugs_per_day']-1)*100):.1f}%)")
        print(f"   Code Quality: {before_avg['code_quality']:.1f} → {after_avg['code_quality']:.1f} (+{((after_avg['code_quality']/before_avg['code_quality']-1)*100):.1f}%)")
        print(f"   Rework %: {before_avg['rework_pct']:.1f}% → {after_avg['rework_pct']:.1f}% ({((after_avg['rework_pct']/before_avg['rework_pct']-1)*100):.1f}%)")
        print(f"   Resolution Time: {before_avg['resolution_hours']:.1f}h → {after_avg['resolution_hours']:.1f}h ({((after_avg['resolution_hours']/before_avg['resolution_hours']-1)*100):.1f}%)")
        
        # Create Prometheus metrics format
        prometheus_metrics = f"""# HELP beast_mode_features_completed_per_day Features completed per day
# TYPE beast_mode_features_completed_per_day gauge
beast_mode_features_completed_per_day{{phase="before"}} {before_avg['features_per_day']}
beast_mode_features_completed_per_day{{phase="after"}} {after_avg['features_per_day']}

# HELP beast_mode_bugs_fixed_per_day Bugs fixed per day
# TYPE beast_mode_bugs_fixed_per_day gauge
beast_mode_bugs_fixed_per_day{{phase="before"}} {before_avg['bugs_per_day']}
beast_mode_bugs_fixed_per_day{{phase="after"}} {after_avg['bugs_per_day']}

# HELP beast_mode_code_quality_score Code quality score
# TYPE beast_mode_code_quality_score gauge
beast_mode_code_quality_score{{phase="before"}} {before_avg['code_quality']}
beast_mode_code_quality_score{{phase="after"}} {after_avg['code_quality']}

# HELP beast_mode_rework_percentage Rework percentage
# TYPE beast_mode_rework_percentage gauge
beast_mode_rework_percentage{{phase="before"}} {before_avg['rework_pct']}
beast_mode_rework_percentage{{phase="after"}} {after_avg['rework_pct']}

# HELP beast_mode_time_to_resolution_hours Time to resolution in hours
# TYPE beast_mode_time_to_resolution_hours gauge
beast_mode_time_to_resolution_hours{{phase="before"}} {before_avg['resolution_hours']}
beast_mode_time_to_resolution_hours{{phase="after"}} {after_avg['resolution_hours']}

# HELP beast_mode_improvement_factor Overall improvement factor
# TYPE beast_mode_improvement_factor gauge
beast_mode_improvement_factor {{}} {after_avg['features_per_day']/before_avg['features_per_day']}
"""
        
        # Save metrics to file for manual import
        with open('beast_mode_metrics.prom', 'w') as f:
            f.write(prometheus_metrics)
        
        print(f"\n📁 Prometheus metrics saved to: beast_mode_metrics.prom")
        print(f"🔗 Dashboard URL: http://localhost:3000/d/7dd80317-f880-4c8d-a2fc-ce075764d429/beast-mode-performance-observatory")
        
        return True
    
    return False

if __name__ == "__main__":
    print("🚀 Beast Mode Historical Data Import")
    print("=" * 50)
    
    success = import_historical_data()
    
    if success:
        print("\n✅ Historical data processed successfully!")
        print("🎯 Next steps:")
        print("   1. Open Grafana: http://localhost:3000")
        print("   2. View Beast Mode Dashboard")
        print("   3. Login: admin/systematic")
    else:
        print("\n❌ Failed to process historical data")