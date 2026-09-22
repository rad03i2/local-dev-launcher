"""Command-line interface."""
from __future__ import annotations
import argparse
import json
import signal
import sys
from pathlib import Path
from . import __version__
from .core import ConfigError, Launcher, load_config


def parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="dev-launch", description="Run multiple local development processes from one safe JSON config.")
    p.add_argument("--version", action="version", version=f"Local Dev Launcher {__version__} — Radwan Abdulhadi Ahmed / @rad03i2")
    sub = p.add_subparsers(dest="action", required=True)
    for action in ("check", "run"):
        s = sub.add_parser(action)
        s.add_argument("config", nargs="?", default="dev-launch.json")
        if action == "run":
            s.add_argument("--log-dir", default=".dev-logs")
            s.add_argument("--json", action="store_true", dest="as_json")
    return p


def main(argv: list[str] | None = None) -> int:
    args = parser().parse_args(argv)
    try:
        specs = load_config(args.config)
        if args.action == "check":
            print(f"OK: {len(specs)} process(es) configured")
            return 0
        launcher = Launcher(specs, Path(args.log_dir))
        def stop_handler(_sig: int, _frame: object) -> None:
            launcher.stop()
            raise KeyboardInterrupt
        signal.signal(signal.SIGINT, stop_handler)
        signal.signal(signal.SIGTERM, stop_handler)
        launcher.start()
        if args.as_json:
            print(json.dumps(launcher.status(), indent=2))
        else:
            for item in launcher.status():
                print(f"started {item['name']} (pid {item['pid']})")
            print("Press Ctrl+C to stop the stack.")
        code = launcher.wait()
        launcher.stop()
        return code
    except KeyboardInterrupt:
        return 130
    except (ConfigError, RuntimeError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
