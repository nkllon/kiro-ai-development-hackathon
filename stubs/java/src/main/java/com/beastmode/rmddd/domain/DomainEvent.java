package com.beastmode.rmddd.domain;

import java.time.Instant;
import java.util.Map;
import java.util.Objects;
import java.util.UUID;

/**
 * Base class for domain events.
 * Represents something significant that happened in the domain.
 */
public abstract class DomainEvent {
    
    private final UUID eventId;
    private final Object aggregateId;
    private final int eventVersion;
    private final Instant occurredAt;
    private final String eventType;
    
    protected DomainEvent(Object aggregateId, int eventVersion) {
        this.eventId = UUID.randomUUID();
        this.aggregateId = Objects.requireNonNull(aggregateId, "Aggregate ID cannot be null");
        this.eventVersion = eventVersion;
        this.occurredAt = Instant.now();
        this.eventType = getClass().getSimpleName();
    }
    
    protected DomainEvent(Object aggregateId) {
        this(aggregateId, 1);
    }
    
    public UUID getEventId() {
        return eventId;
    }
    
    public Object getAggregateId() {
        return aggregateId;
    }
    
    public int getEventVersion() {
        return eventVersion;
    }
    
    public Instant getOccurredAt() {
        return occurredAt;
    }
    
    public String getEventType() {
        return eventType;
    }
    
    /**
     * Get event-specific data
     * @return Map containing event data
     */
    public abstract Map<String, Object> getEventData();
    
    /**
     * Convert event to map representation
     * @return Map representation of the event
     */
    public Map<String, Object> toMap() {
        return Map.of(
            "event_id", eventId.toString(),
            "event_type", eventType,
            "aggregate_id", aggregateId.toString(),
            "event_version", eventVersion,
            "occurred_at", occurredAt.toString(),
            "event_data", getEventData()
        );
    }
    
    @Override
    public boolean equals(Object o) {
        if (this == o) return true;
        if (o == null || getClass() != o.getClass()) return false;
        DomainEvent that = (DomainEvent) o;
        return Objects.equals(eventId, that.eventId);
    }
    
    @Override
    public int hashCode() {
        return Objects.hash(eventId);
    }
    
    @Override
    public String toString() {
        return eventType + "{" +
               "eventId=" + eventId +
               ", aggregateId=" + aggregateId +
               ", eventVersion=" + eventVersion +
               ", occurredAt=" + occurredAt +
               '}';
    }
}