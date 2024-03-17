#include "HeaterController.h"
#include <Arduino.h>

HeaterController::HeaterController(uint8_t oneWireBus, uint8_t heaterPin)
    : oneWire(oneWireBus), sensors(&oneWire), targetTemperature(0.0),
      lastRequestTime(0), currentTemperature(0.0),
      resolution(12), heaterPin(heaterPin), millisToWait(0) {
  sensors.begin();
  sensors.setResolution(resolution);
  sensors.setWaitForConversion(false);
  pinMode(heaterPin, OUTPUT);
  calculateWaitForConversion();
}

void HeaterController::calculateWaitForConversion() {
  // Calculate the wait time based on the resolution
  millisToWait = sensors.millisToWaitForConversion(resolution) + 100;
}

void HeaterController::setTarget(float degreesC) {
  targetTemperature = degreesC;
}

float HeaterController::read() { return currentTemperature; }

void HeaterController::controlHeater() {
  if (currentTemperature <= targetTemperature - 0.5) {
    digitalWrite(heaterPin, HIGH); // Turn on the heater
  } else if (currentTemperature >= targetTemperature) {
    digitalWrite(heaterPin, LOW); // Turn off the heater
  }
}

void HeaterController::update() {
  if (millis() - lastRequestTime > millisToWait) {
    // Conversion finished.
    currentTemperature = sensors.getTempCByIndex(0);
    sensors.requestTemperaturesByIndex(0);
    lastRequestTime = millis();
  }
  controlHeater();
}