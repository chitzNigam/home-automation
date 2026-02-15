from __future__ import annotations

import redis

from config import AppConfig


class RedisStore:
    def __init__(self, config: AppConfig) -> None:
        self._client = redis.Redis(
            host=config.redis_host,
            port=config.redis_port,
            decode_responses=True,
        )

    @staticmethod
    def _tenant_key(tenant_id: str, key: str) -> str:
        return f"tenants:{tenant_id}:temp:{key}"

    def ping(self) -> bool:
        try:
            self._client.ping()
            return True
        except Exception:
            return False

    def set_value(self, tenant_id: str, key: str, value: str) -> None:
        self._client.set(self._tenant_key(tenant_id, key), value)

    def get_value(self, tenant_id: str, key: str) -> str | None:
        return self._client.get(self._tenant_key(tenant_id, key))
