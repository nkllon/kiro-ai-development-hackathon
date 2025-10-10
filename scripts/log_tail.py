import argparse
import time
from pathlib import Path

parser = argparse.ArgumentParser()
parser.add_argument('path')
parser.add_argument('--interval', type=float, default=2.0)
args = parser.parse_args()

path = Path(args.path)
if not path.exists():
    raise SystemExit(f"File {path} not found")

last = 0
while True:
    data = path.read_text()
    if len(data) != last:
        print(data[last:], end='')
        last = len(data)
    time.sleep(args.interval)
