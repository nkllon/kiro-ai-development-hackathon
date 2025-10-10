#!/usr/bin/env python3
"""Send a single message through the Beast Mode Redis mailbox network."""

from __future__ import annotations

import argparse
import json
import logging
import time
from typing import Any, Dict
from uuid import uuid4

import redis

STREAM_PREFIX = "beast:mailbox"


def build_message(args: argparse.Namespace) -> Dict[str, str]:
    if args.json:
        payload: Dict[str, Any] = json.loads(args.json)
    else:
        payload = {"message": args.message}

    message_id = str(uuid4())
    timestamp = time.time()

    return {
        "message_id": message_id,
        "sender": args.sender,
        "recipient": args.recipient,
        "payload": json.dumps(payload),
        "message_type": args.message_type,
        "timestamp": str(timestamp),
    }


def send_message(args: argparse.Namespace) -> str:
    client = redis.Redis(
        host=args.redis_host,
        port=args.redis_port,
        password=args.redis_password,
        db=args.redis_db,
        decode_responses=True,
    )

    message = build_message(args)
    stream = f"{STREAM_PREFIX}:{args.recipient}:in"
    message_id = client.xadd(stream, message, maxlen=1000, approximate=True)
    return message_id


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Send mailbox message via Redis streams")
    parser.add_argument("sender", help="Sender agent ID")
    parser.add_argument("recipient", help="Recipient agent ID")
    parser.add_argument("--message", default="hello", help="Simple text payload")
    parser.add_argument("--json", help="Raw JSON payload (overrides --message)")
    parser.add_argument("--message-type", default="direct_message", help="Logical message type")
    parser.add_argument("--redis-host", default="localhost", help="Redis hostname")
    parser.add_argument("--redis-port", type=int, default=6379, help="Redis port")
    parser.add_argument("--redis-password", default=None, help="Redis password")
    parser.add_argument("--redis-db", type=int, default=0, help="Redis database index")
    parser.add_argument("--verbose", action="store_true", help="Verbose logging output")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    level = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(level=level, format="%(asctime)s %(levelname)s %(message)s")

    try:
        message_id = send_message(args)
        logging.info(
            "Sent message %s from %s to %s",
            message_id,
            args.sender,
            args.recipient,
        )
    except Exception as exc:
        logging.error("Failed to send message: %s", exc)
        raise SystemExit(1)


if __name__ == "__main__":
    main()
