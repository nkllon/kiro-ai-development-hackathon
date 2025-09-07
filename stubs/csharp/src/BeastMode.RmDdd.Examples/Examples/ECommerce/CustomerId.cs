using System;
using System.Collections.Generic;
using BeastMode.RmDdd.Domain;
using BeastMode.RmDdd.Utilities;

namespace BeastMode.RmDdd.Examples.ECommerce
{
    /// <summary>
    /// Value object representing a Customer identifier.
    /// </summary>
    public class CustomerId : ValueObject
    {
        public Guid Value { get; }
        
        public CustomerId(Guid value)
        {
            Value = value;
            ValidateOnConstruction();
        }
        
        public CustomerId(string value) : this(Guid.Parse(value))
        {
        }
        
        public static CustomerId Generate()
        {
            return new CustomerId(Guid.NewGuid());
        }
        
        public override ValidationResult Validate()
        {
            var result = new ValidationResult();
            
            if (Value == Guid.Empty)
            {
                result.AddError("Customer ID value cannot be empty");
            }
            
            return result;
        }
        
        protected override IEnumerable<object?> GetEqualityComponents()
        {
            yield return Value;
        }
        
        public override string ToString()
        {
            return $"CustomerId({Value})";
        }
        
        // Implicit conversion operators for convenience
        public static implicit operator Guid(CustomerId customerId) => customerId.Value;
        public static implicit operator CustomerId(Guid value) => new(value);
    }
}