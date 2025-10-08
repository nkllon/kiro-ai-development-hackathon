"""
Request Processor

Handles preprocessing of consultation requests and context injection with performance safety.
Provides query optimization, Observatory context integration, and resource protection.
"""

import asyncio
import logging
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import hashlib
import re
from concurrent.futures import ThreadPoolExecutor, TimeoutError as FutureTimeoutError

from .models import (
    ConsultationQuery, ObservatoryContext, QueryPriority
)
from .observatory_context_provider import get_observatory_context
from .security_manager import SecurityContext, check_permission, ResourceType
from .feature_flags import feature_flags, FeatureFlag
from .circuit_breaker import with_circuit_breaker
from .exceptions import ProcessingError, ValidationError
from .health_checker import ComponentHealth

logger = logging.getLogger(__name__)


class ProcessingStage(str, Enum):
    """Request processing stages"""
    VALIDATION = "validation"
    PREPROCESSING = "preprocessing"
    CONTEXT_INJECTION = "context_injection"
    OPTIMIZATION = "optimization"
    FINALIZATION = "finalization"


class ContextInjectionMode(str, Enum):
    """Context injection modes"""
    FULL = "full"           # Complete Observatory context
    SUMMARY = "summary"     # Summarized context only
    MINIMAL = "minimal"     # Basic status only
    NONE = "none"          # No context injection


@dataclass
class ProcessingMetrics:
    """Metrics for request processing"""
    stage: ProcessingStage
    start_time: datetime
    end_time: Optional[datetime] = None
    duration_ms: Optional[float] = None
    tokens_before: Optional[int] = None
    tokens_after: Optional[int] = None
    context_size: Optional[int] = None
    error: Optional[str] = None
    
    def complete(self, tokens_after: Optional[int] = None, context_size: Optional[int] = None, error: Optional[str] = None):
        """Mark processing stage as complete"""
        self.end_time = datetime.utcnow()
        self.duration_ms = (self.end_time - self.start_time).total_seconds() * 1000
        self.tokens_after = tokens_after
        self.context_size = context_size
        self.error = error


