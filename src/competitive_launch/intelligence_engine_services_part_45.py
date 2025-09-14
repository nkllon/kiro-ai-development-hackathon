from datetime import datetime
from typing import Dict, List, Any
from src.rm_ddd.core.health import ModuleHealth


    def _analyze_customer_feedback(self, feedback: List[CustomerFeedback]) -> Dict[str, Any]:
        """Analyze customer feedback for competitive insights."""
        return {'total_feedback': len(feedback), 'competitor_mentions': sum((len(f.mentioned_competitors) for f in feedback)), 'positive_sentiment': len([f for f in feedback if f.sentiment == 'positive']), 'competitive_insights': sum((len(f.competitive_insights) for f in feedback))}
