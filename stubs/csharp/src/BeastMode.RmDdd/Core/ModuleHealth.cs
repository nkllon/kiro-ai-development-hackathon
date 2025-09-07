using System;
using System.Collections.Generic;
using System.Linq;

namespace BeastMode.RmDdd.Core
{
    /// <summary>
    /// Comprehensive module health information.
    /// </summary>
    public class ModuleHealth
    {
        public ModuleStatus Status { get; }
        public string Message { get; }
        public IReadOnlyList<ModuleCapability> Capabilities { get; }
        public DomainHealth? DomainHealth { get; }
        public IReadOnlyDictionary<string, object> HealthIndicators { get; }
        public DateTimeOffset Timestamp { get; }
        
        public ModuleHealth(
            ModuleStatus status,
            string message,
            IEnumerable<ModuleCapability> capabilities,
            DomainHealth? domainHealth = null,
            IDictionary<string, object>? healthIndicators = null)
        {
            Status = status;
            Message = message ?? throw new ArgumentNullException(nameof(message));
            Capabilities = capabilities?.ToList().AsReadOnly() ?? throw new ArgumentNullException(nameof(capabilities));
            DomainHealth = domainHealth;
            HealthIndicators = (healthIndicators ?? new Dictionary<string, object>()).ToDictionary(kvp => kvp.Key, kvp => kvp.Value);
            Timestamp = DateTimeOffset.UtcNow;
        }
        
        /// <summary>
        /// Gets whether the module is healthy
        /// </summary>
        public bool IsHealthy => Status == ModuleStatus.Available;
        
        public override bool Equals(object? obj)
        {
            if (obj is not ModuleHealth other) return false;
            
            return Status == other.Status &&
                   Message == other.Message &&
                   Capabilities.SequenceEqual(other.Capabilities) &&
                   Equals(DomainHealth, other.DomainHealth) &&
                   HealthIndicators.SequenceEqual(other.HealthIndicators);
        }
        
        public override int GetHashCode()
        {
            return HashCode.Combine(Status, Message, Capabilities, DomainHealth, HealthIndicators);
        }
        
        public override string ToString()
        {
            return $"ModuleHealth {{ Status = {Status}, Message = '{Message}', Capabilities = {Capabilities.Count}, Timestamp = {Timestamp} }}";
        }
    }
}