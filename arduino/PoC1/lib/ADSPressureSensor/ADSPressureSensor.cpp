#include "ADSPressureSensor.h"

// Constructor for the ADSPressureSensor class
ADSPressureSensor::ADSPressureSensor(uint8_t address, uint8_t gain,
                                     uint8_t dataRate)
    : _gain(gain), _dataRate(dataRate), _ads(address) {}

bool ADSPressureSensor::init() {
  bool success = false;
  success = _ads.begin();
  _ads.setGain(_gain);
  _ads.setDataRate(_dataRate);
  return success;
}

float ADSPressureSensor::readPressure() {
  if (_ads.isReady()) {
    int16_t rawAdc = _ads.getValue();
    float voltage = 5.0 + _ads.toVoltage(rawAdc);
    _pressure = voltageToBars(voltage);
    _ads.requestADC_Differential_0_1();
  }
  return _pressure; // Convert voltage to pressure in bars
}

float ADSPressureSensor::voltageToBars(float voltage) {
  // Direct conversion of voltage to pressure in bars
  float pressure = ((voltage - _minVoltage) * (_maxPressure - _minPressure)) /
                       (_maxVoltage - _minVoltage) +
                   _minPressure;
  return pressure;
}