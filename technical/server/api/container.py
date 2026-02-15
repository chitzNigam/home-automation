from __future__ import annotations

from dataclasses import dataclass

from config import AppConfig
from infra.mqtt_gateway import MqttGateway
from infra.postgres_store import PostgresStore
from infra.redis_store import RedisStore


@dataclass(frozen=True)
class ServiceContainer:
    config: AppConfig
    postgres: PostgresStore
    redis: RedisStore
    mqtt: MqttGateway


def build_container() -> ServiceContainer:
    config = AppConfig.from_env()
    postgres = PostgresStore(config)
    redis = RedisStore(config)
    mqtt = MqttGateway(config)

    postgres.ensure_schema()
    mqtt.connect()

    return ServiceContainer(config=config, postgres=postgres, redis=redis, mqtt=mqtt)
