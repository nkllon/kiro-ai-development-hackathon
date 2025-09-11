namespace BeastMode.RmDdd.Core
{
    /// <summary>
    /// Enumeration of possible module status values.
    /// </summary>
    public enum ModuleStatus
    {
        /// <summary>
        /// Module is fully available and operational
        /// </summary>
        Available,
        
        /// <summary>
        /// Module is operational but with reduced functionality
        /// </summary>
        Degraded,
        
        /// <summary>
        /// Module is temporarily unavailable
        /// </summary>
        Unavailable,
        
        /// <summary>
        /// Module is in error state
        /// </summary>
        Error,
        
        /// <summary>
        /// Module is starting up
        /// </summary>
        Starting,
        
        /// <summary>
        /// Module is shutting down
        /// </summary>
        Stopping
    }
    
    /// <summary>
    /// Extension methods for ModuleStatus
    /// </summary>
    public static class ModuleStatusExtensions
    {
        /// <summary>
        /// Gets the display name for the module status
        /// </summary>
        public static string GetDisplayName(this ModuleStatus status)
        {
            return status switch
            {
                ModuleStatus.Available => "Available",
                ModuleStatus.Degraded => "Degraded",
                ModuleStatus.Unavailable => "Unavailable",
                ModuleStatus.Error => "Error",
                ModuleStatus.Starting => "Starting",
                ModuleStatus.Stopping => "Stopping",
                _ => status.ToString()
            };
        }
        
        /// <summary>
        /// Gets whether the module is operational
        /// </summary>
        public static bool IsOperational(this ModuleStatus status)
        {
            return status is ModuleStatus.Available or ModuleStatus.Degraded;
        }
        
        /// <summary>
        /// Gets whether the module is healthy
        /// </summary>
        public static bool IsHealthy(this ModuleStatus status)
        {
            return status == ModuleStatus.Available;
        }
    }
}