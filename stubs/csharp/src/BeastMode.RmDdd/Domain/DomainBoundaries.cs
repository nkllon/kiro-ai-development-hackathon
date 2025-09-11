using System;
using System.Collections.Generic;
using System.Linq;

namespace BeastMode.RmDdd.Domain
{
    /// <summary>
    /// Defines domain boundaries for a component.
    /// Specifies the domain context, capabilities, and constraints following .NET conventions.
    /// </summary>
    public class DomainBoundaries
    {
        public string Context { get; }
        public string? AggregateType { get; }
        public IReadOnlySet<string> Capabilities { get; }
        public IReadOnlySet<string> Constraints { get; }
        public string? UbiquitousLanguage { get; }
        
        private DomainBoundaries(Builder builder)
        {
            Context = builder.Context ?? throw new ArgumentNullException(nameof(builder.Context));
            AggregateType = builder.AggregateType;
            Capabilities = builder.Capabilities.ToHashSet();
            Constraints = builder.Constraints.ToHashSet();
            UbiquitousLanguage = builder.UbiquitousLanguage;
        }
        
        public bool HasCapability(string capability)
        {
            return Capabilities.Contains(capability);
        }
        
        public bool HasConstraint(string constraint)
        {
            return Constraints.Contains(constraint);
        }
        
        public static Builder Builder()
        {
            return new Builder();
        }
        
        public class Builder
        {
            internal string? Context { get; private set; }
            internal string? AggregateType { get; private set; }
            internal HashSet<string> Capabilities { get; } = new();
            internal HashSet<string> Constraints { get; } = new();
            internal string? UbiquitousLanguage { get; private set; }
            
            public Builder WithContext(string context)
            {
                Context = context;
                return this;
            }
            
            public Builder WithAggregateType(string aggregateType)
            {
                AggregateType = aggregateType;
                return this;
            }
            
            public Builder WithCapability(string capability)
            {
                Capabilities.Add(capability);
                return this;
            }
            
            public Builder WithCapabilities(IEnumerable<string> capabilities)
            {
                foreach (var capability in capabilities)
                {
                    Capabilities.Add(capability);
                }
                return this;
            }
            
            public Builder WithConstraint(string constraint)
            {
                Constraints.Add(constraint);
                return this;
            }
            
            public Builder WithConstraints(IEnumerable<string> constraints)
            {
                foreach (var constraint in constraints)
                {
                    Constraints.Add(constraint);
                }
                return this;
            }
            
            public Builder WithUbiquitousLanguage(string ubiquitousLanguage)
            {
                UbiquitousLanguage = ubiquitousLanguage;
                return this;
            }
            
            public DomainBoundaries Build()
            {
                return new DomainBoundaries(this);
            }
        }
        
        public override bool Equals(object? obj)
        {
            if (obj is not DomainBoundaries other) return false;
            if (ReferenceEquals(this, other)) return true;
            
            return Context == other.Context &&
                   AggregateType == other.AggregateType &&
                   Capabilities.SetEquals(other.Capabilities) &&
                   Constraints.SetEquals(other.Constraints) &&
                   UbiquitousLanguage == other.UbiquitousLanguage;
        }
        
        public override int GetHashCode()
        {
            return HashCode.Combine(Context, AggregateType, Capabilities, Constraints, UbiquitousLanguage);
        }
        
        public override string ToString()
        {
            return $"DomainBoundaries {{ Context = '{Context}', AggregateType = '{AggregateType}', " +
                   $"Capabilities = [{string.Join(", ", Capabilities)}], " +
                   $"Constraints = [{string.Join(", ", Constraints)}], " +
                   $"UbiquitousLanguage = '{UbiquitousLanguage}' }}";
        }
    }
}