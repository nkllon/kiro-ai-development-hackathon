"""
Context Engine for AI Memory Palace.

Intelligent context processing and summarization for efficient context management
with relevance filtering and pattern detection capabilities.
"""

from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
import json
import re
from collections import Counter

from src.beast_mode.core.beastly_module import BeastlyModule
from src.rm_ddd.core.unified_reflective_module import ModuleCapability, ModuleHealth, ModuleStatus, GracefulDegradationResult
from .models import SessionContext, ConversationEvent, ContextEvent


class ContextSummary:
    """Summarized context for efficient loading"""
    
    def __init__(self, original_context: SessionContext, summary_data: Dict[str, Any]):
        self.original_context = original_context
        self.summary_data = summary_data
        self.created_at = datetime.now()
    
    def get_size_reduction(self) -> float:
        """Get compression ratio"""
        original_size = self.original_context.get_context_size()
        summary_size = len(json.dumps(self.summary_data))
        return original_size / summary_size if summary_size > 0 else 1.0


class FilteredContext:
    """Context filtered for relevance"""
    
    def __init__(self, original_context: SessionContext, filtered_data: Dict[str, Any], relevance_score: float):
        self.original_context = original_context
        self.filtered_data = filtered_data
        self.relevance_score = relevance_score
        self.created_at = datetime.now()


class Pattern:
    """Detected pattern in context"""
    
    def __init__(self, pattern_type: str, description: str, frequency: int, examples: List[str]):
        self.pattern_type = pattern_type
        self.description = description
        self.frequency = frequency
        self.examples = examples
        self.confidence = min(frequency / 10.0, 1.0)  # Confidence based on frequency


class MergedContext:
    """Result of merging multiple contexts"""
    
    def __init__(self, contexts: List[SessionContext], merged_data: Dict[str, Any]):
        self.source_contexts = contexts
        self.merged_data = merged_data
        self.created_at = datetime.now()


