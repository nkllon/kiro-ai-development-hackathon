"""
Repository Pattern for AI Consultation Data Access

Provides safe data access patterns that don't interfere with existing
Observatory database operations.
"""

import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union
from uuid import uuid4
import logging

from sqlalchemy import text, select, insert, update, delete, func, and_, or_
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from sqlalchemy.orm import selectinload

from .database import (
    get_database_session, ConsultationQueryTable, ConsultationResultTable,
    DoctorStatusTable, QueuedQueryTable, BudgetStatusTable
)
from .models import (
    ConsultationQuery, ConsultationResult, DoctorStatus, 
    QueuedQuery, BudgetStatus, ProcessingMode, QueryPriority
)
from .exceptions import ConsultationError, ValidationError
from .circuit_breaker import with_circuit_breaker
from .feature_flags import feature_flags, FeatureFlag

logger = logging.getLogger(__name__)


class RepositoryError(ConsultationError):
    """Raised when repository operations encounter errors"""
    
    def __init__(self, message: str, operation: Optional[str] = None):
        super().__init__(
            message=message,
            error_code="REPOSITORY_ERROR",
            details={"operation": operation},
            retry_possible=True
        )


class ConsultationRepository:
    """Repository for consultation queries and results"""
    
    async def store_query(self, query: ConsultationQuery) -> str:
        """Store consultation query"""
        try:
            async with get_database_session() as session:
                # Convert Pydantic model to SQLAlchemy model
                db_query = ConsultationQueryTable(
                    query_id=query.query_id,
                    user_id=query.user_id,
                    query_text=query.query_text,
                    timestamp=query.timestamp,
                    context_snapshot=query.context_snapshot.dict() if query.context_snapshot else None,
                    email_notification=query.email_notification,
                    priority=query.priority.value,
                    processing_mode=query.processing_mode.value if query.processing_mode else None,
                    session_id=query.session_id
                )
                
                session.add(db_query)
                await session.commit()
                
                logger.debug(f"Stored query: {query.query_id}")
                return query.query_id
        
        except IntegrityError as e:
            logger.error(f"Query already exists: {query.query_id}")
            raise ValidationError(f"Query with ID {query.query_id} already exists")
        except Exception as e:
            logger.error(f"Failed to store query: {e}")
            raise RepositoryError(f"Failed to store query: {str(e)}", "store_query")
    
    async def get_query(self, query_id: str) -> Optional[ConsultationQuery]:
        """Get consultation query by ID"""
        try:
            async with get_database_session() as session:
                result = await session.execute(
                    select(ConsultationQueryTable).where(
                        ConsultationQueryTable.query_id == query_id
                    )
                )
                db_query = result.scalar_one_or_none()
                
                if not db_query:
                    return None
                
                # Convert SQLAlchemy model to Pydantic model
                return ConsultationQuery(
                    query_id=db_query.query_id,
                    user_id=db_query.user_id,
                    query_text=db_query.query_text,
                    timestamp=db_query.timestamp,
                    email_notification=db_query.email_notification,
                    priority=QueryPriority(db_query.priority),
                    processing_mode=ProcessingMode(db_query.processing_mode) if db_query.processing_mode else None,
                    session_id=db_query.session_id
                )
        
        except Exception as e:
            logger.error(f"Failed to get query {query_id}: {e}")
            raise RepositoryError(f"Failed to get query: {str(e)}", "get_query")
    
    async def store_result(self, result: ConsultationResult) -> str:
        """Store consultation result"""
        try:
            async with get_database_session() as session:
                # Convert Pydantic model to SQLAlchemy model
                db_result = ConsultationResultTable(
                    result_id=result.result_id,
                    query_id=result.query_id,
                    response=result.response,
                    processing_mode=result.processing_mode.value,
                    cost=result.cost,
                    tokens_used=result.tokens_used,
                    processing_time=result.processing_time,
                    timestamp=result.timestamp,
                    confidence_score=result.confidence_score,
                    error_message=result.error_message,
                    retry_count=result.retry_count
                )
                
                session.add(db_result)
                await session.commit()
                
                logger.debug(f"Stored result: {result.result_id}")
                return result.result_id
        
        except Exception as e:
            logger.error(f"Failed to store result: {e}")
            raise RepositoryError(f"Failed to store result: {str(e)}", "store_result")
    
    async def get_result(self, result_id: str) -> Optional[ConsultationResult]:
        """Get consultation result by ID"""
        try:
            async with get_database_session() as session:
                result = await session.execute(
                    select(ConsultationResultTable).where(
                        ConsultationResultTable.result_id == result_id
                    )
                )
                db_result = result.scalar_one_or_none()
                
                if not db_result:
                    return None
                
                # Get associated query
                query = await self.get_query(db_result.query_id)
                if not query:
                    logger.warning(f"Query not found for result: {result_id}")
                    return None
                
                # Convert SQLAlchemy model to Pydantic model
                return ConsultationResult(
                    result_id=db_result.result_id,
                    query_id=db_result.query_id,
                    query=query,
                    response=db_result.response,
                    processing_mode=ProcessingMode(db_result.processing_mode),
                    cost=db_result.cost,
                    tokens_used=db_result.tokens_used,
                    processing_time=db_result.processing_time,
                    timestamp=db_result.timestamp,
                    confidence_score=db_result.confidence_score,
                    error_message=db_result.error_message,
                    retry_count=db_result.retry_count
                )
        
        except Exception as e:
            logger.error(f"Failed to get result {result_id}: {e}")
            raise RepositoryError(f"Failed to get result: {str(e)}", "get_result")
    
    async def search_results(
        self, 
        user_id: str, 
        query_text: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        limit: int = 50
    ) -> List[ConsultationResult]:
        """Search consultation results"""
        try:
            async with get_database_session() as session:
                # Build query
                query = select(ConsultationResultTable).join(
                    ConsultationQueryTable,
                    ConsultationResultTable.query_id == ConsultationQueryTable.query_id
                ).where(
                    ConsultationQueryTable.user_id == user_id
                )
                
                # Add filters
                if query_text:
                    query = query.where(
                        ConsultationQueryTable.query_text.ilike(f"%{query_text}%")
                    )
                
                if start_date:
                    query = query.where(ConsultationResultTable.timestamp >= start_date)
                
                if end_date:
                    query = query.where(ConsultationResultTable.timestamp <= end_date)
                
                # Order by timestamp and limit
                query = query.order_by(ConsultationResultTable.timestamp.desc()).limit(limit)
                
                result = await session.execute(query)
                db_results = result.scalars().all()
                
                # Convert to Pydantic models
                results = []
                for db_result in db_results:
                    query_obj = await self.get_query(db_result.query_id)
                    if query_obj:
                        consultation_result = ConsultationResult(
                            result_id=db_result.result_id,
                            query_id=db_result.query_id,
                            query=query_obj,
                            response=db_result.response,
                            processing_mode=ProcessingMode(db_result.processing_mode),
                            cost=db_result.cost,
                            tokens_used=db_result.tokens_used,
                            processing_time=db_result.processing_time,
                            timestamp=db_result.timestamp,
                            confidence_score=db_result.confidence_score,
                            error_message=db_result.error_message,
                            retry_count=db_result.retry_count
                        )
                        results.append(consultation_result)
                
                return results
        
        except Exception as e:
            logger.error(f"Failed to search results: {e}")
            raise RepositoryError(f"Failed to search results: {str(e)}", "search_results")
    
    async def get_user_history(self, user_id: str, limit: int = 100) -> List[ConsultationResult]:
        """Get consultation history for user"""
        return await self.search_results(user_id=user_id, limit=limit)
    
    async def cleanup_old_results(self, days: int = 90) -> int:
        """Clean up old consultation results"""
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=days)
            
            async with get_database_session() as session:
                # Delete old results
                result = await session.execute(
                    delete(ConsultationResultTable).where(
                        ConsultationResultTable.timestamp < cutoff_date
                    )
                )
                deleted_results = result.rowcount
                
                # Delete orphaned queries
                result = await session.execute(
                    delete(ConsultationQueryTable).where(
                        and_(
                            ConsultationQueryTable.timestamp < cutoff_date,
                            ~ConsultationQueryTable.query_id.in_(
                                select(ConsultationResultTable.query_id)
                            )
                        )
                    )
                )
                deleted_queries = result.rowcount
                
                await session.commit()
                
                logger.info(f"Cleaned up {deleted_results} results and {deleted_queries} queries")
                return deleted_results + deleted_queries
        
        except Exception as e:
            logger.error(f"Failed to cleanup old results: {e}")
            raise RepositoryError(f"Failed to cleanup: {str(e)}", "cleanup_old_results")


