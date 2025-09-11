using System;
using System.Collections.Generic;
using System.Linq;

namespace BeastMode.RmDdd.Domain
{
    /// <summary>
    /// Defines aggregate boundaries and consistency rules.
    /// Specifies what entities belong to the aggregate and consistency constraints following .NET conventions.
    /// </summary>
    public class AggregateBoundaries
    {
        public string AggregateType { get; }
        public IReadOnlySet<string> EntityTypes { get; }
        public IReadOnlySet<string> Invariants { get; }
        public int MaxSize { get; }
        public bool EnforceConsistency { get; }
        
        private AggregateBoundaries(Builder builder)
        {
            AggregateType = builder.AggregateType ?? throw new ArgumentNullException(nameof(builder.AggregateType));
            EntityTypes = builder.EntityTypes.ToHashSet();
            Invariants = builder.Invariants.ToHashSet();
            MaxSize = builder.MaxSize;
            EnforceConsistency = builder.EnforceConsistency;
        }
        
        public bool ContainsEntityType(string entityType)
        {
            return EntityTypes.Contains(entityType);
        }
        
        public bool HasInvariant(string invariant)
        {
            return Invariants.Contains(invariant);
        }
        
        public static Builder Builder()
        {
            return new Builder();
        }
        
        public class Builder
        {
            internal string? AggregateType { get; private set; }
            internal HashSet<string> EntityTypes { get; } = new();
            internal HashSet<string> Invariants { get; } = new();
            internal int MaxSize { get; private set; } = 100; // Default max size
            internal bool EnforceConsistency { get; private set; } = true;
            
            public Builder WithAggregateType(string aggregateType)
            {
                AggregateType = aggregateType;
                return this;
            }
            
            public Builder WithEntityType(string entityType)
            {
                EntityTypes.Add(entityType);
                return this;
            }
            
            public Builder WithEntityTypes(IEnumerable<string> entityTypes)
            {
                foreach (var entityType in entityTypes)
                {
                    EntityTypes.Add(entityType);
                }
                return this;
            }
            
            public Builder WithInvariant(string invariant)
            {
                Invariants.Add(invariant);
                return this;
            }
            
            public Builder WithInvariants(IEnumerable<string> invariants)
            {
                foreach (var invariant in invariants)
                {
                    Invariants.Add(invariant);
                }
                return this;
            }
            
            public Builder WithMaxSize(int maxSize)
            {
                if (maxSize <= 0)
                    throw new ArgumentException("Max size must be positive", nameof(maxSize));
                
                MaxSize = maxSize;
                return this;
            }
            
            public Builder WithEnforceConsistency(bool enforceConsistency)
            {
                EnforceConsistency = enforceConsistency;
                return this;
            }
            
            public AggregateBoundaries Build()
            {
                return new AggregateBoundaries(this);
            }
        }
        
        public override bool Equals(object? obj)
        {
            if (obj is not AggregateBoundaries other) return false;
            if (ReferenceEquals(this, other)) return true;
            
            return AggregateType == other.AggregateType &&
                   EntityTypes.SetEquals(other.EntityTypes) &&
                   Invariants.SetEquals(other.Invariants) &&
                   MaxSize == other.MaxSize &&
                   EnforceConsistency == other.EnforceConsistency;
        }
        
        public override int GetHashCode()
        {
            return HashCode.Combine(AggregateType, EntityTypes, Invariants, MaxSize, EnforceConsistency);
        }
        
        public override string ToString()
        {
            return $"AggregateBoundaries {{ AggregateType = '{AggregateType}', " +
                   $"EntityTypes = [{string.Join(", ", EntityTypes)}], " +
                   $"Invariants = [{string.Join(", ", Invariants)}], " +
                   $"MaxSize = {MaxSize}, EnforceConsistency = {EnforceConsistency} }}";
        }
    }
}