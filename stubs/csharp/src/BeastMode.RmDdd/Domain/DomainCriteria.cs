using System;
using System.Collections.Generic;
using System.Linq;

namespace BeastMode.RmDdd.Domain
{
    /// <summary>
    /// Represents domain-specific query criteria.
    /// Provides a domain-appropriate way to specify search criteria without exposing infrastructure concerns.
    /// </summary>
    public class DomainCriteria
    {
        public IReadOnlyDictionary<string, object> Criteria { get; }
        public string? SortBy { get; }
        public SortDirection SortDirection { get; }
        public int Limit { get; }
        public int Offset { get; }
        
        private DomainCriteria(Builder builder)
        {
            Criteria = builder.Criteria.ToDictionary(kvp => kvp.Key, kvp => kvp.Value);
            SortBy = builder.SortBy;
            SortDirection = builder.SortDirection;
            Limit = builder.Limit;
            Offset = builder.Offset;
        }
        
        public bool HasCriterion(string key)
        {
            return Criteria.ContainsKey(key);
        }
        
        public object? GetCriterion(string key)
        {
            return Criteria.TryGetValue(key, out var value) ? value : null;
        }
        
        public T? GetCriterion<T>(string key)
        {
            var value = GetCriterion(key);
            return value is T typedValue ? typedValue : default;
        }
        
        public bool HasSorting => !string.IsNullOrWhiteSpace(SortBy);
        public bool HasPaging => Limit > 0;
        
        public static Builder Builder()
        {
            return new Builder();
        }
        
        public static DomainCriteria Empty()
        {
            return new Builder().Build();
        }
        
        public class Builder
        {
            internal Dictionary<string, object> Criteria { get; } = new();
            internal string? SortBy { get; private set; }
            internal SortDirection SortDirection { get; private set; } = SortDirection.Ascending;
            internal int Limit { get; private set; } = 0; // 0 means no limit
            internal int Offset { get; private set; } = 0;
            
            public Builder WithCriterion(string key, object value)
            {
                Criteria[key] = value;
                return this;
            }
            
            public Builder WithCriteria(IDictionary<string, object> criteria)
            {
                foreach (var kvp in criteria)
                {
                    Criteria[kvp.Key] = kvp.Value;
                }
                return this;
            }
            
            public Builder WithSortBy(string sortBy)
            {
                SortBy = sortBy;
                return this;
            }
            
            public Builder WithSortBy(string sortBy, SortDirection direction)
            {
                SortBy = sortBy;
                SortDirection = direction;
                return this;
            }
            
            public Builder WithSortDirection(SortDirection sortDirection)
            {
                SortDirection = sortDirection;
                return this;
            }
            
            public Builder WithLimit(int limit)
            {
                if (limit < 0)
                    throw new ArgumentException("Limit cannot be negative", nameof(limit));
                
                Limit = limit;
                return this;
            }
            
            public Builder WithOffset(int offset)
            {
                if (offset < 0)
                    throw new ArgumentException("Offset cannot be negative", nameof(offset));
                
                Offset = offset;
                return this;
            }
            
            public Builder WithPage(int pageNumber, int pageSize)
            {
                if (pageNumber < 0)
                    throw new ArgumentException("Page number cannot be negative", nameof(pageNumber));
                
                if (pageSize <= 0)
                    throw new ArgumentException("Page size must be positive", nameof(pageSize));
                
                Limit = pageSize;
                Offset = pageNumber * pageSize;
                return this;
            }
            
            public DomainCriteria Build()
            {
                return new DomainCriteria(this);
            }
        }
        
        public override bool Equals(object? obj)
        {
            if (obj is not DomainCriteria other) return false;
            if (ReferenceEquals(this, other)) return true;
            
            return Criteria.SequenceEqual(other.Criteria) &&
                   SortBy == other.SortBy &&
                   SortDirection == other.SortDirection &&
                   Limit == other.Limit &&
                   Offset == other.Offset;
        }
        
        public override int GetHashCode()
        {
            return HashCode.Combine(Criteria, SortBy, SortDirection, Limit, Offset);
        }
        
        public override string ToString()
        {
            return $"DomainCriteria {{ Criteria = [{string.Join(", ", Criteria.Select(kvp => $"{kvp.Key}={kvp.Value}"))}], " +
                   $"SortBy = '{SortBy}', SortDirection = {SortDirection}, Limit = {Limit}, Offset = {Offset} }}";
        }
    }
    
    /// <summary>
    /// Sort direction enumeration
    /// </summary>
    public enum SortDirection
    {
        Ascending,
        Descending
    }
}