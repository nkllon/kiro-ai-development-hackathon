using System;
using System.Collections.Generic;
using System.Threading;
using System.Threading.Tasks;

namespace BeastMode.RmDdd.Domain
{
    /// <summary>
    /// Abstract repository interface for domain layer.
    /// Provides domain-appropriate data access patterns following .NET conventions.
    /// </summary>
    /// <typeparam name="TEntity">The entity type</typeparam>
    /// <typeparam name="TId">The entity identifier type</typeparam>
    public interface IRepository<TEntity, in TId> 
        where TEntity : Entity<TId>
        where TId : notnull
    {
        /// <summary>
        /// Get entity by ID
        /// </summary>
        /// <param name="entityId">The entity identifier</param>
        /// <param name="cancellationToken">Cancellation token</param>
        /// <returns>Task containing optional entity</returns>
        Task<TEntity?> GetByIdAsync(TId entityId, CancellationToken cancellationToken = default);
        
        /// <summary>
        /// Save entity
        /// </summary>
        /// <param name="entity">The entity to save</param>
        /// <param name="cancellationToken">Cancellation token</param>
        /// <returns>Task containing saved entity</returns>
        Task<TEntity> SaveAsync(TEntity entity, CancellationToken cancellationToken = default);
        
        /// <summary>
        /// Delete entity
        /// </summary>
        /// <param name="entityId">The entity identifier</param>
        /// <param name="cancellationToken">Cancellation token</param>
        /// <returns>Task containing deletion success status</returns>
        Task<bool> DeleteAsync(TId entityId, CancellationToken cancellationToken = default);
        
        /// <summary>
        /// Find entities by domain criteria
        /// </summary>
        /// <param name="criteria">The domain criteria</param>
        /// <param name="cancellationToken">Cancellation token</param>
        /// <returns>Task containing enumerable of matching entities</returns>
        Task<IEnumerable<TEntity>> FindByCriteriaAsync(DomainCriteria criteria, CancellationToken cancellationToken = default);
        
        /// <summary>
        /// Check if entity exists
        /// </summary>
        /// <param name="entityId">The entity identifier</param>
        /// <param name="cancellationToken">Cancellation token</param>
        /// <returns>Task containing existence status</returns>
        Task<bool> ExistsAsync(TId entityId, CancellationToken cancellationToken = default);
        
        /// <summary>
        /// Count entities matching criteria
        /// </summary>
        /// <param name="criteria">The domain criteria</param>
        /// <param name="cancellationToken">Cancellation token</param>
        /// <returns>Task containing count</returns>
        Task<long> CountAsync(DomainCriteria criteria, CancellationToken cancellationToken = default);
        
        /// <summary>
        /// Find all entities (use with caution for large datasets)
        /// </summary>
        /// <param name="cancellationToken">Cancellation token</param>
        /// <returns>Task containing all entities</returns>
        Task<IEnumerable<TEntity>> FindAllAsync(CancellationToken cancellationToken = default);
    }
}