class DoctorStatusRepository:
    """Repository for doctor status management"""
    
    async def get_status(self) -> Optional[DoctorStatus]:
        """Get current doctor status"""
        try:
            async with get_database_session() as session:
                result = await session.execute(
                    select(DoctorStatusTable).order_by(DoctorStatusTable.id.desc()).limit(1)
                )
                db_status = result.scalar_one_or_none()
                
                if not db_status:
                    return None
                
                return DoctorStatus(
                    is_available=db_status.is_available,
                    reason=db_status.reason,
                    cost_budget_remaining=db_status.cost_budget_remaining,
                    daily_usage=db_status.daily_usage,
                    monthly_usage=db_status.monthly_usage,
                    last_updated=db_status.last_updated,
                    next_budget_reset=db_status.next_budget_reset,
                    active_sessions=db_status.active_sessions,
                    queue_length=db_status.queue_length
                )
        
        except Exception as e:
            logger.error(f"Failed to get doctor status: {e}")
            raise RepositoryError(f"Failed to get status: {str(e)}", "get_status")
    
    async def update_status(self, status: DoctorStatus) -> None:
        """Update doctor status"""
        try:
            async with get_database_session() as session:
                # Update or insert status
                result = await session.execute(
                    select(DoctorStatusTable).limit(1)
                )
                existing = result.scalar_one_or_none()
                
                if existing:
                    # Update existing
                    await session.execute(
                        update(DoctorStatusTable).values(
                            is_available=status.is_available,
                            reason=status.reason,
                            cost_budget_remaining=status.cost_budget_remaining,
                            daily_usage=status.daily_usage,
                            monthly_usage=status.monthly_usage,
                            last_updated=status.last_updated,
                            next_budget_reset=status.next_budget_reset,
                            active_sessions=status.active_sessions,
                            queue_length=status.queue_length
                        )
                    )
                else:
                    # Insert new
                    db_status = DoctorStatusTable(
                        is_available=status.is_available,
                        reason=status.reason,
                        cost_budget_remaining=status.cost_budget_remaining,
                        daily_usage=status.daily_usage,
                        monthly_usage=status.monthly_usage,
                        last_updated=status.last_updated,
                        next_budget_reset=status.next_budget_reset,
                        active_sessions=status.active_sessions,
                        queue_length=status.queue_length
                    )
                    session.add(db_status)
                
                await session.commit()
                logger.debug("Updated doctor status")
        
        except Exception as e:
            logger.error(f"Failed to update doctor status: {e}")
            raise RepositoryError(f"Failed to update status: {str(e)}", "update_status")


