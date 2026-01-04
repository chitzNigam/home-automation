#include "device_setup.h"
#include "log.h"
#include "pin_map.h"
#include "gpio_utils.h"

void reset_device(){
  #if LOG_LEVEL > 0
      Serial.begin(115200);
  #endif

  LOGI("Setting up the device");
}
void reset_peripheries(){
  LOGI("Setting up the pheripheries");
  for (size_t i = 0; i < PIN_MAP_SIZE; i++) {
    uint8_t pin = PIN_MAP[i].gpio;
    LOGI("a, %d", pin);
    if(gpio::isValid(pin)){
      LOGI("b, %d", pin);
      pinMode(pin, OUTPUT);
      digitalWrite(pin, HIGH);
    }
  }
  //TODO Get local config or remote config and set the pins
}