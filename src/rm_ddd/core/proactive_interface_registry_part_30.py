from datetime import datetime
from typing import Dict, List, Any

    def calculate_name_similarity(self, name1: str, name2: str) -> float:
        """Calculate similarity between two interface names"""
        # Simple similarity based on common words
        words1 = set(name1.lower().split('_'))
        words2 = set(name2.lower().split('_'))
        
        if not words1 or not words2:
            return 0.0
        
        intersection = words1.intersection(words2)
        union = words1.union(words2)
        
        return len(intersection) / len(union) if union else 0.0
    