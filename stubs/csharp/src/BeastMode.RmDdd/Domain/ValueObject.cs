using System;
using BeastMode.RmDdd.Utilities;

namespace BeastMode.RmDdd.Domain
{
    /// <summary>
    /// Base class for value objects.
    /// Provides value-based equality and immutability enforcement following .NET conventions.
    /// </summary>
    public abstract class ValueObject : IEquatable<ValueObject>
    {
        /// <summary>
        /// Validate value object constraints
        /// </summary>
        /// <returns>Validation result</returns>
        public abstract ValidationResult Validate();
        
        /// <summary>
        /// Get equality components for value-based equality
        /// </summary>
        /// <returns>Enumerable of equality components</returns>
        protected abstract System.Collections.Generic.IEnumerable<object?> GetEqualityComponents();
        
        /// <summary>
        /// Value objects are equal if all their attributes are equal
        /// </summary>
        public override bool Equals(object? obj)
        {
            return obj is ValueObject other && Equals(other);
        }
        
        /// <summary>
        /// Value objects are equal if all their attributes are equal
        /// </summary>
        public virtual bool Equals(ValueObject? other)
        {
            if (other is null) return false;
            if (ReferenceEquals(this, other)) return true;
            if (GetType() != other.GetType()) return false;
            
            return GetEqualityComponents().SequenceEqual(other.GetEqualityComponents());
        }
        
        /// <summary>
        /// Hash code based on all attributes
        /// </summary>
        public override int GetHashCode()
        {
            return GetEqualityComponents()
                .Where(x => x != null)
                .Aggregate(1, (current, obj) => HashCode.Combine(current, obj));
        }
        
        /// <summary>
        /// String representation of the value object
        /// </summary>
        public override string ToString()
        {
            return $"{GetType().Name} {{ {string.Join(", ", GetEqualityComponents())} }}";
        }
        
        /// <summary>
        /// Validate the value object during construction
        /// Throws ArgumentException if validation fails
        /// </summary>
        protected void ValidateOnConstruction()
        {
            var result = Validate();
            if (!result.IsValid)
            {
                throw new ArgumentException($"Invalid value object: {string.Join(", ", result.Errors)}");
            }
        }
        
        public static bool operator ==(ValueObject? left, ValueObject? right)
        {
            return Equals(left, right);
        }
        
        public static bool operator !=(ValueObject? left, ValueObject? right)
        {
            return !Equals(left, right);
        }
    }
}