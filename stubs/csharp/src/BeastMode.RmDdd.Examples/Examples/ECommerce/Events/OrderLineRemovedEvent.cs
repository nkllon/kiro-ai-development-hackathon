using System.Collections.Generic;
using BeastMode.RmDdd.Domain;

namespace BeastMode.RmDdd.Examples.ECommerce.Events
{
    /// <summary>
    /// Domain event fired when an order line is removed from an order.
    /// </summary>
    public class OrderLineRemovedEvent : DomainEvent
    {
        public ProductId ProductId { get; }
        
        public OrderLineRemovedEvent(OrderId orderId, ProductId productId) : base(orderId)
        {
            ProductId = productId;
        }
        
        public OrderId OrderId => (OrderId)AggregateId;
        
        public override IDictionary<string, object> GetEventData()
        {
            return new Dictionary<string, object>
            {
                ["order_id"] = OrderId.Value.ToString(),
                ["product_id"] = ProductId.Value.ToString()
            };
        }
    }
}