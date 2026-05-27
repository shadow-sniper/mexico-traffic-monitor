from __future__ import annotations

from abc import ABC, abstractmethod
import math
import random
from typing import Any

import requests

from mexico_traffic_monitor.models import Severity, TrafficIncident, utc_now


class TrafficProvider(ABC):
    @abstractmethod
    def fetch_incidents(self) -> list[TrafficIncident]:
        """Return the latest traffic incidents."""


class DemoTrafficProvider(TrafficProvider):
    def __init__(self) -> None:
        self._tick = 0
        self._locations = [
            ("periferico-sur", "Periferico Sur", "Mexico City", 19.3028, -99.1881),
            ("viaducto", "Viaducto Miguel Aleman", "Mexico City", 19.4018, -99.1587),
            ("reforma", "Paseo de la Reforma", "Mexico City", 19.4270, -99.1677),
            ("insurgentes", "Insurgentes Norte", "Mexico City", 19.4537, -99.1455),
            ("circuito", "Circuito Interior", "Mexico City", 19.4361, -99.1136),
        ]

    def fetch_incidents(self) -> list[TrafficIncident]:
        self._tick += 1
        now = utc_now()
        incidents: list[TrafficIncident] = []

        for index, (slug, title, city, lat, lon) in enumerate(self._locations):
            wave = math.sin((self._tick + index) / 2)
            jitter = random.randint(-6, 6)
            congestion = max(10, min(98, int(55 + wave * 28 + jitter)))
            severity = self._severity_for(congestion)
            incidents.append(
                TrafficIncident(
                    id=slug,
                    title=title,
                    city=city,
                    latitude=lat,
                    longitude=lon,
                    severity=severity,
                    congestion_level=congestion,
                    description=self._description_for(congestion),
                    updated_at=now,
                )
            )

        return sorted(incidents, key=lambda incident: incident.congestion_level, reverse=True)

    @staticmethod
    def _severity_for(congestion: int) -> Severity:
        if congestion >= 90:
            return Severity.CRITICAL
        if congestion >= 75:
            return Severity.HIGH
        if congestion >= 45:
            return Severity.MEDIUM
        return Severity.LOW

    @staticmethod
    def _description_for(congestion: int) -> str:
        if congestion >= 90:
            return "Severe congestion. Consider alternate routes."
        if congestion >= 75:
            return "Heavy traffic with slow movement."
        if congestion >= 45:
            return "Moderate traffic flow."
        return "Traffic moving normally."


class HttpJsonTrafficProvider(TrafficProvider):
    """Adapter for APIs that return a list of traffic incident JSON objects."""

    def __init__(self, url: str, timeout_seconds: float = 8.0) -> None:
        self._url = url
        self._timeout_seconds = timeout_seconds

    def fetch_incidents(self) -> list[TrafficIncident]:
        response = requests.get(self._url, timeout=self._timeout_seconds)
        response.raise_for_status()
        payload = response.json()

        if not isinstance(payload, list):
            raise ValueError("Traffic provider response must be a list")

        return [self._incident_from_json(item) for item in payload]

    @staticmethod
    def _incident_from_json(item: dict[str, Any]) -> TrafficIncident:
        return TrafficIncident(
            id=str(item["id"]),
            title=str(item["title"]),
            city=str(item.get("city", "Mexico")),
            latitude=float(item["latitude"]),
            longitude=float(item["longitude"]),
            severity=Severity(str(item.get("severity", Severity.MEDIUM.value)).lower()),
            congestion_level=int(item.get("congestion_level", 50)),
            description=str(item.get("description", "Traffic incident")),
            updated_at=utc_now(),
        )
