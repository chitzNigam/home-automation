#pragma once

#include "IMqttHandler.h"
#include <vector>

class MqttRouter {
public:
    void registerHandler(IMqttHandler *handler) { handlers.push_back(handler); }

    void dispatch(const char *topic, const uint8_t *payload, size_t length) {
        for (auto *h : handlers) {
            if (strcmp(topic, h->topic()) == 0) {
                h->handle(payload, length);
                return;
            }
        }
    }

private:
    std::vector<IMqttHandler *> handlers;
};
