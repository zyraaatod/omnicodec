from __future__ import annotations
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
APP_DIR = ROOT / "app"
if str(APP_DIR) not in sys.path:
    sys.path.insert(0, str(APP_DIR))

from omnicodec.cli import main as cli_main


def main() -> int:
    argv = sys.argv[1:]
    if not argv:
        argv = ["interactive"]
    return cli_main(argv)


if __name__ == "__main__":
    raise SystemExit(main())
