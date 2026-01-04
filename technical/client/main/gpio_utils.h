#pragma once
#include <Arduino.h>

namespace gpio {

inline bool isValid(uint8_t pin) {
    switch (pin) {
    // Safe GPIOs
    case 4:
    case 5:
    case 12:
    case 13:
    case 14:
    case 16:
        return true;

    // Boot-sensitive GPIOs (allowed but risky)
    case 0:
    case 2:
    case 15:
        return true;

    default:
        return false;
    }
}

inline bool isBootCritical(uint8_t pin) {
    return (pin == 0 || pin == 2 || pin == 15);
}

} // namespace gpio
