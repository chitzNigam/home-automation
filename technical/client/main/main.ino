#include "GpioCommandHandler.h"
#include "MqttService.h"
#include "wifi_setup.h"
#include "device_setup.h"

MqttRouter router;
MqttService mqtt(router);
GpioCommandHandler gpioHandler;

void setup() {
    reset_device();
    reset_peripheries();
    
    setup_wifi();
    router.registerHandler(&gpioHandler);

    mqtt.begin();
    mqtt.registerTopic(gpioHandler.topic());

}

void loop() {
    wifi_loop();
    mqtt.loop();
}
