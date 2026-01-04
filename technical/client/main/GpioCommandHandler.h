#pragma once

#include <ArduinoJson.h>

#include "IMqttHandler.h"
#include "gpio_utils.h"
#include "log.h"
#include "pin_map.h"

constexpr uint8_t INVALID_PIN = 255;

class GpioCommandHandler : public IMqttHandler {
public:
    const char *topic() const override { return "device/gpio"; }

    void handle(const uint8_t *payload, size_t length) override {
        StaticJsonDocument<128> doc;
        DeserializationError err = deserializeJson(doc, payload, length);

        if (err) {
            LOGE("GPIO JSON error: %s", err.c_str());
            return;
        }

        if (!doc["pin"] || !doc["status"]) {
            LOGE("GPIO JSON missing fields");
            return;
        }

        uint8_t pin = resolvePin(doc["pin"]);

        if (pin == INVALID_PIN || !gpio::isValid(pin)) {
            LOGE("Invalid or unsupported GPIO");
            return;
        }

        const char *status = doc["status"];

        if (gpio::isBootCritical(pin) && !doc["force"]) {
            LOGE("Refusing boot-critical GPIO without force");
            return;
        }

        if (!strcmp(status, "ON")) {
            digitalWrite(pin, HIGH);
            LOGI("GPIO %d -> ON", pin);
        } else if (!strcmp(status, "OFF")) {
            digitalWrite(pin, LOW);
            LOGI("GPIO %d -> OFF", pin);
        } else {
            LOGE("Invalid GPIO status");
        }
    }

    uint8_t resolvePin(JsonVariant v) {
        // Numeric GPIO directly
        if (v.is<uint8_t>()) {
            return v.as<uint8_t>();
        }

        // Alias string (e.g. "D1")
        if (v.is<const char *>()) {
            const char *name = v.as<const char *>();

            for (size_t i = 0; i < PIN_MAP_SIZE; i++) {
                if (strcmp(PIN_MAP[i].name, name) == 0) {
                    return PIN_MAP[i].gpio;
                }
            }
        }

        return INVALID_PIN;
    }
};
