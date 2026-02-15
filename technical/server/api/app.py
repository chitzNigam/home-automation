from __future__ import annotations

from flask import Flask

from container import build_container
from routes import register_routes


def create_app() -> Flask:
    app = Flask(__name__)
    services = build_container()
    register_routes(app, services)
    return app
