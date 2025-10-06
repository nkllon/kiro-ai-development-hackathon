"""
AI Memory Palace Context Engine

Intelligent context processing and summarization with performance optimization.
"""

import logging
from typing import Dict, Any, List, Optional, Iterator
from datetime import datetime, timedelta

from src.rm_ddd.core.unified_reflective_module import ReflectiveModule
from ..models.context_models import SessionContext, ContextSummary, ContextEvent


class ContextEngine(ReflectiveModule):
    """Intelligent context processing and summarization."""
    
    def __init__(self):
        super().__init__()
        self.logger = logging.getLogger(__name__)
        self.cache = {}
        self.cache_max_size = 100  # MB
    
    def summarize_context(self, full_context: SessionContext) -> ContextSummary:
        """Summarize context for large datasets."""
        try:
            # Calculate context size
            context_size_mb = len(str(full_context)) / (1024 * 1024)
            
            # Extract recent decisions
            recent_decisions = []
            for decision in full_context.decisions_made[-5:]:
                if isinstance(decision, dict) and 'summary' in decision:
                    recent_decisions.append(decision['summary'])
            
            # Get active specs
            active_specs = []
            if full_context.project_state:
                active_specs = full_context.project_state.active_specs
            
            # Determine system health
            system_health = "unknown"
            if full_context.project_state:
                system_health = full_context.project_state.health_status
            
            return ContextSummary(
                project_id=full_context.project_id,
                last_session=full_context.timestamp,
                total_events=len(full_context.conversation_history),
                recent_decisions=recent_decisions,
                active_specs=active_specs,
                system_health=system_health,
                context_size_mb=context_size_mb
            )
            
        except Exception as e:
            self.logger.error(f"Failed to summarize context: {e}")
            # Return minimal summary
            return ContextSummary(
                project_id=full_context.project_id,
                last_session=full_context.timestamp,
                total_events=0,
                recent_decisions=[],
                active_specs=[],
                system_health="error",
                context_size_mb=0.0
            )
    
    def filter_relevant_context(self, context: SessionContext, query: str) -> SessionContext:
        """Filter context for relevance based on query."""
        try:
            # Simple relevance filtering based on keywords
            query_lower = query.lower()
            keywords = query_lower.split()
            
            # Filter conversation history
            relevant_history = []
            for item in context.conversation_history:
                if isinstance(item, dict):
                    item_text = str(item).lower()
                    if any(keyword in item_text for keyword in keywords):
                        relevant_history.append(item)
            
            # Filter decisions
            relevant_decisions = []
            for decision in context.decisions_made:
                if isinstance(decision, dict):
                    decision_text = str(decision).lower()
                    if any(keyword in decision_text for keyword in keywords):
                        relevant_decisions.append(decision)
            
            # Create filtered context
            filtered_context = SessionContext(
                project_id=context.project_id,
                session_id=context.session_id,
                timestamp=context.timestamp,
                conversation_history=relevant_history,
                project_state=context.project_state,  # Keep full project state
                decisions_made=relevant_decisions,
                work_completed=context.work_completed,  # Keep all work completed
                system_discoveries=context.system_discoveries,
                spec_states=context.spec_states
            )
            
            return filtered_context
            
        except Exception as e:
            self.logger.error(f"Failed to filter context: {e}")
            return context  # Return original on error
    
    def compress_old_data(self, context: SessionContext, threshold_mb: int = 10) -> SessionContext:
        """Compress old context data when size limits exceeded."""
        try:
            context_size_mb = len(str(context)) / (1024 * 1024)
            
            if context_size_mb <= threshold_mb:
                return context  # No compression needed
            
            # Compress conversation history - keep only recent items
            max_history_items = 100
            if len(context.conversation_history) > max_history_items:
                # Keep most recent items
                context.conversation_history = context.conversation_history[-max_history_items:]
            
            # Compress decisions - keep only recent and important ones
            max_decisions = 50
            if len(context.decisions_made) > max_decisions:
                context.decisions_made = context.decisions_made[-max_decisions:]
            
            # Compress discoveries - keep only recent ones
            max_discoveries = 20
            if len(context.system_discoveries) > max_discoveries:
                context.system_discoveries = context.system_discoveries[-max_discoveries:]
            
            self.logger.info(f"Compressed context from {context_size_mb:.2f}MB")
            
            return context
            
        except Exception as e:
            self.logger.error(f"Failed to compress context: {e}")
            return context
    
    def paginate_events(self, events: List[Dict[str, Any]], page_size: int = 100) -> Iterator[List[Dict[str, Any]]]:
        """Paginate large event collections."""
        for i in range(0, len(events), page_size):
            yield events[i:i + page_size]
    
    def validate_staleness(self, context: SessionContext) -> Dict[str, Any]:
        """Validate context freshness."""
        try:
            now = datetime.now()
            staleness_threshold = timedelta(hours=24)  # 24 hours
            
            is_stale = (now - context.timestamp) > staleness_threshold
            
            return {
                "is_stale": is_stale,
                "age_hours": (now - context.timestamp).total_seconds() / 3600,
                "threshold_hours": staleness_threshold.total_seconds() / 3600,
                "refresh_needed": is_stale
            }
            
        except Exception as e:
            self.logger.error(f"Failed to validate staleness: {e}")
            return {"is_stale": True, "refresh_needed": True}
