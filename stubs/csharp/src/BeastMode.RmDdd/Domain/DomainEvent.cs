using System;
using System.Collections.Generic;

namespace BeastMode.RmDdd.Domain
{
    /// <summary>
    /// Base class for domain events.
    /// Represents something significant that happened in the domain following .NET conventions.
    /// </summary>
    public abstract class DomainEvent
    {
        public Guid EventId { get; }
        public object AggregateId { get; }
        public int EventVersion { get; }
        public DateTimeOffset OccurredAt { get; }
        public string EventType { get; }
        
        protected DomainEvent(object aggregateId, int eventVersion = 1)
        {
            EventId = Guid.NewGuid();
            AggregateId = aggregateId ?? throw new ArgumentNullException(nameof(aggregateId));
            EventVersion = eventVersion;
            OccurredAt = DateTimeOffset.UtcNow;
            EventType = GetType().Name;
        }
        
        /// <summary>
        /// Get event-specific data
        /// </summary>
        /// <returns>Dictionary containing event data</returns>
        public abstract IDictionary<string, object> GetEventData();
        
        /// <summary>
        /// Convert event to dictionary representation
        /// </summary>
        /// <returns>Dictionary representation of the event</returns>
        public virtual IDictionary<string, object> ToDictionary()
        {
            return new Dictionary<string, object>
            {
                ["event_id"] = EventId.ToString(),
                ["event_type"] = EventType,
                ["aggregate_id"] = AggregateId.ToString() ?? string.Empty,
                ["event_version"] = EventVersion,
                ["occurred_at"] = OccurredAt.ToString("O"),
                ["event_data"] = GetEventData()
            };
        }
        
        public override bool Equals(object? obj)
        {
            if (obj is not DomainEvent other) return false;
            if (ReferenceEquals(this, other)) return true;
            
            return EventId.Equals(other.EventId);
        }
        
        public override int GetHashCode()
        {
            return EventId.GetHashCode();
        }
        
        public override string ToString()
        {
            return $"{EventType} {{ EventId = {EventId}, AggregateId = {AggregateId}, EventVersion = {EventVersion}, OccurredAt = {OccurredAt} }}";
        }
    }
}