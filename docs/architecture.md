# Architecture

Mexico Traffic Monitor is organized around a small desktop shell and pluggable traffic data providers.

## Layers

- `app.py`: application entry point and Qt event loop.
- `ui.py`: main window, controls, refresh timer, and visual rendering.
- `providers.py`: data-provider contracts and implementations.
- `models.py`: typed domain models for incidents and severity.
- `config.py`: runtime settings.

## Provider model

Every provider implements `TrafficProvider.fetch_incidents()` and returns a list of `TrafficIncident` objects. This keeps the UI independent from the source of the data.

## MVP provider strategy

The repo starts with `DemoTrafficProvider`, which lets the interface run without API keys. Real providers can be added without changing the UI if they return the same model.

## Windows packaging

The app is designed to package with PyInstaller. Keep runtime assets local and avoid relying on shell-specific behavior in the entry point.
