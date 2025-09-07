package com.beastmode.rmddd.domain;

import java.util.Map;
import java.util.HashMap;
import java.util.Objects;
import java.util.Collections;

/**
 * Represents domain-specific query criteria.
 * Provides a domain-appropriate way to specify search criteria without exposing infrastructure concerns.
 */
public class DomainCriteria {
    
    private final Map<String, Object> criteria;
    private final String sortBy;
    private final SortDirection sortDirection;
    private final int limit;
    private final int offset;
    
    private DomainCriteria(Builder builder) {
        this.criteria = Collections.unmodifiableMap(new HashMap<>(builder.criteria));
        this.sortBy = builder.sortBy;
        this.sortDirection = builder.sortDirection;
        this.limit = builder.limit;
        this.offset = builder.offset;
    }
    
    public Map<String, Object> getCriteria() {
        return criteria;
    }
    
    public String getSortBy() {
        return sortBy;
    }
    
    public SortDirection getSortDirection() {
        return sortDirection;
    }
    
    public int getLimit() {
        return limit;
    }
    
    public int getOffset() {
        return offset;
    }
    
    public boolean hasCriterion(String key) {
        return criteria.containsKey(key);
    }
    
    public Object getCriterion(String key) {
        return criteria.get(key);
    }
    
    public boolean hasSorting() {
        return sortBy != null;
    }
    
    public boolean hasPaging() {
        return limit > 0;
    }
    
    public static Builder builder() {
        return new Builder();
    }
    
    public static DomainCriteria empty() {
        return new Builder().build();
    }
    
    public enum SortDirection {
        ASC, DESC
    }
    
    public static class Builder {
        private Map<String, Object> criteria = new HashMap<>();
        private String sortBy;
        private SortDirection sortDirection = SortDirection.ASC;
        private int limit = 0; // 0 means no limit
        private int offset = 0;
        
        public Builder criterion(String key, Object value) {
            this.criteria.put(key, value);
            return this;
        }
        
        public Builder criteria(Map<String, Object> criteria) {
            this.criteria.putAll(criteria);
            return this;
        }
        
        public Builder sortBy(String sortBy) {
            this.sortBy = sortBy;
            return this;
        }
        
        public Builder sortBy(String sortBy, SortDirection direction) {
            this.sortBy = sortBy;
            this.sortDirection = direction;
            return this;
        }
        
        public Builder sortDirection(SortDirection sortDirection) {
            this.sortDirection = sortDirection;
            return this;
        }
        
        public Builder limit(int limit) {
            if (limit < 0) {
                throw new IllegalArgumentException("Limit cannot be negative");
            }
            this.limit = limit;
            return this;
        }
        
        public Builder offset(int offset) {
            if (offset < 0) {
                throw new IllegalArgumentException("Offset cannot be negative");
            }
            this.offset = offset;
            return this;
        }
        
        public Builder page(int pageNumber, int pageSize) {
            if (pageNumber < 0) {
                throw new IllegalArgumentException("Page number cannot be negative");
            }
            if (pageSize <= 0) {
                throw new IllegalArgumentException("Page size must be positive");
            }
            this.limit = pageSize;
            this.offset = pageNumber * pageSize;
            return this;
        }
        
        public DomainCriteria build() {
            return new DomainCriteria(this);
        }
    }
    
    @Override
    public boolean equals(Object o) {
        if (this == o) return true;
        if (o == null || getClass() != o.getClass()) return false;
        DomainCriteria that = (DomainCriteria) o;
        return limit == that.limit &&
               offset == that.offset &&
               Objects.equals(criteria, that.criteria) &&
               Objects.equals(sortBy, that.sortBy) &&
               sortDirection == that.sortDirection;
    }
    
    @Override
    public int hashCode() {
        return Objects.hash(criteria, sortBy, sortDirection, limit, offset);
    }
    
    @Override
    public String toString() {
        return "DomainCriteria{" +
               "criteria=" + criteria +
               ", sortBy='" + sortBy + '\'' +
               ", sortDirection=" + sortDirection +
               ", limit=" + limit +
               ", offset=" + offset +
               '}';
    }
}