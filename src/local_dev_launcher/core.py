"""Core process orchestration for Local Dev Launcher."""
from __future__ import annotations

from dataclasses import dataclass
import json
import os
from pathlib import Path
import signal
import subprocess
import time
from typing import IO, Any


class ConfigError(ValueError):
    """Raised when launcher configuration is invalid."""


@dataclass(frozen=True)
class ProcessSpec:
    name: str
    command: tuple[str, ...]
    cwd: Path
    env: dict[str, str]
    ready_after: float = 0.0
    optional: bool = False


def load_config(path: str | Path) -> list[ProcessSpec]:
    config_path = Path(path).resolve()
    try:
        raw = json.loads(config_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ConfigError(f"Cannot read configuration: {exc}") from exc
    if not isinstance(raw, dict) or not isinstance(raw.get("processes"), list) or not raw["processes"]:
        raise ConfigError("Configuration must contain a non-empty 'processes' array")
    base = config_path.parent
    seen: set[str] = set()
    specs: list[ProcessSpec] = []
    for i, item in enumerate(raw["processes"]):
        if not isinstance(item, dict):
            raise ConfigError(f"processes[{i}] must be an object")
        name = item.get("name")
        command = item.get("command")
        if not isinstance(name, str) or not name.strip() or name in seen:
            raise ConfigError(f"processes[{i}].name must be unique and non-empty")
        if not isinstance(command, list) or not command or not all(isinstance(x, str) and x for x in command):
            raise ConfigError(f"processes[{i}].command must be a non-empty string array")
        cwd_raw = item.get("cwd", ".")
        if not isinstance(cwd_raw, str):
            raise ConfigError(f"processes[{i}].cwd must be a string")
        cwd = (base / cwd_raw).resolve()
        if not cwd.is_dir():
            raise ConfigError(f"Working directory does not exist for {name}: {cwd}")
        env_raw = item.get("env", {})
        if not isinstance(env_raw, dict) or not all(isinstance(k, str) and isinstance(v, str) for k, v in env_raw.items()):
            raise ConfigError(f"processes[{i}].env must contain string keys and values")
        ready_after = item.get("ready_after", 0)
        if not isinstance(ready_after, (int, float)) or isinstance(ready_after, bool) or ready_after < 0 or ready_after > 300:
            raise ConfigError(f"processes[{i}].ready_after must be between 0 and 300 seconds")
        optional = item.get("optional", False)
        if not isinstance(optional, bool):
            raise ConfigError(f"processes[{i}].optional must be boolean")
        specs.append(ProcessSpec(name.strip(), tuple(command), cwd, dict(env_raw), float(ready_after), optional))
        seen.add(name)
    return specs


@dataclass
class RunningProcess:
    spec: ProcessSpec
    process: subprocess.Popen[str]
    log: IO[str]


class Launcher:
    """Start, supervise and stop a configured local development stack."""

    def __init__(self, specs: list[ProcessSpec], log_dir: str | Path = ".dev-logs") -> None:
        if not specs:
            raise ValueError("At least one process is required")
        self.specs = specs
        self.log_dir = Path(log_dir)
        self.running: list[RunningProcess] = []

    def start(self) -> None:
        self.log_dir.mkdir(parents=True, exist_ok=True)
        try:
            for spec in self.specs:
                log = (self.log_dir / f"{spec.name}.log").open("a", encoding="utf-8")
                env = os.environ.copy()
                env.update(spec.env)
                try:
                    proc = subprocess.Popen(list(spec.command), cwd=spec.cwd, env=env, stdout=log, stderr=subprocess.STDOUT, text=True, shell=False)
                except OSError as exc:
                    log.close()
                    if spec.optional:
                        continue
                    raise RuntimeError(f"Failed to start {spec.name}: {exc}") from exc
                running = RunningProcess(spec, proc, log)
                self.running.append(running)
                if spec.ready_after:
                    time.sleep(spec.ready_after)
                    if proc.poll() is not None and not spec.optional:
                        raise RuntimeError(f"{spec.name} exited during startup with code {proc.returncode}")
        except Exception:
            self.stop()
            raise

    def status(self) -> list[dict[str, Any]]:
        return [{"name": r.spec.name, "pid": r.process.pid, "running": r.process.poll() is None, "returncode": r.process.poll()} for r in self.running]

    def wait(self, poll_interval: float = 0.25) -> int:
        while self.running:
            for running in self.running:
                code = running.process.poll()
                if code is not None and code != 0 and not running.spec.optional:
                    return code
            if all(r.process.poll() is not None for r in self.running):
                return 0
            time.sleep(poll_interval)
        return 0

    def stop(self, timeout: float = 5.0) -> None:
        active = [r for r in reversed(self.running) if r.process.poll() is None]
        for running in active:
            try:
                if os.name == "nt":
                    running.process.terminate()
                else:
                    running.process.send_signal(signal.SIGTERM)
            except OSError:
                pass
        deadline = time.monotonic() + timeout
        for running in active:
            remaining = max(0.0, deadline - time.monotonic())
            try:
                running.process.wait(timeout=remaining)
            except subprocess.TimeoutExpired:
                running.process.kill()
                running.process.wait()
        for running in self.running:
            running.log.close()
        self.running.clear()

    def __enter__(self) -> "Launcher":
        self.start()
        return self

    def __exit__(self, *_: object) -> None:
        self.stop()
