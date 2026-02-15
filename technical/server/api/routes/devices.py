from __future__ import annotations

from flask import Blueprint, current_app, jsonify, request

from topics import tenant_command_topic, tenant_event_topic, tenant_state_topic

devices_bp = Blueprint("devices", __name__)


def _missing(*values: str) -> bool:
    return any(not str(v).strip() for v in values)


@devices_bp.post("/api/tenants/<tenant_id>/devices/<device_id>/state")
def save_device_state(tenant_id: str, device_id: str):
    data = request.get_json(silent=True) or {}
    state = data.get("state")
    if _missing(tenant_id, device_id, state):
        return jsonify({"error": "tenant_id, device_id, and state are required"}), 400

    services = current_app.config["services"]
    row = services.postgres.save_state(tenant_id, device_id, str(state), source="api")
    created_at = row["created_at"].isoformat()

    publish_ok = services.mqtt.publish(
        tenant_state_topic(tenant_id, device_id),
        {
            "tenant_id": tenant_id,
            "device_id": device_id,
            "state": state,
            "source": "api",
            "created_at": created_at,
        },
        qos=1,
    )

    row["created_at"] = created_at
    return jsonify({"stored": row, "mqtt_published": publish_ok}), 201


@devices_bp.get("/api/tenants/<tenant_id>/devices/<device_id>/state")
def get_device_state(tenant_id: str, device_id: str):
    services = current_app.config["services"]
    row = services.postgres.latest_state(tenant_id, device_id)
    if not row:
        return jsonify({"error": "state not found"}), 404

    row["created_at"] = row["created_at"].isoformat()
    return jsonify(row), 200


@devices_bp.post("/api/tenants/<tenant_id>/devices/<device_id>/commands/<command>")
def send_device_command(tenant_id: str, device_id: str, command: str):
    data = request.get_json(silent=True) or {}
    payload = data.get("payload", {})

    if _missing(tenant_id, device_id, command):
        return jsonify({"error": "tenant_id, device_id, and command are required"}), 400

    services = current_app.config["services"]
    topic = tenant_command_topic(tenant_id, device_id, command)
    ok = services.mqtt.publish(
        topic,
        {
            "tenant_id": tenant_id,
            "device_id": device_id,
            "command": command,
            "payload": payload,
        },
        qos=1,
    )
    return jsonify({"status": "sent" if ok else "failed", "topic": topic}), (200 if ok else 502)


@devices_bp.post("/api/tenants/<tenant_id>/devices/<device_id>/events/<event_name>")
def publish_device_event(tenant_id: str, device_id: str, event_name: str):
    data = request.get_json(silent=True) or {}
    payload = data.get("payload", {})

    services = current_app.config["services"]
    topic = tenant_event_topic(tenant_id, device_id, event_name)
    ok = services.mqtt.publish(topic, payload, qos=1)
    return jsonify({"status": "sent" if ok else "failed", "topic": topic}), (200 if ok else 502)


@devices_bp.post("/api/state")
def save_state_default_tenant():
    data = request.get_json(silent=True) or {}
    state = data.get("state")
    device_id = data.get("device_id", "device1")
    services = current_app.config["services"]
    tenant_id = data.get("tenant_id", services.config.default_tenant)

    if _missing(tenant_id, device_id, state):
        return jsonify({"error": "tenant_id, device_id, and state are required"}), 400

    row = services.postgres.save_state(tenant_id, device_id, str(state), source="api")
    row["created_at"] = row["created_at"].isoformat()
    return jsonify({"status": "stored", "record": row}), 201


@devices_bp.get("/api/state")
def get_state_default_tenant():
    services = current_app.config["services"]
    tenant_id = request.args.get("tenant_id", services.config.default_tenant)
    device_id = request.args.get("device_id", "device1")

    row = services.postgres.latest_state(tenant_id, device_id)
    if not row:
        return jsonify({"error": "state not found"}), 404

    row["created_at"] = row["created_at"].isoformat()
    return jsonify(row), 200


# Backward compatibility endpoint
@devices_bp.post("/api/send")
def send_raw_topic_message():
    data = request.get_json(silent=True) or {}
    topic = data.get("topic")
    message = data.get("message")
    if _missing(topic, message):
        return jsonify({"error": "Missing topic or message"}), 400

    services = current_app.config["services"]
    ok = services.mqtt.publish(str(topic), str(message), qos=1)
    return jsonify({"status": "sent" if ok else "failed", "topic": topic, "message": message}), (200 if ok else 502)
