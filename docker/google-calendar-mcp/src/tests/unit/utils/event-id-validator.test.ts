import { describe, it, expect } from 'vitest';
import {
  isValidEventId,
  validateEventId,
  sanitizeEventId
} from '../../../utils/event-id-validator.js';

describe('Event ID Validator', () => {
  describe('isValidEventId', () => {
    it('should accept valid event IDs', () => {
      expect(isValidEventId('abcdef123456')).toBe(true);
      expect(isValidEventId('event2025')).toBe(true);
      expect(isValidEventId('a1b2c3d4e5')).toBe(true);
      expect(isValidEventId('meeting0115')).toBe(true);
      expect(isValidEventId('12345')).toBe(true); // Minimum length
      expect(isValidEventId('abcdefghijklmnopqrstuv0123456789')).toBe(true); // All valid chars
    });

    it('should reject IDs that are too short', () => {
      expect(isValidEventId('')).toBe(false);
      expect(isValidEventId('a')).toBe(false);
      expect(isValidEventId('ab')).toBe(false);
      expect(isValidEventId('abc')).toBe(false);
      expect(isValidEventId('abcd')).toBe(false); // 4 chars, min is 5
    });

    it('should reject IDs that are too long', () => {
      const longId = 'a'.repeat(1025);
      expect(isValidEventId(longId)).toBe(false);
    });

    it('should accept IDs at boundary lengths', () => {
      const minId = 'a'.repeat(5);
      const maxId = 'a'.repeat(1024);
      expect(isValidEventId(minId)).toBe(true);
      expect(isValidEventId(maxId)).toBe(true);
    });

    it('should reject IDs with invalid characters', () => {
      expect(isValidEventId('event id')).toBe(false); // Space
      expect(isValidEventId('event_id')).toBe(false); // Underscore
      expect(isValidEventId('event.id')).toBe(false); // Period
      expect(isValidEventId('event/id')).toBe(false); // Slash
      expect(isValidEventId('event@id')).toBe(false); // At symbol
      expect(isValidEventId('event#id')).toBe(false); // Hash
      expect(isValidEventId('event$id')).toBe(false); // Dollar
      expect(isValidEventId('event%id')).toBe(false); // Percent
      expect(isValidEventId('event-id')).toBe(false); // Hyphen (not allowed in base32hex)
      expect(isValidEventId('EventID')).toBe(false); // Uppercase (not allowed)
      expect(isValidEventId('eventwxyz')).toBe(false); // Letters w,x,y,z not in base32hex
    });
  });

  describe('validateEventId', () => {
    it('should not throw for valid event IDs', () => {
      expect(() => validateEventId('validevent123')).not.toThrow();
      expect(() => validateEventId('event2025')).not.toThrow();
      expect(() => validateEventId('abcdefghijklmnopqrstuv')).not.toThrow();
    });

    it('should throw with specific error for short IDs', () => {
      expect(() => validateEventId('abc')).toThrow('Invalid event ID: must be at least 5 characters long');
    });

    it('should throw with specific error for long IDs', () => {
      const longId = 'a'.repeat(1025);
      expect(() => validateEventId(longId)).toThrow('Invalid event ID: must not exceed 1024 characters');
    });

    it('should throw with specific error for invalid characters', () => {
      expect(() => validateEventId('event_id_123')).toThrow('Invalid event ID: can only contain lowercase letters a-v and digits 0-9 (base32hex encoding)');
      expect(() => validateEventId('event-id')).toThrow('Invalid event ID: can only contain lowercase letters a-v and digits 0-9 (base32hex encoding)');
      expect(() => validateEventId('EventID')).toThrow('Invalid event ID: can only contain lowercase letters a-v and digits 0-9 (base32hex encoding)');
    });

    it('should combine multiple error messages', () => {
      expect(() => validateEventId('a b')).toThrow('Invalid event ID: must be at least 5 characters long, can only contain lowercase letters a-v and digits 0-9 (base32hex encoding)');
    });
  });

  describe('sanitizeEventId', () => {
    it('should convert to valid base32hex characters', () => {
      expect(sanitizeEventId('event id 123')).toMatch(/^[a-v0-9]+$/);
      expect(sanitizeEventId('event_id_123')).toMatch(/^[a-v0-9]+$/);
      expect(sanitizeEventId('event.id.123')).toMatch(/^[a-v0-9]+$/);
      // Check specific conversions
      expect(sanitizeEventId('eventid123')).toBe('eventid123');
      expect(sanitizeEventId('EventID123')).toBe('eventid123'); // Lowercase
      expect(sanitizeEventId('event-id-123')).toMatch(/^eventid123/); // Remove hyphens
    });

    it('should map w-z to a-d', () => {
      expect(sanitizeEventId('wxyz')).toMatch(/^abcd/);
      // 'event_with_xyz' -> 'eventaithbcd' (underscores removed, w in 'with' -> a, then xyz -> bcd)
      expect(sanitizeEventId('event_with_xyz')).toBe('eventaithbcd');
    });

    it('should handle special characters', () => {
      expect(sanitizeEventId('-event-id-')).toMatch(/^eventid/);
      expect(sanitizeEventId('___event___')).toMatch(/^event/);
    });

    it('should pad short IDs to meet minimum length', () => {
      const result = sanitizeEventId('ab');
      expect(result.length).toBeGreaterThanOrEqual(5);
      expect(result).toMatch(/^ab[a-v0-9]+$/); // Should append valid base32hex chars
    });

    it('should truncate long IDs to maximum length', () => {
      const longInput = 'a'.repeat(2000);
      const result = sanitizeEventId(longInput);
      expect(result.length).toBe(1024);
    });

    it('should handle empty input', () => {
      const result = sanitizeEventId('');
      expect(result).toMatch(/^event[a-v0-9]+$/);
      expect(result.length).toBeGreaterThanOrEqual(5);
    });

    it('should handle input with only invalid characters', () => {
      const result = sanitizeEventId('!@#$%');
      expect(result).toMatch(/^ev[a-v0-9]+$/);
    });

    it('should preserve valid characters', () => {
      const result = sanitizeEventId('validevent123');
      expect(result).toBe('validevent123');
      // But convert uppercase to lowercase
      const result2 = sanitizeEventId('ValidEvent123');
      expect(result2).toBe('validevent123');
    });

    it('should handle mixed valid and invalid characters', () => {
      const result = sanitizeEventId('Event!@#2025$%^Meeting');
      expect(result).toMatch(/^event2025meeting/);
      expect(result).toMatch(/^[a-v0-9]+$/);
    });
  });
});