class QueueRepository:
    """Repository for query queue management"""
    
    async def add_to_queue(self, queued_query: QueuedQuery) -> str:
        """Add query to processing queue"""
        try:
            async with get_database_session() as session:
                # First store the query if it doesn't exist
                consultation_repo = ConsultationRepository()
                await consultation_repo.store_query(queued_query.query)
                
                # Add to queue
                db_queued = QueuedQueryTable(
                    queue_id=queued_query.queue_id,
                    query_id=queued_query.query.query_id,
                    queued_at=queued_query.queued_at,
                    priority=queued_query.priority.value,
                    estimated_cost=queued_query.estimated_cost,
                    retry_count=queued_query.retry_count,
                    max_retries=queued_query.max_retries,
                    processing_started_at=queued_query.processing_started_at
                )
                
                session.add(db_queued)
                await session.commit()
                
                logger.debug(f"Added to queue: {queued_query.queue_id}")
                return queued_query.queue_id
        
        except Exception as e:
            logger.error(f"Failed to add to queue: {e}")
            raise RepositoryError(f"Failed to add to queue: {str(e)}", "add_to_queue")
    
    async def get_next_batch(self, batch_size: int = 10) -> List[QueuedQuery]:
        """Get next batch of queries to process"""
        try:
            async with get_database_session() as session:
                # Get highest priority, oldest queries that aren't being processed
                result = await session.execute(
                    select(QueuedQueryTable).where(
                        QueuedQueryTable.processing_started_at.is_(None)
                    ).order_by(
                        QueuedQueryTable.priority.desc(),
                        QueuedQueryTable.queued_at.asc()
                    ).limit(batch_size)
                )
                db_queued = result.scalars().all()
                
                # Convert to Pydantic models
                queued_queries = []
                consultation_repo = ConsultationRepository()
                
                for db_item in db_queued:
                    query = await consultation_repo.get_query(db_item.query_id)
                    if query:
                        queued_query = QueuedQuery(
                            queue_id=db_item.queue_id,
                            query=query,
                            queued_at=db_item.queued_at,
                            priority=QueryPriority(db_item.priority),
                            estimated_cost=db_item.estimated_cost,
                            retry_count=db_item.retry_count,
                            max_retries=db_item.max_retries,
                            processing_started_at=db_item.processing_started_at
                        )
                        queued_queries.append(queued_query)
                
                return queued_queries
        
        except Exception as e:
            logger.error(f"Failed to get next batch: {e}")
            raise RepositoryError(f"Failed to get batch: {str(e)}", "get_next_batch")
    
    async def mark_processing(self, queue_id: str) -> None:
        """Mark query as being processed"""
        try:
            async with get_database_session() as session:
                await session.execute(
                    update(QueuedQueryTable).where(
                        QueuedQueryTable.queue_id == queue_id
                    ).values(
                        processing_started_at=datetime.utcnow()
                    )
                )
                await session.commit()
        
        except Exception as e:
            logger.error(f"Failed to mark processing: {e}")
            raise RepositoryError(f"Failed to mark processing: {str(e)}", "mark_processing")
    
    async def remove_from_queue(self, queue_id: str) -> None:
        """Remove query from queue"""
        try:
            async with get_database_session() as session:
                await session.execute(
                    delete(QueuedQueryTable).where(
                        QueuedQueryTable.queue_id == queue_id
                    )
                )
                await session.commit()
                logger.debug(f"Removed from queue: {queue_id}")
        
        except Exception as e:
            logger.error(f"Failed to remove from queue: {e}")
            raise RepositoryError(f"Failed to remove from queue: {str(e)}", "remove_from_queue")
    
    async def get_queue_stats(self) -> Dict[str, Any]:
        """Get queue statistics"""
        try:
            async with get_database_session() as session:
                # Total queued
                result = await session.execute(
                    select(func.count(QueuedQueryTable.id))
                )
                total_queued = result.scalar()
                
                # Currently processing
                result = await session.execute(
                    select(func.count(QueuedQueryTable.id)).where(
                        QueuedQueryTable.processing_started_at.is_not(None)
                    )
                )
                processing = result.scalar()
                
                # By priority
                result = await session.execute(
                    select(
                        QueuedQueryTable.priority,
                        func.count(QueuedQueryTable.id)
                    ).group_by(QueuedQueryTable.priority)
                )
                by_priority = {row[0]: row[1] for row in result}
                
                return {
                    'total_queued': total_queued,
                    'processing': processing,
                    'waiting': total_queued - processing,
                    'by_priority': by_priority
                }
        
        except Exception as e:
            logger.error(f"Failed to get queue stats: {e}")
            return {'error': str(e)}


# Global repository instances with circuit breaker protection
consultation_repo = ConsultationRepository()
doctor_status_repo = DoctorStatusRepository()
queue_repo = QueueRepository()


async def get_consultation_repository() -> ConsultationRepository:
    """Get consultation repository with circuit breaker protection"""
    return consultation_repo


async def get_doctor_status_repository() -> DoctorStatusRepository:
    """Get doctor status repository with circuit breaker protection"""
    return doctor_status_repo


async def get_queue_repository() -> QueueRepository:
    """Get queue repository with circuit breaker protection"""
    return queue_repo