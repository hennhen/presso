#include "NAU7802.h"
#include <Arduino.h>

NAU7802::NAU7802(float calibrationFactor)
    : _calibrationFactor(calibrationFactor), _weight(0) {
  // _scale.begin();
}

bool NAU7802::init() {
  _weight = 0;
  Wire.begin();
  if (!_scale.begin()) {
    // Serial.println("Failed to find NAU7802 chip");
    return false;
  }
  // Serial.println("NAU7802 initialized");
  _scale.setLDO(NAU7802_3V0);         // Set LDO to 3.3V
  _scale.setGain(NAU7802_GAIN_128);   // Set gain to 128
  _scale.setRate(NAU7802_RATE_80SPS); // Set 10 samples per second

  if (!tare()) {
    return false;
  }
  return true;
}

bool NAU7802::available() { return _scale.available(); }

bool NAU7802::tare() {
  // Take 10 readings to flush out readings
  for (int i = 0; i < 10; i++) {
    while (!_scale.available()) {
      delay(1);
      _scale.read();
    }
  }

  if (!_scale.calibrate(NAU7802_CALMOD_OFFSET)) {
    // Serial.println("Failed to calibrate system offset, retrying!");
    return false;
  }

  // Flush out readings again
  for (uint8_t i = 0; i < 10; i++) {
    while (!_scale.available()) {
      delay(1);
      _scale.read();
    }
  }
  _weight = 0;
  _cumulative4Average = 0;
  _currentAverageCount = 0;
  return true;
}

float NAU7802::read() {
  if (_currentAverageCount < _averagingCountTimes) {
    if (!available()) {
      return _weight; // Return the last known weight if not available
    }
    _cumulative4Average += _scale.read() / _calibrationFactor;
    _currentAverageCount++;
  } else {
    _weight = _cumulative4Average / _averagingCountTimes;
    _currentAverageCount = 0; // Reset for next averaging cycle
    _cumulative4Average = 0;
  }
  return _weight;
}