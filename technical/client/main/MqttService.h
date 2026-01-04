#pragma once

#include "MqttRouter.h"
#include "config.h"
#include "log.h"
#include <ESP8266WiFi.h>
#include <PubSubClient.h>

class MqttService {
public:
    explicit MqttService(MqttRouter &router);

    void begin();
    void loop();
    void subscribe(const char *topic);
    void registerTopic(const char *topic);

private:
    void reconnect();

    // Static MQTT callback (NO lambda)
    static void mqttCallback(char *topic, uint8_t *payload, unsigned int len);

private:
    static MqttService *instance;

    WiFiClientSecure secureClient;
    PubSubClient client;
    MqttRouter &router;

    // Fixed-size topic list (NO std::vector)
    static constexpr uint8_t MAX_TOPICS = 4;
    const char *topics[MAX_TOPICS];
    uint8_t topicCount = 0;
};
