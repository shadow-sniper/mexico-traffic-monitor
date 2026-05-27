from __future__ import annotations

from collections.abc import Iterable

from PySide6.QtCore import QPointF, Qt, QTimer
from PySide6.QtGui import QColor, QPainter, QPen
from PySide6.QtWidgets import (
    QFrame,
    QGraphicsEllipseItem,
    QGraphicsScene,
    QGraphicsTextItem,
    QGraphicsView,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QMainWindow,
    QPushButton,
    QSplitter,
    QStatusBar,
    QVBoxLayout,
    QWidget,
)

from mexico_traffic_monitor.config import AppSettings
from mexico_traffic_monitor.models import Severity, TrafficIncident
from mexico_traffic_monitor.providers import TrafficProvider


SEVERITY_COLORS = {
    Severity.LOW: QColor("#1d9a6c"),
    Severity.MEDIUM: QColor("#d99a22"),
    Severity.HIGH: QColor("#d95c22"),
    Severity.CRITICAL: QColor("#c92a3a"),
}


class TrafficMapView(QGraphicsView):
    def __init__(self) -> None:
        super().__init__()
        self._scene = QGraphicsScene(self)
        self.setScene(self._scene)
        self.setRenderHint(QPainter.RenderHint.Antialiasing)
        self.setFrameShape(QFrame.Shape.NoFrame)
        self.setMinimumWidth(600)
        self.setStyleSheet("background: #eef2f3;")

    def render_incidents(self, incidents: Iterable[TrafficIncident]) -> None:
        self._scene.clear()
        self._draw_base_map()
        for incident in incidents:
            point = self._project(incident.latitude, incident.longitude)
            self._draw_incident(point, incident)

    def _draw_base_map(self) -> None:
        self._scene.setSceneRect(0, 0, 720, 560)
        self._scene.addRect(0, 0, 720, 560, QPen(Qt.PenStyle.NoPen), QColor("#eef2f3"))

        road_pen = QPen(QColor("#9aa8ad"), 5)
        road_pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        self._scene.addLine(90, 110, 650, 450, road_pen)
        self._scene.addLine(130, 455, 590, 105, road_pen)
        self._scene.addLine(60, 280, 680, 280, road_pen)
        self._scene.addLine(360, 55, 360, 510, road_pen)

        label = self._scene.addText("Mexico City traffic overview")
        label.setDefaultTextColor(QColor("#203238"))
        label.setPos(24, 18)

    def _draw_incident(self, point: QPointF, incident: TrafficIncident) -> None:
        color = SEVERITY_COLORS[incident.severity]
        radius = 10 + incident.congestion_level / 10
        marker = QGraphicsEllipseItem(point.x() - radius, point.y() - radius, radius * 2, radius * 2)
        marker.setBrush(color)
        marker.setPen(QPen(QColor("#ffffff"), 3))
        marker.setToolTip(f"{incident.title}: {incident.congestion_level}%")
        self._scene.addItem(marker)

        text = QGraphicsTextItem(f"{incident.congestion_level}%")
        text.setDefaultTextColor(QColor("#182226"))
        text.setPos(point.x() + radius + 4, point.y() - 12)
        self._scene.addItem(text)

    @staticmethod
    def _project(latitude: float, longitude: float) -> QPointF:
        min_lat, max_lat = 19.25, 19.55
        min_lon, max_lon = -99.25, -99.05
        x = (longitude - min_lon) / (max_lon - min_lon) * 620 + 50
        y = (1 - (latitude - min_lat) / (max_lat - min_lat)) * 460 + 50
        return QPointF(max(35, min(685, x)), max(35, min(525, y)))


class MainWindow(QMainWindow):
    def __init__(self, settings: AppSettings, provider: TrafficProvider) -> None:
        super().__init__()
        self._settings = settings
        self._provider = provider
        self._timer = QTimer(self)
        self._timer.timeout.connect(self.refresh)

        self.setWindowTitle(settings.app_name)
        self.setStatusBar(QStatusBar())
        self._map = TrafficMapView()
        self._list = QListWidget()
        self._updated_label = QLabel("Waiting for traffic data")
        self._refresh_button = QPushButton("Refresh")
        self._refresh_button.clicked.connect(self.refresh)

        self._build_layout()
        self._timer.start(settings.refresh_seconds * 1000)
        self.refresh()

    def _build_layout(self) -> None:
        root = QWidget()
        layout = QVBoxLayout(root)

        header = QHBoxLayout()
        title = QLabel("Mexico Traffic Monitor")
        title.setStyleSheet("font-size: 24px; font-weight: 700; color: #182226;")
        subtitle = QLabel("Real-time desktop monitoring MVP")
        subtitle.setStyleSheet("color: #53676f;")

        title_group = QVBoxLayout()
        title_group.addWidget(title)
        title_group.addWidget(subtitle)
        header.addLayout(title_group)
        header.addStretch(1)
        header.addWidget(self._updated_label)
        header.addWidget(self._refresh_button)

        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.addWidget(self._map)
        splitter.addWidget(self._list)
        splitter.setStretchFactor(0, 3)
        splitter.setStretchFactor(1, 1)

        layout.addLayout(header)
        layout.addWidget(splitter)
        self.setCentralWidget(root)

    def refresh(self) -> None:
        try:
            incidents = self._provider.fetch_incidents()
        except Exception as exc:  # pragma: no cover - UI status path
            self.statusBar().showMessage(f"Failed to refresh traffic data: {exc}", 8000)
            return

        self._map.render_incidents(incidents)
        self._list.clear()

        for incident in incidents:
            item = QListWidgetItem(
                f"{incident.title}\n{incident.city} | {incident.congestion_level}% | {incident.severity.value}\n{incident.description}"
            )
            item.setToolTip(f"Updated at {incident.updated_label}")
            self._list.addItem(item)

        if incidents:
            self._updated_label.setText(f"Updated {incidents[0].updated_label}")
        self.statusBar().showMessage(f"Loaded {len(incidents)} traffic points", 3000)
