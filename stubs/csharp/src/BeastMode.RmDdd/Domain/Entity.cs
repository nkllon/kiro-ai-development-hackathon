using System;
using System.Collections.Generic;
using System.Threading;
using System.Threading.Tasks;
using BeastMode.RmDdd.Core;
using BeastMode.RmDdd.Utilities;

namespace BeastMode.RmDdd.Domain
{
    /// <summary>
    /// Base class for domain entities.
    /// Provides identity, equality, and RM compliance following .NET conventions.
    /// </summary>
    /// <typeparam name="TId">The type of the entity identifier</typeparam>
    public abstract class Entity<TId> : IDomainReflectiveModule
        where TId : notnull
    {
        private bool _disposed;
        
        public TId Id { get; }
        public string DomainContext { get; }
        public string ModuleId { get; }
        public int Version { get; private set; }
        public DateTimeOffset CreatedAt { get; }
        public DateTimeOffset UpdatedAt { get; private set; }
        
        protected Entity(TId id, string domainContext)
        {
            Id = id ?? throw new ArgumentNullException(nameof(id));
            DomainContext = domainContext ?? throw new ArgumentNullException(nameof(domainContext));
            ModuleId = GenerateModuleId();
            Version = 1;
            CreatedAt = DateTimeOffset.UtcNow;
            UpdatedAt = DateTimeOffset.UtcNow;
        }
        
        private string GenerateModuleId()
        {
            return $"entity_{GetType().Name.ToLowerInvariant()}_{Guid.NewGuid()}";
        }
        
        protected void UpdateVersion()
        {
            Version++;
            UpdatedAt = DateTimeOffset.UtcNow;
        }
        
        public virtual async Task<ModuleHealth> GetModuleStatusAsync(CancellationToken cancellationToken = default)
        {
            var validation = ValidateDomainInvariants();
            var status = validation.IsValid ? ModuleStatus.Available : ModuleStatus.Degraded;
            
            var capabilities = await GetModuleCapabilitiesAsync(cancellationToken);
            var healthIndicators = await GetHealthIndicatorsAsync(cancellationToken);
            
            return new ModuleHealth(
                status,
                $"Entity: {GetType().Name}",
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
                    "domain_entity",
                    "Domain entity with identity and invariants",
                    ValidateDomainInvariants().IsValid,
                    "1.0.0"
                )
            };
            
            return Task.FromResult<IEnumerable<ModuleCapability>>(capabilities);
        }
        
        public virtual Task<bool> IsHealthyAsync(CancellationToken cancellationToken = default)
        {
            return Task.FromResult(ValidateDomainInvariants().IsValid);
        }
        
        public virtual Task<IDictionary<string, object>> GetHealthIndicatorsAsync(CancellationToken cancellationToken = default)
        {
            var indicators = new Dictionary<string, object>
            {
                ["entity_type"] = GetType().Name,
                ["version"] = Version,
                ["domain_context"] = DomainContext,
                ["invariants_valid"] = ValidateDomainInvariants().IsValid
            };
            
            return Task.FromResult<IDictionary<string, object>>(indicators);
        }
        
        public virtual Task InitializeAsync(CancellationToken cancellationToken = default)
        {
            // Default implementation - entities are typically initialized on creation
            return Task.CompletedTask;
        }
        
        public virtual Task ShutdownAsync(CancellationToken cancellationToken = default)
        {
            // Default implementation - entities don't typically need shutdown
            return Task.CompletedTask;
        }
        
        public abstract DomainBoundaries GetDomainBoundaries();
        
        public abstract ValidationResult ValidateDomainInvariants();
        
        public virtual DomainHealth GetDomainHealth()
        {
            var validation = ValidateDomainInvariants();
            
            return new DomainHealth(
                DomainContext,
                true, // Entities maintain boundary integrity by design
                validation.IsValid,
                1.0, // Perfect language consistency for well-designed entities
                CalculateComplexityScore()
            );
        }
        
        /// <summary>
        /// Calculate complexity score for this entity
        /// Subclasses can override to provide more sophisticated complexity calculation
        /// </summary>
        /// <returns>Complexity score (lower is better)</returns>
        protected virtual double CalculateComplexityScore()
        {
            // Default implementation - can be overridden
            return 1.0;
        }
        
        public override bool Equals(object? obj)
        {
            if (obj is not Entity<TId> other) return false;
            if (ReferenceEquals(this, other)) return true;
            
            return GetType() == other.GetType() && EqualityComparer<TId>.Default.Equals(Id, other.Id);
        }
        
        public override int GetHashCode()
        {
            return HashCode.Combine(GetType(), Id);
        }
        
        public override string ToString()
        {
            return $"{GetType().Name} {{ Id = {Id}, DomainContext = '{DomainContext}', Version = {Version} }}";
        }
        
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