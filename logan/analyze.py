from __future__ import annotations

import re
from collections import Counter
from dataclasses import dataclass
from datetime import datetime
from typing import Iterable, Optional

from .parser import LogEntry


@dataclass(frozen=True)
class AnalysisResult:
    total_lines: int
    parsed_with_timestamp: int
    unknown_level: int
    empty_lines: int
    level_counts: dict[str, int]
    top_modules: list[tuple[str, int]]
    top_error_messages: list[tuple[str, int]]
    time_start: Optional[str]
    time_end: Optional[str]
    error_rate: float


def _normalize_message(msg: str) -> str:
    """
    Normalize to group similar messages:
    - replace numbers/hex IDs with <N>/<HEX>
    - trim extra spaces
    """
    s = msg.strip()
    s = re.sub(r"\b0x[0-9a-fA-F]+\b", "<HEX>", s)
    s = re.sub(r"\b\d+\b", "<N>", s)
    s = re.sub(r"\s+", " ", s)
    return s


def analyze(entries: Iterable[LogEntry], top_n: int = 10) -> AnalysisResult:
    entries = list(entries)
    total = len(entries)

    level_counter = Counter(e.level for e in entries)
    modules = Counter(e.module for e in entries if e.module)
    unknown_level = sum(1 for e in entries if e.level == "UNKNOWN")
    empty_lines = sum(1 for e in entries if e.level == "EMPTY")

    ts_list = sorted([e.timestamp for e in entries if isinstance(e.timestamp, datetime)])
    parsed_with_ts = len(ts_list)

    time_start = ts_list[0].isoformat(sep=" ") if ts_list else None
    time_end = ts_list[-1].isoformat(sep=" ") if ts_list else None

    # Errors (ERROR/CRITICAL)
    err_entries = [e for e in entries if e.level in ("ERROR", "CRITICAL")]
    err_msgs = Counter(_normalize_message(e.message) for e in err_entries if e.message)

    error_rate = (len(err_entries) / total) if total else 0.0

    return AnalysisResult(
        total_lines=total,
        parsed_with_timestamp=parsed_with_ts,
        unknown_level=unknown_level,
        empty_lines=empty_lines,
        level_counts=dict(level_counter),
        top_modules=modules.most_common(top_n),
        top_error_messages=err_msgs.most_common(top_n),
        time_start=time_start,
        time_end=time_end,
        error_rate=round(error_rate, 6),
    )
