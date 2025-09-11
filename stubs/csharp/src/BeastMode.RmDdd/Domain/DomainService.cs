using System;
using System.Collections.Generic;
using System.Threading;
using System.Threading.Tasks;
using BeastMode.RmDdd.Core;
using BeastMode.RmDdd.Utilities;

namespace BeastMode.RmDdd.Domain
{
    /// <summary>
    /// Base class for domain services.
    /// Provides stateless domain logic encapsulation with RM compliance following .NET conventions.
    /// </summary>
    public abstract class DomainService : IDomainReflectiveModule
    {
        private bool _disposed;
        
        public string ServiceName { get; }
        public string DomainContext { get; }
        public string ModuleId { get; }
        
        protected DomainService(string serviceName, string domainContext)
        {
            ServiceName = serviceName ?? throw new ArgumentNullException(nameof(serviceName));
            DomainContext = domainContext ?? throw new ArgumentNullException(nameof(domainContext));
            ModuleId = GenerateModuleId();
        }
        
        private string GenerateModuleId()
        {
            return $"domain_service_{ServiceName.ToLowerInvariant()}_{Guid.NewGuid()}";
        }
        
        public virtual async Task<ModuleHealth> GetModuleStatusAsync(CancellationToken cancellationToken = default)
        {
            var validation = ValidateDomainInvariants();
            var status = validation.IsValid ? ModuleStatus.Available : ModuleStatus.Degraded;
            
            var capabilities = await GetModuleCapabilitiesAsync(cancellationToken);
            var healthIndicators = await GetHealthIndicatorsAsync(cancellationToken);
            
            return new ModuleHealth(
                status,
                $"Domain Service: {ServiceName}",
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
                    $"domain_service_{ServiceName}",
                    $"Domain service: {ServiceName}",
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
                ["service_name"] = ServiceName,
                ["domain_context"] = DomainContext,
                ["stateless"] = true,
                ["invariants_valid"] = ValidateDomainInvariants().IsValid
            };
            
            return Task.FromResult<IDictionary<string, object>>(indicators);
        }
        
        public virtual Task InitializeAsync(CancellationToken cancellationToken = default)
        {
            // Domain services are typically stateless and don't need initialization
            return Task.CompletedTask;
        }
        
        public virtual Task ShutdownAsync(CancellationToken cancellationToken = default)
        {
            // Domain services are typically stateless and don't need shutdown
            return Task.CompletedTask;
        }
        
        public abstract DomainBoundaries GetDomainBoundaries();
        
        public virtual ValidationResult ValidateDomainInvariants()
        {
            var result = new ValidationResult();
            
            // Validate that service operates within domain boundaries
            var boundaries = GetDomainBoundaries();
            if (boundaries.Context != DomainContext)
            {
                result.AddError("Service domain context mismatch");
            }
            
            // Additional domain-specific validation can be added by subclasses
            return result;
        }
        
        public virtual DomainHealth GetDomainHealth()
        {
            var validation = ValidateDomainInvariants();
            
            return new DomainHealth(
                DomainContext,
                true, // Domain services maintain boundary integrity by design
                validation.IsValid,
                1.0, // Services should have perfect language consistency
                CalculateComplexityScore()
            );
        }
        
        /// <summary>
        /// Calculate complexity score for this domain service
        /// Subclasses can override to provide more sophisticated complexity calculation
        /// </summary>
        /// <returns>Complexity score (lower is better)</returns>
        protected virtual double CalculateComplexityScore()
        {
            // Default implementation - can be overridden
            return 1.0;
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