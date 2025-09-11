using System;
using System.Collections.Generic;
using System.Threading;
using System.Threading.Tasks;

namespace BeastMode.RmDdd.Core
{
    /// <summary>
    /// Base interface for all RM-DDD components in C#.
    /// Provides the core Reflective Module capabilities following .NET conventions.
    /// </summary>
    public interface IReflectiveModule : IDisposable
    {
        /// <summary>
        /// Gets the unique module identifier
        /// </summary>
        string ModuleId { get; }
        
        /// <summary>
        /// Get current module status
        /// </summary>
        /// <param name="cancellationToken">Cancellation token</param>
        /// <returns>Task containing module health information</returns>
        Task<ModuleHealth> GetModuleStatusAsync(CancellationToken cancellationToken = default);
        
        /// <summary>
        /// Get module capabilities
        /// </summary>
        /// <param name="cancellationToken">Cancellation token</param>
        /// <returns>Task containing list of module capabilities</returns>
        Task<IEnumerable<ModuleCapability>> GetModuleCapabilitiesAsync(CancellationToken cancellationToken = default);
        
        /// <summary>
        /// Check if module is healthy
        /// </summary>
        /// <param name="cancellationToken">Cancellation token</param>
        /// <returns>Task containing health status</returns>
        Task<bool> IsHealthyAsync(CancellationToken cancellationToken = default);
        
        /// <summary>
        /// Get detailed health indicators
        /// </summary>
        /// <param name="cancellationToken">Cancellation token</param>
        /// <returns>Task containing health indicators dictionary</returns>
        Task<IDictionary<string, object>> GetHealthIndicatorsAsync(CancellationToken cancellationToken = default);
        
        /// <summary>
        /// Initialize the module
        /// </summary>
        /// <param name="cancellationToken">Cancellation token</param>
        /// <returns>Task that completes when initialization is done</returns>
        Task InitializeAsync(CancellationToken cancellationToken = default);
        
        /// <summary>
        /// Shutdown the module gracefully
        /// </summary>
        /// <param name="cancellationToken">Cancellation token</param>
        /// <returns>Task that completes when shutdown is done</returns>
        Task ShutdownAsync(CancellationToken cancellationToken = default);
    }
}