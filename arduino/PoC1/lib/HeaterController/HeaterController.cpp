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
  targetReachedCount = 0;
}

float HeaterController::read() { return currentTemperature; }

// Returns true if the heater is done heating
bool HeaterController::controlHeater() {
  // Check if the heater should be turned on or off
  if (currentTemperature < targetTemperature) {
    digitalWrite(heaterPin, HIGH); // Turn on the heater
  } else if (currentTemperature >= targetTemperature) {
    // If the temperature is reached, increment the counter
    targetReachedCount++;
  }
  // If the temperature is reached for 50 times, turn off the heater
  if (targetReachedCount > 50) {
    digitalWrite(heaterPin, LOW); // Turn off the heater
    targetReachedCount = 0;
    return true;
  }
  return false;
}

bool HeaterController::update() {
  // Return true if heater is done heating
  if (millis() - lastRequestTime > millisToWait) {
    // Conversion finished.
    currentTemperature = sensors.getTempCByIndex(0);
    sensors.requestTemperaturesByIndex(0);
    lastRequestTime = millis();
  }
  return controlHeater();
}