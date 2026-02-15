from __future__ import annotations


def _clean(value: str) -> str:
    return value.strip().replace(" ", "_")


def tenant_state_topic(tenant_id: str, device_id: str) -> str:
    return f"tenants/{_clean(tenant_id)}/devices/{_clean(device_id)}/state"


def tenant_event_topic(tenant_id: str, device_id: str, event_name: str) -> str:
    return f"tenants/{_clean(tenant_id)}/devices/{_clean(device_id)}/event/{_clean(event_name)}"


def tenant_command_topic(tenant_id: str, device_id: str, command: str) -> str:
    return f"tenants/{_clean(tenant_id)}/devices/{_clean(device_id)}/cmd/{_clean(command)}"
