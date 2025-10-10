#!/usr/bin/env python3
"""Run the Redis mailbox service for a given agent."""

import argparse
import asyncio
import logging
from typing import Dict

from src.beast_mode.messaging.redis_mailbox import (
    MailboxMessage,
    RedisMailboxService,
)
from src.beast_mode.messaging.redis_foundation import RedisConfig


def configure_logging(verbose: bool) -> None:
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    )


async def _fetch_latest_messages(
    service: RedisMailboxService,
    count: int,
    ack: bool = False,
    trim: bool = False,
) -> None:
    """Retrieve the latest messages without starting the consumer loop.
    
    Args:
        service: The mailbox service instance
        count: Number of messages to retrieve
        ack: If True, acknowledge messages after displaying them
        trim: If True, delete messages after acknowledging them
    """
    if not await service.redis.initialize():
        raise SystemExit("Failed to connect to Redis")

    try:
        client = service.redis.client
        if client is None:
            raise SystemExit("Redis client unavailable after initialization")

        stream = service.inbox_stream
        entries = await client.xrevrange(stream, count=count)

        if not entries:
            logging.info("No messages found in %s", stream)
            return

        message_ids = []
        for message_id, fields in entries:
            mailbox_message = MailboxMessage.from_redis_fields(fields)
            logging.info(
                "📬 %s <- %s (%s) [%s]: %s",
                mailbox_message.recipient,
                mailbox_message.sender,
                mailbox_message.message_type,
                message_id,
                mailbox_message.payload,
            )
            message_ids.append(message_id)

        # Handle acknowledgement if requested
        if ack and message_ids:
            try:
                # Ensure consumer group exists before acknowledging
                consumer_group = f"{service.agent_id}:group"
                try:
                    await client.xgroup_create(
                        name=stream,
                        groupname=consumer_group,
                        id="0",
                        mkstream=True,
                    )
                except Exception as exc:
                    if "BUSYGROUP" not in str(exc):
                        logging.warning("Could not create consumer group: %s", exc)

                # Acknowledge messages
                ack_count = await client.xack(stream, consumer_group, *message_ids)
                logging.info("✓ Acknowledged %d message(s) in group %s", ack_count, consumer_group)
            except Exception as exc:
                logging.error("Failed to acknowledge messages: %s", exc)
                raise SystemExit(f"Acknowledgement failed: {exc}")

        # Handle trim/delete if requested
        if trim and message_ids:
            try:
                delete_count = await client.xdel(stream, *message_ids)
                logging.info("🗑️  Deleted %d message(s) from stream", delete_count)
            except Exception as exc:
                logging.error("Failed to delete messages: %s", exc)
                raise SystemExit(f"Deletion failed: {exc}")

    finally:
        await service.redis.shutdown()


async def main_async(args: argparse.Namespace) -> None:
    config = RedisConfig(
        host=args.redis_host,
        port=args.redis_port,
        password=args.redis_password,
        db=args.redis_db,
    )
    service = RedisMailboxService(
        agent_id=args.agent_id,
        redis_config=config,
        poll_interval=args.poll_interval,
    )

    if args.latest:
        await _fetch_latest_messages(service, args.count, args.ack, args.trim)
        return

    async def printer(message: MailboxMessage) -> None:
        logging.info(
            "📬 %s <- %s (%s): %s",
            message.recipient,
            message.sender,
            message.message_type,
            message.payload,
        )

    service.register_handler(printer)

    started = await service.start()
    if not started:
        raise SystemExit("Failed to start mailbox service")

    logging.info("Mailbox service running as agent '%s'", args.agent_id)

    stop_event = asyncio.Event()

    try:
        await stop_event.wait()
    except (KeyboardInterrupt, asyncio.CancelledError):
        logging.info("Stopping mailbox service...")
    finally:
        await service.stop()
        logging.info("Mailbox service stopped")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run Beast Mode mailbox service")
    parser.add_argument("agent_id", help="Unique agent identifier for this node")
    parser.add_argument("--redis-host", default="localhost", help="Redis host")
    parser.add_argument("--redis-port", type=int, default=6379, help="Redis port")
    parser.add_argument("--redis-password", default=None, help="Redis password")
    parser.add_argument("--redis-db", type=int, default=0, help="Redis database index")
    parser.add_argument(
        "--poll-interval",
        type=float,
        default=2.0,
        help="Seconds between stream polling attempts",
    )
    parser.add_argument(
        "--latest",
        action="store_true",
        help="Print the latest message(s) and exit instead of streaming",
    )
    parser.add_argument(
        "--count",
        type=int,
        default=1,
        help="Number of latest messages to display when using --latest",
    )
    parser.add_argument(
        "--ack",
        action="store_true",
        help="Acknowledge messages after displaying them (requires --latest)",
    )
    parser.add_argument(
        "--trim",
        action="store_true",
        help="Delete messages after acknowledging them (requires --latest and --ack)",
    )
    parser.add_argument("--verbose", action="store_true", help="Enable debug logging")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    configure_logging(args.verbose)
    try:
        asyncio.run(main_async(args))
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
