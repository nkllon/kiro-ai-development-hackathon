"""Command line entry points for the mailbox service."""

from __future__ import annotations

import argparse
import asyncio
import json
import logging
from typing import Any, Dict

from .redis_mailbox import MailboxConfig, MailboxMessage, RedisMailboxService


def configure_logging(verbose: bool) -> None:
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(level=level, format="%(asctime)s %(levelname)s %(name)s: %(message)s")


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
    await service.connect()
    client = service._client
    if client is None:
        raise SystemExit("Redis client unavailable after connection")

    try:
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
        await service.stop()


async def run_service_async(args: argparse.Namespace) -> None:
    config = MailboxConfig(
        host=args.redis_host,
        port=args.redis_port,
        password=args.redis_password,
        db=args.redis_db,
        stream_prefix=args.stream_prefix,
        max_stream_length=args.maxlen,
        poll_interval=args.poll_interval,
    )

    service = RedisMailboxService(agent_id=args.agent_id, config=config)

    # Handle one-shot latest message retrieval
    if args.latest:
        await _fetch_latest_messages(service, args.count, args.ack, args.trim)
        return

    # Streaming mode
    async def printer(message: MailboxMessage) -> None:
        logging.info(
            "📬 %s <- %s (%s): %s",
            message.recipient,
            message.sender,
            message.message_type,
            message.payload,
        )

    if args.echo:
        service.register_handler(printer)

    if not await service.start():
        raise SystemExit("Failed to start mailbox service")

    try:
        await asyncio.Event().wait()
    except (KeyboardInterrupt, asyncio.CancelledError):
        logging.info("Stopping mailbox service...")
    finally:
        await service.stop()
        logging.info("Mailbox service stopped")


def run_service(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="Run Beast mailbox service")
    parser.add_argument("agent_id", help="Agent identifier for this instance")
    parser.add_argument("--redis-host", default="localhost")
    parser.add_argument("--redis-port", type=int, default=6379)
    parser.add_argument("--redis-password", default=None)
    parser.add_argument("--redis-db", type=int, default=0)
    parser.add_argument("--stream-prefix", default="beast:mailbox")
    parser.add_argument("--maxlen", type=int, default=1000, help="Max stream length")
    parser.add_argument("--poll-interval", type=float, default=2.0)
    parser.add_argument("--echo", action="store_true", help="Print received messages to stdout")
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
    parser.add_argument("--verbose", action="store_true")
    args = parser.parse_args(argv)
    configure_logging(args.verbose)
    asyncio.run(run_service_async(args))


async def send_message_async(args: argparse.Namespace) -> None:
    config = MailboxConfig(
        host=args.redis_host,
        port=args.redis_port,
        password=args.redis_password,
        db=args.redis_db,
        stream_prefix=args.stream_prefix,
    )
    service = RedisMailboxService(agent_id=args.sender, config=config)
    payload: Dict[str, Any]
    if args.json:
        payload = json.loads(args.json)
    else:
        payload = {"message": args.message}
    await service.send_message(recipient=args.recipient, payload=payload, message_type=args.message_type)
    await service.stop()
    logging.info("Sent message from %s to %s", args.sender, args.recipient)


def send_message(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="Send message via Beast mailbox")
    parser.add_argument("sender", help="Sender agent id")
    parser.add_argument("recipient", help="Recipient agent id")
    parser.add_argument("--message", default="hello")
    parser.add_argument("--json")
    parser.add_argument("--message-type", default="direct_message")
    parser.add_argument("--redis-host", default="localhost")
    parser.add_argument("--redis-port", type=int, default=6379)
    parser.add_argument("--redis-password", default=None)
    parser.add_argument("--redis-db", type=int, default=0)
    parser.add_argument("--stream-prefix", default="beast:mailbox")
    parser.add_argument("--verbose", action="store_true")
    args = parser.parse_args(argv)
    configure_logging(args.verbose)
    asyncio.run(send_message_async(args))

