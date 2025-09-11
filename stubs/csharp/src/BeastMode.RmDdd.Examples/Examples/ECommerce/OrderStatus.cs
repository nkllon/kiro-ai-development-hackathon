namespace BeastMode.RmDdd.Examples.ECommerce
{
    /// <summary>
    /// Enumeration of possible order status values.
    /// </summary>
    public enum OrderStatus
    {
        Pending,
        Confirmed,
        Shipped,
        Delivered,
        Cancelled
    }
    
    /// <summary>
    /// Extension methods for OrderStatus
    /// </summary>
    public static class OrderStatusExtensions
    {
        /// <summary>
        /// Gets the display name for the order status
        /// </summary>
        public static string GetDisplayName(this OrderStatus status)
        {
            return status switch
            {
                OrderStatus.Pending => "Pending",
                OrderStatus.Confirmed => "Confirmed",
                OrderStatus.Shipped => "Shipped",
                OrderStatus.Delivered => "Delivered",
                OrderStatus.Cancelled => "Cancelled",
                _ => status.ToString()
            };
        }
        
        /// <summary>
        /// Gets whether the order is modifiable
        /// </summary>
        public static bool IsModifiable(this OrderStatus status)
        {
            return status == OrderStatus.Pending;
        }
        
        /// <summary>
        /// Gets whether the order is cancellable
        /// </summary>
        public static bool IsCancellable(this OrderStatus status)
        {
            return status is OrderStatus.Pending or OrderStatus.Confirmed;
        }
        
        /// <summary>
        /// Gets whether the order is in a final state
        /// </summary>
        public static bool IsFinal(this OrderStatus status)
        {
            return status is OrderStatus.Delivered or OrderStatus.Cancelled;
        }
    }
}