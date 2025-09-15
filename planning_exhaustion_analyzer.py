#!/usr/bin/env python3
"""
PLANNING EXHAUSTION ANALYZER
Continue planning until planning exhausts effectiveness of planning
Find the planning asymptote - the point of diminishing returns
"""

import json
import time
from datetime import datetime
from typing import Dict, List, Optional, Tuple
import random

class PlanningExhaustionAnalyzer:
    """Analyzes planning effectiveness until diminishing returns"""
    
    def __init__(self):
        self.analysis_start_time = datetime.now()
        self.analysis_id = f"planning_exhaustion_{self.analysis_start_time.strftime('%Y%m%d_%H%M%S')}"
        self.planning_cycles = []
        self.effectiveness_curve = []
        self.diminishing_returns_detected = False
        self.optimal_planning_depth = 0
        
        print("📊 PLANNING EXHAUSTION ANALYZER INITIATED")
        print("=" * 60)
        print(f"   Analysis ID: {self.analysis_id}")
        print(f"   Start Time: {self.analysis_start_time}")
        print("   Continue planning until planning exhausts effectiveness of planning")
        print()
    
    def calculate_planning_effectiveness(self, cycle_number: int, planning_depth: int, 
                                       time_spent: float, new_insights: int, 
                                       complexity_added: int) -> float:
        """Calculate planning effectiveness using multiple dimensions"""
        
        # Base effectiveness from insights gained
        insight_effectiveness = new_insights / max(1, cycle_number)
        
        # Time efficiency (diminishing returns over time)
        time_efficiency = 1.0 / (1.0 + time_spent * 0.1)
        
        # Complexity penalty (too much planning adds confusion)
        complexity_penalty = 1.0 / (1.0 + complexity_added * 0.05)
        
        # Depth effectiveness (deeper planning has diminishing returns)
        depth_effectiveness = 1.0 / (1.0 + planning_depth * 0.02)
        
        # Combined effectiveness score
        effectiveness = (insight_effectiveness * 0.4 + 
                        time_efficiency * 0.3 + 
                        complexity_penalty * 0.2 + 
                        depth_effectiveness * 0.1)
        
        return round(effectiveness, 4)
    
    def generate_planning_cycle(self, cycle_number: int) -> Dict:
        """Generate a single planning cycle with realistic parameters"""
        
        # Simulate realistic planning progression
        base_insights = max(1, 10 - cycle_number)  # Fewer new insights over time
        base_complexity = cycle_number * 2  # Increasing complexity
        base_time = cycle_number * 0.5  # More time spent per cycle
        
        # Add some randomness to simulate real planning
        new_insights = max(0, base_insights + random.randint(-2, 2))
        complexity_added = base_complexity + random.randint(-1, 3)
        time_spent = base_time + random.uniform(-0.2, 0.5)
        planning_depth = cycle_number
        
        effectiveness = self.calculate_planning_effectiveness(
            cycle_number, planning_depth, time_spent, new_insights, complexity_added
        )
        
        cycle = {
            'cycle_number': cycle_number,
            'planning_depth': planning_depth,
            'time_spent': round(time_spent, 2),
            'new_insights': new_insights,
            'complexity_added': complexity_added,
            'effectiveness': effectiveness,
            'timestamp': datetime.now().isoformat()
        }
        
        return cycle
    
    def detect_diminishing_returns(self, effectiveness_history: List[float], 
                                 window_size: int = 3) -> bool:
        """Detect when planning effectiveness starts declining"""
        
        if len(effectiveness_history) < window_size * 2:
            return False
        
        # Calculate moving averages
        recent_avg = sum(effectiveness_history[-window_size:]) / window_size
        previous_avg = sum(effectiveness_history[-window_size*2:-window_size]) / window_size
        
        # Check for consistent decline
        decline_threshold = 0.05  # 5% decline threshold
        
        if recent_avg < previous_avg * (1 - decline_threshold):
            return True
        
        return False
    
    def run_planning_exhaustion_analysis(self, max_cycles: int = 20) -> Dict:
        """Run planning analysis until diminishing returns detected"""
        
        print("🔄 EXECUTING PLANNING EXHAUSTION ANALYSIS")
        print("=" * 60)
        
        for cycle in range(1, max_cycles + 1):
            print(f"\n📋 PLANNING CYCLE {cycle}")
            print("-" * 30)
            
            # Generate planning cycle
            planning_cycle = self.generate_planning_cycle(cycle)
            self.planning_cycles.append(planning_cycle)
            self.effectiveness_curve.append(planning_cycle['effectiveness'])
            
            # Display cycle results
            print(f"   Planning Depth: {planning_cycle['planning_depth']}")
            print(f"   Time Spent: {planning_cycle['time_spent']}s")
            print(f"   New Insights: {planning_cycle['new_insights']}")
            print(f"   Complexity Added: {planning_cycle['complexity_added']}")
            print(f"   Effectiveness: {planning_cycle['effectiveness']}")
            
            # Check for diminishing returns
            if cycle >= 6:  # Need enough data points
                if self.detect_diminishing_returns(self.effectiveness_curve):
                    print(f"   ⚠️ DIMINISHING RETURNS DETECTED!")
                    self.diminishing_returns_detected = True
                    self.optimal_planning_depth = cycle - 3  # Optimal was 3 cycles ago
                    break
            
            # Brief pause to simulate planning time
            time.sleep(0.1)
        
        # Calculate analysis results
        results = self.calculate_analysis_results()
        
        # Print final analysis
        self.print_analysis_results(results)
        
        return results
    
    def calculate_analysis_results(self) -> Dict:
        """Calculate comprehensive analysis results"""
        
        if not self.planning_cycles:
            return {'error': 'No planning cycles completed'}
        
        effectiveness_values = [cycle['effectiveness'] for cycle in self.planning_cycles]
        time_values = [cycle['time_spent'] for cycle in self.planning_cycles]
        insight_values = [cycle['new_insights'] for cycle in self.planning_cycles]
        
        # Find peak effectiveness
        peak_effectiveness = max(effectiveness_values)
        peak_cycle = effectiveness_values.index(peak_effectiveness) + 1
        
        # Calculate trends
        effectiveness_trend = "declining" if effectiveness_values[-1] < effectiveness_values[0] else "improving"
        
        # Total planning time
        total_planning_time = sum(time_values)
        
        # Total insights gained
        total_insights = sum(insight_values)
        
        results = {
            'analysis_id': self.analysis_id,
            'total_cycles': len(self.planning_cycles),
            'diminishing_returns_detected': self.diminishing_returns_detected,
            'optimal_planning_depth': self.optimal_planning_depth,
            'peak_effectiveness': peak_effectiveness,
            'peak_cycle': peak_cycle,
            'effectiveness_trend': effectiveness_trend,
            'total_planning_time': round(total_planning_time, 2),
            'total_insights_gained': total_insights,
            'final_effectiveness': effectiveness_values[-1],
            'effectiveness_curve': effectiveness_values,
            'planning_cycles': self.planning_cycles,
            'analysis_timestamp': datetime.now().isoformat()
        }
        
        return results
    
    def print_analysis_results(self, results: Dict):
        """Print comprehensive analysis results"""
        
        print("\n" + "=" * 60)
        print("📊 PLANNING EXHAUSTION ANALYSIS COMPLETE")
        print("=" * 60)
        
        print(f"   Analysis ID: {results['analysis_id']}")
        print(f"   Total Cycles: {results['total_cycles']}")
        print(f"   Diminishing Returns: {'DETECTED' if results['diminishing_returns_detected'] else 'NOT DETECTED'}")
        print(f"   Optimal Planning Depth: {results['optimal_planning_depth']} cycles")
        print(f"   Peak Effectiveness: {results['peak_effectiveness']} (Cycle {results['peak_cycle']})")
        print(f"   Effectiveness Trend: {results['effectiveness_trend']}")
        print(f"   Total Planning Time: {results['total_planning_time']}s")
        print(f"   Total Insights Gained: {results['total_insights_gained']}")
        print(f"   Final Effectiveness: {results['final_effectiveness']}")
        
        # Effectiveness curve visualization
        print("\n📈 EFFECTIVENESS CURVE:")
        print("-" * 30)
        for i, effectiveness in enumerate(results['effectiveness_curve'], 1):
            bar_length = int(effectiveness * 20)  # Scale to 20 chars
            bar = "█" * bar_length + "░" * (20 - bar_length)
            print(f"   Cycle {i:2d}: {bar} {effectiveness:.3f}")
        
        # Recommendations
        print("\n💡 PLANNING OPTIMIZATION RECOMMENDATIONS:")
        print("-" * 45)
        
        if results['diminishing_returns_detected']:
            print(f"   ✅ STOP PLANNING at cycle {results['optimal_planning_depth']}")
            print(f"   📊 Peak effectiveness was {results['peak_effectiveness']:.3f} at cycle {results['peak_cycle']}")
            print(f"   ⚠️ Additional planning beyond cycle {results['optimal_planning_depth']} reduces effectiveness")
        else:
            print(f"   🔄 Continue planning - no diminishing returns detected yet")
            print(f"   📈 Effectiveness trend: {results['effectiveness_trend']}")
        
        # Planning efficiency analysis
        if results['total_planning_time'] > 0:
            insights_per_second = results['total_insights_gained'] / results['total_planning_time']
            print(f"   📊 Planning efficiency: {insights_per_second:.2f} insights/second")
        
        print(f"\n🎯 PLANNING EXHAUSTION POINT: {results['optimal_planning_depth']} cycles")
        print("   All plans are useless beyond this point!")

def main():
    """Main planning exhaustion analysis"""
    analyzer = PlanningExhaustionAnalyzer()
    results = analyzer.run_planning_exhaustion_analysis()
    
    # Save analysis results
    results_file = f"planning_exhaustion_{analyzer.analysis_id}.json"
    with open(results_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\n📋 Analysis results saved: {results_file}")
    
    return results

if __name__ == "__main__":
    main()
