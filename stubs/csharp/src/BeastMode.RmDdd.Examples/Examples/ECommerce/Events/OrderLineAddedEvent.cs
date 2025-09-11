using System.Collections.Generic;
using BeastMode.RmDdd.Domain;

namespace BeastMode.RmDdd.Examples.ECommerce.Events
{
    /// <summary>
    /// Domain event fired when an order line is added to an order.
    /// </summary>
    public class OrderLineAddedEvent : DomainEvent
    {
        public ProductId ProductId { get; }
        public int Quantity { get; }
        public decimal UnitPrice { get; }
        
        public OrderLineAddedEvent(OrderId orderId, ProductId productId, int quantity, decimal unitPrice) 
            : base(orderId)
        {
            ProductId = productId;
            Quantity = quantity;
            UnitPrice = unitPrice;
        }
        
        public OrderId OrderId => (OrderId)AggregateId;
        
        public override IDictionary<string, object> GetEventData()
        {
            return new Dictionary<string, object>
            {
                ["order_id"] = OrderId.Value.ToString(),
                ["product_id"] = ProductId.Value.ToString(),
                ["quantity"] = Quantity,
                ["unit_price"] = UnitPrice,
                ["line_total"] = UnitPrice * Quantity
            };
        }
    }
}