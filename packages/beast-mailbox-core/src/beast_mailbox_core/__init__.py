"""Beast Mailbox Core package."""

from .redis_mailbox import MailboxMessage, RedisMailboxService

__all__ = ["MailboxMessage", "RedisMailboxService"]
