package com.beastmode.rmddd.utilities;

import java.util.ArrayList;
import java.util.Collections;
import java.util.List;
import java.util.Objects;

/**
 * Result of validation operation.
 * Contains validation status, errors, and warnings.
 */
public class ValidationResult {
    
    private boolean isValid;
    private final List<String> errors;
    private final List<String> warnings;
    
    public ValidationResult() {
        this.isValid = true;
        this.errors = new ArrayList<>();
        this.warnings = new ArrayList<>();
    }
    
    public ValidationResult(boolean isValid) {
        this.isValid = isValid;
        this.errors = new ArrayList<>();
        this.warnings = new ArrayList<>();
    }
    
    public boolean isValid() {
        return isValid && errors.isEmpty();
    }
    
    public List<String> getErrors() {
        return Collections.unmodifiableList(errors);
    }
    
    public List<String> getWarnings() {
        return Collections.unmodifiableList(warnings);
    }
    
    public void addError(String error) {
        Objects.requireNonNull(error, "Error message cannot be null");
        errors.add(error);
        isValid = false;
    }
    
    public void addWarning(String warning) {
        Objects.requireNonNull(warning, "Warning message cannot be null");
        warnings.add(warning);
    }
    
    public boolean hasErrors() {
        return !errors.isEmpty();
    }
    
    public boolean hasWarnings() {
        return !warnings.isEmpty();
    }
    
    public int getErrorCount() {
        return errors.size();
    }
    
    public int getWarningCount() {
        return warnings.size();
    }
    
    /**
     * Combine this validation result with another
     * @param other The other validation result
     * @return New combined validation result
     */
    public ValidationResult combine(ValidationResult other) {
        ValidationResult combined = new ValidationResult();
        
        // Add all errors and warnings from both results
        this.errors.forEach(combined::addError);
        other.errors.forEach(combined::addError);
        this.warnings.forEach(combined::addWarning);
        other.warnings.forEach(combined::addWarning);
        
        return combined;
    }
    
    /**
     * Create a successful validation result
     * @return Valid validation result
     */
    public static ValidationResult success() {
        return new ValidationResult(true);
    }
    
    /**
     * Create a failed validation result with error
     * @param error The error message
     * @return Invalid validation result
     */
    public static ValidationResult failure(String error) {
        ValidationResult result = new ValidationResult(false);
        result.addError(error);
        return result;
    }
    
    @Override
    public boolean equals(Object o) {
        if (this == o) return true;
        if (o == null || getClass() != o.getClass()) return false;
        ValidationResult that = (ValidationResult) o;
        return isValid == that.isValid &&
               Objects.equals(errors, that.errors) &&
               Objects.equals(warnings, that.warnings);
    }
    
    @Override
    public int hashCode() {
        return Objects.hash(isValid, errors, warnings);
    }
    
    @Override
    public String toString() {
        StringBuilder sb = new StringBuilder();
        sb.append("ValidationResult{");
        sb.append("isValid=").append(isValid());
        
        if (!errors.isEmpty()) {
            sb.append(", errors=").append(errors);
        }
        
        if (!warnings.isEmpty()) {
            sb.append(", warnings=").append(warnings);
        }
        
        sb.append('}');
        return sb.toString();
    }
}