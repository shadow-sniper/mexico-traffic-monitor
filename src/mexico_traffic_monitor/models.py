from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum


class Severity(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass(frozen=True)
class TrafficIncident:
    id: str
    title: str
    city: str
    latitude: float
    longitude: float
    severity: Severity
    congestion_level: int
    description: str
    updated_at: datetime

    def __post_init__(self) -> None:
        if not 0 <= self.congestion_level <= 100:
            raise ValueError("congestion_level must be between 0 and 100")

    @property
    def updated_label(self) -> str:
        local_time = self.updated_at.astimezone()
        return local_time.strftime("%H:%M:%S")


def utc_now() -> datetime:
    return datetime.now(timezone.utc)
