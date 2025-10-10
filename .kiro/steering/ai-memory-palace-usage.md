---
inclusion: always
---

# AI Memory Palace Usage - Persistent AI Context Management

## Core Principle

**"AI assistants must remember context across sessions. Use Beast Mode's AI Memory Palace to eliminate the '50 First Dates' problem and enable continuous development workflows."**

## The AI Memory Palace Pattern

### **ALWAYS Use Memory Palace for AI Context**

```python
from src.ai_memory_palace import MemoryPalace
from src.rm_ddd.core.unified_reflective_module import ReflectiveModule

class YourAISystem(ReflectiveModule):
    """AI system with persistent memory across sessions"""
    
    def __init__(self):
        super().__init__()
        self.memory = MemoryPalace()
    
    def remember_context(self, key: str, context: dict):
        """Store context for future AI sessions"""
        enriched_context = {
            **context,
            "timestamp": datetime.now().isoformat(),
            "session_id": self.generate_correlation_id(),
            "system_state": self.get_current_state()
        }
        self.memory.remember(key, enriched_context)
        
        self.log_info(f"Context stored", key=key, context_size=len(str(context)))
    
    def recall_context(self, key: str) -> dict:
        """Retrieve context from previous sessions"""
        context = self.memory.recall(key)
        
        if context:
            self.log_info(f"Context recalled", key=key, 
                         age_hours=(datetime.now() - datetime.fromisoformat(context["timestamp"])).total_seconds() / 3600)
        else:
            self.log_warning(f"No context found", key=key)
        
        return context or {}
```

### **Context Persistence Patterns**

```python
class AIContextManager(ReflectiveModule):
    """Systematic AI context management"""
    
    def __init__(self):
        super().__init__()
        self.memory = MemoryPalace()
    
    def process_user_request(self, request):
        """Process request with persistent context"""
        
        # 1. Load previous context
        user_context = self.memory.recall(f"user_{request.user_id}")
        project_context = self.memory.recall(f"project_{request.project_id}")
        session_context = self.memory.recall("current_session")
        
        # 2. Merge contexts for comprehensive understanding
        full_context = {
            "user_history": user_context,
            "project_state": project_context,
            "session_state": session_context,
            "current_request": request
        }
        
        # 3. Process with full context
        response = self.process_with_context(request, full_context)
        
        # 4. Update contexts for next session
        self.update_contexts(request, response, full_context)
        
        return response
    
    def update_contexts(self, request, response, full_context):
        """Update all relevant contexts"""
        
        # Update user context
        user_context = {
            **full_context.get("user_history", {}),
            "last_request": request,
            "last_response": response,
            "request_count": full_context.get("user_history", {}).get("request_count", 0) + 1,
            "preferences": self.extract_preferences(request, response),
            "updated_at": datetime.now().isoformat()
        }
        self.memory.remember(f"user_{request.user_id}", user_context)
        
        # Update project context
        project_context = {
            **full_context.get("project_state", {}),
            "recent_changes": self.extract_project_changes(request, response),
            "current_phase": self.determine_project_phase(request, response),
            "decisions_made": self.extract_decisions(request, response),
            "updated_at": datetime.now().isoformat()
        }
        self.memory.remember(f"project_{request.project_id}", project_context)
        
        # Update session context
        session_context = {
            "conversation_flow": self.build_conversation_flow(request, response),
            "active_tasks": self.extract_active_tasks(request, response),
            "context_switches": self.track_context_switches(request),
            "updated_at": datetime.now().isoformat()
        }
        self.memory.remember("current_session", session_context)
```

## Memory Optimization Patterns

### **Intelligent Context Compression**

```python
class ContextOptimizer:
    """Optimize memory storage for AI contexts"""
    
    def compress_context(self, context: dict) -> dict:
        """Compress context while preserving essential information"""
        
        # 1. Extract key decisions and outcomes
        key_decisions = self.extract_key_decisions(context)
        
        # 2. Summarize repetitive information
        summarized_history = self.summarize_history(context.get("history", []))
        
        # 3. Preserve recent high-value information
        recent_context = self.filter_recent_context(context, days=7)
        
        # 4. Compress large data structures
        compressed_data = self.compress_large_structures(context)
        
        return {
            "key_decisions": key_decisions,
            "summarized_history": summarized_history,
            "recent_context": recent_context,
            "compressed_data": compressed_data,
            "compression_metadata": {
                "original_size": len(str(context)),
                "compressed_size": len(str(compressed_data)),
                "compression_ratio": self.calculate_compression_ratio(context, compressed_data),
                "compressed_at": datetime.now().isoformat()
            }
        }
    
    def decompress_context(self, compressed_context: dict) -> dict:
        """Decompress context for AI consumption"""
        
        # Reconstruct full context from compressed representation
        return {
            **compressed_context["key_decisions"],
            **compressed_context["recent_context"],
            "history_summary": compressed_context["summarized_history"],
            "metadata": compressed_context["compression_metadata"]
        }
```

