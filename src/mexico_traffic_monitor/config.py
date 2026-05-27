from __future__ import annotations

from dataclasses import dataclass
import os


@dataclass(frozen=True)
class AppSettings:
    app_name: str = "Mexico Traffic Monitor"
    refresh_seconds: int = 15
    provider_url: str | None = None

    @classmethod
    def from_environment(cls) -> "AppSettings":
        refresh_seconds = int(os.getenv("TRAFFIC_REFRESH_SECONDS", "15"))
        provider_url = os.getenv("TRAFFIC_PROVIDER_URL") or None
        return cls(refresh_seconds=refresh_seconds, provider_url=provider_url)
