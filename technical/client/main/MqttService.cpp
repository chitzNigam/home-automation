#include "MqttService.h"

MqttService *MqttService::instance = nullptr;

MqttService::MqttService(MqttRouter &router)
    : router(router), client(secureClient) {}

void ICACHE_FLASH_ATTR MqttService::begin() {
    instance = this;

    secureClient.setFingerprint(mqttConfig.fingerprint);
    client.setServer(mqttConfig.server, mqttConfig.port);
    client.setCallback(mqttCallback);
}

void ICACHE_FLASH_ATTR MqttService::loop() {
    if (!client.connected()) {
        reconnect();
    }
    client.loop();
}

void ICACHE_FLASH_ATTR MqttService::subscribe(const char *topic) {
    client.subscribe(topic);
}

void ICACHE_FLASH_ATTR MqttService::registerTopic(const char *topic) {
    if (topicCount < MAX_TOPICS) {
        topics[topicCount++] = topic;
    }
}

void ICACHE_FLASH_ATTR MqttService::reconnect() {
    if (!WiFi.isConnected())
        return;

    if (client.connect(mqttConfig.clientId, mqttConfig.username,
                       mqttConfig.password)) {

        LOGI("MQTT connected");

        for (uint8_t i = 0; i < topicCount; i++) {
            client.subscribe(topics[i]);
        }
    } else {
        LOGE("MQTT failed rc=%d", client.state());
    }
}

void ICACHE_FLASH_ATTR MqttService::mqttCallback(char *topic, uint8_t *payload,
                                                 unsigned int len) {

    if (instance) {
        instance->router.dispatch(topic, payload, len);
    }
}
