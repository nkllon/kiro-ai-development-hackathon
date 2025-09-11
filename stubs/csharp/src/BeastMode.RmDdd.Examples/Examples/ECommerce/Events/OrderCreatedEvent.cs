using System.Collections.Generic;
using BeastMode.RmDdd.Domain;

namespace BeastMode.RmDdd.Examples.ECommerce.Events
{
    /// <summary>
    /// Domain event fired when an order is created.
    /// </summary>
    public class OrderCreatedEvent : DomainEvent
    {
        public CustomerId CustomerId { get; }
        
        public OrderCreatedEvent(OrderId orderId, CustomerId customerId) : base(orderId)
        {
            CustomerId = customerId;
        }
        
        public OrderId OrderId => (OrderId)AggregateId;
        
        public override IDictionary<string, object> GetEventData()
        {
            return new Dictionary<string, object>
            {
                ["order_id"] = OrderId.Value.ToString(),
                ["customer_id"] = CustomerId.Value.ToString()
            };
        }
    }
}