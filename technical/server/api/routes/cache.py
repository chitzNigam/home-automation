from __future__ import annotations

from flask import Blueprint, current_app, jsonify, request

cache_bp = Blueprint("cache", __name__)


@cache_bp.post("/api/tenants/<tenant_id>/temp")
def store_temp_data(tenant_id: str):
    data = request.get_json(silent=True) or {}
    key = data.get("key")
    value = data.get("value")
    if not key or value is None:
        return jsonify({"error": "Missing 'key' or 'value'"}), 400

    services = current_app.config["services"]
    services.redis.set_value(tenant_id, str(key), str(value))
    return jsonify({"status": "stored", "tenant_id": tenant_id, "key": key, "value": value}), 200


@cache_bp.get("/api/tenants/<tenant_id>/temp/<key>")
def get_temp_data(tenant_id: str, key: str):
    services = current_app.config["services"]
    value = services.redis.get_value(tenant_id, key)
    if value is None:
        return jsonify({"status": "not found"}), 404
    return jsonify({"tenant_id": tenant_id, "key": key, "value": value}), 200


# Backward compatibility endpoints using DEFAULT_TENANT
@cache_bp.post("/api/temp")
def store_temp_data_default_tenant():
    services = current_app.config["services"]
    tenant = services.config.default_tenant
    data = request.get_json(silent=True) or {}
    key = data.get("key")
    value = data.get("value")
    if not key or value is None:
        return jsonify({"error": "Missing 'key' or 'value'"}), 400

    services.redis.set_value(tenant, str(key), str(value))
    return jsonify({"status": "stored", "tenant_id": tenant, "key": key, "value": value}), 200


@cache_bp.get("/api/temp/<key>")
def get_temp_data_default_tenant(key: str):
    services = current_app.config["services"]
    tenant = services.config.default_tenant
    value = services.redis.get_value(tenant, key)
    if value is None:
        return jsonify({"status": "not found"}), 404
    return jsonify({"tenant_id": tenant, "key": key, "value": value}), 200
