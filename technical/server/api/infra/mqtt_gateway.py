from __future__ import annotations

import json
import ssl

import paho.mqtt.client as mqtt

from config import AppConfig


class MqttGateway:
    def __init__(self, config: AppConfig) -> None:
        self._config = config
        self._client = mqtt.Client()
        self._connected = False
        self._setup_auth()
        self._setup_tls()
        self._client.on_connect = self._on_connect
        self._client.on_disconnect = self._on_disconnect
        self._client.reconnect_delay_set(min_delay=1, max_delay=15)

    def _setup_auth(self) -> None:
        if self._config.mqtt_username:
            self._client.username_pw_set(
                self._config.mqtt_username,
                self._config.mqtt_password,
            )

    def _setup_tls(self) -> None:
        if not self._config.mqtt_tls:
            return

        self._client.tls_set(
            ca_certs=self._config.mqtt_ca,
            certfile=self._config.mqtt_cert,
            keyfile=self._config.mqtt_key,
            tls_version=ssl.PROTOCOL_TLSv1_2,
        )

    def _on_connect(self, client, userdata, flags, rc) -> None:
        self._connected = rc == 0

    def _on_disconnect(self, client, userdata, rc) -> None:
        self._connected = False

    def connect(self) -> None:
        self._client.connect(self._config.mqtt_broker, self._config.mqtt_port, keepalive=60)
        self._client.loop_start()

    def is_connected(self) -> bool:
        return self._connected

    def publish(self, topic: str, payload: dict | str, qos: int = 1, retain: bool = False) -> bool:
        message = payload if isinstance(payload, str) else json.dumps(payload)
        result = self._client.publish(topic, message, qos=qos, retain=retain)
        return result.rc == mqtt.MQTT_ERR_SUCCESS
