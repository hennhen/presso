#include <Arduino.h>
#include "ADSPressureSensor.h"

ADSPressureSensor pressureSensor;  // Create a pressure sensor object

void setup() {
  Wire.begin();
  Serial.begin(250000);
  Serial.println("Pressure Sensor Test");
}

void loop() {
  float pressure = pressureSensor.readPressure();
  Serial.print("Pressure: ");
  Serial.print(pressure);
  Serial.println(" bars");
  // delay(1000);  // Wait for a second before the next reading
}