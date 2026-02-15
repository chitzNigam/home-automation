from __future__ import annotations

import os
from dataclasses import dataclass


def _as_bool(value: str | None, default: bool = False) -> bool:
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


@dataclass(frozen=True)
class AppConfig:
    postgres_host: str
    postgres_port: int
    postgres_db: str
    postgres_user: str
    postgres_password: str
    redis_host: str
    redis_port: int
    mqtt_broker: str
    mqtt_port: int
    mqtt_tls: bool
    mqtt_username: str
    mqtt_password: str
    mqtt_ca: str
    mqtt_cert: str | None
    mqtt_key: str | None
    default_tenant: str

    @staticmethod
    def from_env() -> "AppConfig":
        return AppConfig(
            postgres_host=os.getenv("POSTGRES_HOST", "postgres"),
            postgres_port=int(os.getenv("POSTGRES_PORT", "5432")),
            postgres_db=os.getenv("POSTGRES_DB", "home_automation"),
            postgres_user=os.getenv("POSTGRES_USER", "espuser"),
            postgres_password=os.getenv("POSTGRES_PASSWORD", ""),
            redis_host=os.getenv("REDIS_HOST", "redis"),
            redis_port=int(os.getenv("REDIS_PORT", "6379")),
            mqtt_broker=os.getenv("MQTT_BROKER", "mosquitto"),
            mqtt_port=int(os.getenv("MQTT_PORT", "8883")),
            mqtt_tls=_as_bool(os.getenv("MQTT_TLS"), default=True),
            mqtt_username=os.getenv("MQTT_USERNAME", ""),
            mqtt_password=os.getenv("MQTT_PASSWORD", ""),
            mqtt_ca=os.getenv("MQTT_CA", "/mosquitto/certs/ca.crt"),
            mqtt_cert=os.getenv("MQTT_CERT"),
            mqtt_key=os.getenv("MQTT_KEY"),
            default_tenant=os.getenv("DEFAULT_TENANT", "tenant1"),
        )
