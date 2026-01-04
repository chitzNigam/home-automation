#pragma once
#include "secrets.h"

#include <Arduino.h>

struct MqttConfig {
    const char *server;
    uint16_t port;
    const char *username;
    const char *password;
    const char *clientId;
    const char *fingerprint;
};

inline MqttConfig mqttConfig{.server = MQTT_SERVER,
                             .port = MQTT_PORT,
                             .username = MQTT_USER,
                             .password = MQTT_PASS,
                             .clientId = MQTT_CLIENT_ID,
                             .fingerprint = MQTT_FINGERPRINT};
