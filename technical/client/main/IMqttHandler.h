#pragma once

#include <Arduino.h>

class IMqttHandler {
public:
    virtual ~IMqttHandler() = default;
    virtual const char *topic() const = 0;
    virtual void handle(const uint8_t *payload, size_t length) = 0;
};
