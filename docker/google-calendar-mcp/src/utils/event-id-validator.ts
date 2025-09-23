/**
 * Event ID validation utility for Google Calendar API
 */

/**
 * Validates a custom event ID according to Google Calendar requirements
 * @param eventId The event ID to validate
 * @returns true if valid, false otherwise
 */
export function isValidEventId(eventId: string): boolean {
  // Check length constraints (5-1024 characters)
  if (eventId.length < 5 || eventId.length > 1024) {
    return false;
  }
  
  // Check character constraints (base32hex encoding)
  // Google Calendar allows only: lowercase letters a-v and digits 0-9
  // Based on RFC2938 section 3.1.2
  const validPattern = /^[a-v0-9]+$/;
  return validPattern.test(eventId);
}

/**
 * Validates and throws an error if the event ID is invalid
 * @param eventId The event ID to validate
 * @throws Error if the event ID is invalid
 */
export function validateEventId(eventId: string): void {
  if (!isValidEventId(eventId)) {
    const errors: string[] = [];
    
    if (eventId.length < 5) {
      errors.push("must be at least 5 characters long");
    }
    
    if (eventId.length > 1024) {
      errors.push("must not exceed 1024 characters");
    }
    
    if (!/^[a-v0-9]+$/.test(eventId)) {
      errors.push("can only contain lowercase letters a-v and digits 0-9 (base32hex encoding)");
    }
    
    throw new Error(`Invalid event ID: ${errors.join(", ")}`);
  }
}

/**
 * Sanitizes a string to make it a valid event ID
 * Converts to base32hex encoding (lowercase a-v and 0-9 only)
 * @param input The input string to sanitize
 * @returns A valid event ID
 */
export function sanitizeEventId(input: string): string {
  // Convert to lowercase first
  let sanitized = input.toLowerCase();
  
  // Replace invalid characters:
  // - Keep digits 0-9 as is
  // - Map letters w-z to a-d (shift back)
  // - Map other characters to valid base32hex characters
  sanitized = sanitized.replace(/[^a-v0-9]/g, (char) => {
    // Map w-z to a-d
    if (char >= 'w' && char <= 'z') {
      return String.fromCharCode(char.charCodeAt(0) - 22); // w->a, x->b, y->c, z->d
    }
    // Map any other character to a default valid character
    return '';
  });
  
  // Remove any empty spaces from the mapping
  sanitized = sanitized.replace(/\s+/g, '');
  
  // Ensure minimum length
  if (sanitized.length < 5) {
    // Generate a base32hex timestamp
    const timestamp = Date.now().toString(32).replace(/[w-z]/g, (c) => 
      String.fromCharCode(c.charCodeAt(0) - 22)
    );
    
    if (sanitized.length === 0) {
      sanitized = `event${timestamp}`.substring(0, 26); // Match Google's 26-char format
    } else {
      sanitized = `${sanitized}${timestamp}`.substring(0, 26);
    }
  }
  
  // Ensure maximum length
  if (sanitized.length > 1024) {
    sanitized = sanitized.slice(0, 1024);
  }
  
  // Final validation - ensure only valid characters
  sanitized = sanitized.replace(/[^a-v0-9]/g, '');
  
  // If still too short after all operations, generate a default
  if (sanitized.length < 5) {
    // Generate a valid base32hex ID
    const now = Date.now();
    const base32hex = now.toString(32).replace(/[w-z]/g, (c) => 
      String.fromCharCode(c.charCodeAt(0) - 22)
    );
    sanitized = `ev${base32hex}`.substring(0, 26);
  }
  
  return sanitized;
}