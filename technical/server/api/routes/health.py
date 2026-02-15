from __future__ import annotations

from flask import Blueprint, current_app, jsonify

health_bp = Blueprint("health", __name__)


@health_bp.get("/api/live")
def live() -> tuple[dict, int]:
    return {"status": "alive"}, 200


@health_bp.get("/api/ready")
def ready() -> tuple[dict, int]:
    services = current_app.config["services"]
    checks = {
        "postgres": services.postgres.ping(),
        "redis": services.redis.ping(),
        "mqtt": services.mqtt.is_connected(),
    }
    ok = all(checks.values())
    return jsonify({"status": "ready" if ok else "degraded", "checks": checks}), (200 if ok else 503)


@health_bp.get("/api/health")
def health() -> tuple[dict, int]:
    return ready()
