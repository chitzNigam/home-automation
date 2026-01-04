#pragma once

#define LOG_LEVEL 2
// 0 = no logs (production)
// 1 = info + error
// 2 = debug + info + error

#if LOG_LEVEL > 0
#    include <Arduino.h>
#endif

#if LOG_LEVEL >= 2
#    define LOGD(fmt, ...) Serial.printf_P(PSTR("[D] " fmt "\n"), ##__VA_ARGS__)
#else
#    define LOGD(...)
#endif

#if LOG_LEVEL >= 1
#    define LOGI(fmt, ...) Serial.printf_P(PSTR("[I] " fmt "\n"), ##__VA_ARGS__)
#    define LOGE(fmt, ...) Serial.printf_P(PSTR("[E] " fmt "\n"), ##__VA_ARGS__)
#else
#    define LOGI(...)
#    define LOGE(...)
#endif
