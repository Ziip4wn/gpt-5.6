from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path
from threading import Lock
from typing import Any


class TraceWriter:
    def __init__(self, directory: Path, enabled: bool = True) -> None:
        self.directory = directory
        self.enabled = enabled
        self._lock = Lock()

    def write(self, run_id: str, event: str, **payload: Any) -> None:
        if not self.enabled:
            return
        self.directory.mkdir(parents=True, exist_ok=True)
        record = {
            "timestamp": datetime.now(UTC).isoformat(),
            "run_id": run_id,
            "event": event,
            **payload,
        }
        line = json.dumps(record, ensure_ascii=False, default=str)
        with self._lock, (self.directory / f"{run_id}.jsonl").open(
            "a", encoding="utf-8"
        ) as stream:
            stream.write(line + "\n")

