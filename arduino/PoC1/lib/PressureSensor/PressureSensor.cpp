#include "PressureSensor.h"
#include <Arduino.h>

// Constructor for the PressureSensor class
PressureSensor::PressureSensor(int sensorPin)
: _sensorPin(sensorPin), 
  _pressurePrev(0),
  _minRaw(102.3),
  _maxRaw(920.7),
  _minScaled(0.0),
  _maxScaled(17.24),
  _beta(calculateBeta()) {
}

float PressureSensor::readPressure() {
  // float sensorValue = analogRead(_sensorPin);
  // float pressure = mapfloat(sensorValue, _minRaw, _maxRaw, _minScaled, _maxScaled);
  // pressure = max(pressure, 0.0f); // Clamp negative pressure to zero
  // pressure_filtered = _beta * _pressurePrev + (1 - _beta) * pressure; // Low-pass filter
  // _pressurePrev = pressure_filtered;
  _pressurePrev = mapfloat(analogRead(_sensorPin), _minRaw, _maxRaw, _minScaled, _maxScaled);
  _pressurePrev = max(_pressurePrev, 0.0f); // Clamp negative pressure to zero

  return _pressurePrev;
}

float PressureSensor::mapfloat(float x, float in_min, float in_max, float out_min, float out_max) {
  return (x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min;
}

float PressureSensor::calculateBeta() {
  const float cutOffHz = 10.0;
  const float euler = 2.718281828459045;
  const float pi = 3.14159265358979323846;
  return pow(euler, -2 * pi * cutOffHz * 0.001);
}