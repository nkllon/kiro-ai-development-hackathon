"""Command line entry points for the mailbox service."""

from __future__ import annotations

import argparse
import asyncio
import json
import logging
from typing import Any, Dict

from .redis_mailbox import MailboxConfig, RedisMailboxService


def configure_logging(verbose: bool) -> None:
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(level=level, format="%(asctime)s %(levelname)s %(name)s: %(message)s")


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

    async def printer(message):
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

