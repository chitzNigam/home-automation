#include "wifi_setup.h"
#include "log.h"

#include <WiFiManager.h>

// const char* ssid = "5 Waffle for Wifi";
// const char* password = "ketchup@1234567890";

static WiFiManager wm;
static bool portalRunning = false;

void setup_wifi() {

    LOGI("WiFiManager init");

    WiFi.mode(WIFI_STA);
    wm.setDebugOutput(LOG_LEVEL >= 2);

    // Optional: timeout for config portal
    wm.setConfigPortalTimeout(180); // 3 minutes

    // Try stored credentials, else start portal
    if (!wm.autoConnect("ESP8266-Setup")) {
        LOGE("WiFi failed, rebooting");
        delay(3000);
        ESP.restart();
    }

    LOGI("WiFi connected");
    LOGI("IP: %s", WiFi.localIP().toString().c_str());
}

void wifi_loop() {
    // WiFiManager handles reconnection internally
}

bool wifi_connected() { return WiFi.status() == WL_CONNECTED; }
