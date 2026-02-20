from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import datetime
from typing import Optional


LEVELS = ["DEBUG", "INFO", "WARNING", "WARN", "ERROR", "CRITICAL", "FATAL"]
LEVEL_NORMALIZE = {
    "WARN": "WARNING",
    "FATAL": "CRITICAL",
}

# Format 1: 2026-02-20 07:18:12 [INFO] [module] message
RE_FMT1 = re.compile(
    r"^(?P<ts>\d{4}-\d{2}-\d{2}[ T]\d{2}:\d{2}:\d{2})\s+\[(?P<lvl>[A-Z]+)\]\s+\[(?P<mod>[^\]]+)\]\s+(?P<msg>.*)$"
)

# Format 2: 2026-02-20T07:18:12Z INFO module: message
RE_FMT2 = re.compile(
    r"^(?P<ts>\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?Z?)\s+(?P<lvl>[A-Z]+)\s+(?P<mod>[^:]+):\s*(?P<msg>.*)$"
)

# Format 3 (fallback): ... ERROR ... message
RE_LEVEL_ANYWHERE = re.compile(r"\b(?P<lvl>DEBUG|INFO|WARNING|WARN|ERROR|CRITICAL|FATAL)\b")


@dataclass(frozen=True)
class LogEntry:
    raw: str
    timestamp: Optional[datetime]
    level: str
    module: str
    message: str


def _parse_timestamp(ts: str) -> Optional[datetime]:
    # Best effort parsing (no timezone handling here)
    ts = ts.strip().replace("T", " ")
    ts = ts.rstrip("Z")
    for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%d %H:%M:%S.%f"):
        try:
            return datetime.strptime(ts, fmt)
        except ValueError:
            continue
    return None


def normalize_level(level: str) -> str:
    level = (level or "UNKNOWN").upper()
    return LEVEL_NORMALIZE.get(level, level)


def parse_line(line: str) -> LogEntry:
    line = line.rstrip("\n")
    if not line.strip():
        return LogEntry(raw=line, timestamp=None, level="EMPTY", module="", message="")

    m = RE_FMT1.match(line)
    if m:
        ts = _parse_timestamp(m.group("ts"))
        lvl = normalize_level(m.group("lvl"))
        mod = m.group("mod").strip()
        msg = m.group("msg").strip()
        return LogEntry(raw=line, timestamp=ts, level=lvl, module=mod, message=msg)

    m = RE_FMT2.match(line)
    if m:
        ts = _parse_timestamp(m.group("ts"))
        lvl = normalize_level(m.group("lvl"))
        mod = m.group("mod").strip()
        msg = m.group("msg").strip()
        return LogEntry(raw=line, timestamp=ts, level=lvl, module=mod, message=msg)

    # fallback: find level anywhere, keep rest as message
    m = RE_LEVEL_ANYWHERE.search(line)
    lvl = normalize_level(m.group("lvl")) if m else "UNKNOWN"
    return LogEntry(raw=line, timestamp=None, level=lvl, module="", message=line.strip())