@dataclass
class ProcessedRequest:
    """Processed consultation request with injected context"""
    original_query: ConsultationQuery
    processed_query_text: str
    injected_context: Optional[ObservatoryContext]
    context_injection_mode: ContextInjectionMode
    system_prompt: Optional[str]
    estimated_tokens: int
    processing_metrics: List[ProcessingMetrics]
    optimization_applied: List[str]
    warnings: List[str]
    processing_time_ms: float
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for logging/storage"""
        return {
            'query_id': self.original_query.query_id,
            'user_id': self.original_query.user_id,
            'original_length': len(self.original_query.query_text),
            'processed_length': len(self.processed_query_text),
            'context_injection_mode': self.context_injection_mode.value,
            'estimated_tokens': self.estimated_tokens,
            'processing_time_ms': self.processing_time_ms,
            'optimization_applied': self.optimization_applied,
            'warnings': self.warnings,
            'has_context': self.injected_context is not None,
            'context_size': self.injected_context.get_token_estimate() if self.injected_context else 0
        }


class RequestProcessor:
    """
    Processes consultation requests with Observatory context injection
    
    Features:
    - Query preprocessing and optimization
    - Observatory context injection with performance safety
    - Token estimation and optimization
    - Resource limits and timeout protection
    - Circuit breaker integration
    - Performance monitoring and metrics
    """
    
    def __init__(
        self,
        max_processing_time: float = 5.0,  # 5 seconds max
        max_context_tokens: int = 4000,
        max_query_tokens: int = 2000,
        context_timeout: float = 2.0,  # 2 seconds for context retrieval
        enable_optimization: bool = True,
        thread_pool_size: int = 4
    ):
        self.max_processing_time = max_processing_time
        self.max_context_tokens = max_context_tokens
        self.max_query_tokens = max_query_tokens
        self.context_timeout = context_timeout
        self.enable_optimization = enable_optimization
        
        # Thread pool for CPU-intensive operations
        self.thread_pool = ThreadPoolExecutor(max_workers=thread_pool_size)
        
        # Processing statistics
        self.stats = {
            'requests_processed': 0,
            'requests_failed': 0,
            'context_injections': 0,
            'context_timeouts': 0,
            'optimizations_applied': 0,
            'avg_processing_time_ms': 0.0,
            'avg_context_size': 0.0,
            'total_tokens_saved': 0
        }
        
        # Query optimization patterns
        self.optimization_patterns = {
            'remove_excessive_whitespace': re.compile(r'\s+'),
            'remove_duplicate_punctuation': re.compile(r'([.!?])\1+'),
            'normalize_quotes': re.compile(r'[""]'),
            'remove_excessive_newlines': re.compile(r'\n\s*\n\s*\n+')
        }
        
        # Context injection cache
        self.context_cache: Dict[str, Tuple[ObservatoryContext, datetime]] = {}
        self.cache_ttl = timedelta(minutes=2)  # Short TTL for fresh context
    
    async def initialize(self) -> None:
        """Initialize the request processor"""
        try:
            logger.info("Initializing Request Processor")
            
            # Check if request processing is enabled
            if not await feature_flags.is_enabled(FeatureFlag.REQUEST_PREPROCESSING):
                logger.info("Request preprocessing is disabled via feature flag")
                return
            
            logger.info("Request Processor initialized")
            
        except Exception as e:
            logger.error(f"Failed to initialize Request Processor: {e}")
            # Don't raise - should degrade gracefully
    
    @with_circuit_breaker('request_processing')
    async def process_request(
        self,
        query: ConsultationQuery,
        security_context: Optional[SecurityContext] = None,
        context_mode: ContextInjectionMode = ContextInjectionMode.FULL,
        force_optimization: bool = False
    ) -> ProcessedRequest:
        """Process consultation request with context injection and optimization"""
        start_time = datetime.utcnow()
        processing_metrics = []
        warnings = []
        optimization_applied = []
        
        try:
            self.stats['requests_processed'] += 1
            
            # Check if preprocessing is enabled
            if not await feature_flags.is_enabled(FeatureFlag.REQUEST_PREPROCESSING):
                # Return minimal processing
                return ProcessedRequest(
                    original_query=query,
                    processed_query_text=query.query_text,
                    injected_context=None,
                    context_injection_mode=ContextInjectionMode.NONE,
                    system_prompt=None,
                    estimated_tokens=self._estimate_tokens(query.query_text),
                    processing_metrics=[],
                    optimization_applied=[],
                    warnings=["Request preprocessing disabled"],
                    processing_time_ms=0.0
                )
            
            # Stage 1: Validation
            validation_metrics = ProcessingMetrics(
                stage=ProcessingStage.VALIDATION,
                start_time=datetime.utcnow(),
                tokens_before=self._estimate_tokens(query.query_text)
            )
            
            await self._validate_request(query, security_context)
            validation_metrics.complete()
            processing_metrics.append(validation_metrics)
            
            # Stage 2: Preprocessing
            preprocessing_metrics = ProcessingMetrics(
                stage=ProcessingStage.PREPROCESSING,
                start_time=datetime.utcnow(),
                tokens_before=self._estimate_tokens(query.query_text)
            )
            
            processed_text, preprocessing_optimizations = await self._preprocess_query(
                query.query_text, force_optimization
            )
            optimization_applied.extend(preprocessing_optimizations)
            
            preprocessing_metrics.complete(
                tokens_after=self._estimate_tokens(processed_text)
            )
            processing_metrics.append(preprocessing_metrics)
            
            # Stage 3: Context Injection
            context_metrics = ProcessingMetrics(
                stage=ProcessingStage.CONTEXT_INJECTION,
                start_time=datetime.utcnow()
            )
            
            injected_context, system_prompt = await self._inject_context(
                query, security_context, context_mode
            )
            
            context_size = injected_context.get_token_estimate() if injected_context else 0
            context_metrics.complete(context_size=context_size)
            processing_metrics.append(context_metrics)
            
            # Stage 4: Optimization
            optimization_metrics = ProcessingMetrics(
                stage=ProcessingStage.OPTIMIZATION,
                start_time=datetime.utcnow(),
                tokens_before=self._estimate_tokens(processed_text) + context_size
            )
            
            final_text, context_optimizations = await self._optimize_for_tokens(
                processed_text, injected_context, system_prompt
            )
            optimization_applied.extend(context_optimizations)
            
            final_tokens = self._estimate_tokens(final_text) + context_size
            optimization_metrics.complete(tokens_after=final_tokens)
            processing_metrics.append(optimization_metrics)
            
            # Stage 5: Finalization
            finalization_metrics = ProcessingMetrics(
                stage=ProcessingStage.FINALIZATION,
                start_time=datetime.utcnow()
            )
            
            # Final validation and warnings
            if final_tokens > self.max_context_tokens + self.max_query_tokens:
                warnings.append(f"Total tokens ({final_tokens}) exceed recommended limit")
            
            if context_size > self.max_context_tokens:
                warnings.append(f"Context size ({context_size}) exceeds limit")
            
            finalization_metrics.complete()
            processing_metrics.append(finalization_metrics)
            
            # Calculate total processing time
            processing_time = (datetime.utcnow() - start_time).total_seconds() * 1000
            
            # Update statistics
            self._update_stats(processing_time, context_size, len(optimization_applied))
            
            logger.info(f"Processed request {query.query_id}: {len(optimization_applied)} optimizations, "
                       f"{processing_time:.1f}ms, {final_tokens} tokens")
            
            return ProcessedRequest(
                original_query=query,
                processed_query_text=final_text,
                injected_context=injected_context,
                context_injection_mode=context_mode,
                system_prompt=system_prompt,
                estimated_tokens=final_tokens,
                processing_metrics=processing_metrics,
                optimization_applied=optimization_applied,
                warnings=warnings,
                processing_time_ms=processing_time
            )
            
        except Exception as e:
            self.stats['requests_failed'] += 1
            logger.error(f"Request processing failed for {query.query_id}: {e}")
            
            # Return safe fallback
            return ProcessedRequest(
                original_query=query,
                processed_query_text=query.query_text,
                injected_context=None,
                context_injection_mode=ContextInjectionMode.NONE,
                system_prompt=None,
                estimated_tokens=self._estimate_tokens(query.query_text),
                processing_metrics=processing_metrics,
                optimization_applied=[],
                warnings=[f"Processing failed: {str(e)}"],
                processing_time_ms=(datetime.utcnow() - start_time).total_seconds() * 1000
            )
    
    async def _validate_request(
        self,
        query: ConsultationQuery,
        security_context: Optional[SecurityContext]
    ) -> None:
        """Validate request for processing"""
        try:
            # Basic validation
            if not query.query_text or len(query.query_text.strip()) == 0:
                raise ValidationError("Query text cannot be empty")
            
            if len(query.query_text) > 50000:  # Generous limit for preprocessing
                raise ValidationError("Query text too long for processing")
            
            # Check permissions for context injection
            if security_context:
                has_permission = await check_permission(
                    security_context,
                    ResourceType.METRICS  # Need metrics access for context
                )
                if not has_permission:
                    logger.warning(f"User {query.user_id} lacks permission for full context injection")
            
        except Exception as e:
            logger.warning(f"Request validation failed: {e}")
            raise
    
    async def _preprocess_query(
        self,
        query_text: str,
        force_optimization: bool = False
    ) -> Tuple[str, List[str]]:
        """Preprocess query text with optimization"""
        try:
            if not self.enable_optimization and not force_optimization:
                return query_text, []
            
            optimizations_applied = []
            processed_text = query_text
            
            # Run preprocessing in thread pool for CPU-intensive operations
            def apply_optimizations(text: str) -> Tuple[str, List[str]]:
                opts = []
                result = text
                
                # Remove excessive whitespace
                original_len = len(result)
                result = self.optimization_patterns['remove_excessive_whitespace'].sub(' ', result)
                if len(result) < original_len:
                    opts.append('whitespace_normalization')
                
                # Remove duplicate punctuation
                original_len = len(result)
                result = self.optimization_patterns['remove_duplicate_punctuation'].sub(r'\1', result)
                if len(result) < original_len:
                    opts.append('punctuation_deduplication')
                
                # Normalize quotes
                result = self.optimization_patterns['normalize_quotes'].sub('"', result)
                
                # Remove excessive newlines
                original_len = len(result)
                result = self.optimization_patterns['remove_excessive_newlines'].sub('\n\n', result)
                if len(result) < original_len:
                    opts.append('newline_normalization')
                
                # Strip leading/trailing whitespace
                result = result.strip()
                
                return result, opts
            
            # Execute with timeout
            try:
                future = self.thread_pool.submit(apply_optimizations, processed_text)
                processed_text, optimizations_applied = await asyncio.wait_for(
                    asyncio.wrap_future(future),
                    timeout=1.0  # 1 second timeout for preprocessing
                )
            except asyncio.TimeoutError:
                logger.warning("Query preprocessing timed out, using original text")
                return query_text, ['preprocessing_timeout']
            
            return processed_text, optimizations_applied
            
        except Exception as e:
            logger.error(f"Query preprocessing failed: {e}")
            return query_text, ['preprocessing_error']
    
    async def _inject_context(
        self,
        query: ConsultationQuery,
        security_context: Optional[SecurityContext],
        context_mode: ContextInjectionMode
    ) -> Tuple[Optional[ObservatoryContext], Optional[str]]:
        """Inject Observatory context based on mode and permissions"""
        try:
            if context_mode == ContextInjectionMode.NONE:
                return None, None
            
            # Check cache first
            cache_key = f"{query.user_id}:{context_mode.value}"
            if cache_key in self.context_cache:
                cached_context, cached_time = self.context_cache[cache_key]
                if datetime.utcnow() - cached_time < self.cache_ttl:
                    return cached_context, self._create_system_prompt(cached_context, context_mode)
            
            # Retrieve context with timeout
            context = None
            try:
                context_future = asyncio.create_task(
                    self._get_observatory_context(query, security_context, context_mode)
                )
                context = await asyncio.wait_for(context_future, timeout=self.context_timeout)
                
                if context:
                    self.stats['context_injections'] += 1
                    # Cache the context
                    self.context_cache[cache_key] = (context, datetime.utcnow())
                    
            except asyncio.TimeoutError:
                self.stats['context_timeouts'] += 1
                logger.warning(f"Context injection timed out for {query.query_id}")
                context = None
            
            # Create system prompt
            system_prompt = self._create_system_prompt(context, context_mode) if context else None
            
            return context, system_prompt
            
        except Exception as e:
            logger.error(f"Context injection failed: {e}")
            return None, None
    
    async def _get_observatory_context(
        self,
        query: ConsultationQuery,
        security_context: Optional[SecurityContext],
        context_mode: ContextInjectionMode
    ) -> Optional[ObservatoryContext]:
        """Get Observatory context based on mode"""
        try:
            if not security_context:
                return None
            
            # Determine what context to include based on mode
            include_metrics = context_mode in [ContextInjectionMode.FULL, ContextInjectionMode.SUMMARY]
            include_alerts = context_mode in [ContextInjectionMode.FULL, ContextInjectionMode.SUMMARY]
            include_status = True  # Always include basic status
            
            context = await get_observatory_context(
                user_id=query.user_id,
                security_context=security_context,
                include_metrics=include_metrics,
                include_alerts=include_alerts,
                include_status=include_status
            )
            
            # Apply mode-specific filtering
            if context and context_mode == ContextInjectionMode.MINIMAL:
                # Keep only basic status information
                context.metrics_summary = {"status": "available"}
                context.recent_events = []
            elif context and context_mode == ContextInjectionMode.SUMMARY:
                # Limit recent events to most important
                context.recent_events = context.recent_events[:5] if context.recent_events else []
            
            return context
            
        except Exception as e:
            logger.warning(f"Failed to get Observatory context: {e}")
            return None
    
    def _create_system_prompt(
        self,
        context: Optional[ObservatoryContext],
        context_mode: ContextInjectionMode
    ) -> Optional[str]:
        """Create system prompt with Observatory context"""
        if not context:
            return None
        
        try:
            prompt_parts = [
                "You are an AI assistant helping with Observatory monitoring system analysis.",
                "Use the following current system context to provide accurate, relevant responses:"
            ]
            
            # Add system status
            if context.system_status:
                prompt_parts.append(f"System Status: {context.system_status}")
            
            # Add alerts information
            if context.active_alerts > 0:
                prompt_parts.append(f"Active Alerts: {context.active_alerts}")
            
            # Add metrics summary
            if context.metrics_summary and context_mode != ContextInjectionMode.MINIMAL:
                metrics_info = []
                for key, value in context.metrics_summary.items():
                    if key != "status":  # Already included above
                        metrics_info.append(f"{key}: {value}")
                if metrics_info:
                    prompt_parts.append(f"Metrics Summary: {', '.join(metrics_info)}")
            
            # Add recent events for full context
            if (context.recent_events and 
                context_mode == ContextInjectionMode.FULL and 
                len(context.recent_events) > 0):
                prompt_parts.append(f"Recent Events: {len(context.recent_events)} events in system log")
            
            # Add guidance
            prompt_parts.extend([
                "",
                "Guidelines:",
                "- Provide specific, actionable advice based on the current system state",
                "- Reference specific metrics or alerts when relevant",
                "- If the query is unrelated to monitoring, provide general assistance",
                "- Be concise but thorough in your responses"
            ])
            
            return "\n".join(prompt_parts)
            
        except Exception as e:
            logger.error(f"Failed to create system prompt: {e}")
            return None
    
    async def _optimize_for_tokens(
        self,
        query_text: str,
        context: Optional[ObservatoryContext],
        system_prompt: Optional[str]
    ) -> Tuple[str, List[str]]:
        """Optimize query and context for token efficiency"""
        try:
            optimizations = []
            result_text = query_text
            
            # Calculate current token usage
            query_tokens = self._estimate_tokens(result_text)
            context_tokens = context.get_token_estimate() if context else 0
            prompt_tokens = self._estimate_tokens(system_prompt) if system_prompt else 0
            total_tokens = query_tokens + context_tokens + prompt_tokens
            
            # If within limits, no optimization needed
            if total_tokens <= self.max_context_tokens + self.max_query_tokens:
                return result_text, optimizations
            
            # Apply token optimizations
            if query_tokens > self.max_query_tokens:
                # Truncate query if too long
                target_length = int(len(result_text) * (self.max_query_tokens / query_tokens))
                result_text = result_text[:target_length] + "..."
                optimizations.append('query_truncation')
                self.stats['total_tokens_saved'] += query_tokens - self._estimate_tokens(result_text)
            
            return result_text, optimizations
            
        except Exception as e:
            logger.error(f"Token optimization failed: {e}")
            return query_text, ['optimization_error']
    
    def _estimate_tokens(self, text: str) -> int:
        """Estimate token count for text"""
        if not text:
            return 0
        
        # Simple estimation: ~4 characters per token on average
        # This is a rough approximation - real tokenization would be more accurate
        return max(1, len(text) // 4)
    
    def _update_stats(self, processing_time: float, context_size: int, optimizations: int) -> None:
        """Update processing statistics"""
        try:
            # Update averages
            total_requests = self.stats['requests_processed']
            
            if total_requests > 1:
                current_avg_time = self.stats['avg_processing_time_ms']
                self.stats['avg_processing_time_ms'] = (
                    (current_avg_time * (total_requests - 1) + processing_time) / total_requests
                )
                
                current_avg_context = self.stats['avg_context_size']
                self.stats['avg_context_size'] = (
                    (current_avg_context * (total_requests - 1) + context_size) / total_requests
                )
            else:
                self.stats['avg_processing_time_ms'] = processing_time
                self.stats['avg_context_size'] = context_size
            
            self.stats['optimizations_applied'] += optimizations
            
        except Exception as e:
            logger.error(f"Failed to update stats: {e}")
    
    async def get_processing_stats(self) -> Dict[str, Any]:
        """Get current processing statistics"""
        try:
            return {
                'processing_stats': self.stats.copy(),
                'configuration': {
                    'max_processing_time': self.max_processing_time,
                    'max_context_tokens': self.max_context_tokens,
                    'max_query_tokens': self.max_query_tokens,
                    'context_timeout': self.context_timeout,
                    'enable_optimization': self.enable_optimization
                },
                'cache_stats': {
                    'cache_size': len(self.context_cache),
                    'cache_ttl_minutes': self.cache_ttl.total_seconds() / 60
                },
                'thread_pool_stats': {
                    'max_workers': self.thread_pool._max_workers,
                    'active_threads': len([t for t in self.thread_pool._threads if t.is_alive()])
                }
            }
            
        except Exception as e:
            logger.error(f"Failed to get processing stats: {e}")
            return {'error': str(e)}
    
    async def clear_context_cache(self) -> bool:
        """Clear the context cache"""
        try:
            self.context_cache.clear()
            logger.info("Context cache cleared")
            return True
            
        except Exception as e:
            logger.error(f"Failed to clear context cache: {e}")
            return False
    
    async def get_health_status(self) -> ComponentHealth:
        """Get processor health status"""
        try:
            # Check processing performance
            avg_time = self.stats['avg_processing_time_ms']
            success_rate = (
                self.stats['requests_processed'] / 
                max(1, self.stats['requests_processed'] + self.stats['requests_failed'])
            )
            
            # Determine health status
            if success_rate < 0.8:
                status = "critical"
                error_message = f"Low success rate: {success_rate:.1%}"
            elif avg_time > self.max_processing_time * 1000:
                status = "degraded"
                error_message = f"High processing time: {avg_time:.1f}ms"
            elif self.stats['context_timeouts'] > self.stats['context_injections'] * 0.2:
                status = "degraded"
                error_message = "High context timeout rate"
            else:
                status = "healthy"
                error_message = None
            
            return ComponentHealth(
                component="request_processor",
                status=status,
                response_time=avg_time,
                error_message=error_message,
                metadata={
                    'requests_processed': self.stats['requests_processed'],
                    'success_rate': success_rate,
                    'avg_context_size': self.stats['avg_context_size'],
                    'optimizations_applied': self.stats['optimizations_applied'],
                    'cache_size': len(self.context_cache)
                },
                last_check=datetime.utcnow()
            )
            
        except Exception as e:
            return ComponentHealth(
                component="request_processor",
                status="unhealthy",
                response_time=0.0,
                error_message=str(e),
                metadata={},
                last_check=datetime.utcnow()
            )
    
    def __del__(self):
        """Cleanup thread pool on destruction"""
        try:
            if hasattr(self, 'thread_pool'):
                self.thread_pool.shutdown(wait=False)
        except Exception:
            pass


# Global processor instance
_request_processor: Optional[RequestProcessor] = None


async def get_request_processor() -> RequestProcessor:
    """Get the global request processor instance"""
    global _request_processor
    
    if _request_processor is None:
        _request_processor = RequestProcessor()
        await _request_processor.initialize()
    
    return _request_processor


async def process_consultation_request(
    query: ConsultationQuery,
    security_context: Optional[SecurityContext] = None,
    context_mode: ContextInjectionMode = ContextInjectionMode.FULL,
    force_optimization: bool = False
) -> ProcessedRequest:
    """Process a consultation request (convenience function)"""
    processor = await get_request_processor()
    return await processor.process_request(query, security_context, context_mode, force_optimization)