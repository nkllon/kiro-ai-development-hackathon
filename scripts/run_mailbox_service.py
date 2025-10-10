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