### **Context Lifecycle Management**

```python
class ContextLifecycleManager(ReflectiveModule):
    """Manage context lifecycle and cleanup"""
    
    def __init__(self):
        super().__init__()
        self.memory = MemoryPalace()
        self.optimizer = ContextOptimizer()
    
    def cleanup_stale_contexts(self):
        """Clean up old and unused contexts"""
        
        all_contexts = self.memory.list_all_contexts()
        
        for context_key in all_contexts:
            context = self.memory.recall(context_key)
            
            # Check if context is stale
            if self.is_context_stale(context):
                if self.is_context_valuable(context):
                    # Compress valuable but old contexts
                    compressed = self.optimizer.compress_context(context)
                    self.memory.remember(f"{context_key}_compressed", compressed)
                    self.memory.forget(context_key)
                    
                    self.log_info(f"Context compressed", key=context_key)
                else:
                    # Remove low-value stale contexts
                    self.memory.forget(context_key)
                    self.log_info(f"Context removed", key=context_key)
    
    def is_context_stale(self, context: dict) -> bool:
        """Determine if context is stale"""
        if not context or "updated_at" not in context:
            return True
        
        last_update = datetime.fromisoformat(context["updated_at"])
        age_days = (datetime.now() - last_update).days
        
        return age_days > 30  # Contexts older than 30 days are stale
    
    def is_context_valuable(self, context: dict) -> bool:
        """Determine if context has long-term value"""
        
        # High-value indicators
        value_indicators = [
            len(context.get("key_decisions", [])) > 5,  # Many decisions made
            context.get("request_count", 0) > 10,       # Frequently accessed
            "important" in str(context).lower(),        # Marked as important
            len(context.get("project_state", {})) > 0   # Has project state
        ]
        
        return any(value_indicators)
```

## AI Assistant Integration Patterns

### **Cross-Session Continuity**

```python
class AIAssistantWithMemory(ReflectiveModule):
    """AI assistant with cross-session memory"""
    
    def __init__(self, assistant_id: str):
        super().__init__()
        self.assistant_id = assistant_id
        self.memory = MemoryPalace()
        self.session_id = self.generate_correlation_id()
    
    def start_session(self, user_id: str, project_id: str = None):
        """Start new session with context from previous sessions"""
        
        # Load assistant's memory of this user
        user_memory = self.memory.recall(f"assistant_{self.assistant_id}_user_{user_id}")
        
        # Load project context if specified
        project_memory = {}
        if project_id:
            project_memory = self.memory.recall(f"project_{project_id}")
        
        # Create session context
        session_context = {
            "session_id": self.session_id,
            "user_id": user_id,
            "project_id": project_id,
            "started_at": datetime.now().isoformat(),
            "user_memory": user_memory,
            "project_memory": project_memory,
            "conversation_history": []
        }
        
        self.memory.remember(f"session_{self.session_id}", session_context)
        
        # Generate contextual greeting
        greeting = self.generate_contextual_greeting(user_memory, project_memory)
        
        self.log_info(f"Session started", 
                     user_id=user_id, project_id=project_id, 
                     has_user_memory=bool(user_memory),
                     has_project_memory=bool(project_memory))
        
        return greeting
    
    def generate_contextual_greeting(self, user_memory: dict, project_memory: dict) -> str:
        """Generate greeting based on previous context"""
        
        if not user_memory:
            return "Hello! I'm ready to help you with your Beast Mode development."
        
        last_interaction = user_memory.get("last_interaction")
        if last_interaction:
            last_task = last_interaction.get("task", "development")
            return f"Welcome back! I remember we were working on {last_task}. How can I continue helping you?"
        
        if project_memory:
            project_phase = project_memory.get("current_phase", "development")
            return f"Hello! I see we're in the {project_phase} phase of your project. What would you like to work on?"
        
        return "Hello! I remember our previous conversations. How can I help you today?"
    
    def process_message(self, message: str, context: dict = None):
        """Process message with full context awareness"""
        
        # Get current session context
        session_context = self.memory.recall(f"session_{self.session_id}")
        
        # Add message to conversation history
        session_context["conversation_history"].append({
            "timestamp": datetime.now().isoformat(),
            "message": message,
            "context": context or {}
        })
        
        # Process with full context
        response = self.generate_response(message, session_context, context)
        
        # Add response to conversation history
        session_context["conversation_history"].append({
            "timestamp": datetime.now().isoformat(),
            "response": response,
            "assistant_id": self.assistant_id
        })
        
        # Update session context
        self.memory.remember(f"session_{self.session_id}", session_context)
        
        return response
    
    def end_session(self):
        """End session and update long-term memory"""
        
        session_context = self.memory.recall(f"session_{self.session_id}")
        
        if session_context:
            # Extract key insights from session
            session_insights = self.extract_session_insights(session_context)
            
            # Update user memory
            user_id = session_context["user_id"]
            user_memory = self.memory.recall(f"assistant_{self.assistant_id}_user_{user_id}") or {}
            
            updated_user_memory = {
                **user_memory,
                "last_interaction": {
                    "session_id": self.session_id,
                    "ended_at": datetime.now().isoformat(),
                    "insights": session_insights,
                    "message_count": len(session_context["conversation_history"])
                },
                "total_sessions": user_memory.get("total_sessions", 0) + 1,
                "preferences": self.update_user_preferences(user_memory, session_context)
            }
            
            self.memory.remember(f"assistant_{self.assistant_id}_user_{user_id}", updated_user_memory)
            
            # Update project memory if applicable
            project_id = session_context.get("project_id")
            if project_id:
                self.update_project_memory(project_id, session_insights)
            
            self.log_info(f"Session ended", 
                         session_id=self.session_id,
                         message_count=len(session_context["conversation_history"]),
                         insights_count=len(session_insights))
```

