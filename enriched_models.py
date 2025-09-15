#!/usr/bin/env python3
"""
Enriched Models
===============

Derives insights, patterns, and enriched models from collected browser
and navigation session data.
"""

import json
import time
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from collections import defaultdict, Counter
import statistics


@dataclass
class UserBehaviorPattern:
    """Patterns in user behavior"""
    pattern_type: str  # "navigation_preference", "form_completion_style", etc.
    frequency: int
    confidence: float
    examples: List[Dict[str, Any]]
    insights: List[str]


@dataclass
class SiteInteractionModel:
    """Model of how users interact with a specific site"""
    site_domain: str
    total_sessions: int
    common_navigation_paths: List[Dict[str, Any]]
    form_completion_patterns: Dict[str, Any]
    error_patterns: List[Dict[str, Any]]
    performance_metrics: Dict[str, float]
    user_preferences: Dict[str, Any]


@dataclass
class FormOptimizationRecommendation:
    """Recommendations for form optimization"""
    form_id: str
    recommendation_type: str
    current_issue: str
    suggested_improvement: str
    expected_benefit: str
    confidence: float


class DataEnrichmentEngine:
    """Engine for deriving enriched models from raw data"""
    
    def __init__(self):
        self.session_data: List[Dict[str, Any]] = []
        self.telemetry_data: List[Dict[str, Any]] = []
        self.enriched_models: Dict[str, Any] = {}
    
    def load_session_data(self, session_files: List[str]):
        """Load session data from files"""
        for file_path in session_files:
            try:
                with open(file_path, 'r') as f:
                    data = json.load(f)
                    self.session_data.append(data)
            except Exception as e:
                print(f"⚠️  Error loading {file_path}: {e}")
    
    def load_telemetry_data(self, telemetry_files: List[str]):
        """Load telemetry data from files"""
        for file_path in telemetry_files:
            try:
                with open(file_path, 'r') as f:
                    for line in f:
                        data = json.loads(line.strip())
                        self.telemetry_data.append(data)
            except Exception as e:
                print(f"⚠️  Error loading {file_path}: {e}")
    
    def analyze_navigation_patterns(self) -> List[UserBehaviorPattern]:
        """Analyze navigation patterns across sessions"""
        patterns = []
        
        # Analyze common navigation sequences
        navigation_sequences = defaultdict(int)
        for session in self.session_data:
            if 'session' in session and 'navigation_actions' in session['session']:
                actions = session['session']['navigation_actions']
                for i in range(len(actions) - 1):
                    sequence = f"{actions[i]['action_type']} -> {actions[i+1]['action_type']}"
                    navigation_sequences[sequence] += 1
        
        # Find common patterns
        for sequence, frequency in navigation_sequences.items():
            if frequency >= 2:  # Appears in at least 2 sessions
                confidence = min(frequency / len(self.session_data), 1.0)
                patterns.append(UserBehaviorPattern(
                    pattern_type="navigation_sequence",
                    frequency=frequency,
                    confidence=confidence,
                    examples=[{"sequence": sequence, "frequency": frequency}],
                    insights=[f"Users commonly follow {sequence} pattern"]
                ))
        
        return patterns
    
    def analyze_form_completion_patterns(self) -> Dict[str, Any]:
        """Analyze how users complete forms"""
        form_stats = defaultdict(lambda: {
            'total_attempts': 0,
            'auto_fill_usage': 0,
            'manual_edits': 0,
            'completion_times': [],
            'abandonment_points': []
        })
        
        for session in self.session_data:
            if 'session' in session:
                session_data = session['session']
                
                # Analyze active forms
                for form in session_data.get('active_forms', []):
                    form_id = form['form_id']
                    form_stats[form_id]['total_attempts'] += 1
                    form_stats[form_id]['auto_fill_usage'] += form.get('auto_fill_attempts', 0)
                    form_stats[form_id]['manual_edits'] += form.get('manual_edits', 0)
                
                # Analyze completed forms
                for form in session_data.get('completed_forms', []):
                    form_id = form['form_id']
                    form_stats[form_id]['total_attempts'] += 1
                    form_stats[form_id]['auto_fill_usage'] += form.get('auto_fill_attempts', 0)
                    form_stats[form_id]['manual_edits'] += form.get('manual_edits', 0)
        
        # Calculate insights
        insights = {}
        for form_id, stats in form_stats.items():
            auto_fill_rate = stats['auto_fill_usage'] / max(stats['total_attempts'], 1)
            manual_edit_rate = stats['manual_edits'] / max(stats['total_attempts'], 1)
            
            insights[form_id] = {
                'auto_fill_adoption': auto_fill_rate,
                'manual_intervention_rate': manual_edit_rate,
                'form_complexity': 'high' if manual_edit_rate > 0.5 else 'medium' if manual_edit_rate > 0.2 else 'low',
                'optimization_opportunity': auto_fill_rate < 0.8
            }
        
        return insights
    
    def analyze_performance_patterns(self) -> Dict[str, Any]:
        """Analyze performance patterns from telemetry data"""
        performance_metrics = {
            'page_load_times': [],
            'navigation_times': [],
            'form_completion_times': [],
            'error_rates': []
        }
        
        for telemetry in self.telemetry_data:
            if 'data' in telemetry:
                data = telemetry['data']
                
                # Collect load times
                if 'performanceMetrics' in data:
                    load_time = data['performanceMetrics'].get('loadTime')
                    if load_time:
                        performance_metrics['page_load_times'].append(load_time)
                
                # Collect element counts as complexity indicator
                element_count = data.get('totalElements', 0)
                if element_count > 0:
                    performance_metrics['page_complexity'] = performance_metrics.get('page_complexity', [])
                    performance_metrics['page_complexity'].append(element_count)
        
        # Calculate statistics
        stats = {}
        for metric, values in performance_metrics.items():
            if values:
                stats[metric] = {
                    'mean': statistics.mean(values),
                    'median': statistics.median(values),
                    'min': min(values),
                    'max': max(values),
                    'count': len(values)
                }
        
        return stats
    
    def generate_form_optimization_recommendations(self) -> List[FormOptimizationRecommendation]:
        """Generate recommendations for form optimization"""
        recommendations = []
        form_patterns = self.analyze_form_completion_patterns()
        
        for form_id, patterns in form_patterns.items():
            # Auto-fill adoption recommendations
            if patterns['auto_fill_adoption'] < 0.5:
                recommendations.append(FormOptimizationRecommendation(
                    form_id=form_id,
                    recommendation_type="auto_fill_improvement",
                    current_issue=f"Low auto-fill adoption ({patterns['auto_fill_adoption']:.1%})",
                    suggested_improvement="Improve field naming and labeling for better auto-fill recognition",
                    expected_benefit="Increase auto-fill usage and reduce manual input",
                    confidence=0.8
                ))
            
            # Manual intervention recommendations
            if patterns['manual_intervention_rate'] > 0.3:
                recommendations.append(FormOptimizationRecommendation(
                    form_id=form_id,
                    recommendation_type="form_simplification",
                    current_issue=f"High manual intervention rate ({patterns['manual_intervention_rate']:.1%})",
                    suggested_improvement="Simplify form fields and improve validation",
                    expected_benefit="Reduce user friction and completion time",
                    confidence=0.7
                ))
        
        return recommendations
    
    def create_site_interaction_model(self, site_domain: str) -> SiteInteractionModel:
        """Create a comprehensive site interaction model"""
        # Filter data for specific site
        site_sessions = [s for s in self.session_data 
                        if s.get('session', {}).get('site_domain') == site_domain]
        
        # Analyze patterns
        navigation_patterns = self.analyze_navigation_patterns()
        form_patterns = self.analyze_form_completion_patterns()
        performance_patterns = self.analyze_performance_patterns()
        
        # Extract common navigation paths
        common_paths = []
        path_counts = defaultdict(int)
        
        for session in site_sessions:
            if 'session' in session and 'page_history' in session['session']:
                path = ' -> '.join(session['session']['page_history'])
                path_counts[path] += 1
        
        for path, count in path_counts.items():
            if count >= 2:
                common_paths.append({
                    'path': path,
                    'frequency': count,
                    'percentage': (count / len(site_sessions)) * 100
                })
        
        # Sort by frequency
        common_paths.sort(key=lambda x: x['frequency'], reverse=True)
        
        return SiteInteractionModel(
            site_domain=site_domain,
            total_sessions=len(site_sessions),
            common_navigation_paths=common_paths[:10],  # Top 10
            form_completion_patterns=form_patterns,
            error_patterns=[],  # Could be expanded
            performance_metrics=performance_patterns,
            user_preferences={
                'preferred_navigation_style': self._infer_navigation_preference(navigation_patterns),
                'form_completion_style': self._infer_form_preference(form_patterns)
            }
        )
    
    def _infer_navigation_preference(self, patterns: List[UserBehaviorPattern]) -> str:
        """Infer user's navigation preference"""
        step_nav_count = sum(1 for p in patterns if 'step' in p.pattern_type.lower())
        form_nav_count = sum(1 for p in patterns if 'form' in p.pattern_type.lower())
        
        if step_nav_count > form_nav_count:
            return "step-by-step"
        elif form_nav_count > step_nav_count:
            return "form-focused"
        else:
            return "mixed"
    
    def _infer_form_preference(self, form_patterns: Dict[str, Any]) -> str:
        """Infer user's form completion preference"""
        total_auto_fill = sum(p.get('auto_fill_adoption', 0) for p in form_patterns.values())
        avg_auto_fill = total_auto_fill / max(len(form_patterns), 1)
        
        if avg_auto_fill > 0.7:
            return "auto-fill_preferred"
        elif avg_auto_fill > 0.3:
            return "mixed_approach"
        else:
            return "manual_entry_preferred"
    
    def generate_comprehensive_report(self, site_domain: str = "devpost.com") -> Dict[str, Any]:
        """Generate a comprehensive analysis report"""
        site_model = self.create_site_interaction_model(site_domain)
        navigation_patterns = self.analyze_navigation_patterns()
        form_recommendations = self.generate_form_optimization_recommendations()
        
        return {
            "report_metadata": {
                "generated_at": datetime.now().isoformat(),
                "site_domain": site_domain,
                "total_sessions_analyzed": len(self.session_data),
                "total_telemetry_points": len(self.telemetry_data)
            },
            "site_interaction_model": asdict(site_model),
            "user_behavior_patterns": [asdict(p) for p in navigation_patterns],
            "optimization_recommendations": [asdict(r) for r in form_recommendations],
            "key_insights": self._generate_key_insights(site_model, navigation_patterns, form_recommendations)
        }
    
    def _generate_key_insights(self, site_model: SiteInteractionModel, 
                             patterns: List[UserBehaviorPattern],
                             recommendations: List[FormOptimizationRecommendation]) -> List[str]:
        """Generate key insights from analysis"""
        insights = []
        
        # Navigation insights
        if site_model.common_navigation_paths:
            most_common_path = site_model.common_navigation_paths[0]
            insights.append(f"Most common user path: {most_common_path['path']} "
                          f"({most_common_path['percentage']:.1f}% of sessions)")
        
        # Form insights
        high_intervention_forms = [r for r in recommendations 
                                 if r.recommendation_type == "form_simplification"]
        if high_intervention_forms:
            insights.append(f"{len(high_intervention_forms)} forms need simplification "
                          f"to reduce user friction")
        
        # Performance insights
        if 'page_load_times' in site_model.performance_metrics:
            avg_load_time = site_model.performance_metrics['page_load_times']['mean']
            insights.append(f"Average page load time: {avg_load_time:.2f}ms")
        
        # Auto-fill insights
        low_auto_fill_forms = [r for r in recommendations 
                              if r.recommendation_type == "auto_fill_improvement"]
        if low_auto_fill_forms:
            insights.append(f"{len(low_auto_fill_forms)} forms could benefit from "
                          f"improved auto-fill recognition")
        
        return insights


def create_enrichment_engine() -> DataEnrichmentEngine:
    """Create a new data enrichment engine"""
    return DataEnrichmentEngine()


if __name__ == "__main__":
    # Test the enrichment engine
    engine = create_enrichment_engine()
    
    # Simulate loading some data
    print("🔍 Testing data enrichment engine...")
    
    # Generate a sample report
    report = engine.generate_comprehensive_report("devpost.com")
    
    print("📊 Sample Analysis Report:")
    print(json.dumps(report, indent=2))
