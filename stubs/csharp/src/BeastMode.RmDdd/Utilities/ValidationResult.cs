using System;
using System.Collections.Generic;
using System.Linq;

namespace BeastMode.RmDdd.Utilities
{
    /// <summary>
    /// Result of validation operation.
    /// Contains validation status, errors, and warnings following .NET conventions.
    /// </summary>
    public class ValidationResult
    {
        private readonly List<string> _errors = new();
        private readonly List<string> _warnings = new();
        
        public bool IsValid => !_errors.Any();
        public IReadOnlyList<string> Errors => _errors.AsReadOnly();
        public IReadOnlyList<string> Warnings => _warnings.AsReadOnly();
        
        public ValidationResult()
        {
        }
        
        public ValidationResult(bool isValid)
        {
            if (!isValid)
            {
                _errors.Add("Validation failed");
            }
        }
        
        public bool HasErrors => _errors.Any();
        public bool HasWarnings => _warnings.Any();
        public int ErrorCount => _errors.Count;
        public int WarningCount => _warnings.Count;
        
        public void AddError(string error)
        {
            if (string.IsNullOrWhiteSpace(error))
                throw new ArgumentException("Error message cannot be null or empty", nameof(error));
            
            _errors.Add(error);
        }
        
        public void AddWarning(string warning)
        {
            if (string.IsNullOrWhiteSpace(warning))
                throw new ArgumentException("Warning message cannot be null or empty", nameof(warning));
            
            _warnings.Add(warning);
        }
        
        /// <summary>
        /// Combine this validation result with another
        /// </summary>
        /// <param name="other">The other validation result</param>
        /// <returns>New combined validation result</returns>
        public ValidationResult Combine(ValidationResult other)
        {
            if (other == null) throw new ArgumentNullException(nameof(other));
            
            var combined = new ValidationResult();
            
            // Add all errors and warnings from both results
            foreach (var error in _errors.Concat(other._errors))
            {
                combined.AddError(error);
            }
            
            foreach (var warning in _warnings.Concat(other._warnings))
            {
                combined.AddWarning(warning);
            }
            
            return combined;
        }
        
        /// <summary>
        /// Create a successful validation result
        /// </summary>
        /// <returns>Valid validation result</returns>
        public static ValidationResult Success()
        {
            return new ValidationResult();
        }
        
        /// <summary>
        /// Create a failed validation result with error
        /// </summary>
        /// <param name="error">The error message</param>
        /// <returns>Invalid validation result</returns>
        public static ValidationResult Failure(string error)
        {
            var result = new ValidationResult();
            result.AddError(error);
            return result;
        }
        
        /// <summary>
        /// Create a failed validation result with multiple errors
        /// </summary>
        /// <param name="errors">The error messages</param>
        /// <returns>Invalid validation result</returns>
        public static ValidationResult Failure(IEnumerable<string> errors)
        {
            var result = new ValidationResult();
            foreach (var error in errors)
            {
                result.AddError(error);
            }
            return result;
        }
        
        public override bool Equals(object? obj)
        {
            if (obj is not ValidationResult other) return false;
            if (ReferenceEquals(this, other)) return true;
            
            return IsValid == other.IsValid &&
                   _errors.SequenceEqual(other._errors) &&
                   _warnings.SequenceEqual(other._warnings);
        }
        
        public override int GetHashCode()
        {
            return HashCode.Combine(IsValid, _errors, _warnings);
        }
        
        public override string ToString()
        {
            var parts = new List<string> { $"IsValid = {IsValid}" };
            
            if (_errors.Any())
            {
                parts.Add($"Errors = [{string.Join(", ", _errors)}]");
            }
            
            if (_warnings.Any())
            {
                parts.Add($"Warnings = [{string.Join(", ", _warnings)}]");
            }
            
            return $"ValidationResult {{ {string.Join(", ", parts)} }}";
        }
    }
}