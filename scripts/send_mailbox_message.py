#!/usr/bin/env python3
"""Send a message through the Beast Mode Redis mailbox."""

import argparse
import asyncio
import json
import logging
from typing import Any, Dict

from src.beast_mode.messaging.redis_mailbox import RedisMailboxService
from src.beast_mode.messaging.redis_foundation import RedisConfig


async def main_async(args: argparse.Namespace) -> None:
    config = RedisConfig(
        host=args.redis_host,
        port=args.redis_port,
        password=args.redis_password,
        db=args.redis_db,
    )
    service = RedisMailboxService(agent_id=args.sender, redis_config=config)
    if not await service.start():
        raise SystemExit("Failed to initialise Redis mailbox")

    payload: Dict[str, Any]
    if args.json:
        payload = json.loads(args.json)
    else:
        payload = {"message": args.message}

    await service.send_message(
        recipient=args.recipient,
        payload=payload,
        message_type=args.message_type,
    )
    await service.stop()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Send mailbox message")
    parser.add_argument("sender", help="Sender agent identifier")
    parser.add_argument("recipient", help="Recipient agent identifier")
    parser.add_argument("--message", default="hello", help="Message text payload")
    parser.add_argument(
        "--json",
        help="Raw JSON payload (overrides --message)",
    )
    parser.add_argument(
        "--message-type",
        default="direct_message",
        help="Logical message type",
    )
    parser.add_argument("--redis-host", default="localhost", help="Redis host")
    parser.add_argument("--redis-port", type=int, default=6379, help="Redis port")
    parser.add_argument("--redis-password", default=None, help="Redis password")
    parser.add_argument("--redis-db", type=int, default=0, help="Redis database index")
    return parser.parse_args()


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    args = parse_args()
    asyncio.run(main_async(args))


if __name__ == "__main__":
    main()
