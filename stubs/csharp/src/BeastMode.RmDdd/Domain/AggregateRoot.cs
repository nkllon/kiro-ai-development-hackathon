using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading;
using System.Threading.Tasks;
using BeastMode.RmDdd.Core;
using BeastMode.RmDdd.Utilities;

namespace BeastMode.RmDdd.Domain
{
    /// <summary>
    /// Base class for aggregate roots.
    /// Extends Entity with domain event management and aggregate boundary enforcement.
    /// </summary>
    /// <typeparam name="TId">The type of the aggregate root identifier</typeparam>
    public abstract class AggregateRoot<TId> : Entity<TId>
        where TId : notnull
    {
        private readonly List<DomainEvent> _domainEvents = new();
        
        protected AggregateRoot(TId id, string domainContext) : base(id, domainContext)
        {
        }
        
        /// <summary>
        /// Add a domain event to be published
        /// </summary>
        /// <param name="domainEvent">The domain event to add</param>
        protected void AddDomainEvent(DomainEvent domainEvent)
        {
            if (domainEvent != null)
            {
                _domainEvents.Add(domainEvent);
            }
        }
        
        /// <summary>
        /// Get pending domain events
        /// </summary>
        /// <returns>Read-only list of pending domain events</returns>
        public IReadOnlyList<DomainEvent> GetDomainEvents()
        {
            return _domainEvents.AsReadOnly();
        }
        
        /// <summary>
        /// Clear domain events after publishing
        /// </summary>
        public void ClearDomainEvents()
        {
            _domainEvents.Clear();
        }
        
        /// <summary>
        /// Get aggregate boundaries definition
        /// </summary>
        /// <returns>Aggregate boundaries</returns>
        public abstract AggregateBoundaries GetAggregateBoundaries();
        
        /// <summary>
        /// Validate aggregate-specific rules
        /// </summary>
        /// <returns>Validation result for aggregate rules</returns>
        protected abstract ValidationResult ValidateAggregateRules();
        
        public override ValidationResult ValidateDomainInvariants()
        {
            var entityValidation = base.ValidateDomainInvariants();
            var aggregateValidation = ValidateAggregateRules();
            
            return entityValidation.Combine(aggregateValidation);
        }
        
        public override async Task<ModuleHealth> GetModuleStatusAsync(CancellationToken cancellationToken = default)
        {
            var baseHealth = await base.GetModuleStatusAsync(cancellationToken);
            var healthIndicators = new Dictionary<string, object>(baseHealth.HealthIndicators)
            {
                ["pending_events"] = _domainEvents.Count,
                ["aggregate_type"] = GetType().Name
            };
            
            return new ModuleHealth(
                baseHealth.Status,
                baseHealth.Message,
                baseHealth.Capabilities,
                baseHealth.DomainHealth,
                healthIndicators
            );
        }
        
        /// <summary>
        /// Apply business operation and generate domain events
        /// This is a template method that subclasses can override
        /// </summary>
        /// <param name="operation">The business operation to apply</param>
        /// <param name="cancellationToken">Cancellation token</param>
        /// <returns>Task that completes when operation is applied</returns>
        protected virtual Task ApplyBusinessOperationAsync(IBusinessOperation operation, CancellationToken cancellationToken = default)
        {
            // Template method - subclasses should override
            UpdateVersion();
            return Task.CompletedTask;
        }
    }
    
    /// <summary>
    /// Marker interface for business operations
    /// </summary>
    public interface IBusinessOperation
    {
        /// <summary>
        /// Gets the name of the operation
        /// </summary>
        string OperationName { get; }
    }
}