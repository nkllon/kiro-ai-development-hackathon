using System;
using System.Collections.Generic;
using BeastMode.RmDdd.Domain;
using BeastMode.RmDdd.Utilities;

namespace BeastMode.RmDdd.Examples.ECommerce
{
    /// <summary>
    /// Value object representing a Product identifier.
    /// </summary>
    public class ProductId : ValueObject
    {
        public Guid Value { get; }
        
        public ProductId(Guid value)
        {
            Value = value;
            ValidateOnConstruction();
        }
        
        public ProductId(string value) : this(Guid.Parse(value))
        {
        }
        
        public static ProductId Generate()
        {
            return new ProductId(Guid.NewGuid());
        }
        
        public override ValidationResult Validate()
        {
            var result = new ValidationResult();
            
            if (Value == Guid.Empty)
            {
                result.AddError("Product ID value cannot be empty");
            }
            
            return result;
        }
        
        protected override IEnumerable<object?> GetEqualityComponents()
        {
            yield return Value;
        }
        
        public override string ToString()
        {
            return $"ProductId({Value})";
        }
        
        // Implicit conversion operators for convenience
        public static implicit operator Guid(ProductId productId) => productId.Value;
        public static implicit operator ProductId(Guid value) => new(value);
    }
}