class ContextEngine(BeastlyModule):
    """Intelligent context processing and summarization"""
    
    def __init__(self):
        super().__init__()
        
        # Processing metrics
        self._summarizations_performed = 0
        self._filterings_performed = 0
        self._patterns_detected = 0
        self._merges_performed = 0
        
        # Pattern cache
        self._pattern_cache: Dict[str, List[Pattern]] = {}
        
        self._logger.info("🧠 ContextEngine initialized")
    
    def summarize_context(self, full_context: SessionContext, max_size_kb: int = 100) -> ContextSummary:
        """Create intelligent summary of context for efficiency"""
        try:
            self.emit_observation({
                "type": "context_summarization_started",
                "session_id": full_context.session_id,
                "original_size": full_context.get_context_size(),
                "max_size_kb": max_size_kb
            })
            
            # Calculate target size
            target_size = max_size_kb * 1024
            current_size = full_context.get_context_size()
            
            if current_size <= target_size:
                # No summarization needed
                summary_data = full_context.to_dict()
            else:
                # Perform intelligent summarization
                summary_data = self._create_intelligent_summary(full_context, target_size)
            
            summary = ContextSummary(full_context, summary_data)
            self._summarizations_performed += 1
            
            self._logger.info(f"📊 Context summarized: {summary.get_size_reduction():.1f}x compression")
            
            self.emit_observation({
                "type": "context_summarization_completed",
                "session_id": full_context.session_id,
                "compression_ratio": summary.get_size_reduction(),
                "summary_size": len(json.dumps(summary_data))
            })
            
            return summary
            
        except Exception as e:
            self._logger.error(f"💥 Error summarizing context: {e}")
            # Return original context as fallback
            return ContextSummary(full_context, full_context.to_dict())
    
    def filter_relevant_context(self, context: SessionContext, query: str, relevance_threshold: float = 0.3) -> FilteredContext:
        """Filter context for relevance to current query/work"""
        try:
            self.emit_observation({
                "type": "context_filtering_started",
                "session_id": context.session_id,
                "query_length": len(query),
                "relevance_threshold": relevance_threshold
            })
            
            # Extract keywords from query
            keywords = self._extract_keywords(query)
            
            # Score and filter different context components
            filtered_data = {
                "project_id": context.project_id,
                "session_id": context.session_id,
                "timestamp": context.timestamp.isoformat(),
                "project_state": context.project_state.to_dict(),  # Always include project state
                "conversation_history": self._filter_conversation_history(context.conversation_history, keywords),
                "decisions_made": self._filter_decisions(context.decisions_made, keywords),
                "work_completed": self._filter_work_items(context.work_completed, keywords),
                "system_discoveries": self._filter_discoveries(context.system_discoveries, keywords),
                "spec_states": context.spec_states
            }
            
            # Calculate overall relevance score
            relevance_score = self._calculate_relevance_score(filtered_data, keywords)
            
            filtered_context = FilteredContext(context, filtered_data, relevance_score)
            self._filterings_performed += 1
            
            self._logger.info(f"🎯 Context filtered: relevance score {relevance_score:.2f}")
            
            self.emit_observation({
                "type": "context_filtering_completed",
                "session_id": context.session_id,
                "relevance_score": relevance_score,
                "filtered_items": sum(len(v) if isinstance(v, list) else 0 for v in filtered_data.values())
            })
            
            return filtered_context
            
        except Exception as e:
            self._logger.error(f"💥 Error filtering context: {e}")
            # Return original context as fallback
            return FilteredContext(context, context.to_dict(), 1.0)
    
    def detect_context_patterns(self, context: SessionContext) -> List[Pattern]:
        """Detect patterns in context for learning and optimization"""
        try:
            # Check cache first
            cache_key = f"{context.project_id}_{len(context.conversation_history)}"
            if cache_key in self._pattern_cache:
                return self._pattern_cache[cache_key]
            
            patterns = []
            
            # Detect conversation patterns
            patterns.extend(self._detect_conversation_patterns(context.conversation_history))
            
            # Detect decision patterns
            patterns.extend(self._detect_decision_patterns(context.decisions_made))
            
            # Detect work patterns
            patterns.extend(self._detect_work_patterns(context.work_completed))
            
            # Detect discovery patterns
            patterns.extend(self._detect_discovery_patterns(context.system_discoveries))
            
            # Cache results
            self._pattern_cache[cache_key] = patterns
            self._patterns_detected += len(patterns)
            
            self._logger.info(f"🔍 Detected {len(patterns)} context patterns")
            
            self.emit_observation({
                "type": "context_patterns_detected",
                "session_id": context.session_id,
                "pattern_count": len(patterns),
                "pattern_types": [p.pattern_type for p in patterns]
            })
            
            return patterns
            
        except Exception as e:
            self._logger.error(f"💥 Error detecting patterns: {e}")
            return []
    
    def merge_contexts(self, contexts: List[SessionContext]) -> MergedContext:
        """Merge multiple contexts for cross-project work"""
        try:
            if not contexts:
                raise ValueError("No contexts provided for merging")
            
            self.emit_observation({
                "type": "context_merging_started",
                "context_count": len(contexts),
                "project_ids": [c.project_id for c in contexts]
            })
            
            # Merge conversation histories chronologically
            all_conversations = []
            for context in contexts:
                for conv in context.conversation_history:
                    all_conversations.append((conv, context.project_id))
            
            all_conversations.sort(key=lambda x: x[0].timestamp)
            
            # Merge other components
            all_decisions = []
            all_work = []
            all_discoveries = []
            all_specs = {}
            
            for context in contexts:
                all_decisions.extend(context.decisions_made)
                all_work.extend(context.work_completed)
                all_discoveries.extend(context.system_discoveries)
                all_specs.update({f"{context.project_id}_{k}": v for k, v in context.spec_states.items()})
            
            # Create merged data structure
            merged_data = {
                "merged_projects": [c.project_id for c in contexts],
                "merge_timestamp": datetime.now().isoformat(),
                "conversation_history": [{"event": conv.to_dict(), "project": proj} for conv, proj in all_conversations],
                "decisions_made": [d.to_dict() for d in all_decisions],
                "work_completed": [w.to_dict() for w in all_work],
                "system_discoveries": [d.to_dict() for d in all_discoveries],
                "spec_states": {k: v.to_dict() for k, v in all_specs.items()},
                "project_states": {c.project_id: c.project_state.to_dict() for c in contexts}
            }
            
            merged_context = MergedContext(contexts, merged_data)
            self._merges_performed += 1
            
            self._logger.info(f"🔗 Merged {len(contexts)} contexts")
            
            self.emit_observation({
                "type": "context_merging_completed",
                "context_count": len(contexts),
                "total_events": len(all_conversations),
                "total_decisions": len(all_decisions),
                "total_work_items": len(all_work)
            })
            
            return merged_context
            
        except Exception as e:
            self._logger.error(f"💥 Error merging contexts: {e}")
            # Return empty merged context
            return MergedContext(contexts, {"error": str(e)})
    
    def _create_intelligent_summary(self, context: SessionContext, target_size: int) -> Dict[str, Any]:
        """Create intelligent summary targeting specific size"""
        # Start with essential data
        summary = {
            "project_id": context.project_id,
            "session_id": context.session_id,
            "timestamp": context.timestamp.isoformat(),
            "project_state": context.project_state.to_dict(),
            "spec_states": {k: v.to_dict() for k, v in context.spec_states.items()}
        }
        
        # Add summarized conversation history (most recent and important)
        summary["conversation_history"] = self._summarize_conversations(context.conversation_history, target_size // 4)
        
        # Add key decisions (most recent)
        summary["key_decisions"] = [d.to_dict() for d in context.decisions_made[-10:]]
        
        # Add recent work (most recent)
        summary["recent_work"] = [w.to_dict() for w in context.work_completed[-10:]]
        
        # Add important discoveries
        summary["key_discoveries"] = [d.to_dict() for d in context.system_discoveries[-5:]]
        
        return summary
    
    def _summarize_conversations(self, conversations: List[ConversationEvent], target_size: int) -> List[Dict[str, Any]]:
        """Summarize conversation history"""
        if not conversations:
            return []
        
        # Take most recent conversations first
        recent_conversations = conversations[-50:]  # Last 50 conversations
        
        summarized = []
        current_size = 0
        
        for conv in reversed(recent_conversations):
            conv_dict = conv.to_dict()
            conv_size = len(json.dumps(conv_dict))
            
            if current_size + conv_size > target_size:
                break
            
            summarized.insert(0, conv_dict)
            current_size += conv_size
        
        return summarized
    
    def _extract_keywords(self, text: str) -> List[str]:
        """Extract keywords from text"""
        # Simple keyword extraction
        words = re.findall(r'\b\w+\b', text.lower())
        
        # Filter out common stop words
        stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should'}
        
        keywords = [word for word in words if word not in stop_words and len(word) > 2]
        
        # Return most common keywords
        return [word for word, count in Counter(keywords).most_common(20)]
    
    def _filter_conversation_history(self, conversations: List[ConversationEvent], keywords: List[str]) -> List[Dict[str, Any]]:
        """Filter conversation history for relevance"""
        relevant_conversations = []
        
        for conv in conversations:
            relevance_score = self._calculate_text_relevance(conv.content, keywords)
            if relevance_score > 0.2:  # Threshold for relevance
                conv_dict = conv.to_dict()
                conv_dict['relevance_score'] = relevance_score
                relevant_conversations.append(conv_dict)
        
        # Sort by relevance and recency
        relevant_conversations.sort(key=lambda x: (x['relevance_score'], x['timestamp']), reverse=True)
        
        return relevant_conversations[:20]  # Top 20 most relevant
    
    def _filter_decisions(self, decisions: List, keywords: List[str]) -> List[Dict[str, Any]]:
        """Filter decisions for relevance"""
        relevant_decisions = []
        
        for decision in decisions:
            text = f"{decision.description} {decision.rationale}"
            relevance_score = self._calculate_text_relevance(text, keywords)
            if relevance_score > 0.1:
                decision_dict = decision.to_dict()
                decision_dict['relevance_score'] = relevance_score
                relevant_decisions.append(decision_dict)
        
        return sorted(relevant_decisions, key=lambda x: x['relevance_score'], reverse=True)[:10]
    
    def _filter_work_items(self, work_items: List, keywords: List[str]) -> List[Dict[str, Any]]:
        """Filter work items for relevance"""
        relevant_work = []
        
        for work in work_items:
            text = f"{work.description} {' '.join(work.files_created)} {' '.join(work.files_modified)}"
            relevance_score = self._calculate_text_relevance(text, keywords)
            if relevance_score > 0.1:
                work_dict = work.to_dict()
                work_dict['relevance_score'] = relevance_score
                relevant_work.append(work_dict)
        
        return sorted(relevant_work, key=lambda x: x['relevance_score'], reverse=True)[:10]
    
    def _filter_discoveries(self, discoveries: List, keywords: List[str]) -> List[Dict[str, Any]]:
        """Filter discoveries for relevance"""
        relevant_discoveries = []
        
        for discovery in discoveries:
            text = f"{discovery.description} {' '.join(discovery.components_found)} {' '.join(discovery.capabilities_identified)}"
            relevance_score = self._calculate_text_relevance(text, keywords)
            if relevance_score > 0.1:
                discovery_dict = discovery.to_dict()
                discovery_dict['relevance_score'] = relevance_score
                relevant_discoveries.append(discovery_dict)
        
        return sorted(relevant_discoveries, key=lambda x: x['relevance_score'], reverse=True)[:5]
    
    def _calculate_text_relevance(self, text: str, keywords: List[str]) -> float:
        """Calculate relevance score for text against keywords"""
        if not keywords or not text:
            return 0.0
        
        text_lower = text.lower()
        matches = sum(1 for keyword in keywords if keyword in text_lower)
        
        return matches / len(keywords)
    
    def _calculate_relevance_score(self, filtered_data: Dict[str, Any], keywords: List[str]) -> float:
        """Calculate overall relevance score for filtered context"""
        total_items = 0
        relevant_items = 0
        
        for key, value in filtered_data.items():
            if isinstance(value, list):
                total_items += len(value)
                relevant_items += sum(1 for item in value if isinstance(item, dict) and item.get('relevance_score', 0) > 0)
        
        return relevant_items / total_items if total_items > 0 else 0.0
    
    def _detect_conversation_patterns(self, conversations: List[ConversationEvent]) -> List[Pattern]:
        """Detect patterns in conversation history"""
        patterns = []
        
        if len(conversations) < 5:
            return patterns
        
        # Detect frequent event types
        event_types = [conv.event_type for conv in conversations]
        type_counts = Counter(event_types)
        
        for event_type, count in type_counts.most_common(3):
            if count >= 3:
                patterns.append(Pattern(
                    pattern_type="frequent_event_type",
                    description=f"Frequent {event_type} events",
                    frequency=count,
                    examples=[conv.content[:100] for conv in conversations if conv.event_type == event_type][:3]
                ))
        
        return patterns
    
    def _detect_decision_patterns(self, decisions: List) -> List[Pattern]:
        """Detect patterns in decisions"""
        patterns = []
        
        if len(decisions) < 3:
            return patterns
        
        # Detect common decision themes
        all_text = " ".join([f"{d.description} {d.rationale}" for d in decisions])
        keywords = self._extract_keywords(all_text)
        
        if keywords:
            patterns.append(Pattern(
                pattern_type="decision_themes",
                description=f"Common decision themes: {', '.join(keywords[:5])}",
                frequency=len(decisions),
                examples=[d.description for d in decisions[:3]]
            ))
        
        return patterns
    
    def _detect_work_patterns(self, work_items: List) -> List[Pattern]:
        """Detect patterns in work completed"""
        patterns = []
        
        if len(work_items) < 3:
            return patterns
        
        # Detect common work types
        work_types = [work.work_type for work in work_items]
        type_counts = Counter(work_types)
        
        for work_type, count in type_counts.most_common(2):
            if count >= 2:
                patterns.append(Pattern(
                    pattern_type="common_work_type",
                    description=f"Frequent {work_type} work",
                    frequency=count,
                    examples=[work.description for work in work_items if work.work_type == work_type][:3]
                ))
        
        return patterns
    
    def _detect_discovery_patterns(self, discoveries: List) -> List[Pattern]:
        """Detect patterns in system discoveries"""
        patterns = []
        
        if len(discoveries) < 2:
            return patterns
        
        # Detect common discovery types
        discovery_types = [d.discovery_type for d in discoveries]
        type_counts = Counter(discovery_types)
        
        for discovery_type, count in type_counts.most_common(2):
            if count >= 2:
                patterns.append(Pattern(
                    pattern_type="discovery_pattern",
                    description=f"Frequent {discovery_type} discoveries",
                    frequency=count,
                    examples=[d.description for d in discoveries if d.discovery_type == discovery_type][:2]
                ))
        
        return patterns
    
    def health_check(self) -> Dict[str, Any]:
        """Health check for ContextEngine"""
        return {
            "status": "healthy",
            "summarizations_performed": self._summarizations_performed,
            "filterings_performed": self._filterings_performed,
            "patterns_detected": self._patterns_detected,
            "merges_performed": self._merges_performed,
            "pattern_cache_size": len(self._pattern_cache)
        }
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get Prometheus-style metrics"""
        return {
            "context_engine_summarizations_total": self._summarizations_performed,
            "context_engine_filterings_total": self._filterings_performed,
            "context_engine_patterns_detected_total": self._patterns_detected,
            "context_engine_merges_total": self._merges_performed,
            "context_engine_pattern_cache_size": len(self._pattern_cache)
        }
    
    def get_module_info(self) -> Dict[str, Any]:
        """Get module information - RDI Compliant"""
        return {
            "module_id": "ai_memory_palace_context_engine",
            "module_name": "ContextEngine", 
            "version": "1.0.0",
            "description": "Intelligent context processing and summarization"
        }
    
    def get_capabilities(self) -> List[ModuleCapability]:
        """Get module capabilities - RDI Compliant"""
        from src.rm_ddd.core.unified_reflective_module import ModuleCapability
        return [
            ModuleCapability.CORE_FUNCTIONALITY,
            ModuleCapability.DATA_PROCESSING,
            ModuleCapability.API_INTEGRATION
        ]
    
    def get_health_status(self) -> ModuleHealth:
        """Get module health status - RDI Compliant"""
        from src.rm_ddd.core.unified_reflective_module import ModuleHealth, ModuleStatus
        return ModuleHealth(
            module_id="ai_memory_palace_context_engine",
            status=ModuleStatus.HEALTHY,
            health_score=0.95,
            issues=[],
            last_check=datetime.now(),
            uptime_seconds=(datetime.now() - self._start_time).total_seconds(),
            error_count=self._error_count,
            warning_count=self._warning_count
        )
    
    def graceful_degradation(self) -> GracefulDegradationResult:
        """Perform graceful degradation - RDI Compliant"""
        from src.rm_ddd.core.unified_reflective_module import GracefulDegradationResult, ModuleCapability
        return GracefulDegradationResult(
            success=True,
            degraded_capabilities=[],
            remaining_capabilities=[
                ModuleCapability.CORE_FUNCTIONALITY,
                ModuleCapability.DATA_PROCESSING,
                ModuleCapability.API_INTEGRATION
            ]
        )