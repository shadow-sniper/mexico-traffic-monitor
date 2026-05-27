# Mexico Traffic Monitor

A Windows desktop starter app for real-time traffic monitoring in Mexico. The first version focuses on Mexico City and ships with a demo traffic provider so the UI can run immediately while real data connectors are added.

## Goals

- Show live or near-real-time traffic conditions in a desktop UI.
- Start with Mexico City, then expand to other Mexican cities and highways.
- Support pluggable data providers for official feeds, paid traffic APIs, or internal telemetry.
- Package the app for Windows users.

## Tech stack

- Python 3.11+
- PySide6 for the desktop interface
- `requests` for HTTP data providers
- `pytest` for tests
- PyInstaller for Windows packaging

## Quick start

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -e .[dev]
python -m mexico_traffic_monitor
```

The default app runs with simulated traffic data around Mexico City, so it does not require API keys.

## Data providers

The app uses a provider interface in `src/mexico_traffic_monitor/providers.py`.

Current providers:

- `DemoTrafficProvider`: local simulated traffic for development.
- `HttpJsonTrafficProvider`: starter adapter for a JSON API that returns incident data.

Recommended next connectors:

- TomTom Traffic API
- HERE Traffic API
- Google Maps Platform traffic-related APIs
- Official city or federal open-data feeds when available

## Windows build

After installing dependencies on Windows:

```bash
pip install -e .[dev]
pyinstaller --noconfirm --windowed --name MexicoTrafficMonitor src/mexico_traffic_monitor/__main__.py
```

The packaged app will be generated under `dist/`.

## Project status

This is an MVP scaffold: the desktop app, provider contract, demo data, and packaging path are ready. Real traffic providers should be added behind the existing provider interface.
