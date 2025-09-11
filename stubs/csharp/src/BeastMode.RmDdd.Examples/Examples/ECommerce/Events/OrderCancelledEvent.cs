using System.Collections.Generic;
using BeastMode.RmDdd.Domain;

namespace BeastMode.RmDdd.Examples.ECommerce.Events
{
    /// <summary>
    /// Domain event fired when an order is cancelled.
    /// </summary>
    public class OrderCancelledEvent : DomainEvent
    {
        public OrderCancelledEvent(OrderId orderId) : base(orderId)
        {
        }
        
        public OrderId OrderId => (OrderId)AggregateId;
        
        public override IDictionary<string, object> GetEventData()
        {
            return new Dictionary<string, object>
            {
                ["order_id"] = OrderId.Value.ToString()
            };
        }
    }
}