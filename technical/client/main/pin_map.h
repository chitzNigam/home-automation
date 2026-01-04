#pragma once
#include <Arduino.h>

struct PinAlias {
    const char *name;
    uint8_t gpio;
};

// ESP8266 NodeMCU pin mapping
constexpr PinAlias PIN_MAP[] = {{"D0", 16}, {"D1", 5},  {"D2", 4},
                                {"D3", 0},  {"D4", 2},  {"D5", 14},
                                {"D6", 12}, {"D7", 13}, {"D8", 15}};

constexpr size_t PIN_MAP_SIZE = sizeof(PIN_MAP) / sizeof(PIN_MAP[0]);
