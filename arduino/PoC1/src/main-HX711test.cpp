#include "HX711_Scale.h"
#include <Arduino.h>

#define LOADCELL_DOUT_PIN 20
#define LOADCELL_SCK_PIN 21
#define LOADCELL_CALIBRATION_FACTOR 1036.1112060547

// HX711_Scale scale(LOADCELL_DOUT_PIN, LOADCELL_SCK_PIN,
//                   LOADCELL_CALIBRATION_FACTOR);

void setup() {
  Serial.begin(115200);
  Serial.println("HX711 scale test");

//   // Tare the scale
//   scale.tare();
//   Serial.println("Scale tared");
}

long main_loop_start_time = 0;
void loop() {
  // scale.updateWeight();
  // Serial.print("Weight: ");
  // Serial.println(scale.weight);
  // Serial.println(" grams");
  Serial.println(millis() - main_loop_start_time);
  main_loop_start_time = millis();
}
