from __future__ import annotations

import sys

from PySide6.QtWidgets import QApplication

from mexico_traffic_monitor.config import AppSettings
from mexico_traffic_monitor.providers import DemoTrafficProvider, HttpJsonTrafficProvider, TrafficProvider
from mexico_traffic_monitor.ui import MainWindow


def build_provider(settings: AppSettings) -> TrafficProvider:
    if settings.provider_url:
        return HttpJsonTrafficProvider(settings.provider_url)
    return DemoTrafficProvider()


def main() -> int:
    settings = AppSettings.from_environment()
    app = QApplication(sys.argv)
    app.setApplicationName(settings.app_name)

    window = MainWindow(settings=settings, provider=build_provider(settings))
    window.resize(1120, 720)
    window.show()

    return app.exec()
