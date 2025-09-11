using System.Collections.Generic;
using BeastMode.RmDdd.Domain;

namespace BeastMode.RmDdd.Examples.ECommerce.Events
{
    /// <summary>
    /// Domain event fired when an order is confirmed.
    /// </summary>
    public class OrderConfirmedEvent : DomainEvent
    {
        public decimal TotalAmount { get; }
        
        public OrderConfirmedEvent(OrderId orderId, decimal totalAmount) : base(orderId)
        {
            TotalAmount = totalAmount;
        }
        
        public OrderId OrderId => (OrderId)AggregateId;
        
        public override IDictionary<string, object> GetEventData()
        {
            return new Dictionary<string, object>
            {
                ["order_id"] = OrderId.Value.ToString(),
                ["total_amount"] = TotalAmount
            };
        }
    }
}