## Memory Palace Performance Optimization

### **Efficient Context Retrieval**

```python
class OptimizedMemoryPalace(MemoryPalace):
    """Performance-optimized Memory Palace"""
    
    def __init__(self):
        super().__init__()
        self.context_cache = {}
        self.cache_ttl = 300  # 5 minutes
    
    def recall_with_caching(self, key: str) -> dict:
        """Recall context with intelligent caching"""
        
        # Check cache first
        if key in self.context_cache:
            cached_entry = self.context_cache[key]
            if time.time() - cached_entry["cached_at"] < self.cache_ttl:
                self.record_metric("memory_cache_hits", 1)
                return cached_entry["context"]
        
        # Cache miss - retrieve from storage
        context = self.recall(key)
        
        # Cache the result
        self.context_cache[key] = {
            "context": context,
            "cached_at": time.time()
        }
        
        self.record_metric("memory_cache_misses", 1)
        return context
    
    def batch_recall(self, keys: list) -> dict:
        """Efficiently retrieve multiple contexts"""
        
        results = {}
        uncached_keys = []
        
        # Check cache for all keys
        for key in keys:
            if key in self.context_cache:
                cached_entry = self.context_cache[key]
                if time.time() - cached_entry["cached_at"] < self.cache_ttl:
                    results[key] = cached_entry["context"]
                else:
                    uncached_keys.append(key)
            else:
                uncached_keys.append(key)
        
        # Batch retrieve uncached contexts
        if uncached_keys:
            uncached_results = self.batch_recall_from_storage(uncached_keys)
            results.update(uncached_results)
            
            # Update cache
            for key, context in uncached_results.items():
                self.context_cache[key] = {
                    "context": context,
                    "cached_at": time.time()
                }
        
        return results
```

## Anti-Patterns - Memory Management Violations

### ❌ **No Context Persistence**
```python
# WRONG: AI forgets everything between sessions
class ForgetfulAI:
    def process_request(self, request):
        # No memory of previous interactions
        return self.process_without_context(request)
```

### ❌ **Unbounded Memory Growth**
```python
# WRONG: Memory grows without bounds
def store_everything(context):
    # Never clean up old contexts
    memory.remember(f"context_{time.time()}", context)
```

### ❌ **No Context Optimization**
```python
# WRONG: Store raw contexts without compression
def store_context(huge_context):
    memory.remember("context", huge_context)  # Wastes storage
```

## Success Metrics

### **Memory Performance**
- **Retrieval Time**: <100ms for context recall
- **Storage Efficiency**: >50% compression ratio
- **Cache Hit Rate**: >80% for frequently accessed contexts
- **Memory Usage**: <100MB for typical workloads

### **AI Continuity**
- **Context Retention**: 100% of important decisions preserved
- **Session Continuity**: Seamless handoff between sessions
- **User Recognition**: AI remembers user preferences and history
- **Project Awareness**: AI maintains project state across sessions

## The Meta-Principle

**"AI assistants must remember everything important across sessions. Use Beast Mode's AI Memory Palace to create continuous, context-aware AI experiences that eliminate the '50 First Dates' problem."**

AI Memory Palace enables:
- **Continuous Development**: AI picks up where it left off
- **Personalized Experience**: AI learns user preferences over time
- **Project Awareness**: AI maintains project context and decisions
- **Efficient Workflows**: No need to re-explain context every session

---

**This steering rule ensures AI assistants using Beast Mode have persistent memory and provide continuous, context-aware assistance across all development sessions.**