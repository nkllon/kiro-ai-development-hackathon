using System;
using System.Collections.Generic;
using BeastMode.RmDdd.Domain;
using BeastMode.RmDdd.Utilities;

namespace BeastMode.RmDdd.Examples.ECommerce
{
    /// <summary>
    /// Value object representing an Order identifier.
    /// Demonstrates proper value object implementation in C#.
    /// </summary>
    public class OrderId : ValueObject
    {
        public Guid Value { get; }
        
        public OrderId(Guid value)
        {
            Value = value;
            ValidateOnConstruction();
        }
        
        public OrderId(string value) : this(Guid.Parse(value))
        {
        }
        
        public static OrderId Generate()
        {
            return new OrderId(Guid.NewGuid());
        }
        
        public override ValidationResult Validate()
        {
            var result = new ValidationResult();
            
            if (Value == Guid.Empty)
            {
                result.AddError("Order ID value cannot be empty");
            }
            
            return result;
        }
        
        protected override IEnumerable<object?> GetEqualityComponents()
        {
            yield return Value;
        }
        
        public override string ToString()
        {
            return $"OrderId({Value})";
        }
        
        // Implicit conversion operators for convenience
        public static implicit operator Guid(OrderId orderId) => orderId.Value;
        public static implicit operator OrderId(Guid value) => new(value);
    }
}