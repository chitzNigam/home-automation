from __future__ import annotations

from flask import Flask

from container import ServiceContainer
from routes.cache import cache_bp
from routes.devices import devices_bp
from routes.health import health_bp


def register_routes(app: Flask, services: ServiceContainer) -> None:
    app.config["services"] = services
    app.register_blueprint(health_bp)
    app.register_blueprint(devices_bp)
    app.register_blueprint(cache_bp)
