from __future__ import annotations

from typing import Any

import psycopg2
import psycopg2.extras

from config import AppConfig


class PostgresStore:
    def __init__(self, config: AppConfig) -> None:
        self._config = config
        self._conn = None

    def _connect(self) -> None:
        if self._conn and self._conn.closed == 0:
            return

        self._conn = psycopg2.connect(
            host=self._config.postgres_host,
            port=self._config.postgres_port,
            dbname=self._config.postgres_db,
            user=self._config.postgres_user,
            password=self._config.postgres_password,
            cursor_factory=psycopg2.extras.RealDictCursor,
        )
        self._conn.autocommit = True

    def ping(self) -> bool:
        try:
            self._connect()
            with self._conn.cursor() as cur:
                cur.execute("SELECT 1")
                cur.fetchone()
            return True
        except Exception:
            return False

    def ensure_schema(self) -> None:
        self._connect()
        with self._conn.cursor() as cur:
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS tenant_device_state (
                    id SERIAL PRIMARY KEY,
                    tenant_id TEXT NOT NULL,
                    device_id TEXT NOT NULL,
                    state TEXT NOT NULL,
                    source TEXT NOT NULL DEFAULT 'api',
                    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
                );
                """
            )
            cur.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_tenant_device_state_latest
                ON tenant_device_state (tenant_id, device_id, created_at DESC);
                """
            )

    def save_state(
        self, tenant_id: str, device_id: str, state: str, source: str = "api"
    ) -> dict[str, Any]:
        self._connect()
        with self._conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO tenant_device_state (tenant_id, device_id, state, source)
                VALUES (%s, %s, %s, %s)
                RETURNING id, tenant_id, device_id, state, source, created_at;
                """,
                (tenant_id, device_id, state, source),
            )
            row = cur.fetchone()
            return dict(row)

    def latest_state(self, tenant_id: str, device_id: str) -> dict[str, Any] | None:
        self._connect()
        with self._conn.cursor() as cur:
            cur.execute(
                """
                SELECT id, tenant_id, device_id, state, source, created_at
                FROM tenant_device_state
                WHERE tenant_id = %s AND device_id = %s
                ORDER BY created_at DESC
                LIMIT 1;
                """,
                (tenant_id, device_id),
            )
            row = cur.fetchone()
            return dict(row) if row else None
