using System;
using System.Collections.Generic;
using System.Threading;
using System.Threading.Tasks;
using BeastMode.RmDdd.Core;
using BeastMode.RmDdd.Utilities;

namespace BeastMode.RmDdd.Domain
{
    /// <summary>
    /// RM-compliant repository base class following .NET conventions.
    /// </summary>
    /// <typeparam name="TEntity">The entity type</typeparam>
    /// <typeparam name="TId">The entity identifier type</typeparam>
    public abstract class RepositoryRM<TEntity, TId> : IDomainReflectiveModule, IRepository<TEntity, TId>
        where TEntity : Entity<TId>
        where TId : notnull
    {
        private bool _disposed;
        
        public string EntityType { get; }
        public string DomainContext { get; }
        public string ModuleId { get; }
        
        protected RepositoryRM(string domainContext, string entityType)
        {
            DomainContext = domainContext ?? throw new ArgumentNullException(nameof(domainContext));
            EntityType = entityType ?? throw new ArgumentNullException(nameof(entityType));
            ModuleId = GenerateModuleId();
        }
        
        private string GenerateModuleId()
        {
            return $"repository_{EntityType.ToLowerInvariant()}_{Guid.NewGuid()}";
        }
        
        public virtual async Task<ModuleHealth> GetModuleStatusAsync(CancellationToken cancellationToken = default)
        {
            var isHealthy = await IsHealthyAsync(cancellationToken);
            var status = isHealthy ? ModuleStatus.Available : ModuleStatus.Degraded;
            
            var capabilities = await GetModuleCapabilitiesAsync(cancellationToken);
            var healthIndicators = await GetHealthIndicatorsAsync(cancellationToken);
            
            return new ModuleHealth(
                status,
                $"Repository for {EntityType}",
                capabilities,
                GetDomainHealth(),
                healthIndicators
            );
        }
        
        public virtual Task<IEnumerable<ModuleCapability>> GetModuleCapabilitiesAsync(CancellationToken cancellationToken = default)
        {
            var capabilities = new[]
            {
                new ModuleCapability(
                    $"repository_{EntityType}",
                    $"Repository for {EntityType}",
                    true,
                    "1.0.0"
                )
            };
            
            return Task.FromResult<IEnumerable<ModuleCapability>>(capabilities);
        }
        
        public virtual async Task<bool> IsHealthyAsync(CancellationToken cancellationToken = default)
        {
            try
            {
                await PerformHealthCheckAsync(cancellationToken);
                return true;
            }
            catch
            {
                return false;
            }
        }
        
        public virtual Task<IDictionary<string, object>> GetHealthIndicatorsAsync(CancellationToken cancellationToken = default)
        {
            var indicators = new Dictionary<string, object>
            {
                ["entity_type"] = EntityType,
                ["domain_context"] = DomainContext,
                ["repository_type"] = GetType().Name
            };
            
            return Task.FromResult<IDictionary<string, object>>(indicators);
        }
        
        public virtual Task InitializeAsync(CancellationToken cancellationToken = default)
        {
            // Default implementation - repositories typically don't need initialization
            return Task.CompletedTask;
        }
        
        public virtual Task ShutdownAsync(CancellationToken cancellationToken = default)
        {
            // Default implementation - repositories typically don't need shutdown
            return Task.CompletedTask;
        }
        
        public virtual DomainBoundaries GetDomainBoundaries()
        {
            return DomainBoundaries.Builder()
                .WithContext(DomainContext)
                .WithAggregateType(EntityType)
                .WithCapability("data_access")
                .WithCapability("persistence")
                .Build();
        }
        
        public virtual ValidationResult ValidateDomainInvariants()
        {
            var result = new ValidationResult();
            
            if (string.IsNullOrWhiteSpace(DomainContext))
            {
                result.AddError("Repository must have a domain context");
            }
            
            if (string.IsNullOrWhiteSpace(EntityType))
            {
                result.AddError("Repository must specify an entity type");
            }
            
            return result;
        }
        
        public virtual DomainHealth GetDomainHealth()
        {
            var validation = ValidateDomainInvariants();
            
            return new DomainHealth(
                DomainContext,
                true, // Repositories maintain boundary integrity by design
                validation.IsValid,
                1.0, // Perfect language consistency for well-designed repositories
                1.0  // Low complexity for repositories
            );
        }
        
        /// <summary>
        /// Perform repository-specific health check
        /// </summary>
        /// <param name="cancellationToken">Cancellation token</param>
        /// <returns>Task that completes when health check is done</returns>
        protected abstract Task PerformHealthCheckAsync(CancellationToken cancellationToken = default);
        
        // IRepository implementation
        public abstract Task<TEntity?> GetByIdAsync(TId entityId, CancellationToken cancellationToken = default);
        
        public abstract Task<TEntity> SaveAsync(TEntity entity, CancellationToken cancellationToken = default);
        
        public abstract Task<bool> DeleteAsync(TId entityId, CancellationToken cancellationToken = default);
        
        public abstract Task<IEnumerable<TEntity>> FindByCriteriaAsync(DomainCriteria criteria, CancellationToken cancellationToken = default);
        
        public abstract Task<bool> ExistsAsync(TId entityId, CancellationToken cancellationToken = default);
        
        public abstract Task<long> CountAsync(DomainCriteria criteria, CancellationToken cancellationToken = default);
        
        public abstract Task<IEnumerable<TEntity>> FindAllAsync(CancellationToken cancellationToken = default);
        
        protected virtual void Dispose(bool disposing)
        {
            if (!_disposed)
            {
                if (disposing)
                {
                    // Dispose managed resources
                }
                
                _disposed = true;
            }
        }
        
        public void Dispose()
        {
            Dispose(true);
            GC.SuppressFinalize(this);
        }
    }
}