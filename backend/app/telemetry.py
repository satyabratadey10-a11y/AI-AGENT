from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone


@dataclass
class TelemetryEvent:
    event_name: str
    timestamp: str
    metadata: dict


class TelemetryCollector:
    def __init__(self) -> None:
        self.events: list[TelemetryEvent] = []

    def emit(self, event_name: str, metadata: dict) -> None:
        self.events.append(
            TelemetryEvent(
                event_name=event_name,
                timestamp=datetime.now(timezone.utc).isoformat(),
                metadata=metadata,
            )
        )
